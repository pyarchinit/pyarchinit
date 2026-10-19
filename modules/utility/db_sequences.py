"""I contatori (sequenze) di PostgreSQL in pari con gli id scritti a mano.

Le schede di pyArchInit scrivono gli id MAX + 1 (``max_num_id``), e così
l'import da QField: il contatore della colonna non si muove. Il primo record
che usa l'id di default (un poligono disegnato in QGIS, un documento dei
disegni ricavati dal 3D) prenderebbe allora un id già usato: «duplicate key».

``sync_sequence`` porta il contatore oltre il massimo della colonna, mai
indietro. Lo trova sia quando è OWNED BY la colonna (SERIAL, identity) sia
quando la colonna lo chiama solo nel DEFAULT (``nextval('…'::regclass)``),
come fa lo schema del plugin per i gid. Su SQLite non serve: un INTEGER
PRIMARY KEY riparte sempre dal massimo.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import text

log = logging.getLogger(__name__)


MOVED, IN_STEP, FAILED = "moved", "ok", "failed"


def _ident(nome: str) -> str:
    return '"%s"' % str(nome).replace('"', '""')


def _is_pg(conn) -> bool:
    return conn.dialect.name.startswith("postgres")


def _in_transaction(conn, fn):
    """Chiama ``fn()`` dentro la transazione di chi chiama, o in una propria
    se non ce n'è una: un SAVEPOINT su una connessione senza transazione ne
    aprirebbe una da sé e la lascerebbe aperta (il ``begin()`` dopo
    fallirebbe)."""
    if conn.in_transaction():
        return fn()
    with conn.begin():
        return fn()


def column_sequence(conn, table: str, column: str) -> Optional[str]:
    """Il nome (regclass) della sequenza che dà i valori a ``table.column``,
    o None: su SQLite, per una tabella o una colonna che non ci sono, per
    una colonna senza sequenza."""
    if not _is_pg(conn):
        return None
    return _in_transaction(conn, lambda: _column_sequence(conn, table, column))


def _column_sequence(conn, table: str, column: str) -> Optional[str]:
    try:
        with conn.begin_nested():
            # la colonna prima di tutto: una che non c'è (l'import da QField
            # prova le due grafie della chiave dei collegamenti) non è un errore
            if conn.execute(text(
                    "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :c "
                    "AND attnum > 0 AND NOT attisdropped"), {"t": _ident(table), "c": column}).scalar() is None:
                return None
            # OWNED BY: SERIAL e identity
            seq = conn.execute(text("SELECT pg_get_serial_sequence(:t, :c)"),
                               {"t": _ident(table), "c": column}).scalar()
            if seq:
                return str(seq)
            # solo nel DEFAULT: la sequenza da cui dipende il default della colonna
            seq = conn.execute(text(
                "SELECT d.refobjid::regclass::text FROM pg_attrdef ad "
                "JOIN pg_attribute a ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum "
                "JOIN pg_depend d ON d.classid = 'pg_attrdef'::regclass AND d.objid = ad.oid "
                "AND d.refclassid = 'pg_class'::regclass "
                "JOIN pg_class s ON s.oid = d.refobjid AND s.relkind = 'S' "
                "WHERE ad.adrelid = to_regclass(:t) AND a.attname = :c AND NOT a.attisdropped "
                "LIMIT 1"), {"t": _ident(table), "c": column}).scalar()
            return str(seq) if seq else None
    except Exception as e:                                  # noqa: BLE001
        log.warning("sequenza di %s.%s non letta: %s", table, column, e)
        return None


def sync_sequence_state(conn, table: str, column: str) -> str:
    """Porta il contatore di ``table.column`` oltre il massimo della colonna,
    se è indietro. ``MOVED`` se l'ha spostato; ``IN_STEP`` se non serviva
    (anche su SQLite e per una colonna senza sequenza); ``FAILED`` se è
    indietro e non si è potuto spostare (permessi, MAXVALUE): chi usa l'id
    di default allora troverebbe un doppione. Nella transazione di chi
    chiama, con un SAVEPOINT intorno, così un errore non la guasta."""
    seq = column_sequence(conn, table, column)
    if not seq:
        return IN_STEP
    return _in_transaction(conn, lambda: _sync(conn, table, column, seq))


def _sync(conn, table: str, column: str, seq: str) -> str:
    try:
        with conn.begin_nested():
            massimo = conn.execute(text("SELECT MAX(%s) FROM %s" % (_ident(column), _ident(table)))).scalar()
            if massimo is None:
                return IN_STEP
            ultimo, chiamato = conn.execute(text("SELECT last_value, is_called FROM %s" % seq)).fetchone()
            passo = conn.execute(text("SELECT seqincrement FROM pg_sequence WHERE seqrelid = CAST(:s AS regclass)"),
                                 {"s": seq}).scalar() or 1
            prossimo = int(ultimo) + int(passo) if chiamato else int(ultimo)
            if prossimo > int(massimo):
                return IN_STEP
            conn.execute(text("SELECT setval(CAST(:s AS regclass), :v, true)"), {"s": seq, "v": int(massimo)})
            return MOVED
    except Exception as e:                                  # noqa: BLE001
        log.warning("sequenza %s non rimessa in pari: %s", seq, e)
        return FAILED


def sync_sequence(conn, table: str, column: str) -> bool:
    """Come :func:`sync_sequence_state`; True se ha spostato il contatore."""
    return sync_sequence_state(conn, table, column) == MOVED
