#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
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

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management


def convert_cell_schema(s, c):
    cell_schema = s  # riceve lo schema delle celle in formato lista di liste [['N° US: /us', '02', '03', 'Area: /area','05', '06', '07', '09']]
    campi = c  # riceve la lista dei campi con slash davanti

    cell_schema_res = []

    for sing_row in cell_schema:  # da qui itera su ogni singolo valore contenuto nelle liste
        sing_row_list = []
        for value in sing_row:
            diz_field_value = create_dict_field_value(campi)  # crea un dizionario con {/campo:valore}
            value = dynamic_replace(value,
                                    diz_field_value)  # sostituire con un dizionario campo:valore per il singolo record
            sing_row_list.append(value)
        cell_schema_res.append(sing_row_list)
    return cell_schema_res


def dynamic_replace(s, d):
    diz_field_value = d
    stringa = s
    s1 = stringa
    # print diz_field_value
    valori = []
    campi = []
    for k, v in list(diz_field_value.items()):
        valori.append(v)
        campi.append(k)
    valori_tupla = tuple(valori)
    res = stringa
    lista_valori_sost = []
    try:
        for i in range(len(campi)):
            s2 = s1.replace(campi[i], "%s")
            if s1.find(campi[i]) != -1:
                lista_valori_sost.append(diz_field_value[campi[i]])
                lista_valori_sost = tuple(lista_valori_sost)
                res = s2 % (lista_valori_sost)
    except Exception as e:
        pass
    return res


def create_dict_field_value(f):
    fields = f  # riceve la lista dei campi
    diz_field_value = {}
    for field in fields:  # per ogni campi esegue una query per ricavare il valore
        field_copy = field[1:]
        print("query su", field_copy)
        value = "qui il valore"  # query al db per ricavare il singolo valore, deve cerca in base a nome_tabella, id record e nome campo
        ##		"""VERIFICARE COME ARRIVA IL DATO DAL DB"""
        diz_field_value[field] = value

    return diz_field_value


# http://www.anthropology-resources.net/Texts/files.html dynamic_replace("il mio /sw preferito: /nome!", ["/gig", "/ugo"],["plugin", "pyArchInit"])

cell_schema = [['Nr US: /us', 'numero di us: /us', '03', 'Area: /area', '05', '06', '07', '09'],
               ['la fava: /us', 'numero di us: /us', '03', 'Area: /area', '05', '06', '07', '09']]

conn = Connection()
conn_str = conn.conn_str()

db = Pyarchinit_db_management(conn_str)
print(db.query(eval('SITE')))
# print convert_cell_schema(cell_schema, ['/us', '/area'])
