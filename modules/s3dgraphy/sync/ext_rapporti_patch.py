"""Runtime patch: multilingual / localized d13 for the vendored ext_libs.

Why this exists
---------------
The d13 ``physical_relationships`` packed string is built by the s3dgraphy
**core** GraphML exporter, which does
``from ...sync.rapporti import serialize_rapporti_from_edges`` — i.e. it
resolves against ``ext_libs/s3dgraphy/sync/rapporti.py``, NOT pyArchInit's
own ``modules/s3dgraphy/sync/rapporti.py``. ``ext_libs/`` is a *vendored*
copy reinstalled from PyPI on every ``pip install -r requirements.txt``,
so edits there are not durable.

pyArchInit's tracked copy (``modules/s3dgraphy/sync/rapporti.py``) carries
the fix (2026-06): recognise the multilingual US/USM ``unita_tipo`` codes
(SU/WSU=en, SE/MSE=de, UE/UEM=es·ca·pt, USZ=ro, ΣΜ/ΤΣΜ=el — see
``pyarchinit_i18n_stratigraphic.UNIT_TYPE_ABBREV``) so real Harris units
take the verbose branch, and emit the localized label from the source
node's own ``rapporti`` column, capitalized ("Covers"/"Copre"), instead of
the ``>>`` / ``<<`` shorthand.

This module copies those corrected symbols onto the ext_libs module at
plugin start so the export path picks them up. It is a stop-gap: once the
fix is released upstream (s3Dgraphy > 1.6.0.dev7) and ``requirements.txt``
pins a version that includes it, delete this module and its call site in
``pyarchinitPlugin.initGui``.
"""
from __future__ import annotations

#: Public + internal symbols that must agree between the two copies. The
#: functions carry their own module globals, so once ``serialize_…`` /
#: ``select_…`` point at the fixed copy they resolve every helper and
#: constant inside the fixed module — copying the constants too keeps any
#: direct ``ext.select_rapporti_label`` / ``ext.CANONICAL_UNIT_TYPES``
#: caller consistent.
_PATCHED_NAMES = (
    "CANONICAL_UNIT_TYPES",
    "CONTINUITY_UNIT_TYPES",
    "select_rapporti_label",
    "serialize_rapporti_from_edges",
    "_source_rapporti_label",
    "_SHORTHAND_TOKENS",
)

_SENTINEL = "_pyarchinit_multilingual_d13_patch"


def apply() -> bool:
    """Idempotently patch ``ext_libs`` ``s3dgraphy.sync.rapporti``.

    Returns ``True`` when the patch was applied this call, ``False`` if the
    ext_libs copy is unavailable or was already patched. Never raises — the
    caller wraps it defensively but this keeps plugin start robust.
    """
    try:
        import s3dgraphy.sync.rapporti as ext  # ext_libs copy (export path)
        from . import rapporti as fixed        # pyArchInit tracked copy
    except Exception:
        return False

    if ext is fixed or getattr(ext, _SENTINEL, False):
        return False

    applied = False
    for name in _PATCHED_NAMES:
        if hasattr(fixed, name):
            try:
                setattr(ext, name, getattr(fixed, name))
                applied = True
            except Exception:
                pass
    if applied:
        setattr(ext, _SENTINEL, True)
    return applied
