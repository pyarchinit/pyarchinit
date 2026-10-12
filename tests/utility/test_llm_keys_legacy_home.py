"""Le chiavi API salvate prima del cambio di casa (2026-06-27, ~/pyarchinit →
~/pyarchinit_5) restano nella vecchia `bin`: si leggono da lì finché non se
ne salva una nuova (2026-10-12, trovato provando la narrativa: il profilo
aveva Claude e GPT impostati ma «Nessuna AI impostata»)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import llm_providers as lp  # noqa: E402


def _case(tmp_path, monkeypatch):
    nuova = tmp_path / "pyarchinit_5" / "bin"
    vecchia = tmp_path / "pyarchinit" / "bin"
    nuova.mkdir(parents=True)
    vecchia.mkdir(parents=True)
    monkeypatch.setattr(lp, "pyarchinit_home_bin", lambda: str(nuova))
    monkeypatch.setattr(lp, "legacy_pyarchinit_home", lambda: str(tmp_path / "pyarchinit"))
    return nuova, vecchia


def test_la_chiave_nella_casa_vecchia_vale_finche_la_nuova_non_ne_ha_una(tmp_path, monkeypatch):
    nuova, vecchia = _case(tmp_path, monkeypatch)
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.ANTHROPIC) == ""
    (vecchia / "claude_api_key.txt").write_text("chiave-vecchia\n", encoding="utf-8")
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.ANTHROPIC) == "chiave-vecchia"
    (vecchia / "gpt_api_key.txt").write_text("gpt-vecchia", encoding="utf-8")
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.OPENAI) == "gpt-vecchia"
    (nuova / "claude_api_key.txt").write_text("chiave-nuova", encoding="utf-8")
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.ANTHROPIC) == "chiave-nuova"


def test_il_nome_storico_di_anthropic_vale_anche_nella_casa_vecchia(tmp_path, monkeypatch):
    _nuova, vecchia = _case(tmp_path, monkeypatch)
    (vecchia / "anthropic_api_key.txt").write_text("storica", encoding="utf-8")
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.ANTHROPIC) == "storica"


def test_i_fornitori_locali_non_hanno_chiave(tmp_path, monkeypatch):
    _nuova, vecchia = _case(tmp_path, monkeypatch)
    (vecchia / "gpt_api_key.txt").write_text("x", encoding="utf-8")
    assert lp.LLMProviderManager.get_api_key(lp.LLMProvider.OLLAMA) == ""
