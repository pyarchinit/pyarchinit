"""
Central LLM provider abstraction for PyArchInit.

Supports OpenAI, Anthropic Claude, Ollama and LM Studio behind a single API.
Ollama and LM Studio expose an OpenAI-compatible REST API, so we reuse the
``openai`` Python client and only change the ``base_url``.

Public surface:
    - LLMProvider (enum)
    - LLMConfig (dataclass)
    - LLMProviderManager (static helpers: discover, factory, stream)

The manager intentionally avoids any QGIS UI dependency so that headless
scripts can also use it.
"""

import json
import os
import socket
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Iterator
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


PROVIDER_DEFAULTS = {
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "needs_api_key": True,
        "is_local": False,
        "default_models": [
            "gpt-5.5",
            "gpt-5.5-2026-04-23",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        "vision_models": [
            "gpt-5.5",
            "gpt-5.5-2026-04-23",
            "gpt-5",
            "gpt-5-mini",
            "gpt-4.1",
            "gpt-4o",
            "gpt-4-turbo",
        ],
    },
    LLMProvider.ANTHROPIC: {
        "base_url": "https://api.anthropic.com",
        "needs_api_key": True,
        "is_local": False,
        "default_models": [
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
            "claude-opus-4-5-20251021",
            "claude-sonnet-4-5-20250929",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ],
        "vision_models": [
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
            "claude-opus-4-5-20251021",
            "claude-sonnet-4-5-20250929",
            "claude-3-5-sonnet-20241022",
        ],
    },
    LLMProvider.OLLAMA: {
        "base_url": "http://localhost:11434/v1",
        "needs_api_key": False,
        "is_local": True,
        "default_models": [],
        "vision_models": [],
    },
    LLMProvider.LMSTUDIO: {
        "base_url": "http://localhost:1234/v1",
        "needs_api_key": False,
        "is_local": True,
        "default_models": [],
        "vision_models": [],
    },
}


# OpenAI families that reject `max_tokens` and require `max_completion_tokens`
# instead — the GPT-5 family and o-series reasoning models. Match by prefix so
# dated snapshots (e.g. "gpt-5.5-2026-04-23") are caught too.
OPENAI_MAX_COMPLETION_TOKENS_PREFIXES = ("gpt-5", "o1", "o3", "o4")


def _openai_token_param(model: str) -> str:
    """Return the right token-limit parameter name for an OpenAI model."""
    m = (model or "").lower()
    return (
        "max_completion_tokens"
        if any(m.startswith(p) for p in OPENAI_MAX_COMPLETION_TOKENS_PREFIXES)
        else "max_tokens"
    )


VISION_MODEL_HINTS = (
    "vision",
    "vl",
    "llava",
    "bakllava",
    "moondream",
    "minicpm-v",
    "internvl",
    "qwen-vl",
    "qwen2-vl",
    "qwen2.5-vl",
    "pixtral",
    "phi-3-vision",
    "phi-3.5-vision",
    "gemma3",
    "deepseek-vl",
)


@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str = ""
    api_key: str = ""
    base_url: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.base_url:
            self.base_url = PROVIDER_DEFAULTS[self.provider]["base_url"]

    @property
    def is_local(self) -> bool:
        return PROVIDER_DEFAULTS[self.provider]["is_local"]

    @property
    def needs_api_key(self) -> bool:
        return PROVIDER_DEFAULTS[self.provider]["needs_api_key"]


