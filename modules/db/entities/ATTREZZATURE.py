import uuid


class ATTREZZATURE(object):
    def __init__(self,
                 id_attrezzatura,     # 0
                 sito,                # 1
                 codice_inventario,   # 2
                 nome,                # 3
                 categoria,           # 4
                 marca,               # 5
                 modello,             # 6
                 numero_serie,        # 7
                 proprieta,           # 8
                 data_acquisto,       # 9
                 costo_acquisto,      # 10
                 costo_noleggio_giorno, # 11
                 stato,               # 12
                 assegnato_a,         # 13
                 data_ultima_manutenzione,    # 14
                 data_prossima_manutenzione,  # 15
                 note,                # 16
                 entity_uuid=None     # 17
                 ):
        self.id_attrezzatura = id_attrezzatura
        self.sito = sito
        self.codice_inventario = codice_inventario
        self.nome = nome
        self.categoria = categoria
        self.marca = marca
        self.modello = modello
        self.numero_serie = numero_serie
        self.proprieta = proprieta
        self.data_acquisto = data_acquisto
        self.costo_acquisto = costo_acquisto
        self.costo_noleggio_giorno = costo_noleggio_giorno
        self.stato = stato
        self.assegnato_a = assegnato_a
        self.data_ultima_manutenzione = data_ultima_manutenzione
        self.data_prossima_manutenzione = data_prossima_manutenzione
        self.note = note
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<ATTREZZATURE('%d','%s','%s','%s')>" % (
            self.id_attrezzatura, self.sito, self.codice_inventario, self.nome)
