"""I modelli di Claude e di OpenAI: gli ultimi, e l'elenco vero dal
fornitore quando c'è la chiave (2026-10-12, «aggiorna i modelli di claude
alle ultime versioni e quelli di openai»)."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import llm_providers as lp  # noqa: E402

A, O = lp.LLMProvider.ANTHROPIC, lp.LLMProvider.OPENAI


def test_i_predefiniti_partono_dalla_famiglia_5_di_claude_e_dai_gpt_6():
    claude = lp.PROVIDER_DEFAULTS[A]["default_models"]
    assert claude[:4] == ["claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
    assert "claude-opus-4-7" in claude                       # quello salvato da Enzo resta
    assert not any(m.startswith("claude-3") for m in claude)  # ritirati dall'API
    gpt = lp.PROVIDER_DEFAULTS[O]["default_models"]
    assert gpt[0].startswith("gpt-6") and "gpt-5.5" in gpt and "gpt-5.4-mini" in gpt
    assert not any(m.endswith("-pro") for m in gpt)           # non rispondono in chat/completions
    assert not any(m[-10:].count("-") == 2 and m[-10:-6].isdigit() for m in gpt)  # niente snapshot datati
    for prov in (A, O):
        assert set(lp.PROVIDER_DEFAULTS[prov]["vision_models"]) <= set(lp.PROVIDER_DEFAULTS[prov]["default_models"])


def test_il_parametro_dei_token_segue_la_famiglia_anche_oltre_gpt_5():
    assert lp._openai_token_param("gpt-6.1-sol") == "max_completion_tokens"
    assert lp._openai_token_param("gpt-5.4-mini") == "max_completion_tokens"
    assert lp._openai_token_param("o4-mini") == "max_completion_tokens"
    assert lp._openai_token_param("gpt-4o") == "max_tokens"
    assert lp._openai_token_param("gpt-4.1") == "max_tokens"


def test_quali_modelli_openai_sono_da_chat():
    assert lp.openai_is_chat_model("gpt-6-sol") and lp.openai_is_chat_model("gpt-5.5")
    assert lp.openai_is_chat_model("o3") and lp.openai_is_chat_model("gpt-4o-mini")
    for no in ("gpt-5.5-pro", "gpt-5.5-2026-04-23", "gpt-4o-mini-tts", "gpt-image-2",
               "gpt-realtime", "gpt-5.1-codex", "gpt-5-search-api", "o3-deep-research",
               "gpt-5.2-chat-latest", "chatgpt-image-latest", "whisper-1", "gpt-3.5-turbo-instruct"):
        assert not lp.openai_is_chat_model(no), no


def _risposta(payload):
    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    return _Resp(json.dumps(payload).encode("utf-8"))


def test_con_la_chiave_l_elenco_viene_dal_fornitore_dal_piu_nuovo(monkeypatch):
    monkeypatch.setattr(lp.LLMProviderManager, "get_api_key", staticmethod(lambda p: "k"))
    visti = []

    def finto_urlopen(req, timeout=None):
        visti.append((req.full_url, dict(req.header_items())))
        if "anthropic" in req.full_url:
            return _risposta({"data": [
                {"id": "claude-opus-4-7", "created_at": "2026-04-14T00:00:00Z"},
                {"id": "claude-haiku-5-5", "created_at": "2026-10-07T00:00:00Z"},
                {"id": "claude-nuovissimo-9", "created_at": "2027-01-01T00:00:00Z"}]})
        return _risposta({"data": [
            {"id": "gpt-5.5-2026-04-23"}, {"id": "gpt-5.5"}, {"id": "gpt-6-sol"}, {"id": "gpt-6.1-sol"},
            {"id": "gpt-4o-mini-tts"}, {"id": "gpt-5.5-pro"}, {"id": "o4-mini"}, {"id": "gpt-4o"}]})
    monkeypatch.setattr(lp, "urlopen", finto_urlopen)

    claude = lp.LLMProviderManager.discover_models(A)
    assert claude[:3] == ["claude-nuovissimo-9", "claude-haiku-5-5", "claude-opus-4-7"]
    assert "claude-opus-5-5" in claude                        # i predefiniti in coda, senza doppioni
    assert claude.count("claude-opus-4-7") == 1
    intestazioni = {k.lower(): v for k, v in visti[0][1].items()}
    assert intestazioni.get("x-api-key") == "k" and "anthropic-version" in intestazioni

    gpt = lp.LLMProviderManager.discover_models(O)
    assert gpt[:5] == ["gpt-6.1-sol", "gpt-6-sol", "gpt-5.5", "gpt-4o", "o4-mini"]   # gpt-* prima, poi o-series
    assert "gpt-5.5-pro" not in gpt and "gpt-4o-mini-tts" not in gpt and "gpt-5.5-2026-04-23" not in gpt
    assert "gpt-5.4-mini" in gpt                              # dai predefiniti


def test_senza_chiave_o_senza_rete_restano_i_predefiniti(monkeypatch):
    monkeypatch.setattr(lp.LLMProviderManager, "get_api_key", staticmethod(lambda p: ""))
    chiamate = []
    monkeypatch.setattr(lp, "urlopen", lambda *a, **k: chiamate.append(a))
    assert lp.LLMProviderManager.discover_models(A) == lp.PROVIDER_DEFAULTS[A]["default_models"]
    assert chiamate == []
    monkeypatch.setattr(lp.LLMProviderManager, "get_api_key", staticmethod(lambda p: "k"))

    def giu(*a, **k):
        raise lp.URLError("niente rete")
    monkeypatch.setattr(lp, "urlopen", giu)
    assert lp.LLMProviderManager.discover_models(O) == lp.PROVIDER_DEFAULTS[O]["default_models"]


def test_il_filtro_vision_dei_fornitori_cloud_accetta_i_modelli_nuovi():
    tenuti = lp.LLMProviderManager.filter_vision_models(
        O, ["gpt-6-sol", "gpt-5.4-nano", "gpt-4o", "gpt-3.5-turbo", "gpt-4", "o3-mini", "o4-mini"])
    assert tenuti == ["gpt-6-sol", "gpt-5.4-nano", "gpt-4o", "o4-mini"]
    assert lp.LLMProviderManager.filter_vision_models(
        A, ["claude-haiku-5-5", "claude-nuovissimo-9", "claude-2.1"]) == ["claude-haiku-5-5", "claude-nuovissimo-9"]


def test_il_selettore_aggiorna_l_elenco_cloud_in_sottofondo_se_c_e_la_chiave():
    src = (_ROOT / "modules" / "utility" / "llm_selector_widget.py").read_text(encoding="utf-8")
    assert "get_api_key(provider)" in src
    assert "i predefiniti restano" in src
