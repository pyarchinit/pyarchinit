"""I pittogrammi ufficiali dell'Extended Matrix, pronti da disegnare.

Estrattore, combinatore e documento non sono una forma geometrica: sono
un **disegno**, quello del manuale dell'Extended Matrix e della tavolozza
di yEd. Le regole visive della libreria
(``ext_libs/s3dgraphy/JSON_config/em_visual_rules.json``) se lo portano
dietro già pronto — ``2d_glyphs`` — come tracciati ``d`` con soltanto
comandi assoluti ``M``/``L``/``C``/``Z``, nelle coordinate del
``viewBox``: «new Path2D(d) and nothing else», dice il file. Non c'è
nessun file SVG da aprire e nessuna immagine da decodificare, quindi
nessun disegno che sparisce quando un file manca.

Qui sta la sola lettura di quei dati, e ci sta **una volta**: il writer
SVG e la scena Qt disegnano gli stessi tracciati, con gli stessi colori e
nella stessa posizione, altrimenti il file salvato e l'anteprima a
schermo direbbero due cose diverse. Niente Qt: si prova headless.

Tre casi, e il file dice perché sono tre:

* ``2d_render_glyph_types.types`` — **icona centrata** (estrattore,
  combinatore). La casella è guidata dall'altezza: larghezza = altezza x
  ``aspect``. Il nome si scrive SOTTO il disegno.
* ``2d_render_glyph_types.sheet_types`` — il **documento**. Ha i suoi
  tracciati, ma non è un'icona centrata: il suo nome si scrive SOPRA il
  foglio, al 62% dell'altezza, senza tagliarlo. Metterlo fra i ``types``
  schiaccerebbe il nome a «…».
* La **proprietà** non è in nessuno dei due elenchi e non ci sarà mai:
  «a text annotation in a bracket, whose width its text decides». Non ha
  tracciati in ``2d_glyphs``; il disegno autorevole è
  ``src/2D/property.svg`` — un campo grigio chiaro con gli angoli
  arrotondati e una parentesi nera sul lato sinistro — e la larghezza
  gliela dà il testo. Le proporzioni stanno qui sotto, misurate una
  volta sola da quel file come fa ``aspect`` con gli altri.

I colori non si toccano: il ruolo di ogni livello (``_roles``) serve a
chi rifà un tema scuro, e noi disegniamo sulla carta chiara della
matrice. Ogni livello si disegna con il colore che si porta.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: Quanti caratteri al massimo entrano in una etichetta: una casella è
#: larga quanto è larga, e un nome che sborda è peggio di un nome
#: accorciato. Il writer SVG e la vista Qt tagliano qui, e
#: l'impaginatore misura la proprietà sullo stesso taglio.
MAX_LABEL = 16

#: Larghezza media di un carattere dell'etichetta, in pixel della
#: matrice. L'impaginatore è puro — non può chiedere a Qt quanto è largo
#: un testo — e la proprietà ha bisogno di una misura: corpo 12 di una
#: grottesca di sistema, circa 0,55 em. Serve a dare una larghezza, non
#: a impaginare un libro.
CHAR_W = 6.6

#: Dove va il nome di un foglio: al 62% della sua altezza, come fa il
#: renderer di EMStudio, e senza tagliarlo.
SHEET_LABEL_Y = 0.62

#: Quanto sotto l'icona centrata si scrive il nome.
GLYPH_LABEL_GAP = 12.0

# --------------------------------------------------- la proprietà a mano
#
# Misurate una volta sola da ``src/2D/property.svg`` (viewBox 26.68 x
# 11.59) e scritte qui come frazioni dell'altezza della casella, perché
# la larghezza della proprietà è il suo testo e non si può prendere dal
# disegno. Stessa scelta di ``2d_render_glyph_types.aspect``: un numero
# statico, misurato dove il disegno sta, invece di un numero letto a
# ogni avvio.

#: Spessore della parentesi (0,75 su 11,59 di altezza).
PROP_STROKE = 0.0647
#: Raggio degli angoli (1,5 su 11,59).
PROP_RADIUS = 0.1294
#: Quanto sono lunghi i due bracci della parentesi (6,77 su 11,59).
PROP_ARM = 0.5841
#: Il campo grigio chiaro su cui sta il testo.
PROP_PAPER = "#DEDDDE"
#: L'inchiostro della parentesi.
PROP_INK = "#000000"
#: Il respiro fra la parentesi, il testo e il bordo destro.
PROP_PAD = 6.0

#: Il fattore di Bézier che approssima un quarto di cerchio.
_KAPPA = 0.5523


@dataclass(frozen=True)
class GlyphLayer:
    """Un livello del pittogramma: un tracciato, un colore."""
    d: str
    role: str
    commands: Tuple[tuple, ...]
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: float = 0.0
    fill_rule: str = "nonzero"
    line_cap: str = "butt"
    line_join: str = "miter"
    opacity: float = 1.0


@dataclass(frozen=True)
class Glyph:
    """Il pittogramma di un tipo di nodo, nelle coordinate del suo viewBox."""
    key: str
    view_box: Tuple[float, float, float, float]
    aspect: float
    layers: Tuple[GlyphLayer, ...]
    #: Il nome si scrive SOPRA il disegno (il foglio del documento) invece
    #: che sotto: è la differenza fra ``sheet_types`` e ``types``.
    sheet: bool = False


@dataclass(frozen=True)
class PropertyDrawing:
    """La proprietà: un campo grigio e una parentesi, in coordinate scena."""
    field_d: str
    bracket_d: str
    fill: str
    stroke: str
    stroke_width: float
    #: Dove comincia il testo: subito dopo il braccio della parentesi.
    text_x: float
    text_right: float


def rules_path() -> Path:
    """Il file delle regole visive della libreria vendorizzata."""
    return (Path(__file__).resolve().parents[2] / "ext_libs" / "s3dgraphy"
            / "JSON_config" / "em_visual_rules.json")


_CACHE: Dict[str, object] = {}

_TOKEN = re.compile(r"[A-Za-z]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

#: Quanti numeri vuole ogni comando ammesso dal contratto di ``_layer``.
_ARGS = {"M": 2, "L": 2, "C": 6, "Z": 0}


def parse_path(d: str) -> Tuple[tuple, ...]:
    """I comandi di un tracciato, o ``ValueError`` se non è del contratto.

    Il file promette soltanto ``M``/``L``/``C``/``Z`` assoluti — archi,
    comandi relativi e scorciatoie sono già stati convertiti da chi l'ha
    generato. Qui non si prova a indovinare il resto: chi legge un
    tracciato che non rispetta la promessa ripiega sulla forma
    geometrica, che è quello che il file stesso prevede.
    """
    token = _TOKEN.findall(str(d or ""))
    comandi: List[tuple] = []
    corrente: Optional[str] = None
    i = 0
    while i < len(token):
        pezzo = token[i]
        if pezzo.isalpha():
            if pezzo not in _ARGS:
                raise ValueError("comando «%s» non ammesso in un glifo" % pezzo)
            i += 1
            if pezzo == "Z":
                comandi.append(("Z",))
                corrente = None
                continue
            corrente = pezzo
        if corrente is None:
            raise ValueError("tracciato senza comando: «%s»" % str(d)[:40])
        quanti = _ARGS[corrente]
        if i + quanti > len(token):
            raise ValueError("comando «%s» senza abbastanza numeri" % corrente)
        valori = []
        for k in range(quanti):
            if token[i + k].isalpha():
                raise ValueError("comando «%s» senza abbastanza numeri"
                                 % corrente)
            valori.append(float(token[i + k]))
        comandi.append((corrente,) + tuple(valori))
        i += quanti
        if corrente == "M":
            # Ripetizione implicita di «M»: l'SVG dice che è una linea.
            corrente = "L"
    if not comandi:
        raise ValueError("tracciato vuoto")
    return tuple(comandi)


def _float(valore, ripiego: float) -> float:
    try:
        return float(valore)
    except (TypeError, ValueError):
        return ripiego


def label_overhang(node_type: str, label, w: float) -> float:
    """Quanto il nome sborda dalla casella, da un lato solo.

    Il nome di un'icona centrata sta sotto il disegno, quello di un
    foglio ci sta sopra: in tutt'e due i casi centrato e **non
    tagliato** — tagliarlo ridurrebbe il nome di un documento a «…», che
    è la ragione per cui il file tiene il documento fuori dai ``types``.
    La casella però è stretta, e la tela deve essere larga abbastanza
    perché l'ultimo nome a destra non finisca fuori dal foglio.
    """
    if glyph_for(node_type) is None:
        return 0.0
    return max(0.0, (label_width(label) - float(w)) / 2.0)


def _layer(grezzo) -> GlyphLayer:
    d = str((grezzo or {}).get("d") or "")
    return GlyphLayer(
        d=d,
        role=str((grezzo or {}).get("role") or ""),
        commands=parse_path(d),
        fill=(str(grezzo["fill"]) if grezzo.get("fill") else None),
        stroke=(str(grezzo["stroke"]) if grezzo.get("stroke") else None),
        stroke_width=_float(grezzo.get("stroke_width"), 0.0),
        fill_rule=str(grezzo.get("fill_rule") or "nonzero"),
        line_cap=str(grezzo.get("line_cap") or "butt"),
        line_join=str(grezzo.get("line_join") or "miter"),
        opacity=_float(grezzo.get("opacity"), 1.0))


def _rules() -> dict:
    regole = _CACHE.get("rules")
    if regole is None:
        try:
            regole = json.loads(rules_path().read_text(encoding="utf-8"))
        except Exception:                           # noqa: BLE001
            regole = {}                             # senza regole si ripiega
        if not isinstance(regole, dict):
            regole = {}
        _CACHE["rules"] = regole
    return regole                                   # type: ignore[return-value]


def _glyphs() -> Dict[str, Glyph]:
    pronti = _CACHE.get("glyphs")
    if pronti is not None:
        return pronti                               # type: ignore[return-value]
    regole = _rules()
    elenchi = regole.get("2d_render_glyph_types") or {}
    centrati = {str(t) for t in (elenchi.get("types") or [])}
    fogli = {str(t) for t in (elenchi.get("sheet_types") or [])}
    aspetti = elenchi.get("aspect") or {}
    disegni = regole.get("2d_glyphs") or {}
    pronti = {}
    for chiave in sorted(centrati | fogli):
        grezzo = disegni.get(chiave)
        if not isinstance(grezzo, dict):
            continue                                # nessun tracciato: la forma
        riquadro = grezzo.get("viewBox") or []
        if len(riquadro) != 4:
            continue
        try:
            livelli = tuple(_layer(l) for l in (grezzo.get("layers") or []))
        except ValueError:
            # Un tracciato fuori contratto: meglio la forma geometrica —
            # che il file stesso dichiara come ripiego — di un disegno
            # monco che il writer SVG e la scena Qt interpreterebbero in
            # due modi diversi.
            continue
        if not livelli:
            continue
        pronti[chiave] = Glyph(
            key=chiave,
            view_box=tuple(_float(v, 0.0) for v in riquadro),  # type: ignore
            aspect=_float(grezzo.get("aspect")
                          or aspetti.get(chiave), 1.0) or 1.0,
            layers=livelli,
            sheet=chiave in fogli)
    _CACHE["glyphs"] = pronti
    return pronti


def glyph_for(node_type: str) -> Optional[Glyph]:
    """Il pittogramma del tipo, o ``None`` se si disegna con la forma.

    La tabella è indicizzata per ``node_type`` di esecuzione — è una
    scelta del file, perché la leggono sia EMStudio sia il suo motore di
    impaginazione — quindi niente sigle: ``extractor``, non ``EXT``.
    """
    return _glyphs().get(str(node_type or ""))


def is_glyph(node_type: str) -> bool:
    """Vero se il tipo si disegna con il suo pittogramma."""
    return glyph_for(node_type) is not None


def is_sheet(node_type: str) -> bool:
    """Vero se il nome va scritto SOPRA il disegno (il documento)."""
    glifo = glyph_for(node_type)
    return bool(glifo and glifo.sheet)


def is_property(node_type: str) -> bool:
    """Vero se è la proprietà: una annotazione fra parentesi."""
    return str(node_type or "") == "property"


def contain(glyph: Glyph, x: float, y: float, w: float,
            h: float) -> Tuple[float, float, float]:
    """Scala e spostamento per infilare il ``viewBox`` nella casella.

    «Fit the viewBox into the node box with CONTAIN, centred»: è quello
    per cui ``aspect`` esiste, e con la casella guidata dall'altezza il
    disegno riempie la casella invece di galleggiarci dentro.
    """
    vx, vy, vw, vh = glyph.view_box
    if vw <= 0 or vh <= 0:
        return 1.0, x, y
    scala = min(w / vw, h / vh)
    return (scala,
            x + (w - vw * scala) / 2.0 - vx * scala,
            y + (h - vh * scala) / 2.0 - vy * scala)


def short_label(testo, massimo: int = MAX_LABEL) -> str:
    """L'etichetta tagliata alla lunghezza che una casella regge."""
    testo = str(testo)
    return testo if len(testo) <= massimo else testo[:massimo - 1] + "…"


