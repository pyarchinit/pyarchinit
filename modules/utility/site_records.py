"""I record di una scheda, per il sito su cui il plugin è settato.

Perché esiste: il bottone «view all» delle schede caricava la tabella
intera, con i record di tutti i siti, invece di quelli del sito impostato
in `config.cfg`. Il filtro esisteva solo dentro la scheda US; qui vive in
un posto solo, così le altre schede possono chiamarlo senza copiarlo.

Il modulo non importa QGIS: `Connection` si importa dentro `current_site`,
e il resto lavora su qualunque oggetto con `DB_MANAGER` e
`MAPPER_TABLE_CLASS`, quindi si prova con dei finti.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def current_site():
    """Il sito su cui il plugin è settato, da `config.cfg`, o '' se non c'è.

    Non solleva: una configurazione illeggibile vale «nessun sito», e chi
    chiama ricade sul comportamento di prima.
    """
    try:
        from ..db.pyarchinit_conn_strings import Connection
        sito = Connection().sito_set()['sito_set']
    except Exception as e:
        # Tornare '' riporta «view all» a mostrare tutti i siti: non
        # succeda in silenzio.
        logger.warning(
            "Sito corrente illeggibile (config.cfg): 'view all' carica "
            "i record di tutti i siti. Causa: %s", e)
        return ''
    return str(sito).strip() if sito else ''


def records_for_site(db_manager, mapper_name, sito):
    """I record di una tabella per un sito solo.

    `mapper_name` è il nome della classe come lo portano le schede
    (`MAPPER_TABLE_CLASS`, per esempio "US"), non la classe.
    """
    # Gli apici attorno al valore sono la convenzione storica delle schede;
    # `query_bool` li normalizza, con o senza.
    return db_manager.query_bool({'sito': f"'{sito}'"}, mapper_name)


def _sorted_by_id(rows, id_attr):
    """Ordina per id crescente, senza mai sollevare.

    `query_bool` non ordina, mentre `charge_records()` sì (`query_ordered`,
    'asc'): senza questo «view all» cambierebbe il primo record mostrato.
    Le righe senza l'attributo o con id `None` vanno in fondo, nell'ordine
    in cui sono arrivate (l'ordinamento è stabile).
    """
    def chiave(r):
        v = getattr(r, id_attr, None) if id_attr else None
        if v is None:
            return (1, 0)
        try:
            return (0, float(v))
        except (TypeError, ValueError):
            return (1, 0)
    try:
        return sorted(rows, key=chiave)
    except Exception:
        return list(rows)


def charge_records_for_site(tab):
    """Riempie `tab.DATA_LIST` con i record del sito configurato.

    Vero quando c'è almeno un record da mostrare. Senza un sito impostato
    carica tutto, com'è sempre stato: meglio il comportamento di prima che
    una lista vuota.

    Attenzione per chi chiama: se il sito non ha record di quella tabella
    torna False e `tab.DATA_LIST` resta vuota. Le schede che dopo il
    caricamento fanno `self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR =
    self.DATA_LIST[0]` andrebbero in `IndexError`: devono guardare il
    ritorno e, come fa la scheda US, aprire un record nuovo.
    """
    # «View all» è il modo in cui si ricarica la scheda: `query_bool` tiene
    # una cache di cinque minuti, e senza questo i record appena importati
    # non si vedrebbero. Il percorso senza sito passa da `query_ordered`,
    # che non è cachato, ma azzerare qui vale per tutti e due.
    svuota = getattr(tab.DB_MANAGER, "clear_cache", None)
    if callable(svuota):
        try:
            svuota()
        except Exception:
            pass

    sito = current_site()
    if not sito:
        tab.charge_records()
        tab.REC_TOT, tab.REC_CORR = len(tab.DATA_LIST), 0
        return bool(tab.DATA_LIST)

    res = records_for_site(tab.DB_MANAGER, tab.MAPPER_TABLE_CLASS, sito)
    tab.DATA_LIST = _sorted_by_id(res, getattr(tab, 'ID_TABLE', None)) if res else []
    if not tab.DATA_LIST:
        return False
    tab.REC_TOT, tab.REC_CORR = len(tab.DATA_LIST), 0
    return True


def clear_form_state(tab):
    """Rimette la scheda in uno stato usabile quando il sito non ha record.

    Svuotare `DATA_LIST` senza azzerare i contatori non toglie l'IndexError:
    lo sposta al clic successivo, dentro uno slot Qt, dove diventa una
    finestra di errore che non dice niente. Qui si azzera tutto quello che i
    bottoni di navigazione leggono.
    """
    tab.DATA_LIST = []
    tab.REC_TOT = 0
    tab.REC_CORR = 0
    tab.DATA_LIST_REC_TEMP = tab.DATA_LIST_REC_CORR = None
    tab.BROWSE_STATUS = "x"
    for metodo, argomenti in (("set_rec_counter", (0, 0)),):
        f = getattr(tab, metodo, None)
        if callable(f):
            try:
                f(*argomenti)
            except Exception:
                pass
    voci = getattr(tab, "STATUS_ITEMS", None)
    # Quasi tutte le schede non hanno la voce «x» (solo US e Fauna): con
    # BROWSE_STATUS = "x" un `STATUS_ITEMS[self.BROWSE_STATUS]` qualunque,
    # altrove nella scheda, solleverebbe KeyError.
    if isinstance(voci, dict) and "x" not in voci:
        voci["x"] = "Nessun record"
    etichetta = getattr(tab, "label_status", None)
    if etichetta is not None and isinstance(voci, dict) and "x" in voci:
        try:
            etichetta.setText(voci["x"])
        except Exception:
            pass
