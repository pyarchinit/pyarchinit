"""Chi sta in quale area: completare ``area`` e ``sito`` nei rapporti.

Segnalato da Enzo l'11 ottobre 2026: «quando si hanno più aree, il bottone
che deve riempire le due colonne mancanti area e sito… se US 1 in area 1
copre US 9 in area 2, il reciproco dovrà scrivere US 9 area 2 "coperto da
US 1 area 1". Nel farlo è andato poi a scrivere l'area sbagliata».

Non si sbagliava. Misurato sul DB di prova che ha in mano, il bottone
«Aggiorna Area/Sito nei rapporti» (Ctrl+U) faceva **due** cose sbagliate:

1. ``update_rapporti_col`` riempiva la forma corta ``['Copre', '9']`` con
   l'area **della scheda**, anche quando la US 9 in quell'area non esiste;
2. ``find_correct_area_for_us`` cercava l'area con ``WHERE us = ? AND
   sito = ?`` e prendeva la **prima** riga — e poi riscriveva la colonna
   area **anche** dove era già giusta. Sul DB di prova, dove US 1 e US 9
   esistono in area 1 e in area 2, le due relazioni dell'area 2
   (``['Copre', '9', '2']`` e ``['Coperto da', '1', '2']``) diventavano
   entrambe area 1: la scheda dell'area 2 finiva a parlare delle unità
   dell'area 1.

La regola che vale, e che questi test fissano: l'identità di una scheda è
``UniqueConstraint('sito', 'area', 'us', 'unita_tipo')``, quindi un
rapporto senza area non nomina una riga. Si completa così — l'area della
scheda se l'unità collegata esiste lì (è la convenzione del formato corto,
la stratigrafia si osserva dentro un'area), altrimenti l'unica area in cui
quell'unità esiste, altrimenti **niente**: un'area inventata è peggio di
una colonna vuota. E un'area che nomina una riga che esiste non si tocca.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from modules.utility.rapporti_entries import (  # noqa: E402
    AMBIGUA, INESISTENTE, STESSA_AREA, UNICA, completa_rapporti,
    indice_aree, leggi_riga_reciproco, risolvi_area)

SORGENTE = RADICE / "tabs" / "US_USM.py"


# --------------------------------------------------------------------------
# risolvi_area: quale area si scrive
# --------------------------------------------------------------------------

def test_lunita_collegata_esiste_nella_mia_area_e_quella_vince():
    """La convenzione del formato corto: «stessa area di chi la cita»."""
    assert risolvi_area("9", "1", {"1", "2"}) == ("1", STESSA_AREA)


def test_se_sta_solo_altrove_si_scrive_quellaltra_area():
    """Il caso di Enzo: US 1 in area 1 copre US 9, che sta in area 2."""
    assert risolvi_area("9", "1", {"2"}) == ("2", UNICA)


def test_due_aree_e_nessuna_e_la_mia_non_si_decide():
    """Inventare vuol dire collegare la scheda all'unità sbagliata."""
    assert risolvi_area("9", "1", {"2", "3"}) == (None, AMBIGUA)


def test_ununita_che_non_esiste_non_ha_area():
    assert risolvi_area("9", "1", set()) == (None, INESISTENTE)


def test_le_aree_si_confrontano_strisciate():
    """``area`` è testo battuto a mano: ``'1 '`` è l'area 1."""
    assert risolvi_area("9", " 1", {"1 ", ""}) == ("1", STESSA_AREA)


def test_indice_aree_raccoglie_le_aree_di_ogni_numero():
    idx = indice_aree([("1", "1"), ("9", "1"), ("9", "2"), (9, 3)])
    assert idx["9"] == {"1", "2", "3"}
    assert idx["1"] == {"1"}


# --------------------------------------------------------------------------
# completa_rapporti: la colonna area e la colonna sito
# --------------------------------------------------------------------------

AREE = {"9": {"2"}, "1": {"1"}}


def test_la_forma_corta_prende_larea_vera_dellunita_collegata():
    """US 1 in area 1 copre US 9, che sta in area 2 — l'esempio di Enzo."""
    fuori, irrisolti = completa_rapporti(
        [["Copre", "9"]], area_scheda="1", sito="Scavo", aree_per_us=AREE)
    assert fuori == [["Copre", "9", "2", "Scavo"]]
    assert irrisolti == []


