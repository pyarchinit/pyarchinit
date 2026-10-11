"""L'anteprima della matrice disegnata: il PNG con la matrice e la pianta.

Questo è l'unico pezzo dell'anteprima che tocca QGIS. Quello che decide
— il filtro, l'espressione con cui si ritrovano le geometrie, la misura
dell'immagine, il posto dei due pezzi — sta in ``matrix_preview``, è
puro e si prova headless.

Due render e un incollaggio:

1. la **matrice** dal modello dell'em.json, già ridotto alle unità
   filtrate, disegnata nella stessa scena Qt del pannello
   (``em_matrix_view.build_scene``) — non si passa dalla vista, che è un
   widget: qui non serve una finestra, serve un'immagine;
2. la **pianta** dei layer dei disegni, filtrati con la stessa identità
   a quattro colonne;
3. un PNG solo, la matrice sopra e la pianta sotto, dentro
   ``pyarchinit_Matrix_folder``.

Non si passa da ``QgsPrintLayout``: una composizione di stampa è una
pagina fissa, e l'immagine deve adattarsi al contenuto.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from .matrix_preview import (GUTTER, PLAN_TABLES, Identity, PlanSource,
                             choose_site, compose, filter_model,
                             identities_from_records, keys_of, layer_filter,
                             plan_size, plan_source)

#: Il colore di fondo, lo stesso della scena della matrice: le due metà
#: dell'immagine devono sembrare una cosa sola.
SFONDO = "#FBFCFE"

#: La riga di stacco fra la matrice e la pianta.
STACCO = "#C8CDD4"

#: Il geometrico di ogni tabella dei disegni.
GEOMETRIA = "the_geom"

#: Lo stile delle quote: un cerchietto arancione con il valore accanto.
#: Non si inventa niente — è quello che il plugin applica ai layer delle
#: quote da sempre (``modules/gis/styles/stile_quote.qml``, un QML di
#: QGIS 2 che dichiara ``<labelfield>quota_q</labelfield>``). Il QML
#: porta il simbolo; l'etichetta va riaccesa con l'API di QGIS 3, che
#: quel formato non conosce — un punto senza la sua quota su una pianta
#: non dice niente.
STILE_QUOTE = ("styles", "stile_quote.qml")
CAMPO_QUOTA = "quota_q"

#: Lo stile delle unità disegnate: il QML che il plugin si porta dietro
#: con il nome della tabella. Solo il contorno, nessun riempimento — è
#: quello che serve a una pianta, dove le unità si sovrappongono. Senza
#: uno stile QGIS sceglie **un colore a caso a ogni caricamento**, e
#: un'immagine da mettere in una relazione non può cambiare colore ogni
#: volta che si preme il bottone.
STILE_US = ("styles", "stile_pyunitastratigrafiche.qml")


@dataclass
class Preview:
    """Quello che l'anteprima ha prodotto, e quello che va detto."""
    path: Optional[str] = None
    matrix_size: Optional[Tuple[int, int]] = None
    plan_size: Optional[Tuple[int, int]] = None
    units: int = 0
    dimmed: int = 0
    warnings: Optional[List[str]] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


# ------------------------------------------------------------- la matrice

def matrix_image(lay, scala: float = 2.0):
    """Il disegno della matrice come ``QImage``, o ``None``.

    Si costruisce la scena e si disegna lì: ``MatrixView`` è un widget, e
    per salvare un'immagine una finestra non serve. Il tetto dei pixel è
    quello della vista — una tela grande con la scala a 2 chiedeva 0,3 GB
    sul caso Ventena.
    """
    from qgis.PyQt.QtGui import QColor, QImage, QPainter
    from qgis.PyQt.QtWidgets import QGraphicsScene

    from .em_matrix_view import MAX_PIXELS, build_scene

    if lay is None or lay.width <= 0 or lay.height <= 0:
        return None
    scena = QGraphicsScene()
    build_scene(lay, scena)
    rettangolo = scena.sceneRect()
    pixel = rettangolo.width() * rettangolo.height()
    if pixel > 0:
        scala = min(float(scala), (MAX_PIXELS / pixel) ** 0.5)
    immagine = QImage(max(int(rettangolo.width() * scala), 1),
                      max(int(rettangolo.height() * scala), 1),
                      QImage.Format.Format_ARGB32)
    if immagine.isNull():
        return None
    immagine.fill(QColor(SFONDO))
    pittore = QPainter(immagine)
    pittore.setRenderHint(QPainter.RenderHint.Antialiasing)
    scena.render(pittore)
    pittore.end()
    return immagine


# -------------------------------------------------------------- la pianta

def _uri(source: PlanSource, tabella: str, filtro: str):
    """L'indirizzo del layer, o ``None`` se la fonte non si sa leggere."""
    from qgis.core import QgsDataSourceUri

    if source.provider == "ogr":
        return "%s|layername=%s" % (source.path, tabella)
    if source.provider == "postgres":
        uri = QgsDataSourceUri()
        uri.setConnection(source.host, source.port, source.database,
                          source.user, source.password)
        uri.setDataSource("public", tabella, GEOMETRIA, filtro or "", "gid")
        return uri.uri()
    return None


