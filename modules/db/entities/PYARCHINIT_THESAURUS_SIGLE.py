'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYARCHINIT_THESAURUS_SIGLE(object):
    # def __init__"
    def __init__(self,
                 id_thesaurus_sigle,
                 nome_tabella,
                 sigla,
                 sigla_estesa,
                 descrizione,
                 tipologia_sigla,
                 lingua
                 ):
        self.id_thesaurus_sigle = id_thesaurus_sigle  # 0
        self.nome_tabella = nome_tabella  # 1
        self.sigla = sigla  # 2
        self.sigla_estesa = sigla_estesa  # 3
        self.descrizione = descrizione  # 4
        self.tipologia_sigla = tipologia_sigla  # 5
        self.lingua = lingua

    # def __repr__"
    def __repr__(self):
        return "<PYARCHINIT_THESAURUS_SIGLE('%d', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_thesaurus_sigle,
            self.nome_tabella,
            self.sigla,
            self.sigla_estesa,
            self.descrizione,
            self.tipologia_sigla,
            self.lingua
        )
