#!/usr/bin/env python3
"""Riempie i vocabolari che le schede chiedono e il thesaurus non ha.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fill_thesaurus.py

Le schede interrogano `pyarchinit_thesaurus_sigle` con `{'nome_tabella':
"'" + 'tomba_table' + "'", 'tipologia_sigla': "'" + '7.1' + "'"}` e mettono
nel menu a tendina il campo `sigla_estesa`. Dove quella coppia non c'è, il
menu esce **vuoto**.

Che cosa sia ogni sigla non sta scritto da nessuna parte: si legge dal
codice, dal nome del menu che riempie — `6.15` è
`comboBox_sviluppo_planimetrico`, `8.1` è `comboBox_posizione_cranio`. Le
voci qui sotto sono quelle, in italiano, con i termini che un archeologo si
aspetta di trovare.

Idempotente: una coppia che c'è già non si tocca.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
LINGUA = "IT"

#: Le aree dello scavo. Una lista sola, usata da tutte le schede che hanno
#: un campo «area»: `tabs/Thesaurus.py` le tiene sincronizzate
#: (`SYNCHRONIZED_FIELDS['area']`), e scriverne due versioni diverse
#: vorrebbe dire che la stessa area si chiama in due modi a seconda della
#: scheda da cui la si guarda.
AREE = ["1", "2", "3", "4", "5"]

#: (nome_tabella, sigla) -> (che cos'è, le voci del menu)
#:
#: Il «che cos'è» finisce in `tipologia_sigla` leggibile e nella
#: descrizione: serve a chi aprirà il thesaurus fra un anno e si chiederà
#: cosa sia «8.4».
VOCABOLARI = {
    ("campioni_table", "4.1"): ("Tipo di campione", [
        "Carbone", "Terreno", "Malta", "Osso animale", "Osso umano",
        "Intonaco", "Semi carbonizzati", "Ceramica", "Metallo",
        "Sedimento", "Legno", "Pollini"]),

    ("documentazione_table", "9.1"): ("Tipo di documentazione", [
        "Planimetria", "Sezione", "Prospetto", "Fotopiano", "Diario",
        "Modello tridimensionale", "Tavola dei materiali",
        "Documentazione fotografica"]),
    ("documentazione_table", "9.2"): ("Sorgente della documentazione", [
        "Rilievo diretto", "Fotogrammetria", "Fotogrammetria da drone",
        "Laser scanner", "Disegno al tratto", "Compilazione diretta",
        "Stazione totale", "GNSS"]),

    ("individui_table", "8.1"): ("Posizione del cranio", [
        "In asse", "Ruotato a destra", "Ruotato a sinistra",
        "Reclinato in avanti", "Reclinato all'indietro", "Non determinabile",
        "Assente"]),
    ("individui_table", "8.2"): ("Posizione dello scheletro", [
        "Supino", "Prono", "Decubito laterale destro",
        "Decubito laterale sinistro", "Rannicchiato", "Seduto",
        "Non determinabile"]),
    ("individui_table", "8.3"): ("Orientamento dell'asse", [
        "N-S", "S-N", "E-W", "W-E", "NE-SW", "SW-NE", "NW-SE", "SE-NW",
        "Non determinabile"]),
    ("individui_table", "8.4"): ("Posizione degli arti superiori", [
        "Distesi lungo i fianchi", "Flessi sul bacino", "Flessi sul torace",
        "Incrociati sul bacino", "Incrociati sul torace", "Asimmetrici",
        "Non determinabile"]),
    ("individui_table", "8.5"): ("Posizione degli arti inferiori", [
        "Distesi e paralleli", "Distesi e incrociati", "Flessi a destra",
        "Flessi a sinistra", "Iperflessi", "Non determinabile"]),
    ("individui_table", "8.6"): ("Area", AREE),
    ("individui_table", "801.801"): ("Sì / No", ["Sì", "No"]),

    ("inventario_lapidei_table", "5.1"): ("Tipologia del lapideo", [
        "Architettonico", "Epigrafico", "Scultoreo", "Strumentale",
        "Funerario", "Decorativo", "Non determinabile"]),
    ("inventario_lapidei_table", "5.2"): ("Materiale del lapideo", [
        "Calcare", "Marmo bianco", "Marmo colorato", "Travertino", "Tufo",
        "Panchina", "Granito", "Basalto", "Arenaria", "Alabastro"]),
    ("inventario_lapidei_table", "5.3"): ("Oggetto lapideo", [
        "Base di colonna", "Rocchio di colonna", "Capitello", "Architrave",
        "Cornice", "Soglia", "Lastra pavimentale", "Cippo", "Mortaio",
        "Macina", "Blocco squadrato", "Frammento non determinabile"]),

    ("inventario_materiali_table", "3.11"): ("Area", AREE),
    ("inventario_materiali_table", "3.13"): ("Anno", [
        str(a) for a in range(2010, 2027)]),
    ("inventario_materiali_table", "3.14"): ("Compilatore", [
        "Marta Benedetti", "Luca Ferraris", "Chiara Mancuso",
        "Davide Rinaldi", "Paola Donati"]),

    ("struttura_table", "6.15"): ("Sviluppo planimetrico", [
        "Rettilineo", "Curvilineo", "Absidato", "Rettangolare",
        "Quadrangolare", "Circolare", "Irregolare", "Non determinabile"]),

    ("tomba_table", "7.2"): ("Tipo di copertura", [
        "Lastre litiche", "Cassa in laterizi", "Coppi", "Terra di riempimento",
        "Assente", "Non determinabile"]),
    # 7.8 è **area**, non il corredo: lo dice `SYNCHRONIZED_FIELDS` in
    # `tabs/Thesaurus.py`, dove `('tomba_table', '7.8')` sta nel gruppo
    # «area» insieme a `us_table 2.43` e `individui_table 8.6`. Quel
    # gruppo è la fonte: i campi che vi stanno dentro devono mostrare le
    # **stesse** voci in tutte le schede, se no la stessa area si chiama
    # in due modi a seconda della scheda da cui la si guarda.
    ("tomba_table", "7.8"): ("Area", AREE),
}


def main() -> int:
    if not DB.is_file():
        raise SystemExit("manca %s" % DB)
    conn = sqlite3.connect(DB)
    try:
        esistono = {
            (t, s) for t, s in conn.execute(
                "SELECT nome_tabella, tipologia_sigla"
                " FROM pyarchinit_thesaurus_sigle WHERE lingua = ?",
                (LINGUA,))}
        prossimo = (conn.execute(
            "SELECT COALESCE(MAX(id_thesaurus_sigle), 0)"
            " FROM pyarchinit_thesaurus_sigle").fetchone()[0] or 0) + 1

        aggiunti = 0
        for (tabella, sigla), (che_cosa, voci) in sorted(VOCABOLARI.items()):
            if (tabella, sigla) in esistono:
                print("  %-28s %-9s già presente" % (tabella, sigla))
                continue
            for n, voce in enumerate(voci, start=1):
                conn.execute(
                    "INSERT INTO pyarchinit_thesaurus_sigle"
                    " (id_thesaurus_sigle, nome_tabella, sigla,"
                    "  sigla_estesa, descrizione, tipologia_sigla, lingua)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (prossimo, tabella, voce[:3].upper(), voce,
                     "%s — %s" % (che_cosa, voce), sigla, LINGUA))
                prossimo += 1
                aggiunti += 1
            print("  %-28s %-9s +%d voci (%s)"
                  % (tabella, sigla, len(voci), che_cosa))
        conn.commit()
        print("aggiunte %d voci in tutto" % aggiunti)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
