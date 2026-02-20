import uuid


class PRESENZE(object):
    def __init__(self,
                 id_presenza,         # 0
                 sito,                # 1
                 id_personale,        # 2
                 data,                # 3
                 ora_ingresso,        # 4
                 ora_uscita,          # 5
                 ore_ordinarie,       # 6
                 ore_straordinario,   # 7
                 tipo_giornata,       # 8
                 turno,               # 9
                 area_lavoro,         # 10
                 note,                # 11
                 costo_giornata,      # 12
                 entity_uuid=None     # 13
                 ):
        self.id_presenza = id_presenza
        self.sito = sito
        self.id_personale = id_personale
        self.data = data
        self.ora_ingresso = ora_ingresso
        self.ora_uscita = ora_uscita
        self.ore_ordinarie = ore_ordinarie
        self.ore_straordinario = ore_straordinario
        self.tipo_giornata = tipo_giornata
        self.turno = turno
        self.area_lavoro = area_lavoro
        self.note = note
        self.costo_giornata = costo_giornata
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<PRESENZE('%d','%s','%d','%s')>" % (
            self.id_presenza, self.sito, self.id_personale, self.data)