def test_unarea_che_nomina_una_riga_esistente_non_si_tocca():
    """Il guasto peggiore: riscriveva anche quello che era già giusto.

    Sul DB di prova US 9 esiste in area 1 e in area 2; la scheda US 1
    dell'area 2 dichiara ``['Copre', '9', '2']``, ed è esatto.
    """
    aree = {"9": {"1", "2"}}
    fuori, irrisolti = completa_rapporti(
        [["Copre", "9", "2", "Scavo"]], area_scheda="2", sito="Scavo",
        aree_per_us=aree)
    assert fuori == [["Copre", "9", "2", "Scavo"]]
    assert irrisolti == []


def test_unarea_che_non_nomina_nessuna_riga_si_corregge():
    fuori, _ = completa_rapporti(
        [["Copre", "9", "7", "Scavo"]], area_scheda="1", sito="Scavo",
        aree_per_us=AREE)
    assert fuori == [["Copre", "9", "2", "Scavo"]]


def test_quando_non_si_decide_la_colonna_resta_e_si_segnala():
    aree = {"9": {"2", "3"}}
    fuori, irrisolti = completa_rapporti(
        [["Copre", "9"]], area_scheda="1", sito="Scavo", aree_per_us=aree)
    assert fuori == [["Copre", "9", "", "Scavo"]]
    assert irrisolti == [("9", AMBIGUA, "")]


def test_ununita_inesistente_si_segnala_senza_inventare_larea():
    fuori, irrisolti = completa_rapporti(
        [["Taglia", "77"]], area_scheda="1", sito="Scavo", aree_per_us=AREE)
    assert fuori == [["Taglia", "77", "", "Scavo"]]
    assert irrisolti == [("77", INESISTENTE, "")]


def test_il_sito_si_scrive_sempre():
    fuori, _ = completa_rapporti(
        [["Copre", "9", "2", "Altro"]], area_scheda="1", sito="Scavo",
        aree_per_us=AREE)
    assert fuori[0][3] == "Scavo"


def test_le_voci_che_non_nominano_nessuna_us_si_buttano():
    """Una riga vuota lasciata nella tabella della scheda non è un rapporto."""
    fuori, _ = completa_rapporti(
        [[], ["Copre"], ["Copre", "9"]], area_scheda="1", sito="Scavo",
        aree_per_us=AREE)
    assert fuori == [["Copre", "9", "2", "Scavo"]]


def test_oltre_la_colonna_sito_non_si_tiene_niente():
    fuori, _ = completa_rapporti(
        [["Copre", "9", "2", "Scavo", "avanzo"]], area_scheda="1",
        sito="Scavo", aree_per_us=AREE)
    assert fuori == [["Copre", "9", "2", "Scavo"]]


# --------------------------------------------------------------------------
# rapporti2: le stesse due colonne, al sesto e settimo posto
# --------------------------------------------------------------------------

def test_rapporti2_riempie_il_sesto_e_il_settimo_posto():
    voce = ["Copre", "9", "US", "strato", "Periodo I"]
    fuori, _ = completa_rapporti(
        [voce], area_scheda="1", sito="Scavo", aree_per_us=AREE,
        pos_area=5, pos_sito=6)
    assert fuori == [["Copre", "9", "US", "strato", "Periodo I", "2",
                      "Scavo"]]


def test_rapporti2_non_riscrive_unarea_giusta():
    aree = {"9": {"1", "2"}}
    voce = ["Copre", "9", "US", "strato", "Periodo I", "2", "Scavo"]
    fuori, _ = completa_rapporti(
        [voce], area_scheda="2", sito="Scavo", aree_per_us=aree,
        pos_area=5, pos_sito=6)
    assert fuori == [voce]


# --------------------------------------------------------------------------
# leggi_riga_reciproco: la riga del rapporto che il controllo scrive
# --------------------------------------------------------------------------

def test_la_riga_italiana_si_legge_tutta():
    riga = ("Sito: Scavo Archeologico, Area: 1, US: 1 Copre US: 9 Area: 2: "
            "Rapporto reciproco non trovato")
    assert leggi_riga_reciproco(riga) == {
        "sito": "Scavo Archeologico", "area_a": "1", "us_a": "1",
        "rapporto": "Copre", "us_b": "9", "area_b": "2", "unita_tipo": "US"}


