#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2007-12-01
        copyright            : (C) 2008 by Luca Mandolesi
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

import os

import psycopg2
from builtins import object
from builtins import range
from builtins import str
from builtins import zip
from sqlalchemy import and_, or_, Table, select, func, asc
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData

from modules.db.pyarchinit_db_mapper import US, UT, SITE, PERIODIZZAZIONE, \
    STRUTTURA, SCHEDAIND, INVENTARIO_MATERIALI, DETSESSO, DOCUMENTAZIONE, DETETA, MEDIA, \
    MEDIA_THUMB, MEDIATOENTITY, TAFONOMIA, CAMPIONI, PYARCHINIT_THESAURUS_SIGLE, \
    ARCHEOZOOLOGY, INVENTARIO_LAPIDEI, PDF_ADMINISTRATOR
from modules.db.pyarchinit_db_update import DB_update
from modules.db.pyarchinit_utility import Utility


class Pyarchinit_db_management(object):
    metadata = ''
    engine = ''
    boolean = ''

    if os.name == 'posix':
        boolean = 'True'
    elif os.name == 'nt':
        boolean = 'True'

    def __init__(self, c):
        self.conn_str = c

    def connection(self):
        test = ""

        try:
            test_conn = self.conn_str.find("sqlite")
            if test_conn == 0:
                self.engine = create_engine(self.conn_str, echo=eval(self.boolean))
            else:
                self.engine = create_engine(self.conn_str, max_overflow=-1, echo=eval(self.boolean))
            self.metadata = MetaData(self.engine)
            self.engine.connect()
        except Exception as e:
            test = str(e)

        try:
            db_upd = DB_update()
            db_upd.update_table()
        except Exception as e:
            test = str(e)
        return test

        # insert statement

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
                arg[50]
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
                    arg[8])

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
                                                    arg[28])

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
                              arg[11])

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
                                  arg[6])

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

    def insert_values_tafonomia(self, *arg):
        """Istanzia la classe TAFONOMIA da pyarchinit_db_mapper"""

        tafonomia = TAFONOMIA(arg[0],
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
                              arg[34])

        return tafonomia

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

        thesaurus = PYARCHINIT_THESAURUS_SIGLE(arg[0],
                                               arg[1],
                                               arg[2],
                                               arg[3],
                                               arg[4],
                                               arg[5])

        return thesaurus

    def insert_values_archeozoology(self, *arg):
        """Istanzia la classe ARCHEOZOOLOGY da pyarchinit_db_mapper"""

        archeozoology = ARCHEOZOOLOGY(arg[0],
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
                                      arg[20])

        return archeozoology

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

    ##	def insert_relationship_check_values(self, *arg):
    ##		"""Istanzia la classe RELATIONSHIP_CHECK da pyarchinit_db_mapper"""
    ##		relationship_check = RELATIONSHIP_CHECK(arg[0],
    ##												arg[1],
    ##												arg[2],
    ##												arg[3],
    ##												arg[4],
    ##												arg[5],
    ##												arg[6],
    ##												arg[7],
    ##												arg[8],
    ##												arg[9])
    ##
    ##		return relationship_check


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
        session.remove()

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
        session.remove()

        # query statement

    #
    def query(self, n):
        class_name = eval(n)
        # engine = self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query = session.query(class_name)
        res = query.all()
        session.remove()
        return res

    def query_bool(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())

        field_value_string = ""

        for sing_couple_n in range(len(list_keys_values)):
            if sing_couple_n == 0:
                if type(list_keys_values[sing_couple_n][1]) != '<str>':
                    field_value_string = table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = table + ".%s == u%s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
            else:
                if type(list_keys_values[sing_couple_n][1]) == '<str>':
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

        '''
        t = open("/test_import.txt", "w")
        t.write(str(query_str))
        t.close()
        '''
        session.remove()
        return eval(query_str)

    def query_operator(self, params, table):
        u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
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
        session.remove()
        return eval(query_str)

    def query_distinct(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##		return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

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
        session.remove()
        return eval(query_cmd)

    def query_distinct_sql(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##		return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

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
        Session = sessionmaker(bind=self.engine, autoflush=True)
        session = Session()
        session.add(data)
        session.commit()
        session.remove()

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

        session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
        self.table_class_str, self.table_class_str, self.id_table_str, self.value_id_list[0], changes_dict)

        # f = open('/test_update.txt', "w")
        # f.write(str(session_exec_str))
        # f.close()

        eval(session_exec_str)
        session.remove()

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
        session.remove()

    def empty_find_check(self, table_class_str, find_check_value):
        self.table_class_str = table_class_str
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).update(values = {"find_check": %d})' % (self.table_class_str, 0)

        eval(session_exec_str)
        session.remove()

    def delete_one_record(self, tn, id_col, id_rec):
        self.table_name = tn
        self.id_column = id_col
        self.id_rec = id_rec
        # self.connection()
        table = Table(self.table_name, self.metadata, autoload=True)
        exec_str = ('%s%s%s%d%s') % ('table.delete(table.c.', self.id_column, ' == ', self.id_rec, ').execute()')

        eval(exec_str)

    def max_num_id(self, tc, f):
        self.table_class = tc
        self.field_id = f

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        exec_str = "session.query(func.max({}.{}))".format(self.table_class, self.field_id)
        max_id_func = eval(exec_str)
        res_all = max_id_func.all()
        res_max_num_id = res_all[0][0]
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

        # managements utilities
        session.remove()

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
        session.remove()
        return res

    def query_sort(self, id_list, op, to, tc, idn):
        self.order_params = op
        self.type_order = to
        self.table_class = tc
        self.id_name = idn

        filter_params = self.type_order + "(" + self.table_class + "." + self.order_params[0] + ")"

        for i in self.order_params[1:]:
            filter_temp = self.type_order + "(" + self.table_class + "." + i + ")"

            filter_params = filter_params + ", " + filter_temp

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        cmd_str = "session.query({0}).filter({0}.{1}.in_(id_list)).order_by({2}).all()".format(self.table_class,
                                                                                               self.id_name,
                                                                                               filter_params)
        s = eval(cmd_str)
        session.remove()
        return s

    def run(self, stmt):
        rs = stmt.execute()
        res_list = []
        for row in rs:
            res_list.append(row[0])

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
        session.remove()
        return self.engine.execute(s).fetchall()

    def query_where_text(self, c, v):
        self.c = c
        self.v = v
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        string = ('%s%s%s%s%s') % ('session.query(PERIODIZZAZIONE).filter_by(', self.c, "='", self.v, "')")

        res = eval(string)
        session.remove()
        return res

    def update_cont_per(self, s):
        self.sito = s

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        string = ('%s%s%s%s%s') % ('session.query(US).filter_by(', 'sito', "='", str(self.sito), "')")
        session.remove()
        # print string
        lista_us = eval(string)

        for i in lista_us:
            if not i.periodo_finale and i.periodo_iniziale:
                    periodiz = self.query_bool(
                        {'sito': "'" + str(self.sito) + "'", 'periodo': i.periodo_iniziale, 'fase': i.fase_iniziale},
                        'PERIODIZZAZIONE')
                    self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [periodiz[0].cont_per])
            elif i.periodo_finale and i.periodo_iniziale:
                cod_cont_iniz_temp = self.query_bool(
                    {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_iniziale),
                     'fase': int(i.fase_iniziale)}, 'PERIODIZZAZIONE')
                cod_cont_fin_temp = self.query_bool(
                    {'sito': "'" + str(self.sito) + "'", 'periodo': int(i.periodo_finale), 'fase': int(i.fase_finale)},
                    'PERIODIZZAZIONE')

                cod_cont_iniz = cod_cont_iniz_temp[0].cont_per
                cod_cont_fin = cod_cont_fin_temp[0].cont_per

                cod_cont_var_n = cod_cont_iniz
                cod_cont_var_txt = str(cod_cont_iniz)

                while cod_cont_var_n != cod_cont_fin:
                    cod_cont_var_n += 1

                    cod_cont_var_txt = cod_cont_var_txt + "/" + str(cod_cont_var_n)

                self.update('US', 'id_us', [int(i.id_us)], ['cont_per'], [cod_cont_var_txt])

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

    def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
        sql_query_string = (
                           "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND tipo_doc = '%s' AND nome_doc = '%s'") % (
                           sito, tipo_doc, nome_doc)
        res = self.engine.execute(sql_query_string)
        return res

    def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
        sql_query_string = (
                           "SELECT * FROM pyarchinit_us_negative_doc WHERE sito_n = '%s' AND  tipo_doc_n = '%s' AND nome_doc_n = '%s'") % (
                           sito, tipo_doc, nome_doc)
        res = self.engine.execute(sql_query_string)
        return res

    def select_db_sql(self, table):
        sql_query_string = ("SELECT * FROM %s") % table
        res = self.engine.execute(sql_query_string)
        return res

    def query_in_contains(self, value_list, sitof, areaf):
        self.value_list = value_list

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        res_list = []
        n = len(self.value_list) - 1
        while self.value_list:
            chunk = self.value_list[0:n]
            self.value_list = self.value_list[n:]
            res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                or_(*[US.rapporti.contains(v) for v in chunk])))
            # res_list.extend(us for us, in session.query(US.us).filter(or_(*[US.rapporti.contains(v) for v in chunk])))
        session.remove()
        return res_list

    def insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us):
        id_us = self.max_num_id('US', 'id_us')
        for i in range(us_range):
            id_us += 1
            n_us += 1

            data_ins = self.insert_values(id_us, sito, area, n_us, '', '', '', '', '', '', '', '', '', '', '', '', '[]',
                                          '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', 'US', '', '', '', '',
                                          '', '', '', '', '', '', '', '', '', None, None, '', '', '', '', '', '[]')
            self.insert_data_session(data_ins)

    def select_like_from_db_sql(self, rapp_list, us_rapp_list):
        # this is a test
        pass

    ##		self.us_rapp_list = us_rapp_list
    ##		rapp_type = rapp_list
    ##		query_string_base = """session.query(US).filter(or_("""
    ##		query_list = []
    ##
    ##		#costruisce la stringa che trova i like
    ##		for sing_us_rapp in self.us_rapp_list:
    ##			for sing_rapp in rapp_type:
    ##				sql_query_string = """US.rapporti.contains("[u'%s', u'%s']")""" % (sing_rapp,sing_us_rapp) #funziona!!!
    ##				query_list.append(sql_query_string)
    ##
    ##		string_contains = ""
    ##		for sing_contains in range(len(query_list)):
    ##			if sing_contains == 0:
    ##				string_contains = query_list[sing_contains]
    ##			else:
    ##				string_contains = string_contains + "," + query_list[sing_contains]
    ##
    ##		query_string_execute = query_string_base + string_contains + '))'
    ##
    ##		Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
    ##		session = Session()
    ##		res = eval(query_string_execute)
    ##
    ##		return res

    def select_not_like_from_db_sql(self, sitof, areaf):
        # NB per funzionare con postgres è necessario che al posto di " ci sia '
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
            and_(~US.rapporti.like("%'Taglia'%"), ~US.rapporti.like("%'Si appoggia a'%"),
                 ~US.rapporti.like("%'Copre'%"), ~US.rapporti.like("%'Riempie'%")))
        # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
        session.remove()
        return res

    def query_in_idusb(self):
        pass


def main():
    db = Pyarchinit_db_management('sqlite:////Users//Luca//pyarchinit_DB_folder//pyarchinit_db.sqlite')
    db.connection()

    db.insert_arbitrary_number_of_records(10, 'Giorgio', 1, 1)  # us_range, sito, area, n_us)


if __name__ == '__main__':
    main()
