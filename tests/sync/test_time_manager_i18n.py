"""Le finestre della stampa delle tavole parlano la lingua di QGIS
(13 ottobre 2026: «le finestre e i messaggi di generate_images sono tutti
in italiano fisso»). I testi stanno in una tabella it/en a parte; qui si
controlla che nel codice non restino frasi italiane fisse e che la
tabella sia completa."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.time_manager_messages import MESSAGES, tm  # noqa: E402

SRC = _ROOT / "tabs" / "Gis_Time_controller.py"
UI = _ROOT / "gui" / "ui" / "Gis_Time_controller.ui"
FUNZIONI = ("browse_for_template", "create_new_template", "open_layout_designer",
            "save_current_as_template", "generate_images", "choose_template")
ITALIANO = ("Seleziona", "Nuovo Template", "Nome per il nuovo", "Template Creato", "Errore",
            "Nessun layout", "Salva Template", "Inserisci", "esiste già", "Selezionare una cartella",
            "Impossibile", "Vuoi ", "Modifica Template", "Generazione", "NON scritte",
            "Atlas Completato", "Atlas Interrotto", "Salvate in", "interrotta", "Continua Atlas",
            "Hai terminato", "Nessuna US", "Nessun order_layer", "Scegli Layout", "Sfoglia",
            "Usa Template", "trovato nelle", "Annulla")


def _stringhe(funzione):
    for c in ast.walk(funzione):
        if isinstance(c, ast.Constant) and isinstance(c.value, str):
            yield c.value
        elif isinstance(c, ast.JoinedStr):
            for v in c.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    yield v.value


def test_le_finestre_della_stampa_non_hanno_testo_fisso_in_italiano():
    albero = ast.parse(SRC.read_text(encoding="utf-8"))
    trovate = [(n.name, s[:60]) for n in ast.walk(albero)
               if isinstance(n, ast.FunctionDef) and n.name in FUNZIONI
               for s in _stringhe(n) if any(p in s for p in ITALIANO)]
    assert trovate == [], trovate


def test_la_tabella_ha_italiano_e_inglese_con_gli_stessi_segnaposto():
    assert set(MESSAGES) == {"it", "en"}
    assert set(MESSAGES["it"]) == set(MESSAGES["en"]) and MESSAGES["it"]
    for chiave, it in MESSAGES["it"].items():
        en = MESSAGES["en"][chiave]
        assert set(re.findall(r"{(\w+)}", it)) == set(re.findall(r"{(\w+)}", en)), chiave


def test_tm_formatta_nella_lingua_e_cade_sull_inglese():
    assert tm("en", "done_text", done=3, total=4, valid=2, path="/x", tail="") == \
        "Atlas generated.\nOrder layers processed: 3/4\nSheets with a valid dating: 2\nSaved in: /x"
    assert "Salvate in: /x" in tm("it", "done_text", done=3, total=4, valid=2, path="/x", tail="")
    assert tm("de", "folder") == tm("en", "folder")
    assert tm("it", "chiave_che_non_esiste") == "chiave_che_non_esiste"


def test_gli_anni_della_cronologia_assoluta_arrivano_oltre_il_2010():
    """Il massimo delle due caselle era 2010: il 2022 dell'età contemporanea
    non ci entrava."""
    testo = UI.read_text(encoding="utf-8")
    for nome in ("spinBox_cron_iniz", "spinBox_cron_fin"):
        blocco = testo[testo.index('name="%s"' % nome):]
        massimo = int(re.search(r"<property name=\"maximum\">\s*<number>(-?\d+)</number>", blocco).group(1))
        assert massimo >= 2100, (nome, massimo)
