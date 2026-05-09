# scripts/pix2pix_turbo.py

## Overview

This file contains 12 documented elements.

## Classes

### TwinConv

Dual convolution for interpolating between pretrained and finetuned

**Inherits from**: torch.nn.Module

#### Methods

##### __init__(self, convin_pretrained, convin_curr)

Initializes a `TwinConv` module by creating independent deep copies of two provided convolution layers, `convin_pretrained` and `convin_curr`, stored as `self.conv_in_pretrained` and `self.conv_in_curr` respectively. The interpolation scalar `self.r` is initialized to `None` and must be set externally before calling `forward`. Calls `super().__init__()` to properly initialize the parent `torch.nn.Module`.

##### forward(self, x)

Performs a weighted interpolation between the outputs of two convolutional layers applied to the input tensor `x`. The pretrained convolution output is computed with gradient tracking disabled (`.detach()`), while the current convolution output retains gradients. The two outputs are blended using the scalar weight `self.r`, returning `x1 * (1 - self.r) + x2 * self.r`.

### Pix2Pix_Turbo

*No description available.*
A `torch.nn.Module` that implements an image-to-image translation pipeline built on the `stabilityai/sd-turbo` pretrained model. It combines a CLIP text encoder, a VAE with custom skip-connection convolutions between encoder and decoder, and a UNet performing single-step denoising, with optional LoRA adapters injected into both the UNet and VAE when a `pretrained_path` is provided. The `forward` method accepts an input image tensor and a text prompt (or pre-tokenized prompt), and returns a translated image tensor clamped to the range `[-1, 1]`, supporting both deterministic and noise-interpolated non-deterministic inference modes.

**Inherits from**: torch.nn.Module

#### Methods

##### __init__(self, pretrained_path)

Initializes the `Pix2Pix_Turbo` module by loading and configuring the tokenizer, text encoder, scheduler, VAE, and UNet from the `"stabilityai/sd-turbo"` pretrained checkpoint. The VAE encoder and decoder forward methods are replaced with custom implementations, and four skip connection convolutional layers are added to the decoder. If `pretrained_path` is provided, LoRA adapters are injected into both the UNet and VAE using rank and target module configurations loaded from the checkpoint, and all corresponding weights—including skip connection base layer weights—are restored from the saved state dictionaries.

##### set_eval(self)

Sets the model components to evaluation mode by calling `.eval()` on both `self.unet` and `self.vae`, then disables gradient computation for both components via `requires_grad_(False)`. This ensures that neither the UNet nor the VAE will update their parameters during inference.

##### set_train(self)

Sets the model to training mode by enabling gradient computation for specific parameters in both the UNet and VAE components. For the UNet, only LoRA-related parameters and the `conv_in` layer are set as trainable. For the VAE, only LoRA-related parameters and the four skip convolution layers (`skip_conv_1` through `skip_conv_4`) in the decoder are set as trainable.

##### forward(self, c_t, prompt, prompt_tokens, deterministic, r, noise_map)

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

## Functions

### make_1step_sched()

*No description available.*
Loads a `DDPMScheduler` from the pretrained `"stabilityai/sd-turbo"` model (using the `"scheduler"` subfolder) and configures it for single-step inference by calling `set_timesteps(1, device=device)`. The cumulative product of alphas (`alphas_cumprod`) is moved to the target device before the scheduler is returned. Returns the configured `DDPMScheduler` instance.

### my_vae_encoder_fwd(self, sample)

Modified VAE encoder that saves intermediate activations for skip connections

**Parameters:**
- `self`
- `sample`

### my_vae_decoder_fwd(self, sample, latent_embeds)

Modified VAE decoder that uses skip connections from encoder

**Parameters:**
- `self`
- `sample`
- `latent_embeds`

