-- Test data for Struttura form - 5 complete records
-- Run this SQL in your PyArchInit database (PostgreSQL)

-- First, ensure the site exists
INSERT INTO site_table (id_sito, sito, nazione, regione, comune, descrizione, provincia)
SELECT COALESCE(MAX(id_sito), 0) + 1, 'Sito_Test_AR', 'Italia', 'Puglia', 'Matera', 'Sito test per architettura rupestre', 'MT'
FROM site_table
WHERE NOT EXISTS (SELECT 1 FROM site_table WHERE sito = 'Sito_Test_AR');

-- AR 1 - Chiesa rupestre
INSERT INTO struttura_table (
    id_struttura, sito, sigla_struttura, numero_struttura,
    categoria_struttura, tipologia_struttura, definizione_struttura,
    descrizione, interpretazione,
    periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    datazione_estesa, materiali_impiegati, elementi_strutturali,
    rapporti_struttura, misure_struttura,
    data_compilazione, nome_compilatore, stato_conservazione, quota,
    relazione_topografica, prospetto_ingresso, orientamento_ingresso,
    articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico,
    elementi_costitutivi, motivo_decorativo, potenzialita_archeologica,
    manufatti, elementi_datanti, fasi_funzionali
)
SELECT
    COALESCE(MAX(id_struttura), 0) + 1,
    'Sito_Test_AR', 'AR', 1,
    'Architettura rupestre', 'Chiesa rupestre', 'Chiesa ipogea monoabsidata',
    'Struttura ipogea scavata nella roccia calcarea, costituita da un unico ambiente rettangolare con abside semicircolare orientata ad est. Le pareti presentano tracce di intonaco dipinto con motivi geometrici e figure sacre. Il soffitto è piano nella navata e a semicupola nell''abside. L''ingresso originario si apriva sul lato occidentale, attualmente parzialmente ostruito da crolli. Sono visibili nicchie laterali utilizzate probabilmente come depositi liturgici. Il pavimento mostra tracce di un battuto in cocciopesto.',
    'La struttura è interpretabile come luogo di culto cristiano di epoca altomedievale, probabilmente legato ad una comunità monastica. La tipologia architettonica e le tracce pittoriche suggeriscono una datazione tra IX e XI secolo. La presenza di sepolture nell''area circostante conferma l''uso cultuale prolungato nel tempo.',
    1, 1, 2, 2,
    'IX-XI secolo d.C.',
    '[[''Calcare locale''], [''Malta di calce''], [''Intonaco dipinto''], [''Cocciopesto'']]',
    '[[''Abside'', ''Semicircolare orientata ad Est''], [''Navata'', ''Rettangolare unica''], [''Ingresso'', ''Lato occidentale''], [''Nicchie'', ''Laterali per depositi'']]',
    '[[''Si lega a'', ''Struttura'', ''AR'', ''2''], [''Copre'', ''US'', ''100'', ''''], [''Taglia'', ''US'', ''101'', '''']]',
    '[[''Lunghezza'', ''m'', ''8.50''], [''Larghezza'', ''m'', ''4.20''], [''Altezza max'', ''m'', ''3.10''], [''Diametro abside'', ''m'', ''2.80'']]',
    '15/01/2024', 'Dott. Mario Rossi',
    '[[''Struttura muraria'', ''Discreto''], [''Intonaci'', ''Pessimo''], [''Copertura'', ''Buono'']]',
    425.50,
    'Versante nord-orientale della gravina, a circa 15m dal fondo',
    '[[''Tipo'', ''Architravato''], [''Larghezza'', ''1.20m''], [''Altezza'', ''1.80m'']]',
    'Ovest',
    'Monocellulare con abside', 1,
    '[[''Navata'', ''Est-Ovest''], [''Abside'', ''Est'']]',
    'Longitudinale',
    '[[''Altare'', ''Monolitico in pietra''], [''Sedili'', ''Scavati nella roccia''], [''Acquasantiera'', ''Incavata presso ingresso'']]',
    'Affreschi con scene cristologiche e santi, cornici geometriche',
    'Alta - presenza di depositi stratificati non indagati',
    '[[''Ceramica'', ''Frammenti medievali''], [''Vetro'', ''Frammenti di lampade''], [''Metallo'', ''Chiodi e grappe'']]',
    'Ceramica invetriata X-XI sec., moneta bizantina',
    '[[''Fase 1'', ''IX-X sec.'', ''Impianto originario''], [''Fase 2'', ''X-XI sec.'', ''Ampliamento e decorazione''], [''Fase 3'', ''XII sec.'', ''Abbandono'']]'
