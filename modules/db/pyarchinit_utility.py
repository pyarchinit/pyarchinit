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


class Utility:
    def pos_none_in_list(self, l):

        """take a list of values and return the position number of the values
        equal to 'None' """
        self.list = l
        l2 = []
        for i in range(len(self.list)):
            if self.list[i] == 'None':
                l2.append(i)
        for i in l2:
            self.list[i] = None

        return self.list

    def tup_2_list(self, t, s='', i=0):

        """take a tuple of strings, and return a list of lists of the values.
        if s is set, add the value to the strings. If i is set return only the
        value in the i position"""
        self.tupla = t
        self.index = i
        self.subfix = s
        l = []
        for n in range(len(self.tupla)):
            try:
                int(self.tupla[n][self.index])
            except ValueError:
                v = [self.subfix + self.tupla[n][self.index]]
            else:
                v = [self.subfix + str(self.tupla[n][self.index])]
            l.append(v)
        return l

    def tup_2_list_II(self, l):
        """take a list of tuples ad return a list of lists"""
        self.list = l
        l = []
        for i in self.list:
            sublist = []
            for n in i:
                sublist.append(n)
            l.append(sublist)
        return l

    def tup_2_list_III(self, l):
        """take a list of tuples ad return a list of values"""
        self.list = l
        nl = []
        for i in self.list:
            nl.append(i[0])
        return nl

    def list_tup_2_list(self, l):
        """take a list of tuples ad return a list of lists"""
        self.list = l
        res_list = []
        for i in self.list:
            res_list.append(i[0])
        return res_list

    def select_in_list(self, l, p):
        """take a list of lists or value and return the in a list of lists
        the value taken by the value of p. """
        self.list = l
        self.pos = p
        res_list = []
        for i in self.list:
            if type(i) is list:
                par_tup = i
                res_list.append([par_tup[self.pos]])
            else:
                res_list.append([self.list[self.pos]])

                break
        return res_list

    def count_list_eq_v(self, l, v):
        """take a list and a value. If the number of occurens of a
        items inside the list is equal to v value, put the singol value
        into list_res as a list. Return a list of lists"""

        self.list = l
        self.value = v
        list_res = []
        for i in self.list:
            if self.list.count(i) == self.value:
                list_res.append([i])
        return list_res

    def find_list_in_dict(self, d):
        """recives a dict and if contains a list of lists and
        delete the item from the dict.
        Return a tuple containin the new dict and a list of
        tuples wich contain the keys and the values"""

        self.dict = d

        res_list = []
        ret = []
        for key, value in list(self.dict.items()):
            if bool(value):
                if type(value[0]) is list:
                    res_list.append((key, value))
                    del self.dict[key]

        if bool(res_list):
            for i in res_list:
                cont = 0
                for n in range(len(i)):

                    try:
                        ret.append((i[0] + str(cont), i[1][cont]))
                    except:
                        pass
                    cont += 1

        return self.dict, ret

    def add_item_to_dict(self, d, i):
        """receive a dict and a list containt tuple with key,value
        and add them to dict"""

        self.dict = d
        self.item = i
        for i in self.item:
            self.dict[i[0]] = i[1]
        return self.dict

    def list_col_index_value(self, v1, v2):
        """return two lists into one tupla,
        takin' two list with same lenght and lookin for the occurrences.
        for every occurrences between v_1 and v_2 the v_2 value it's charged
        into mod_value and its position in list it's put into list_index.
        """
        self.v_1 = v1
        self.v_2 = v2
        list_index = []
        mod_value = []
        for i in range(len(self.v_1)):
            if self.v_1[i] != self.v_2[i]:
                mod_value.append(self.v_2[i])
                list_index.append(str(i))
        return mod_value, list_index

    def deunicode_list(self, l):
        self.list = l
        # f = open("test_list.txt", "w")
        # f.write(str(self.list))
        # f.close()
        for i in range(len(self.list)):
            if str(type(self.list[i])) != "<class 'int'>" and str(type(self.list[i])) != "<class 'float'>":
                if not self.list[i]:
                    pass
                elif self.list[i][0:3] == '"""':
                    self.list[i] = self.list[i][3:-3]
                elif self.list[i][0:1] == '"':
                    self.list[i] = self.list[i][1:-1]
        return self.list

    def zip_lists(self, l1, l2):
        self.l1 = l1
        self.l2 = l2

        eq_list = list(zip(l1, l2))
        lr = []
        for i in eq_list:
            if i[0] == i[1]:
                lr.append(i[0])

        if bool(lr):
            return lr

    def join_list_if(self, l1, l2, v1, v2):
        self.l1 = l1
        self.l2 = l2
        self.value_pos_1 = v1
        self.value_pos_2 = v2
        r_list = []
        for l1 in self.l1:
            sublist = []
            for l2 in self.l2:
                if str(type(l1[self.value_pos_1])) != "<type 'int'>":
                    if l1[self.value_pos_1] == l2[self.value_pos_2]:
                        sublist += l2[self.value_pos_2 + 1:]
                    else:
                        if l1[self.value_pos_1].strip() == l2[self.value_pos_2]:
                            sublist += l2[self.value_pos_2 + 1:]

            if bool(sublist):
                r_list.append(l1 + sublist)

        if bool(r_list):
            return r_list

    def extract_from_list(self, l, p):
        self.list = l
        self.pos = p
        res_list = []
        for i in self.list:
            res_list.append([i[self.pos]])
        return res_list

    def remove_empty_items_fr_dict(self, d):
        for k, v in list(d.items()):
            if v == "" or v == '' or v == "''" or v == '""' or v == None:
                d.pop(k)
        return d

    def findFieldFrDict(self, d, fn):
        self.dict = d
        self.field_name = fn
        for i in self.dict:
            if self.dict[i] == self.field_name:
                res = i
            else:
                res = None
        return res

    def remove_dup_from_list(self, ls):
        self.list = ls

        self.list.sort()
        nl = []

        if len(self.list) > 1:
            value = self.list[0]
            nl.append(value)
            for sing_value in range(len(self.list)):
                if sing_value > 0:
                    if self.list[sing_value] != value:
                        value = self.list[sing_value]
                        nl.append(value)
            return nl
        else:
            return self.list

    def sum_list_of_tuples_for_value(self, l):
        self.l = l
        self.l.sort()
        cfr_txt = self.l[0][0]
        number = self.l[0][1]
        res_list = []
        for i in range(len(self.l)):
            if len(self.l) == 1:
                temp_tup = (cfr_txt, number)
                res_list.append(temp_tup)
            elif i > 0:
                if self.l[i][0] == cfr_txt:
                    number += self.l[i][1]

                if self.l[i][0] != cfr_txt and i < len(self.l) - 1:
                    temp_tup = (cfr_txt, number)
                    res_list.append(temp_tup)

                    cfr_txt = self.l[i][0]
                    number = self.l[i][1]

                if self.l[i][0] == cfr_txt and i == len(self.l) - 1:
                    temp_tup = (cfr_txt, number)
                    res_list.append(temp_tup)

                if self.l[i][0] != cfr_txt and i == len(self.l) - 1:
                    temp_tup1, temp_tup2 = (cfr_txt, number), (self.l[i][0], self.l[i][1])
                    res_list.append(temp_tup1)
                    res_list.append(temp_tup2)
        return res_list

    def conversione_numeri(self, Numero):
        self.numero = Numero
        # source from http://www.python-it.org/forum/index.php?topic=7142.0
        if type(self.numero) is not str:
            self.numero = str(self.numero)

        Punto = self.numero.find(".")
        Decimale = self.numero[Punto + 1:]
        if len(Decimale) == 1:
            Decimale += "0"
        elif Punto == -1:
            Decimale = "00"
            Punto = len(self.numero)

        self.numero = self.numero[:Punto]

        ListaNumero = []
        for n in range(int(len(self.numero) / 3)):
            newNumero = self.numero[-3:]
            self.numero = self.numero[:-3]
            ListaNumero.append(newNumero)

        ListaNumero.reverse()

        if self.numero != "":
            ListaNumero[0:0] = [self.numero]

        Decimale = Decimale[0:3]

        res = ".".join(ListaNumero) + "." + Decimale

        return res

    def getQuery(name):
        query = ""
        try:
            with open('queries.txt') as query_file:
                for line in query_file:
                    if name in line:
                        print('Query trovata')
                        query = line.split("=")
                        break
        except Exception as e:
            print(e)
            print('Impossibile recuperare file')
        return query
