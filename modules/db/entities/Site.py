'''
Created on 15 feb 2018

@author: Serena Sensini
'''
from sqlalchemy.orm import mapper
from modules.db.structures.Site_table import Site_table

class SITE(object):
        #def __init__"
        def __init__(self,
        id_sito,
        sito,
        nazione,
        regione,
        comune,
        descrizione,
        provincia,
        definizione_sito,
        find_check
        ):
            self.id_sito = id_sito                             #0
            self.sito = sito                                 #1
            self.nazione = nazione                         #2
            self.regione = regione                         #3
            self.comune = comune                     #4
            self.descrizione = descrizione                 #5
            self.provincia = provincia                     #6
            self.definizione_sito = definizione_sito    #7
            self.find_check = find_check                 #8

        #def __repr__"
        def __repr__(self):
            return "<SITE('%d','%s', '%s',%s,'%s','%s', '%s', '%s', '%d')>" % (
            self.id_sito,
            self.sito,
            self.nazione,
            self.regione,
            self.comune,
            self.descrizione,
            self.provincia,
            self.definizione_sito,
            self.find_check
            )

#mapper
mapper(SITE, Site_table.site_table)