def test_la_riga_inglese_si_legge_tutta():
    riga = ("Site: Dig, Area: 1, SU: 1 Covers SU: 9 Area: 2: "
            "Reciprocal relationship not found")
    letto = leggi_riga_reciproco(riga)
    assert (letto["sito"], letto["us_a"], letto["rapporto"], letto["us_b"],
            letto["area_b"]) == ("Dig", "1", "Covers", "9", "2")


def test_la_riga_tedesca_si_legge_tutta():
    """Il vecchio lettore cercava solo SU/US/USM/WSU: su «SE:» alzava
    ValueError e la correzione tedesca non partiva mai."""
    riga = ("Ausgrabungsstätte: Grabung, Areal: 1, SE: 1 Liegt über SE: 9 "
            "Area: 2: Gegenseitiger Bericht nicht gefunden")
    letto = leggi_riga_reciproco(riga)
    assert (letto["sito"], letto["us_a"], letto["rapporto"], letto["us_b"],
            letto["area_b"]) == ("Grabung", "1", "Liegt über", "9", "2")


def test_le_aree_non_numeriche_si_leggono():
    """Il vecchio lettore pretendeva ``\\d+`` e ripiegava sull'area '1'."""
    riga = ("Sito: Scavo, Area: Saggio I, US: 1 Copre US: 9 Area: Saggio II: "
            "Rapporto reciproco non trovato")
    letto = leggi_riga_reciproco(riga)
    assert (letto["area_a"], letto["area_b"]) == ("Saggio I", "Saggio II")


def test_un_sito_col_nome_che_contiene_una_virgola():
    riga = ("Sito: Volterra, Vallebuona, Area: 1, US: 1 Copre US: 9 "
            "Area: 2: Rapporto reciproco non trovato")
    assert leggi_riga_reciproco(riga)["sito"] == "Volterra, Vallebuona"


def test_una_riga_che_non_si_legge_da_niente():
    """Meglio non proporre la correzione che proporla con l'area sbagliata."""
    assert leggi_riga_reciproco("US 1 copre US 9") is None


def test_il_rapporto_di_piu_parole_resta_intero():
    riga = ("Sito: Scavo, Area: 1, US: 1 Si appoggia a US: 9 Area: 2: "
            "Rapporto reciproco non trovato")
    assert leggi_riga_reciproco(riga)["rapporto"] == "Si appoggia a"


# --------------------------------------------------------------------------
# l'innesto nella scheda US, letto dall'albero sintattico
# --------------------------------------------------------------------------

def _corpo(nome: str) -> str:
    albero = ast.parse(SORGENTE.read_text(encoding="utf-8"))
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == nome:
            return ast.get_source_segment(
                SORGENTE.read_text(encoding="utf-8"), nodo) or ""
    raise AssertionError("%s non esiste in US_USM.py" % nome)


def test_i_due_riempitori_passano_dal_modulo_condiviso():
    for nome in ("_update_rapporti_add_area_sito",
                 "_update_rapporti2_add_area_sito", "update_rapporti_col"):
        assert "completa_rapporti" in _corpo(nome), nome


def test_nessuno_cerca_piu_larea_una_riga_per_volta():
    """``find_correct_area_for_us`` rifletteva la tabella a ogni rapporto
    (``Table(..., autoload_with=...)`` dentro il ciclo) e prendeva la prima
    riga che capitava: una query per relazione, e la risposta sbagliata."""
    for nome in ("_update_rapporti_add_area_sito",
                 "_update_rapporti2_add_area_sito"):
        assert "find_correct_area_for_us" not in _corpo(nome), nome


def test_la_correzione_dei_reciproci_cerca_la_scheda_nella_sua_area():
    corpo = _corpo("fix_missing_relationships")
    assert "leggi_riga_reciproco" in corpo
    assert "area_b" in corpo


def test_anche_la_correzione_dei_rapporti_incompleti_passa_di_la():
    corpo = _corpo("fix_incomplete_relationships")
    assert "completa_rapporti" in corpo
    assert "related_records[0].area" not in corpo