FROM struttura_table
WHERE NOT EXISTS (SELECT 1 FROM struttura_table WHERE sito = 'Sito_Test_AR' AND sigla_struttura = 'AR' AND numero_struttura = 1);

-- AR 2 - Abitazione rupestre
INSERT INTO struttura_table (
    id_struttura, sito, sigla_struttura, numero_struttura,
    categoria_struttura, tipologia_struttura, definizione_struttura,
    descrizione, interpretazione,
    periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    datazione_estesa, materiali_impiegati, elementi_strutturali,
    rapporti_struttura, misure_struttura,
    data_compilazione, nome_compilatore, stato_conservazione, quota,
    relazione_topografica, prospetto_ingresso, orientamento_ingresso,
    articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico,
    elementi_costitutivi, motivo_decorativo, potenzialita_archeologica,
    manufatti, elementi_datanti, fasi_funzionali
)
SELECT
    COALESCE(MAX(id_struttura), 0) + 1,
    'Sito_Test_AR', 'AR', 2,
    'Architettura rupestre', 'Abitazione rupestre', 'Casa-grotta plurivano',
    'Complesso abitativo ipogeo articolato in tre ambienti comunicanti, scavati nella calcarenite. L''ambiente principale presenta pianta sub-rettangolare con nicchie perimetrali e focolare centrale. I due ambienti secondari, più piccoli, erano probabilmente destinati a deposito e stalla. Le pareti mostrano tracce di affumicatura e incisioni per l''alloggiamento di mensole. Il soffitto è a volta ribassata, con fori di aerazione.',
    'Abitazione rupestre tipica dell''insediamento contadino medievale della gravina. La presenza del focolare e delle nicchie-dispensa indica un uso residenziale prolungato. L''articolazione degli spazi riflette l''organizzazione familiare dell''epoca.',
    2, 1, 3, 1,
    'XI-XIV secolo d.C.',
    '[[''Calcarenite''], [''Malta bastarda''], [''Legno per infissi'']]',
    '[[''Vano principale'', ''Ambiente centrale con focolare''], [''Vano deposito'', ''Ambiente laterale nord''], [''Vano stalla'', ''Ambiente laterale sud'']]',
    '[[''Si appoggia a'', ''Struttura'', ''AR'', ''1''], [''Anteriore a'', ''Struttura'', ''AR'', ''3'']]',
    '[[''Lunghezza tot.'', ''m'', ''12.00''], [''Larghezza max'', ''m'', ''5.50''], [''Altezza'', ''m'', ''2.40''], [''Superficie'', ''mq'', ''45.00'']]',
    '16/01/2024', 'Dott.ssa Anna Bianchi',
    '[[''Pareti'', ''Buono''], [''Soffitto'', ''Discreto''], [''Pavimento'', ''Discreto'']]',
    423.20,
    'Adiacente alla chiesa AR1, stesso livello',
    '[[''Tipo'', ''Ad arco ribassato''], [''Larghezza'', ''1.00m''], [''Altezza'', ''1.60m'']]',
    'Sud-Est',
    'Pluricellulare comunicante', 3,
    '[[''Vano principale'', ''Nord-Sud''], [''Deposito'', ''Est''], [''Stalla'', ''Ovest'']]',
    'Irregolare aggregato',
    '[[''Focolare'', ''Centrale con cappa''], [''Mangiatoia'', ''Nel vano stalla''], [''Nicchie'', ''Perimetrali multiple'']]',
    'Assente',
    'Media - depositi parzialmente disturbati',
    '[[''Ceramica'', ''Uso domestico medievale''], [''Osso'', ''Resti faunistici''], [''Litico'', ''Macina in pietra'']]',
    'Ceramica acroma medievale, moneta angioina',
    '[[''Fase 1'', ''XI-XII sec.'', ''Prima occupazione''], [''Fase 2'', ''XIII-XIV sec.'', ''Ampliamento''], [''Fase 3'', ''XV sec.'', ''Abbandono'']]'
