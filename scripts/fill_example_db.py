#!/usr/bin/env python3
"""Riempie le schede vuote del database di esempio con dati da provare.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fill_example_db.py

Dieci record per scheda, **tutti i campi compilati**, su «Scavo
archeologico». Dati inventati ma **coerenti**: le presenze citano le persone
che esistono in `personale_table`, i campioni citano US e numeri di
inventario che ci sono davvero, l'antropologia cita i dieci individui di
`individui_table`, la tafonomia le dieci tombe di `tomba_table`. Un
riferimento che non punta a niente non serve a fare prove.

Perché uno script e non un `.sqlite` modificato a mano: così si vede in una
diff **quali** dati ci sono e perché, si rifà quando lo schema cambia, e si
replica sugli altri nove siti tradotti quando serve (`--sito`).

Idempotente: una scheda che ha già dieci record o più non si tocca.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"

#: Quanti record per scheda.
QUANTI = 10

#: L'angolo sud-ovest del saggio **vero** del database di esempio, in
#: EPSG:3004 (Monte Mario / Italia zona 2). Si legge dall'estensione di
#: `pyunitastratigrafiche`, non si inventa: le geometrie aggiunte devono
#: cadere **dentro lo scavo**, non da un'altra parte. La prima versione di
#: questo script le metteva a (1.650.000, 4.810.000), cioè seicentosettanta
#: chilometri più in là, e aprendo i layer non si vedeva niente vicino alla
#: pianta.
EST, NORD = 2_324_920.5, 4_881_955.2
#: Quanto è grande il saggio: 5,4 m per 6,4 m.
LARG, ALT = 5.4, 6.4


def _dentro(i: int, quanti: int = 10):
    """Un punto dentro il saggio, su una griglia che non esce dai bordi."""
    colonne = 5
    righe = max(1, (quanti + colonne - 1) // colonne)
    x = EST + LARG * (0.12 + 0.76 * ((i % colonne) / (colonne - 1.0)))
    y = NORD + ALT * (0.12 + 0.76 * ((i // colonne) / max(1.0, righe - 1.0)))
    return x, y


def _attorno(i: int, raggio: float = 60.0, quanti: int = 10):
    """Un punto attorno allo scavo, per quello che sta nel paesaggio."""
    import math
    angolo = 2.0 * math.pi * i / float(quanti)
    return (EST + LARG / 2.0 + raggio * math.cos(angolo),
            NORD + ALT / 2.0 + raggio * math.sin(angolo))

SPATIALITE = (
    os.environ.get("MOD_SPATIALITE", ""),
    "/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so",
    "/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite.so",
    "mod_spatialite", "mod_spatialite.so", "libspatialite.so.7",
)

_INIZIO = date(2026, 5, 4)


def _data(giorno: int) -> str:
    return (_INIZIO + timedelta(days=giorno)).isoformat()


def _uuid(tabella: str, n: int) -> str:
    """Un uuid stabile: rifare il riempimento non cambia gli identificativi."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          "pyarchinit/%s/%s/%d" % (SITO, tabella, n)))


# --- le dieci persone, da cui pendono presenze e attrezzature -------------
PERSONE = [
    ("Marta", "Benedetti", "Direttore scientifico", "Archeologa",
     "direzione", 42.0, 336.0),
    ("Luca", "Ferraris", "Responsabile di scavo", "Archeologo",
     "coordinamento", 31.0, 248.0),
    ("Chiara", "Mancuso", "Archeologa di settore", "Archeologa",
     "scavo", 24.0, 192.0),
    ("Davide", "Rinaldi", "Archeologo di settore", "Archeologo",
     "scavo", 24.0, 192.0),
    ("Sara", "Lombardi", "Topografa", "Topografa",
     "rilievo", 27.0, 216.0),
    ("Nicola", "Esposito", "Disegnatore", "Disegnatore tecnico",
     "documentazione", 22.0, 176.0),
    ("Elena", "Vitali", "Antropologa", "Antropologa fisica",
     "laboratorio", 28.0, 224.0),
    ("Giovanni", "Serra", "Archeozoologo", "Archeozoologo",
     "laboratorio", 28.0, 224.0),
    ("Paola", "Donati", "Restauratrice", "Restauratrice",
     "laboratorio", 26.0, 208.0),
    ("Matteo", "Guerrini", "Operaio specializzato", "Operaio",
     "scavo", 18.0, 144.0),
]


def personale(_rif) -> list:
    righe = []
    for i, (nome, cognome, ruolo, qualifica, _reparto, oraria,
            giornaliera) in enumerate(PERSONE):
        iniziali = (cognome[:3] + nome[:3]).upper()
        righe.append({
            "sito": SITO, "nome": nome, "cognome": cognome, "ruolo": ruolo,
            "qualifica": qualifica,
            "codice_fiscale": "%sX%02dA000%s" % (iniziali, 60 + i,
                                                 "ABCDEFGHIJ"[i]),
            "email": "%s.%s@esempio.it" % (nome.lower(), cognome.lower()),
            "telefono": "+39 055 %06d" % (430000 + i * 37),
            "data_nascita": date(1972 + i, 1 + i % 12, 1 + i * 2).isoformat(),
            "indirizzo": "Via dei Cipressi %d, 56048 Volterra (PI)" % (3 + i),
            "tipo_contratto": ("Tempo indeterminato" if i < 2
                               else "Collaborazione a progetto"),
            "data_inizio_contratto": _data(0),
            "data_fine_contratto": _data(120),
            "tariffa_oraria": oraria, "tariffa_giornaliera": giornaliera,
            "iban": "IT%02dX0542811101000000%06d" % (10 + i, 123400 + i),
            "note": "Campagna 2026, settore %d." % (1 + i % 3),
            "attivo": 1,
            "entity_uuid": _uuid("personale_table", i),
        })
    return righe


def presenze(rif) -> list:
    """Una giornata per persona, con le ore che tornano col costo."""
    righe = []
    for i, id_pers in enumerate(rif["personale"][:QUANTI]):
        ordinarie = 8.0 if i % 4 else 6.0
        straordinario = 1.5 if i % 3 == 0 else 0.0
        tariffa = PERSONE[i][5]
        righe.append({
            "sito": SITO, "id_personale": id_pers, "data": _data(7 + i),
            "ora_ingresso": "08:00",
            "ora_uscita": "%02d:30" % (14 + int(ordinarie + straordinario) - 6),
            "ore_ordinarie": ordinarie, "ore_straordinario": straordinario,
            "tipo_giornata": "Scavo" if i % 2 else "Laboratorio",
            "turno": "Mattina" if i % 2 else "Giornata intera",
            "area_lavoro": "Area 1 - settore %d" % (1 + i % 3),
            "note": "Presenza regolare.",
            "costo_giornata": round(
                ordinarie * tariffa + straordinario * tariffa * 1.3, 2),
            "entity_uuid": _uuid("presenze_table", i),
        })
    return righe


