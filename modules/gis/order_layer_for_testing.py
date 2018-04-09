#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
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


class Order_layers_non_funzia:
    if os.name == 'posix':
        HOME = os.environ['HOME']
    elif os.name == 'nt':
        HOME = os.environ['HOMEPATH']

    REPORT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")

    LISTA_US = []  # lista che contiene tutte le US singole prese dai singoli rapporti stratigrafici
    DIZ_ORDER_LAYERS = {}  # contiene una serie di chiavi valori dove la chiave e' il livello di ordinamento e il valore l'US relativa
    MAX_VALUE_KEYS = -1  # contiene l'indice progressivo dei livelli del dizionario
    TUPLE_TO_REMOVING = []  # contiene le tuple da rimuovere dai rapporti stratigrafici man mano che si passa ad un livello successivo
    LISTA_RAPPORTI = ""

    """variabili di controllo di paradossi nei rapporti stratigrafici"""
    status = 0  # contiene lo stato della lunghezza della lista dei rapporti stratigrafici
    check_status = 0  # il valore aumenta se la lunghezza della lista dei rapporti stratigrafici non cambia. Va in errore dopo 4000 ripetizioni del loop stratigraficocambia
    stop_while = ''  # assume il valore 'stop' dopo 4000 ripetizioni ed esce dal loop

    def __init__(self, lr):
        self.LISTA_RAPPORTI = lr  # istanzia la classe con una lista di tuple rappresentanti i rapporti stratigrafici
        self.LISTA_RAPPORTI.sort()  # ordina la lista dei rapporti stratigrafici
        self.status = len(
            self.LISTA_RAPPORTI)  # assegna la lunghezza della lista dei rapporti per verificare se cambia nel corso del loop

    # print self.lista_rapporti

    def progress(self, data, *args):
        it = iter(data)
        widget = QtGui.QProgressDialog(*args + (0, it.__length_hint__()))
        c = 0
        for v in it:
            QtCore.QCoreApplication.instance().processEvents()
            if widget.wasCanceled():
                raise StopIteration
            c += 1
            widget.setValue(c)
            yield (v)

    def main(self):
        # esegue la funzione per creare la lista valori delle US dai singoli rapporti stratigrafici
        self.add_values_to_lista_us()  # fin qui  e' ok 1
        # finche la lista US contiene valori la funzione bool ritorna True e il ciclo while prosegue
        while bool(self.LISTA_RAPPORTI) == True and self.stop_while == '':
            # viene eseguito il ciclo per ogni US contenuto nella lista delle US
            self.loop_on_lista_us()
        # dovrebbero rimanere le US che non hanno altre US, dopo
        if bool(self.LISTA_RAPPORTI) == False and bool(self.LISTA_US) == True:
            for sing_us in self.LISTA_US:
                self.add_key_value_to_diz(sing_us)
        return self.DIZ_ORDER_LAYERS

    def loop_on_lista_us(self):
        # se il valore di stop_while rimane vuoto (ovvero non vi sono paradossi stratigrafici) parte la ricerca del livello da assegnare all'US
        for i in self.LISTA_US:
            if self.check_position(
                    i) == 1:  # se la funzione check_position ritorna 1 significa che e' stata trovata l'US che va nel prossimo livello e in seguito viene rimossa
                self.LISTA_US.remove(i)
            else:
                # se il valore ritornato e' 0 significa che e' necessario passare all'US successiva in lista US e la lista delle tuple da rimuovere e' svuotata
                self.TUPLE_TO_REMOVING = []
            # se il valore di status non cambia significa che non e' stata trovata l'US da rimuovere. Se cio' accade per + di 4000 volte e' possibile che vi sia un paradosso e lo script va in errore
            if self.status == len(self.LISTA_RAPPORTI):
                self.check_status += 1
                # print self.check_status
                if self.check_status > 20:
                    self.stop_while = 'stop'
            else:
                # se entro le 4000 ricerche il valore cambia il check status torna a 0 e lo script va avanti
                self.check_status = 0

    def add_values_to_lista_us(self):
        # crea la lista valori delle US dai singoli rapporti stratigrafici
        for i in self.LISTA_RAPPORTI:
            if i[0] == i[1]:
                msg = str(i)
                filename_errori_in_add_value = ('%s%s%s') % (self.REPORT_PATH, os.sep, 'errori_in_add_value.txt')
                f = open(filename_errori_in_add_value, "w")
                f.write(msg)
                f.close()
                self.stop_while = "stop"
            else:
                if self.LISTA_US.count(i[0]) == 0:
                    self.LISTA_US.append(i[0])
                if self.LISTA_US.count(i[1]) == 0:
                    self.LISTA_US.append(i[1])
                # print "lista us", str(self.LISTA_US)

    def check_position(self, n):
        # riceve un numero di US dalla lista_US
        num_us = n
        # assegna 0 alla variabile check
        check = 0
        # inizia l'iterazione sUlla lista rapporti
        for i in self.LISTA_RAPPORTI:
            # se la tupla assegnata a i contiene in prima posizione il numero di US, ovvero e' un'US che viene dopo le altre nella sequenza, check diventa 1 e non si ha un nuovo livello stratigrafico
            if i[1] == num_us:
                ##				print "num_us", num_us
                check = 1
                self.TUPLE_TO_REMOVING = []
            # break <----ATTENZIONE FORSE DEVE ESSERE RIATTIVATO!!!
            # se invece il valore e' sempre e solo in posizione 1, ovvero e' in cima ai rapporti stratigrafici viene assegnata la tupla di quei rapporti stratigrafici per essere rimossa in seguito
            elif i[0] == num_us:
                self.TUPLE_TO_REMOVING.append(i)
        # se alla fine dell'iterazione check e' rimasto 0, significa che quell'US e' in cima ai rapporti stratigrafici e si passa all'assegnazione di un nuovo livello stratigrafico nel dizionario
        if bool(self.TUPLE_TO_REMOVING):
            # viene eseguita la funzione di aggiunta valori al dizionario passandogli il numero di US
            self.add_key_value_to_diz(num_us)
            # vengono rimosse tutte le tuple in cui e' presente l'us assegnata al dizionario e la lista di tuple viene svuotata
            for i in self.TUPLE_TO_REMOVING:
                try:
                    self.LISTA_RAPPORTI.remove(i)
                except Exception as e:
                    msg = "check_position: \n" + str(i) + "  Lista rapporti presenti: \n" + str(
                        self.LISTA_RAPPORTI) + str(e)
                    filename_check_position = ('%s%s%s') % (self.REPORT_PATH, os.sep, 'check_position.txt')
                    f = open(filename_check_position, "w")
                    f.write(msg)
                    f.close()
                    self.stop_while = "stop"
            self.TUPLE_TO_REMOVING = []
            # la funzione ritorna il valore 1
            return 1

    def add_key_value_to_diz(self, n):
        self.num_us_value = n  # numero di US da inserire nel dizionario
        self.MAX_VALUE_KEYS += 1  # il valore globale del numero di chiave aumenta di 1
        self.DIZ_ORDER_LAYERS[
            self.MAX_VALUE_KEYS] = self.num_us_value  # viene assegnata una nuova coppia di chiavi-valori


