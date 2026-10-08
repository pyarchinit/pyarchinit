"""Quello che un'unità della matrice tocca fuori dalla matrice.

Il pannello disegna l'em.json e basta. Ma l'archeologo che clicca una US
vuole anche le sue foto e, se la pianta è disegnata, il posto dove sta
sulla mappa — richiesta di Enzo del 2026-10-08. Quei due legami non
appartengono al file: stanno nel database del progetto e nei layer di
QGIS, cioè da questo lato del ponte.

Perciò qui non si importa niente dell'esportazione: l'em.json porta già
``sito``, ``area``, ``us`` e ``node_uuid`` dentro ``data``, e sono le
quattro chiavi che ritrovano la riga. Nessun campo nuovo entra nel file e
il projector non sa che questo modulo esiste.

Niente Qt e niente QGIS: la parte che decide si prova headless.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

#: Quante anteprime si mostrano al più nella scheda. Una US con duecento
#: foto non deve far aspettare chi voleva solo guardare la matrice.
MAX_MEDIA = 24

#: Come i layer di pyArchInit chiamano sito, area e us: la vista
#: ``pyarchinit_us_view`` usa i nomi della scheda, la tabella dei disegni
#: ``pyunitastratigrafiche`` i propri. Si cerca nell'ordine.
FIELD_SETS = (
    ("sito", "area", "us", "unita_tipo"),
    ("scavo_s", "area_s", "us_s", "unita_tipo_s"),
)


@dataclass(frozen=True)
class MediaRef:
    """Un media attaccato all'unità: il nome, l'anteprima, l'originale."""
    id_media: int
    name: str
    thumb_file: str = ""
    original_file: str = ""


def unit_identity(unit) -> Dict[str, str]:
    """Le chiavi con cui si ritrova la riga di ``us_table``, o ``{}``.

    Vuoto per tutto ciò che non è una riga della scheda — un nodo di
    continuità, un documento, una proprietà: cercarli nel database
    significherebbe cercare una US che non c'è.
    """
    dati = getattr(unit, "data", None) or {}
    if not isinstance(dati, dict):
        return {}
    us = str(dati.get("us") or "").strip()
    sito = str(dati.get("sito") or "").strip()
    if not us or not sito:
        return {}
    identita = {
        "sito": sito,
        "us": us,
        "area": str(dati.get("area") or "").strip(),
        "unita_tipo": str(dati.get("unita_tipo") or "").strip(),
    }
    node_uuid = str(dati.get("node_uuid") or "").strip()
    if node_uuid:
        identita["node_uuid"] = node_uuid
    return identita


# --------------------------------------------------------------- database

def _sqlite_file_missing(connection) -> bool:
    """Vero se è un SQLite che non esiste.

    SQLAlchemy lo creerebbe vuoto: un file nuovo dove dovrebbe stare il
    database del progetto è peggio di una risposta vuota.
    """
    from pathlib import Path

    if isinstance(connection, Path):
        return not connection.exists()
    if not isinstance(connection, str) or not connection.startswith("sqlite"):
        return False
    percorso = connection.split("///", 1)[-1].split("?", 1)[0]
    return bool(percorso) and percorso != ":memory:" \
        and not Path(percorso).exists()


def _engine_for(connection):
    """L'engine con cui si legge il database del progetto, e se è nostro.

    Il secondo valore dice se l'engine l'abbiamo aperto noi: in quel caso
    lo si chiude subito dopo. Il database di chi usa il plugin lo tiene
    aperto il suo QGIS, e un pannello che lascia dietro di sé una
    connessione agganciata al file è il modo in cui si arriva a un «disk
    I/O error» (2026-10-08).

    Non si passa dalla libreria: leggere il PROPRIO database è roba del
    plugin, e appoggiarsi a un nome privato di s3dgraphy faceva tacere
    media e zoom dove la libreria non è importabile — visto provando con
    QGIS vero.
    """
    from pathlib import Path

    if connection is None:
        return None, False
    if isinstance(connection, Path):
        connection = "sqlite:///%s" % connection
    if isinstance(connection, str):
        from sqlalchemy import create_engine
        try:
            return create_engine(connection), True
        except Exception:                           # noqa: BLE001
            return None, False
    engine = getattr(connection, "engine", None)   # il gestore del plugin
    if engine is not None and hasattr(engine, "connect"):
        return engine, False
    if hasattr(connection, "connect"):             # è già un engine
        return connection, False
    return None, False


@contextmanager
def _connected(connection):
    """Una connessione al database del progetto, o niente.

    Si accetta una stringa, un percorso SQLite, l'engine o il gestore del
    database del plugin: chi chiama usa quello che ha già in mano.
    """
    if _sqlite_file_missing(connection):
        yield None
        return
    engine, nostro = _engine_for(connection)
    if engine is None:
        yield None
        return
    try:
        with engine.connect() as conn:
            yield conn
    except Exception:                               # noqa: BLE001
        yield None
    finally:
        if nostro:
            try:
                engine.dispose()
            except Exception:                       # noqa: BLE001
                pass