def attrezzature(rif) -> list:
    beni = [
        ("Stazione totale", "Topografia", "Leica", "TS16", 24800.0, 95.0),
        ("Livello ottico", "Topografia", "Leica", "NA532", 980.0, 12.0),
        ("Ricevitore GNSS", "Topografia", "Emlid", "Reach RS2+", 2400.0, 40.0),
        ("Fotocamera reflex", "Documentazione", "Nikon", "D7500", 1150.0, 18.0),
        ("Drone", "Documentazione", "DJI", "Mini 4 Pro", 1099.0, 60.0),
        ("Metal detector", "Prospezione", "Minelab", "Equinox 800", 1049.0, 20.0),
        ("Setaccio a colonna", "Laboratorio", "Retsch", "AS 200", 3200.0, 15.0),
        ("Microscopio stereo", "Laboratorio", "Zeiss", "Stemi 305", 2750.0, 25.0),
        ("Gruppo elettrogeno", "Cantiere", "Honda", "EU22i", 1490.0, 22.0),
        ("Tenda da cantiere", "Cantiere", "Ferrino", "Base Camp", 620.0, 8.0),
    ]
    righe = []
    for i, (nome, cat, marca, modello, costo, noleggio) in enumerate(beni):
        righe.append({
            "sito": SITO,
            "codice_inventario": "ATT-2026-%03d" % (i + 1),
            "nome": nome, "categoria": cat, "marca": marca,
            "modello": modello,
            "numero_serie": "%s%06d" % (marca[:2].upper(), 100200 + i * 13),
            "proprieta": "Proprietà della missione" if i % 3 else "Noleggio",
            "data_acquisto": date(2022 + i % 4, 1 + i % 12, 10).isoformat(),
            "costo_acquisto": costo, "costo_noleggio_giorno": noleggio,
            "stato": "In uso" if i % 4 else "In manutenzione",
            "assegnato_a": rif["personale"][i % len(rif["personale"])],
            "data_ultima_manutenzione": _data(-30 - i),
            "data_prossima_manutenzione": _data(300 - i),
            "note": "Verificata a inizio campagna.",
            "entity_uuid": _uuid("attrezzature_table", i),
        })
    return righe


def budget(_rif) -> list:
    voci = [
        ("Personale", "Compensi archeologi di settore", 28000.0, 27450.0,
         "Cooperativa Arcadia", "FT/2026/0141"),
        ("Personale", "Compenso antropologa", 6400.0, 6400.0,
         "Elena Vitali", "FT/2026/0152"),
        ("Attrezzature", "Noleggio stazione totale", 3800.0, 3610.0,
         "Geotop srl", "FT/2026/0163"),
        ("Attrezzature", "Acquisto ricevitore GNSS", 2400.0, 2400.0,
         "Emlid Europe", "FT/2026/0170"),
        ("Analisi", "Datazioni radiocarbonio (6 campioni)", 2700.0, 2890.0,
         "CEDAD Lecce", "FT/2026/0188"),
        ("Analisi", "Archeometria ceramica", 1800.0, 1620.0,
         "Dip. Scienze della Terra", "FT/2026/0191"),
        ("Logistica", "Alloggio équipe", 9200.0, 9050.0,
         "Residenza Le Balze", "FT/2026/0205"),
        ("Logistica", "Trasporti e carburante", 2100.0, 2340.0,
         "Autonoleggio Etruria", "FT/2026/0211"),
        ("Restauro", "Pronto intervento su reperti metallici", 3500.0, 3500.0,
         "Laboratorio Donati", "FT/2026/0224"),
        ("Pubblicazione", "Rilievi e tavole per il volume", 4200.0, 3980.0,
         "Studio Esposito", "FT/2026/0239"),
    ]
    righe = []
    for i, (cat, descr, previsto, effettivo, forn, fattura) in enumerate(voci):
        righe.append({
            "sito": SITO, "anno": 2026, "categoria": cat,
            "descrizione": descr, "importo_previsto": previsto,
            "importo_effettivo": effettivo,
            "data_registrazione": _data(i * 3),
            "data_spesa": _data(i * 3 + 9), "fornitore": forn,
            "numero_fattura": fattura,
            "note": "Scostamento %+.1f%%." % (
                (effettivo - previsto) / previsto * 100.0),
            "entity_uuid": _uuid("budget_table", i),
        })
    return righe


