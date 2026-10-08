"""La matrice dell'Extended Matrix dentro QGIS.

Un pannello agganciato alla finestra di QGIS che disegna l'em.json: le
fasce delle epoche, le unità con la simbologia dell'Extended Matrix e i
rapporti stratigrafici. Non serve EMStudio, non serve il nodo, non serve
un motore web — richiesta di Enzo del 2026-10-08, dopo aver constatato
che la pagina per-stanza del nodo chiede di accedere.

Dal 5.13.42 la scheda dell'unità scelta mostra anche i suoi media e
permette di andare a vedere la geometria sulla mappa. Quei due legami non
stanno nell'em.json: vengono dal database del progetto e dai layer
caricati, cioè da questo lato del ponte (``modules/utility/em_matrix_links``
e ``em_matrix_map``). Nell'em.json non entra niente di nuovo.

Un pannello per sessione (stesso ``objectName``, si riusa e si porta
davanti) e ``close_panel`` in ``unload()``: la lezione della 5.13.29, dove
un dock sopravvissuto al plugin lasciava voci doppie al ricaricamento.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

PANEL_OBJECT_NAME = "pyarchinitEmMatrixPanel"

#: Quanto è alta la striscia delle anteprime, e quanto grandi le icone.
THUMB_SIZE = 96

#: Le unità del sito aperto adesso. Vivono qui e non dentro la chiusura
#: che mostra la scheda, perché quella si aggancia una volta sola, alla
#: creazione del dock: riusando il pannello su un secondo sito mostrerebbe
#: per sempre i dati del primo.
_CURRENT_UNITS = {}

#: La connessione del progetto da cui viene il sito aperto adesso, per gli
#: stessi motivi. ``None`` quando il pannello è stato aperto su un em.json
#: senza il database dietro: allora la scheda mostra i campi del file e
#: nient'altro, invece di cercare media in un database che non c'è.
_CURRENT_CONN: List[Optional[str]] = [None]


def remember_units(units) -> None:
    """Sostituisce le unità che la scheda può mostrare."""
    _CURRENT_UNITS.clear()
    _CURRENT_UNITS.update({u.node_id: u for u in units})


def remember_connection(conn_str) -> None:
    """Sostituisce la connessione da cui si leggono media e geometrie."""
    _CURRENT_CONN[0] = conn_str or None


def details_for(node_id: str) -> str:
    """La scheda dell'unità scelta, o l'invito a sceglierne una."""
    unit = _CURRENT_UNITS.get(node_id)
    if unit is None:
        return "<i>Scegli un'unità per vederne la scheda.</i>"
    return _details_text(unit)


def media_for(node_id: str):
    """I media attaccati all'unità scelta, o un elenco vuoto."""
    unit = _CURRENT_UNITS.get(node_id)
    if unit is None or not _CURRENT_CONN[0]:
        return []
    from ..utility.em_matrix_links import media_for_unit
    return media_for_unit(_CURRENT_CONN[0], unit)


def can_zoom(node_id: str) -> bool:
    """Vero se l'unità scelta è una riga della scheda US.

    Un nodo di continuità o un documento non ha una geometria: offrire lo
    zoom su di lui sarebbe un bottone che non può funzionare.
    """
    unit = _CURRENT_UNITS.get(node_id)
    if unit is None:
        return False
    from ..utility.em_matrix_links import unit_identity
    return bool(unit_identity(unit))


def zoom_to(iface, node_id: str):
    """Inquadra sulla mappa la geometria dell'unità scelta."""
    unit = _CURRENT_UNITS.get(node_id)
    if unit is None:
        return False, "Scegli prima un'unità nella matrice."
    from ..utility.em_matrix_map import zoom_to_unit
    return zoom_to_unit(iface, unit, connection=_CURRENT_CONN[0])


def thumb_base() -> str:
    """La cartella (o l'indirizzo) delle anteprime, o una stringa vuota."""
    try:
        from modules.db.pyarchinit_conn_strings import Connection
        return str(Connection().thumb_path().get("thumb_path") or "")
    except Exception:                               # noqa: BLE001
        return ""


def thumbs_are_remote() -> bool:
    """Vero se le anteprime stanno su un archivio remoto.

    Allora ogni miniatura è una richiesta in rete: si caricano quando
    l'utente le chiede, non appena clicca un nodo.
    """
    base = thumb_base()
    if not base:
        return False
    try:
        from ..utility.remote_image_loader import is_remote_url
        return bool(is_remote_url(base))
    except Exception:                               # noqa: BLE001
        return False


