#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2007-12-01
        copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
        email                : mandoluca at gmail.com
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

import math
import os
import time
import traceback
from builtins import object
from builtins import range
from builtins import str
from builtins import zip
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QProgressBar, QApplication
from qgis.core import *

import psycopg2
from geoalchemy2 import *
from sqlalchemy import and_, or_, asc, desc
from sqlalchemy.engine import create_engine
from sqlalchemy.event import listen
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData

from modules.db.pyarchinit_db_mapper import US, UT, SITE, PERIODIZZAZIONE, POTTERY, TMA, TMA_MATERIALI, \
    STRUTTURA, SCHEDAIND, INVENTARIO_MATERIALI, DETSESSO, DOCUMENTAZIONE, DETETA, MEDIA, \
    MEDIA_THUMB, MEDIATOENTITY, MEDIAVIEW, TOMBA, CAMPIONI, PYARCHINIT_THESAURUS_SIGLE, \
    INVENTARIO_LAPIDEI, PDF_ADMINISTRATOR, PYUS, PYUSM, PYSITO_POINT, PYSITO_POLYGON, PYQUOTE, PYQUOTEUSM, \
    PYUS_NEGATIVE, PYSTRUTTURE, PYREPERTI, PYINDIVIDUI, PYCAMPIONI, PYTOMBA, PYDOCUMENTAZIONE, PYLINEERIFERIMENTO, \
    PYRIPARTIZIONI_SPAZIALI, PYSEZIONI
from modules.db.pyarchinit_db_update import DB_update
from modules.db.pyarchinit_utility import Utility
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility


