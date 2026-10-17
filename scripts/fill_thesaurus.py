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

sys.path.insert(0, str(RADICE))
from modules.utility.site_toponyms import NAZIONI_IT, PROVINCE_IT, REGIONI_IT  # noqa: E402

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
    # I toponimi della scheda sito passano dal thesaurus (Enzo, 17 ottobre
    # 2026): prima regione e provincia erano elenchi scritti nella scheda.
    # Le sigle sono quelle delle targhe e tre lettere per le regioni:
    # uniche per codice, come vuole il vincolo del thesaurus su PostgreSQL.
    ("site_table", "1.2"): ("Nazione", NAZIONI_IT),
    ("site_table", "1.3"): ("Regione", REGIONI_IT),
    ("site_table", "1.4"): ("Provincia", PROVINCE_IT),
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

    # 7.2 è lo **stato di conservazione**: la scheda lo mette in
    # `comboBox_conservazione_taf`, colonna `stato_di_conservazione`, e i
    # record ci scrivono «Buono», «Scarso». Qui era «Tipo di copertura», con
    # lastre litiche e coppi: la copertura è il 7.3 (`copertura_tipo`).
    ("tomba_table", "7.2"): ("Stato di conservazione", [
        "Ottimo", "Buono", "Discreto", "Scarso", "Non determinabile"]),
    # 7.8 è **area**, non il corredo: lo dice `SYNCHRONIZED_FIELDS` in
    # `tabs/Thesaurus.py`, dove `('tomba_table', '7.8')` sta nel gruppo
    # «area» insieme a `us_table 2.43` e `individui_table 8.6`. Quel
    # gruppo è la fonte: i campi che vi stanno dentro devono mostrare le
    # **stesse** voci in tutte le schede, se no la stessa area si chiama
    # in due modi a seconda della scheda da cui la si guarda.
    ("tomba_table", "7.8"): ("Area", AREE),

    # --- Reperti: le quattro tabelle dentro la scheda ------------------
    # Non sono menu della scheda ma **delegati di colonna**:
    # `tableWidget_elementi_reperto` col 0 ← 3.4,
    # `tableWidget_tecnologie` col 0..3 ← 3.7, 3.8, 3.9, 3.10.
    # Senza di loro la cella non offre niente e il campo resta vuoto.
    ("inventario_materiali_table", "3.4"): ("Elemento rinvenuto", [
        "Orlo", "Ansa", "Fondo", "Parete", "Collo", "Piede", "Spalla",
        "Carena", "Presa", "Beccuccio", "Coperchio", "Puntale"]),
    ("inventario_materiali_table", "3.7"): ("Tipo di tecnologia", [
        "Vernice nera", "Vernice rossa", "Ingobbio", "Sigillata",
        "Invetriatura", "Smalto", "Dipintura", "Stralucido",
        "Lisciatura", "Steccatura", "Impressione", "Graffito"]),
    ("inventario_materiali_table", "3.8"): ("Posizione della tecnologia", [
        "Superficie interna", "Superficie esterna", "Orlo", "Fondo",
        "Parete interna", "Parete esterna", "Su tutta la superficie",
        "Ansa", "Non determinabile"]),
    ("inventario_materiali_table", "3.9"): ("Tipo di quantità", [
        "Numero di frammenti", "Numero di esemplari", "Peso",
        "Numero minimo di individui", "Percentuale di superficie"]),
    # Qui la scheda mostra `sigla`, non `sigla_estesa`
    # (`delegateUnMis.def_values(valueunmis)` legge `.sigla`): la voce è
    # la coppia (sigla, nome), e nella cella si legge «nr», «g», «cm».
    ("inventario_materiali_table", "3.10"): ("Unità di misura", [
        ("nr", "Numero"), ("g", "Grammi"), ("kg", "Chilogrammi"),
        ("cm", "Centimetri"), ("mm", "Millimetri"),
        ("%", "Percentuale")]),

    # --- Strutture: sei delegati di colonna ---------------------------
    ("struttura_table", "6.9"): ("Elementi architettonici", [
        "Muro", "Paramento", "Fondazione", "Zoccolo", "Arco", "Volta",
        "Pilastro", "Colonna", "Soglia", "Stipite", "Architrave",
        "Gradino", "Pavimento", "Copertura"]),
    ("struttura_table", "6.10"): ("Fattori agenti sul degrado", [
        "Umidità di risalita", "Dilavamento", "Gelo",
        "Vegetazione infestante", "Radici", "Crollo", "Spoliazione",
        "Attività antropica", "Escursione termica", "Salinizzazione"]),
    ("struttura_table", "6.11"): ("Prospetto", [
        "Nord", "Sud", "Est", "Ovest", "Nord-est", "Nord-ovest",
        "Sud-est", "Sud-ovest", "Interno", "Esterno"]),
    ("struttura_table", "6.12"): ("Elemento costitutivo", [
        "Laterizio", "Pietra sbozzata", "Pietra squadrata", "Ciottolo",
        "Scaglia lapidea", "Malta di calce", "Malta di terra",
        "Cocciopesto", "Intonaco", "Tegola", "Coppo", "Legno"]),
    ("struttura_table", "6.13"): ("Manufatto", [
        "Macina", "Focolare", "Vasca", "Canaletta", "Pozzo", "Cisterna",
        "Mangiatoia", "Banco di lavoro", "Dolio infisso",
        "Soglia lavorata"]),
    ("struttura_table", "6.14"): ("Definizione e fasi funzionali", [
        "Costruzione", "Uso", "Rifacimento", "Ampliamento",
        "Tamponatura", "Restauro", "Riuso", "Abbandono", "Crollo",
        "Spoliazione"]),

    # --- TMA: la scheda ICCD dei materiali ----------------------------
    # `tabs/Tma.py` li chiedeva coi **nomi visualizzati**
    # («TMA materiali archeologici»), che non sono nomi di tabella: la
    # fonte è `TABLE_DISPLAY_MAPPING_I18N` in `tabs/Thesaurus.py`, e dice
    # `tma_materiali_archeologici` / `tma_materiali_ripetibili`. Due di
    # questi vocabolari li chiede anche la scheda Reperti (10.4 per la
    # datazione, 10.12 per la precisazione tipologica).
    ("tma_materiali_archeologici", "10.1"): ("Denominazione collocazione", [
        "Deposito di scavo", "Magazzino comunale",
        "Magazzino della soprintendenza", "Museo civico",
        "Laboratorio di restauro", "Deposito universitario"]),
    ("tma_materiali_archeologici", "10.2"): ("Tipologia collocazione", [
        "Magazzino", "Museo", "Deposito", "Laboratorio",
        "Esposizione permanente", "Cassaforte"]),
    ("tma_materiali_archeologici", "10.3"): ("Località", [
        "Volterra", "Vallebuona", "Acropoli", "Teatro romano",
        "Porta all'Arco", "Necropoli del Portone"]),
    ("tma_materiali_archeologici", "10.4"): ("Fascia cronologica", [
        "Preistoria", "Protostoria", "Età del Bronzo",
        "Età del Ferro", "Età etrusca", "Età romana",
        "Tarda antichità", "Alto medioevo", "Basso medioevo",
        "Età moderna", "Età contemporanea"]),
    ("tma_materiali_archeologici", "10.5"): ("Denominazione scavo", [
        "Scavo archeologico", "Saggio di verifica",
        "Assistenza archeologica", "Scavo d'emergenza",
        "Ricognizione di superficie"]),
    ("tma_materiali_archeologici", "10.6"): ("Tipo di acquisizione", [
        "Scavo stratigrafico", "Ricognizione di superficie",
        "Recupero", "Sequestro", "Donazione", "Acquisto",
        "Rinvenimento fortuito"]),
    ("tma_materiali_archeologici", "10.7"): ("Area", AREE),
    ("tma_materiali_archeologici", "10.9"): ("Tipo di fotografia", [
        "Fotografia digitale", "Fotografia di dettaglio",
        "Fotografia d'insieme", "Fotopiano", "Macrofotografia",
        "Fotografia di cantiere"]),
    ("tma_materiali_archeologici", "10.15"): ("Settore", [
        "A", "B", "C", "D", "E"]),
    # Le quattro tendine della tabella dei materiali ripetibili della TMA:
    # categoria, classe, precisazione, definizione. `tabs/Tma.py` le
    # chiede con `thesaurus_map` dentro `load_thesaurus_values`, e la
    # tabella la compone a runtime — per questo il censimento delle
    # coppie scritte a mano non le vedeva.
    ("tma_materiali_ripetibili", "10.10"): ("Categoria del materiale", [
        "Ceramica", "Vetro", "Metallo", "Osso", "Pietra", "Laterizio",
        "Intonaco", "Malta", "Materiale organico"]),
    ("tma_materiali_ripetibili", "10.11"): ("Classe", [
        "Ceramica fine", "Ceramica grezza", "Ceramica da fuoco",
        "Ceramica invetriata", "Maiolica", "Terra sigillata",
        "Anfore", "Laterizi da copertura", "Vetro da mensa",
        "Metallo da costruzione"]),
    ("tma_materiali_ripetibili", "10.13"): ("Definizione", [
        "Frammento di parete", "Frammento di orlo", "Frammento di fondo",
        "Frammento di ansa", "Esemplare integro", "Frammento di tegola",
        "Frammento di coppo", "Chiodo", "Lamina", "Scoria"]),
    ("tma_materiali_ripetibili", "10.12"): ("Precisazione tipologica", [
        "Olla", "Olpe", "Anfora", "Coppa", "Piatto", "Scodella",
        "Brocca", "Boccale", "Bicchiere", "Tegame", "Catino",
        "Lucerna", "Dolio", "Mortaio"]),
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
                # Una voce è il testo del menu, oppure la coppia
                # (sigla, testo) quando la scheda mostra `sigla` invece di
                # `sigla_estesa` — è il caso dell'unità di misura dei
                # reperti, dove nella cella si deve leggere «nr», non
                # «Num».
                if isinstance(voce, (tuple, list)):
                    breve, estesa = voce[0], voce[1]
                else:
                    breve, estesa = voce[:3].upper(), voce
                conn.execute(
                    "INSERT INTO pyarchinit_thesaurus_sigle"
                    " (id_thesaurus_sigle, nome_tabella, sigla,"
                    "  sigla_estesa, descrizione, tipologia_sigla, lingua)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (prossimo, tabella, breve, estesa,
                     "%s — %s" % (che_cosa, estesa), sigla, LINGUA))
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