def describe_failure(em_json_path) -> Optional[str]:
    """La frase da mostrare se il file non si può disegnare, o None.

    Si legge PRIMA di aprire il pannello: meglio una frase in un avviso
    che una finestra vuota senza spiegazione.
    """
    percorso = Path(em_json_path)
    if not percorso.exists():
        return "Il file «%s» non c'è." % percorso.name
    try:
        from ..utility.em_matrix_model import read_em_json
        read_em_json(percorso)
    except ValueError as e:
        return str(e)
    except Exception as e:                          # noqa: BLE001
        return "«%s» non si legge come em.json: %s" % (percorso.name, e)
    return None


def summary_line(em_json_path) -> str:
    """«51 unità · 12 epoche · 93 rapporti», per la barra del pannello."""
    from ..utility.em_matrix_model import read_em_json

    model = read_em_json(Path(em_json_path))
    return "%d unità · %d epoche · %d rapporti" % (
        len(model.units), len(model.epochs), len(model.relations))


def _existing(iface):
    try:
        from qgis.PyQt.QtWidgets import QDockWidget
        return iface.mainWindow().findChild(QDockWidget, PANEL_OBJECT_NAME)
    except Exception:                               # noqa: BLE001
        return None


def _details_text(unit) -> str:
    """I campi della scheda che servono a riconoscere l'unità."""
    dati = unit.data or {}
    righe = [("Unità", unit.label), ("Tipo", unit.node_type)]
    for chiave, etichetta in (("d_stratigrafica", "Definizione"),
                              ("d_interpretativa", "Interpretazione"),
                              ("periodo_iniziale", "Periodo iniziale"),
                              ("fase_iniziale", "Fase iniziale"),
                              ("periodo_finale", "Periodo finale"),
                              ("fase_finale", "Fase finale"),
                              ("datazione_estesa", "Datazione"),
                              ("area", "Area"), ("struttura", "Struttura")):
        if dati.get(chiave):
            righe.append((etichetta, str(dati[chiave])))
    corpo = "".join(
        "<tr><td style='color:#5A6B80;padding-right:10px'>%s</td>"
        "<td>%s</td></tr>" % (e, v) for e, v in righe)
    return "<table>%s</table>" % corpo


def _fill_media(lista, etichetta, node_id, con_anteprime: bool) -> int:
    """Riempie la striscia dei media. Restituisce quanti ne ha trovati."""
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtWidgets import QListWidgetItem

    lista.clear()
    media = media_for(node_id)
    if not media:
        lista.setVisible(False)
        etichetta.setVisible(False)
        return 0
    base = thumb_base()
    for m in media:
        voce = QListWidgetItem(m.name)
        voce.setToolTip(m.name)
        voce.setData(Qt.ItemDataRole.UserRole, m.thumb_file)
        if con_anteprime and m.thumb_file and base:
            try:
                from ..utility.remote_image_loader import (get_image_path,
                                                           load_icon)
                voce.setIcon(load_icon(get_image_path(base, m.thumb_file)))
            except Exception:                       # noqa: BLE001
                pass
        lista.addItem(voce)
    lista.setVisible(True)
    etichetta.setVisible(True)
    etichetta.setText("%d media" % len(media) if con_anteprime
                      else "%d media — le anteprime sono su un archivio "
                           "remoto" % len(media))
    return len(media)


