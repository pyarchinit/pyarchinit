"""Stili delle viste di pyArchInit: il registro delle viste, le ricette
delle etichette, la scelta dello stile (spec 2026-10-13, «Stili delle
viste»). Modulo puro: niente Qt né QGIS, così si prova da solo. La parte
che tocca i layer sta in :mod:`view_styles_apply`, la tabella in
:mod:`view_styles_store`, la finestra in ``gui/view_styles_dialog.py``.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, Optional, Sequence, Tuple

#: Le ricette delle etichette che la finestra sa comporre.
PRESETS = ("none", "us_circle", "quota", "field")
#: Dove mettere l'etichetta, per il preset ``field``.
PLACEMENTS = ("centroid", "around_point", "above_symbol")

#: I gruppi dell'elenco, nell'ordine in cui compaiono.
GROUPS: Dict[str, Dict[str, str]] = {
    "unita": {"it": "Unità stratigrafiche", "en": "Stratigraphic units"},
    "quote": {"it": "Quote", "en": "Elevations"},
    "documentazione": {"it": "Documentazione", "en": "Documentation"},
    "strutture": {"it": "Strutture e tombe", "en": "Structures and burials"},
    "ut": {"it": "Unità topografiche", "en": "Topographic units"},
    "siti": {"it": "Siti", "en": "Sites"},
    "reperti": {"it": "Reperti", "en": "Finds"},
    "sezioni": {"it": "Sezioni", "en": "Sections"},
}


@dataclass(frozen=True)
class ViewSpec:
    """Una vista di pyArchInit come la vede la finestra degli stili."""
    name: str
    label: Dict[str, str]
    geometry: str                      # polygon | line | point
    site_field: Optional[str]          # il campo con il nome del sito, per filtrare
    qml: Optional[str]                 # QML fornito in modules/gis/styles_spatialite
    recipe: Optional[str]              # la ricetta delle etichette di partenza
    category_fields: Tuple[str, ...]   # campi sensati per una categorizzazione
    group: str


def _v(name, it, en, geometry, site_field, qml=None, recipe=None, category_fields=(), group="unita"):
    return ViewSpec(name, {"it": it, "en": en}, geometry, site_field, qml, recipe,
                    tuple(category_fields), group)


VIEWS: Tuple[ViewSpec, ...] = (
    _v("pyarchinit_us_view", "US Vista", "SU view", "polygon", "scavo_s", "us_view.qml", "us_circle",
       ("d_stratigrafica", "tipo_us_s", "d_interpretativa", "cont_per", "us"), "unita"),
    _v("pyarchinit_usm_view", "USM Vista", "SUW View", "polygon", "scavo_s", "us_view.qml", "us_circle",
       ("d_stratigrafica", "tipo_us_s", "d_interpretativa", "cont_per", "us"), "unita"),
    _v("pyarchinit_us_negative_doc_view", "Vista US Negative per sezioni/elevati",
       "Negative SU for section/elevation view", "polygon", "sito_n", None, None, ("tipo_doc_n",), "unita"),
    _v("pyarchinit_quote_view", "Quote US Vista", "SU elevation view", "point", "sito_q", "quote_us_view.qml",
       "quota", (), "quote"),
    _v("pyarchinit_quote_usm_view", "Quote USM Vista", "SUW Elevation View", "point", "sito_q",
       "quote_us_view.qml", "quota", (), "quote"),
    _v("pyarchinit_doc_view", "Documentazione Vista", "Documentation view", "polygon", "sito", None, None,
       ("tipo_doc",), "documentazione"),
    _v("pyarchinit_doc_view_b", "Documentazione Vista B", "Documentation view B", "polygon", "sito", None, None,
       ("tipo_doc",), "documentazione"),
    _v("pyarchinit_strutture_view", "Ipotesi strutture da scavo Vista", "Hypothetical excavation structures view",
       "polygon", "sito", None, None, ("tipologia_struttura",), "strutture"),
    _v("pyarchinit_tomba_view", "Tomba Vista", "Taphonomy view", "polygon", "sito", None, None,
       ("tipo_sepoltura", "tipo_deposizione"), "strutture"),
    _v("pyarchinit_individui_view", "Individui Vista", "Individuals view", "polygon", "sito", None, None,
       (), "strutture"),
    _v("pyarchinit_ut_point_view", "UT puntuali Vista", "TU points view", "point", "sito", None, None, (), "ut"),
    _v("pyarchinit_ut_line_view", "UT lineari Vista", "TU lines view", "line", "sito", None, None,
       ("tipo_linea",), "ut"),
    _v("pyarchinit_ut_polygon_view", "UT poligonali Vista", "TU polygons view", "polygon", "sito", None, None,
       (), "ut"),
    _v("pyarchinit_site_view", "Localizzazione siti Vista", "Site point view", "point", "sito", None, None,
       (), "siti"),
    _v("pyarchinit_siti_polygonal_view", "Perimetrazione siti poligonali Vista", "Areal site view", "polygon",
       "sito", None, None, (), "siti"),
    _v("pyarchinit_reperti_view", "Reperti Vista", "Artefact view", "point", "sito", None, None,
       ("tipo_reperto",), "reperti"),
    _v("pyarchinit_sezioni_view", "Sezioni di scavo Vista", "Excavation section view", "line", "sito", None, None,
       ("tipo_doc",), "sezioni"),
)

_BY_NAME = {v.name: v for v in VIEWS}


def view_by_name(name: str) -> Optional[ViewSpec]:
    return _BY_NAME.get(str(name or ""))


def view_label(spec: ViewSpec, lang: Optional[str] = None) -> str:
    lingua = "it" if str(lang or "").lower().startswith("it") else "en"
    return spec.label.get(lingua) or spec.label.get("en") or spec.name


def group_label(group: str, lang: Optional[str] = None) -> str:
    lingua = "it" if str(lang or "").lower().startswith("it") else "en"
    voce = GROUPS.get(group) or {}
    return voce.get(lingua) or voce.get("en") or group


@dataclass(frozen=True)
class LabelRecipe:
    """Quello che il QML non sa dire delle etichette: la ricetta.

    ``one_per_unit`` si ricalcola a ogni caricamento (l'elenco dei disegni
    da etichettare cambia col filtro); ``preset`` dice chi la compone."""
    enabled: bool = False
    preset: str = "none"
    expression: Optional[str] = None
    placement: str = "centroid"
    offset_mm: float = 0.0
    one_per_unit: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, text) -> "LabelRecipe":
        try:
            dati = json.loads(text) if text else {}
        except (TypeError, ValueError):
            dati = {}
        if not isinstance(dati, dict):
            dati = {}
        preset = str(dati.get("preset") or "none")
        placement = str(dati.get("placement") or "centroid")
        try:
            scostamento = float(dati.get("offset_mm") or 0.0)
        except (TypeError, ValueError):
            scostamento = 0.0
        return cls(enabled=bool(dati.get("enabled", False)),
                   preset=preset if preset in PRESETS else "none",
                   expression=(str(dati["expression"]) if dati.get("expression") else None),
                   placement=placement if placement in PLACEMENTS else "centroid",
                   offset_mm=scostamento,
                   one_per_unit=bool(dati.get("one_per_unit", False)))


def default_recipe(spec: ViewSpec) -> LabelRecipe:
    """La ricetta di partenza della vista: quella che il plugin applica
    quando non c'è uno stile salvato."""
    if spec.recipe == "us_circle":
        return LabelRecipe(enabled=True, preset="us_circle", one_per_unit=True)
    if spec.recipe == "quota":
        return LabelRecipe(enabled=True, preset="quota", placement="above_symbol")
    return LabelRecipe()


@dataclass
class SavedStyle:
    """Una riga di ``pyarchinit_view_styles``."""
    id: Optional[int]
    view_name: str
    site: Optional[str]                # None = tutti i siti
    name: str
    qml: str
    recipe: LabelRecipe = field(default_factory=LabelRecipe)
    is_default: bool = False
    author: str = ""
    updated_at: str = ""

    @property
    def for_all_sites(self) -> bool:
        return self.site is None or not str(self.site).strip()


def choose_style(styles: Iterable[SavedStyle], site: Optional[str]) -> Optional[SavedStyle]:
    """Lo stile che comanda al caricamento: il predefinito del sito, poi
    quello predefinito per tutti i siti, poi niente."""
    elenco = [s for s in (styles or ()) if getattr(s, "is_default", False)]
    if site:
        for s in elenco:
            if not s.for_all_sites and str(s.site) == str(site):
                return s
    for s in elenco:
        if s.for_all_sites:
            return s
    return None
