"""I toponimi della scheda sito e il loro posto nel thesaurus.

La scheda sito legge la definizione del sito dal thesaurus (``site_table``,
codice 1.1) e, dal 17 ottobre 2026, anche nazione, regione, provincia e
comune (codici 1.2–1.5): «andrebbero aggiornati anche nella scheda
thesaurus perché li dovrebbe leggere da lì» (Enzo). Prima regione e
provincia erano elenchi scritti nel codice della scheda, solo in italiano;
restano qui come ripiego per un database che nel thesaurus non li ha, e
come voci con cui riempirlo (``scripts/fill_thesaurus.py``).

Le sigle sono uniche per codice: su PostgreSQL il thesaurus può avere
``UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla)``. Per le province
sono quelle delle targhe, per le regioni tre lettere.

Puro: niente Qt, niente database.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

#: la definizione del sito
SITE_DEFINITION_CODE = "1.1"

#: (campo di site_table, codice del thesaurus)
TOPONYM_CODES: Tuple[Tuple[str, str], ...] = (
    ("nazione", "1.2"), ("regione", "1.3"), ("provincia", "1.4"), ("comune", "1.5"))

NAZIONI_IT: List[Tuple[str, str]] = [("ITA", "Italia")]

REGIONI_IT: List[Tuple[str, str]] = [
    ("ABR", "Abruzzo"), ("BAS", "Basilicata"), ("CAL", "Calabria"),
    ("CAM", "Campania"), ("EMR", "Emilia-Romagna"),
    ("FVG", "Friuli Venezia Giulia"), ("LAZ", "Lazio"), ("LIG", "Liguria"),
    ("LOM", "Lombardia"), ("MAR", "Marche"), ("MOL", "Molise"),
    ("PIE", "Piemonte"), ("PUG", "Puglia"), ("SAR", "Sardegna"),
    ("SIC", "Sicilia"), ("TOS", "Toscana"), ("TAA", "Trentino Alto Adige"),
    ("UMB", "Umbria"), ("VDA", "Valle d'Aosta"), ("VEN", "Veneto"),
]

#: le province dell'elenco che la scheda sito aveva (anche le quattro sarde
#: soppresse nel 2016, per le schede di allora) e la Sud Sardegna
PROVINCE_IT: List[Tuple[str, str]] = [
    ("AG", "Agrigento"), ("AL", "Alessandria"), ("AN", "Ancona"), ("AO", "Aosta"),
    ("AR", "Arezzo"), ("AP", "Ascoli Piceno"), ("AT", "Asti"), ("AV", "Avellino"),
    ("BA", "Bari"), ("BT", "Barletta-Andria-Trani"), ("BL", "Belluno"),
    ("BN", "Benevento"), ("BG", "Bergamo"), ("BI", "Biella"), ("BO", "Bologna"),
    ("BZ", "Bolzano"), ("BS", "Brescia"), ("BR", "Brindisi"), ("CA", "Cagliari"),
    ("CL", "Caltanissetta"), ("CB", "Campobasso"), ("CI", "Carbonia-Iglesias"),
    ("CE", "Caserta"), ("CT", "Catania"), ("CZ", "Catanzaro"), ("CH", "Chieti"),
    ("CO", "Como"), ("CS", "Cosenza"), ("CR", "Cremona"), ("KR", "Crotone"),
    ("CN", "Cuneo"), ("EN", "Enna"), ("FM", "Fermo"), ("FE", "Ferrara"),
    ("FI", "Firenze"), ("FG", "Foggia"), ("FC", "Forlì-Cesena"), ("FR", "Frosinone"),
    ("GE", "Genova"), ("GO", "Gorizia"), ("GR", "Grosseto"), ("IM", "Imperia"),
    ("IS", "Isernia"), ("AQ", "L'Aquila"), ("SP", "La Spezia"), ("LT", "Latina"),
    ("LE", "Lecce"), ("LC", "Lecco"), ("LI", "Livorno"), ("LO", "Lodi"),
    ("LU", "Lucca"), ("MC", "Macerata"), ("MN", "Mantova"), ("MS", "Massa e Carrara"),
    ("MT", "Matera"), ("VS", "Medio Campidano"), ("ME", "Messina"), ("MI", "Milano"),
    ("MO", "Modena"), ("MB", "Monza e Brianza"), ("NA", "Napoli"), ("NO", "Novara"),
    ("NU", "Nuoro"), ("OG", "Ogliastra"), ("OT", "Olbia-Tempio"), ("OR", "Oristano"),
    ("PD", "Padova"), ("PA", "Palermo"), ("PR", "Parma"), ("PV", "Pavia"),
    ("PG", "Perugia"), ("PU", "Pesaro e Urbino"), ("PE", "Pescara"), ("PC", "Piacenza"),
    ("PI", "Pisa"), ("PT", "Pistoia"), ("PN", "Pordenone"), ("PZ", "Potenza"),
    ("PO", "Prato"), ("RG", "Ragusa"), ("RA", "Ravenna"), ("RC", "Reggio Calabria"),
    ("RE", "Reggio Emilia"), ("RI", "Rieti"), ("RN", "Rimini"), ("RM", "Roma"),
    ("RO", "Rovigo"), ("SA", "Salerno"), ("SS", "Sassari"), ("SV", "Savona"),
    ("SI", "Siena"), ("SR", "Siracusa"), ("SO", "Sondrio"), ("SU", "Sud Sardegna"),
    ("TA", "Taranto"), ("TE", "Teramo"), ("TR", "Terni"), ("TO", "Torino"),
    ("TP", "Trapani"), ("TN", "Trento"), ("TV", "Treviso"), ("TS", "Trieste"),
    ("UD", "Udine"), ("VA", "Varese"), ("VE", "Venezia"),
    ("VB", "Verbano-Cusio-Ossola"), ("VC", "Vercelli"), ("VR", "Verona"),
    ("VV", "Vibo Valentia"), ("VI", "Vicenza"), ("VT", "Viterbo"),
]


def toponym_choices(dal_thesaurus: Dict[str, Iterable[str]], lingua: str) -> Dict[str, List[str]]:
    """Le voci delle quattro tendine: quelle del thesaurus quando ci sono;
    altrimenti, per l'italiano, le regioni e le province di sempre."""
    ripiego = {"regione": [r for _s, r in REGIONI_IT],
               "provincia": [p for _s, p in PROVINCE_IT]}
    out: Dict[str, List[str]] = {}
    for campo, _codice in TOPONYM_CODES:
        voci = sorted({str(v).strip() for v in (dal_thesaurus.get(campo) or ()) if str(v or "").strip()})
        if not voci and str(lingua or "").lower().startswith("it"):
            voci = list(ripiego.get(campo, []))
        out[campo] = voci
    return out
