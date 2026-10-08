"""La matrice dell'Extended Matrix dentro QGIS.

Un pannello agganciato alla finestra di QGIS che disegna l'em.json: le
fasce delle epoche, le unità con la simbologia dell'Extended Matrix e i
rapporti stratigrafici. Non serve EMStudio, non serve il nodo, non serve
un motore web — richiesta di Enzo del 2026-10-08, dopo aver constatato
che la pagina per-stanza del nodo chiede di accedere.

Un pannello per sessione (stesso ``objectName``, si riusa e si porta
davanti) e ``close_panel`` in ``unload()``: la lezione della 5.13.29, dove
un dock sopravvissuto al plugin lasciava voci doppie al ricaricamento.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

PANEL_OBJECT_NAME = "pyarchinitEmMatrixPanel"

#: Le unità del sito aperto adesso. Vivono qui e non dentro la chiusura
#: che mostra la scheda, perché quella si aggancia una volta sola, alla
#: creazione del dock: riusando il pannello su un secondo sito mostrerebbe
#: per sempre i dati del primo.
_CURRENT_UNITS = {}


def remember_units(units) -> None:
    """Sostituisce le unità che la scheda può mostrare."""
    _CURRENT_UNITS.clear()
    _CURRENT_UNITS.update({u.node_id: u for u in units})


def details_for(node_id: str) -> str:
    """La scheda dell'unità scelta, o l'invito a sceglierne una."""
    unit = _CURRENT_UNITS.get(node_id)
    if unit is None:
        return "<i>Scegli un'unità per vederne la scheda.</i>"
    return _details_text(unit)


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


def open_in_panel(iface, em_json_path, title: str = "") -> bool:
    """Apre (o riusa) il pannello sulla matrice del file. False se non si può."""
    guasto = describe_failure(em_json_path)
    if guasto:
        return False
    try:
        from qgis.PyQt.QtCore import Qt
        from qgis.PyQt.QtWidgets import (QDockWidget, QHBoxLayout, QLabel,
                                         QPushButton, QSplitter, QTextBrowser,
                                         QVBoxLayout, QWidget)

        from ..utility.em_matrix_layout import layout
        from ..utility.em_matrix_model import read_em_json
        from ..utility.em_matrix_view import MatrixView, is_heavy

        model = read_em_json(Path(em_json_path))
        impaginato = layout(model)

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

            scheda = QTextBrowser(contenitore)
            scheda.setObjectName("scheda")
            scheda.setMinimumWidth(240)
            scheda.setHtml("<i>Scegli un'unità per vederne la scheda.</i>")

            divisore = QSplitter(Qt.Orientation.Horizontal, contenitore)
            divisore.addWidget(vista)
            divisore.addWidget(scheda)
            divisore.setStretchFactor(0, 4)
            divisore.setStretchFactor(1, 1)
            colonna.addWidget(divisore)

            dock.setWidget(contenitore)
            iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

            def mostra(node_id):
                scheda.setHtml(details_for(node_id))

            vista.selected.connect(mostra)
        else:
            dock.setWindowTitle(title or "Matrice Extended Matrix")
            vista = dock.widget().findChild(MatrixView, "vista")
            conteggi = dock.widget().findChild(QLabel, "conteggi")
            scheda = dock.widget().findChild(QTextBrowser, "scheda")
            if scheda is not None:
                scheda.setHtml("<i>Scegli un'unità per vederne la scheda.</i>")

        remember_units(model.units)

        vista.show_layout(impaginato)
        if conteggi is not None:
            conteggi.setText("%d unità · %d epoche · %d rapporti"
                             % (len(model.units), len(model.epochs),
                                len(model.relations)))
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
    except Exception:                               # noqa: BLE001
        # una finestra che non si apre non è un motivo per un traceback
        return False


def _save(iface, vista, formato: str) -> None:
    from qgis.PyQt.QtWidgets import QFileDialog

    filtro = ("Immagine SVG (*.svg)" if formato == "svg"
              else "Immagine PNG (*.png)")
    percorso, _ = QFileDialog.getSaveFileName(
        vista, "Salva la matrice", "matrice.%s" % formato, filtro)
    if not percorso:
        return
    if formato == "svg":
        vista.save_svg(percorso)
    else:
        vista.save_png(percorso)
    try:
        iface.messageBar().pushInfo("Matrice", "Salvata in %s" % percorso)
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