FROM struttura_table
WHERE NOT EXISTS (SELECT 1 FROM struttura_table WHERE sito = 'Sito_Test_AR' AND sigla_struttura = 'AR' AND numero_struttura = 2);

-- AR 3 - Cisterna
INSERT INTO struttura_table (
    id_struttura, sito, sigla_struttura, numero_struttura,
    categoria_struttura, tipologia_struttura, definizione_struttura,
    descrizione, interpretazione,
    periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    datazione_estesa, materiali_impiegati, elementi_strutturali,
    rapporti_struttura, misure_struttura,
    data_compilazione, nome_compilatore, stato_conservazione, quota,
    relazione_topografica, prospetto_ingresso, orientamento_ingresso,
    articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico,
    elementi_costitutivi, motivo_decorativo, potenzialita_archeologica,
    manufatti, elementi_datanti, fasi_funzionali
)
SELECT
    COALESCE(MAX(id_struttura), 0) + 1,
    'Sito_Test_AR', 'AR', 3,
    'Architettura rupestre', 'Cisterna', 'Cisterna ipogea a bottiglia',
    'Cisterna scavata nella roccia con tipica sezione a bottiglia. Il collo superiore presenta un''apertura circolare di circa 60 cm di diametro. Il corpo inferiore si allarga fino a raggiungere un diametro massimo di 3.50 m. Le pareti interne sono rivestite con cocciopesto idraulico. Sul fondo sono visibili tracce di depositi limosi.',
    'Sistema di approvvigionamento idrico a servizio dell''insediamento rupestre. La capacità stimata di circa 25 mc indica un utilizzo comunitario. La posizione in prossimità delle abitazioni conferma la funzione pubblica.',
    1, 2, 3, 2,
    'X-XV secolo d.C.',
    '[[''Calcare''], [''Cocciopesto idraulico''], [''Malta idraulica'']]',
    '[[''Imboccatura'', ''Circolare con vera in pietra''], [''Corpo'', ''A bottiglia''], [''Fondo'', ''Concavo'']]',
    '[[''Posteriore a'', ''Struttura'', ''AR'', ''2''], [''Serve'', ''Struttura'', ''AR'', ''1'']]',
    '[[''Profondità'', ''m'', ''4.80''], [''Diametro imboccatura'', ''m'', ''0.60''], [''Diametro max'', ''m'', ''3.50''], [''Capacità'', ''mc'', ''25.00'']]',
    '17/01/2024', 'Dott. Luigi Verdi',
    '[[''Rivestimento'', ''Discreto''], [''Struttura'', ''Buono''], [''Imboccatura'', ''Restaurata'']]',
    422.80,
    'Area centrale dell''insediamento, tra AR1 e AR2',
    '[[''Tipo'', ''Circolare''], [''Diametro'', ''0.60m'']]',
    'Verticale',
    'Monocamerale a bottiglia', 1,
    '[[''Camera'', ''Verticale'']]',
    'Circolare',
    '[[''Vera'', ''In blocchi di pietra''], [''Canaletta'', ''Di adduzione acque''], [''Gradini'', ''Per discesa manutenzione'']]',
    'Assente',
    'Alta - depositi sul fondo non scavati',
    '[[''Ceramica'', ''Frammenti di brocche''], [''Corda'', ''Resti carbonizzati'']]',
    'Ceramica invetriata XI-XII sec.',
    '[[''Fase 1'', ''X-XI sec.'', ''Costruzione''], [''Fase 2'', ''XII-XIV sec.'', ''Uso continuativo''], [''Fase 3'', ''XV sec.'', ''Abbandono e riempimento'']]'