def _qml(nome) -> str:
    """Il percorso di un QML di ``modules/gis``."""
    return os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "gis", *nome)


def _carica_stile(layer, nome) -> None:
    """Lo stile del plugin sul layer; se non si carica, pazienza."""
    percorso = _qml(nome)
    if not os.path.exists(percorso):
        return
    try:
        layer.loadNamedStyle(percorso)
    except Exception:                               # noqa: BLE001
        pass


def _stile_quote(layer) -> None:
    """Il cerchietto e l'etichetta delle quote, come li fa il plugin."""
    from qgis.core import (QgsPalLayerSettings, QgsTextFormat,
                           QgsVectorLayerSimpleLabeling)

    _carica_stile(layer, STILE_QUOTE)
    if CAMPO_QUOTA not in layer.fields().names():
        return
    impostazioni = QgsPalLayerSettings()
    impostazioni.fieldName = CAMPO_QUOTA
    formato = QgsTextFormat()
    formato.setSize(7)
    impostazioni.setFormat(formato)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(impostazioni))
    layer.setLabelsEnabled(True)


def plan_layers(source: Optional[PlanSource],
                identities: Sequence[Identity],
                tables: Sequence[str] = PLAN_TABLES) -> List:
    """I layer dei disegni, filtrati sulle unità scelte.

    Si tengono solo i layer validi che hanno almeno una geometria: un
    layer vuoto nella pianta non si vede e allarga l'inquadratura per
    niente. Una tabella che non c'è — ``pyarchinit_quote_usm`` è vuota in
    ogni database visto finora — non ferma la pianta.
    """
    from qgis.core import QgsVectorLayer

    if source is None or not identities:
        return []
    layer_buoni = []
    for tabella in tables:
        try:
            layer = QgsVectorLayer(_uri(source, tabella, "") or "",
                                   tabella, source.provider)
        except Exception:                           # noqa: BLE001
            continue
        if not layer.isValid():
            continue
        filtro = layer_filter(identities, layer.fields().names())
        if not filtro:
            continue
        try:
            if not layer.setSubsetString(filtro):
                continue
        except Exception:                           # noqa: BLE001
            continue
        if layer.featureCount() == 0 or layer.extent().isEmpty():
            continue
        if CAMPO_QUOTA in layer.fields().names():
            _stile_quote(layer)
        else:
            _carica_stile(layer, STILE_US)
        layer_buoni.append(layer)
    return layer_buoni


def plan_extent(layers) -> Optional[Tuple[float, float, float, float]]:
    """Il rettangolo che contiene tutte le geometrie filtrate, o ``None``.

    ``None`` quando le unità scelte non sono disegnate: allora
    l'anteprima è la sola matrice, non una metà bianca.
    """
    from .em_matrix_links import merge_boxes, padded_box

    riquadri = []
    for layer in layers or ():
        e = layer.extent()
        if e.isEmpty():
            continue
        riquadri.append((e.xMinimum(), e.yMinimum(),
                         e.xMaximum(), e.yMaximum()))
    return padded_box(merge_boxes(riquadri))


def plan_image(layers, size, extent):
    """La pianta come ``QImage``, o ``None``.

    Il sistema di riferimento è quello dei layer — lo portano loro, come
    in ``pyarchinit_pyqgis``, dove viene dal SRID di
    ``geometry_columns``: il render lo prende dal primo layer e non
    riproietta niente.
    """
    from qgis.core import (QgsMapRendererParallelJob, QgsMapSettings,
                           QgsRectangle)
    from qgis.PyQt.QtCore import QSize
    from qgis.PyQt.QtGui import QColor

    if not layers or not size or not extent:
        return None
    larghezza, altezza = int(size[0]), int(size[1])
    if larghezza <= 0 or altezza <= 0:
        return None
    impostazioni = QgsMapSettings()
    # L'ordine di disegno di QGIS è dall'ultimo al primo: le quote, che
    # sono punti, devono stare sopra le unità o scompaiono sotto i
    # poligoni.
    impostazioni.setLayers(list(reversed(layers)))
    impostazioni.setBackgroundColor(QColor(SFONDO))
    impostazioni.setOutputSize(QSize(larghezza, altezza))
    # Il riferimento lo portano i layer: si prende il primo che ne ha uno
    # valido, perché un layer senza SRID dichiarato non deve decidere il
    # riferimento di tutta la pianta.
    for layer in layers:
        if layer.crs().isValid():
            impostazioni.setDestinationCrs(layer.crs())
            break
    impostazioni.setExtent(QgsRectangle(*(float(v) for v in extent)))
    lavoro = QgsMapRendererParallelJob(impostazioni)
    lavoro.start()
    lavoro.waitForFinished()
    immagine = lavoro.renderedImage()
    if immagine is None or immagine.isNull():
        return None
    return immagine


