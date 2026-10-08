"""La matrice disegnata in SVG, senza dipendenze.

Serve due volte: all'utente, che salva e stampa, e ai test, che un
disegno lo possono provare solo se è testo. La vista Qt disegna le stesse
forme a partire dallo stesso impaginato, così quello che si vede a schermo
e quello che esce dal file non divergono.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

from .em_matrix_layout import Band, Box, Edge, Layout

#: Oltre questa lunghezza l'etichetta si taglia: una casella è larga
#: quanto è larga, e un nome che sborda è peggio di un nome accorciato.
_MAX_LABEL = 16

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


def _short(testo: str, massimo: int = _MAX_LABEL) -> str:
    testo = str(testo)
    return testo if len(testo) <= massimo else testo[:massimo - 1] + "…"


def _dash(stile: str) -> str:
    if stile == "dashed":
        return ' stroke-dasharray="7 4"'
    if stile == "dotted":
        return ' stroke-dasharray="2 4"'
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


#: La punta della freccia. Senza, il verso del rapporto lo direbbe solo
#: la posizione verticale — che però la decide la fascia dell'epoca, non
#: la stratigrafia: dove le due si contraddicono non si capirebbe più
#: chi copre chi (review 2026-10-08).
_MARKERS = (
    '<defs>'
    '<marker id="freccia" viewBox="0 0 8 8" refX="7" refY="4" '
    'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    '<path d="M0,0 L8,4 L0,8 z" fill="#6B7684"/></marker>'
    '<marker id="freccia-continuita" viewBox="0 0 8 8" refX="7" refY="4" '
    'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    '<path d="M0,0 L8,4 L0,8 z" fill="#1A1A1A"/></marker>'
    '</defs>')


def _edge_svg(edge: Edge) -> str:
    """La linea di un rapporto.

    Quella di un nodo di continuità si disegna più marcata e scura: dice
    per quanto a lungo una unità sopravvive — dal suo periodo fino alla
    fascia dove sta il nodo — e non che una sta sopra l'altra.
    """
    if edge.continuity:
        return ('<polyline class="edge continuity" points="%s" fill="none" '
                'stroke="#1A1A1A" stroke-width="2.2" '
                'marker-end="url(#freccia-continuita)"/>'
                % _points(edge.points))
    if edge.symmetric:
        # «Uguale a» non ha un verso: nessuna punta.
        return ('<polyline class="edge" points="%s" fill="none" '
                'stroke="#6B7684" stroke-width="1.4" '
                'stroke-dasharray="6 4"/>' % _points(edge.points))
    return ('<polyline class="edge" points="%s" fill="none" stroke="#6B7684" '
            'stroke-width="1.4" marker-end="url(#freccia)"/>'
            % _points(edge.points))


def _box_svg(box: Box) -> str:
    colore = _readable_on(box.unit.style.fill)
    return ('<g class="unit" data-id="%s">%s'
            '<title>%s</title>'
            '<text x="%.1f" y="%.1f" font-size="12" text-anchor="middle" '
            'fill="%s">%s</text></g>'
            % (_esc(box.unit.node_id), _node_shape(box),
               _esc("%s — %s" % (box.unit.label, box.unit.description)
                    if box.unit.description else box.unit.label),
               box.x + box.w / 2, box.y + box.h / 2 + 4, colore,
               _esc(_short(box.unit.label))))


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
        '<rect width="100%%" height="100%%" fill="#FBFCFE"/>',
        _MARKERS,
    ]
    if titolo:
        pezzi.append('<text x="24" y="24" font-size="15" font-weight="700" '
                     'fill="#1A2B3C">%s</text>' % _esc(titolo))
        pezzi.append('<g transform="translate(0,%.1f)">' % alto)
    for band in lay.bands:
        pezzi.append(_band_svg(band, larghezza))
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
