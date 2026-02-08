'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
import uuid


class STRUTTURA(object):
    def __init__(self,
                 id_struttura,
                 sito,
                 sigla_struttura,
                 numero_struttura,
                 categoria_struttura,
                 tipologia_struttura,
                 definizione_struttura,
                 descrizione,
                 interpretazione,
                 periodo_iniziale,
                 fase_iniziale,
                 periodo_finale,
                 fase_finale,
                 datazione_estesa,
                 materiali_impiegati,
                 elementi_strutturali,
                 rapporti_struttura,
                 misure_struttura,
                 # Nuovi campi per scheda struttura AR
                 data_compilazione=None,
                 nome_compilatore=None,
                 stato_conservazione=None,
                 quota=None,
                 relazione_topografica=None,
                 prospetto_ingresso=None,
                 orientamento_ingresso=None,
                 articolazione=None,
                 n_ambienti=None,
                 orientamento_ambienti=None,
                 sviluppo_planimetrico=None,
                 elementi_costitutivi=None,
                 motivo_decorativo=None,
                 potenzialita_archeologica=None,
                 manufatti=None,
                 elementi_datanti=None,
                 fasi_funzionali=None,
                 entity_uuid=None
                 ):
        self.id_struttura = id_struttura  # 0
        self.sito = sito  # 1
        self.sigla_struttura = sigla_struttura  # 2
        self.numero_struttura = numero_struttura  # 3
        self.categoria_struttura = categoria_struttura  # 4
        self.tipologia_struttura = tipologia_struttura  # 5
        self.definizione_struttura = definizione_struttura  # 6
        self.descrizione = descrizione  # 7
        self.interpretazione = interpretazione  # 8
        self.periodo_iniziale = periodo_iniziale  # 9
        self.fase_iniziale = fase_iniziale  # 10
        self.periodo_finale = periodo_finale  # 11
        self.fase_finale = fase_finale  # 12
        self.datazione_estesa = datazione_estesa  # 13
        self.materiali_impiegati = materiali_impiegati  # 14
        self.elementi_strutturali = elementi_strutturali  # 15
        self.rapporti_struttura = rapporti_struttura  # 16
        self.misure_struttura = misure_struttura  # 17
        # Nuovi campi per scheda struttura AR
        self.data_compilazione = data_compilazione  # 18
        self.nome_compilatore = nome_compilatore  # 19
        self.stato_conservazione = stato_conservazione  # 20
        self.quota = quota  # 21
        self.relazione_topografica = relazione_topografica  # 22
        self.prospetto_ingresso = prospetto_ingresso  # 23
        self.orientamento_ingresso = orientamento_ingresso  # 24
        self.articolazione = articolazione  # 25
        self.n_ambienti = n_ambienti  # 26
        self.orientamento_ambienti = orientamento_ambienti  # 27
        self.sviluppo_planimetrico = sviluppo_planimetrico  # 28
        self.elementi_costitutivi = elementi_costitutivi  # 29
        self.motivo_decorativo = motivo_decorativo  # 30
        self.potenzialita_archeologica = potenzialita_archeologica  # 31
        self.manufatti = manufatti  # 32
        self.elementi_datanti = elementi_datanti  # 33
        self.fasi_funzionali = fasi_funzionali  # 34
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<STRUTTURA('%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_struttura,
            self.sito,
            self.sigla_struttura,
            self.numero_struttura,
            self.categoria_struttura,
            self.tipologia_struttura,
            self.definizione_struttura,
            self.descrizione,
            self.interpretazione,
            self.periodo_iniziale,
            self.fase_iniziale,
            self.periodo_finale,
            self.fase_finale,
            self.datazione_estesa,
            self.materiali_impiegati,
            self.elementi_strutturali,
            self.rapporti_struttura,
            self.misure_struttura
        )
