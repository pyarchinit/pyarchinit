"""La matrice disegnata in SVG, senza dipendenze.

Serve due volte: all'utente, che salva e stampa, e ai test, che un
disegno lo possono provare solo se è testo. La vista Qt disegna le stesse
forme a partire dallo stesso impaginato, così quello che si vede a schermo
e quello che esce dal file non divergono.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

from .em_matrix_glyphs import (GLYPH_LABEL_GAP, PROP_PAPER, SHEET_LABEL_Y,
                               Glyph, GlyphLayer, contain, glyph_for,
                               is_property, property_drawing)
from .em_matrix_glyphs import short_label as _short
from .em_matrix_layout import Band, Box, Edge, Layout
from .em_matrix_model import CUT_COLOR, CUT_KIND, edge_style_for

_FONT = ("Helvetica Neue, Helvetica, Arial, sans-serif")


#: I caratteri che l'XML non ammette: un nome che ne contiene uno
#: produceva un SVG che nessun browser apre (review 2026-10-08).
_VIETATI = "".join(chr(c) for c in list(range(0, 9)) + [11, 12]
                   + list(range(14, 32)))
_RIPULISCI = {ord(c): None for c in _VIETATI}


def _esc(testo) -> str:
    return (str(testo).translate(_RIPULISCI)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _dash(stile: str) -> str:
    if stile == "dashed":
        return ' stroke-dasharray="7 4"'
    if stile == "dotted":
        return ' stroke-dasharray="2 4"'
    if stile == "dashed-dotted":
        return ' stroke-dasharray="7 3 2 3"'
    return ""


def _points(punti: Sequence[Tuple[float, float]]) -> str:
    return " ".join("%.1f,%.1f" % (x, y) for x, y in punti)


def _polygon(shape: str, x: float, y: float, w: float, h: float):
    """I vertici della forma, o None se si disegna in un altro modo."""
    taglio = min(w, h) * 0.28
    if shape == "parallelogram":
        return [(x + taglio, y), (x + w, y), (x + w - taglio, y + h), (x, y + h)]
    if shape == "hexagon":
        return [(x + taglio, y), (x + w - taglio, y), (x + w, y + h / 2),
                (x + w - taglio, y + h), (x + taglio, y + h), (x, y + h / 2)]
    if shape == "octagon":
        return [(x + taglio, y), (x + w - taglio, y), (x + w, y + taglio),
                (x + w, y + h - taglio), (x + w - taglio, y + h),
                (x + taglio, y + h), (x, y + h - taglio), (x, y + taglio)]
    if shape == "diamond":
        return [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h),
                (x, y + h / 2)]
    if shape == "pentagon":
        return [(x + w / 2, y), (x + w, y + h * 0.38),
                (x + w * 0.81, y + h), (x + w * 0.19, y + h),
                (x, y + h * 0.38)]
    if shape == "triangle":
        return [(x + w / 2, y), (x + w, y + h), (x, y + h)]
    return None


def _node_shape(box: Box) -> str:
    stile = box.unit.style
    shape = stile.shape
    attrs = ('fill="%s" stroke="%s" stroke-width="%.1f"%s'
             % (_esc(stile.fill), _esc(stile.stroke),
                min(stile.width, 3.0), _dash(stile.dash)))
    punti = _polygon(shape, box.x, box.y, box.w, box.h)
    if punti:
        return '<polygon points="%s" %s/>' % (_points(punti), attrs)
    if shape in ("ellipse", "circle"):
        return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" %s/>'
                % (box.x + box.w / 2, box.y + box.h / 2,
                   box.w / 2, box.h / 2, attrs))
    raggio = 9 if "round" in shape else 2
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
            'rx="%d" %s/>' % (box.x, box.y, box.w, box.h, raggio, attrs))


def _layer_svg(livello: GlyphLayer) -> str:
    """Un livello del pittogramma: un tracciato, un colore, e basta.

    Il ``d`` si scrive com'è: il file lo distribuisce già normalizzato,
    e riscriverlo sarebbe l'occasione di sbagliarlo.
    """
    attributi = []
    if livello.fill:
        attributi.append('fill="%s"' % _esc(livello.fill))
        if livello.fill_rule == "evenodd":
            attributi.append('fill-rule="evenodd"')
    else:
        attributi.append('fill="none"')
    if livello.stroke:
        attributi.append('stroke="%s" stroke-width="%.3f"'
                         % (_esc(livello.stroke), livello.stroke_width))
        if livello.line_cap != "butt":
            attributi.append('stroke-linecap="%s"' % _esc(livello.line_cap))
        if livello.line_join != "miter":
            attributi.append('stroke-linejoin="%s"' % _esc(livello.line_join))
    if livello.opacity < 1.0:
        attributi.append('opacity="%.3f"' % livello.opacity)
    return '<path d="%s" %s/>' % (livello.d, " ".join(attributi))


def _glyph_svg(glifo: Glyph, box: Box) -> str:
    """Il pittogramma dentro la casella: ``contain``, centrato.

    Una sola trasformazione per tutto il disegno, così gli spessori dei
    tratti si scalano insieme al resto — nel ``viewBox`` sono misurati,
    non in pixel.
    """
    scala, dx, dy = contain(glifo, box.x, box.y, box.w, box.h)
    pezzi = ['<g class="glifo" transform="translate(%.2f,%.2f) scale(%.4f)">'
             % (dx, dy, scala)]
    pezzi.extend(_layer_svg(l) for l in glifo.layers)
    pezzi.append('</g>')
    return "".join(pezzi)


def _property_svg(box: Box) -> str:
    """La proprietà: il campo grigio e la parentesi aperta a sinistra."""
    disegno = property_drawing(box.x, box.y, box.w, box.h)
    return ('<g class="parentesi">'
            '<path d="%s" fill="%s" stroke="none"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
            'stroke-linejoin="round" stroke-linecap="butt"/></g>'
            % (disegno.field_d, _esc(disegno.fill), disegno.bracket_d,
               _esc(disegno.stroke), disegno.stroke_width))


def _drawing_svg(box: Box) -> str:
    """Il disegno della casella: il pittogramma se il tipo ne ha uno."""
    glifo = glyph_for(box.unit.node_type)
    if glifo is not None:
        return _glyph_svg(glifo, box)
    if is_property(box.unit.node_type):
        return _property_svg(box)
    return _node_shape(box)


def _label_place(box: Box):
    """Dove va il nome dell'unità, e di che colore.

    Tre posti, e il file dice perché: sotto l'icona centrata, SOPRA il
    foglio del documento (al 62% della sua altezza, senza tagliarlo),
    dentro la parentesi della proprietà. Per tutto il resto il nome sta
    in mezzo alla casella, come è sempre stato.
    """
    glifo = glyph_for(box.unit.node_type)
    if glifo is not None and glifo.sheet:
        return (box.x + box.w / 2, box.y + box.h * SHEET_LABEL_Y + 4,
                "#1A1A1A")
    if glifo is not None:
        return (box.x + box.w / 2, box.y + box.h + GLYPH_LABEL_GAP, "#1A1A1A")
    if is_property(box.unit.node_type):
        disegno = property_drawing(box.x, box.y, box.w, box.h)
        return ((disegno.text_x + disegno.text_right) / 2,
                box.y + box.h / 2 + 4, _readable_on(PROP_PAPER))
    return (box.x + box.w / 2, box.y + box.h / 2 + 4,
            _readable_on(box.unit.style.fill))


def _readable_on(fill: str) -> str:
    """Nero o bianco, secondo quanto è scuro il riempimento."""
    colore = str(fill or "#FFFFFF").lstrip("#")
    if len(colore) != 6:
        return "#1A1A1A"
    try:
        r, g, b = (int(colore[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return "#1A1A1A"
    return "#1A1A1A" if (r * 299 + g * 587 + b * 114) / 1000 > 140 else "#FFFFFF"


def _band_svg(band: Band, larghezza: float, config_margin: float = 24.0) -> str:
    pezzi = ['<g class="band">']
    pezzi.append('<rect x="0" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s" fill-opacity="0.45"/>'
                 % (band.y, larghezza, band.h, _esc(band.color)))
    pezzi.append('<line x1="0" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="#C8CDD4" stroke-width="1"/>'
                 % (band.y, larghezza, band.y))
    pezzi.append('<text x="%.1f" y="%.1f" font-size="13" font-weight="600" '
                 'fill="#2C4A6E">%s</text>'
                 % (config_margin, band.y + 20, _esc(_short(band.label, 26))))
    pezzi.append('<text x="%.1f" y="%.1f" font-size="11" fill="#5A6B80">%s</text>'
                 % (config_margin, band.y + 36, _esc(band.sublabel)))
    pezzi.append('</g>')
    return "".join(pezzi)


#: Il rosso di una freccia che risale le fasce. Non è decorazione: dice
#: che la stratigrafia e la cronologia si contraddicono — chi copre sta
#: in un'epoca più antica di chi è coperto — ed è l'errore che
#: l'archeologo deve vedere senza cercarlo. Convenzione dell'Extended
#: Matrix (E. Demetrescu, 2026-10-09).
ROSSO_SALITA = "#C0392B"


#: Quanto è lunga la punta della freccia, e quanto larga a metà.
_PUNTA_L, _PUNTA_W = 9.0, 3.5


def arrow_points(da, a):
    """I tre vertici della punta in fondo al segmento ``da``→``a``.

    Un poligono esplicito e non un ``<marker>``: QGIS disegna gli SVG con
    QSvgRenderer, che è SVG Tiny 1.2 e i marker non li conosce — nella
    tavola dell'atlante le punte sparivano e la matrice perdeva il verso
    (visto il 2026-10-09). Un triangolo lo capiscono tutti.
    """
    import math

    dx, dy = a[0] - da[0], a[1] - da[1]
    lunghezza = math.hypot(dx, dy)
    if lunghezza < 1.0:
        return None
    ux, uy = dx / lunghezza, dy / lunghezza
    bx, by = a[0] - ux * _PUNTA_L, a[1] - uy * _PUNTA_L
    lx, ly = -uy * _PUNTA_W, ux * _PUNTA_W
    return [(a[0], a[1]), (bx + lx, by + ly), (bx - lx, by - ly)]


def _punta_svg(edge: Edge, colore: str) -> str:
    """Il triangolo in fondo alla linea, o niente se non si può orientare."""
    punti = arrow_points(edge.points[-2], edge.points[-1])
    if not punti:
        return ""
    return ('<polygon class="punta" points="%s" fill="%s"/>'
            % (_points(punti), colore))


def _edge_svg(edge: Edge) -> str:
    """La linea di un rapporto, con la sua punta.

    Quella di un nodo di continuità si disegna più marcata e scura: dice
    per quanto a lungo una unità sopravvive — dal suo periodo fino alla
    fascia dove sta il nodo — e non che una sta sopra l'altra.
    """
    if edge.symmetric:
        # «Uguale a» non ha un verso e non è una sovrapposizione: due
        # linee orizzontali staccate, come il segno di uguale, e nessuna
        # punta.
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = edge.points[:4]
        return ('<g class="edge equality">'
                '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                'stroke="#6B7684" stroke-width="1.4"/>'
                '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                'stroke="#6B7684" stroke-width="1.4"/></g>'
                % (x1, y1, x2, y2, x3, y3, x4, y4))
    # La linea dice che rapporto è (Enzo, 12 ottobre 2026). La sequenza
    # — copre, riempie, si appoggia — resta grigia e piena: è la matrice.
    # Il taglio è punteggiato verde. I paradati prendono lo stile che la
    # libreria dichiara in `em_visual_rules.json` (colore, tratto,
    # spessore), con una deroga sola: mai pieni, perché un arco verso un
    # documento o un estrattore non deve sembrare una sovrapposizione —
    # `combines` nel file è «solid», qui esce tratteggiato. La continuità
    # resta spessa e nera.
    taglio = edge.kind == CUT_KIND
    tratto = ""
    if taglio:
        colore, spessore, tratto = CUT_COLOR, 1.6, _dash("dotted")
        aggiunta = " cut"
    elif edge.paradata:
        regola = edge_style_for(edge.kind)
        colore = regola.color if regola else "#6B7684"
        spessore = min(regola.width, 2.0) if regola else 1.2
        linea = regola.line if regola else "dashed"
        tratto = _dash(linea if linea != "solid" else "dashed")
        aggiunta = " paradata"
    elif edge.continuity:
        colore, spessore, aggiunta = "#1A1A1A", 2.2, " continuity"
    else:
        colore, spessore, aggiunta = "#6B7684", 1.4, ""
    if edge.upward:
        # Il rosso vince sul colore, non sulla linea: un taglio che
        # risale è una contraddizione **e** un taglio. Lo spessore tiene
        # la continuità distinta dagli altri rapporti.
        colore = ROSSO_SALITA
        spessore = 2.2 if edge.continuity else max(spessore, 1.6)
        classe = "edge salita" + ("" if edge.continuity else aggiunta)
    else:
        classe = "edge" + aggiunta
    return ('<g class="%s"><polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>%s</g>'
            % (classe, _points(edge.points), colore, spessore, tratto,
               _punta_svg(edge, colore)))


#: Quanto resta visibile una unità che non è fra quelle guardate.
OPACITA_FUORI = 0.4


def _box_svg(box: Box) -> str:
    x, y, colore = _label_place(box)
    # Fuori vista: nel disegno c'è perché un rapporto la cita, ma non è
    # sulla mappa, e si deve capire a colpo d'occhio.
    fuori = bool(getattr(box.unit, "dimmed", False))
    descrizione = (box.unit.description if box.unit.description else "")
    if fuori:
        descrizione = ((descrizione + " — ") if descrizione else "") \
            + "non visibile sulla mappa"
    titolo = _esc("%s — %s" % (box.unit.label, descrizione)
                  if descrizione else box.unit.label)
    if box.unit.node_type == "BR":
        # Il rombo della continuità non porta il nome sopra: è piccolo e
        # nero, com'è nell'Extended Matrix, e la sua unità sta dritta
        # sotto di lui. Il nome resta nel `<title>` per chi ci passa col
        # mouse.
        return ('<g class="unit%s" data-id="%s"%s>%s<title>%s</title></g>'
                % (" fuori" if fuori else "", _esc(box.unit.node_id),
                   ' opacity="%.2f"' % OPACITA_FUORI if fuori else "",
                   _drawing_svg(box), titolo))
    return ('<g class="unit%s" data-id="%s"%s>%s'
            '<title>%s</title>'
            '<text x="%.1f" y="%.1f" font-size="12" text-anchor="middle" '
            'fill="%s">%s</text></g>'
            % (" fuori" if fuori else "", _esc(box.unit.node_id),
               ' opacity="%.2f"' % OPACITA_FUORI if fuori else "",
               _drawing_svg(box), titolo,
               x, y, colore, _esc(_short(box.unit.label))))


def to_svg(lay: Layout, title: str = "") -> str:
    """Il disegno completo, pronto da salvare o da mettere in una pagina."""
    titolo = title or lay.title
    alto = 34.0 if titolo else 0.0
    larghezza = max(lay.width, 420.0)
    altezza = max(lay.height, 220.0) + alto
    pezzi: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
        'viewBox="0 0 %.0f %.0f" font-family="%s">'
        % (larghezza, altezza, larghezza, altezza, _FONT),
        # `100%`, non `100%%`: questa stringa non è un modello di
        # formato — nessun `%` la interpola — e il doppio per cento
        # finiva letterale nel file. `width="100%%"` non è una lunghezza
        # SVG valida, così lo sfondo non si dipingeva e la matrice
        # usciva trasparente (misurato: pixel (0,0,0,0) invece di
        # #FBFCFE).
        '<rect width="100%" height="100%" fill="#FBFCFE"/>',
    ]
    if titolo:
        pezzi.append('<text x="24" y="24" font-size="15" font-weight="700" '
                     'fill="#1A2B3C">%s</text>' % _esc(titolo))
        pezzi.append('<g transform="translate(0,%.1f)">' % alto)
    for band in lay.bands:
        pezzi.append(_band_svg(band, larghezza))
    # Il gruppo dei paradati di un'unità: la cornice tratteggiata di EMStudio.
    for gruppo in getattr(lay, "groups", None) or ():
        pezzi.append('<rect class="paradata-group" x="%.1f" y="%.1f" width="%.1f" '
                     'height="%.1f" rx="4" fill="none" stroke="#9AA4B2" '
                     'stroke-width="1" stroke-dasharray="4 3"/>'
                     % (gruppo.x, gruppo.y, gruppo.w, gruppo.h))
    for edge in lay.edges:
        pezzi.append(_edge_svg(edge))
    for box in lay.boxes:
        pezzi.append(_box_svg(box))
    if titolo:
        pezzi.append('</g>')
    pezzi.append('</svg>')
    return "\n".join(pezzi)


def write_svg(lay: Layout, path, title: str = "") -> str:
    percorso = Path(path)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(to_svg(lay, title), encoding="utf-8")
    return str(percorso)
