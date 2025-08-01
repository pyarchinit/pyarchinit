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
                 lingua,
                 order_layer=0,
                 id_parent=None,
                 parent_sigla=None,
                 hierarchy_level=0
                 ):
        self.id_thesaurus_sigle = id_thesaurus_sigle  # 0
        self.nome_tabella = nome_tabella  # 1
        self.sigla = sigla  # 2
        self.sigla_estesa = sigla_estesa  # 3
        self.descrizione = descrizione  # 4
        self.tipologia_sigla = tipologia_sigla  # 5
        self.lingua = lingua  # 6
        self.order_layer = order_layer  # 7
        self.id_parent = id_parent  # 8
        self.parent_sigla = parent_sigla  # 9
        self.hierarchy_level = hierarchy_level  # 10

    # def __repr__"
    def __repr__(self):
        return "<PYARCHINIT_THESAURUS_SIGLE('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%d')>" % (
            self.id_thesaurus_sigle,
            self.nome_tabella,
            self.sigla,
            self.sigla_estesa,
            self.descrizione if self.descrizione is not None else '',
            self.tipologia_sigla,
            self.lingua,
            self.order_layer,
            self.id_parent if self.id_parent is not None else 'None',
            self.parent_sigla if self.parent_sigla is not None else 'None',
            self.hierarchy_level
        )