def test_il_terzo_correttore_dei_reciproci_non_esiste_piu():
    """``check_inverse_relationships`` aveva lo stesso difetto delle aree —
    cercava la scheda bersaglio nell'area di **chi dichiara** il rapporto —
    e non si raggiungeva: nessuno la chiamava, e le righe che pretendeva
    («relationships not verified») le scriveva la vecchia
    `rapporti_stratigrafici_check`, commentata da tempo. Invece di
    correggere codice morto, via (Enzo l'ha confermato l'11 ottobre 2026).
    """
    testo = SORGENTE.read_text(encoding="utf-8")
    assert "check_inverse_relationships" not in testo
    produttori = [r for r in testo.splitlines()
                  if "relationships not verified" in r
                  and not r.lstrip().startswith("#")]
    assert produttori == [], produttori


# --------------------------------------------------------------------------
# Sul database di prova che si installa: il bottone, dall'inizio alla fine
# --------------------------------------------------------------------------

PROVA = RADICE / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"
SITO = "Scavo a due aree"


def _dopo_il_bottone():
    """Quello che il bottone scrive su ogni riga del sito di prova.

    È la stessa catena della scheda US — l'indice delle aree con una query,
    poi :func:`completa_rapporti` riga per riga — senza il giro per Qt:
    ``tabs/US_USM.py`` non si importa sotto pytest.
    """
    import ast as _ast
    import sqlite3

    conn = sqlite3.connect("file:%s?mode=ro" % PROVA, uri=True)
    try:
        righe = conn.execute(
            "SELECT area, us, rapporti FROM us_table WHERE sito = ?",
            (SITO,)).fetchall()
    finally:
        conn.close()
    aree = indice_aree([(u, a) for a, u, _r in righe])
    fuori, irrisolti = {}, []
    for area, us, rapporti in righe:
        lista = _ast.literal_eval(rapporti) if rapporti else []
        nuovi, non_decisi = completa_rapporti(
            lista, area_scheda=area, sito=SITO, aree_per_us=aree)
        fuori[(str(area), str(us))] = nuovi
        irrisolti.extend(non_decisi)
    return fuori, irrisolti


def test_la_forma_corta_che_esce_dallarea_trova_larea_dellaltro():
    """Caso 11: US 60 area 1 «Copre 61», e la 61 sta solo nell'area 2."""
    fuori, _ = _dopo_il_bottone()
    assert fuori[("1", "60")] == [["Copre", "61", "2", SITO]]


def test_la_scheda_dellarea_2_resta_a_parlare_dellarea_2():
    """La regressione segnalata: il bottone riscriveva area 2 -> area 1
    perché US 1 e US 9 esistono in entrambe le aree, e la ricerca prendeva
    la prima riga."""
    fuori, _ = _dopo_il_bottone()
    assert fuori[("2", "1")] == [["Copre", "9", "2", SITO]]
    assert fuori[("2", "9")] == [["Coperto da", "1", "2", SITO]]


def test_unarea_dichiarata_e_giusta_non_si_tocca_nemmeno_qui():
    """Caso 11: US 62 area 1 copre la US 63 **dell'area 2**, e la US 63
    esiste anche in area 1."""
    fuori, _ = _dopo_il_bottone()
    assert fuori[("1", "62")] == [["Copre", "63", "2", SITO]]


def test_la_forma_corta_dentro_la_propria_area_resta_dove_sta():
    """Caso 3: US 5 area 1 «Coperto da 9» e la US 9 c'è anche in area 1 —
    la convenzione del formato corto vale, ed è l'area 1."""
    fuori, _ = _dopo_il_bottone()
    assert fuori[("1", "5")] == [["Coperto da", "9", "1", SITO]]


def test_sul_sito_di_prova_non_resta_niente_di_indeciso():
    _, irrisolti = _dopo_il_bottone()
    assert irrisolti == []


def test_una_riga_cominciata_e_non_finita_non_si_cancella():
    """La scheda conserva le righe parziali di proposito
    (`table2dict(preserve_empty=True)`, il guasto segnalato da Monica):
    chi ha battuto «Copre» e non ancora il numero non deve vedersela
    sparire perché ha premuto Ctrl+U."""
    fuori, irrisolti = completa_rapporti(
        [["Copre", ""]], area_scheda="1", sito="Scavo", aree_per_us=AREE)
    assert fuori == [["Copre", "", "", "Scavo"]]
    assert irrisolti == []