FROM struttura_table
WHERE NOT EXISTS (SELECT 1 FROM struttura_table WHERE sito = 'Sito_Test_AR' AND sigla_struttura = 'AR' AND numero_struttura = 3);

-- AR 4 - Frantoio ipogeo
INSERT INTO struttura_table (
    id_struttura, sito, sigla_struttura, numero_struttura,
    categoria_struttura, tipologia_struttura, definizione_struttura,
    descrizione, interpretazione,
    periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    datazione_estesa, materiali_impiegati, elementi_strutturali,
    rapporti_struttura, misure_struttura,
    data_compilazione, nome_compilatore, stato_conservazione, quota,
    relazione_topografica, prospetto_ingresso, orientamento_ingresso,
    articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico,
    elementi_costitutivi, motivo_decorativo, potenzialita_archeologica,
    manufatti, elementi_datanti, fasi_funzionali
)
SELECT
    COALESCE(MAX(id_struttura), 0) + 1,
    'Sito_Test_AR', 'AR', 4,
    'Architettura rupestre', 'Frantoio ipogeo', 'Trappeto rupestre con vasche',
    'Impianto produttivo per la lavorazione delle olive, interamente scavato nella roccia. L''ambiente principale ospita la macina circolare con canale di scolo. Due vasche laterali comunicanti servivano per la decantazione dell''olio. Nicchie perimetrali erano destinate allo stoccaggio delle giare. Tracce di usura sulla macina indicano un uso prolungato e intensivo.',
    'Frantoio comunitario al servizio dell''insediamento rupestre. La presenza di due vasche di decantazione indica una produzione su scala medio-grande. L''impianto era probabilmente gestito dalla comunità monastica della chiesa AR1.',
    2, 2, 3, 1,
    'XII-XIV secolo d.C.',
    '[[''Calcare duro''], [''Basalto per macina''], [''Legno per torchio'']]',
    '[[''Macina'', ''Circolare monolitica''], [''Vasche'', ''Due comunicanti''], [''Torchio'', ''Alloggiamento in roccia''], [''Nicchie'', ''Per stoccaggio'']]',
    '[[''Contemporaneo a'', ''Struttura'', ''AR'', ''2''], [''Dipende da'', ''Struttura'', ''AR'', ''1'']]',
    '[[''Lunghezza'', ''m'', ''10.00''], [''Larghezza'', ''m'', ''6.00''], [''Altezza'', ''m'', ''2.80''], [''Diametro macina'', ''m'', ''1.80'']]',
    '18/01/2024', 'Dott.ssa Maria Neri',
    '[[''Macina'', ''Buono''], [''Vasche'', ''Discreto''], [''Pareti'', ''Buono'']]',
    420.50,
    'Livello inferiore dell''insediamento, accesso dalla gravina',
    '[[''Tipo'', ''Rettangolare''], [''Larghezza'', ''1.50m''], [''Altezza'', ''2.00m'']]',
    'Est',
    'Monocellulare con annessi', 1,
    '[[''Ambiente produttivo'', ''Est-Ovest'']]',
    'Rettangolare allungato',
    '[[''Macina'', ''Con ara e canale''], [''Vasche decantazione'', ''n.2 comunicanti''], [''Contrappeso'', ''Per torchio a leva'']]',
    'Croce incisa presso ingresso',
    'Media - impianto già documentato',
    '[[''Ceramica'', ''Giare da olio''], [''Pietra'', ''Frammenti di macina''], [''Metallo'', ''Cerchiature'']]',
    'Ceramica da trasporto XIII sec., moneta sveva',
    '[[''Fase 1'', ''XII sec.'', ''Impianto''], [''Fase 2'', ''XIII sec.'', ''Massima attività''], [''Fase 3'', ''XIV sec.'', ''Dismissione'']]'
FROM struttura_table
WHERE NOT EXISTS (SELECT 1 FROM struttura_table WHERE sito = 'Sito_Test_AR' AND sigla_struttura = 'AR' AND numero_struttura = 4);

