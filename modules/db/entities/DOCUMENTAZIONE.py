'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class DOCUMENTAZIONE(object):
    # def __init__"
    def __init__(self,
                 id_documentazione,  # 0
                 sito,  # 1
                 nome_doc,  # 2
                 data,  # 3
                 tipo_documentazione,  # 4
                 sorgente,  # 5
                 scala,  # 6
                 disegnatore,  # 7
                 note,  # 8
                 ):
        self.id_documentazione = id_documentazione  # 0
        self.sito = sito  # 1
        self.nome_doc = nome_doc  # 2
        self.data = data  # 3
        self.tipo_documentazione = tipo_documentazione  # 4
        self.sorgente = sorgente  # 5
        self.scala = scala  # 6
        self.disegnatore = disegnatore  # 7
        self.note = note  # 8

        # def __repr__"

    def __repr__(self):
        return "<DOCUMENTAZIONE('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_documentazione,  # 0
            self.sito,  # 1
            self.nome_doc,  # 2
            self.data,  # 3
            self.tipo_documentazione,  # 4
            self.sorgente,  # 5
            self.scala,  # 6
            self.disegnatore,  # 7
            self.note  # 8
        )
