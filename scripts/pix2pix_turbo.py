"""
Pix2Pix_Turbo model for PotteryInk
Adapted from PyPotteryInk (https://github.com/lrncrd/PyPotteryInk)
Fixed for compatibility with diffusers 0.29+ and peft
"""

import os
import copy
import torch
from transformers import AutoTokenizer, CLIPTextModel
from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler
from peft import LoraConfig, inject_adapter_in_model

# Device selection
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")


def make_1step_sched():
    noise_scheduler = DDPMScheduler.from_pretrained("stabilityai/sd-turbo", subfolder="scheduler")
    noise_scheduler.set_timesteps(1, device=device)
    noise_scheduler.alphas_cumprod = noise_scheduler.alphas_cumprod.to(device)
    return noise_scheduler


def my_vae_encoder_fwd(self, sample):
    """Modified VAE encoder that saves intermediate activations for skip connections"""
    sample = self.conv_in(sample)
    l_blocks = []
    for down_block in self.down_blocks:
        l_blocks.append(sample)
        sample = down_block(sample)
    sample = self.mid_block(sample)
    sample = self.conv_norm_out(sample)
    sample = self.conv_act(sample)
    sample = self.conv_out(sample)
    self.current_down_blocks = l_blocks
    return sample


def my_vae_decoder_fwd(self, sample, latent_embeds=None):
    """Modified VAE decoder that uses skip connections from encoder"""
    sample = self.conv_in(sample)
    upscale_dtype = next(iter(self.up_blocks.parameters())).dtype
    sample = self.mid_block(sample, latent_embeds)
    sample = sample.to(upscale_dtype)

    if not self.ignore_skip:
        skip_convs = [self.skip_conv_1, self.skip_conv_2, self.skip_conv_3, self.skip_conv_4]
        for idx, up_block in enumerate(self.up_blocks):
            skip_in = skip_convs[idx](self.incoming_skip_acts[::-1][idx] * self.gamma)
            sample = sample + skip_in
            sample = up_block(sample, latent_embeds)
    else:
        for idx, up_block in enumerate(self.up_blocks):
            sample = up_block(sample, latent_embeds)

    if latent_embeds is None:
        sample = self.conv_norm_out(sample)
    else:
        sample = self.conv_norm_out(sample, latent_embeds)
    sample = self.conv_act(sample)
    sample = self.conv_out(sample)
    return sample


class TwinConv(torch.nn.Module):
    """Dual convolution for interpolating between pretrained and finetuned"""
    def __init__(self, convin_pretrained, convin_curr):
        super().__init__()
        self.conv_in_pretrained = copy.deepcopy(convin_pretrained)
        self.conv_in_curr = copy.deepcopy(convin_curr)
        self.r = None

    def forward(self, x):
        x1 = self.conv_in_pretrained(x).detach()
        x2 = self.conv_in_curr(x)
        return x1 * (1 - self.r) + x2 * self.r


