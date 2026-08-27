# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-24
    copyright            : (C) 2018 by Salvatore Larosa
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import subprocess
from qgis.core import QgsSettings
from graphviz import Digraph, Source
from .pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ...tabs.pyarchinit_setting_matrix import *
from .matrix_layout_policy import (
    apply_large_graph_policy, graphviz_stderr_guard, safe_raster_dpi,
    set_dot_dpi, vector_dot_source,
)
from .matrix_poster import POSTER_SCALE_MODES, build_poster_pdf, plan_poster


def _render(graph, **kwargs):
    """``graph.render(**kwargs)`` that survives ``sys.stderr is None``.

    graphviz-python re-emits dot's stderr with ``sys.stderr.write()``;
    inside QGIS without the Python console (Windows GUI process) that is
    ``None`` and a mere dot *warning* — the period export triggers
    "Two clusters named ..." — aborted the whole export with
    "'NoneType' object has no attribute 'write'".
    """
    with graphviz_stderr_guard('graphviz'):
        return graph.render(**kwargs)


def _clamp_raster_dpi(dot_path, requested_dpi):
    """Lower the ``dpi`` inside the laid-out *dot_path* so that the bitmap
    graphviz will produce stays within the cairo limit (32767 px/side).

    Must run while the file still carries the root ``bb``. Returns
    ``(dpi_used, clamped)``. On the 2026-08 test DB (1311 US) the 300-dpi
    JPG was a 0-byte file and the PNG was scaled ×0.098; see
    ``matrix_layout_policy``.
    """
    try:
        with open(dot_path, 'r', encoding='utf-8', errors='replace') as fh:
            text = fh.read()
    except OSError:
        return requested_dpi, False
    dpi = safe_raster_dpi(text, requested_dpi)
    try:
        requested = int(float(requested_dpi))
    except (TypeError, ValueError):
        requested = dpi
    if dpi >= requested:
        return requested, False
    with open(dot_path, 'w', encoding='utf-8') as fh:
        fh.write(set_dot_dpi(text, dpi))
    print(f"matrix: a {requested}-dpi bitmap would exceed the cairo limit; "
          f"rendering at {dpi} dpi and writing .svg/.pdf copies")
    return dpi, True


def _pipe(source_text, fmt):
    """Render *source_text* with dot and return the bytes (stdin → stdout:
    nothing is written next to the tred file)."""
    with graphviz_stderr_guard('graphviz'):
        return Source(source_text).pipe(format=fmt)


def _render_vector_copies(dot_path, formats=('svg', 'pdf')):
    """Write ``<dot_path>.svg`` / ``.pdf`` next to the raster: a matrix too
    wide for a bitmap is still fully readable (zoomable) as vector.

    The copies use ``dpi=72`` (1 pt = 1 pt) and, when the drawing exceeds
    200 in on a side, a graphviz ``size`` cap: Acrobat/Preview otherwise
    show only a window of the page ("vedo solo una parte").
    """
    with open(dot_path, encoding='utf-8') as fh:
        vector_src = vector_dot_source(fh.read())
    written = []
    for fmt in formats:
        out = f"{dot_path}.{fmt}"
        try:
            with open(out, 'wb') as fh:
                fh.write(_pipe(vector_src, fmt))
            written.append(out)
        except Exception as e:
            print(f"matrix: {fmt} render failed: {e}")
    return written


def _poster_settings(dialog):
    """(requested, paper, mode) from the Setting_Matrix widgets; defaults
    (False, 'A0', 'fit_height') when the dialog has no poster controls."""
    box = getattr(dialog, 'checkBox_poster', None)
    requested = bool(box.isChecked()) if box is not None else False
    paper_combo = getattr(dialog, 'comboBox_poster_paper', None)
    paper = paper_combo.currentText().strip() if paper_combo is not None else 'A0'
    mode_combo = getattr(dialog, 'comboBox_poster_scale', None)
    idx = mode_combo.currentIndex() if mode_combo is not None else 0
    mode = POSTER_SCALE_MODES[idx][0] if 0 <= idx < len(POSTER_SCALE_MODES) \
        else POSTER_SCALE_MODES[0][0]
    return requested, paper or 'A0', mode


def _render_matrix_poster(dot_path, paper='A0', mode='fit_height'):
    """Tile the uncapped 1:1 vector PDF of *dot_path* onto *paper* sheets.

    Returns ``(poster_pdf_path, plan)`` or ``(None, None)`` on failure —
    the poster is a bonus output and must never break the export.
    """
    import shutil
    import tempfile
    try:
        with open(dot_path, encoding='utf-8') as fh:
            src_72 = set_dot_dpi(fh.read(), 72)   # 1 pt = 1 pt, no size cap
        tmp_dir = tempfile.mkdtemp(prefix='pyarchinit_poster_')
        try:
            full_pdf = os.path.join(tmp_dir, 'matrix_full.pdf')
            with open(full_pdf, 'wb') as fh:
                fh.write(_pipe(src_72, 'pdf'))
            import fitz  # PyMuPDF (plugin dependency)
            with fitz.open(full_pdf) as doc:
                rect = doc[0].rect
            plan = plan_poster(rect.width, rect.height, paper=paper, mode=mode)
            stem = dot_path[:-len('_tred.dot')] if dot_path.endswith('_tred.dot') \
                else dot_path
            out = f"{stem}_poster_{paper}.pdf"
            build_poster_pdf(full_pdf, out, plan)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"matrix: poster {os.path.basename(out)} — {plan.describe()}")
        return out, plan
    except Exception as e:
        print(f"matrix: poster PDF failed: {e}")
        return None, None


def _large_matrix_notice(dpi, poster=None):
    text = ("Matrix molto grande: l'immagine JPG è stata generata a "
            f"{dpi} dpi (limite del renderer bitmap). Per la versione "
            "leggibile usa i file .svg / .pdf salvati nella stessa "
            "cartella (pyarchinit_Matrix_folder).")
    if poster:
        text += _poster_notice(poster)
    return text