def campioni(rif) -> list:
    tipi = [("Carbone", "Datazione radiocarbonio"),
            ("Terreno", "Analisi palinologica"),
            ("Malta", "Caratterizzazione dei leganti"),
            ("Osso animale", "Analisi isotopica"),
            ("Osso umano", "Datazione e paleodieta"),
            ("Intonaco", "Analisi dei pigmenti"),
            ("Semi carbonizzati", "Archeobotanica"),
            ("Ceramica", "Archeometria degli impasti"),
            ("Metallo", "Analisi metallografica"),
            ("Sedimento", "Micromorfologia")]
    righe = []
    for i, (tipo, scopo) in enumerate(tipi):
        us = rif["us"][i % len(rif["us"])]
        righe.append({
            "sito": SITO, "nr_campione": i + 1, "tipo_campione": tipo,
            "descrizione": "%s prelevato dalla US %s. %s." % (tipo, us, scopo),
            "area": "1", "us": str(us),
            "numero_inventario_materiale":
                rif["inventario"][i % len(rif["inventario"])],
            "nr_cassa": "CS-%02d" % (1 + i // 3),
            "luogo_conservazione": "Deposito comunale di Volterra, scaffale %s"
                                   % "ABCDEFGHIJ"[i],
            "version_number": 1, "editing_by": "pyarchinit_demo",
            "editing_since": _data(i), "audit_trail": None,
            "entity_uuid": _uuid("campioni_table", i),
        })
    return righe


def documentazione(_rif) -> list:
    documenti = [
        ("Pianta di fase 1", "Planimetria", "Rilievo diretto", "1:20"),
        ("Pianta di fase 2", "Planimetria", "Rilievo diretto", "1:20"),
        ("Sezione A-A'", "Sezione", "Rilievo diretto", "1:20"),
        ("Sezione B-B'", "Sezione", "Rilievo diretto", "1:20"),
        ("Prospetto del muro US 14", "Prospetto", "Fotopiano", "1:10"),
        ("Ortofoto di cantiere", "Fotopiano", "Fotogrammetria da drone", "1:50"),
        ("Modello 3D del saggio", "Modello tridimensionale",
         "Fotogrammetria", "—"),
        ("Diario di scavo, settimana 1", "Diario", "Compilazione diretta", "—"),
        ("Diario di scavo, settimana 2", "Diario", "Compilazione diretta", "—"),
        ("Tavola dei materiali diagnostici", "Tavola dei materiali",
         "Disegno al tratto", "1:1"),
    ]
    righe = []
    for i, (nome, tipo, sorgente, scala) in enumerate(documenti):
        righe.append({
            "sito": SITO, "nome_doc": nome, "data": _data(3 + i * 4),
            "tipo_documentazione": tipo, "sorgente": sorgente,
            "scala": scala,
            "disegnatore": "%s %s" % (PERSONE[5][0], PERSONE[5][1]),
            "note": "Archiviato in DosCo/%s." % tipo.lower().replace(" ", "_"),
            "version_number": 1, "editing_by": "pyarchinit_demo",
            "editing_since": _data(3 + i * 4), "audit_trail": None,
            "entity_uuid": _uuid("documentazione_table", i),
        })
    return righe


def computo_metrico(_rif) -> list:
    righe = []
    for i in range(QUANTI):
        # L'area per lo spessore medio fa il volume: i numeri si tengono.
        area = round(18.0 + i * 3.5, 2)
        qmin = round(11.20 + i * 0.35, 2)
        qmax = round(qmin + 0.45 + i * 0.05, 2)
        volume = round(area * (qmax - qmin), 2)
        righe.append({
            "sito": SITO,
            "nome_calcolo": "Asportazione US %d" % (i + 1),
            "tipo_calcolo": "Volume fra due superfici",
            "dem_pre": "dem_us%02d_pre.tif" % (i + 1),
            "dem_post": "dem_us%02d_post.tif" % (i + 1),
            "layer_poligono": "pyunitastratigrafiche",
            "area_mq": area, "volume_mc": volume,
            "quota_min": qmin, "quota_max": qmax,
            "data_calcolo": _data(20 + i * 2),
            "fase_scavo": "Campagna 2026, fase %d" % (1 + i % 4),
            "note": "Spessore medio %.2f m." % (qmax - qmin),
            "entity_uuid": _uuid("computo_metrico_table", i),
        })
    return righe


def inventario_lapidei(_rif) -> list:
    pezzi = [
        ("Base di colonna", "Architettonico", "Calcare", 48.0, 48.0, 22.0),
        ("Rocchio di colonna", "Architettonico", "Calcare", 42.0, 42.0, 55.0),
        ("Capitello corinzio", "Architettonico", "Marmo bianco",
         52.0, 52.0, 46.0),
        ("Soglia", "Architettonico", "Panchina", 118.0, 36.0, 14.0),
        ("Lastra pavimentale", "Architettonico", "Travertino",
         60.0, 60.0, 8.0),
        ("Cippo iscritto", "Epigrafico", "Tufo", 34.0, 28.0, 96.0),
        ("Frammento di cornice", "Architettonico", "Marmo bianco",
         44.0, 19.0, 16.0),
        ("Mortaio", "Strumentale", "Granito", 38.0, 38.0, 24.0),
        ("Macina", "Strumentale", "Basalto", 46.0, 46.0, 12.0),
        ("Blocco squadrato", "Architettonico", "Calcare",
         88.0, 42.0, 40.0),
    ]
    righe = []
    for i, (oggetto, tipologia, materiale, lung, larg, h) in enumerate(pezzi):
        righe.append({
            "sito": SITO, "scheda_numero": i + 1,
            "collocazione": "Deposito comunale, settore lapidario, ripiano %d"
                            % (1 + i // 4),
            "oggetto": oggetto, "tipologia": tipologia,
            "materiale": materiale,
            "d_letto_posa": round(larg * 0.9, 2),
            "d_letto_attesa": round(larg * 0.85, 2),
            "toro": round(min(larg, h) * 0.2, 2),
            "spessore": round(min(larg, h) * 0.5, 2),
            "larghezza": larg, "lunghezza": lung, "h": h,
            "descrizione": "%s in %s, superficie a vista lavorata."
                           % (oggetto, materiale.lower()),
            "lavorazione_e_stato_di_conservazione":
                "Lavorazione a gradina; stato di conservazione %s."
                % ("buono" if i % 3 else "discreto, con scheggiature ai bordi"),
            "confronti": "Confronti con il lapidario di Volterra, inv. %d."
                         % (210 + i * 7),
            "cronologia": "Periodo 2, fase %d" % (1 + i % 4),
            "bibliografia": "Benedetti M. 2026, «Il lapidario», pp. %d-%d."
                            % (40 + i * 6, 44 + i * 6),
            "compilatore": "%s %s" % (PERSONE[0][0], PERSONE[0][1]),
            "entity_uuid": _uuid("inventario_lapidei_table", i),
        })
    return righe


def archeozoology(rif) -> list:
    """I conteggi per US. Le colonne sono quantità, e la somma delle specie
    non può superare il numero di resti determinati."""
    righe = []
    for i in range(QUANTI):
        us = rif["us"][i % len(rif["us"])]
        cervo, capriolo, bos = 6 + i, 3 + i % 4, 2 + i % 3
        righe.append({
            "sito": SITO, "area": "1", "us": int(us),
            "quadrato": "%s%d" % ("ABCDE"[i % 5], 1 + i % 4),
            "coord_x": round(EST + 4.0 + i * 1.6, 3),
            "coord_y": round(NORD - 3.0 - i * 1.2, 3),
            "coord_z": round(12.40 + i * 0.18, 3),
            "bos_bison": bos, "calcinati": 1 + i % 3,
            "camoscio": i % 2, "capriolo": capriolo, "cervo": cervo,
            "combusto": 2 + i % 4, "coni": i % 3, "pdi": 4 + i % 5,
            "stambecco": i % 2, "strie": 1 + i % 4,
            "canidi": i % 3, "ursidi": 1 if i == 4 else 0,
            "megacero": 0,
            "version_number": 1, "editing_by": "pyarchinit_demo",
            "editing_since": _data(30 + i), "audit_trail": None,
            "entity_uuid": _uuid("archeozoology_table", i),
        })
    return righe


#: Specie, classe, ordine, famiglia: una tassonomia che sta in piedi.
TAXA = [
    ("Bos taurus", "Mammalia", "Artiodactyla", "Bovidae", "Grande"),
    ("Ovis aries", "Mammalia", "Artiodactyla", "Bovidae", "Media"),
    ("Capra hircus", "Mammalia", "Artiodactyla", "Bovidae", "Media"),
    ("Sus domesticus", "Mammalia", "Artiodactyla", "Suidae", "Media"),
    ("Cervus elaphus", "Mammalia", "Artiodactyla", "Cervidae", "Grande"),
    ("Capreolus capreolus", "Mammalia", "Artiodactyla", "Cervidae", "Media"),
    ("Equus caballus", "Mammalia", "Perissodactyla", "Equidae", "Grande"),
    ("Canis familiaris", "Mammalia", "Carnivora", "Canidae", "Media"),
    ("Oryctolagus cuniculus", "Mammalia", "Lagomorpha", "Leporidae", "Piccola"),
    ("Gallus gallus", "Aves", "Galliformes", "Phasianidae", "Piccola"),
]

OSSA = [("Omero", "Epifisi distale"), ("Femore", "Diafisi"),
        ("Tibia", "Epifisi proximale"), ("Mandibola", "Ramo orizzontale"),
        ("Scapola", "Cavità glenoidea"), ("Metacarpo", "Completo"),
        ("Radio", "Diafisi"), ("Astragalo", "Completo"),
        ("Costa", "Porzione mediale"), ("Cranio", "Frammento di parietale")]


def fauna_lista(rif) -> list:
    """La scheda `fauna`: un resto per riga, con le misure in millimetri."""
    righe = []
    for i in range(QUANTI):
        specie, classe, ordine, famiglia, taglia = TAXA[i]
        osso, porzione = OSSA[i]
        us = rif["us"][i % len(rif["us"])]
        lung = 48 + i * 11
        larg = 18 + i * 4
        spess = 9 + i * 2
        righe.append({
            "code": 1000 + i, "n_rilievo": "R-%03d" % (i + 1),
            "n_codice": "FAU-2026-%03d" % (i + 1), "anno": "2026",
            "sito": SITO,
            "quadrato": "%s%d" % ("ABCDE"[i % 5], 1 + i % 4),
            "us": int(us), "periodo": 2, "fase": 1 + i % 4,
            "specie": specie, "classe": classe, "ordine": ordine,
            "famiglia": famiglia,
            "elemnto_anat_generico": "Arto" if i % 2 else "Scheletro assiale",
            "elem_specifici": osso, "taglia": taglia,
            "eta": ("Adulto" if i % 3 else "Subadulto"),
            "lato": ("Destro" if i % 2 else "Sinistro"),
            "lunghezza": lung, "larghezza": larg, "spessore": spess,
            "porzione": porzione,
            # Il peso cresce col volume del frammento: non è un numero a caso.
            "peso": round(lung * larg * spess * 0.00085, 2),
            "coord_x": round(EST + 3.0 + i * 1.4, 3),
            "coord_y": round(NORD - 2.0 - i * 1.1, 3),
            "coord_z": round(12.60 + i * 0.16, 3),
            "azione": ("Macellazione" if i % 3 == 0 else
                       "Combustione" if i % 3 == 1 else "Nessuna traccia"),
            "modulo_osso": "Osso lungo" if i % 2 else "Osso piatto",
        })
    return righe


def fauna_scheda(rif) -> list:
    """La scheda `fauna_table`, quella di contesto: un record per US."""
    righe = []
    for i in range(QUANTI):
        specie, _c, _o, _f, _t = TAXA[i]
        us = rif["us"][i % len(rif["us"])]
        nmi = 1 + i % 4
        resti = str(12 + i * 7)
        righe.append({
            "id_us": None, "sito": SITO, "area": "1", "saggio": "Saggio I",
            "us": str(us),
            "datazione_us": "Periodo 2, fase %d" % (1 + i % 4),
            "responsabile_scheda": "%s %s" % (PERSONE[7][0], PERSONE[7][1]),
            "data_compilazione": _data(45 + i),
            "documentazione_fotografica": "FAU_%03d_01.jpg; FAU_%03d_02.jpg"
                                          % (i + 1, i + 1),
            "metodologia_recupero": ("Setacciatura a secco, maglia 2 mm"
                                     if i % 2 else "Raccolta manuale"),
            "contesto": ("Riempimento di fossa" if i % 3 == 0 else
                         "Strato di accumulo" if i % 3 == 1 else
                         "Butto di officina"),
            "descrizione_contesto":
                "Accumulo di resti faunistici nella US %s, con matrice "
                "sabbioso-limosa e inclusi carboniosi." % us,
            "resti_connessione_anatomica": "No" if i % 3 else "Sì, parziale",
            "tipologia_accumulo": "Secondario" if i % 2 else "Primario",
            "deposizione": "Sparsa" if i % 2 else "Concentrata",
            "numero_stimato_resti": resti,
            "numero_minimo_individui": nmi,
            "specie": specie,
            "parti_scheletriche": OSSA[i][0] + ", " + OSSA[(i + 3) % 10][0],
            "specie_psi": "%s (%d%%)" % (specie, 40 + i * 3),
            "misure_ossa": "Lunghezza max %d mm; larghezza max %d mm"
                           % (48 + i * 11, 18 + i * 4),
            "stato_frammentazione": ("Elevato" if i % 3 == 0 else
                                     "Medio" if i % 3 == 1 else "Basso"),
            "tracce_combustione": "Sì" if i % 3 == 1 else "No",
            "combustione_altri_materiali_us": 1 if i % 3 == 1 else 0,
            "tipo_combustione": ("Carbonizzazione parziale" if i % 3 == 1
                                 else "Nessuna"),
            "segni_tafonomici_evidenti": "Sì" if i % 2 else "No",
            "caratterizzazione_segni_tafonomici":
                ("Strie di macellazione sulla diafisi" if i % 2
                 else "Nessun segno riconoscibile"),
            "stato_conservazione": "Buono" if i % 4 else "Mediocre",
            "alterazioni_morfologiche": ("Esfoliazione corticale" if i % 4 == 0
                                         else "Assenti"),
            "note_terreno_giacitura":
                "Giacitura sub-orizzontale, terreno asciutto.",
            "campionature_effettuate": "Campione %d per analisi isotopica"
                                       % (i + 1),
            "affidabilita_stratigrafica": "Alta" if i % 3 else "Media",
            "classi_reperti_associazione":
                "Ceramica comune, frammenti di laterizio",
            "osservazioni": "Nessuna anomalia rilevata in fase di lavaggio.",
            "interpretazione":
                "Scarto di macellazione" if i % 3 == 0 else
                "Resti di pasto" if i % 3 == 1 else "Accumulo di butto",
            "entity_uuid": _uuid("fauna_table", i),
        })
    return righe


def tafonomia(rif) -> list:
    """Una scheda per tomba, agganciata alle dieci di `tomba_table` e ai
    dieci individui di `individui_table`."""
    righe = []
    for i in range(QUANTI):
        tomba = rif["tombe"][i % len(rif["tombe"])]
        individuo = rif["individui"][i % len(rif["individui"])]
        maschio = i % 2 == 0
        completo = "Sì" if i % 3 else "No"
        righe.append({
            "sito": SITO, "nr_scheda_taf": i + 1,
            "sigla_struttura": "T", "nr_struttura": int(tomba),
            "nr_individuo": int(individuo),
            "rito": "Inumazione",
            "descrizione_taf":
                "Inumato in fossa semplice, deposto in posizione supina con "
                "arti superiori lungo i fianchi.",
            "interpretazione_taf":
                "Deposizione primaria indisturbata" if i % 3 else
                "Deposizione primaria con disturbo post-depositionale",
            "segnacoli": "Assenti" if i % 4 else "Lastra litica in posto",
            "canale_libatorio_si_no": "No",
            "oggetti_rinvenuti_esterno":
                "Frammenti ceramici residuali" if i % 3 == 0 else "Nessuno",
            "stato_di_conservazione": ("Buono" if i % 3 else "Discreto"),
            "copertura_tipo": ("Lastre di calcare" if i % 2
                               else "Terra di riempimento"),
            "tipo_contenitore_resti": "Fossa terragna",
            "orientamento_asse": "E-W" if i % 2 else "NE-SW",
            "orientamento_azimut": 90.0 if i % 2 else 45.0,
            "riferimenti_stratigrafici": "Taglia la US %s, coperta dalla US %s"
                % (rif["us"][i % len(rif["us"])],
                   rif["us"][(i + 1) % len(rif["us"])]),
            "corredo_presenza": "Sì" if i % 2 else "No",
            "corredo_tipo": ("Personale" if i % 2 else "Assente"),
            "corredo_descrizione":
                ("Anello in bronzo alla falange della mano destra"
                 if i % 2 else "Nessun oggetto in connessione"),
            # Statura coerente col sesso dichiarato nelle schede
            # antropologiche: maschi più alti, e il cranio in asse.
            "lunghezza_scheletro": 168.0 + i * 1.5 if maschio else 157.0 + i,
            "posizione_scheletro": "Supino, arti distesi",
            "posizione_cranio": "In asse, ruotato a destra" if i % 2
                                else "In asse",
            "posizione_arti_superiori": "Distesi lungo i fianchi",
            "posizione_arti_inferiori": "Distesi e paralleli",
            "completo_si_no": completo,
            "disturbato_si_no": "No" if i % 3 else "Sì",
            "in_connessione_si_no": "Sì" if completo == "Sì" else "No",
            "caratteristiche":
                "Nessuna patologia macroscopica evidente sul post-craniale.",
            "periodo_iniziale": 2, "fase_iniziale": 1 + i % 4,
            "periodo_finale": 2, "fase_finale": 1 + i % 4,
            "datazione_estesa": "Periodo 2, fase %d" % (1 + i % 4),
            "misure_tafonomia":
                "Fossa: lunghezza 198 cm, larghezza %d cm, profondità %d cm"
                % (62 + i * 2, 38 + i),
            "version_number": 1, "editing_by": "pyarchinit_demo",
            "editing_since": _data(60 + i), "audit_trail": None,
        })
    return righe


def det_eta(rif) -> list:
    """La determinazione dell'età: indicatori osteologici e loro intervalli.

    I numeri si tengono fra loro: i gradi di obliterazione delle suture (0-4)
    crescono con l'età, e gli intervalli `min`/`max` degli indicatori si
    sovrappongono intorno all'età stimata — se no la scheda direbbe due cose
    diverse sullo stesso individuo.
    """
    righe = []
    for i in range(QUANTI):
        individuo = rif["individui"][i % len(rif["individui"])]
        eta = 22 + i * 6                      # da 22 a 76 anni
        grado = min(4, eta // 18)             # suture: più vecchio, più chiuso
        meta = max(0, min(4, grado))
        voce = {
            "sito": SITO, "nr_individuo": int(individuo),
            # sinfisi pubica (Suchey-Brooks): l'intervallo contiene l'età
            "sinf_min": max(15, eta - 6), "sinf_max": eta + 7,
            "sinf_min_2": max(15, eta - 4), "sinf_max_2": eta + 5,
            "SSPIA": meta, "SSPIB": meta, "SSPIC": max(0, meta - 1),
            "SSPID": max(0, meta - 1),
            # superficie auricolare (Lovejoy)
            "sup_aur_min": max(15, eta - 8), "sup_aur_max": eta + 9,
            "sup_aur_min_2": max(15, eta - 5), "sup_aur_max_2": eta + 6,
            # usura dentaria, mascellari superiore e inferiore
            "ms_sup_min": max(15, eta - 7), "ms_sup_max": eta + 8,
            "ms_inf_min": max(15, eta - 7), "ms_inf_max": eta + 8,
            "usura_min": max(1, min(8, eta // 9)),
            "usura_max": max(2, min(8, eta // 9 + 1)),
            # obliterazione endocranica: gli intervalli larghi di questo metodo
            "endo_min": max(18, eta - 12), "endo_max": eta + 14,
            "volta_min": max(18, eta - 10), "volta_max": eta + 12,
            "ant_lat_min": max(18, eta - 11), "ant_lat_max": eta + 13,
            "ecto_min": max(18, eta - 9), "ecto_max": eta + 11,
        }
        # I gradi di ogni sutura, endocranica e della volta: 0 = aperta,
        # 4 = obliterata. Tutte intorno al grado dell'età, con un po' di
        # variazione come in una scheda vera.
        suture = ["Id_endo", "Is_endo", "IId_endo", "IIs_endo", "IIId_endo",
                  "IIIs_endo", "IV_endo", "V_endo", "VI_endo", "VII_endo",
                  "VIIId_endo", "VIIIs_endo", "IXd_endo", "IXs_endo",
                  "Xd_endo", "Xs_endo",
                  "volta_1", "volta_2", "volta_3", "volta_4", "volta_5",
                  "volta_6", "volta_7",
                  "lat_6", "lat_7", "lat_8", "lat_9", "lat_10"]
        for k, nome in enumerate(suture):
            voce[nome] = max(0, min(4, meta - (k % 3 == 0) + (k % 5 == 0)))
        righe.append(voce)
    return righe


def det_sesso(rif) -> list:
    """La determinazione del sesso: gradi di espressione dei caratteri.

    Coerente per costruzione: i dieci individui si alternano maschio e
    femmina, e **tutti** gli indicatori di uno stesso individuo puntano
    nella stessa direzione — i gradi cranici alti e il punteggio positivo
    per i maschi, bassi e negativo per le femmine, con gli indicatori
    pelvici che dicono la stessa lettera. Una scheda in cui il cranio dice
    M e il bacino F non servirebbe a provare niente.
    """
    cranici = ["glab", "pmast", "pnuc", "pzig", "arcsop", "tub", "pocc",
               "inclfr", "zig", "msorb", "palato", "mfmand", "mento",
               "anmand", "minf", "brmont", "condm"]
    righe = []
    for i in range(QUANTI):
        individuo = rif["individui"][i % len(rif["individui"])]
        maschio = i % 2 == 0
        base = 4 if maschio else 2           # grado di espressione 1-5
        voce = {"sito": SITO, "num_individuo": int(individuo)}
        totale = 0.0
        for k, nome in enumerate(cranici):
            grado = max(1, min(5, base + (k % 3 == 0) - (k % 4 == 0)))
            valore = grado - 3               # da -2 a +2, positivo = maschile
            voce["%s_grado_imp" % nome] = grado
            voce["%s_valori" % nome] = valore
            totale += valore
        voce["sex_cr_tot"] = round(totale / len(cranici), 2)
        lettera = "M" if maschio else "F"
        voce["ind_cr_sex"] = ("Maschile" if maschio else "Femminile")
        for nome in ("sup_p_I", "sup_p_II", "sup_p_III", "sup_p_sex",
                     "in_isch_I", "in_isch_II", "in_isch_III", "in_isch_sex",
                     "arco_c_sex", "ramo_ip_I", "ramo_ip_II", "ramo_ip_III",
                     "ramo_ip_sex", "prop_ip_sex"):
            voce[nome] = lettera
        voce["ind_bac_sex"] = ("Maschile" if maschio else "Femminile")
        righe.append(voce)
    return righe


def ut(_rif) -> list:
    """Le Unità Topografiche: dieci ricognizioni intorno a Volterra."""
    luoghi = [
        ("Podere Le Balze", "Concentrazione di laterizi", 38.0, 4.5),
        ("Fonte di San Felice", "Struttura muraria affiorante", 12.0, 2.0),
        ("Campo del Pino", "Dispersione di ceramica comune", 55.0, 6.0),
        ("Poggio Caselli", "Traccia di strada glareata", 90.0, 3.0),
        ("Villa Montecchi", "Area di frammenti di dolio", 26.0, 3.5),
        ("Fosso dell'Era", "Scarico di fornace", 18.0, 2.5),
        ("Casale Sant'Ottaviano", "Basamento in opera incerta", 9.0, 1.5),
        ("Pian di Lago", "Concentrazione di tegole", 33.0, 4.0),
        ("Botro ai Marmi", "Affioramento di blocchi lavorati", 15.0, 2.0),
        ("Colle della Pieve", "Necropoli ipotizzata", 48.0, 5.5),
    ]
    righe = []
    for i, (localita, interpretazione, dim, prec) in enumerate(luoghi):
        est = EST + 120.0 + i * 65.0
        nord = NORD - 90.0 - i * 48.0
        righe.append({
            "progetto": SITO, "nr_ut": i + 1,
            "ut_letterale": "UT%02d" % (i + 1),
            "def_ut": interpretazione.split()[0],
            "descrizione_ut":
                "%s: %s su un'area di circa %d m², con visibilità "
                "parziale del suolo." % (localita, interpretazione.lower(), dim),
            "interpretazione_ut": interpretazione,
            "nazione": "Italia", "regione": "Toscana", "provincia": "Pisa",
            "comune": "Volterra", "frazione": "Capoluogo",
            "localita": localita,
            "indirizzo": "Strada vicinale %s" % localita.split()[-1],
            "nr_civico": "snc",
            "carta_topo_igm": "F. 111 III NE", "carta_ctr": "285140",
            "coord_geografiche": "43.40%02d N, 10.86%02d E" % (10 + i, 20 + i),
            "coord_piane": "E %.2f, N %.2f (EPSG:3004)" % (est, nord),
            "quota": round(305.0 + i * 7.5, 1),
            "andamento_terreno_pendenza": "Pendio %s, %d%%"
                % ("lieve" if i % 2 else "moderato", 4 + i),
            "utilizzo_suolo_vegetazione": ("Arativo" if i % 3 == 0 else
                                           "Oliveto" if i % 3 == 1 else
                                           "Incolto"),
            "descrizione_empirica_suolo":
                "Suolo argilloso bruno, scheletro minuto, umidità scarsa.",
            "descrizione_luogo":
                "Area a monte del fosso, delimitata a nord dalla strada "
                "vicinale e a sud dal filare di cipressi.",
            "metodo_rilievo_e_ricognizione":
                "Ricognizione sistematica per transetti paralleli a 5 m",
            "geometria": "Poligono", "bibliografia":
                "Benedetti M. 2026, «Carta archeologica», UT %d." % (i + 1),
            "data": _data(i * 2),
            "ora_meteo": "09:%02d, sereno" % (10 + i * 4),
            "responsabile": "%s %s" % (PERSONE[1][0], PERSONE[1][1]),
            "dimensioni_ut": "%d m²" % dim,
            "rep_per_mq": "%.1f" % (0.4 + i * 0.3),
            "rep_datanti": "Ceramica a vernice nera" if i % 2
                           else "Sigillata italica",
            "periodo_I": "Periodo 2", "datazione_I": "XV secolo",
            "interpretazione_I": "Frequentazione rurale",
            "periodo_II": "Periodo 4",
            "datazione_II": "Generico XIII secolo - Primi del XIV secolo",
            "interpretazione_II": "Insediamento sparso",
            "documentazione": "Foto UT%02d_01-04; schizzo di campagna"
                              % (i + 1),
            "enti_tutela_vincoli":
                "Soprintendenza ABAP Pisa e Livorno; nessun vincolo diretto",
            "indagini_preliminari": "Ricognizione di superficie 2026",
            "visibility_percent": 40 + i * 5,
            "vegetation_coverage": "%d%% di copertura erbacea" % (20 + i * 4),
            "gps_method": "RTK con base locale",
            "coordinate_precision": prec,
            "survey_type": "Sistematica per transetti",
            "surface_condition": ("Arato di fresco" if i % 2
                                  else "Stoppie non lavorate"),
            "accessibility": "Accessibile da strada vicinale",
            "photo_documentation": 4,
            "weather_conditions": "Sereno, vento assente, 18 °C",
            "team_members": ", ".join(
                "%s %s" % (p[0], p[1]) for p in PERSONE[1:4]),
            "foglio_catastale": "Foglio %d, particella %d" % (24 + i, 110 + i * 3),
            "entity_uuid": _uuid("ut_table", i),
        })
    return righe


# --- le geometrie delle schede che ne hanno una --------------------------
#: Dal numero di `geometry_columns.geometry_type` al nome WKT.
_TIPI = {1: "POINT", 2: "LINESTRING", 3: "POLYGON", 4: "MULTIPOINT",
         5: "MULTILINESTRING", 6: "MULTIPOLYGON"}


def _registrazione(conn, tabella: str):
    """Lo SRID e il tipo con cui quella tabella **è registrata**.

    Si leggono, non si decidono: nel database di esempio le UT stanno a
    `srid = -1` e come `POLYGON`, non `MULTIPOLYGON`, e scriverci dentro una
    geometria diversa fa `IntegrityError: geom-type or SRID not allowed`.
    """
    riga = conn.execute(
        "SELECT srid, geometry_type FROM geometry_columns"
        " WHERE f_table_name = ? AND f_geometry_column = 'the_geom'",
        (tabella,)).fetchone()
    if not riga:
        return None, None
    return int(riga[0]), _TIPI.get(int(riga[1]))


def _poligono(est: float, nord: float, lato: float, tipo: str) -> str:
    anello = ("%f %f, %f %f, %f %f, %f %f, %f %f"
              % (est, nord, est + lato, nord, est + lato, nord + lato,
                 est, nord + lato, est, nord))
    if tipo == "MULTIPOLYGON":
        return "MULTIPOLYGON(((%s)))" % anello
    return "POLYGON((%s))" % anello


def geometrie(conn, rif) -> list:
    """Un disegno per ogni scheda che ne usa uno, dove la tabella è vuota.

    Disegni inventati ma coerenti, e soprattutto **nel posto giusto**:
    quello che sta nello scavo cade dentro il saggio vero (5,4 x 6,4 m
    intorno a 2.324.920 / 4.881.955), quello che sta nel paesaggio — le
    Unità Topografiche, i sondaggi, le linee di riferimento — gli sta
    attorno a qualche decina di metri. Servono a far vedere i layer accesi
    sopra la pianta, non a somigliare a un rilievo.

    Lo SRID e il tipo di geometria si **leggono** da `geometry_columns`,
    non si decidono: scrivere un MULTIPOLYGON in una colonna registrata
    come POLYGON alza `IntegrityError: geom-type or SRID not allowed`.
    """
    fatto = []

    def vuota(tabella):
        try:
            return conn.execute(
                'SELECT count(*) FROM "%s"' % tabella).fetchone()[0] == 0
        except Exception:                           # noqa: BLE001
            return False

    def srid_di(tabella):
        riga = conn.execute(
            "SELECT srid FROM geometry_columns WHERE f_table_name = ?"
            "   AND f_geometry_column = 'the_geom'", (tabella,)).fetchone()
        return int(riga[0]) if riga else -1

    def tipo_di(tabella):
        riga = conn.execute(
            "SELECT geometry_type FROM geometry_columns"
            " WHERE f_table_name = ? AND f_geometry_column = 'the_geom'",
            (tabella,)).fetchone()
        return {1: "POINT", 2: "LINESTRING", 3: "POLYGON",
                6: "MULTIPOLYGON"}.get(int(riga[0])) if riga else None

    def punto(x, y):
        return "POINT(%f %f)" % (x, y)

    def linea(x1, y1, x2, y2):
        return "LINESTRING(%f %f, %f %f)" % (x1, y1, x2, y2)

    def area(x, y, lato, tipo):
        anello = ("%f %f, %f %f, %f %f, %f %f, %f %f"
                  % (x, y, x + lato, y, x + lato, y + lato,
                     x, y + lato, x, y))
        return ("MULTIPOLYGON(((%s)))" % anello if tipo == "MULTIPOLYGON"
                else "POLYGON((%s))" % anello)

    def scrivi(tabella, colonne, valori_per_riga, quante=QUANTI,
               descrizione=None):
        """Scrive le righe se la tabella è vuota, con lo SRID e il tipo suoi."""
        if not vuota(tabella):
            return
        tipo = tipo_di(tabella)
        if tipo is None:
            return
        srid = srid_di(tabella)
        scritte = 0
        for i in range(quante):
            valori, wkt = valori_per_riga(i, tipo)
            if wkt is None:
                continue
            conn.execute(
                'INSERT INTO "%s" (%s, the_geom) VALUES (%s,'
                ' GeomFromText(?, ?))'
                % (tabella, ", ".join(colonne),
                   ", ".join("?" for _ in colonne)),
                list(valori) + [wkt, srid])
            scritte += 1
        if scritte:
            fatto.append("%d %s" % (scritte, descrizione or tabella))

    # --- quello che sta DENTRO lo scavo ---------------------------------
    scrivi("pyarchinit_reperti", ("siti", "id_rep", "quota", "link"),
           lambda i, t: ((SITO,
                          int(rif["inventario"][i % len(rif["inventario"])])
                          if rif["inventario"] else i + 1,
                          round(488.20 + i * 0.04, 2),
                          "DosCo/reperti/INV_%03d.jpg" % (i + 1)),
                         punto(*_dentro(i))),
           descrizione="punti di reperti")

    scrivi("pyarchinit_individui",
           ("sito", "sigla_struttura", "id_individuo", "note"),
           lambda i, t: ((SITO, "T",
                          int(rif["individui"][i % len(rif["individui"])])
                          if rif["individui"] else i + 1,
                          "Inumato della tomba %d" % (i + 1)),
                         punto(*_dentro(i))),
           descrizione="punti di individui")

    _CAMPIONI = ("Carbone", "Terreno", "Malta", "Osso animale", "Osso umano",
                 "Intonaco", "Semi carbonizzati", "Ceramica", "Metallo",
                 "Sedimento")
    scrivi("pyarchinit_campionature",
           ("sito", "id_campion", "tipo_camp", "dataz", "cronologia",
            "link_immag", "sigla_camp"),
           lambda i, t: ((SITO, i + 1, _CAMPIONI[i], _data(i * 3),
                          "Periodo 2, fase %d" % (1 + i % 4),
                          "DosCo/campioni/CS_%03d.jpg" % (i + 1),
                          "CS-%02d" % (1 + i // 3)),
                         punto(*_dentro(i))),
           descrizione="punti di campionature")

    scrivi("pyarchinit_tafonomia", ("sito", "nr_scheda"),
           lambda i, t: ((SITO, i + 1), punto(*_dentro(i))),
           descrizione="punti di tafonomia (le tombe)")

    scrivi("pyarchinit_quote_usm",
           ("sito_q", "area_q", "us_q", "unita_misu_q", "quota_q",
            "unita_tipo_q", "data", "disegnatore", "rilievo_originale"),
           lambda i, t: ((SITO, "1", str(14 + i), "m",
                          round(488.60 + i * 0.07, 2), "USM", _data(10 + i),
                          "%s %s" % (PERSONE[5][0], PERSONE[5][1]),
                          "Rilievo diretto"),
                         punto(*_dentro(i))),
           descrizione="quote delle murature")

    scrivi("pyarchinit_us_negative_doc",
           ("sito_n", "area_n", "us_n", "tipo_doc_n", "nome_doc_n"),
           lambda i, t: ((SITO, "1", str(rif["us"][i % len(rif["us"])]),
                          "Planimetria", "Sezione della fossa %d" % (i + 1)),
                         linea(*(_dentro(i) + (_dentro(i)[0] + 0.8,
                                               _dentro(i)[1] + 0.5)))),
           descrizione="tracce di US negative")

    scrivi("pyarchinit_ripartizioni_spaziali",
           ("id_rs", "sito_rs", "tip_rip", "descr_rs"),
           lambda i, t: ((i + 1, SITO, "Quadrato",
                          "Quadrato %s%d della griglia di scavo"
                          % ("ABCDE"[i % 5], 1 + i // 5)),
                         area(EST + (i % 5) * (LARG / 5.0),
                              NORD + (i // 5) * (ALT / 2.0),
                              min(LARG / 5.0, ALT / 2.0) * 0.9, t)),
           descrizione="quadrati della griglia")

    scrivi("pyarchinit_strutture_ipotesi",
           ("sito", "id_strutt", "per_iniz", "per_fin", "dataz_ext",
            "fase_iniz", "fase_fin", "descrizione", "sigla_strut",
            "nr_strut"),
           lambda i, t: ((SITO, i + 1, 2, 2, "Periodo 2, fase %d" % (1 + i % 4),
                          1 + i % 4, 1 + i % 4,
                          "Ipotesi ricostruttiva della struttura %d" % (1 + i % 2),
                          "STR", 1 + i % 2),
                         area(EST + (i % 5) * (LARG / 5.5),
                              NORD + (i // 5) * (ALT / 2.5),
                              min(LARG / 6.0, ALT / 3.0), t)),
           descrizione="ipotesi di strutture")

    # --- quello che sta ATTORNO allo scavo -------------------------------
    # Uno solo, e non dieci: è il perimetro del sito, non una scheda.
    scrivi("pyarchinit_siti_polygonal", ("sito_id",),
           lambda i, t: ((SITO,),
                         area(EST - 4.0, NORD - 4.0, max(LARG, ALT) + 8.0, t)),
           quante=1, descrizione="il poligono del sito")

    scrivi("pyarchinit_documentazione",
           ("sito", "nome_doc", "tipo_doc", "path_qgis_pj"),
           lambda i, t: ((SITO,
                          ("Sezione %s-%s'" % ("ABCDEFGHIJ"[i],
                                               "ABCDEFGHIJ"[i])),
                          "Sezione", "DosCo/sezioni/sez_%s.qgs"
                          % "ABCDEFGHIJ"[i]),
                         linea(*(_attorno(i, 8.0) + _attorno(i + 5, 8.0)))),
           descrizione="linee di sezione")

    scrivi("pyarchinit_linee_rif", ("sito", "definizion", "descrizion"),
           lambda i, t: ((SITO, "Base %d" % (i + 1),
                          "Linea di riferimento del rilievo, base %d"
                          % (i + 1)),
                         linea(*(_attorno(i, 12.0) + _attorno(i + 3, 12.0)))),
           descrizione="linee di riferimento")

    scrivi("pyarchinit_sondaggi", ("sito_sond", "id_sondaggio"),
           lambda i, t: ((SITO, i + 1),
                         area(*(_attorno(i, 35.0) + (3.0, t)))),
           descrizione="sondaggi")

    scrivi("pyarchinit_ut_polygon",
           ("sito", "nr_ut", "def_ut", "area_mq", "perimetro",
            "data_rilevamento", "responsabile", "note"),
           lambda i, t: ((SITO, i + 1, "UT%02d" % (i + 1),
                          round(12.0 ** 2, 2), round(12.0 * 4, 2),
                          _data(i * 2),
                          "%s %s" % (PERSONE[1][0], PERSONE[1][1]),
                          "Ricognizione sistematica per transetti."),
                         area(*(_attorno(i, 120.0) + (12.0, t)))),
           descrizione="poligoni di UT")

    scrivi("pyarchinit_ut_point",
           ("sito", "nr_ut", "def_ut", "quota", "data_rilevamento",
            "responsabile", "note"),
           lambda i, t: ((SITO, i + 1, "UT%02d" % (i + 1),
                          round(305.0 + i * 7.5, 1), _data(i * 2),
                          "%s %s" % (PERSONE[1][0], PERSONE[1][1]),
                          "Punto di riferimento della UT."),
                         punto(*_attorno(i, 120.0))),
           descrizione="punti di UT")

    scrivi("pyarchinit_ut_line",
           ("sito", "nr_ut", "def_ut", "tipo_linea", "lunghezza",
            "data_rilevamento", "responsabile", "note"),
           lambda i, t: ((SITO, i + 1, "UT%02d" % (i + 1), "Transetto",
                          round(40.0 + i * 5, 1), _data(i * 2),
                          "%s %s" % (PERSONE[1][0], PERSONE[1][1]),
                          "Transetto di ricognizione."),
                         linea(*(_attorno(i, 100.0) + _attorno(i, 150.0)))),
           descrizione="transetti di UT")

    return fatto


# --- la meccanica -------------------------------------------------------
#: Scheda → funzione che ne produce i dieci record. L'ordine conta: le
#: presenze e le attrezzature citano le persone, quindi il personale va
#: inserito prima.
SCHEDE = (
    ("personale_table", personale),
    ("presenze_table", presenze),
    ("attrezzature_table", attrezzature),
    ("budget_table", budget),
    ("campioni_table", campioni),
    ("documentazione_table", documentazione),
    ("computo_metrico_table", computo_metrico),
    ("inventario_lapidei_table", inventario_lapidei),
    ("archeozoology_table", archeozoology),
    ("fauna", fauna_lista),
    ("fauna_table", fauna_scheda),
    ("tafonomia_table", tafonomia),
    ("deteta_table", det_eta),
    ("detsesso_table", det_sesso),
    ("ut_table", ut),
)


def _apri(percorso: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(percorso)
    conn.enable_load_extension(True)
    for nome in SPATIALITE:
        if not nome:
            continue
        try:
            conn.load_extension(nome)
            return conn
        except sqlite3.OperationalError:
            continue
    conn.close()
    raise SystemExit(
        "spatialite non si carica: le geometrie non si possono scrivere.\\n"
        "Lancia questo script con il Python di QGIS, o di' dov'è con "
        "MOD_SPATIALITE=/percorso/mod_spatialite.so")


def _colonne(conn, tabella: str) -> set:
    return {r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)}


def _inserisci(conn, tabella: str, righe: list) -> int:
    """Scrive le righe tenendo **solo** le colonne che la tabella ha.

    Difensivo di proposito: se domani una colonna cambia nome, questo script
    scrive quello che può invece di morire, e il test dice che la scheda è
    rimasta sotto i dieci record.
    """
    presenti = _colonne(conn, tabella)
    scritte = 0
    for riga in righe:
        campi = {k: v for k, v in riga.items() if k in presenti}
        if not campi:
            continue
        conn.execute(
            'INSERT INTO "%s" (%s) VALUES (%s)'
            % (tabella, ", ".join('"%s"' % c for c in campi),
               ", ".join("?" for _ in campi)),
            list(campi.values()))
        scritte += 1
    return scritte


def _riferimenti(conn) -> dict:
    """I numeri veri a cui agganciare i dati: US, individui, tombe, inventario.

    Si leggono dal database invece di scriverli nello script: un riferimento
    che non punta a niente non serve a fare prove, e i numeri del sito
    possono cambiare.
    """
    def elenco(sql, *params):
        return [r[0] for r in conn.execute(sql, params)]

    return {
        "us": elenco("SELECT DISTINCT us FROM us_table WHERE sito = ?"
                     " ORDER BY CAST(us AS INTEGER) LIMIT 12", SITO),
        "individui": elenco("SELECT nr_individuo FROM individui_table"
                            " WHERE sito = ? ORDER BY nr_individuo LIMIT 10",
                            SITO),
        "tombe": elenco("SELECT nr_scheda_taf FROM tomba_table WHERE sito = ?"
                        " ORDER BY nr_scheda_taf LIMIT 10", SITO),
        "inventario": elenco("SELECT numero_inventario"
                             " FROM inventario_materiali_table"
                             " WHERE sito = ? ORDER BY numero_inventario"
                             " LIMIT 10", SITO),
        "personale": [],
    }


def main(argv=None) -> int:
    global SITO
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sito", default=SITO,
                    help="il sito da riempire (default: %s)" % SITO)
    ap.add_argument("--db", default=str(DB), help="il database da riempire")
    args = ap.parse_args(argv)
    SITO = args.sito
    percorso = Path(args.db)
    if not percorso.is_file():
        raise SystemExit("manca %s" % percorso)

    conn = _apri(percorso)
    try:
        esiste = conn.execute(
            "SELECT count(*) FROM site_table WHERE sito = ?", (SITO,)
        ).fetchone()[0]
        if not esiste:
            raise SystemExit("il sito %r non è in site_table" % SITO)

        rif = _riferimenti(conn)
        print("=== %s ===" % SITO)
        print("  riferimenti: %d US, %d individui, %d tombe, %d inventario"
              % (len(rif["us"]), len(rif["individui"]), len(rif["tombe"]),
                 len(rif["inventario"])))

        for tabella, genera in SCHEDE:
            colonna_sito = "sito" if "sito" in _colonne(conn, tabella) \
                else ("progetto" if "progetto" in _colonne(conn, tabella)
                      else None)
            if colonna_sito:
                quante = conn.execute(
                    'SELECT count(*) FROM "%s" WHERE "%s" = ?'
                    % (tabella, colonna_sito), (SITO,)).fetchone()[0]
            else:
                quante = conn.execute(
                    'SELECT count(*) FROM "%s"' % tabella).fetchone()[0]
            if quante >= QUANTI:
                print("  %-28s già %d record, non si tocca"
                      % (tabella, quante))
                continue
            scritte = _inserisci(conn, tabella, genera(rif))
            print("  %-28s +%d record (ne aveva %d)"
                  % (tabella, scritte, quante))
            # Le persone appena scritte servono a chi le cita.
            if tabella == "personale_table":
                rif["personale"] = [
                    r[0] for r in conn.execute(
                        "SELECT id_personale FROM personale_table"
                        " WHERE sito = ? ORDER BY id_personale", (SITO,))]

        fatto = geometrie(conn, rif)
        for riga in fatto:
            print("  geometrie: %s" % riga)
        if not fatto:
            print("  geometrie: già presenti")

        # Le statistiche dei layer toccati, se no QGIS conta sbagliato.
        for tabella, _c in conn.execute(
                "SELECT f_table_name, f_geometry_column"
                " FROM geometry_columns").fetchall():
            conn.execute("SELECT InvalidateLayerStatistics(?, 'the_geom')",
                         (tabella,))
            conn.execute("SELECT UpdateLayerStatistics(?, 'the_geom')",
                         (tabella,))
        conn.commit()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