class Pyarchinit_db_management(object):
    metadata = ''
    engine = ''
    boolean = ''
    
    if os.name == 'posix':
        boolean = 'True'
    elif os.name == 'nt':
        boolean = 'True'
    L = QgsSettings().value("locale/userLocale")[0:2]

    def __init__(self, c):
        self.conn_str = c
        
    
    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)
        
        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')
        
        elif Pyarchinit_OS_Utility.isMac()== True:
            dbapi_conn.load_extension('mod_spatialite.so')
        else:
            dbapi_conn.load_extension('mod_spatialite.so')
        
        # Enable foreign keys for SQLite
        dbapi_conn.execute("PRAGMA foreign_keys=ON")




    def connection(self):
        conn = None
        test = True

        try:
            test_conn = self.conn_str.find("sqlite")
            if test_conn == 0:
                self.engine = create_engine(self.conn_str, echo=eval(self.boolean))
                listen(self.engine, 'connect', self.load_spatialite)
            else:
                self.engine = create_engine(self.conn_str, max_overflow=-1, echo=eval(self.boolean))
            
                
            self.metadata = MetaData(self.engine)
            conn = self.engine.connect()

        except Exception as e:
            error_message = f"Error. Problema nella connessione con il db: {e}\nTraceback: {traceback.format_exc()}"
            QMessageBox.warning(None, "Message", error_message, QMessageBox.Ok)
            test = False
        finally:
            if conn:
                conn.close()

        try:
            db_upd = DB_update(self.conn_str)
            db_upd.update_table()
        except Exception as e:
            error_message = f"Error. problema nell' aggiornamento del db: {e}\nTraceback: {traceback.format_exc()}"
            QMessageBox.warning(None, "Message", error_message, QMessageBox.Ok)
            test = False
            
        # Force creation of TMA tables
        try:
            self.ensure_tma_tables_exist()
        except Exception as e:
            print(f"Error ensuring TMA tables exist: {e}")
            
        return test
    
    def ensure_tma_tables_exist(self):
        """Ensure TMA tables are created if they don't exist"""
        try:
            # Import the table structures to trigger their creation
            from modules.db.structures.Tma_table import Tma_table
            from modules.db.structures.Tma_materiali_table import Tma_materiali_table
            
            # Force metadata creation
            Tma_table.metadata.create_all(self.engine)
            Tma_materiali_table.metadata.create_all(self.engine)
            
        except Exception as e:
            print(f"Error in ensure_tma_tables_exist: {str(e)}")

        # insert statement

    def insert_pottery_values(self, *arg):
        """Istanzia la classe POTTERY da pyarchinit_db_mapper"""
        pottery = POTTERY(arg[0],
                  arg[1],
                  arg[2],
                  arg[3],
                  arg[4],
                  arg[5],
                  arg[6],
                  arg[7],
                  arg[8],
                  arg[9],
                  arg[10],
                  arg[11],
                  arg[12],
                  arg[13],
                  arg[14],
                  arg[15],
                  arg[16],
                  arg[17],
                  arg[18],
                  arg[19],
                  arg[20],
                  arg[21],
                  arg[22],
                  arg[23],
                  arg[24],
                  arg[25],
                  arg[26],
                  arg[27],
                  arg[28],
                  arg[29],
                  arg[30],
                  arg[31])

        return pottery
    def insert_pyus(self, *arg):
        pyus = PYUS(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13])
        return pyus
    def insert_pyusm(self, *arg):
        pyusm = PYUSM(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13])
        return pyusm
    def insert_pysito_point(self, *arg):
        pysito_point = PYSITO_POINT(arg[0],
                arg[1],
                arg[2])
        return pysito_point
    
    
    def insert_pysito_polygon(self, *arg):
        pysito_polygon = PYSITO_POLYGON(arg[0],
                arg[1],
                arg[2])
        return pysito_polygon
        
    def insert_pyquote(self, *arg):
        pyquote = PYQUOTE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10])
        return pyquote    
    def insert_pyquote_usm(self, *arg):
        pyquote_usm = PYQUOTEUSM(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10])
        return pyquote_usm    
    def insert_pyus_negative(self, *arg):
        pyus_negative = PYUS_NEGATIVE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])
        return pyus_negative
    
    def insert_pystrutture(self, *arg):
        pystrutture = PYSTRUTTURE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11])
        return pystrutture
    
    def insert_pyreperti(self, *arg):
        pyreperti = PYREPERTI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4])
        return pyreperti
    
    def insert_pyindividui(self, *arg):
        pyindividui = PYINDIVIDUI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5])
        return pyindividui
    
    def insert_pycampioni(self, *arg):
        pycampioni = PYCAMPIONI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8])
        return pycampioni
    
    def insert_pytomba(self, *arg):
        pytomba = PYTOMBA(arg[0],
                arg[1],
                arg[2],
                arg[3])
        return pytomba
    
    def insert_pydocumentazione(self, *arg):
        pydocumentazione = PYDOCUMENTAZIONE(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])
        return pydocumentazione
    
    def insert_pylineeriferimento(self, *arg):
        pylineeriferimento = PYLINEERIFERIMENTO(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4])
        return pylineeriferimento
    
    def insert_pyripartizioni_spaziali(self, *arg):
        pyripartizioni_spaziali = PYRIPARTIZIONI_SPAZIALI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5])
        return pyripartizioni_spaziali
    
    def insert_pysezioni(self, *arg):
        pysezioni = PYSEZIONI(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7])
        return pysezioni
    
    
    
    def insert_values(self, *arg):
        """Istanzia la classe US da pyarchinit_db_mapper"""

        us = US(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13],
                arg[14],
                arg[15],
                arg[16],
                arg[17],
                arg[18],
                arg[19],
                arg[20],
                arg[21],
                arg[22],
                arg[23],
                arg[24],
                arg[25],
                arg[26],
                arg[27],
                arg[28],
                arg[29],
                arg[30],
                arg[31],
                arg[32],
                arg[33],
                arg[34],
                arg[35],
                arg[36],
                arg[37],
                arg[38],
                arg[39],
                arg[40],
                arg[41],
                arg[42],
                arg[43],
                arg[44],
                arg[45],
                arg[46],
                arg[47],
                arg[48],
                arg[49],
                arg[50],
                arg[51],    # 51 campi aggiunti per archeo 3.0 e allineamento ICCD
                arg[52],
                arg[53],
                arg[54],
                arg[55],
                arg[56],
                arg[57],
                arg[58],
                arg[59],
                arg[60],
                arg[61],
                arg[62],
                arg[63],
                arg[64],
                arg[65],
                arg[66],
                arg[67],
                arg[68],
                arg[69],
                arg[70],
                arg[71],
                arg[72],
                arg[73],
                arg[74],
                arg[75],
                arg[76],
                arg[77],
                arg[78],
                arg[79],
                arg[80],
                arg[81],
                arg[82],
                arg[83],
                arg[84],
                arg[85],
                arg[86],
                arg[87],
                arg[88],
                arg[89],
                arg[90],
                arg[91],
                arg[92],
                arg[93],
                arg[94],
                arg[95],
                arg[96],
                arg[97],
                arg[98],
                arg[99],
                arg[100],
                arg[101],
                arg[102],
                arg[103],
                arg[104],
                arg[105],
                arg[106],
                arg[107],
                arg[108],
                arg[109],
                arg[110],
                arg[111],
                arg[112],
                arg[113],
                arg[114],
                arg[115],
                arg[116],
                )

        return us

    def insert_ut_values(self, *arg):
        """Istanzia la classe UT da pyarchinit_db_mapper"""

        ut = UT(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6],
                arg[7],
                arg[8],
                arg[9],
                arg[10],
                arg[11],
                arg[12],
                arg[13],
                arg[14],
                arg[15],
                arg[16],
                arg[17],
                arg[18],
                arg[19],
                arg[20],
                arg[21],
                arg[22],
                arg[23],
                arg[24],
                arg[25],
                arg[26],
                arg[27],
                arg[28],
                arg[29],
                arg[30],
                arg[31],
                arg[32],
                arg[33],
                arg[34],
                arg[35],
                arg[36],
                arg[37],
                arg[38],
                arg[39],
                arg[40],
                arg[41])

        return ut

    def insert_site_values(self, *arg):
        """Istanzia la classe SITE da pyarchinit_db_mapper"""
        sito = SITE(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9])

        return sito

    def insert_periodizzazione_values(self, *arg):
        """Istanzia la classe Periodizzazione da pyarchinit_db_mapper"""
        periodizzazione = PERIODIZZAZIONE(arg[0],
                                          arg[1],
                                          arg[2],
                                          arg[3],
                                          arg[4],
                                          arg[5],
                                          arg[6],
                                          arg[7],
                                          arg[8])

        return periodizzazione

    def insert_values_reperti(self, *arg):
        """Istanzia la classe Reperti da pyarchinit_db_mapper"""
        inventario_materiali = INVENTARIO_MATERIALI(arg[0],
                                                    arg[1],
                                                    arg[2],
                                                    arg[3],
                                                    arg[4],
                                                    arg[5],
                                                    arg[6],
                                                    arg[7],
                                                    arg[8],
                                                    arg[9],
                                                    arg[10],
                                                    arg[11],
                                                    arg[12],
                                                    arg[13],
                                                    arg[14],
                                                    arg[15],
                                                    arg[16],
                                                    arg[17],
                                                    arg[18],
                                                    arg[19],
                                                    arg[20],
                                                    arg[21],
                                                    arg[22],
                                                    arg[23],
                                                    arg[24],
                                                    arg[25],
                                                    arg[26],
                                                    arg[27],
                                                    arg[28],
                                                    arg[29],
                                                    arg[30],
                                                    arg[31],
                                                    arg[32])

        return inventario_materiali

    def insert_struttura_values(self, *arg):
        """Istanzia la classe Struttura da pyarchinit_db_mapper"""
        struttura = STRUTTURA(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17])

        return struttura

    def insert_values_ind(self, *arg):
        """Istanzia la classe SCHEDAIND da pyarchinit_db_mapper"""
        schedaind = SCHEDAIND(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17],
                              arg[18],
                              arg[19],
                              arg[20],
                              arg[21],
                              arg[22],
                              arg[23])

        return schedaind

    def insert_values_detsesso(self, *arg):
        """Istanzia la classe DETSESSO da pyarchinit_db_mapper"""
        detsesso = DETSESSO(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9],
                            arg[10],
                            arg[11],
                            arg[12],
                            arg[13],
                            arg[14],
                            arg[15],
                            arg[16],
                            arg[17],
                            arg[18],
                            arg[19],
                            arg[20],
                            arg[21],
                            arg[22],
                            arg[23],
                            arg[24],
                            arg[25],
                            arg[26],
                            arg[27],
                            arg[28],
                            arg[29],
                            arg[30],
                            arg[31],
                            arg[32],
                            arg[33],
                            arg[34],
                            arg[35],
                            arg[36],
                            arg[37],
                            arg[38],
                            arg[39],
                            arg[40],
                            arg[41],
                            arg[42],
                            arg[43],
                            arg[44],
                            arg[45],
                            arg[46],
                            arg[47],
                            arg[48],
                            arg[49],
                            arg[50],
                            arg[51],
                            arg[52],
                            arg[53])

        return detsesso

    def insert_values_deteta(self, *arg):
        """Istanzia la classe DETETA da pyarchinit_db_mapper"""
        deteta = DETETA(arg[0],
                        arg[1],
                        arg[2],
                        arg[3],
                        arg[4],
                        arg[5],
                        arg[6],
                        arg[7],
                        arg[8],
                        arg[9],
                        arg[10],
                        arg[11],
                        arg[12],
                        arg[13],
                        arg[14],
                        arg[15],
                        arg[16],
                        arg[17],
                        arg[18],
                        arg[19],
                        arg[20],
                        arg[21],
                        arg[22],
                        arg[23],
                        arg[24],
                        arg[25],
                        arg[26],
                        arg[27],
                        arg[28],
                        arg[29],
                        arg[30],
                        arg[31],
                        arg[32],
                        arg[33],
                        arg[34],
                        arg[35],
                        arg[36],
                        arg[37],
                        arg[38],
                        arg[39],
                        arg[40],
                        arg[41],
                        arg[42],
                        arg[43],
                        arg[44],
                        arg[45],
                        arg[46],
                        arg[47],
                        arg[48],
                        arg[49],
                        arg[50],
                        arg[51],
                        arg[52],
                        arg[53],
                        arg[54],
                        arg[55],
                        arg[56])

        return deteta

    def insert_media_values(self, *arg):
        """Istanzia la classe MEDIA da pyarchinit_db_mapper"""
        media = MEDIA(arg[0],
                      arg[1],
                      arg[2],
                      arg[3],
                      arg[4],
                      arg[5],
                      arg[6])

        return media

    def insert_mediathumb_values(self, *arg):
        """Istanzia la classe MEDIA da pyarchinit_db_mapper"""
        media_thumb = MEDIA_THUMB(arg[0],
                                  arg[1],
                                  arg[2],
                                  arg[3],
                                  arg[4],
                                  arg[5],
                                  arg[6],
                                  arg[7])

        return media_thumb

    def insert_media2entity_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediatoentity = MEDIATOENTITY(arg[0],
                                      arg[1],
                                      arg[2],
                                      arg[3],
                                      arg[4],
                                      arg[5],
                                      arg[6])

        return mediatoentity

    
    def insert_media2entity_view_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediaentity_view= MEDIAVIEW(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])

        return mediaentity_view 
    
    def insert_values_tomba(self, *arg):
        """Istanzia la classe TOMBA da pyarchinit_db_mapper"""

        tomba = TOMBA(arg[0],
                              arg[1],
                              arg[2],
                              arg[3],
                              arg[4],
                              arg[5],
                              arg[6],
                              arg[7],
                              arg[8],
                              arg[9],
                              arg[10],
                              arg[11],
                              arg[12],
                              arg[13],
                              arg[14],
                              arg[15],
                              arg[16],
                              arg[17],
                              arg[18],
                              arg[19],
                              arg[20],
                              arg[21],
                              arg[22],
                              arg[23],
                              arg[24],
                              arg[25],)

        return tomba

    def insert_values_campioni(self, *arg):
        """Istanzia la classe CAMPIONI da pyarchinit_db_mapper"""

        campioni = CAMPIONI(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9])

        return campioni

    def insert_values_thesaurus(self, *arg):
        """Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper"""
        
        # Standard format with all required fields
        if len(arg) == 7:
            # Basic format with descrizione
            thesaurus = PYARCHINIT_THESAURUS_SIGLE(
                arg[0],  # id_thesaurus_sigle
                arg[1],  # nome_tabella
                arg[2],  # sigla
                arg[3],  # sigla_estesa
                arg[4],  # descrizione
                arg[5],  # tipologia_sigla
                arg[6]   # lingua
            )
        elif len(arg) >= 8:
            # Extended format with hierarchy fields
            thesaurus = PYARCHINIT_THESAURUS_SIGLE(
                arg[0],  # id_thesaurus_sigle
                arg[1],  # nome_tabella
                arg[2],  # sigla
                arg[3],  # sigla_estesa
                arg[4],  # descrizione
                arg[5],  # tipologia_sigla
                arg[6],  # lingua
                arg[7] if len(arg) > 7 else 0,  # order_layer
                arg[8] if len(arg) > 8 else None,  # id_parent
                arg[9] if len(arg) > 9 else None,  # parent_sigla
                arg[10] if len(arg) > 10 else 0  # hierarchy_level
            )
        else:
            # Handle legacy format or missing descrizione
            raise ValueError(f"Invalid number of arguments for thesaurus: {len(arg)}. Expected at least 7.")

        return thesaurus

    # def insert_values_archeozoology(self, *arg):
        # """Istanzia la classe ARCHEOZOOLOGY da pyarchinit_db_mapper"""

        # archeozoology = ARCHEOZOOLOGY(arg[0],
                                        # arg[1],
                                        # arg[2],
                                        # arg[3],
                                        # arg[4],
                                        # arg[5],
                                        # arg[6],
                                        # arg[7],
                                        # arg[8],
                                        # arg[9],
                                        # arg[10],
                                        # arg[11],
                                        # arg[12],
                                        # arg[13],
                                        # arg[14],
                                        # arg[15],
                                        # arg[16],
                                        # arg[17],
                                        # arg[18],
                                        # arg[19],
                                        # arg[20],
                                        # arg[21],
                                        # arg[22],
                                        # arg[23],
                                        # arg[24],
                                        # arg[25],
                                        # arg[26],
                                        # arg[27],
                                        # arg[28],
                                        # arg[29],
                                        # arg[30])

        # return archeozoology

    def insert_values_Lapidei(self, *arg):
        """Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper"""

        inventario_lapidei = INVENTARIO_LAPIDEI(arg[0],
                                                arg[1],
                                                arg[2],
                                                arg[3],
                                                arg[4],
                                                arg[5],
                                                arg[6],
                                                arg[7],
                                                arg[8],
                                                arg[9],
                                                arg[10],
                                                arg[11],
                                                arg[12],
                                                arg[13],
                                                arg[14],
                                                arg[15],
                                                arg[16],
                                                arg[17],
                                                arg[18],
                                                arg[19])

        return inventario_lapidei

    def insert_values_documentazione(self, *arg):
        """Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper"""

        documentazione = DOCUMENTAZIONE(arg[0],
                                        arg[1],
                                        arg[2],
                                        arg[3],
                                        arg[4],
                                        arg[5],
                                        arg[6],
                                        arg[7],
                                        arg[8])

        return documentazione

    def insert_pdf_administrator_values(self, *arg):
        """Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper"""
        pdf_administrator = PDF_ADMINISTRATOR(arg[0],
                                              arg[1],
                                              arg[2],
                                              arg[3],
                                              arg[4])

        return pdf_administrator

    def insert_campioni_values(self, *arg):
        """Istanzia la classe CAMPIONI da pyarchinit_db_mapper"""
        campioni = CAMPIONI(arg[0],
                            arg[1],
                            arg[2],
                            arg[3],
                            arg[4],
                            arg[5],
                            arg[6],
                            arg[7],
                            arg[8],
                            arg[9])

        return campioni
        
    def insert_tma_values(self, *arg):
        """Istanzia la classe TMA da pyarchinit_db_mapper"""
        tma = TMA(arg[0],  # id
                  arg[1],  # sito
                  arg[2],  # area
                  arg[3],  # localita
                  arg[4],  # settore
                  arg[5],  # inventario
                  arg[6],  # ogtm
                  arg[7],  # ldct
                  arg[8],  # ldcn
                  arg[9],  # vecchia_collocazione
                  arg[10], # cassetta
                  arg[11], # scan
                  arg[12], # saggio
                  arg[13], # vano_locus
                  arg[14], # dscd
                  arg[15], # dscu
                  arg[16], # rcgd
                  arg[17], # rcgz
                  arg[18], # aint
                  arg[19], # aind
                  arg[20], # dtzg
                  arg[21], # deso
                  arg[22], # nsc
                  arg[23], # ftap
                  arg[24], # ftan
                  arg[25], # drat
                  arg[26], # dran
                  arg[27], # draa
                  arg[28], # created_at
                  arg[29], # updated_at
                  arg[30], # created_by
                  arg[31]) # updated_by

        return tma

    def insert_tma_materiali_values(self, *arg):
        """Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper"""
        from modules.db.entities.TMA_MATERIALI import TMA_MATERIALI
        tma_materiali = TMA_MATERIALI(arg[0],  # id
                                     arg[1],  # id_tma
                                     arg[2],  # madi
                                     arg[3],  # macc
                                     arg[4],  # macl
                                     arg[5],  # macp
                                     arg[6],  # macd
                                     arg[7],  # cronologia_mac
                                     arg[8],  # macq
                                     arg[9],  # peso
                                     arg[10], # created_at
                                     arg[11], # updated_at
                                     arg[12], # created_by
                                     arg[13]) # updated_by

        return tma_materiali

    def insert_media_to_entity_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper"""
        mediatoentity = MEDIATOENTITY(arg[0],  # id_mediaToEntity
                                      arg[1],  # id_entity
                                      arg[2],  # entity_type
                                      arg[3],  # table_name
                                      arg[4],  # id_media
                                      arg[5],  # filepath
                                      arg[6]   # media_name
                                      )
        return mediatoentity

    ##  def insert_relationship_check_values(self, *arg):
    ##      """Istanzia la classe RELATIONSHIP_CHECK da pyarchinit_db_mapper"""
    ##      relationship_check = RELATIONSHIP_CHECK(arg[0],
    ##                                              arg[1],
    ##                                              arg[2],
    ##                                              arg[3],
    ##                                              arg[4],
    ##                                              arg[5],
    ##                                              arg[6],
    ##                                              arg[7],
    ##                                              arg[8],
    ##                                              arg[9])
    ##
    ##      return relationship_check


    def execute_sql_create_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_create_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()
        self.engine.raw_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.engine.text(stringa).execute()

    def execute_sql_create_spatialite_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_create_spatialite_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

    def execute_sql_create_layers(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'pyarchinit_layers_postgis.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

        # query statement

    def query(self, n):
        class_name = eval(n)
        # engine = self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query = session.query(class_name)
        res = query.all()
        session.close()
        return res

    def query_limit_offset(self, table_name, filter_text=None, limit=None, offset=None):
        # Inizializza la sessione
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Ottieni la tabella
        table = Table(table_name, MetaData(bind=self.engine), autoload_with=self.engine)

        # Costruisci la query
        query = select(table)

        # Se c'è un testo da filtrare
        if filter_text:
            query = query.where(table.c.media_filename.ilike(f"%{filter_text}%")).order_by(table.c.media_filename)

        # Se c'è un limite e un offset
        if limit is not None and offset is not None:
            query = query.limit(limit).offset(offset)

        # Esegui la query e ottieni i risultati
        records = session.execute(query).fetchall()

        # Chiudi la sessione
        session.close()

        return records

    def count_total_images(self, table_name, filter_text=None):
        # Inizializza la sessione
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Ottieni la tabella
        table = Table(table_name, MetaData(bind=self.engine), autoload_with=self.engine)

        # Costruisci la query per ottenere il conteggio totale delle immagini
        query = select(func.count('*')).select_from(table)

        # Se c'è un testo da filtrare
        if filter_text:
            query = query.where(table.c.title.ilike(f"%{filter_text}%"))

        # Esegui la query e ottieni il conteggio
        total_images = session.execute(query).scalar()

        # Chiudi la sessione
        session.close()

        return total_images

    def query_bool_us(self, params, table_class):

        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Start with an empty list of conditions
        conditions = []

        # Iterate over the parameters to create conditions
        for key, value in params.items():
            column = getattr(table_class, key)
            if isinstance(value, str):
                conditions.append(column.like(value))
            else:
                conditions.append(column == value)

        # Construct the query with the conditions
        query = session.query(table_class).filter(and_(*conditions))

        # Execute the query and fetch all results
        res = query.all()

        # Close the session
        session.close()

        return res

    def query_bool_like(self, params, table, join_operator='or'):

        meta = MetaData(bind=self.engine)
        table_to_query = Table(table, meta, autoload_with=self.engine)

        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())
        sito_filter = None  # This will hold the 'sito' filter
        filters = []
        for sing_couple_n in range(len(list_keys_values)):
            key, value = list_keys_values[sing_couple_n]
            column = getattr(table_to_query.c, key)
            if key == "settore" or key == "struttura" or key == "quad_par" or key == "ambient" or key == "saggio" or key == "area":
                value_list = value.split(", ")
                filters.append(or_(*[column.ilike(f'%{field_value}%') for field_value in value_list]))
            else:
                if key == 'sito':
                    sito_filter = column.ilike(f'%{value}%')
                else:
                    filters.append(column.ilike(f'%{value}%'))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        # choose join_operator based on given argument


        join_operator_func = and_ if join_operator == 'and' else or_
        # Add 'sito' filter
        if sito_filter is not None:
            filters.insert(0, sito_filter)

        query = session.query(table_to_query).filter(and_(*[filters.pop(0)]), join_operator_func(*filters))
        # Convert query to a SQL string
        # sql_query_str = str(query.statement.compile(dialect=self.engine.dialect))
        #
        # with open("C:\\Users\\enzoc\\Desktop\\test_import.txt", "w") as t:
        #     t.write(str(sql_query_str))

        # Execute query
        res = query.all()

        session.close()
        return res

    def query_bool_postgres(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        conditions = []
        query_params = {}

        for key, value in params.items():
            if isinstance(value, str):
                conditions.append(text(f"{table}.{key} = :{key}"))
            else:
                conditions.append(text(f"{table}.{key} = :{key}"))
            query_params[key] = value

        try:
            Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
            with Session() as session:
                query = session.query(table).filter(and_(*conditions))
                res = query.params(**query_params).all()
            return res
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            return []
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    def query_bool(self, params, table_class_name):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)
        
        # Handle thesaurus table name compatibility
        if table_class_name == 'PYARCHINIT_THESAURUS_SIGLE' and 'nome_tabella' in params:
            # Import compatibility helper
            try:
                from modules.utility.pyarchinit_thesaurus_compatibility import get_compatible_names
                
                nome_tabella = params['nome_tabella'].strip("'")
                compatible_names = get_compatible_names(nome_tabella)
                
                # If we have multiple compatible names, we need to query for all of them
                if len(compatible_names) > 1:
                    # Create a session
                    Session = sessionmaker(bind=self.engine)
                    session = Session()
                    
                    # Build query with OR condition for all compatible names
                    all_results = []
                    for compat_name in compatible_names:
                        temp_params = params.copy()
                        temp_params['nome_tabella'] = f"'{compat_name}'"
                        
                        conditions = []
                        for key, value in temp_params.items():
                            column = getattr(PYARCHINIT_THESAURUS_SIGLE, key)
                            if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
                                value = value.strip("'")
                            conditions.append(column == value)
                        
                        query = session.query(PYARCHINIT_THESAURUS_SIGLE).filter(and_(*conditions))
                        results = query.all()
                        all_results.extend(results)
                    
                    session.close()
                    # Remove duplicates based on sigla
                    seen = set()
                    unique_results = []
                    for result in all_results:
                        if result.sigla not in seen:
                            seen.add(result.sigla)
                            unique_results.append(result)
                    
                    return unique_results
                    
            except ImportError:
                # If compatibility module not available, continue with normal flow
                pass
        
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        # Mapping of table class names to class references
        table_classes = {
            'US':US, 'UT': UT, 'SITE': SITE, 'PERIODIZZAZIONE': PERIODIZZAZIONE, 'POTTERY': POTTERY,
            'STRUTTURA': STRUTTURA, 'SCHEDAIND': SCHEDAIND, 'INVENTARIO_MATERIALI': INVENTARIO_MATERIALI,
            'DETSESSO': DETSESSO, 'DOCUMENTAZIONE': DOCUMENTAZIONE, 'DETETA': DETETA, 'MEDIA': MEDIA,
            'MEDIA_THUMB': MEDIA_THUMB, 'MEDIATOENTITY': MEDIATOENTITY, 'MEDIAVIEW': MEDIAVIEW,
            'TOMBA': TOMBA, 'CAMPIONI': CAMPIONI, 'PYARCHINIT_THESAURUS_SIGLE': PYARCHINIT_THESAURUS_SIGLE,
            'INVENTARIO_LAPIDEI': INVENTARIO_LAPIDEI, 'PDF_ADMINISTRATOR': PDF_ADMINISTRATOR,
            'PYUS': PYUS, 'PYUSM': PYUSM, 'PYSITO_POINT': PYSITO_POINT, 'PYSITO_POLYGON': PYSITO_POLYGON,
            'PYQUOTE': PYQUOTE, 'PYQUOTEUSM': PYQUOTEUSM, 'PYUS_NEGATIVE': PYUS_NEGATIVE,
            'PYSTRUTTURE': PYSTRUTTURE, 'PYREPERTI': PYREPERTI, 'PYINDIVIDUI': PYINDIVIDUI,
            'PYCAMPIONI': PYCAMPIONI, 'PYTOMBA': PYTOMBA, 'PYDOCUMENTAZIONE': PYDOCUMENTAZIONE,
            'PYLINEERIFERIMENTO': PYLINEERIFERIMENTO, 'PYRIPARTIZIONI_SPAZIALI': PYRIPARTIZIONI_SPAZIALI,
            'PYSEZIONI': PYSEZIONI, 'TMA': TMA, 'TMA_MATERIALI': TMA_MATERIALI
            # Add other table class mappings here
        }
        
        # Get the table class from the mapping
        table_class = table_classes.get(table_class_name)
        if not table_class:
            raise ValueError(f"No table class found for {table_class_name}")
        
        # Start with an empty list of conditions
        conditions = []
        
        # Iterate over the parameters to create conditions
        for key, value in params.items():
            column = getattr(table_class, key)
            # Clean the value if it's a string with quotes
            if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
                value = value.strip("'")
            conditions.append(column == value)
        
        # Construct the query with the conditions
        query = session.query(table_class).filter(and_(*conditions))
        
        # Execute the query and fetch all results
        res = query.all()
        
        # Close the session
        session.close()
        
        return res

    def select_mediapath_from_id(self, media_id):
        sql_query = "SELECT filepath FROM media_table WHERE id_media = ?"
        params = (media_id,)
        res = self.engine.execute(sql_query, params)
        row = res.fetchone()
        return row[0] if row else None


    def query_all_us(self, table_class_str, column_name='us'):
        """
        Retrieve all records from a specified table and return values of a specific column.

        :param table_class_str: The name of the table class as a string.
        :param column_name: The name of the column to retrieve values from.
        :return: A list of values from the specified column of all records.
        """
        # Reflect the table from the database
        table = Table(table_class_str, self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Query all records from the table
            query = session.query(table).all()
            # Extract the 'us' column values
            us_values = [getattr(record, column_name, None) for record in query]
            return us_values
        except Exception as e:
            print(f"An error occurred while querying all records: {e}")
            return []
        finally:
            # Close the session
            session.close()
    def query_all(self, table_class_str):
        """
        Retrieve all records from a specified table.

        :param table_class_str: The name of the table class as a string.
        :return: A list of all records from the specified table.
        """
        # Reflect the table from the database
        table = Table(table_class_str, self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Query all records from the table
            query = session.query(table).all()
            return query
        except Exception as e:
            print(f"An error occurred while querying all records: {e}")
            return []
        finally:
            # Close the session
            session.close()
    
    def query_bool_special(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())

        field_value_string = ""

        for sing_couple_n in range(len(list_keys_values)):
            if sing_couple_n == 0:
                if type(list_keys_values[sing_couple_n][1]) != "<type 'str'>":
                    field_value_string = table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = table + ".%s == u%s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
            else:
                if type(list_keys_values[sing_couple_n][1]) == "<type 'str'>":
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])

                    # field_value_string = ", ".join([table + ".%s == u%s" % (k, v) for k, v in params.items()])

        """
        Per poter utilizzare l'operatore LIKE è necessario fare una iterazione attraverso il dizionario per discriminare tra
        stringhe e numeri
        #field_value_string = ", ".join([table + ".%s.like(%s)" % (k, v) for k, v in params.items()])
        """
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"
        res = eval(query_str)

        '''
        t = open("/test_import.txt", "w")
        t.write(str(query_str))
        t.close()
        '''
        session.close()
        return res
    def query_operator(self, params, table):
        u = Utility()
        #params = u.remove_empty_items_fr_dict(params)
        field_value_string = ''
        for i in params:
            if field_value_string == '':
                field_value_string = '%s.%s %s %s' % (table, i[0], i[1], i[2])
            else:
                field_value_string = field_value_string + ', %s.%s %s %s' % (table, i[0], i[1], i[2])

        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"

        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_str)

    def query_distinct(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s.%s==%s' % (table, i[0], i[1])
            else:
                query_string = query_string + ',%s.%s==%s' % (table, i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s.%s' % (table, i)
            else:
                distinct_string = distinct_string + ',%s.%s' % (table, i)

        query_cmd = "session.query(" + distinct_string + ").filter(and_(" + query_string + ")).distinct().order_by(" + distinct_string + ")"
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_cmd)

    def query_distinct_sql(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s=%s' % (i[0], i[1])
            else:
                query_string = query_string + ' AND %s=%s' % (i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s' % (i)
            else:
                distinct_string = distinct_string + ',%s' % (i)

        query_cmd = "SELECT DISTINCT " + distinct_string + " FROM " + table + ' WHERE ' + query_string
        # self.connection()
        res = self.engine.execute(query_cmd)
        return res

    # count distinct "name" values

    # session statement
    def insert_data_session(self, data):
        Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        session = Session()
        session.add(data)
        # Log per debug
        try:
            session.commit()
            print(f"DEBUG: Record committed successfully - Type: {type(data).__name__}")
        except Exception as e:
            session.rollback()
            print(f"DEBUG: Commit failed - Error: {str(e)}")
            raise
        session.close()
    def insert_data_conflict(self, data):
        Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        session = Session()
        session.begin_nested()
        session.merge(data)
       
        session.commit()
        
        session.close()
    def update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list):
        """
        Receives 5 values then putted in a list. The values must be passed
        in this order: table name->string, column_name_where->list containin'
        one value
        ('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
        self.set_update = arg
        #self.connection()
        table = Table(self.set_update[0], self.metadata, autoload=True)
        changes_dict= {}
        u = Utility()
        set_update_4 = u.deunicode_list(self.set_update[4])

        u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

        f = open("test_update.txt", "w")
        f.write(str(self.set_update))
        f.close()

        exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                          self.set_update[1],
                                         " == '",
                                         self.set_update[2][0],
                                         "').execute(",
                                         changes_dict ,")")

        #session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})
        """

        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id_list = value_id_list
        self.columns_name_list = columns_name_list
        self.values_update_list = values_update_list

        changes_dict = {}
        u = Utility()
        update_value_list = u.deunicode_list(self.values_update_list)

        column_list = []
        for field in self.columns_name_list:
            column_str = ('%s.%s') % (table_class_str, field)
            column_list.append(column_str)

        u.add_item_to_dict(changes_dict, list(zip(self.columns_name_list, update_value_list)))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        # session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

        # Ensure the ID value is properly typed
        id_value = self.value_id_list[0]
        # If it's a numeric ID field and the value is a string, convert to int
        if self.id_table_str.lower() in ['id', 'id_tma', 'id_us', 'id_site', 'id_invmat', 'id_media']:
            try:
                id_value = int(id_value)
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails
        
        session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
        self.table_class_str, self.table_class_str, self.id_table_str, id_value, changes_dict)

        
        eval(session_exec_str)
        session.close()

    def update_tomba_dating_from_periodizzazione(self, site_name):
        # Reflect the tables from the database
        tomba_table = Table('tomba_table', self.metadata, autoload_with=self.engine)
        periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Start a transaction
            with session.begin():
                # Select records from tomba_table for the specified site
                tomba_records = session.query(tomba_table).filter_by(sito=site_name).all()

                updates_made = 0
                for tomba_record in tomba_records:
                    # Skip records with empty 'periodo' or 'fase'
                    if not tomba_record.periodo_iniziale or not tomba_record.fase_iniziale:
                        continue

                    # Find the corresponding periodizzazione records for the specific site
                    periodizzazione_iniziale = session.query(periodizzazione_table). \
                        filter_by(sito=site_name, periodo=tomba_record.periodo_iniziale,
                                  fase=tomba_record.fase_iniziale).first()

                    periodizzazione_finale = None
                    if bool(tomba_record.periodo_finale):
                        periodizzazione_finale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=tomba_record.periodo_finale,
                                      fase=tomba_record.fase_finale).first()

                    # Concatenate the 'datazione_estesa' values if both are present
                    datazione_string = ""
                    if periodizzazione_iniziale and periodizzazione_finale:
                        datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
                    elif periodizzazione_iniziale:
                        datazione_string = periodizzazione_iniziale.datazione_estesa

                    if periodizzazione_iniziale or periodizzazione_finale:
                        # Check if the current 'Dating' value is different from the new value
                        current_dating = getattr(tomba_record, 'datazione_estesa', None)
                        if datazione_string and current_dating != datazione_string:
                            # Update the 'Dating' field in tomba_table
                            session.query(tomba_table). \
                                filter_by(id_tomba=tomba_record.id_tomba). \
                                update({'datazione_estesa': datazione_string}, synchronize_session=False)
                            updates_made += 1

                # Print the number of updates made
                print(
                    f"'Dating' fields for tombs in site '{site_name}' have been updated successfully. Total updates made: {updates_made}")

            # Commit the changes
            session.commit()
            return updates_made  # Return the count of updates made
        except Exception as e:
            # Rollback the transaction on error
            session.rollback()
            QMessageBox.warning(None, 'Error',
                                f"An error occurred while updating 'Dating' for tombs in site '{site_name}': {e}")
            raise e  # Re-raise the exception to be handled by the calling function
        finally:
            # Close the session
            session.close()

    # def update_us_dating_from_periodizzazione(self):
    #     # Reflect the tables from the database
    #     us_table = Table('us_table', self.metadata, autoload_with=self.engine)
    #     periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)
    #
    #     # Create a session
    #     Session = sessionmaker(bind=self.engine)
    #     session = Session()
    #
    #     try:
    #         # Start a transaction
    #         with session.begin():
    #             # Select all records from us_table
    #             us_records = session.query(us_table).all()
    #
    #             updates_made = 0
    #             for us_record in us_records:
    #                 periodizzazione_iniziale, periodizzazione_finale = None, None
    #
    #                 if us_record.periodo_iniziale and us_record.fase_iniziale:
    #                     periodizzazione_iniziale = session.query(periodizzazione_table). \
    #                         filter_by(periodo=us_record.periodo_iniziale, fase=us_record.fase_iniziale).first()
    #
    #                 if not periodizzazione_iniziale:
    #                     # Update the 'Dating' field in us_table to None if periodizzazione_iniziale does not exist
    #                     session.query(us_table). \
    #                         filter_by(id_us=us_record.id_us). \
    #                         update({'datazione': None}, synchronize_session=False)
    #                     updates_made += 1
    #                     continue
    #
    #                 if us_record.periodo_finale and us_record.fase_finale:
    #                     periodizzazione_finale = session.query(periodizzazione_table). \
    #                         filter_by(periodo=us_record.periodo_finale, fase=us_record.fase_finale).first()
    #
    #                 datazione_string = ""
    #                 if periodizzazione_iniziale and periodizzazione_finale:
    #                     datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
    #                 elif periodizzazione_iniziale:
    #                     datazione_string = periodizzazione_iniziale.datazione_estesa
    #
    #                 current_dating = getattr(us_record, 'datazione', None)
    #                 if datazione_string != current_dating:
    #                     # Update the 'Dating' field in us_table
    #                     session.query(us_table). \
    #                         filter_by(id_us=us_record.id_us). \
    #                         update({'datazione': datazione_string}, synchronize_session=False)
    #                     updates_made += 1
    #
    #             # Print the number of updates made
    #             print(f"All 'Dating' fields have been updated successfully. Total updates made: {updates_made}")
    #
    #         session.commit()
    #         return updates_made  # Return the count of updates made
    #     except Exception as e:
    #         # Rollback the transaction in case of error
    #         session.rollback()
    #         QMessageBox.warning(None, 'ok', f"An error occurred while updating 'Dating': {e}")
    #         raise e  # Re-raise the exception
    #     finally:
    #         # Close the session
    #         session.close()

    def update_us_dating_from_periodizzazione(self, site_name):
        # Reflect the tables from the database
        us_table = Table('us_table', self.metadata, autoload_with=self.engine)
        periodizzazione_table = Table('periodizzazione_table', self.metadata, autoload_with=self.engine)

        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Start a transaction
            with session.begin():
                # Select only records from the specified site
                us_records = session.query(us_table).filter_by(sito=site_name).all()

                updates_made = 0
                for us_record in us_records:
                    periodizzazione_iniziale, periodizzazione_finale = None, None

                    if us_record.periodo_iniziale and us_record.fase_iniziale:
                        periodizzazione_iniziale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=us_record.periodo_iniziale,
                                      fase=us_record.fase_iniziale).first()

                    if not periodizzazione_iniziale:
                        # Update the 'Dating' field in us_table to None if periodizzazione_iniziale does not exist
                        session.query(us_table). \
                            filter_by(id_us=us_record.id_us). \
                            update({'datazione': None}, synchronize_session=False)
                        updates_made += 1
                        continue

                    if us_record.periodo_finale and us_record.fase_finale:
                        periodizzazione_finale = session.query(periodizzazione_table). \
                            filter_by(sito=site_name, periodo=us_record.periodo_finale,
                                      fase=us_record.fase_finale).first()

                    datazione_string = ""
                    if periodizzazione_iniziale and periodizzazione_finale:
                        datazione_string = f"{periodizzazione_iniziale.datazione_estesa}/{periodizzazione_finale.datazione_estesa}"
                    elif periodizzazione_iniziale:
                        datazione_string = periodizzazione_iniziale.datazione_estesa

                    current_dating = getattr(us_record, 'datazione', None)
                    if datazione_string != current_dating:
                        # Update the 'Dating' field in us_table
                        session.query(us_table). \
                            filter_by(id_us=us_record.id_us). \
                            update({'datazione': datazione_string}, synchronize_session=False)
                        updates_made += 1

                # Print the number of updates made
                print(
                    f"'Dating' fields for site '{site_name}' have been updated successfully. Total updates made: {updates_made}")

            session.commit()
            return updates_made  # Return the count of updates made
        except Exception as e:
            # Rollback the transaction in case of error
            session.rollback()
            QMessageBox.warning(None, 'Error', f"An error occurred while updating 'Dating' for site '{site_name}': {e}")
            raise e  # Re-raise the exception
        finally:
            # Close the session
            session.close()

    def update_find_check(self, table_class_str, id_table_str, value_id, find_check_value):
        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id = value_id
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).filter(%s.%s == %s)).update(values = {"find_check": %d})' % (
        self.table_class_str, self.table_class_str, self.id_table_str, self.value_id, find_check_value)

        eval(session_exec_str)
        session.close()
    def empty_find_check(self, table_class_str, find_check_value):
        self.table_class_str = table_class_str
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).update(values = {"find_check": %d})' % (self.table_class_str, 0)

        eval(session_exec_str)
        session.close()
    def delete_one_record(self, tn, id_col, id_rec):
        
        self.table_name = tn
        self.id_column = id_col
        self.id_rec = id_rec
        # self.connection()
        table = Table(self.table_name, self.metadata, autoload=True)
        exec_str = ('%s%s%s%d%s') % ('table.delete(table.c.', self.id_column, ' == ', self.id_rec, ').execute()')

        eval(exec_str)
    
    def delete_record_by_field(self, table_name, field_name, field_value):
        """Delete records from a table where field matches value"""
        try:
            Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
            session = Session()
            
            # Map table names to entity classes
            table_classes = {
                'TMA_MATERIALI': TMA_MATERIALI
            }
            
            if table_name in table_classes:
                entity_class = table_classes[table_name]
                # Build the query dynamically
                query = session.query(entity_class).filter(getattr(entity_class, field_name) == field_value)
                records_deleted = query.count()
                query.delete()
                session.close()
                return records_deleted
            else:
                # For tables without entity class, use raw SQL
                # Get the correct table name
                actual_table_name = 'tma_materiali_ripetibili' if table_name == 'TMA_MATERIALI' else table_name.lower()
                
                # Always use raw SQL for tma_materiali_ripetibili to avoid foreign key issues
                from sqlalchemy import text
                sql = text(f"DELETE FROM {actual_table_name} WHERE {field_name} = :field_value")
                with self.engine.begin() as conn:
                    result = conn.execute(sql, {"field_value": field_value})
                return result.rowcount
                
        except Exception as e:
            if 'session' in locals():
                session.close()
            raise Exception(f"Error deleting records: {str(e)}")
        
    def max_num_id(self, tc, f):
        self.table_class = tc
        self.field_id = f

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        exec_str = "session.query(func.max({}.{}))".format(self.table_class, self.field_id)
        max_id_func = eval(exec_str)
        res_all = max_id_func.all()
        res_max_num_id = res_all[0][0]
        session.close()
        if not res_max_num_id:
            return 0
        else:
            return int(res_max_num_id)


    def dir_query(self):
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        # session.query(SITE).filter(SITE.id_sito == '1').update(values = {SITE.sito:"updatetest"})
        # return session.query(SITE).filter(and_(SITE.id_sito == 1)).all()
        # return os.environ['HOME']

        session.close()# managements utilities
        
    def fields_list(self, t, s=''):
        """return the list of columns in a table. If s is set a int,
        return only one column"""
        self.table_name = t
        self.sing_column = s
        table = Table(self.table_name, self.metadata, autoload=True)

        if not str(s):
            return [c.name for c in table.columns]
        else:
            return [c.name for c in table.columns][int(s)]

    def query_in_idus(self, id_list):
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res = session.query(US).filter(US.id_us.in_(id_list)).all()

        session.close()

        return res

    def query_sort(self, id_list, op, to, tc, idn):
        self.order_params = op
        self.type_order = to
        self.table_class = tc
        self.id_name = idn



        # Mappa delle classi
        class_map = {
            'US': US,

            'SITE': SITE,
            'PERIODIZZAZIONE': PERIODIZZAZIONE,
            'INVENTARIO_MATERIALI': INVENTARIO_MATERIALI,
            'STRUTTURA': STRUTTURA,
            'TOMBA': TOMBA,
            'SCHEDAIND': SCHEDAIND,
            'DETSESSO': DETSESSO,
            'DETETA': DETETA,
            'POTTERY': POTTERY,
            'CAMPIONI': CAMPIONI,
            'TMA': TMA,
            'DOCUMENTAZIONE': DOCUMENTAZIONE,
            'PYARCHINIT_THESAURUS_SIGLE': PYARCHINIT_THESAURUS_SIGLE
        }

        # Ottieni la classe corretta
        table_class_obj = class_map.get(self.table_class)
        if not table_class_obj:
            raise ValueError(f"Classe {self.table_class} non supportata")

        # Costruisci la lista dei parametri di ordinamento
        order_by_list = []

        for param in self.order_params:
            # Ottieni l'attributo della colonna
            column_attr = getattr(table_class_obj, param)

            # Applica la funzione di ordinamento appropriata
            if self.type_order.lower() == 'asc':
                order_by_list.append(asc(column_attr))
            elif self.type_order.lower() == 'desc':
                order_by_list.append(desc(column_attr))
            else:
                order_by_list.append(asc(column_attr))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        try:
            # Costruisci ed esegui la query
            id_column = getattr(table_class_obj, self.id_name)

            query = session.query(table_class_obj).filter(
                id_column.in_(id_list)
            ).order_by(*order_by_list)

            result = query.all()

            return result

        except Exception as e:
            print(f"Errore in query_sort: {str(e)}")
            raise
        finally:
            session.close()


    def run(self, stmt):
        rs = stmt.execute()
        res_list = []
        for row in rs:
            res_list.append(row[0])
        #session.close()
        return res_list

    def update_for(self):
        """
        table = Table('us_table_toimp', self.metadata, autoload=True)
        s = table.select(table.c.id_us > 0)
        res_list = self.run(s)
        cont = 11900
        for i in res_list:
            self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
            cont = cont+1
        """
        table = Table('inventario_materiali_table_toimp', self.metadata, autoload=True)
        s = table.select(table.c.id_invmat > 0)
        res_list = self.run(s)
        cont = 900
        for i in res_list:
            self.update('INVENTARIO_MATERIALI_TOIMP', 'id_invmat', [i], ['id_invmat'], [cont])
            cont = cont + 1

    def group_by(self, tn, fn, CD):
        """Group by the values by table name - string, field name - string, table class DB from mapper - string"""
        self.table_name = tn
        self.field_name = fn
        self.table_class = CD

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        s = eval('select([{0}.{1}]).group_by({0}.{1})'.format(self.table_class, self.field_name))
        session.close()
        return self.engine.execute(s).fetchall()

    def query_where_text(self, c, v):
        self.c = c
        self.v = v
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        string = ('%s%s%s%s%s') % ('session.query(PERIODIZZAZIONE).filter_by(', self.c, "='", self.v, "')")

        res = eval(string)
        session.close()
        return res

    def update_cont_per(self, s):
        self.sito = s



        # Lista per raccogliere tutti gli errori
        errori = []
        avvisi = []

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        try:
            # Otteniamo la query
            string = ('%s%s%s%s%s') % ('session.query(US).filter_by(', 'sito', "='", str(self.sito), "')")
            query_us = eval(string)

            # Convertiamo la query in lista per poter usare len()
            lista_us = list(query_us)
            total_records = len(lista_us)

            if total_records == 0:
                # Se non ci sono record, mostra un messaggio e termina
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.information(None, "Informazione", "Nessun record da elaborare", QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "Information", "No records to process", QMessageBox.Ok)
                return

            # Creiamo una progress bar
            progress = QProgressBar()
            progress.setWindowTitle("Aggiornamento Continuità Periodi")
            progress.setGeometry(300, 300, 400, 40)

            # Utilizziamo la classe Qt di QGIS
            try:
                progress.setWindowModality(Qt.WindowModal)
                progress.setAlignment(Qt.AlignCenter)
            except AttributeError:
                pass

            progress.setMinimum(0)
            progress.setMaximum(total_records)
            progress.setValue(0)
            progress.show()
            QApplication.processEvents()

            # Contatore per tenere traccia dell'avanzamento
            count = 0
            last_update_time = time.time()

            # Procediamo con l'elaborazione
            for i in lista_us:
                # Incrementiamo il contatore
                count += 1

                # Aggiorniamo la progress bar ogni 10 record o ogni secondo
                current_time = time.time()
                if count % 10 == 0 or (current_time - last_update_time) >= 1.0:
                    progress.setValue(count)
                    percentage = int((count / total_records) * 100)
                    progress.setFormat(f"Elaborazione record {count} di {total_records} ({percentage}%)")
                    QApplication.processEvents()
                    last_update_time = current_time

                try:
                    # Logica originale di elaborazione record
                    if not i.periodo_finale and i.periodo_iniziale:
                        periodiz = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': i.periodo_iniziale,
                             'fase': "'" + str(i.fase_iniziale) + "'"},
                            'PERIODIZZAZIONE')
                        if periodiz and len(periodiz) > 0:
                            self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [periodiz[0].cont_per])
                        else:
                            errori.append(f"US {i.us}: Nessun dato di periodizzazione trovato")

                    elif not i.periodo_iniziale:
                        continue

                    elif i.periodo_finale and i.periodo_iniziale:
                        cod_cont_iniz_temp = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_iniziale),
                             'fase': int(i.fase_iniziale)}, 'PERIODIZZAZIONE')

                        cod_cont_fin_temp = self.query_bool(
                            {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_finale),
                             'fase': int(i.fase_finale)},
                            'PERIODIZZAZIONE')

                        if not cod_cont_iniz_temp or not cod_cont_fin_temp:
                            errori.append(f"US {i.us}: Dati di periodizzazione mancanti")
                            continue

                        cod_cont_iniz = cod_cont_iniz_temp[0].cont_per
                        cod_cont_fin = cod_cont_fin_temp[0].cont_per

                        # Controllo che i valori siano numeri
                        try:
                            start_val = int(cod_cont_iniz)
                            end_val = int(cod_cont_fin)
                        except (ValueError, TypeError):
                            errori.append(
                                f"US {i.us}: Errore di conversione - cod_cont_iniz: {cod_cont_iniz}, cod_cont_fin: {cod_cont_fin}")

                            # Se non sono numeri, usiamo i valori originali senza calcolare range
                            if cod_cont_iniz != cod_cont_fin:
                                cod_cont_var_txt = f"{cod_cont_iniz}/{cod_cont_fin}"
                            else:
                                cod_cont_var_txt = str(cod_cont_iniz)
                            self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
                            continue

                        # Se start_val > end_val, invertiamo i valori per evitare loop infiniti
                        if start_val > end_val:
                            #avvisi.append(
                               # f"US {i.us}: Valore iniziale ({start_val}) maggiore del finale ({end_val}). Inversione effettuata.")
                            start_val, end_val = end_val, start_val

                        # Generiamo la sequenza completa di valori
                        if start_val == end_val:
                            cod_cont_var_txt = str(start_val)
                        else:
                            values = list(range(start_val, end_val + 1))
                            cod_cont_var_txt = "/".join(str(v) for v in values)

                        self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])

                except Exception as e:
                    errori.append(f"US {i.us}: {str(e)}")
                    continue

            # Al termine dell'elaborazione, aggiorniamo la progress bar
            progress.setValue(total_records)
            progress.setFormat("Elaborazione completata (100%)")
            QApplication.processEvents()

            # Chiudiamo la progress bar
            progress.close()

            # Mostriamo un riepilogo degli errori/avvisi
            if errori:
                error_text = ""
                if errori:
                    error_text += f"ERRORI ({len(errori)}):\n" + "\n".join(errori) + "\n\n"
                #if avvisi:
                    #error_text += f"AVVISI ({len(avvisi)}):\n" + "\n".join(avvisi)

                # Creiamo una finestra di dialogo per mostrare tutti gli errori
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.warning(None, "Completato con errori",
                                        f"Elaborazione completata con {len(errori)} errori.\n\n{error_text}",
                                        QMessageBox.Ok)
                else:
                    QMessageBox.warning(None, "Completed with errors/warnings",
                                        f"Processing completed with {len(errori)} errors.\n\n{error_text}",
                                        QMessageBox.Ok)
            else:
                # Nessun errore
                if hasattr(self, 'L') and self.L == 'it':
                    QMessageBox.information(None, "Completato",
                                            f"Elaborazione completata con successo. {count} record aggiornati.",
                                            QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "Completed",
                                            f"Processing completed successfully. {count} records updated.",
                                            QMessageBox.Ok)

        except Exception as e:
            # Gestiamo eccezioni generali
            error_msg = f"Errore durante l'aggiornamento: {str(e)}"
            print(error_msg)
            if 'progress' in locals() and progress:
                progress.close()
            QMessageBox.critical(None, "Errore", error_msg, QMessageBox.Ok)

        finally:
            # Assicuriamoci che la sessione venga chiusa
            if 'session' in locals():
                session.close()

    # def update_cont_per(self, s):
    #     '''
    #     Esegue l'operazione per aggiornare la continuità dei periodi per un sito specificato. Esegue operazioni sul
    #     database e gestisce l'elaborazione dei record con un feedback visivo sul progresso.
    #
    #     Attributi:
    #         sito (str): L'identificatore del sito per i record da elaborare.
    #
    #     Parametri:
    #         s (str): L'identificatore del sito da aggiornare.
    #
    #     Eccezioni sollevate:
    #         Exception: Eccezione generale sollevata per errori imprevisti che si verificano durante l'operazione.
    #
    #     Dettagli:
    #         Questa operazione recupera i record corrispondenti all'identificatore del sito fornito, li elabora e
    #         aggiorna la continuità dei periodi secondo una logica specificata. Fornisce aggiornamenti sul progresso in
    #         tempo reale utilizzando una barra di avanzamento e gestisce potenziali eccezioni per garantire
    #         un'elaborazione senza interruzioni.
    #
    #     Effetti collaterali:
    #         Aggiorna il campo 'cont_per' nel database per ciascun record elaborato. Mostra il progresso visivo e
    #         messaggi di notifica sia per le informazioni che per gli errori.
    #
    #     Note:
    #         - Il metodo gestisce sia set di record vuoti che eccezioni di record individuali senza interrompere
    #         l'elaborazione dei record successivi.
    #         - Elabora le interazioni con il database tramite una sessione e garantisce la corretta chiusura della
    #         sessione dopo l'operazione.
    #         - Implementa messaggi localizzati per notifiche interattive dove applicabile.
    #
    #     '''
    #
    #     self.sito = s
    #
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     try:
    #         # Otteniamo la query
    #         string = ('%s%s%s%s%s') % ('session.query(US).filter_by(', 'sito', "='", str(self.sito), "')")
    #         query_us = eval(string)
    #
    #         # Convertiamo la query in lista per poter usare len()
    #         lista_us = list(query_us)
    #         total_records = len(lista_us)
    #
    #         # Debug - verifichiamo che ci siano effettivamente dei record
    #         print(f"Totale record da elaborare: {total_records}")
    #
    #         if total_records == 0:
    #             # Se non ci sono record, mostra un messaggio e termina
    #             if hasattr(self, 'L') and self.L == 'it':
    #                 QMessageBox.information(None, "Informazione", "Nessun record da elaborare", QMessageBox.Ok)
    #             else:
    #                 QMessageBox.information(None, "Information", "No records to process", QMessageBox.Ok)
    #             return
    #
    #         # Creiamo una progress bar
    #         progress = QProgressBar()
    #         progress.setWindowTitle("Aggiornamento Continuità Periodi")
    #         progress.setGeometry(300, 300, 300, 40)
    #         progress.setWindowModality(Qt.WindowModal)
    #         progress.setMinimum(0)
    #         progress.setMaximum(total_records)
    #         progress.setValue(0)
    #         #progress.setAlignment(Qt.AlignCenter)
    #         progress.show()
    #         QApplication.processEvents()
    #
    #         # Contatore per tenere traccia dell'avanzamento
    #         count = 0
    #         last_update_time = time.time()
    #
    #         # Procediamo con l'elaborazione
    #         for i in lista_us:
    #             # Incrementiamo il contatore
    #             count += 1
    #
    #             # Aggiorniamo la progress bar ogni 10 record o ogni secondo
    #             current_time = time.time()
    #             if count % 10 == 0 or (current_time - last_update_time) >= 1.0:
    #                 progress.setValue(count)
    #                 percentage = int((count / total_records) * 100)
    #                 progress.setFormat(f"Elaborazione record {count} di {total_records} ({percentage}%)")
    #                 QApplication.processEvents()
    #                 last_update_time = current_time
    #
    #             try:
    #                 # Logica originale di elaborazione record
    #                 if not i.periodo_finale and i.periodo_iniziale:
    #                     periodiz = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': i.periodo_iniziale,
    #                          'fase': "'" + str(i.fase_iniziale) + "'"},
    #                         'PERIODIZZAZIONE')
    #                     if periodiz and len(periodiz) > 0:
    #                         self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [periodiz[0].cont_per])
    #                     else:
    #                         print(f"Nessun dato di periodizzazione trovato per US {i.us}")
    #
    #                 elif not i.periodo_iniziale:
    #                     print(f"US {i.us} senza periodo iniziale, continuo...")
    #                     continue
    #
    #                 elif i.periodo_finale and i.periodo_iniziale:
    #                     cod_cont_iniz_temp = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_iniziale),
    #                          'fase': int(i.fase_iniziale)}, 'PERIODIZZAZIONE')
    #
    #                     cod_cont_fin_temp = self.query_bool(
    #                         {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_finale),
    #                          'fase': int(i.fase_finale)},
    #                         'PERIODIZZAZIONE')
    #
    #                     if not cod_cont_iniz_temp or not cod_cont_fin_temp:
    #                         print(f"Dati di periodizzazione mancanti per US {i.us}")
    #                         continue
    #
    #                     cod_cont_iniz = cod_cont_iniz_temp[0].cont_per
    #                     cod_cont_fin = cod_cont_fin_temp[0].cont_per
    #
    #                     # Debug - vediamo i valori reali
    #                     print(f"US {i.us} - Continuità iniziale: {cod_cont_iniz}, Continuità finale: {cod_cont_fin}")
    #
    #                     # Controllo che i valori siano numeri
    #                     try:
    #                         start_val = int(cod_cont_iniz)
    #                         end_val = int(cod_cont_fin)
    #                     except (ValueError, TypeError):
    #                         print(
    #                             f"Errore di conversione - cod_cont_iniz: {cod_cont_iniz}, cod_cont_fin: {cod_cont_fin}")
    #                         # Se non sono numeri, usiamo i valori originali senza calcolare range
    #                         if cod_cont_iniz != cod_cont_fin:
    #                             cod_cont_var_txt = f"{cod_cont_iniz}/{cod_cont_fin}"
    #                         else:
    #                             cod_cont_var_txt = str(cod_cont_iniz)
    #                         self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
    #                         continue
    #
    #                     # Se start_val > end_val, invertiamo i valori per evitare loop infiniti
    #                     if start_val > end_val:
    #                         print(
    #                             f"Attenzione: valore iniziale ({start_val}) maggiore del valore finale ({end_val}). Inversione.")
    #                         start_val, end_val = end_val, start_val
    #
    #                     # Generiamo la sequenza completa di valori
    #                     if start_val == end_val:
    #                         cod_cont_var_txt = str(start_val)
    #                     else:
    #                         values = list(range(start_val, end_val + 1))
    #                         cod_cont_var_txt = "/".join(str(v) for v in values)
    #
    #                     print(f"US {i.us} - Risultato: {cod_cont_var_txt}")
    #                     self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])
    #
    #             except Exception as e:
    #                 print(f"Errore nell'elaborazione del record {count} (US {i.us}): {str(e)}")
    #                 # Continuiamo con il prossimo record invece di interrompere tutto
    #                 continue
    #
    #         # Al termine dell'elaborazione, aggiorniamo e chiudiamo la progress bar
    #         progress.setValue(total_records)
    #         progress.setFormat("Elaborazione completata (100%)")
    #         QApplication.processEvents()
    #
    #         # Mostriamo un messaggio di completamento
    #         if hasattr(self, 'L') and self.L == 'it':
    #             QMessageBox.information(None, "Completato", f"Elaborazione completata. {count} record aggiornati.",
    #                                     QMessageBox.Ok)
    #         else:
    #             QMessageBox.information(None, "Completed", f"Processing completed. {count} records updated.",
    #                                     QMessageBox.Ok)
    #
    #         # Chiudiamo la progress bar
    #         progress.close()
    #
    #     except Exception as e:
    #         # Gestiamo eccezioni generali
    #         error_msg = f"Errore durante l'aggiornamento: {str(e)}"
    #         print(error_msg)
    #         QMessageBox.critical(None, "Errore", error_msg, QMessageBox.Ok)
    #
    #     finally:
    #         # Assicuriamoci che la sessione venga chiusa
    #         if 'session' in locals():
    #             session.close()
                

    def remove_alltags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE media_name  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res    
    
    def remove_tags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE id_entity  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res

    def remove_tags_from_db_sql_scheda(self, s,n):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE id_entity  = '%s' and media_name= '%s' ") % (s,n)

        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res
    def delete_thumb_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_thumb_table WHERE media_filename  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res    
    def select_medianame_from_st_sql(self,sito,sigla,numero):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  struttura_table as b, media_thumb_table as c WHERE b.id_struttura=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.sigla_struttura='%s' and b.numero_struttura='%s' and entity_type='STRUTTURA'")%(sito,sigla,numero) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows    
    def select_medianame_from_db_sql(self,sito,area):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s'")%(sito,area) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_tb_from_db_sql(self,sito,area):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  tomba_table as b, media_thumb_table as c WHERE b.id_tomba=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s'and entity_type='TOMBA'")%(sito,area) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows

    def select_medianame_pot_from_db_sql(self, sito, area, us):
        sql_query_string = (
                               "SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  pottery_table as b, media_thumb_table as c WHERE b.id_rep=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='CERAMICA'") % (
                           sito, area, us)

        res = self.engine.execute(sql_query_string)
        rows = res.fetchall()
        return rows


    def select_medianame_ra_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  inventario_materiali_table as b, media_thumb_table as c WHERE b.id_invmat=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='REPERTO'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_medianame_2_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, a.media_name FROM media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and b.us = '%s' and entity_type='US'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows

    def get_total_pages(self, filter_query, page_size):
        # Esegui una query per contare il numero totale di record che corrispondono al filtro
        sql_query_string = (
                               "SELECT COUNT(*) FROM media_thumb_table as a, media_to_entity_table as b  %s") % filter_query
        res = self.engine.execute(sql_query_string)
        total_records = res.scalar()  # .scalar() restituisce il primo elemento della prima riga, che in questo caso è il conteggio

        # Calcola e restituisci il numero totale di pagine
        total_pages = math.ceil(total_records / page_size)
        return total_pages

    def select_thumb(self, page_number, page_size):
        start_index = (page_number - 1) * page_size
        sql_query_string = (
            "SELECT * FROM media_thumb_table LIMIT {} OFFSET {}"
        ).format( page_size, start_index)
        res = self.engine.execute(sql_query_string)
        rows = res.fetchall()
        return rows
    def select_original(self, page_number, page_size):
        start_index = (page_number - 1) * page_size
        sql_query_string = (
            "SELECT * FROM media_to_entity_table LIMIT {} OFFSET {}"
        ).format( page_size, start_index)
        res = self.engine.execute(sql_query_string)
        rows = res.fetchall()
        return rows
    def select_ra_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT n_reperto from inventario_materiali_table WHERE sito = '%s' and area = '%s' and us = '%s'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_coord_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT coord from pyunitastratigrafiche WHERE scavo_s = '%s' and area_s = '%s' and us_s = '%s'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_medianame_3_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  inventario_materiali_table as b, media_thumb_table as c WHERE b.id_invmat=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and us = '%s'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_thumbnail_from_db_sql(self,sito):
        sql_query_string = ("SELECT c.filepath, group_concat ((select us from us_table where id_us like id_entity))as us,a.media_name,b.area,b.unita_tipo FROM  media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media and sito='%s' group by a.media_name order by a.media_name asc")%(sito)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_quote_from_db_sql(self, sito, area, us):
        sql_query_string = ("SELECT * FROM pyarchinit_quote WHERE sito_q = '%s' AND area_q = '%s' AND us_q = '%s'") % (
        sito, area, us)
        res = self.engine.execute(sql_query_string)
        return res
    def select_us_from_db_sql(self, sito, area, us, stratigraph_index_us):
        sql_query_string = (
                           "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND area_s = '%s' AND us_s = '%s' AND stratigraph_index_us = '%s'") % (
                           sito, area, us, stratigraph_index_us)
        res = self.engine.execute(sql_query_string)
        return res

    # def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
    #     sql_query_string = (
    #                        "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND tipo_doc = '%s' AND nome_doc = '%s'") % (
    #                        sito, tipo_doc, nome_doc)
    #     res = self.engine.execute(sql_query_string)
    #     return res
    #
    # def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
    #     sql_query_string = (
    #                        "SELECT * FROM pyarchinit_us_negative_doc WHERE sito_n = '%s' AND  tipo_doc_n = '%s' AND nome_doc_n = '%s'") % (
    #                        sito, tipo_doc, nome_doc)
    #     res = self.engine.execute(sql_query_string)
    #     return res
    def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):


        sql_query = text(
            "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = :sito AND tipo_doc = :tipo_doc AND nome_doc = :nome_doc")

        res = self.engine.execute(sql_query, sito=sito, tipo_doc=tipo_doc, nome_doc=nome_doc)
        return res

    def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):


        sql_query = text(
            "SELECT * FROM pyarchinit_us_negative_doc WHERE sito_n = :sito AND tipo_doc_n = :tipo_doc AND nome_doc_n = :nome_doc")

        res = self.engine.execute(sql_query, sito=sito, tipo_doc=tipo_doc, nome_doc=nome_doc)
        return res

    def select_db_sql(self, table):
        sql_query_string = ("SELECT * FROM %s") % table
        res = self.engine.execute(sql_query_string)
        return res
    
    def select_db_sql_2(self, sito,area,us,d_stratigrafica):
        sql_query_string = ("SELECT * FROM us_table as a where a.sito='%s' AND a.area='%s' AND a.us='%s' AND a.d_stratigrafica='%s'") % (sito,area,us,d_stratigrafica)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        
        return rows
    
    
    def test_ut_sql(self,unita_tipo):
        sql_query_string = ("SELECT %s FROM us_table")% (unita_tipo)
        res = self.engine.execute(sql_query_string)
        return res





    def query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size=100):
        """
        Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

        Args:
            value_list (list): Lista di valori da cercare.
            sitof (str): Valore per il filtro 'sito'.
            areaf (str): Valore per il filtro 'area'.
            chunk_size (int): Dimensione dei chunk. Default è 100.

        Returns:
            list: Lista dei risultati della query.
        """
        self.value_list = value_list

        # Configura la sessione
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        res_list = []

        while self.value_list:
            # Suddividi la lista in chunk
            chunk = self.value_list[:chunk_size]
            self.value_list = self.value_list[chunk_size:]

            # Esegui la query per il chunk
            results = session.query(US) \
                .filter_by(sito=sitof, area=areaf) \
                .filter(or_(*[US.rapporti.contains(v) for v in chunk])) \
                .all()

            res_list.extend(results)

        session.close()
        return res_list
    def query_in_contains(self, value_list, sitof, areaf):
        self.value_list = value_list
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res_list = []
        n = 500  # smaller chunk size

        while self.value_list:
            chunk = self.value_list[:n]
            self.value_list = self.value_list[n:]
            chunk_query = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                or_(*[US.rapporti.contains(v) for v in chunk])).all()
            res_list.extend(chunk_query)

        session.close()
        return res_list


    # def query_in_contains(self, value_list, sitof, areaf):
    #     # use a copy of the list to avoid emptying the input list
    #     values = value_list[:]
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #     res_list = []
    #     n = len(values) - 1 if values else 0  # handle empty list
    #     while values:
    #         chunk = values[0:n]
    #         values = values[n:]
    #         try:
    #             res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #                 or_(*[US.rapporti.contains(v) for v in chunk])))
    #         except Exception as e:
    #             print(f"Error while executing query: {e}")
    #             continue
    #     session.close()
    #     return res_list

    # def query_in_contains(self, value_list, sitof, areaf):
    #
    #     self.value_list = value_list
    #
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     res_list = []
    #     n = len(self.value_list) - 1
    #
    #     while self.value_list:
    #
    #         chunk = self.value_list[0:n]
    #         self.value_list = self.value_list[n:]
    #         res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             or_(*[US.rapporti.contains(v) for v in chunk])))
    #         # res_list.extend(us for us, in session.query(US.us).filter(or_(*[US.rapporti.contains(v) for v in chunk])))
    #     session.close()
    #     return res_list

    def insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        for i in range(us_range):
            id_us += 1

            data_ins = self.insert_values(id_us, sito, area, n_us, '', '', '', '', '', '', '', '', '', '', '', '', '[]',
                                          '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', unita_tipo, '', '', '', '',
                                          '', '', '', '', '', '', '', '', '', None, None, '', '[]','[]', '[]', '[]', '[]','','','','',None,None,'','','','','','','[]','[]',None,None,None,None,None,None,None,None,None,None,'','','','','','','','','','',None,None,None,'','','','','','','','','','','','','','','','','','','','','','','','','','','','','')
                                           
            self.insert_data_session(data_ins)
            n_us += 1
        return

    def insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        l = QgsSettings().value("locale/userLocale")[0:2]

        if l == 'it':
            text = "SCHEDA CREATA IN AUTOMATICO"
        else:
            text = "FORM MADE AUTOMATIC"

        id_us += 1

        # Inseriamo `n_rapporti` nella posizione corretta come lista di liste
        rapporti_list = [[rapporto_tipo, rapporto_n_us, rapporto_area, rapporto_sito] for
                         rapporto_tipo, rapporto_n_us, rapporto_area, rapporto_sito in n_rapporti]

        data_ins = self.insert_values(id_us, sito, area, n_us, text, '', '', '', '', '', '', '', '', '', '', '',
                                      '[]', '[]', str(rapporti_list), '', '', '', '', '', '', '', '', '0', '[]',
                                      unita_tipo,
                                      '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', None, None, '', '[]', '[]', '[]', '[]', '[]',
                                      '', '', '', '', None, None, '', '', '', '', '', '', '[]', '[]', None, None, None,
                                      None, None, None, None, None, None, None, '', '', '', '', '', '', '', '', '', '',
                                      None, None, None, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', '', '', '', '')

        self.insert_data_session(data_ins)

        return



    def insert_number_of_us_records(self, sito, area, n_us,unita_tipo):
        id_us = self.max_num_id('US', 'id_us')
        #text = "SCHEDA CREATA IN AUTOMATICO"
        l=QgsSettings().value("locale/userLocale")[0:2]

        if l == 'it':
            text = "SCHEDA CREATA IN AUTOMATICO"
            #unita_tipo
        else:
            text = "FORM MADE AUTOMATIC"
            #unita_tipo = 'SU'
        id_us += 1

        data_ins = self.insert_values(id_us, sito, area, n_us, text, '', '', '', '', '', '', '', '', '', '', '', '[]',
                                      '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', unita_tipo, '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', None, None, '', '[]', '[]', '[]', '[]', '[]',
                                      '', '', '', '', None, None, '', '', '', '', '', '', '[]', '[]', None, None, None,
                                      None, None, None, None, None, None, None, '', '', '', '', '', '', '', '', '', '',
                                      None, None, None, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '', '', '', '', '', '')

        self.insert_data_session(data_ins)

        return
    
    def insert_number_of_reperti_records(self, sito, numero_inventario):
        id_invmat = self.max_num_id('INVENTARIO_MATERIALI', 'id_invmat')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_invmat += 1

        data_ins = self.insert_values_reperti(id_invmat, sito, numero_inventario, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', None, None, '', None, '', '','0','','','')
                                           
        self.insert_data_session(data_ins)
        
        
        return

    def insert_number_of_pottery_records(self,  id_number,sito, area,us):
        id_rep = self.max_num_id('POTTERY', 'id_rep')

        l = QgsSettings().value("locale/userLocale")[0:2]

        id_rep += 1

        data_ins = self.insert_pottery_values(id_rep, id_number, sito, area, us, 0, '', '', 0, '', '', '', '',
                                              '', '', '', '', '', '', '', '', '', '', None, 0, None, None, None, None, '',
                                              0,'')

        self.insert_data_session(data_ins)

        return
    
    
    
    def insert_number_of_tomba_records(self, sito, nr_scheda_taf):
        id_tomba = self.max_num_id('TOMBA', 'id_tomba')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_tomba += 1

        data_ins = self.insert_values_tomba(id_tomba, sito, '', nr_scheda_taf, '', '', '', '', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '','')
                                           
        self.insert_data_session(data_ins)
        
        return
    def insert_struttura_records(self, sito, sigla_struttura,numero_struttura):
        id_struttura = self.max_num_id('STRUTTURA', 'id_struttura')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_struttura += 1

        data_ins = self.insert_struttura_values(id_struttura, sito, sigla_struttura, numero_struttura, '', '', '', '', '', '', '', '', '', '', '', '', '', '')
                                           
        self.insert_data_session(data_ins)
        
        return
    def select_like_from_db_sql(self, rapp_list, us_rapp_list):
        # this is a test
        pass

    ##      self.us_rapp_list = us_rapp_list
    ##      rapp_type = rapp_list
    ##      query_string_base = """session.query(US).filter(or_("""
    ##      query_list = []
    ##
    ##      #costruisce la stringa che trova i like
    ##      for sing_us_rapp in self.us_rapp_list:
    ##          for sing_rapp in rapp_type:
    ##              sql_query_string = """US.rapporti.contains("[u'%s', u'%s']")""" % (sing_rapp,sing_us_rapp) #funziona!!!
    ##              query_list.append(sql_query_string)
    ##
    ##      string_contains = ""
    ##      for sing_contains in range(len(query_list)):
    ##          if sing_contains == 0:
    ##              string_contains = query_list[sing_contains]
    ##          else:
    ##              string_contains = string_contains + "," + query_list[sing_contains]
    ##
    ##      query_string_execute = query_string_base + string_contains + '))'
    ##
    ##      Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    ##      session = Session()
    ##      res = eval(query_string_execute)
    ##
    ##      return res

    # def select_not_like_from_db_sql(self, sitof, areaf):
    #     # NB per funzionare con postgres è necessario che al posto di " ci sia '
    #     l=QgsSettings().value("locale/userLocale")[0:2]
    #     Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    #     session = Session()
    #
    #     if l=='it':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'>>'%"),~US.rapporti.like("%'Copre'%"), ~US.rapporti.like("%'Riempie'%"),
    #                  ~US.rapporti.like("%'Taglia'%"), ~US.rapporti.like("%'Si appoggia a'%")))
    #             # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     elif l=='en':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'Cuts'%"), ~US.rapporti.like("%'Abuts'%"),
    #                  ~US.rapporti.like("%'Covers'%"), ~US.rapporti.like("%'Fills'%")))
    #         # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     elif l=='de':
    #         res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
    #             and_(~US.rapporti.like("%'Schneidet'%"), ~US.rapporti.like("%'Stützt sich auf'%"),
    #                  ~US.rapporti.like("%'Liegt über'%"), ~US.rapporti.like("%'Verfüllt'%")))
    #         # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
    #     session.close()
    #     #QMessageBox.warning(None, "Messaggio", "DATA LIST" + str(res), QMessageBox.Ok)
    #     return res

    def select_not_like_from_db_sql(self, sitof, areaf):
        l = QgsSettings().value("locale/userLocale")[0:2]
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res = None

        if l == 'it':
            filters = ["%'>>'%", "%'Copre'%", "%'Riempie'%", "%'Taglia'%", "%'Si appoggia a'%"]
        elif l == 'en':
            filters = ["%'>>'%","%'Cuts'%", "%'Abuts'%", "%'Covers'%", "%'Fills'%"]
        elif l == 'de':
            filters = ["%'>>'%","%'Schneidet'%", "%'Stützt sich auf'%", "%'Liegt über'%", "%'Verfüllt'%"]
        else:
            filters = []  # Add fallback filters or handle this case differently.

        for f in filters:
            res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(~US.rapporti.like(f))

        session.close()
        return res

    def query_in_idusb(self):
        pass


# def main():
    # db = Pyarchinit_db_management('sqlite:////Users//Luca//pyarchinit_DB_folder//pyarchinit_db.sqlite')
    # db.connection()

    # db.insert_arbitrary_number_of_records(10, 'Giorgio', 1, 1, 'US')  # us_range, sito, area, n_us)
    

# if __name__ == '__main__':
    # main()
class ANSI():
    def background(code):
        return "\33[{code}m".format(code=code)
  
    def style_text(code):
        return "\33[{code}m".format(code=code)
  
    def color_text(code):
        return "\33[{code}m".format(code=code)
  
  
