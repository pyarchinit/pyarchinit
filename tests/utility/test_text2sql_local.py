"""Text2SQL col modello locale (17 ottobre 2026): la scheda US chiamava
`MakeSQL.make_local_request` ed `explain_local_request`, che non esistevano
— scegliere «modello locale» dava un AttributeError. Il modello che la
finestra scarica è un GGUF (Phi-3 mini): lo usa `llama-cpp-python` quando
c'è; senza, si passa a Ollama se è acceso; senza nessuno dei due si dice
che cosa manca, invece di rompersi."""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("qgis.PyQt")
from modules.utility import textTosql  # noqa: E402
from modules.utility.textTosql import MakeSQL  # noqa: E402


@pytest.fixture
def messaggi(monkeypatch):
    detti = []

    class Box:
        @staticmethod
        def information(_p, _t, testo, *a, **k):
            detti.append(testo)
        warning = critical = information

    monkeypatch.setattr(textTosql, "QMessageBox", Box)
    monkeypatch.setattr(MakeSQL, "_local_model_path", staticmethod(lambda: "/non/esiste/phi3_text2sql.gguf"))
    monkeypatch.setitem(sys.modules, "llama_cpp", None)            # non installato
    return detti


def test_senza_motore_locale_ne_ollama_si_dice_cosa_manca(messaggi, monkeypatch):
    monkeypatch.setattr(MakeSQL, "check_ollama_status", staticmethod(lambda: False))
    assert MakeSQL.make_local_request("tutte le US del sito", "sqlite", None) is None
    assert MakeSQL.explain_local_request("SELECT 1", None) is None
    assert messaggi and "llama-cpp-python" in messaggi[0] and "Ollama" in messaggi[0]


def test_con_ollama_acceso_si_usa_ollama(messaggi, monkeypatch):
    chiesto = {}
    monkeypatch.setattr(MakeSQL, "check_ollama_status", staticmethod(lambda: True))
    monkeypatch.setattr(MakeSQL, "get_ollama_models", staticmethod(lambda: ["llama3.2:latest", "phi3:mini"]))

    def ollama(prompt, db_type, model="llama3.2", parent=None):
        chiesto.update(prompt=prompt, db=db_type, model=model)
        return "SELECT * FROM us_table", "spiegazione"

    monkeypatch.setattr(MakeSQL, "make_ollama_request", staticmethod(ollama))
    monkeypatch.setattr(MakeSQL, "explain_ollama_request",
                        staticmethod(lambda sql, model="llama3.2", parent=None: "spiega " + sql))
    assert MakeSQL.make_local_request("tutte le US", "postgres", None) == "SELECT * FROM us_table"
    assert chiesto == {"prompt": "tutte le US", "db": "postgres", "model": "phi3:mini"}   # Phi-3, come il GGUF
    assert MakeSQL.explain_local_request("SELECT 1", None) == "spiega SELECT 1"
    assert messaggi == []


def test_col_gguf_e_llama_cpp_si_usa_il_modello_scaricato(messaggi, monkeypatch, tmp_path):
    modello = tmp_path / "phi3_text2sql.gguf"
    modello.write_bytes(b"GGUF")
    monkeypatch.setattr(MakeSQL, "_local_model_path", staticmethod(lambda: str(modello)))
    monkeypatch.setattr(MakeSQL, "schema_to_text", staticmethod(lambda _m: "TABLE us_table (us, sito)"))
    monkeypatch.setattr(textTosql.database_schema, "get_metadata", lambda: None)
    caricati = []

    class Llama:
        def __init__(self, model_path, **kw):
            caricati.append(model_path)

        def create_chat_completion(self, messages, **kw):
            testo = messages[-1]["content"]
            risposta = ("```sql\nSELECT * FROM us_table;\n```\n--- elenca le US" if "SQL" in testo
                        else "Elenca tutte le unità stratigrafiche.")
            return {"choices": [{"message": {"content": risposta}}]}

    monkeypatch.setitem(sys.modules, "llama_cpp", types.SimpleNamespace(Llama=Llama))
    monkeypatch.setattr(MakeSQL, "_llama", None, raising=False)
    assert MakeSQL.make_local_request("tutte le US", "sqlite", None) == "SELECT * FROM us_table;"
    assert MakeSQL.explain_local_request("SELECT * FROM us_table", None) == "Elenca tutte le unità stratigrafiche."
    assert caricati == [str(modello)]                      # caricato una volta sola
    assert messaggi == []
