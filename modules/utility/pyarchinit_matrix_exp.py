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

                                with f.subgraph(name='cluster_cont') as temp:
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




            # Rendering del file DOT
            G.format = 'dot'
            try:
                dot_file = G.render(directory=matrix_path, filename=filename)
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

        try:
            g = Source.from_file(tred_output_file_path, format='jpg')
            g.render()
            print()#showMessage("Rendering del grafico completato.")
            # return g (Considera che in una GUI, potresti voler gestire il risultato in modo diverso)
        except Exception as e:
            print()#showMessage(f"Errore durante il rendering del grafico finale: {e}", title='Errore',
                        #icon=QMessageBox.Critical)
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

            # Rendering del file DOT
            G.format = 'dot'
            dot_file = G.render(directory=matrix_path, filename=filename)
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

        try:
            g = Source.from_file(tred_output_file_path, format='jpg')
            g.render()
            #showMessage("Rendering del grafico completato.")
            # return g (Considera che in una GUI, potresti voler gestire il risultato in modo diverso)
        except Exception as e:
            print()#showMessage(f"Errore durante il rendering del grafico finale: {e}", title='Errore',
                        #icon=QMessageBox.Critical)


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
        G.format = 'dot'
        dot_file = G.render(directory=matrix_path, filename=filename)
        # For MS-Windows, we need to hide the console window.
        if Pyarchinit_OS_Utility.isWindows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        # cmd = ' '.join(['tred', dot_file])
        # dotargs = shlex.split(cmd)
        with open(os.path.join(matrix_path, filename + '_viewtred.dot'), "w") as out, \
                open(os.path.join(matrix_path, 'matrix_error.txt'), "w") as err:
            subprocess.Popen(['tred', dot_file],
                             # shell=True,
                             stdout=out,
                             stderr=err,
                             startupinfo=si if Pyarchinit_OS_Utility.isWindows() else None)
        tred_file = os.path.join(matrix_path, filename + '_viewtred.dot')

        f = Source.from_file(tred_file, format='png')
        f.render()
        g = Source.from_file(tred_file, format='jpg')
        g.render()
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
        # DPI iniziale, verrà ottimizzato automaticamente se necessario
        G.graph_attr['dpi'] = '150'

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

                            with f.subgraph(name='cluster_cont') as temp:
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

            # Rendering del file DOT
            G.format = 'dot'
            dot_file = G.render(directory=matrix_path, filename=filename)
            tred_output_file_path = os.path.join(matrix_path, f"{filename}_viewtred.dot")

            error_file_path = os.path.join(matrix_path, 'matrix_error.txt')
        except Exception as e:
            showMessage(f"Errore durante la creazione del file DOT: {e}", title='Errore', icon=QMessageBox.Critical)
            return

        startupinfo = None
        if Pyarchinit_OS_Utility.isWindows():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        # Sistema intelligente auto-adattivo per DPI
        dpi_levels = ['150', '120', '100', '75', '50']  # DPI decrescenti da provare
        matrix_generated = False
        
        for i, current_dpi in enumerate(dpi_levels):
            try:
                print(f"Tentativo generazione matrice con DPI {current_dpi} ({i+1}/{len(dpi_levels)})...")
                
                # Aggiorna DPI nel grafico
                G.graph_attr['dpi'] = current_dpi
                
                # Rigenera il file DOT con il nuovo DPI
                G.format = 'dot'
                dot_file = G.render(directory=matrix_path, filename=filename, cleanup=True)
                
                # Esegui tred
                with open(tred_output_file_path, "w") as out_file, open(error_file_path, "w") as err_file:
                    subprocess.call(['tred', dot_file], stdout=out_file, stderr=err_file, startupinfo=startupinfo)
                
                # Controlla errori ma non mostrare all'utente se sono solo warning sui cicli
                has_critical_errors = False
                if os.path.getsize(error_file_path) > 0:
                    with open(error_file_path, "r") as err_file:
                        errors = err_file.read().lower()
                        # Solo errori critici, non warning sui cicli
                        if 'error' in errors and 'warning' not in errors:
                            has_critical_errors = True
                            print(f"Errori critici con DPI {current_dpi}: {errors}")
                        else:
                            print(f"Warning tred con DPI {current_dpi} (normale per matrici complesse)")
                
                # Prova il rendering
                if not has_critical_errors:
                    try:
                        g = Source.from_file(tred_output_file_path, format='jpg')
                        g.render()
                        matrix_generated = True
                        print(f"✓ Matrice generata con successo con DPI {current_dpi}")
                        break  # Successo, esci dal loop
                    except Exception as render_error:
                        print(f"Errore rendering con DPI {current_dpi}: {render_error}")
                        continue  # Prova DPI successivo
                        
            except Exception as e:
                print(f"Errore generale con DPI {current_dpi}: {e}")
                continue  # Prova DPI successivo
        
        # Solo se non riusciamo a generare con nessun DPI, mostra errore (solo in console)
        if not matrix_generated:
            print("ERRORE: Impossibile generare la matrice anche con DPI ridotti. Controlla i dati stratigrafici.")
            # Solo per debug critici, non durante l'atlas
            # showMessage(f"Impossibile generare la matrice anche con DPI ridotti. Controlla i dati stratigrafici.", 
            #            title='Errore Matrix', icon=QMessageBox.Warning)
        else:
            # Messaggio di successo solo in console per non interrompere l'atlas
            print(f"✓ Matrice Harris generata con successo! Utilizzato DPI ottimale per le dimensioni dei dati.")
