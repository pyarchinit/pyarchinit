import uuid


class PERSONALE(object):
    def __init__(self,
                 id_personale,        # 0
                 sito,                # 1
                 nome,                # 2
                 cognome,             # 3
                 ruolo,               # 4
                 qualifica,           # 5
                 codice_fiscale,      # 6
                 email,               # 7
                 telefono,            # 8
                 data_nascita,        # 9
                 indirizzo,           # 10
                 tipo_contratto,      # 11
                 data_inizio_contratto, # 12
                 data_fine_contratto,   # 13
                 tariffa_oraria,      # 14
                 tariffa_giornaliera, # 15
                 iban,                # 16
                 note,                # 17
                 attivo,              # 18
                 entity_uuid=None     # 19
                 ):
        self.id_personale = id_personale
        self.sito = sito
        self.nome = nome
        self.cognome = cognome
        self.ruolo = ruolo
        self.qualifica = qualifica
        self.codice_fiscale = codice_fiscale
        self.email = email
        self.telefono = telefono
        self.data_nascita = data_nascita
        self.indirizzo = indirizzo
        self.tipo_contratto = tipo_contratto
        self.data_inizio_contratto = data_inizio_contratto
        self.data_fine_contratto = data_fine_contratto
        self.tariffa_oraria = tariffa_oraria
        self.tariffa_giornaliera = tariffa_giornaliera
        self.iban = iban
        self.note = note
        self.attivo = attivo
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<PERSONALE('%d','%s','%s','%s')>" % (
            self.id_personale, self.sito, self.nome, self.cognome)