class Pix2Pix_Turbo(torch.nn.Module):
    def __init__(self, pretrained_path=None):
        super().__init__()

        # Load tokenizer and text encoder
        self.tokenizer = AutoTokenizer.from_pretrained("stabilityai/sd-turbo", subfolder="tokenizer")
        self.text_encoder = CLIPTextModel.from_pretrained("stabilityai/sd-turbo", subfolder="text_encoder").to(device)

        # Scheduler
        self.sched = make_1step_sched()

        # Load VAE with custom forward methods for skip connections
        vae = AutoencoderKL.from_pretrained("stabilityai/sd-turbo", subfolder="vae")
        vae.encoder.forward = my_vae_encoder_fwd.__get__(vae.encoder, vae.encoder.__class__)
        vae.decoder.forward = my_vae_decoder_fwd.__get__(vae.decoder, vae.decoder.__class__)

        # Add skip connection convolutions
        vae.decoder.skip_conv_1 = torch.nn.Conv2d(512, 512, kernel_size=(1, 1), stride=(1, 1), bias=False).to(device)
        vae.decoder.skip_conv_2 = torch.nn.Conv2d(256, 512, kernel_size=(1, 1), stride=(1, 1), bias=False).to(device)
        vae.decoder.skip_conv_3 = torch.nn.Conv2d(128, 512, kernel_size=(1, 1), stride=(1, 1), bias=False).to(device)
        vae.decoder.skip_conv_4 = torch.nn.Conv2d(128, 256, kernel_size=(1, 1), stride=(1, 1), bias=False).to(device)
        vae.decoder.ignore_skip = False

        # Load UNet
        unet = UNet2DConditionModel.from_pretrained("stabilityai/sd-turbo", subfolder="unet")

        if pretrained_path is not None:
            print(f"Loading pretrained weights from: {pretrained_path}")
            sd = torch.load(pretrained_path, map_location="cpu", weights_only=False)

            rank_unet = sd["rank_unet"]
            rank_vae = sd["rank_vae"]
            unet_lora_target_modules = sd["unet_lora_target_modules"]
            vae_lora_target_modules = sd["vae_lora_target_modules"]

            print(f"Config: UNet rank={rank_unet}, VAE rank={rank_vae}")
            print(f"UNet targets: {len(unet_lora_target_modules)}, VAE targets: {len(vae_lora_target_modules)}")

            # Inject LoRA adapters into UNet
            unet_lora_config = LoraConfig(
                r=rank_unet,
                lora_alpha=rank_unet,
                target_modules=unet_lora_target_modules,
                lora_dropout=0.0,
            )
            unet = inject_adapter_in_model(unet_lora_config, unet, adapter_name="default")

            # Inject LoRA adapters into VAE
            vae_lora_config = LoraConfig(
                r=rank_vae,
                lora_alpha=rank_vae,
                target_modules=vae_lora_target_modules,
                lora_dropout=0.0,
            )
            vae = inject_adapter_in_model(vae_lora_config, vae, adapter_name="vae_skip")

            # Load UNet weights
            unet_state = sd["state_dict_unet"]
            unet_current = unet.state_dict()
            loaded_unet = 0
            for k, v in unet_state.items():
                if k in unet_current:
                    unet_current[k] = v
                    loaded_unet += 1
            unet.load_state_dict(unet_current, strict=False)
            print(f"Loaded {loaded_unet}/{len(unet_state)} UNet weights")

            # Load VAE weights
            vae_state = sd["state_dict_vae"]
            vae_current = vae.state_dict()
            loaded_vae = 0
            for k, v in vae_state.items():
                if k in vae_current:
                    vae_current[k] = v
                    loaded_vae += 1
            vae.load_state_dict(vae_current, strict=False)
            print(f"Loaded {loaded_vae}/{len(vae_state)} VAE LoRA weights")

            # Load skip_conv base layer weights separately
            if "decoder.skip_conv_1.base_layer.weight" in vae_state:
                vae.decoder.skip_conv_1.weight.data = vae_state["decoder.skip_conv_1.base_layer.weight"]
                vae.decoder.skip_conv_2.weight.data = vae_state["decoder.skip_conv_2.base_layer.weight"]
                vae.decoder.skip_conv_3.weight.data = vae_state["decoder.skip_conv_3.base_layer.weight"]
                vae.decoder.skip_conv_4.weight.data = vae_state["decoder.skip_conv_4.base_layer.weight"]
                print("Loaded skip_conv base layer weights")

            # Store config for saving
            self.target_modules_unet = unet_lora_target_modules
            self.target_modules_vae = vae_lora_target_modules
            self.lora_rank_unet = rank_unet
            self.lora_rank_vae = rank_vae

        # Move to device
        unet.to(device)
        vae.to(device)

        self.unet = unet
        self.vae = vae
        self.vae.decoder.gamma = 1
        self.timesteps = torch.tensor([999], device=device).long()
        self.text_encoder.requires_grad_(False)

    def set_eval(self):
        self.unet.eval()
        self.vae.eval()
        self.unet.requires_grad_(False)
        self.vae.requires_grad_(False)

    def set_train(self):
        self.unet.train()
        self.vae.train()
        for n, p in self.unet.named_parameters():
            if "lora" in n:
                p.requires_grad = True
        self.unet.conv_in.requires_grad_(True)
        for n, p in self.vae.named_parameters():
            if "lora" in n:
                p.requires_grad = True
        self.vae.decoder.skip_conv_1.requires_grad_(True)
        self.vae.decoder.skip_conv_2.requires_grad_(True)
        self.vae.decoder.skip_conv_3.requires_grad_(True)
        self.vae.decoder.skip_conv_4.requires_grad_(True)

    def forward(self, c_t, prompt=None, prompt_tokens=None, deterministic=True, r=1.0, noise_map=None):
        """
        Process input image through the model

        Args:
            c_t: Input image tensor [B, 3, H, W] in range [0, 1]
            prompt: Text prompt string
            prompt_tokens: Pre-tokenized prompt (alternative to prompt)
            deterministic: Use deterministic mode
            r: Interpolation weight for LoRA
            noise_map: Optional noise tensor

        Returns:
            Output image tensor [B, 3, H, W] in range [-1, 1]
        """
        assert (prompt is None) != (prompt_tokens is None), "Provide either prompt or prompt_tokens"

        # Encode text
        if prompt is not None:
            caption_tokens = self.tokenizer(
                prompt,
                max_length=self.tokenizer.model_max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            ).input_ids.to(device)
            caption_enc = self.text_encoder(caption_tokens)[0]
        else:
            caption_enc = self.text_encoder(prompt_tokens)[0]

        if deterministic:
            # Encode input image
            encoded_control = self.vae.encode(c_t).latent_dist.sample() * self.vae.config.scaling_factor

            # UNet forward
            model_pred = self.unet(encoded_control, self.timesteps, encoder_hidden_states=caption_enc).sample

            # Single step denoising
            x_denoised = self.sched.step(model_pred, self.timesteps, encoded_control, return_dict=True).prev_sample
            x_denoised = x_denoised.to(model_pred.dtype)

            # Decode with skip connections
            self.vae.decoder.incoming_skip_acts = self.vae.encoder.current_down_blocks
            output_image = self.vae.decode(x_denoised / self.vae.config.scaling_factor).sample
            output_image = output_image.clamp(-1, 1)
        else:
            # Non-deterministic mode with interpolation
            encoded_control = self.vae.encode(c_t).latent_dist.sample() * self.vae.config.scaling_factor
            unet_input = encoded_control * r + noise_map * (1 - r)
            unet_output = self.unet(unet_input, self.timesteps, encoder_hidden_states=caption_enc).sample
            x_denoised = self.sched.step(unet_output, self.timesteps, unet_input, return_dict=True).prev_sample
            x_denoised = x_denoised.to(unet_output.dtype)
            self.vae.decoder.incoming_skip_acts = self.vae.encoder.current_down_blocks
            self.vae.decoder.gamma = r
            output_image = self.vae.decode(x_denoised / self.vae.config.scaling_factor).sample
            output_image = output_image.clamp(-1, 1)

        return output_image
