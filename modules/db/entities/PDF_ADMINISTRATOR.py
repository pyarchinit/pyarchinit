'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PDF_ADMINISTRATOR(object):
    # def __init__"
    def __init__(self,
                 id_pdf_administrator,
                 table_name,
                 schema_griglia,
                 schema_fusione_celle,
                 modello
                 ):
        self.id_pdf_administrator = id_pdf_administrator  # 0
        self.table_name = table_name  # 1
        self.schema_griglia = schema_griglia  # 2
        self.schema_fusione_celle = schema_fusione_celle  # 3
        self.modello = modello  # 4

    # def __repr__"
    def __repr__(self):
        return "<PDF_ADMINISTRATOR('%d', '%s', '%s', '%s', '%s')>" % (
            self.id_pdf_administrator,  # 0
            self.table_name,  # 1
            self.schema_griglia,  # 2
            self.schema_fusione_celle,  # 3
            self.modello  # 4
        )
