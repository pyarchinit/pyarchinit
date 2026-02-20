import uuid


class BUDGET(object):
    def __init__(self,
                 id_budget,           # 0
                 sito,                # 1
                 anno,                # 2
                 categoria,           # 3
                 descrizione,         # 4
                 importo_previsto,    # 5
                 importo_effettivo,   # 6
                 data_registrazione,  # 7
                 data_spesa,          # 8
                 fornitore,           # 9
                 numero_fattura,      # 10
                 note,                # 11
                 entity_uuid=None     # 12
                 ):
        self.id_budget = id_budget
        self.sito = sito
        self.anno = anno
        self.categoria = categoria
        self.descrizione = descrizione
        self.importo_previsto = importo_previsto
        self.importo_effettivo = importo_effettivo
        self.data_registrazione = data_registrazione
        self.data_spesa = data_spesa
        self.fornitore = fornitore
        self.numero_fattura = numero_fattura
        self.note = note
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<BUDGET('%d','%s','%d','%s')>" % (
            self.id_budget, self.sito, self.anno, self.categoria)