def _rows(conn, sql: str, params: Dict[str, Any]) -> List[tuple]:
    """Le righe della query, o nessuna se la tabella non c'è.

    Le tabelle media le crea l'aggiornamento del database e ``node_uuid``
    una migrazione: su un database che non le ha ancora il pannello
    mostra meno, non un errore.
    """
    from sqlalchemy import text
    try:
        return list(conn.execute(text(sql), params).fetchall())
    except Exception:                               # noqa: BLE001
        return []


def resolve_id_us(connection, unit) -> Optional[int]:
    """L'``id_us`` della riga che sta sotto questa unità, o ``None``.

    Prima per ``node_uuid``, che è l'identità vera e non cambia se si
    rinumera; poi per (sito, area, us, unita_tipo), il vincolo unico di
    ``us_table``; infine senza il tipo, per i database in cui la colonna
    è ancora vuota.
    """
    identita = unit_identity(unit)
    if not identita:
        return None
    with _connected(connection) as conn:
        if conn is None:
            return None
        return _id_us(conn, identita)


def _id_us(conn, identita: Dict[str, str]) -> Optional[int]:
    tentativi: List[tuple] = []
    if identita.get("node_uuid"):
        tentativi.append((
            "SELECT id_us FROM us_table WHERE node_uuid = :node_uuid",
            {"node_uuid": identita["node_uuid"]}))
    base = ("SELECT id_us FROM us_table WHERE sito = :sito "
            "AND TRIM(CAST(us AS CHAR(50))) = :us")
    params = {"sito": identita["sito"], "us": identita["us"]}
    if identita.get("area"):
        base += " AND TRIM(CAST(area AS CHAR(50))) = :area"
        params["area"] = identita["area"]
    if identita.get("unita_tipo"):
        tentativi.append((base + " AND unita_tipo = :unita_tipo",
                          dict(params, unita_tipo=identita["unita_tipo"])))
    tentativi.append((base, params))
    for sql, p in tentativi:
        righe = _rows(conn, sql, p)
        if righe and righe[0][0] is not None:
            try:
                return int(righe[0][0])
            except (TypeError, ValueError):
                return None
    return None


def media_for_unit(connection, unit, limit: int = MAX_MEDIA) -> List[MediaRef]:
    """I media attaccati a questa unità, con l'anteprima quando c'è.

    Si filtra anche su ``entity_type``/``table_name``: lo stesso
    ``id_entity`` appartiene a un reperto o a una tomba in altre schede, e
    senza il filtro le foto di un reperto finirebbero su una US.
    """
    try:
        massimo = max(int(limit), 0)
    except (TypeError, ValueError):
        massimo = MAX_MEDIA
    if not massimo:
        return []
    identita = unit_identity(unit)
    if not identita:
        return []
    with _connected(connection) as conn:
        if conn is None:
            return []
        id_us = _id_us(conn, identita)
        if id_us is None:
            return []
        righe = _rows(conn,
                      "SELECT m.id_media, m.media_name, m.filepath, "
                      "t.filepath FROM media_to_entity_table m "
                      "LEFT JOIN media_thumb_table t "
                      "ON t.id_media = m.id_media "
                      "WHERE m.id_entity = :id_us "
                      "AND (m.entity_type = 'US' "
                      "OR m.table_name = 'us_table') "
                      "ORDER BY m.media_name LIMIT %d" % (massimo * 4),
                      {"id_us": id_us})
    return _media_refs(righe, massimo)


def _media_refs(righe: Iterable[tuple], massimo: int) -> List[MediaRef]:
    """Le voci da mostrare: una per media, anche senza anteprima.

    Un media che c'è e non si vede è peggio di un media senza miniatura,
    e ``media_thumb_table`` non ha un vincolo unico su ``id_media``.
    """
    visti = set()
    media: List[MediaRef] = []
    for id_media, nome, originale, anteprima in righe:
        try:
            chiave = int(id_media)
        except (TypeError, ValueError):
            continue
        if chiave in visti:
            continue
        visti.add(chiave)
        media.append(MediaRef(
            id_media=chiave,
            name=str(nome or "") or "media %d" % chiave,
            thumb_file=str(anteprima or ""),
            original_file=str(originale or "")))
        if len(media) >= massimo:
            break
    return media


# ------------------------------------------------------------- sulla mappa

def _quoted(valore: str) -> str:
    """Il valore dentro un'espressione QGIS: l'apostrofo si raddoppia,
    altrimenti «L'Aquila» spezza l'espressione in due."""
    return "'%s'" % str(valore).replace("'", "''")


def _eq(campo: str, valore: str) -> str:
    return '"%s" = %s' % (campo, _quoted(valore))