-- AR 5 - Cripta sepolcrale
INSERT INTO struttura_table (
    id_struttura, sito, sigla_struttura, numero_struttura,
    categoria_struttura, tipologia_struttura, definizione_struttura,
    descrizione, interpretazione,
    periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    datazione_estesa, materiali_impiegati, elementi_strutturali,
    rapporti_struttura, misure_struttura,
    data_compilazione, nome_compilatore, stato_conservazione, quota,
    relazione_topografica, prospetto_ingresso, orientamento_ingresso,
    articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico,
    elementi_costitutivi, motivo_decorativo, potenzialita_archeologica,
    manufatti, elementi_datanti, fasi_funzionali
)
SELECT
    COALESCE(MAX(id_struttura), 0) + 1,
    'Sito_Test_AR', 'AR', 5,
    'Architettura rupestre', 'Cripta sepolcrale', 'Ipogeo funerario con loculi',
    'Camera sepolcrale ipogea con accesso tramite scala scavata nella roccia. L''ambiente presenta pianta rettangolare con loculi distribuiti su tre pareti. I loculi sono disposti su due ordini sovrapposti. Tracce di chiusura in muratura sono visibili in alcuni loculi. Il soffitto presenta una croce incisa al centro.',
    'Area cimiteriale connessa alla chiesa AR1. La disposizione dei loculi e la presenza della croce indicano un uso cristiano. Il numero di sepolture (12 loculi) suggerisce una destinazione familiare o comunitaria ristretta.',
    1, 1, 2, 1,
    'IX-XI secolo d.C.',
    '[[''Calcare''], [''Malta per chiusure''], [''Intonaco'']]',
    '[[''Scala accesso'', ''n.8 gradini''], [''Camera'', ''Rettangolare''], [''Loculi'', ''n.12 su due ordini'']]',
    '[[''Pertinente a'', ''Struttura'', ''AR'', ''1''], [''Anteriore a'', ''Struttura'', ''AR'', ''2'']]',
    '[[''Lunghezza'', ''m'', ''4.00''], [''Larghezza'', ''m'', ''3.00''], [''Altezza'', ''m'', ''2.20''], [''Prof. loculi'', ''m'', ''1.80'']]',
    '19/01/2024', 'Dott. Paolo Gialli',
    '[[''Loculi'', ''Discreto''], [''Scala'', ''Buono''], [''Soffitto'', ''Buono'']]',
    424.00,
    'Adiacente all''abside della chiesa AR1, accesso esterno',
    '[[''Tipo'', ''Rettangolare con scala''], [''Larghezza'', ''0.80m''], [''Altezza'', ''1.20m'']]',
    'Nord',
    'Monocamerale con loculi', 1,
    '[[''Camera sepolcrale'', ''Nord-Sud'']]',
    'Rettangolare',
    '[[''Loculi'', ''n.12 arcuati''], [''Banchina'', ''Perimetrale per deposizione''], [''Croce'', ''Incisa sul soffitto'']]',
    'Croce greca sul soffitto, decorazioni geometriche nei loculi',
    'Alta - loculi sigillati non indagati',
    '[[''Ceramica'', ''Lucerne''], [''Vetro'', ''Balsamari''], [''Metallo'', ''Fibule e anelli'']]',
    'Lucerne a disco IX-X sec., monete bizantine',
    '[[''Fase 1'', ''IX sec.'', ''Escavazione''], [''Fase 2'', ''X-XI sec.'', ''Uso sepolcrale''], [''Fase 3'', ''XII sec.'', ''Chiusura'']]'
FROM struttura_table
WHERE NOT EXISTS (SELECT 1 FROM struttura_table WHERE sito = 'Sito_Test_AR' AND sigla_struttura = 'AR' AND numero_struttura = 5);

-- Verify insertion
SELECT id_struttura, sigla_struttura, numero_struttura, tipologia_struttura,
       LEFT(descrizione, 50) as descrizione_preview
FROM struttura_table
WHERE sito = 'Sito_Test_AR'
ORDER BY numero_struttura;