def label_width(testo) -> float:
    """Quanto viene larga l'etichetta, a occhio ma sempre allo stesso modo."""
    return len(short_label(testo)) * CHAR_W


def box_size(node_type: str, label, box_w: float,
             box_h: float) -> Tuple[float, float]:
    """Quanto è grande la casella di una unità.

    Tre regole, e due sono del file:

    * un pittogramma ha la casella **guidata dall'altezza** — larghezza =
      altezza x ``aspect`` — se no un disegno quadrato dentro una casella
      larga lascia margini vuoti e la freccia arriva lontano dal disegno;
    * la **proprietà** è larga quanto il suo testo, più la parentesi;
    * tutto il resto — le unità stratigrafiche — resta come è sempre
      stato, che è il punto: la matrice non deve cambiare faccia.
    """
    glifo = glyph_for(node_type)
    if glifo is not None:
        return (box_h * glifo.aspect, box_h)
    if is_property(node_type):
        larghezza = (box_h * PROP_ARM + PROP_PAD * 2.0 + label_width(label))
        return (max(min(larghezza, box_w), box_h), box_h)
    return (box_w, box_h)


def property_drawing(x: float, y: float, w: float,
                     h: float) -> PropertyDrawing:
    """Il disegno della proprietà dentro la casella data.

    Due tracciati, come ``src/2D/property.svg``: il campo grigio con gli
    angoli arrotondati e, sopra, la parentesi aperta che ne borda solo il
    lato sinistro. I tracciati escono con gli stessi comandi assoluti dei
    pittogrammi, così il writer SVG li scrive e la scena Qt li legge
    senza che nessuno dei due reinventi la forma.
    """
    sw = h * PROP_STROKE
    i = sw / 2.0
    x0, y0 = x + i, y + i
    x1, y1 = x + w - i, y + h - i
    r = min(h * PROP_RADIUS, (x1 - x0) / 2.0, (y1 - y0) / 2.0)
    braccio = min(h * PROP_ARM, x1 - x0 - r)
    k = r * _KAPPA

    campo = (
        "M%.2f %.2f" % (x0 + r, y0)
        + "L%.2f %.2f" % (x1 - r, y0)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x1 - r + k, y0, x1, y0 + r - k,
                                              x1, y0 + r)
        + "L%.2f %.2f" % (x1, y1 - r)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x1, y1 - r + k, x1 - r + k, y1,
                                              x1 - r, y1)
        + "L%.2f %.2f" % (x0 + r, y1)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x0 + r - k, y1, x0, y1 - r + k,
                                              x0, y1 - r)
        + "L%.2f %.2f" % (x0, y0 + r)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x0, y0 + r - k, x0 + r - k, y0,
                                              x0 + r, y0)
        + "Z")
    parentesi = (
        "M%.2f %.2f" % (x0 + braccio, y1)
        + "L%.2f %.2f" % (x0 + r, y1)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x0 + r - k, y1, x0, y1 - r + k,
                                              x0, y1 - r)
        + "L%.2f %.2f" % (x0, y0 + r)
        + "C%.2f %.2f %.2f %.2f %.2f %.2f" % (x0, y0 + r - k, x0 + r - k, y0,
                                              x0 + r, y0)
        + "L%.2f %.2f" % (x0 + braccio, y0))
    return PropertyDrawing(
        field_d=campo, bracket_d=parentesi, fill=PROP_PAPER, stroke=PROP_INK,
        stroke_width=sw, text_x=x0 + braccio + PROP_PAD / 2.0,
        text_right=x1 - PROP_PAD / 2.0)
