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


def _ident(nome: str) -> str:
    return '"%s"' % str(nome).replace('"', '""')


def _is_pg(conn) -> bool:
    return conn.dialect.name.startswith("postgres")


def column_sequence(conn, table: str, column: str) -> Optional[str]:
    """Il nome (regclass) della sequenza che dà i valori a ``table.column``,
    o None: su SQLite, per una tabella o una colonna che non ci sono, per
    una colonna senza sequenza."""
    if not _is_pg(conn):
        return None
    try:
        with conn.begin_nested():
            if conn.execute(text("SELECT to_regclass(:t)"), {"t": _ident(table)}).scalar() is None:
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


def sync_sequence(conn, table: str, column: str) -> bool:
    """Porta il contatore di ``table.column`` oltre il massimo della colonna,
    se è indietro; True se l'ha spostato. Nella transazione di chi chiama
    (un SAVEPOINT intorno, così un errore non la guasta)."""
    seq = column_sequence(conn, table, column)
    if not seq:
        return False
    try:
        with conn.begin_nested():
            massimo = conn.execute(text("SELECT MAX(%s) FROM %s" % (_ident(column), _ident(table)))).scalar()
            if massimo is None:
                return False
            ultimo, chiamato = conn.execute(text("SELECT last_value, is_called FROM %s" % seq)).fetchone()
            passo = conn.execute(text("SELECT seqincrement FROM pg_sequence WHERE seqrelid = CAST(:s AS regclass)"),
                                 {"s": seq}).scalar() or 1
            prossimo = int(ultimo) + int(passo) if chiamato else int(ultimo)
            if prossimo > int(massimo):
                return False
            conn.execute(text("SELECT setval(CAST(:s AS regclass), :v, true)"), {"s": seq, "v": int(massimo)})
            return True
    except Exception as e:                                  # noqa: BLE001
        log.warning("sequenza %s non rimessa in pari: %s", seq, e)
        return False