def open_in_panel(iface, em_json_path, title: str = "", conn_str=None) -> bool:
    """Apre (o riusa) il pannello sulla matrice del file. False se non si può.

    ``conn_str`` è la connessione del progetto: serve per i media e per lo
    zoom sulla geometria. Senza, il pannello disegna la matrice e mostra
    la scheda che sta nel file, e nient'altro.
    """
    try:
        from qgis.PyQt.QtCore import QSize, Qt
        from qgis.PyQt.QtWidgets import (QDockWidget, QHBoxLayout, QLabel,
                                         QListWidget, QPushButton, QSplitter,
                                         QTextBrowser, QVBoxLayout, QWidget)

        from ..utility.em_matrix_layout import layout
        from ..utility.em_matrix_model import read_em_json
        from ..utility.em_matrix_view import MatrixView, is_heavy

        # Si legge UNA volta: describe_failure lo rileggeva daccapo, e su
        # un file grande la sola analisi costava più del disegno.
        model = read_em_json(Path(em_json_path))
        impaginato = layout(model)

        # Prima di disegnare: la scheda che si aprirà deve già guardare al
        # sito giusto, non a quello di un'apertura precedente.
        remember_units(model.units)
        remember_connection(conn_str)

        dock = _existing(iface)
        if dock is None:
            dock = QDockWidget(title or "Matrice Extended Matrix",
                               iface.mainWindow())
            dock.setObjectName(PANEL_OBJECT_NAME)
            contenitore = QWidget(dock)
            colonna = QVBoxLayout(contenitore)
            colonna.setContentsMargins(6, 6, 6, 6)

            barra = QHBoxLayout()
            conteggi = QLabel("")
            conteggi.setObjectName("conteggi")
            barra.addWidget(conteggi)
            barra.addStretch(1)
            vista = MatrixView(contenitore)
            vista.setObjectName("vista")
            for etichetta, azione in (
                    ("Adatta", lambda: vista.fit()),
                    ("＋", lambda: vista.zoom(1.25)),
                    ("－", lambda: vista.zoom(1 / 1.25)),
                    ("Salva SVG…", lambda: _save(iface, vista, "svg")),
                    ("Salva PNG…", lambda: _save(iface, vista, "png"))):
                bottone = QPushButton(etichetta)
                bottone.clicked.connect(azione)
                barra.addWidget(bottone)
            colonna.addLayout(barra)

            # La colonna di destra: la scheda, lo zoom sulla mappa, i media.
            destra = QWidget(contenitore)
            destra.setObjectName("destra")
            pila = QVBoxLayout(destra)
            pila.setContentsMargins(0, 0, 0, 0)

            scheda = QTextBrowser(destra)
            scheda.setObjectName("scheda")
            scheda.setHtml("<i>Scegli un'unità per vederne la scheda.</i>")
            # La scheda e la striscia dei media si dividono l'altezza: senza
            # i pesi la scheda si prendeva tutto e le anteprime restavano
            # schiacciate in fondo (visto nello screenshot del 2026-10-08).
            pila.addWidget(scheda, 3)

            zoom = QPushButton("Zoom sulla geometria", destra)
            zoom.setObjectName("zoom")
            zoom.setToolTip("Inquadra sulla mappa la geometria di questa "
                            "unità, se è disegnata in un layer caricato.")
            zoom.setEnabled(False)
            pila.addWidget(zoom)

            avviso_media = QLabel("", destra)
            avviso_media.setObjectName("avviso_media")
            avviso_media.setVisible(False)
            pila.addWidget(avviso_media)

            anteprime = QPushButton("Carica le anteprime", destra)
            anteprime.setObjectName("anteprime")
            anteprime.setVisible(False)
            pila.addWidget(anteprime)

            media = QListWidget(destra)
            media.setObjectName("media")
            media.setViewMode(QListWidget.ViewMode.IconMode)
            media.setIconSize(QSize(THUMB_SIZE, THUMB_SIZE))
            media.setResizeMode(QListWidget.ResizeMode.Adjust)
            media.setMovement(QListWidget.Movement.Static)
            media.setWordWrap(True)
            media.setMinimumHeight(THUMB_SIZE + 44)
            media.setVisible(False)
            pila.addWidget(media, 2)

            # Il suggerimento di dimensione di un QTextBrowser è generoso:
            # senza misure esplicite il divisore gli dava due terzi e la
            # matrice restava una colonnina (visto nello screenshot).
            destra.setMinimumWidth(240)
            destra.setMaximumWidth(380)

            divisore = QSplitter(Qt.Orientation.Horizontal, contenitore)
            divisore.addWidget(vista)
            divisore.addWidget(destra)
            divisore.setStretchFactor(0, 5)
            divisore.setStretchFactor(1, 0)
            divisore.setSizes([1000, 300])
            colonna.addWidget(divisore)

            dock.setWidget(contenitore)
            iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

            # Il nodo scelto vive in una lista e non in una variabile della
            # chiusura: i bottoni si agganciano una volta sola, qui, e
            # devono vedere l'ultima scelta anche molte aperture dopo.
            scelto = [""]

            def mostra(node_id):
                scelto[0] = str(node_id)
                scheda.setHtml(details_for(scelto[0]))
                zoom.setEnabled(can_zoom(scelto[0]))
                remoto = thumbs_are_remote()
                quanti = _fill_media(media, avviso_media, scelto[0],
                                     con_anteprime=not remoto)
                anteprime.setVisible(bool(quanti) and remoto)

            def carica_anteprime():
                _fill_media(media, avviso_media, scelto[0],
                            con_anteprime=True)
                anteprime.setVisible(False)

            def vai_sulla_mappa():
                fatto, messaggio = zoom_to(iface, scelto[0])
                try:
                    barra_messaggi = iface.messageBar()
                    if fatto:
                        barra_messaggi.pushInfo("Matrice", messaggio)
                    else:
                        barra_messaggi.pushWarning("Matrice", messaggio)
                except Exception:                   # noqa: BLE001
                    pass

            vista.selected.connect(mostra)
            zoom.clicked.connect(vai_sulla_mappa)
            anteprime.clicked.connect(carica_anteprime)
        else:
            dock.setWindowTitle(title or "Matrice Extended Matrix")
            contenuto = dock.widget()
            vista = contenuto.findChild(MatrixView, "vista")
            conteggi = contenuto.findChild(QLabel, "conteggi")
            scheda = contenuto.findChild(QTextBrowser, "scheda")
            if scheda is not None:
                scheda.setHtml("<i>Scegli un'unità per vederne la scheda.</i>")
            # Un sito nuovo: la scheda di prima non vale più.
            for nome, vuoto in (("zoom", False), ("anteprime", None)):
                bottone = contenuto.findChild(QPushButton, nome)
                if bottone is None:
                    continue
                if vuoto is None:
                    bottone.setVisible(False)
                else:
                    bottone.setEnabled(vuoto)
            for nome, tipo in (("media", QListWidget),
                               ("avviso_media", QLabel)):
                widget = contenuto.findChild(tipo, nome)
                if widget is not None:
                    if isinstance(widget, QListWidget):
                        widget.clear()
                    widget.setVisible(False)

        vista.show_layout(impaginato)
        if conteggi is not None:
            testo = ("%d unità · %d epoche · %d rapporti"
                     % (len(model.units), len(model.epochs),
                        len(model.relations)))
            if impaginato.removed_redundant:
                # Altrimenti l'intestazione dice 93 e nel disegno se ne
                # contano 59, senza che niente spieghi la differenza.
                testo += (" (%d non disegnati: già detti da un cammino "
                          "più lungo)" % impaginato.removed_redundant)
            conteggi.setText(testo)
        for avviso in model.warnings:
            try:
                iface.messageBar().pushInfo("Matrice", str(avviso))
            except Exception:                       # noqa: BLE001
                pass
        if is_heavy(impaginato):
            try:
                iface.messageBar().pushInfo(
                    "Matrice",
                    "Il disegno è grande (%d unità): navigarlo può essere "
                    "lento. Conviene salvarlo in SVG e aprirlo a parte."
                    % len(model.units))
            except Exception:                       # noqa: BLE001
                pass
        dock.show()
        dock.raise_()
        return True
    except Exception as e:                          # noqa: BLE001
        # una finestra che non si apre non è un motivo per un traceback,
        # ma nemmeno per un silenzio: senza questa riga un guasto dentro
        # il disegno è indistinguibile da un file sbagliato.
        try:
            from qgis.core import Qgis, QgsMessageLog
            QgsMessageLog.logMessage(
                "Pannello matrice non aperto: %s: %s" % (type(e).__name__, e),
                "PyArchInit", Qgis.MessageLevel.Warning)
        except Exception:                           # noqa: BLE001
            pass
        return False


def _save(iface, vista, formato: str) -> None:
    from qgis.PyQt.QtWidgets import QFileDialog

    filtro = ("Immagine SVG (*.svg)" if formato == "svg"
              else "Immagine PNG (*.png)")
    percorso, _ = QFileDialog.getSaveFileName(
        vista, "Salva la matrice", "matrice.%s" % formato, filtro)
    if not percorso:
        return
    scritto = (vista.save_svg(percorso) if formato == "svg"
               else vista.save_png(percorso))
    try:
        if scritto:
            iface.messageBar().pushInfo("Matrice", "Salvata in %s" % scritto)
        else:
            iface.messageBar().pushWarning(
                "Matrice", "Non sono riuscito a salvare il disegno in %s."
                % percorso)
    except Exception:                               # noqa: BLE001
        pass


def close_panel(iface) -> None:
    """Per ``unload()``: il dock non deve sopravvivere al plugin."""
    dock = _existing(iface)
    if dock is not None:
        try:
            iface.removeDockWidget(dock)
            dock.deleteLater()
        except Exception:                           # noqa: BLE001
            pass
