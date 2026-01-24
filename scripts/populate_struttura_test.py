#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to populate test data for Struttura form.
Run from QGIS Python console.
"""

import os
import sys

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.dirname(script_dir)
sys.path.insert(0, plugin_dir)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

# Test data for 5 struttura records with ALL fields filled
# Note: tableWidget fields use list of lists format
STRUTTURA_TEST_DATA = [
    {
        'sito': 'Sito_Test_AR',
        'sigla_struttura': 'AR',
        'numero_struttura': 1,
        'categoria_struttura': 'Architettura rupestre',
        'tipologia_struttura': 'Chiesa rupestre',
        'definizione_struttura': 'Chiesa ipogea monoabsidata',
        'descrizione': '''Struttura ipogea scavata nella roccia calcarea, costituita da un unico ambiente rettangolare con abside semicircolare orientata ad est.
Le pareti presentano tracce di intonaco dipinto con motivi geometrici e figure sacre.
Il soffitto è piano nella navata e a semicupola nell'abside.
L'ingresso originario si apriva sul lato occidentale, attualmente parzialmente ostruito da crolli.
Sono visibili nicchie laterali utilizzate probabilmente come depositi liturgici.
Il pavimento mostra tracce di un battuto in cocciopesto.''',
        'interpretazione': '''La struttura è interpretabile come luogo di culto cristiano di epoca altomedievale,
probabilmente legato ad una comunità monastica. La tipologia architettonica e le tracce pittoriche
suggeriscono una datazione tra IX e XI secolo. La presenza di sepolture nell'area circostante
conferma l'uso cultuale prolungato nel tempo.''',
        'periodo_iniziale': 1,
        'fase_iniziale': 1,
        'periodo_finale': 2,
        'fase_finale': 2,
        'datazione_estesa': 'IX-XI secolo d.C.',
        'materiali_impiegati': "[['Calcare locale'], ['Malta di calce'], ['Intonaco dipinto'], ['Cocciopesto']]",
        'elementi_strutturali': "[['Abside', 'Semicircolare orientata ad Est'], ['Navata', 'Rettangolare unica'], ['Ingresso', 'Lato occidentale'], ['Nicchie', 'Laterali per depositi']]",
        'rapporti_struttura': "[['Si lega a', 'Struttura', 'AR', '2'], ['Copre', 'US', '100', ''], ['Taglia', 'US', '101', '']]",
        'misure_struttura': "[['Lunghezza', 'm', '8.50'], ['Larghezza', 'm', '4.20'], ['Altezza max', 'm', '3.10'], ['Diametro abside', 'm', '2.80']]",
        'data_compilazione': '15/01/2024',
        'nome_compilatore': 'Dott. Mario Rossi',
        'stato_conservazione': "[['Struttura muraria', 'Discreto'], ['Intonaci', 'Pessimo'], ['Copertura', 'Buono']]",
        'quota': 425.50,
        'relazione_topografica': 'Versante nord-orientale della gravina, a circa 15m dal fondo',
        'prospetto_ingresso': "[['Tipo', 'Architravato'], ['Larghezza', '1.20m'], ['Altezza', '1.80m']]",
        'orientamento_ingresso': 'Ovest',
        'articolazione': 'Monocellulare con abside',
        'n_ambienti': 1,
        'orientamento_ambienti': "[['Navata', 'Est-Ovest'], ['Abside', 'Est']]",
        'sviluppo_planimetrico': 'Longitudinale',
        'elementi_costitutivi': "[['Altare', 'Monolitico in pietra'], ['Sedili', 'Scavati nella roccia'], ['Acquasantiera', 'Incavata presso ingresso']]",
        'motivo_decorativo': 'Affreschi con scene cristologiche e santi, cornici geometriche',
        'potenzialita_archeologica': 'Alta - presenza di depositi stratificati non indagati',
        'manufatti': "[['Ceramica', 'Frammenti medievali'], ['Vetro', 'Frammenti di lampade'], ['Metallo', 'Chiodi e grappe']]",
        'elementi_datanti': 'Ceramica invetriata X-XI sec., moneta bizantina',
        'fasi_funzionali': "[['Fase 1', 'IX-X sec.', 'Impianto originario'], ['Fase 2', 'X-XI sec.', 'Ampliamento e decorazione'], ['Fase 3', 'XII sec.', 'Abbandono']]"
    },
    {
        'sito': 'Sito_Test_AR',
        'sigla_struttura': 'AR',
        'numero_struttura': 2,
        'categoria_struttura': 'Architettura rupestre',
        'tipologia_struttura': 'Abitazione rupestre',
        'definizione_struttura': 'Casa-grotta plurivano',
        'descrizione': '''Complesso abitativo ipogeo articolato in tre ambienti comunicanti, scavati nella calcarenite.
L'ambiente principale presenta pianta sub-rettangolare con nicchie perimetrali e focolare centrale.
I due ambienti secondari, più piccoli, erano probabilmente destinati a deposito e stalla.
Le pareti mostrano tracce di affumicatura e incisioni per l'alloggiamento di mensole.
Il soffitto è a volta ribassata, con fori di aerazione.''',
        'interpretazione': '''Abitazione rupestre tipica dell'insediamento contadino medievale della gravina.
La presenza del focolare e delle nicchie-dispensa indica un uso residenziale prolungato.
L'articolazione degli spazi riflette l'organizzazione familiare dell'epoca.''',
        'periodo_iniziale': 2,
        'fase_iniziale': 1,
        'periodo_finale': 3,
        'fase_finale': 1,
        'datazione_estesa': 'XI-XIV secolo d.C.',
        'materiali_impiegati': "[['Calcarenite'], ['Malta bastarda'], ['Legno per infissi']]",
        'elementi_strutturali': "[['Vano principale', 'Ambiente centrale con focolare'], ['Vano deposito', 'Ambiente laterale nord'], ['Vano stalla', 'Ambiente laterale sud']]",
        'rapporti_struttura': "[['Si appoggia a', 'Struttura', 'AR', '1'], ['Anteriore a', 'Struttura', 'AR', '3']]",
        'misure_struttura': "[['Lunghezza tot.', 'm', '12.00'], ['Larghezza max', 'm', '5.50'], ['Altezza', 'm', '2.40'], ['Superficie', 'mq', '45.00']]",
        'data_compilazione': '16/01/2024',
        'nome_compilatore': 'Dott.ssa Anna Bianchi',
        'stato_conservazione': "[['Pareti', 'Buono'], ['Soffitto', 'Discreto'], ['Pavimento', 'Discreto']]",
        'quota': 423.20,
        'relazione_topografica': 'Adiacente alla chiesa AR1, stesso livello',
        'prospetto_ingresso': "[['Tipo', 'Ad arco ribassato'], ['Larghezza', '1.00m'], ['Altezza', '1.60m']]",
        'orientamento_ingresso': 'Sud-Est',
        'articolazione': 'Pluricellulare comunicante',
        'n_ambienti': 3,
        'orientamento_ambienti': "[['Vano principale', 'Nord-Sud'], ['Deposito', 'Est'], ['Stalla', 'Ovest']]",
        'sviluppo_planimetrico': 'Irregolare aggregato',
        'elementi_costitutivi': "[['Focolare', 'Centrale con cappa'], ['Mangiatoia', 'Nel vano stalla'], ['Nicchie', 'Perimetrali multiple']]",
        'motivo_decorativo': 'Assente',
        'potenzialita_archeologica': 'Media - depositi parzialmente disturbati',
        'manufatti': "[['Ceramica', 'Uso domestico medievale'], ['Osso', 'Resti faunistici'], ['Litico', 'Macina in pietra']]",
        'elementi_datanti': 'Ceramica acroma medievale, moneta angioina',
        'fasi_funzionali': "[['Fase 1', 'XI-XII sec.', 'Prima occupazione'], ['Fase 2', 'XIII-XIV sec.', 'Ampliamento'], ['Fase 3', 'XV sec.', 'Abbandono']]"
    },
    {
        'sito': 'Sito_Test_AR',
        'sigla_struttura': 'AR',
        'numero_struttura': 3,
        'categoria_struttura': 'Architettura rupestre',
        'tipologia_struttura': 'Cisterna',
        'definizione_struttura': 'Cisterna ipogea a bottiglia',
        'descrizione': '''Cisterna scavata nella roccia con tipica sezione a bottiglia.
Il collo superiore presenta un'apertura circolare di circa 60 cm di diametro.
Il corpo inferiore si allarga fino a raggiungere un diametro massimo di 3.50 m.
Le pareti interne sono rivestite con cocciopesto idraulico.
Sul fondo sono visibili tracce di depositi limosi.''',
        'interpretazione': '''Sistema di approvvigionamento idrico a servizio dell'insediamento rupestre.
La capacità stimata di circa 25 mc indica un utilizzo comunitario.
La posizione in prossimità delle abitazioni conferma la funzione pubblica.''',
        'periodo_iniziale': 1,
        'fase_iniziale': 2,
        'periodo_finale': 3,
        'fase_finale': 2,
        'datazione_estesa': 'X-XV secolo d.C.',
        'materiali_impiegati': "[['Calcare'], ['Cocciopesto idraulico'], ['Malta idraulica']]",
        'elementi_strutturali': "[['Imboccatura', 'Circolare con vera in pietra'], ['Corpo', 'A bottiglia'], ['Fondo', 'Concavo']]",
        'rapporti_struttura': "[['Posteriore a', 'Struttura', 'AR', '2'], ['Serve', 'Struttura', 'AR', '1']]",
        'misure_struttura': "[['Profondità', 'm', '4.80'], ['Diametro imboccatura', 'm', '0.60'], ['Diametro max', 'm', '3.50'], ['Capacità', 'mc', '25.00']]",
        'data_compilazione': '17/01/2024',
        'nome_compilatore': 'Dott. Luigi Verdi',
        'stato_conservazione': "[['Rivestimento', 'Discreto'], ['Struttura', 'Buono'], ['Imboccatura', 'Restaurata']]",
        'quota': 422.80,
        'relazione_topografica': 'Area centrale dell insediamento, tra AR1 e AR2',
        'prospetto_ingresso': "[['Tipo', 'Circolare'], ['Diametro', '0.60m']]",
        'orientamento_ingresso': 'Verticale',
        'articolazione': 'Monocamerale a bottiglia',
        'n_ambienti': 1,
        'orientamento_ambienti': "[['Camera', 'Verticale']]",
        'sviluppo_planimetrico': 'Circolare',
        'elementi_costitutivi': "[['Vera', 'In blocchi di pietra'], ['Canaletta', 'Di adduzione acque'], ['Gradini', 'Per discesa manutenzione']]",
        'motivo_decorativo': 'Assente',
        'potenzialita_archeologica': 'Alta - depositi sul fondo non scavati',
        'manufatti': "[['Ceramica', 'Frammenti di brocche'], ['Corda', 'Resti carbonizzati']]",
        'elementi_datanti': 'Ceramica invetriata XI-XII sec.',
        'fasi_funzionali': "[['Fase 1', 'X-XI sec.', 'Costruzione'], ['Fase 2', 'XII-XIV sec.', 'Uso continuativo'], ['Fase 3', 'XV sec.', 'Abbandono e riempimento']]"
    },
    {
        'sito': 'Sito_Test_AR',
        'sigla_struttura': 'AR',
        'numero_struttura': 4,
        'categoria_struttura': 'Architettura rupestre',
        'tipologia_struttura': 'Frantoio ipogeo',
        'definizione_struttura': 'Trappeto rupestre con vasche',
        'descrizione': '''Impianto produttivo per la lavorazione delle olive, interamente scavato nella roccia.
L'ambiente principale ospita la macina circolare con canale di scolo.
Due vasche laterali comunicanti servivano per la decantazione dell olio.
Nicchie perimetrali erano destinate allo stoccaggio delle giare.
Tracce di usura sulla macina indicano un uso prolungato e intensivo.''',
        'interpretazione': '''Frantoio comunitario al servizio dell insediamento rupestre.
La presenza di due vasche di decantazione indica una produzione su scala medio-grande.
L impianto era probabilmente gestito dalla comunità monastica della chiesa AR1.''',
        'periodo_iniziale': 2,
        'fase_iniziale': 2,
        'periodo_finale': 3,
        'fase_finale': 1,
        'datazione_estesa': 'XII-XIV secolo d.C.',
        'materiali_impiegati': "[['Calcare duro'], ['Basalto per macina'], ['Legno per torchio']]",
        'elementi_strutturali': "[['Macina', 'Circolare monolitica'], ['Vasche', 'Due comunicanti'], ['Torchio', 'Alloggiamento in roccia'], ['Nicchie', 'Per stoccaggio']]",
        'rapporti_struttura': "[['Contemporaneo a', 'Struttura', 'AR', '2'], ['Dipende da', 'Struttura', 'AR', '1']]",
        'misure_struttura': "[['Lunghezza', 'm', '10.00'], ['Larghezza', 'm', '6.00'], ['Altezza', 'm', '2.80'], ['Diametro macina', 'm', '1.80']]",
        'data_compilazione': '18/01/2024',
        'nome_compilatore': 'Dott.ssa Maria Neri',
        'stato_conservazione': "[['Macina', 'Buono'], ['Vasche', 'Discreto'], ['Pareti', 'Buono']]",
        'quota': 420.50,
        'relazione_topografica': 'Livello inferiore dell insediamento, accesso dalla gravina',
        'prospetto_ingresso': "[['Tipo', 'Rettangolare'], ['Larghezza', '1.50m'], ['Altezza', '2.00m']]",
        'orientamento_ingresso': 'Est',
        'articolazione': 'Monocellulare con annessi',
        'n_ambienti': 1,
        'orientamento_ambienti': "[['Ambiente produttivo', 'Est-Ovest']]",
        'sviluppo_planimetrico': 'Rettangolare allungato',
        'elementi_costitutivi': "[['Macina', 'Con ara e canale'], ['Vasche decantazione', 'n.2 comunicanti'], ['Contrappeso', 'Per torchio a leva']]",
        'motivo_decorativo': 'Croce incisa presso ingresso',
        'potenzialita_archeologica': 'Media - impianto già documentato',
        'manufatti': "[['Ceramica', 'Giare da olio'], ['Pietra', 'Frammenti di macina'], ['Metallo', 'Cerchiature']]",
        'elementi_datanti': 'Ceramica da trasporto XIII sec., moneta sveva',
        'fasi_funzionali': "[['Fase 1', 'XII sec.', 'Impianto'], ['Fase 2', 'XIII sec.', 'Massima attività'], ['Fase 3', 'XIV sec.', 'Dismissione']]"
    },
    {
        'sito': 'Sito_Test_AR',
        'sigla_struttura': 'AR',
        'numero_struttura': 5,
        'categoria_struttura': 'Architettura rupestre',
        'tipologia_struttura': 'Cripta sepolcrale',
        'definizione_struttura': 'Ipogeo funerario con loculi',
        'descrizione': '''Camera sepolcrale ipogea con accesso tramite scala scavata nella roccia.
L ambiente presenta pianta rettangolare con loculi distribuiti su tre pareti.
I loculi sono disposti su due ordini sovrapposti.
Tracce di chiusura in muratura sono visibili in alcuni loculi.
Il soffitto presenta una croce incisa al centro.''',
        'interpretazione': '''Area cimiteriale connessa alla chiesa AR1.
La disposizione dei loculi e la presenza della croce indicano un uso cristiano.
Il numero di sepolture (12 loculi) suggerisce una destinazione familiare o comunitaria ristretta.''',
        'periodo_iniziale': 1,
        'fase_iniziale': 1,
        'periodo_finale': 2,
        'fase_finale': 1,
        'datazione_estesa': 'IX-XI secolo d.C.',
        'materiali_impiegati': "[['Calcare'], ['Malta per chiusure'], ['Intonaco']]",
        'elementi_strutturali': "[['Scala accesso', 'n.8 gradini'], ['Camera', 'Rettangolare'], ['Loculi', 'n.12 su due ordini']]",
        'rapporti_struttura': "[['Pertinente a', 'Struttura', 'AR', '1'], ['Anteriore a', 'Struttura', 'AR', '2']]",
        'misure_struttura': "[['Lunghezza', 'm', '4.00'], ['Larghezza', 'm', '3.00'], ['Altezza', 'm', '2.20'], ['Prof. loculi', 'm', '1.80']]",
        'data_compilazione': '19/01/2024',
        'nome_compilatore': 'Dott. Paolo Gialli',
        'stato_conservazione': "[['Loculi', 'Discreto'], ['Scala', 'Buono'], ['Soffitto', 'Buono']]",
        'quota': 424.00,
        'relazione_topografica': 'Adiacente all abside della chiesa AR1, accesso esterno',
        'prospetto_ingresso': "[['Tipo', 'Rettangolare con scala'], ['Larghezza', '0.80m'], ['Altezza', '1.20m']]",
        'orientamento_ingresso': 'Nord',
        'articolazione': 'Monocamerale con loculi',
        'n_ambienti': 1,
        'orientamento_ambienti': "[['Camera sepolcrale', 'Nord-Sud']]",
        'sviluppo_planimetrico': 'Rettangolare',
        'elementi_costitutivi': "[['Loculi', 'n.12 arcuati'], ['Banchina', 'Perimetrale per deposizione'], ['Croce', 'Incisa sul soffitto']]",
        'motivo_decorativo': 'Croce greca sul soffitto, decorazioni geometriche nei loculi',
        'potenzialita_archeologica': 'Alta - loculi sigillati non indagati',
        'manufatti': "[['Ceramica', 'Lucerne'], ['Vetro', 'Balsamari'], ['Metallo', 'Fibule e anelli']]",
        'elementi_datanti': 'Lucerne a disco IX-X sec., monete bizantine',
        'fasi_funzionali': "[['Fase 1', 'IX sec.', 'Escavazione'], ['Fase 2', 'X-XI sec.', 'Uso sepolcrale'], ['Fase 3', 'XII sec.', 'Chiusura']]"
    }
]


def populate_struttura():
    """Populate struttura_table with test data"""

    conn = Connection()
    conn_str = conn.conn_str()

    try:
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()

        print("Connected to database successfully")
        print("=" * 60)

        inserted_count = 0

        for data in STRUTTURA_TEST_DATA:
            # Check if entry already exists
            search_dict = {
                'sito': f"'{data['sito']}'",
                'sigla_struttura': f"'{data['sigla_struttura']}'",
                'numero_struttura': data['numero_struttura']
            }

            existing = db_manager.query_bool(search_dict, 'STRUTTURA')

            if existing:
                print(f"  - {data['sigla_struttura']} {data['numero_struttura']} - already exists, skipping")
                continue

            # Get new ID
            new_id = db_manager.max_num_id('STRUTTURA', 'id_struttura') + 1

            # Create struttura object
            struttura_obj = db_manager.insert_struttura_values(
                new_id,
                data['sito'],
                data['sigla_struttura'],
                data['numero_struttura'],
                data['categoria_struttura'],
                data['tipologia_struttura'],
                data['definizione_struttura'],
                data['descrizione'],
                data['interpretazione'],
                data['periodo_iniziale'],
                data['fase_iniziale'],
                data['periodo_finale'],
                data['fase_finale'],
                data['datazione_estesa'],
                data['materiali_impiegati'],
                data['elementi_strutturali'],
                data['rapporti_struttura'],
                data['misure_struttura'],
                data.get('data_compilazione'),
                data.get('nome_compilatore'),
                data.get('stato_conservazione'),
                data.get('quota'),
                data.get('relazione_topografica'),
                data.get('prospetto_ingresso'),
                data.get('orientamento_ingresso'),
                data.get('articolazione'),
                data.get('n_ambienti'),
                data.get('orientamento_ambienti'),
                data.get('sviluppo_planimetrico'),
                data.get('elementi_costitutivi'),
                data.get('motivo_decorativo'),
                data.get('potenzialita_archeologica'),
                data.get('manufatti'),
                data.get('elementi_datanti'),
                data.get('fasi_funzionali')
            )

            # Insert into database
            db_manager.insert_data_session(struttura_obj)

            print(f"  + {data['sigla_struttura']} {data['numero_struttura']} ({data['tipologia_struttura']}) - inserted")
            inserted_count += 1

        print("\n" + "=" * 60)
        print(f"Total entries inserted: {inserted_count}")
        print("Done! Restart QGIS to see the test data in Struttura form.")
        print("\nTest records created:")
        print("  AR 1 - Chiesa rupestre")
        print("  AR 2 - Abitazione rupestre")
        print("  AR 3 - Cisterna")
        print("  AR 4 - Frantoio ipogeo")
        print("  AR 5 - Cripta sepolcrale")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    populate_struttura()