class Order_layers_funzia:
    LISTA_US = []  # lista che contiene tutte le US singole prese dai singoli rapporti stratigrafici
    DIZ_ORDER_LAYERS = {}  # contiene una serie di chiavi valori dove la chiave e' il livello di ordinamento e il valore l'US relativa
    MAX_VALUE_KEYS = -1  # contiene l'indice progressivo dei livelli del dizionario
    TUPLE_TO_REMOVING = []  # contiene le tuple da rimuovere dai rapporti stratigrafici man mano che si passa ad un livello successivo
    LISTA_RAPPORTI = ""

    """variabili di controllo di paradossi nei rapporti stratigrafici"""
    status = 0  # contiene lo stato della lunghezza della lista dei rapporti stratigrafici
    check_status = 0  # il valore aumenta se la lunghezza della lista dei rapporti stratigrafici non cambia. Va in errore dopo 4000 ripetizioni del loop stratigraficocambia
    stop_while = ''  # assume il valore 'stop' dopo 4000 ripetizioni ed esce dal loop

    def __init__(self, lr):
        self.LISTA_RAPPORTI = lr  # istanzia la classe con una lista di tuple rappresentanti i rapporti stratigrafici
        # f = open('C:\\test_matrix_1.txt', 'w') #to delete
        # f.write(str(self.lista_rapporti))
        # f.close()
        self.LISTA_RAPPORTI.sort()  # ordina la lista dei rapporti stratigrafici
        self.status = len(
            self.LISTA_RAPPORTI)  # assegna la lunghezza della lista dei rapporti per verificare se cambia nel corso del loop

    # print self.lista_rapporti
    def main(self):
        # esegue la funzione per creare la lista valori delle US dai singoli rapporti stratigrafici
        self.add_values_to_lista_us()  # fin qui  e' ok 1
        # finche la lista US contiene valori la funzione bool ritorna True e il ciclo while prosegue
        len_lista = len(self.LISTA_RAPPORTI)
        while bool(self.LISTA_RAPPORTI) == True or len(self.LISTA_RAPPORTI) == 4:
            print("len_lista_rapp", self.LISTA_RAPPORTI)
            print("len_lista_us", self.LISTA_US)
            # viene eseguito il ciclo per ogni US contenuto nella lista delle US
            self.loop_on_lista_us()
        # dovrebbero rimanere le US che non hanno altre US, dopo
        if bool(self.LISTA_RAPPORTI) == False and bool(self.LISTA_US) == True:
            for sing_us in self.LISTA_US:
                self.add_key_value_to_diz(sing_us)
        return self.DIZ_ORDER_LAYERS

    # self.print_values():

    def loop_on_lista_us(self):
        # se il valore di stop_while rimane vuoto (ovvero non vi sono paradossi stratigrafici) parte la ricerca del livello da assegnare all'US
        ##		if self.stop_while == '':
        for i in self.LISTA_US:
            if self.check_position(
                    i) == 1:  # se la funzione check_position ritorna 1 significa che e' stata trovata l'US che va nel prossimo livello e in seguito viene rimossa
                self.LISTA_US.remove(i)
            else:
                # se il valore ritornato e' 0 significa che e' necessario passare all'US successiva in lista US e la lista delle tuple da rimuovere e' svuotata
                self.TUPLE_TO_REMOVING = []
            # se il valore di status non cambia significa che non e' stata trovata l'US da rimuovere. Se cio' accade per + di 4000 volte e' possibile che vi sia un paradosso e lo script va in errore
            if self.status == len(self.LISTA_RAPPORTI):
                self.check_status += 1
                # print self.check_status
                if self.check_status > 10:
                    self.stop_while = 'stop'
            else:
                # se entro le 4000 ricerche il valore cambia il check status torna a 0 e lo script va avanti
                self.check_status = 0
            ##		else:
            ##			#ferma il loop ma va in errore (baco da correggere)
            ##			error = MyError('error')
            ##			raise error

    def add_values_to_lista_us(self):
        # crea la lista valori delle US dai singoli rapporti stratigrafici
        for i in self.LISTA_RAPPORTI:
            if i[0] == i[1]:
                print("errore!!!")
            else:
                if self.LISTA_US.count(i[0]) == 0:
                    self.LISTA_US.append(i[0])
                if self.LISTA_US.count(i[1]) == 0:
                    self.LISTA_US.append(i[1])
                # print "lista us", str(self.LISTA_US)

    def check_position(self, n):
        # riceve un numero di US dalla lista_US
        num_us = n
        # assegna 0 alla variabile check
        check = 0
        # inizia l'iterazione sUlla lista rapporti
        for i in self.LISTA_RAPPORTI:
            # se la tupla assegnata a i contiene in prima posizione il numero di US, ovvero e' un'US che viene dopo le altre nella sequenza, check diventa 1 e non si ha un nuovo livello stratigrafico
            if i[1] == num_us:
                # print "num_us", num_us
                check = 1
                self.TUPLE_TO_REMOVING = []
                break
            # se invece il valore e' sempre e solo in posizione 1, ovvero e' in cima ai rapporti stratigrafici viene assegnata la tupla di quei rapporti stratigrafici per essere rimossa in seguito
            elif i[0] == num_us:
                self.TUPLE_TO_REMOVING.append(i)
        # se alla fine dell'iterazione check e' rimasto 0, significa che quell'US e' in cima ai rapporti stratigrafici e si passa all'assegnazione di un nuovo livello stratigrafico nel dizionario
        if bool(self.TUPLE_TO_REMOVING):
            # viene eseguita la funzione di aggiunta valori al dizionario passandogli il numero di US
            self.add_key_value_to_diz(num_us)
            # vengono rimosse tutte le tuple in cui e' presente l'us assegnata al dizionario e la lista di tuple viene svuotata
            for i in self.TUPLE_TO_REMOVING:
                self.LISTA_RAPPORTI.remove(i)
            # print "toremove", i
            # print "self.LISTA_RAPPORTI", self.LISTA_RAPPORTI
            # print self.DIZ_ORDER_LAYERS
            self.TUPLE_TO_REMOVING = []
            # la funzione ritorna il valore 1
            return 1

    def add_key_value_to_diz(self, n):
        self.num_us_value = n  # numero di US da inserire nel dizionario
        self.MAX_VALUE_KEYS += 1  # il valore globale del numero di chiave aumenta di 1
        self.DIZ_ORDER_LAYERS[
            self.MAX_VALUE_KEYS] = self.num_us_value  # viene assegnata una nuova coppia di chiavi-valori

    """
    def print_values(self):
        print "dizionario_valori per successione stratigrafica: ",self.DIZ_ORDER_LAYERS
        print "ordine di successione delle US: "
        for k in self.DIZ_ORDER_LAYERS.keys():
            print k
    """


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


lista_rapporti = [(1, 2), (2, 3), (3, 0)]
OL = Order_layers_funzia(lista_rapporti)
print(OL.main())
