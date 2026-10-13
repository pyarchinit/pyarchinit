"""Lettura e scrittura di ``pyarchinit_view_styles`` con SQLAlchemy Core:
vale su SQLite e su PostgreSQL. Niente Qt, niente QGIS (tranne
:func:`legacy_qgis_styles`, che chiede al layer gli stili salvati da
QGIS in ``layer_styles``)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select, update

from ..db.structures.View_styles_table import View_styles_table as _VS
from .view_styles import LabelRecipe, SavedStyle

TABLE = _VS.pyarchinit_view_styles


def ensure_table(engine) -> None:
    """Crea la tabella se manca, su entrambi i motori. Idempotente."""
    _VS.metadata.create_all(engine, checkfirst=True)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _to_style(row) -> SavedStyle:
    m = row._mapping
    return SavedStyle(id=int(m["id"]), view_name=str(m["view_name"]), site=m["site"],
                      name=str(m["name"] or ""), qml=str(m["qml"] or ""),
                      recipe=LabelRecipe.from_json(m["recipe"]), is_default=bool(m["is_default"]),
                      author=str(m["author"] or ""), updated_at=str(m["updated_at"] or ""))


def _same_site(site: Optional[str]):
    return TABLE.c.site.is_(None) if site in (None, "") else TABLE.c.site == str(site)


def list_styles(engine, view_name: str) -> List[SavedStyle]:
    """Gli stili della vista: prima quelli per tutti i siti, poi per sito,
    in ordine di nome."""
    with engine.connect() as conn:
        righe = conn.execute(select(TABLE).where(TABLE.c.view_name == str(view_name))).fetchall()
    stili = [_to_style(r) for r in righe]
    stili.sort(key=lambda s: (0 if s.for_all_sites else 1, str(s.site or ""), s.name.lower()))
    return stili


def save_style(engine, style: SavedStyle) -> int:
    """Inserisce (``id`` nullo) o aggiorna; torna l'``id`` e lo scrive sullo stile."""
    style.updated_at = now_iso()
    valori = dict(view_name=str(style.view_name), site=(None if style.for_all_sites else str(style.site)),
                  name=str(style.name), qml=str(style.qml), recipe=style.recipe.to_json(),
                  is_default=1 if style.is_default else 0, author=str(style.author or ""),
                  updated_at=style.updated_at)
    with engine.begin() as conn:
        if style.id is None:
            esito = conn.execute(TABLE.insert().values(**valori))
            style.id = int(esito.inserted_primary_key[0])
        else:
            conn.execute(update(TABLE).where(TABLE.c.id == int(style.id)).values(**valori))
    return int(style.id)


def delete_style(engine, style_id: int) -> None:
    with engine.begin() as conn:
        conn.execute(delete(TABLE).where(TABLE.c.id == int(style_id)))


def rename_style(engine, style_id: int, name: str) -> None:
    with engine.begin() as conn:
        conn.execute(update(TABLE).where(TABLE.c.id == int(style_id))
                     .values(name=str(name), updated_at=now_iso()))


def set_default(engine, style_id: int) -> None:
    """Uno solo per (vista, sito) e uno solo per (vista, tutti): gli altri
    con la stessa vista e lo stesso sito si spengono."""
    with engine.begin() as conn:
        riga = conn.execute(select(TABLE.c.view_name, TABLE.c.site)
                            .where(TABLE.c.id == int(style_id))).fetchone()
        if riga is None:
            return
        vista, sito = riga._mapping["view_name"], riga._mapping["site"]
        conn.execute(update(TABLE).where(TABLE.c.view_name == vista).where(_same_site(sito))
                     .values(is_default=0))
        conn.execute(update(TABLE).where(TABLE.c.id == int(style_id)).values(is_default=1))


def clear_default(engine, style_id: int) -> None:
    with engine.begin() as conn:
        conn.execute(update(TABLE).where(TABLE.c.id == int(style_id)).values(is_default=0))


def legacy_qgis_styles(layer) -> list:
    """Gli stili che QGIS ha salvato nel database per questo layer
    (``layer_styles``): ``[(id, nome)]``, vuoto se il provider non li sa."""
    try:
        esito = layer.listStylesInDatabase()
    except Exception:                               # noqa: BLE001
        return []
    try:
        _n, ids, nomi, _descrizioni, _errore = esito
    except (TypeError, ValueError):
        return []
    return list(zip([str(i) for i in ids], [str(n) for n in nomi]))