def pick_feature_expression(unit, available_fields, id_us=None) -> Optional[str]:
    """L'espressione che trova questa unità in un layer, o ``None``.

    ``None`` vuol dire «questo layer non sa chi è»: il chiamante prova il
    prossimo invece di selezionare la geometria sbagliata.
    """
    identita = unit_identity(unit)
    if not identita:
        return None
    campi = {str(c) for c in (available_fields or ())}
    if id_us is not None and "id_us" in campi:
        try:
            return '"id_us" = %d' % int(id_us)
        except (TypeError, ValueError):
            pass
    for sito_f, area_f, us_f, tipo_f in FIELD_SETS:
        if not {sito_f, us_f} <= campi:
            continue
        parti = [_eq(sito_f, identita["sito"])]
        if identita.get("area") and area_f in campi:
            parti.append(_eq(area_f, identita["area"]))
        parti.append(_eq(us_f, identita["us"]))
        if identita.get("unita_tipo") and tipo_f in campi:
            parti.append(_eq(tipo_f, identita["unita_tipo"]))
        return " AND ".join(parti)
    return None

#: Quanto conta un insieme di campi: più piccolo, più preciso.
_PRECISIONE_ID = -1


def candidate_layers(unit, descriptors, id_us=None):
    """I layer che possono trovare questa unità, dal più preciso.

    ``descriptors`` è una sequenza di ``(chiave, nomi_dei_campi)``: la
    chiave è quello che il chiamante vuole riavere indietro — in QGIS il
    layer stesso. Si restituisce ``[(chiave, espressione)]``, e chi
    chiama prova il primo che dà una geometria.

    L'ordine conta perché i layer di un progetto arrivano come capita:
    senza una precedenza si finirebbe per zoomare sul disegno di un'altra
    US che porta lo stesso numero in un altro sito.
    """
    identita = unit_identity(unit)
    if not identita:
        return []
    classificati = []
    for posizione, (chiave, campi) in enumerate(descriptors or ()):
        nomi = {str(c) for c in (campi or ())}
        espressione = pick_feature_expression(unit, nomi, id_us=id_us)
        if not espressione:
            continue
        classificati.append(
            (_precisione(nomi, espressione), posizione, chiave, espressione))
    classificati.sort(key=lambda r: (r[0], r[1]))
    return [(chiave, espressione)
            for _, _, chiave, espressione in classificati]


def _precisione(nomi, espressione) -> float:
    """Il posto in classifica: l'id prima di tutto, poi i nomi della
    scheda, poi quelli dei disegni; a pari insieme, più condizioni vince."""
    if espressione.startswith('"id_us" ='):
        return _PRECISIONE_ID
    for indice, (sito_f, _area_f, us_f, _tipo_f) in enumerate(FIELD_SETS):
        if {sito_f, us_f} <= nomi:
            return indice - espressione.count(" AND ") / 100.0
    return len(FIELD_SETS)


def merge_boxes(boxes) -> Optional[tuple]:
    """Il rettangolo che contiene tutti quelli dati, o ``None``.

    Si lavora su quadruple e non su ``QgsRectangle`` perché la scelta di
    dove inquadrare si prova senza avviare QGIS.
    """
    utili = [b for b in (boxes or ()) if b]
    if not utili:
        return None
    return (min(b[0] for b in utili), min(b[1] for b in utili),
            max(b[2] for b in utili), max(b[3] for b in utili))


def padded_box(box, margin: float = 0.15, minimum: float = 5.0) -> Optional[tuple]:
    """Lo stesso rettangolo con un po' d'aria intorno.

    Dove è piatto — una quota è un punto, un muro può essere una linea —
    si allarga di ``minimum`` invece di moltiplicare per zero: inquadrare
    un rettangolo di larghezza nulla è uno zoom infinito.
    """
    if not box:
        return None
    x1, y1, x2, y2 = (float(v) for v in box)
    larghezza, altezza = x2 - x1, y2 - y1
    dx = larghezza * margin if larghezza > 0 else minimum
    dy = altezza * margin if altezza > 0 else minimum
    return (x1 - dx, y1 - dy, x2 + dx, y2 + dy)


def find_unit_extent(unit, descriptors, id_us=None, *, fetch) -> Optional[tuple]:
    """``(chiave, id_delle_geometrie, rettangolo)`` del primo layer che
    disegna questa unità, o ``None``.

    ``fetch(chiave, espressione)`` restituisce ``[(id, rettangolo)]``: il
    chiamante ci mette dentro QGIS, qui si decide soltanto quale layer
    vince e quanto grande è il risultato. Un layer che solleva o che ha la
    riga senza geometria non ferma la ricerca: si passa al prossimo, che è
    quello che fa la differenza fra «non è disegnata» e «non si è potuto
    guardare».
    """
    for chiave, espressione in candidate_layers(unit, descriptors, id_us=id_us):
        try:
            trovate = list(fetch(chiave, espressione) or ())
        except Exception:                           # noqa: BLE001
            continue
        ids = [i for i, box in trovate if box]
        riquadro = merge_boxes([box for _i, box in trovate])
        if ids and riquadro:
            return (chiave, ids, riquadro)
    return None