def _poster_notice(poster):
    path, plan = poster
    return (f"\n\nPoster per la stampa: {os.path.basename(path)} "
            f"({plan.describe()}, sovrapposizione 2 cm tra i fogli).")




class HarrisMatrix:
    """
        This class is used to create a Harris Matrix, a tool used in archaeology to depict the temporal succession of archaeological contexts.

        Attributes:
        L (str): The user's locale.
        HOME (str): The home directory for the PyArchInit application.
        DB_MANAGER (str): The database manager for the application.
        TABLE_NAME (str): The name of the table in the database.
        MAPPER_TABLE_CLASS (str): The mapper table class for the application.
        ID_TABLE (str): The ID of the table.
        MATRIX (Setting_Matrix): The matrix settings for the application.
        """

    L=QgsSettings().value("locale/userLocale")[0:2]
    HOME = os.environ['PYARCHINIT_HOME']
    DB_MANAGER = ""
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    ID_TABLE = "id_us"
    MATRIX = Setting_Matrix()
    def __init__(self, sequence,negative,conteporene,connection,connection_to,periodi):
        """
        The constructor for the HarrisMatrix class.

        Parameters:
        sequence (list): A list of sequences.
        negative (list): A list of negative relationships.
        conteporene (list): A list of contemporary relationships.
        connection (list): A list of connections.
        connection_to (list): A list of connections to other elements.
        periodi (list): A list of periods.
        """
        self.sequence = sequence
        self.negative = negative
        self.periodi=periodi
        self.conteporene=conteporene
        self.connection=connection
        self.connection_to=connection_to
        self.dialog = Setting_Matrix()        
        self.dialog.exec_()

    @property
    def export_matrix(self):
        """
        Export the matrix as a graph using Digraph to visualize relationships between elements, including periods, phases, and service units.
        The graph includes custom colors and styles to represent different relationships and types of service units.
        """
        # Genera un grafico utilizzando Digraph per visualizzare relazioni tra elementi, inclusi periodi, fasi e unità di servizio.
        # Il grafico include colori e stili personalizzati per rappresentare diverse relazioni e tipi di unità di servizio.

        global periodo_key, periodo, us_list
        G = Digraph(engine='dot', strict=False)
        G.attr(rankdir='TB', viewport="", ratio="auto")
        G.attr(compound='true')
        G.graph_attr['pad'] = "0.5"
        G.graph_attr['nodesep'] = "1"
        G.graph_attr['ranksep'] = "3"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = str(self.dialog.lineEdit_dpi.text())

        elist1 = []
        elist2 = []
        elist3 = []

        # Costruisci l'insieme delle US coinvolte in una relazione
        us_rilevanti = set()
        for source, target in self.sequence:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.conteporene:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.negative:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection_to:
            us_rilevanti.add(source)
            us_rilevanti.add(target)

        if self.dialog.checkBox_period.isChecked():

            self.periodi = sorted(self.periodi, key=lambda x: x[2][0])  # Supponendo che x[2][0] sia l'indicatore di data/periodo
            # Crea i subgraph per siti, aree e periodi
            for entry in self.periodi:
                cluster, sito, area_info = entry
                datazione, periodo_info = area_info[2]
                periodo, fase_info = periodo_info
                fase, us_list = fase_info

                site_key = f'cluster_{cluster}'
                area_key = f'{site_key}_sito_{sito}'
                periodo_key = f'cluster_{area_key}_per_{periodo}'
                fase_key = f'cluster_{periodo_key}_fase_{fase}'

                with G.subgraph(name=site_key) as site:
                    site.attr(color="lightgray", style='filled')  # Rimuovi il bordo impostandolo come bianco
                    site.attr(rank='same') # Forza questo sottografo al livello più alto
                    site.attr(label=sito.replace("_", " ")) # Crea il nodo del sito
                    site.node('node0', shape='plaintext', label='', width='0', Height='0') # Crea un nodo vuoto per forzare il nodo del sito in alto
                    if periodo:
                        with site.subgraph(name=periodo_key) as p:
                            p.attr(label=datazione, margin='100',area='150',labeljust='l', style='filled', color='lightblue', rank='same')
                            p.attr(shape='plaintext')

                            with p.subgraph(name=fase_key) as f:
                                f.attr(label=fase, labeljust='l',area='200',margin='150',style='filled,dashed', fillcolor='#FFFFE080', color='black',
                                       rank='same', penwidth='1.5')

                                with f.subgraph(name=f'{fase_key}_cont') as temp:
                                    temp.attr(rankdir='LR',label='',style='invis')

                                    negative_sources = {source for source, _ in self.negative}
                                    conteporene_sources = {source for source, _ in self.conteporene}

                                    for us in us_list:
                                        if us in us_rilevanti:
                                            # Rimuovi "Area_" e il numero
                                            label_name = us.split('_')[1] if '_' in us else us.replace("_", " ")



                                            if us in negative_sources:
                                                # cambia colore per noi negativo
                                                f.node(us.split('_')[1], label=label_name, shape=str(self.dialog.combo_box_6.currentText()),
                                                       style='filled', rank='same', color=str(self.dialog.combo_box_2.currentText()))
                                            elif us in conteporene_sources:
                                               #cambia colore per conteporene noi
                                                temp.node(us.split('_')[1], label=label_name, shape=str(self.dialog.combo_box_18.currentText()),
                                                        color=str(self.dialog.combo_box_17.currentText()), style='filled')
                                            else:
                                                # colore predefinito
                                                f.node(us.split('_')[1], label=label_name, shape=str(self.dialog.combo_box_3.currentText()),
                                                       style='filled', color=str(self.dialog.combo_box.currentText()))
        for bb in self.sequence:
            if bb[0] in us_rilevanti and bb[1] in us_rilevanti:
                a = (f"{bb[0].split('_')[-1]}", f"{bb[1].split('_')[-1]}")
                elist1.append(a)

        with G.subgraph(name='main') as e:

            e.edges(elist1)
            e.node_attr['shape'] = str(self.dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(self.dialog.combo_box_4.currentText())
            e.node_attr.update( style='filled', fillcolor=str(self.dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'
            e.node_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(self.dialog.combo_box_10.currentText())
            e.edge_attr['color'] = '#00000080'
            e.edge_attr['len'] = '0'
            e.edge_attr.update(arrowhead=str(self.dialog.combo_box_11.currentText()),
                               arrowsize=str(self.dialog.combo_box_12.currentText()))


            for cc in self.conteporene:
                if cc[0] in us_rilevanti and cc[1] in us_rilevanti:
                    a = (f"{cc[0].split('_')[-1]}", f"{cc[1].split('_')[-1]}")
                    elist3.append(a)
            # One subgraph for ALL contemporary edges. Re-opening it inside
            # the loop re-emitted the growing list at every iteration —
            # O(n²) duplicate edges (225 576 edge lines for 2 039 relations
            # on a 1311-US DB: 34 MB layout, 5 s of dot before tred).
            with G.subgraph(name='main1') as b:

                b.edges(elist3)
                b.node_attr['shape'] = str(self.dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(self.dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'
                b.node_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(self.dialog.combo_box_23.currentText())

                b.edge_attr['color'] = '#00000080'
                b.edge_attr.update(constraint='False',arrowhead=str(self.dialog.combo_box_21.currentText()),
                                   arrowsize=str(self.dialog.combo_box_24.currentText()))


            for dd in self.negative:
                if dd[0] in us_rilevanti and dd[1] in us_rilevanti:
                    a = (f"{dd[0].split('_')[-1]}", f"{dd[1].split('_')[-1]}")
                    elist2.append(a)

            # Same for the negative relations (see above).
            with G.subgraph(name='main2') as a:

                a.edges(elist2)
                a.node_attr['shape'] = str(self.dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'
                a.node_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(self.dialog.combo_box_15.currentText())
                a.edge_attr['color'] = '#00000080'
                a.edge_attr['len'] = '0'
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_14.currentText()),
                                   arrowsize=str(self.dialog.combo_box_16.currentText()))

        if bool(self.dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black', fontsize='16',
                       style='filled')
                with G.subgraph(name='cluster3') as i:
                    with i.subgraph(name='cluster_temp') as temp:
                        temp.attr(style='invis')
                        temp.attr(rankdir='LR', rank='same')
                        if self.L == 'it':
                            i.node('a0', shape=str(self.dialog.combo_box_3.currentText()),
                                   fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',
                                   label='Ante/Post')
                            i.edge('a0', 'a1', shape=str(self.dialog.combo_box_3.currentText()),
                                   fillcolor=str(self.dialog.combo_box.currentText()),
                                   style=str(self.dialog.combo_box_10.currentText()),
                                   arrowhead=str(self.dialog.combo_box_11.currentText()),
                                   arrowsize=str(self.dialog.combo_box_12.currentText()))
                            i.node('a1', shape=str(self.dialog.combo_box_6.currentText()),
                                   fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',
                                   label='Negative')
                            i.edge('a1', 'a2', shape=str(self.dialog.combo_box_8.currentText()),
                                   fillcolor=str(self.dialog.combo_box_2.currentText()),
                                   style=str(self.dialog.combo_box_15.currentText()),
                                   arrowhead=str(self.dialog.combo_box_14.currentText()),
                                   arrowsize=str(self.dialog.combo_box_16.currentText()))


                            temp.node('a2', shape=str(self.dialog.combo_box_18.currentText()),
                                   fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',
                                   label='Contemporaneo')

                            # i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                            temp.edge('a2', 'a3', constraint='False', shape=str(self.dialog.combo_box_22.currentText()),
                                   fillcolor=str(self.dialog.combo_box_17.currentText()),
                                   style=str(self.dialog.combo_box_23.currentText()),
                                   arrowhead=str(self.dialog.combo_box_21.currentText()),
                                   arrowsize=str(self.dialog.combo_box_24.currentText()))
                            temp.node('a3', rank='same', shape=str(self.dialog.combo_box_18.currentText()),
                                   fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',
                                   label='Contemporaneo')
                            temp.edge('a3', 'a2', constraint='False', shape=str(self.dialog.combo_box_22.currentText()),
                                   fillcolor=str(self.dialog.combo_box_17.currentText()),
                                   style=str(self.dialog.combo_box_23.currentText()),
                                   arrowhead=str(self.dialog.combo_box_21.currentText()),
                                   arrowsize=str(self.dialog.combo_box_24.currentText()))


                        else:
                            i.node('a0', shape=str(self.dialog.combo_box_3.currentText()),
                                   fillcolor=str(self.dialog.combo_box.currentText()), style='filled',
                                   gradientangle='90',
                                   label='Ante/Post')
                            i.edge('a0', 'a1', shape=str(self.dialog.combo_box_3.currentText()),
                                   fillcolor=str(self.dialog.combo_box.currentText()),
                                   style=str(self.dialog.combo_box_10.currentText()),
                                   arrowhead=str(self.dialog.combo_box_11.currentText()),
                                   arrowsize=str(self.dialog.combo_box_12.currentText()))
                            i.node('a1', shape=str(self.dialog.combo_box_6.currentText()),
                                   fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled',
                                   gradientangle='90',
                                   label='Negative')
                            i.edge('a1', 'a2', shape=str(self.dialog.combo_box_8.currentText()),
                                   fillcolor=str(self.dialog.combo_box_2.currentText()),
                                   style=str(self.dialog.combo_box_15.currentText()),
                                   arrowhead=str(self.dialog.combo_box_14.currentText()),
                                   arrowsize=str(self.dialog.combo_box_16.currentText()))

                            temp.node('a2', shape=str(self.dialog.combo_box_18.currentText()),
                                      fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled',
                                      gradientangle='1',
                                      label='Sama as')

                            # i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                            temp.edge('a2', 'a3', constraint='False', shape=str(self.dialog.combo_box_22.currentText()),
                                      fillcolor=str(self.dialog.combo_box_17.currentText()),
                                      style=str(self.dialog.combo_box_23.currentText()),
                                      arrowhead=str(self.dialog.combo_box_21.currentText()),
                                      arrowsize=str(self.dialog.combo_box_24.currentText()))
                            temp.node('a3', rank='same', shape=str(self.dialog.combo_box_18.currentText()),
                                      fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled',
                                      gradientangle='1',
                                      label='Same as')
                            temp.edge('a3', 'a2', constraint='False', shape=str(self.dialog.combo_box_22.currentText()),
                                      fillcolor=str(self.dialog.combo_box_17.currentText()),
                                      style=str(self.dialog.combo_box_23.currentText()),
                                      arrowhead=str(self.dialog.combo_box_21.currentText()),
                                      arrowsize=str(self.dialog.combo_box_24.currentText()))

        def node_loops_to_self(objects):
            """
            This function checks if there are any loops in the graph. A loop in a graph is a situation where a node is connected to itself.

            Parameters:
            objects (list): A list of lists. Each inner list represents a set of edges in the graph, where each edge is a tuple of two elements (source, target).

            Returns:
            bool: True if there is at least one loop in the graph, False otherwise.
            """
            for obj in objects:
                for source, target in obj:
                    if source == target:
                        return True
            return False

        # Define the edges of the graph
        objects = [self.sequence, self.conteporene, self.negative, self.connection, self.connection_to]

        # Check if the graph has any loops
        has_loop = node_loops_to_self(objects)

        # If the graph has loops, display a warning message
        if has_loop:
            QMessageBox.warning(None, "Warning", "The graph contains loops, the rendering may not be correct")

        def showMessage(message, title='Info', icon=QMessageBox.Information):
            msgBox = QMessageBox()
            msgBox.setIcon(icon)
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.exec_()
        try:
            # Assumi che self.HOME sia già definito
            matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
            filename = 'Harris_matrix'




            # Large graphs: ortho routing is unusable (>15 min at ~2000
            # edges) → polyline + tighter spacing (matrix_layout_policy).
            apply_large_graph_policy(
                G.graph_attr, len(elist1) + len(elist2) + len(elist3))

            # Rendering del file DOT
            G.format = 'dot'
            try:
                dot_file = _render(G, directory=matrix_path, filename=filename)
            except Exception as e:
                showMessage(f"Errore durante il rendering del file DOT: {e}", title='Errore', icon=QMessageBox.Critical)
                return
            tred_output_file_path = os.path.join(matrix_path, f"{filename}_tred.dot")

            error_file_path = os.path.join(matrix_path, 'matrix_error.txt')
        except Exception as e:
            #showMessage(f"Errore durante la creazione del file DOT: {e}", title='Errore', icon=QMessageBox.Critical)
            return

        startupinfo = None
        if Pyarchinit_OS_Utility.isWindows():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:

            with open(tred_output_file_path, "w") as out_file, open(error_file_path, "w") as err_file:
                subprocess.call(['tred', dot_file], stdout=out_file, stderr=err_file, startupinfo=startupinfo)
            #showMessage("Comando `tred` eseguito con successo.")
        except Exception as e:
            #showMessage(f"Errore durante l'esecuzione di `tred`: {e}", title='Errore', icon=QMessageBox.Critical)
            return
        if os.path.getsize(error_file_path) > 0:
            with open(error_file_path, "r") as err_file:
                print()#errors = err_file.read()
                #showMessage(f"Errori durante l'esecuzione di `tred`:\n{errors}", title='Errore')
                            #icon=QMessageBox.Warning)
        else:
            print()#showMessage("Nessun errore riportato da `tred`.")

        raster_dpi, clamped = _clamp_raster_dpi(
            tred_output_file_path, self.dialog.lineEdit_dpi.text())
        try:
            g = Source.from_file(tred_output_file_path, format='jpg')
            _render(g)
            poster_requested, poster_paper, poster_mode = _poster_settings(self.dialog)
            poster = None
            if clamped or poster_requested:
                _render_vector_copies(tred_output_file_path)
                # Printable output: the JPG of a huge matrix is unreadable,
                # so the poster is produced whenever the bitmap had to be
                # clamped or the user asked for it in Setting_Matrix.
                poster_path, poster_plan = _render_matrix_poster(
                    tred_output_file_path, poster_paper, poster_mode)
                if poster_path:
                    poster = (poster_path, poster_plan)
            if clamped:
                showMessage(_large_matrix_notice(raster_dpi, poster),
                            title='Matrix', icon=QMessageBox.Information)
            elif poster:
                showMessage(_poster_notice(poster).strip(),
                            title='Matrix', icon=QMessageBox.Information)
            # return g (Considera che in una GUI, potresti voler gestire il risultato in modo diverso)
        except Exception as e:
            print(f"export_matrix: graphviz render failed: {e}")
    @property
    def export_matrix_2(self):
        G = Digraph(engine='dot',strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad']="0.5"
        G.graph_attr['nodesep']="1"
        G.graph_attr['ranksep']="1.5"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = str(self.dialog.lineEdit_dpi.text())
        elist1 = []
        elist2 = []
        elist3 = []
        elist4 = []
        elist5 = []
        # Costruisci l'insieme delle US coinvolte in una relazione
        us_rilevanti = set()
        for source, target in self.sequence:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.conteporene:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.negative:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection_to:
            us_rilevanti.add(source)
            us_rilevanti.add(target)

        if bool(self.dialog.checkBox_period.isChecked()):
            for aa in self.periodi:
                if any(us in us_rilevanti for us in aa[0]):  # controlla se almeno una delle US è in us_rilevanti
                    with G.subgraph(name=aa[1]) as c:
                        for n in aa[0]:
                            if n in us_rilevanti:
                                c.attr('node', shape='record', label=str(n))
                                c.node(str(n))
                        c.attr(color='blue')
                        c.attr('node', shape='record', fillcolor='white', style='filled', gradientangle='90',
                               label=aa[2])
                        c.node(aa[2])

        for bb in self.sequence:
            if bb[0] in us_rilevanti and bb[1] in us_rilevanti:
                a = (bb[0], bb[1])
                elist1.append(a)
        with G.subgraph(name='main') as e:
            e.attr(rankdir='TB')
            e.edges(elist1)
            e.node_attr['shape'] = str(self.dialog.combo_box_3.currentText())
            e.node_attr['style'] = str(self.dialog.combo_box_4.currentText())
            e.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box.currentText()))
            e.node_attr['color'] = 'black'
            e.node_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['penwidth'] = str(self.dialog.combo_box_5.currentText())
            e.edge_attr['style'] = str(self.dialog.combo_box_10.currentText())
            e.edge_attr.update(arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
            for cc in self.conteporene:
                if cc[0] in us_rilevanti and cc[1] in us_rilevanti:
                    a = (cc[0], cc[1])
                    elist3.append(a)

            with G.subgraph(name='main1') as b:
                b.edges(elist3)
                b.node_attr['shape'] = str(self.dialog.combo_box_18.currentText())
                b.node_attr['style'] = str(self.dialog.combo_box_22.currentText())
                b.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_17.currentText()))
                b.node_attr['color'] = 'black'
                b.node_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['penwidth'] = str(self.dialog.combo_box_19.currentText())
                b.edge_attr['style'] = str(self.dialog.combo_box_23.currentText())
                b.edge_attr.update(arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
            for dd in self.negative:
                if dd[0] in us_rilevanti and dd[1] in us_rilevanti:
                    a = (dd[0], dd[1])
                    elist2.append(a)

            with G.subgraph(name='main2') as a:
                #a.attr(rank='same')
                a.edges(elist2)
                a.node_attr['shape'] = str(self.dialog.combo_box_6.currentText())
                a.node_attr['style'] = str(self.dialog.combo_box_8.currentText())
                a.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_2.currentText()))
                a.node_attr['color'] = 'black'
                a.node_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['penwidth'] = str(self.dialog.combo_box_7.currentText())
                a.edge_attr['style'] = str(self.dialog.combo_box_15.currentText())
                a.edge_attr.update(arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
            for ee in self.connection:
                if ee[0] in us_rilevanti and ee[1] in us_rilevanti:
                    a = (ee[0], ee[1])
                    elist4.append(a)

            with G.subgraph(name='main3') as r:
                #a.attr(rank='same')
                r.edges(elist4)
                r.node_attr['shape'] = str(self.dialog.combo_box_26.currentText())
                r.node_attr['style'] = str(self.dialog.combo_box_30.currentText())
                r.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_28.currentText()))
                r.node_attr['color'] = 'black'
                r.node_attr['penwidth'] = str(self.dialog.combo_box_27.currentText())
                r.edge_attr['penwidth'] = str(self.dialog.combo_box_27.currentText())
                r.edge_attr['style'] = str(self.dialog.combo_box_31.currentText())
                r.edge_attr.update(arrowhead=str(self.dialog.combo_box_29.currentText()), arrowsize=str(self.dialog.combo_box_32.currentText()))
            for ff in self.connection_to:
                if ff[0] in us_rilevanti and ff[1] in us_rilevanti:
                    a = (ff[0], ff[1])
                    elist5.append(a)
            with G.subgraph(name='main4') as t:
                #a.attr(rank='same')
                t.edges(elist5)
                t.node_attr['shape'] = str(self.dialog.combo_box_34.currentText())
                t.node_attr['style'] = str(self.dialog.combo_box_38.currentText())
                t.node_attr.update(style='filled', fillcolor=str(self.dialog.combo_box_36.currentText()))
                t.node_attr['color'] = 'black'
                t.node_attr['penwidth'] = str(self.dialog.combo_box_35.currentText())
                t.edge_attr['penwidth'] = str(self.dialog.combo_box_35.currentText())
                t.edge_attr['style'] = str(self.dialog.combo_box_39.currentText())
                t.edge_attr.update(arrowhead=str(self.dialog.combo_box_37.currentText()), arrowsize=str(self.dialog.combo_box_40.currentText()))
        if bool(self.dialog.checkBox_legend.isChecked()):
            with G.subgraph(name='cluster3') as j:
                j.attr(rank='max')
                j.attr(fillcolor='white', label='Legend', fontcolor='black',fontsize='16',
                style='filled')
                with G.subgraph(name='cluster3') as i:
                    i.attr(rank='max')
                    if self.L=='it':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post')
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Cont.')
                        # i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    elif self.L=='de':
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post')
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negativ')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Wie')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))
                    else:
                        i.node('a0', shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style='filled', gradientangle='90',label='Ante/Post')
                        i.edge('a0', 'a1',shape=str(self.dialog.combo_box_3.currentText()), fillcolor=str(self.dialog.combo_box.currentText()), style=str(self.dialog.combo_box_10.currentText()),arrowhead=str(self.dialog.combo_box_11.currentText()), arrowsize=str(self.dialog.combo_box_12.currentText()))
                        i.node('a1', shape=str(self.dialog.combo_box_6.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style='filled', gradientangle='90',label='Negative')
                        i.edge('a1', 'a2',shape=str(self.dialog.combo_box_8.currentText()), fillcolor=str(self.dialog.combo_box_2.currentText()), style=str(self.dialog.combo_box_15.currentText()),arrowhead=str(self.dialog.combo_box_14.currentText()), arrowsize=str(self.dialog.combo_box_16.currentText()))
                        i.node('a2', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1',label='Same')
                        #i.node('node3', shape=str(self.dialog.combo_box_18.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style='filled', gradientangle='1')
                        i.edge('a2', 'a1',shape=str(self.dialog.combo_box_22.currentText()), fillcolor=str(self.dialog.combo_box_17.currentText()), style=str(self.dialog.combo_box_23.currentText()),arrowhead=str(self.dialog.combo_box_21.currentText()), arrowsize=str(self.dialog.combo_box_24.currentText()))

        def showMessage(message, title='Info', icon=QMessageBox.Information):
            msgBox = QMessageBox()
            msgBox.setIcon(icon)
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.exec_()

        try:
            # Assumi che self.HOME sia già definito
            matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
            filename = 'Harris_matrix2ED'

            apply_large_graph_policy(
                G.graph_attr,
                len(elist1) + len(elist2) + len(elist3) + len(elist4) + len(elist5))

            # Rendering del file DOT
            G.format = 'dot'
            dot_file = _render(G, directory=matrix_path, filename=filename)
            tred_output_file_path = os.path.join(matrix_path, f"{filename}_graphml.dot")

            error_file_path = os.path.join(matrix_path, 'matrix_error.txt')
        except Exception as e:
            #showMessage(f"Errore durante la creazione del file DOT: {e}", title='Errore', icon=QMessageBox.Critical)
            return

        startupinfo = None
        if Pyarchinit_OS_Utility.isWindows():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:

            with open(tred_output_file_path, "w") as out_file, open(error_file_path, "w") as err_file:
                subprocess.call(['tred', dot_file], stdout=out_file, stderr=err_file, startupinfo=startupinfo)
            #showMessage("Comando `tred` eseguito con successo.")
        except Exception as e:
            print()#showMessage(f"Errore durante l'esecuzione di `tred`: {e}", title='Errore', icon=QMessageBox.Critical)

        if os.path.getsize(error_file_path) > 0:
            with open(error_file_path, "r") as err_file:
                print()
                #errors = err_file.read()
                #showMessage(f"Errori durante l'esecuzione di `tred`:\n{errors}", title='Errore',
                            #icon=QMessageBox.Warning)
        else:
            print()#showMessage("Nessun errore riportato da `tred`.")

        raster_dpi, clamped = _clamp_raster_dpi(
            tred_output_file_path, self.dialog.lineEdit_dpi.text())
        try:
            g = Source.from_file(tred_output_file_path, format='jpg')
            _render(g)
            poster_requested, poster_paper, poster_mode = _poster_settings(self.dialog)
            poster = None
            if clamped or poster_requested:
                _render_vector_copies(tred_output_file_path)
                # Printable output: the JPG of a huge matrix is unreadable,
                # so the poster is produced whenever the bitmap had to be
                # clamped or the user asked for it in Setting_Matrix.
                poster_path, poster_plan = _render_matrix_poster(
                    tred_output_file_path, poster_paper, poster_mode)
                if poster_path:
                    poster = (poster_path, poster_plan)
            if clamped:
                showMessage(_large_matrix_notice(raster_dpi, poster),
                            title='Matrix', icon=QMessageBox.Information)
            elif poster:
                showMessage(_poster_notice(poster).strip(),
                            title='Matrix', icon=QMessageBox.Information)
            # return g (Considera che in una GUI, potresti voler gestire il risultato in modo diverso)
        except Exception as e:
            print(f"graphml export_matrix: render failed: {e}")


class ViewHarrisMatrix:
    L = QgsSettings().value("locale/userLocale")[0:2]
    HOME = os.environ['PYARCHINIT_HOME']
    DB_MANAGER = ""
    TABLE_NAME = 'us_table'
    MAPPER_TABLE_CLASS = "US"
    ID_TABLE = "id_us"
    MATRIX = Setting_Matrix()

    # s=pyqtSignal(str)
    def __init__(self, sequence, negative, conteporene, connection, connection_to, periodi):
        self.sequence = sequence
        self.negative = negative
        self.periodi = periodi
        self.conteporene = conteporene
        self.connection = connection
        self.connection_to = connection_to
        #self.dialog = Setting_Matrix()
        #self.dialog.exec_()

    @property
    def export_matrix(self):
        G = Digraph(engine='dot', strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad'] = "0.5"
        G.graph_attr['nodesep'] = "1"
        G.graph_attr['ranksep'] = "1.5"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = '150'
        elist1 = []
        elist2 = []
        elist3 = []
        elist4 = []
        elist5 = []


        for bb in self.sequence:
            a = (bb[0], bb[1])
            elist1.append(a)
        with G.subgraph(name='main') as e:
            e.attr(rankdir='TB')
            e.edges(elist1)
            e.node_attr['shape'] = 'box'
            e.node_attr['style'] = 'solid'
            e.node_attr.update(style='filled', fillcolor='white')
            e.node_attr['color'] = 'black'
            e.node_attr['penwidth'] = '.5'
            e.edge_attr['penwidth'] = '.5'
            e.edge_attr['style'] = 'solid'
            e.edge_attr.update(arrowhead='normal',
                               arrowsize='.8')
            for cc in self.conteporene:
                a = (cc[0], cc[1])
                elist3.append(a)
            with G.subgraph(name='main1') as b:
                b.edges(elist3)
                b.node_attr['shape'] = 'box'
                b.node_attr['style'] = 'solid'
                b.node_attr.update(style='filled', fillcolor='white')
                b.node_attr['color'] = 'black'
                b.node_attr['penwidth'] = '.5'
                b.edge_attr['penwidth'] = '.5'
                b.edge_attr['style'] = 'solid'
                b.edge_attr.update(arrowhead='none',
                                   arrowsize='.8')
            for dd in self.negative:
                a = (dd[0], dd[1])
                elist2.append(a)
            with G.subgraph(name='main2') as a:
                # a.attr(rank='same')
                a.edges(elist2)
                a.node_attr['shape'] = 'box'
                a.node_attr['style'] = 'solid'
                a.node_attr.update(style='filled', fillcolor='white')
                a.node_attr['color'] = 'black'
                a.node_attr['penwidth'] = '.5'
                a.edge_attr['penwidth'] = '.5'
                a.edge_attr['style'] = 'solid'
                a.edge_attr.update(arrowhead='normal',
                                   arrowsize='.8')
            for ee in self.connection:
                a = (ee[0], ee[1])
                elist4.append(a)
            with G.subgraph(name='main3') as tr:
                # a.attr(rank='same')
                a.edges(elist4)
                a.node_attr['shape'] = 'box'
                a.node_attr['style'] = 'solid'
                a.node_attr.update(style='filled', fillcolor='white')
                a.node_attr['color'] = 'black'
                a.node_attr['penwidth'] = '.5'
                a.edge_attr['penwidth'] = '.5'
                a.edge_attr['style'] = 'solid'
                a.edge_attr.update(arrowhead='normal',
                                   arrowsize='.8')
            for ff in self.connection_to:
                a = (ff[0], ff[1])
                elist5.append(a)
            with G.subgraph(name='main4') as tb:
                # a.attr(rank='same')
                a.edges(elist5)
                a.node_attr['shape'] = 'box'
                a.node_attr['style'] = 'solid'
                a.node_attr.update(style='filled', fillcolor='white')
                a.node_attr['color'] = 'black'
                a.node_attr['penwidth'] = '.5'
                a.edge_attr['penwidth'] = '.5'
                a.edge_attr['style'] = 'solid'
                a.edge_attr.update(arrowhead='normal',
                                   arrowsize='.8')


        matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
        filename = 'Harris_matrix'
        # f = open(filename, "w")
        apply_large_graph_policy(
            G.graph_attr,
            len(elist1) + len(elist2) + len(elist3) + len(elist4) + len(elist5))
        G.format = 'dot'
        dot_file = _render(G, directory=matrix_path, filename=filename)
        # For MS-Windows, we need to hide the console window.
        if Pyarchinit_OS_Utility.isWindows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        # cmd = ' '.join(['tred', dot_file])
        # dotargs = shlex.split(cmd)
        with open(os.path.join(matrix_path, filename + '_viewtred.dot'), "w") as out, \
                open(os.path.join(matrix_path, 'matrix_error.txt'), "w") as err:
            proc = subprocess.Popen(['tred', dot_file],
                                    # shell=True,
                                    stdout=out,
                                    stderr=err,
                                    startupinfo=si if Pyarchinit_OS_Utility.isWindows() else None)
            proc.wait()  # the file is read right below
        tred_file = os.path.join(matrix_path, filename + '_viewtred.dot')

        raster_dpi, clamped = _clamp_raster_dpi(tred_file, G.graph_attr.get('dpi', '150'))
        f = Source.from_file(tred_file, format='png')
        _render(f)
        g = Source.from_file(tred_file, format='jpg')
        _render(g)
        if clamped:
            _render_vector_copies(tred_file)
            print(_large_matrix_notice(raster_dpi))
        return g, f
        # return f

    @property
    def export_matrix_3(self):
        # Genera un grafico utilizzando Digraph per visualizzare relazioni tra elementi, inclusi periodi, fasi e unità di servizio.
        # Il grafico include colori e stili personalizzati per rappresentare diverse relazioni e tipi di unità di servizio.

        global periodo_key, periodo, us_list
        G = Digraph(engine='dot', strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad'] = "0.5"
        G.graph_attr['nodesep'] = "1"
        G.graph_attr['ranksep'] = "3"
        G.graph_attr['splines'] = 'ortho'
        G.graph_attr['dpi'] = '300'

        elist1 = []
        elist2 = []
        elist3 = []

        # Costruisci l'insieme delle US coinvolte in una relazione
        us_rilevanti = set()
        for source, target in self.sequence:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.conteporene:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.negative:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection:
            us_rilevanti.add(source)
            us_rilevanti.add(target)
        for source, target in self.connection_to:
            us_rilevanti.add(source)
            us_rilevanti.add(target)

        self.periodi = sorted(self.periodi, key=lambda x: x[2][0])
        # Crea i subgraph per siti, aree e periodi
        for entry in self.periodi:
            cluster, sito, area_info = entry
            datazione, periodo_info = area_info[2]
            periodo, fase_info = periodo_info
            fase, us_list = fase_info

            site_key = f'cluster_{cluster}'
            area_key = f'{site_key}_sito_{sito}'
            periodo_key = f'cluster_{area_key}_per_{periodo}'
            fase_key = f'cluster_{periodo_key}_fase_{fase}'

            with G.subgraph(name=site_key) as site:
                site.attr(color="lightgray", style='filled')  # Rimuovi il bordo impostandolo come bianco
                site.attr(rank='same')  # Forza questo sottografo al livello più alto
                site.attr(label=sito.replace("_", " "))  # Crea il nodo del sito
                site.node('node0', shape='plaintext', label='', width='0',
                          Height='0')  # Crea un nodo vuoto per forzare il nodo del sito in alto
                if periodo:
                    with site.subgraph(name=periodo_key) as p:
                        p.attr(label=datazione, margin='100', area='150', labeljust='l', style='filled',
                               color='lightblue', rank='same')
                        p.attr(shape='plaintext')

                        with p.subgraph(name=fase_key) as f:
                            f.attr(label=fase, labeljust='l', area='200', margin='150', style='filled,dashed',
                                   fillcolor='#FFFFE080', color='black',
                                   rank='same', penwidth='1.5')

                            with f.subgraph(name=f'{fase_key}_cont') as temp:
                                temp.attr(rankdir='LR', label='', style='invis')

                                negative_sources = {source for source, _ in self.negative}
                                conteporene_sources = {source for source, _ in self.conteporene}

                                for us in us_list:
                                    if us in us_rilevanti:
                                        # Rimuovi "Area_" e il numero
                                        label_name = us.split('_')[1] if '_' in us else us.replace("_", " ")


                                        if us in negative_sources:
                                            # cambia colore per noi negativo
                                            f.node(us.split('_')[-1], label=label_name,
                                                   shape='box',
                                                   style='filled', rank='same',
                                                   color='gray')
                                        elif us in conteporene_sources:
                                            # cambia colore per conteporene noi
                                            temp.node(us.split('_')[-1], label=label_name,
                                                      shape='box',
                                                      color='white',
                                                      style='filled')
                                        else:
                                            # colore predefinito
                                            f.node(us.split('_')[-1], label=label_name,
                                                   shape='box',
                                                   style='filled', color='white')
        for bb in self.sequence:
            if bb[0] in us_rilevanti and bb[1] in us_rilevanti:
                a = (f"{bb[0].split('_')[-1]}", f"{bb[1].split('_')[-1]}")
                elist1.append(a)

        with G.subgraph(name='main') as e:

            e.attr(rankdir='TB')
            e.edges(elist1)
            e.node_attr['shape'] = 'box'
            e.node_attr['style'] = 'solid'
            e.node_attr.update(style='filled', fillcolor='white')
            e.node_attr['color'] = 'black'
            e.node_attr['penwidth'] = '.5'
            e.edge_attr['penwidth'] = '.5'
            e.edge_attr['style'] = 'solid'
            e.edge_attr.update(arrowhead='normal',
                               arrowsize='.8')

            for cc in self.conteporene:
                if cc[0] in us_rilevanti and cc[1] in us_rilevanti:
                    a = (f"{cc[0].split('_')[-1]}", f"{cc[1].split('_')[-1]}")
                    elist3.append(a)
            # One subgraph for ALL contemporary edges. Re-opening it inside
            # the loop re-emitted the growing list at every iteration —
            # O(n²) duplicate edges (225 576 edge lines for 2 039 relations
            # on a 1311-US DB: 34 MB layout, 5 s of dot before tred).
            with G.subgraph(name='main1') as b:
                b.edges(elist3)
                b.node_attr['shape'] = 'box'
                b.node_attr['style'] = 'solid'
                b.node_attr.update(style='filled', fillcolor='white')
                b.node_attr['color'] = 'black'
                b.node_attr['penwidth'] = '.5'
                b.edge_attr['penwidth'] = '.5'
                b.edge_attr['style'] = 'solid'
                b.edge_attr.update(arrowhead='none',
                                   arrowsize='.8')

            for dd in self.negative:
                if dd[0] in us_rilevanti and dd[1] in us_rilevanti:
                    a = (f"{dd[0].split('_')[-1]}", f"{dd[1].split('_')[-1]}")
                    elist2.append(a)

            # Same for the negative relations (see above).
            with G.subgraph(name='main2') as a:
                a.edges(elist2)
                a.node_attr['shape'] = 'box'
                a.node_attr['style'] = 'solid'
                a.node_attr.update(style='filled', fillcolor='gray')
                a.node_attr['color'] = 'gray'
                a.node_attr['penwidth'] = '.5'
                a.edge_attr['penwidth'] = '.5'
                a.edge_attr['style'] = 'dashed'
                a.edge_attr.update(constraint='False',arrowhead='normal',
                                   arrowsize='.8')



        def showMessage(message, title='Info', icon=QMessageBox.Information):
            msgBox = QMessageBox()
            msgBox.setIcon(icon)
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.exec_()

        try:
            # Assumi che self.HOME sia già definito
            matrix_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_Matrix_folder")
            filename = 'Harris_matrix'

            apply_large_graph_policy(
                G.graph_attr, len(elist1) + len(elist2) + len(elist3))

            # Rendering del file DOT
            G.format = 'dot'
            dot_file = _render(G, directory=matrix_path, filename=filename)
            tred_output_file_path = os.path.join(matrix_path, f"{filename}_viewtred")

            error_file_path = os.path.join(matrix_path, 'matrix_error.txt')
        except Exception as e:
            showMessage(f"Errore durante la creazione del file DOT: {e}", title='Errore', icon=QMessageBox.Critical)
            return

        startupinfo = None
        if Pyarchinit_OS_Utility.isWindows():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:

            with open(tred_output_file_path, "w") as out_file, open(error_file_path, "w") as err_file:
                subprocess.call(['tred', dot_file], stdout=out_file, stderr=err_file, startupinfo=startupinfo)
            # showMessage("Comando `tred` eseguito con successo.")
        except Exception as e:
            #showMessage(f"Errore durante l'esecuzione di `tred`: {e}", title='Errore', icon=QMessageBox.Critical)
            return
        if os.path.getsize(error_file_path) > 0:
            with open(error_file_path, "r") as err_file:
                errors = err_file.read()
                showMessage(f"Errori durante l'esecuzione di `tred`:\n{errors}\n prova a ridurre i dpi", title='Errore',
                icon=QMessageBox.Warning)
        else:
            pass#showMessage("Nessun errore riportato da `tred`.")

        raster_dpi, clamped = _clamp_raster_dpi(
            tred_output_file_path, G.graph_attr.get('dpi', '300'))
        try:
            g = Source.from_file(tred_output_file_path, format='jpg')
            _render(g)
            if clamped:
                _render_vector_copies(tred_output_file_path)
                showMessage(_large_matrix_notice(raster_dpi),
                            title='Matrix', icon=QMessageBox.Information)
            # return g (Considera che in una GUI, potresti voler gestire il risultato in modo diverso)
        except Exception as e:
            showMessage(f"Errore durante il rendering del grafico finale: {e}", title='Errore',
            icon=QMessageBox.Critical)