# ---------------------------------------------------------- l'incollaggio

def paste(matrice, pianta, destinazione, gutter: int = GUTTER):
    """Le due immagini in un PNG solo. ``(percorso, composizione)``.

    ``(None, None)`` se non c'è niente da incollare.
    """
    from qgis.PyQt.QtGui import QColor, QImage, QPainter

    misura = compose(
        (matrice.width(), matrice.height()) if matrice is not None else None,
        (pianta.width(), pianta.height()) if pianta is not None else None,
        gutter=gutter)
    if misura is None:
        return None, None
    foglio = QImage(misura.width, misura.height, QImage.Format.Format_ARGB32)
    if foglio.isNull():
        return None, None
    foglio.fill(QColor(SFONDO))
    pittore = QPainter(foglio)
    if matrice is not None and misura.matrix_at:
        pittore.drawImage(misura.matrix_at[0], misura.matrix_at[1], matrice)
    if misura.divider_y is not None:
        pittore.setPen(QColor(STACCO))
        pittore.drawLine(0, misura.divider_y,
                         misura.width, misura.divider_y)
    if pianta is not None and misura.plan_at:
        pittore.drawImage(misura.plan_at[0], misura.plan_at[1], pianta)
    pittore.end()
    cartella = os.path.dirname(str(destinazione))
    if cartella:
        os.makedirs(cartella, exist_ok=True)
    if not foglio.save(str(destinazione)):
        return None, None
    return str(destinazione), misura


# ------------------------------------------------------------ tutto insieme

def build_preview(conn_str, site, records, out_dir,
                  filename: str = "Harris_matrix_preview.png") -> Preview:
    """L'anteprima della matrice del sito, filtrata come la scheda.

    ``records`` è ``DATA_LIST``: la query che l'archeologo ha davanti.
    Senza righe non si disegna niente — un'anteprima di nulla non serve.

    L'em.json passa da una cartella temporanea: nella cartella della
    matrice ci va l'immagine, che è quello che l'utente ha chiesto, non
    un file di lavoro che non ha ordinato.

    Solleva ``em_export.EmExportError`` con una frase per l'utente
    quando il grafo del sito non si può costruire.
    """
    # Il modulo del plugin, non la libreria: si importa il pacchetto e poi
    # il nome, come fa ``pyarchinitPlugin`` — la forma col punto
    # (``..s3dgraphy.em_export``) è quella che la rinomina A5 aveva
    # lasciato rotta altrove, e un test la vieta.
    from ..s3dgraphy import em_export
    from .em_matrix_layout import layout
    from .em_matrix_model import read_em_json

    identita = identities_from_records(records)
    if not identita:
        return Preview(warnings=["Nessuna unità da disegnare: fai prima "
                                 "una ricerca nella scheda."])
    # Una ricerca può toccare più siti; il grafo si costruisce per un sito
    # alla volta. Si disegna quello e si dice quali sono rimasti fuori,
    # invece di mescolare stratigrafie che non si parlano.
    site, altri = choose_site(identita, site)
    identita = tuple(v for v in identita if v.sito == site)
    temporanea = tempfile.mkdtemp(prefix="pyarchinit_anteprima_")
    try:
        percorso, _n, _e, avvisi = em_export.export_site(
            conn_str, site, temporanea)
        modello = filter_model(read_em_json(percorso), keys_of(identita))
    finally:
        import shutil
        shutil.rmtree(temporanea, ignore_errors=True)

    impaginato = layout(modello)
    matrice = matrix_image(impaginato)
    layers = plan_layers(plan_source(conn_str), identita)
    estensione = plan_extent(layers)
    misura_pianta = plan_size(
        matrice.width() if matrice is not None else 0, estensione)
    pianta = plan_image(layers, misura_pianta, estensione)
    destinazione = os.path.join(str(out_dir), filename)
    salvato, composizione = paste(matrice, pianta, destinazione)
    messaggi = list(avvisi) + list(modello.warnings)
    if altri:
        messaggi.append("La ricerca tocca anche %s: disegno la matrice di "
                        "«%s»." % (", ".join("«%s»" % s for s in altri), site))
    if pianta is None:
        # Uno scavo senza disegno: l'immagine esce con la sola matrice,
        # invece di una metà bianca o di un errore.
        messaggi.append("Le unità filtrate non hanno geometrie: "
                        "l'immagine contiene la sola matrice.")
    return Preview(
        path=salvato,
        matrix_size=((matrice.width(), matrice.height())
                     if matrice is not None else None),
        plan_size=((pianta.width(), pianta.height())
                   if pianta is not None else None),
        units=len(modello.units),
        dimmed=len([u for u in modello.units if u.dimmed]),
        warnings=messaggi)
