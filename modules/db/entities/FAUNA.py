'''
Created on 2024
Fauna entity for SCHEDA FR (Fauna Record Sheet)

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
import uuid


class FAUNA(object):
    def __init__(self,
                 id_fauna,
                 id_us,
                 sito,
                 area,
                 saggio,
                 us,
                 datazione_us,
                 responsabile_scheda,
                 data_compilazione,
                 documentazione_fotografica,
                 metodologia_recupero,
                 contesto,
                 descrizione_contesto,
                 resti_connessione_anatomica,
                 tipologia_accumulo,
                 deposizione,
                 numero_stimato_resti,
                 numero_minimo_individui,
                 specie,
                 parti_scheletriche,
                 specie_psi,
                 misure_ossa,
                 stato_frammentazione,
                 tracce_combustione,
                 combustione_altri_materiali_us,
                 tipo_combustione,
                 segni_tafonomici_evidenti,
                 caratterizzazione_segni_tafonomici,
                 stato_conservazione,
                 alterazioni_morfologiche,
                 note_terreno_giacitura,
                 campionature_effettuate,
                 affidabilita_stratigrafica,
                 classi_reperti_associazione,
                 osservazioni,
                 interpretazione,
                 entity_uuid=None
                 ):
        self.id_fauna = id_fauna
        self.id_us = id_us
        self.sito = sito
        self.area = area
        self.saggio = saggio
        self.us = us
        self.datazione_us = datazione_us
        self.responsabile_scheda = responsabile_scheda
        self.data_compilazione = data_compilazione
        self.documentazione_fotografica = documentazione_fotografica
        self.metodologia_recupero = metodologia_recupero
        self.contesto = contesto
        self.descrizione_contesto = descrizione_contesto
        self.resti_connessione_anatomica = resti_connessione_anatomica
        self.tipologia_accumulo = tipologia_accumulo
        self.deposizione = deposizione
        self.numero_stimato_resti = numero_stimato_resti
        self.numero_minimo_individui = numero_minimo_individui
        self.specie = specie
        self.parti_scheletriche = parti_scheletriche
        self.specie_psi = specie_psi
        self.misure_ossa = misure_ossa
        self.stato_frammentazione = stato_frammentazione
        self.tracce_combustione = tracce_combustione
        self.combustione_altri_materiali_us = combustione_altri_materiali_us
        self.tipo_combustione = tipo_combustione
        self.segni_tafonomici_evidenti = segni_tafonomici_evidenti
        self.caratterizzazione_segni_tafonomici = caratterizzazione_segni_tafonomici
        self.stato_conservazione = stato_conservazione
        self.alterazioni_morfologiche = alterazioni_morfologiche
        self.note_terreno_giacitura = note_terreno_giacitura
        self.campionature_effettuate = campionature_effettuate
        self.affidabilita_stratigrafica = affidabilita_stratigrafica
        self.classi_reperti_associazione = classi_reperti_associazione
        self.osservazioni = osservazioni
        self.interpretazione = interpretazione
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<FAUNA('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_fauna,
            self.id_us,
            self.sito,
            self.area,
            self.saggio,
            self.us,
            self.datazione_us,
            self.responsabile_scheda,
            self.data_compilazione,
            self.documentazione_fotografica,
            self.metodologia_recupero,
            self.contesto,
            self.descrizione_contesto,
            self.resti_connessione_anatomica,
            self.tipologia_accumulo,
            self.deposizione,
            self.numero_stimato_resti,
            self.numero_minimo_individui,
            self.specie,
            self.parti_scheletriche,
            self.specie_psi,
            self.misure_ossa,
            self.stato_frammentazione,
            self.tracce_combustione,
            self.combustione_altri_materiali_us,
            self.tipo_combustione,
            self.segni_tafonomici_evidenti,
            self.caratterizzazione_segni_tafonomici,
            self.stato_conservazione,
            self.alterazioni_morfologiche,
            self.note_terreno_giacitura,
            self.campionature_effettuate,
            self.affidabilita_stratigrafica,
            self.classi_reperti_associazione,
            self.osservazioni,
            self.interpretazione
        )
