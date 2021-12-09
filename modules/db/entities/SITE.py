'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class SITE(object):
    # def __init__"
    def __init__(self,
                 id_sito,
                 sito,
                 nazione,
                 regione,
                 comune,
                 descrizione,
                 provincia,
                 definizione_sito,
                 sito_path,
                 find_check
                 ):
        self.id_sito = id_sito  # 0
        self.sito = sito  # 1
        self.nazione = nazione  # 2
        self.regione = regione  # 3
        self.comune = comune  # 4
        self.descrizione = descrizione  # 5
        self.provincia = provincia  # 6
        self.definizione_sito = definizione_sito  # 7
        self.sito_path = sito_path  # 8
        self.find_check = find_check  # 9

    # def __repr__"
    def __repr__(self):
        return "<SITE('%d','%s', '%s',%s,'%s','%s', '%s', '%s','%s', '%d')>" % (
            self.id_sito,
            self.sito,
            self.nazione,
            self.regione,
            self.comune,
            self.descrizione,
            self.provincia,
            self.definizione_sito,
            self.sito_path,
            self.find_check
        )