class LLMProviderManager:
    SETTINGS_PREFIX = "pyArchInit/llm/"

    @staticmethod
    def is_provider_available(provider: LLMProvider, timeout: float = 1.5) -> bool:
        """Health check.

        Cloud providers always return True (we can only know once we make a real
        call). Local providers do a fast TCP connect to ``host:port``.
        """
        if not PROVIDER_DEFAULTS[provider]["is_local"]:
            return True
        base_url = PROVIDER_DEFAULTS[provider]["base_url"]
        parsed = urlparse(base_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (80 if parsed.scheme == "http" else 443)
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return True
        except (OSError, socket.timeout):
            return False

    @staticmethod
    def discover_models(provider: LLMProvider, timeout: float = 3.0) -> List[str]:
        """Return the list of usable model IDs on the provider.

        - **LM Studio**: prefers the native ``/api/v0/models`` endpoint and
          returns only models with ``state == "loaded"`` — calling chat with
          a model that's merely *downloaded* (not loaded into RAM) returns a
          400 "No models loaded" error.
        - **Ollama**: returns all installed models (Ollama lazy-loads on
          first use, so any installed model is usable).
        - **OpenAI / Anthropic**: returns a curated default list (the cloud
          ``/models`` endpoints either require auth or report hundreds of
          irrelevant entries).
        """
        defaults = PROVIDER_DEFAULTS[provider]
        if not defaults["is_local"]:
            return list(defaults["default_models"])

        base_url = defaults["base_url"].rstrip("/")

        # LM Studio: prefer native endpoint with `state` field
        if provider == LLMProvider.LMSTUDIO:
            try:
                native_url = base_url.replace("/v1", "") + "/api/v0/models"
                with urlopen(native_url, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    loaded = []
                    for m in data.get("data", []):
                        mid = m.get("id", "")
                        if not mid or m.get("state") != "loaded":
                            continue
                        # Strip LM Studio instance suffix ":<n>" — the chat
                        # API accepts only the base id (e.g. "openai/gpt-oss-20b")
                        # not "openai/gpt-oss-20b:2".
                        loaded.append(mid.rsplit(":", 1)[0] if ":" in mid.rsplit("/", 1)[-1] else mid)
                    return sorted(set(loaded))
            except (URLError, socket.timeout, json.JSONDecodeError, ValueError):
                # Fall through to OpenAI-compat endpoint below
                pass

        # OpenAI-compatible endpoint
        url = f"{base_url}/models"
        try:
            req = Request(url, headers={"Authorization": "Bearer not-needed"})
            with urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
                if models:
                    return sorted(set(models))
        except (URLError, socket.timeout, json.JSONDecodeError, ValueError):
            pass

        # Ollama fallback: native API
        if provider == LLMProvider.OLLAMA:
            try:
                native_url = base_url.replace("/v1", "") + "/api/tags"
                with urlopen(native_url, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                    return sorted(set(models))
            except (URLError, socket.timeout, json.JSONDecodeError, ValueError):
                pass

        return []

    @staticmethod
    def discover_embedding_models(provider: LLMProvider, timeout: float = 3.0) -> List[str]:
        """Return loaded embedding model IDs on a local provider.

        Used by ``_get_embeddings`` to decide whether the chosen local server
        can serve ``/v1/embeddings`` calls — if not, callers should fall back
        to OpenAI cloud embeddings (whose vectors only need to be consistent
        within the FAISS index, not aligned with the chat model).
        """
        if provider == LLMProvider.LMSTUDIO:
            try:
                base_url = PROVIDER_DEFAULTS[provider]["base_url"].rstrip("/").replace(
                    "/v1", ""
                )
                with urlopen(base_url + "/api/v0/models", timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    out = []
                    for m in data.get("data", []):
                        mid = m.get("id", "")
                        if (
                            mid
                            and m.get("type") == "embeddings"
                            and m.get("state") == "loaded"
                        ):
                            out.append(mid.rsplit(":", 1)[0] if ":" in mid.rsplit("/", 1)[-1] else mid)
                    return sorted(set(out))
            except (URLError, socket.timeout, json.JSONDecodeError, ValueError):
                return []
        # Ollama doesn't expose model "type" — assume any installed model
        # whose name suggests embeddings is usable.
        if provider == LLMProvider.OLLAMA:
            installed = LLMProviderManager.discover_models(provider, timeout)
            hints = ("embed", "nomic", "bge", "mxbai", "snowflake")
            return [m for m in installed if any(h in m.lower() for h in hints)]
        return []

    @staticmethod
    def discover_all_models(provider: LLMProvider, timeout: float = 3.0) -> List[dict]:
        """Return *all* models on a local provider with metadata.

        Each entry is ``{"id": str, "loaded": bool, "type": str}`` where
        ``type`` is ``"llm" / "vlm" / "embeddings"`` when reported by the
        backend, or ``""`` otherwise. Only meaningful for LM Studio (which
        distinguishes loaded vs downloaded). For Ollama all installed models
        are reported as loaded since Ollama auto-loads on demand.
        """
        defaults = PROVIDER_DEFAULTS[provider]
        if not defaults["is_local"]:
            return [{"id": m, "loaded": True, "type": ""} for m in defaults["default_models"]]
        base_url = defaults["base_url"].rstrip("/")

        if provider == LLMProvider.LMSTUDIO:
            try:
                native_url = base_url.replace("/v1", "") + "/api/v0/models"
                with urlopen(native_url, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [
                        {
                            "id": m.get("id", ""),
                            "loaded": m.get("state") == "loaded",
                            "type": m.get("type", ""),
                        }
                        for m in data.get("data", [])
                        if m.get("id")
                    ]
            except (URLError, socket.timeout, json.JSONDecodeError, ValueError):
                return []

        # Ollama: all installed are usable
        return [{"id": m, "loaded": True, "type": ""} for m in
                LLMProviderManager.discover_models(provider, timeout)]

    @staticmethod
    def filter_vision_models(provider: LLMProvider, models: List[str]) -> List[str]:
        """Best-effort filter to keep only models likely to support images."""
        defaults = PROVIDER_DEFAULTS[provider]
        if not defaults["is_local"]:
            allow = set(defaults["vision_models"])
            return [m for m in models if m in allow]
        return [m for m in models if any(h in m.lower() for h in VISION_MODEL_HINTS)]

    @staticmethod
    def get_chat_client(config: LLMConfig):
        """Factory returning a configured client.

        OpenAI / Ollama / LM Studio share the ``openai.OpenAI`` client.
        Anthropic uses the dedicated ``anthropic.Anthropic`` client.
        """
        if config.provider == LLMProvider.ANTHROPIC:
            from anthropic import Anthropic

            return Anthropic(api_key=config.api_key)
        from openai import OpenAI

        # Local providers don't need a real key but the SDK refuses an empty one
        api_key = config.api_key or "not-needed"
        return OpenAI(api_key=api_key, base_url=config.base_url)

    @staticmethod
    def _validate_local_model(config: LLMConfig) -> None:
        """For local providers, raise a helpful error if the requested model
        isn't actually loaded on the server. Avoids the cryptic 400 from
        LM Studio's ``No models loaded`` and similar messages from Ollama.
        """
        if not config.is_local or not config.model:
            return
        try:
            usable = set(LLMProviderManager.discover_models(config.provider))
        except Exception:
            return  # discovery itself failed — let the upstream call surface its own error
        if not usable:
            raise RuntimeError(
                f"Nessun modello caricato su {config.provider.value} "
                f"({config.base_url}). Carica un modello prima di lanciare la query."
            )
        if config.model not in usable:
            available = ", ".join(sorted(usable)[:5])
            raise RuntimeError(
                f"Il modello '{config.model}' non è caricato su "
                f"{config.provider.value}. Caricati: {available}. "
                "Premi 'Aggiorna modelli' nel selettore e scegli uno dei caricati."
            )

    @staticmethod
    def _annotate_error(config: LLMConfig, exc: Exception) -> Exception:
        """Wrap a low-level error with provider/base_url/model context.

        Without this, an LLM error from a misconfigured client looks identical
        to an error from the right server, making debugging impossible.
        Returning a new exception keeps the stack but makes the cause obvious.
        """
        ctx = (
            f"[provider={config.provider.value} base_url={config.base_url} "
            f"model={config.model!r}]"
        )
        return type(exc)(f"{exc} {ctx}")

    @staticmethod
    def stream_chat(
        config: LLMConfig,
        messages: list,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
    ) -> Iterator[str]:
        """Unified streaming generator yielding text chunks.

        Hides the Anthropic vs OpenAI streaming API difference. ``messages``
        follows the OpenAI shape ``[{"role": "system"|"user"|"assistant",
        "content": "..."}]``; for Anthropic the system message is extracted
        and passed via ``system=`` (Anthropic's required convention).
        """
        LLMProviderManager._validate_local_model(config)
        client = LLMProviderManager.get_chat_client(config)

        if config.provider == LLMProvider.ANTHROPIC:
            system_msg = ""
            user_msgs = []
            for m in messages:
                if m["role"] == "system":
                    system_msg = m["content"]
                else:
                    user_msgs.append(m)
            kwargs = dict(
                model=config.model,
                max_tokens=max_tokens,
                system=system_msg or "You are a helpful assistant.",
                messages=user_msgs,
            )
            if temperature is not None:
                kwargs["temperature"] = temperature
            try:
                with client.messages.stream(**kwargs) as stream:
                    for text in stream.text_stream:
                        yield text
            except Exception as e:
                raise LLMProviderManager._annotate_error(config, e) from e
            return

        kwargs = dict(model=config.model, messages=messages, stream=True)
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None and config.provider == LLMProvider.OPENAI:
            # GPT-5 family / o-series reject `max_tokens` — they require
            # `max_completion_tokens`. Local OpenAI-compatible backends
            # (Ollama, LM Studio) still expect `max_tokens`.
            kwargs[_openai_token_param(config.model)] = max_tokens
        elif max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        try:
            response = client.chat.completions.create(**kwargs)
            for chunk in response:
                try:
                    delta = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    delta = None
                if delta is not None:
                    yield delta
        except Exception as e:
            raise LLMProviderManager._annotate_error(config, e) from e

    @staticmethod
    def chat(
        config: LLMConfig,
        messages: list,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
    ) -> str:
        """Non-streaming convenience wrapper. Concatenates all chunks."""
        return "".join(
            LLMProviderManager.stream_chat(
                config, messages, max_tokens=max_tokens, temperature=temperature
            )
        )

    # ------------------------------------------------------------------ keys

    @staticmethod
    def _key_file_path(provider: LLMProvider) -> Optional[str]:
        if provider == LLMProvider.OPENAI:
            return os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "gpt_api_key.txt")
        if provider == LLMProvider.ANTHROPIC:
            return os.path.join(
                os.path.expanduser("~"), "pyarchinit", "bin", "claude_api_key.txt"
            )
        return None

    @staticmethod
    def get_api_key(provider: LLMProvider) -> str:
        """Read the saved API key for cloud providers (empty for local)."""
        if PROVIDER_DEFAULTS[provider]["is_local"]:
            return ""
        path = LLMProviderManager._key_file_path(provider)
        if not path:
            return ""
        # Anthropic legacy filename
        if provider == LLMProvider.ANTHROPIC and not os.path.exists(path):
            legacy = os.path.join(
                os.path.expanduser("~"), "pyarchinit", "bin", "anthropic_api_key.txt"
            )
            if os.path.exists(legacy):
                path = legacy
        try:
            if os.path.exists(path):
                with open(path, "r") as fh:
                    return fh.read().strip()
        except OSError:
            pass
        return ""

    @staticmethod
    def save_api_key(provider: LLMProvider, key: str) -> None:
        if PROVIDER_DEFAULTS[provider]["is_local"]:
            return
        path = LLMProviderManager._key_file_path(provider)
        if not path:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(key.strip())

    # -------------------------------------------------------------- settings

    @staticmethod
    def save_config(config: LLMConfig, scope: str = "default") -> None:
        """Persist config (provider, model, base_url) to QSettings.

        API keys are NOT saved here — they live in the dedicated key files.
        """
        from qgis.PyQt.QtCore import QSettings

        s = QSettings()
        prefix = f"{LLMProviderManager.SETTINGS_PREFIX}{scope}/"
        s.setValue(prefix + "provider", config.provider.value)
        s.setValue(prefix + "model", config.model)
        s.setValue(prefix + "base_url", config.base_url)

    @staticmethod
    def load_config(scope: str = "default") -> Optional[LLMConfig]:
        from qgis.PyQt.QtCore import QSettings

        s = QSettings()
        prefix = f"{LLMProviderManager.SETTINGS_PREFIX}{scope}/"
        provider_val = s.value(prefix + "provider", "", type=str)
        if not provider_val:
            return None
        try:
            provider = LLMProvider(provider_val)
        except ValueError:
            return None
        cfg = LLMConfig(
            provider=provider,
            model=s.value(prefix + "model", "", type=str),
            base_url=s.value(prefix + "base_url", "", type=str),
        )
        if cfg.needs_api_key:
            cfg.api_key = LLMProviderManager.get_api_key(provider)
        return cfg

    @staticmethod
    def resolve_config(
        scope: str = "default",
        fallback_provider: LLMProvider = LLMProvider.OPENAI,
    ) -> LLMConfig:
        """Return the saved config for ``scope``, or a sensible default.

        This is the single entry point callers should use when they just want
        "the AI config the user picked".
        """
        cfg = LLMProviderManager.load_config(scope)
        if cfg is None:
            cfg = LLMConfig(provider=fallback_provider)
            if cfg.needs_api_key:
                cfg.api_key = LLMProviderManager.get_api_key(fallback_provider)
            defaults = PROVIDER_DEFAULTS[fallback_provider]["default_models"]
            if defaults:
                cfg.model = defaults[0]
        return cfg
