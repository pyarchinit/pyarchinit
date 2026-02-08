'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
import uuid


class PERIODIZZAZIONE(object):
    # def __init__"
    def __init__(self,
                 id_perfas,
                 sito,
                 periodo,
                 fase,
                 cron_iniziale,
                 cron_finale,
                 descrizione,
                 datazione_estesa,
                 cont_per,
                 entity_uuid=None
                 ):
        self.id_perfas = id_perfas  # 0
        self.sito = sito  # 1
        self.periodo = periodo  # 2
        self.fase = fase  # 3
        self.cron_iniziale = cron_iniziale  # 4
        self.cron_finale = cron_finale  # 5
        self.descrizione = descrizione  # 6
        self.datazione_estesa = datazione_estesa  # 7
        self.cont_per = cont_per  # 8
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    # def __repr__"
    def __repr__(self):
        return "<PERIODIZZAZIONE('%d', '%s', '%d', '%s', '%d', '%d', '%s', '%s', '%d')>" % (
            self.id_perfas,
            self.sito,
            self.periodo,
            self.fase,
            self.cron_iniziale,
            self.cron_finale,
            self.descrizione,
            self.datazione_estesa,
            self.cont_per
        )
