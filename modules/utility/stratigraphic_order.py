"""Drawing order of the US/USM layers, computed like the Time Manager.

The Time Manager (tabs/Gis_Time_controller.py) reads order_layer as time
going up — 0 = oldest, N = most recent: "order_layer <= v" builds the site
up level by level — and places a US in time through the chronology
(cron_iniziale) of its periodo_iniziale / fase_iniziale in
periodizzazione_table. The map draws in the same order, so the most recent
units end up on top: undated units first, then periods by chronology, then
order_layer, then stratigraph_index_us (the cut, 2, over its fill, 1).

Pure Python: the QGIS side (QgsFeatureRequest.OrderBy on the renderer) is
apply_stratigraphic_order() in modules/utility/create_style.py.
"""
from __future__ import annotations

#: attributes that place a feature in the periodization
PERIOD_FIELDS = ("sito", "periodo_iniziale", "fase_iniziale", "cont_per")


def norm(value):
    """Comparable form of a periodo / fase / cont_per value: the views store
    text ('2', '2.1'), periodizzazione_table numbers (2, 2.1).
    '2', 2, 2.0 -> '2'; '2.10', 2.1 -> '2.1'; None, '' -> None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return text
    return str(int(number)) if number.is_integer() else repr(number)


def period_starts(rows) -> dict:
    """Start years from periodizzazione_table rows (sito, periodo, fase,
    cron_iniziale, cont_per): of each phase, of each period (its oldest
    phase) and of each cont_per code, per site."""
    starts = {}

    def keep(key, year):
        if key not in starts or year < starts[key]:
            starts[key] = year

    for sito, periodo, fase, cron_iniziale, cont_per in rows:
        try:
            year = float(cron_iniziale)
        except (TypeError, ValueError):
            continue
        year = int(year) if year.is_integer() else year
        site, period, phase = norm(sito), norm(periodo), norm(fase)
        if period is not None:
            keep(("phase", site, period, phase), year)
            keep(("period", site, period), year)
        code = norm(cont_per)
        if code is not None:
            keep(("code", site, code), year)
    return starts


def period_start(starts, sito, periodo, fase, cont_per):
    """Start year of a US: that of its periodo_iniziale / fase_iniziale (as
    the Time Manager does), else of its oldest cont_per code; None when
    unknown."""
    site, period, phase = norm(sito), norm(periodo), norm(fase)
    if period is not None:
        year = starts.get(("phase", site, period, phase)) if phase is not None else None
        if year is None:
            year = starts.get(("period", site, period))
        if year is not None:
            return year
    years = [starts.get(("code", site, norm(code))) for code in str(cont_per or "").split("/")]
    years = [y for y in years if y is not None]
    return min(years) if years else None


def _condition(field, value):
    name = '"%s"' % field.replace('"', '""')
    if value is None:
        return "%s IS NULL" % name
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, (int, float)):
        return "%s = %r" % (name, value)
    return "%s = '%s'" % (name, str(value).replace("'", "''"))


def period_case(combos):
    """QGIS expression giving each feature the start year of its period.
    ``combos``: ({field: value as stored in the layer}, start year or None);
    values are compared exactly as stored. None when no period is known."""
    whens = ["WHEN %s THEN %s" % (" AND ".join(_condition(f, v) for f, v in values.items()), start)
             for values, start in combos if start is not None]
    return "CASE %s END" % " ".join(whens) if whens else None


def order_clauses(field_names, period_expression=None) -> list:
    """(expression, ascending, nulls first) of the drawing order: the first
    drawn end up underneath."""
    names = set(field_names)
    clauses = []
    if period_expression:
        clauses.append((period_expression, True, True))       # undated first, oldest period first
    if "order_layer" in names:
        clauses.append(('"order_layer"', True, False))        # 0 = oldest ... N = most recent
    if "stratigraph_index_us" in names:
        clauses.append(('"stratigraph_index_us"', True, False))  # the cut (2) over its fill (1)
    return clauses
