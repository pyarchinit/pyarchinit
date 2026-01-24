# Tutorial 21: Scheda UT - Unità Topografiche

## Introduzione

La **Scheda UT** (Unità Topografiche) è il modulo di PyArchInit dedicato alla documentazione delle ricognizioni archeologiche di superficie (survey). Permette di registrare i dati relativi alle concentrazioni di materiali, anomalie del terreno e siti individuati durante le prospezioni.

### Concetti Base

**Unità Topografica (UT):**
- Area delimitata con caratteristiche archeologiche omogenee
- Individuata durante ricognizione di superficie
- Definita da concentrazione di materiali o anomalie visibili

**Ricognizione (Survey):**
- Prospezione sistematica del territorio
- Raccolta dati su presenza antropica antica
- Documentazione senza scavo

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda UT** (o **TU form**)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **UT**

---

## Panoramica dell'Interfaccia

La scheda è organizzata in più tab per documentare tutti gli aspetti della ricognizione.

### Tab Principali

| # | Tab | Descrizione |
|---|-----|-------------|
| 1 | Identificazione | Progetto, Nr. UT, Localizzazione |
| 2 | Descrizione | Definizione, descrizione, interpretazione |
| 3 | Dati UT | Condizioni, metodologia, date |
| 4 | Analisi | Potenziale e rischio archeologico |

### Toolbar Principale

| Pulsante | Funzione |
|----------|----------|
| ⏮ First | Vai al primo record |
| ◀ Prev | Record precedente |
| ▶ Next | Record successivo |
| ⏭ Last | Vai all'ultimo record |
| 🔍 Search | Ricerca avanzata |
| 💾 Save | Salva record |
| 🗑 Delete | Elimina record |
| 📄 PDF | Esporta scheda PDF |
| 📋 **PDF List** | Esporta elenco UT in PDF |
| 📦 **GNA Export** | Esporta in formato GNA |
| 🗺 Show Layer | Visualizza layer su mappa |

---

## Campi Identificativi

### Progetto

**Campo**: `comboBox_progetto`
**Database**: `progetto`

Nome del progetto di ricognizione.

### Numero UT

**Campo**: `comboBox_nr_ut`
**Database**: `nr_ut`

Numero progressivo dell'Unità Topografica.

### UT Letterale

**Campo**: `lineEdit_ut_letterale`
**Database**: `ut_letterale`

Eventuale suffisso alfabetico (es. UT 15a, 15b).

---

## Campi Localizzazione

### Dati Amministrativi

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Nazione | `nazione` | Stato |
| Regione | `regione` | Regione amministrativa |
| Provincia | `provincia` | Provincia |
| Comune | `comune` | Comune |
| Frazione | `frazione` | Frazione/località |
| Località | `localita` | Toponimo locale |
| Indirizzo | `indirizzo` | Via/strada |
| Nr. civico | `nr_civico` | Numero civico |

### Dati Cartografici

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Carta IGM | `carta_topo_igm` | Foglio IGM |
| Carta CTR | `carta_ctr` | Elemento CTR |
| Foglio catastale | `foglio_catastale` | Riferimento catasto |

### Coordinate

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Coord. geografiche | `coord_geografiche` | Lat/Long (formato: lat, lon) |
| Coord. piane | `coord_piane` | UTM/Gauss-Boaga (formato: x, y) |
| Quota | `quota` | Altitudine s.l.m. |
| Precisione coord. | `coordinate_precision` | Accuratezza GPS in metri |

**⚠️ IMPORTANTE**: Le coordinate sono utilizzate per la generazione delle heatmap. Almeno uno tra `coord_geografiche` e `coord_piane` deve essere compilato per ogni UT.

---

## Campi Descrittivi

### Definizione UT

**Campo**: `comboBox_def_ut`
**Database**: `def_ut`
**Thesaurus**: Codice 12.7

Classificazione tipologica dell'UT. I valori sono caricati dal thesaurus e tradotti automaticamente nella lingua corrente.

**Valori standard:**
| Sigla | Italiano | Inglese |
|-------|----------|---------|
| scatter | Area di dispersione materiali | Material scatter |
| site | Sito archeologico | Archaeological site |
| anomaly | Anomalia del terreno | Terrain anomaly |
| structure | Struttura affiorante | Outcropping structure |
| concentration | Concentrazione reperti | Finds concentration |
| traces | Tracce antropiche | Anthropic traces |
| findspot | Rinvenimento sporadico | Sporadic find |
| negative | Esito negativo | Negative result |

### Descrizione UT

**Campo**: `textEdit_descrizione`
**Database**: `descrizione_ut`

Descrizione dettagliata dell'Unità Topografica.

**Contenuti:**
- Estensione e forma dell'area
- Densità dei materiali
- Caratteristiche del terreno
- Visibilità e condizioni

### Interpretazione UT

**Campo**: `textEdit_interpretazione`
**Database**: `interpretazione_ut`

Interpretazione funzionale/storica.

---

## Campi Survey con Thesaurus

I seguenti campi utilizzano il sistema thesaurus per garantire terminologia standardizzata e tradotta in 7 lingue (IT, EN, DE, ES, FR, AR, CA).

### Tipo Survey (12.1)

**Campo**: `comboBox_survey_type`
**Database**: `survey_type`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| intensive | Ricognizione intensiva | Ricognizione sistematica intensiva |
| extensive | Ricognizione estensiva | Ricognizione a campionamento |
| targeted | Ricognizione mirata | Indagine su aree specifiche |
| random | Campionamento casuale | Metodologia casuale |

### Copertura Vegetazione (12.2)

**Campo**: `comboBox_vegetation_coverage`
**Database**: `vegetation_coverage`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| none | Assente | Terreno nudo |
| sparse | Rada | Copertura < 25% |
| moderate | Moderata | Copertura 25-50% |
| dense | Densa | Copertura 50-75% |
| very_dense | Molto densa | Copertura > 75% |

### Metodo GPS (12.3)

**Campo**: `comboBox_gps_method`
**Database**: `gps_method`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| handheld | GPS portatile | Dispositivo GPS portatile |
| dgps | GPS differenziale | DGPS con stazione base |
| rtk | GPS RTK | Cinematico in tempo reale |
| total_station | Stazione totale | Rilievo con stazione totale |

### Condizione Superficie (12.4)

**Campo**: `comboBox_surface_condition`
**Database**: `surface_condition`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| ploughed | Arato | Campo arato di recente |
| stubble | Stoppie | Presenza di stoppie |
| pasture | Pascolo | Terreno a pascolo/prato |
| woodland | Bosco | Area boscata |
| urban | Urbano | Area urbana/edificata |

### Accessibilità (12.5)

**Campo**: `comboBox_accessibility`
**Database**: `accessibility`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| easy | Facile accesso | Nessuna restrizione |
| moderate_access | Accesso moderato | Alcune difficoltà |
| difficult | Accesso difficile | Problemi significativi |
| restricted | Accesso ristretto | Solo su autorizzazione |

### Condizioni Meteo (12.6)

**Campo**: `comboBox_weather_conditions`
**Database**: `weather_conditions`

| Sigla | Italiano | Descrizione |
|-------|----------|-------------|
| sunny | Soleggiato | Tempo sereno |
| cloudy | Nuvoloso | Condizioni nuvolose |
| rainy | Piovoso | Pioggia durante ricognizione |
| windy | Ventoso | Vento forte |

---

## Dati Ambientali

### Visibilità Percentuale

**Campo**: `spinBox_visibility_percent`
**Database**: `visibility_percent`

Percentuale di visibilità del suolo (0-100%). Valore numerico importante per il calcolo del potenziale archeologico.

### Andamento Terreno

**Campo**: `lineEdit_andamento_terreno_pendenza`
**Database**: `andamento_terreno_pendenza`

Morfologia e pendenza del terreno.

### Utilizzo Suolo

**Campo**: `lineEdit_utilizzo_suolo_vegetazione`
**Database**: `utilizzo_suolo_vegetazione`

Uso del suolo al momento della ricognizione.

---

## Dati Materiali

### Dimensioni UT

**Campo**: `lineEdit_dimensioni_ut`
**Database**: `dimensioni_ut`

Estensione in mq.

### Reperti per mq

**Campo**: `lineEdit_rep_per_mq`
**Database**: `rep_per_mq`

Densità materiali per metro quadro. Valore critico per il calcolo del potenziale.

### Reperti Datanti

**Campo**: `lineEdit_rep_datanti`
**Database**: `rep_datanti`

Descrizione materiali diagnostici.

---

## Cronologia

### Periodo I

| Campo | Database |
|-------|----------|
| Periodo I | `periodo_I` |
| Datazione I | `datazione_I` |
| Interpretazione I | `interpretazione_I` |

### Periodo II

| Campo | Database |
|-------|----------|
| Periodo II | `periodo_II` |
| Datazione II | `datazione_II` |
| Interpretazione II | `interpretazione_II` |

---

## Tab Analisi - Potenziale e Rischio Archeologico

Il tab **Analisi** fornisce strumenti avanzati per il calcolo automatico del potenziale e rischio archeologico.

### Potenziale Archeologico

Il sistema calcola un punteggio da 0 a 100 basato su diversi fattori pesati:

| Fattore | Peso | Descrizione | Come viene calcolato |
|---------|------|-------------|---------------------|
| Definizione UT | 30% | Tipo di evidenza archeologica | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, ecc. |
| Periodo storico | 25% | Cronologia dei materiali | Periodi antichi pesano di più (Preistorico = 90, Romano = 85, Medievale = 70, ecc.) |
| Densità reperti | 20% | Materiali per mq | >10/mq = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Condizione superficie | 15% | Visibilità e accessibilità | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentazione | 10% | Qualità della documentazione | Presenza foto = +20, bibliografia = +30, indagini = +50 |

**Classificazione del punteggio:**

| Punteggio | Livello | Colore | Significato |
|-----------|---------|--------|-------------|
| 80-100 | Alto | 🟢 Verde | Elevata probabilità di depositi significativi |
| 60-79 | Medio-Alto | 🟡 Giallo-Verde | Buona probabilità, consigliata verifica |
| 40-59 | Medio | 🟠 Arancione | Probabilità moderata |
| 20-39 | Basso | 🔴 Rosso | Bassa probabilità |
| 0-19 | Non valutabile | ⚫ Grigio | Dati insufficienti |

### Rischio Archeologico

Valuta il rischio di impatto/perdita del patrimonio:

| Fattore | Peso | Descrizione | Come viene calcolato |
|---------|------|-------------|---------------------|
| Accessibilità | 25% | Facilità di accesso all'area | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Uso del suolo | 25% | Attività agricole/edilizie | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Vincoli esistenti | 20% | Protezioni legali | Assenza vincoli = 80, vincolo paesaggistico = 40, vincolo archeologico = 10 |
| Indagini pregresse | 15% | Stato delle conoscenze | Nessuna indagine = 60, ricognizione = 40, scavo = 20 |
| Potenziale | 15% | Inversamente proporzionale al potenziale | Alto potenziale = alto rischio di perdita |

**Classificazione del rischio:**

| Punteggio | Livello | Colore | Azione raccomandata |
|-----------|---------|--------|---------------------|
| 75-100 | Alto | 🔴 Rosso | Intervento urgente, misure di tutela immediate |
| 50-74 | Medio | 🟠 Arancione | Monitoraggio attivo, valutare protezione |
| 25-49 | Basso | 🟡 Giallo | Monitoraggio periodico |
| 0-24 | Nullo | 🟢 Verde | Nessun intervento immediato necessario |

### Campi Database per l'Analisi

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Punteggio Potenziale | `potential_score` | Valore 0-100 calcolato |
| Punteggio Rischio | `risk_score` | Valore 0-100 calcolato |
| Fattori Potenziale | `potential_factors` | JSON con dettaglio fattori |
| Fattori Rischio | `risk_factors` | JSON con dettaglio fattori |
| Data Analisi | `analysis_date` | Timestamp del calcolo |
| Metodo Analisi | `analysis_method` | Algoritmo utilizzato |

---

## Layer Geometrici UT

PyArchInit gestisce tre tipi di geometrie per le Unità Topografiche:

### Tabelle Geometriche

| Layer | Tabella | Tipo Geometria | Uso |
|-------|---------|----------------|-----|
| UT Punti | `pyarchinit_ut_point` | Point | Localizzazione puntuale |
| UT Linee | `pyarchinit_ut_line` | LineString | Tracciati, percorsi |
| UT Poligoni | `pyarchinit_ut_polygon` | Polygon | Aree di dispersione |

### Creazione Layer UT

1. **Via QGIS Browser:**
   - Aprire il database in Browser
   - Localizzare la tabella `pyarchinit_ut_point/line/polygon`
   - Trascinare sulla mappa

2. **Via Menu PyArchInit:**
   - Menu **PyArchInit** > **GIS Tools** > **Load UT Layers**
   - Selezionare il tipo di geometria

### Collegamento UT-Geometria

Ogni record geometrico è collegato alla scheda UT tramite:

| Campo | Descrizione |
|-------|-------------|
| `progetto` | Nome progetto (deve corrispondere) |
| `nr_ut` | Numero UT (deve corrispondere) |

### Workflow Creazione Geometrie

1. **Attivare editing** sul layer UT desiderato
2. **Disegnare** la geometria sulla mappa
3. **Compilare** gli attributi `progetto` e `nr_ut`
4. **Salvare** il layer
5. **Verificare** il collegamento dalla scheda UT

---

## Generazione Heatmap

Il modulo di generazione heatmap permette di visualizzare la distribuzione spaziale del potenziale e del rischio archeologico.

### Requisiti Minimi

- **Almeno 2 UT** con coordinate valide (`coord_geografiche` O `coord_piane`)
- **Punteggi calcolati** per potenziale e/o rischio
- **CRS definito** nel progetto QGIS

### Metodi di Interpolazione

| Metodo | Descrizione | Quando usarlo |
|--------|-------------|---------------|
| **KDE** (Kernel Density) | Stima densità kernel gaussiana | Distribuzione continua, molti punti |
| **IDW** (Inverse Distance) | Peso inverso della distanza | Dati sparsi, valori puntuali importanti |
| **Grid** | Interpolazione su griglia regolare | Analisi sistematiche |

### Parametri Heatmap

| Parametro | Valore Default | Descrizione |
|-----------|----------------|-------------|
| Cell Size | 50 m | Risoluzione della griglia |
| Bandwidth (KDE) | Auto | Raggio di influenza |
| Power (IDW) | 2 | Esponente di ponderazione |

### Procedura Generazione

1. **Dalla scheda UT:**
   - Andare al tab **Analisi**
   - Verificare che i punteggi siano calcolati
   - Cliccare **Genera Heatmap**

2. **Selezione parametri:**
   - Tipo: Potenziale o Rischio
   - Metodo: KDE, IDW, o Grid
   - Cell size: tipicamente 25-100 m

3. **Output:**
   - Layer raster aggiunto a QGIS
   - Salvato in `pyarchinit_Raster_folder`
   - Simbologia applicata automaticamente

### Heatmap con Maschera Poligonale (GNA)

Per generare heatmap **all'interno di un'area di progetto** (es. perimetro di studio):

1. **Preparare il poligono** dell'area di progetto
2. **Usare GNA Export** (vedi sezione successiva)
3. Il sistema **maschera** automaticamente la heatmap al poligono

---

## Export GNA - Geoportale Nazionale Archeologia

### Cos'è il GNA?

Il **Geoportale Nazionale per l'Archeologia** (GNA) è il sistema informativo del Ministero della Cultura italiano per la gestione dei dati archeologici territoriali. PyArchInit supporta l'export nel formato GeoPackage standard GNA.

### Struttura GeoPackage GNA

| Layer | Tipo | Descrizione |
|-------|------|-------------|
| **MOPR** | Polygon | Area/Perimetro di progetto |
| **MOSI** | Point/Polygon | Siti archeologici (UT) |
| **VRP** | MultiPolygon | Carta del Potenziale Archeologico |
| **VRD** | MultiPolygon | Carta del Rischio Archeologico |

### Mapping Campi UT → MOSI GNA

| Campo GNA | Campo UT PyArchInit | Note |
|-----------|---------------------|------|
| ID | `{progetto}_{nr_ut}` | Identificativo composito |
| AMA | `def_ut` | Vocabolario controllato GNA |
| OGD | `interpretazione_ut` | Definizione oggetto |
| OGT | `geometria` | Tipo geometria |
| DES | `descrizione_ut` | Descrizione (max 10000 char) |
| OGM | `metodo_rilievo_e_ricognizione` | Modalità individuazione |
| DTSI | `periodo_I` → data | Data inizio (negativo per a.C.) |
| DTSF | `periodo_II` → data | Data fine |
| PRVN | `nazione` | Nazione |
| PVCR | `regione` | Regione |
| PVCP | `provincia` | Provincia |
| PVCC | `comune` | Comune |
| LCDQ | `quota` | Quota s.l.m. |

### Classificazione VRP (Potenziale)

| Range | Codice GNA | Etichetta | Colore |
|-------|------------|-----------|--------|
| 0-20 | NV | Non valutabile | Grigio |
| 20-40 | NU | Nullo | Verde |
| 40-60 | BA | Basso | Giallo |
| 60-80 | ME | Medio | Arancione |
| 80-100 | AL | Alto | Rosso |

### Classificazione VRD (Rischio)

| Range | Codice GNA | Etichetta | Colore |
|-------|------------|-----------|--------|
| 0-25 | NU | Nullo | Verde |
| 25-50 | BA | Basso | Giallo |
| 50-75 | ME | Medio | Arancione |
| 75-100 | AL | Alto | Rosso |

### Procedura Export GNA

1. **Preparazione dati:**
   - Verificare che tutte le UT abbiano coordinate
   - Calcolare i punteggi potenziale/rischio
   - Preparare il poligono dell'area di progetto (MOPR)

2. **Avvio export:**
   - Dalla scheda UT, cliccare **GNA Export**
   - Oppure menu **PyArchInit** > **GNA** > **Export**

3. **Configurazione:**
   ```
   Progetto: [seleziona progetto]
   Area di progetto: [seleziona layer poligono MOPR]
   Output: [percorso file .gpkg]

   ☑ Esporta MOSI (siti)
   ☑ Genera VRP (potenziale)
   ☑ Genera VRD (rischio)

   Metodo heatmap: KDE
   Cell size: 50 m
   ```

4. **Esecuzione:**
   - Cliccare **Esporta**
   - Attendere generazione (può richiedere alcuni minuti)
   - Il GeoPackage viene salvato nel percorso specificato

5. **Verifica output:**
   - Aprire il GeoPackage in QGIS
   - Verificare i layer MOPR, MOSI, VRP, VRD
   - Controllare che le geometrie VRP/VRD siano clippate al MOPR

### Validazione GNA

Per validare l'output contro le specifiche GNA:

1. Caricare il GeoPackage nel **template GNA ufficiale**
2. Verificare che i layer siano riconosciuti
3. Controllare i vocabolari controllati
4. Verificare le relazioni geometriche (MOSI dentro MOPR)

---

## Export PDF

### Scheda UT Singola

Esporta la scheda UT completa in formato PDF professionale.

**Contenuto:**
- Header con progetto e numero UT
- Sezione Identificazione
- Sezione Localizzazione
- Sezione Terreno
- Sezione Dati Survey
- Sezione Cronologia
- Sezione Analisi (potenziale/rischio con barre colorate)
- Sezione Documentazione

**Procedura:**
1. Selezionare il record UT
2. Cliccare il pulsante **PDF** nella toolbar
3. Il PDF viene salvato in `pyarchinit_PDF_folder`

### Elenco UT (PDF List)

Esporta un elenco tabellare di tutte le UT in formato landscape.

**Colonne:**
- UT, Progetto, Definizione, Interpretazione
- Comune, Coordinate, Periodo I, Periodo II
- Rep/m², Visibilità, Potenziale, Rischio

**Procedura:**
1. Caricare le UT da esportare (ricerca o visualizza tutto)
2. Cliccare il pulsante **PDF List** nella toolbar
3. Il PDF viene salvato come `Elenco_UT.pdf`

### Report Analisi UT

Genera un report dettagliato dell'analisi potenziale/rischio.

**Contenuto:**
1. Dati identificativi dell'UT
2. Sezione Potenziale Archeologico
   - Punteggio con indicatore grafico
   - Testo narrativo descrittivo
   - Tabella fattori con contributi
3. Sezione Rischio Archeologico
   - Punteggio con indicatore grafico
   - Testo narrativo con raccomandazioni
   - Tabella fattori con contributi
4. Sezione Metodologia

---

## Workflow Operativo Completo

### Fase 1: Setup Progetto

1. **Creare nuovo progetto** in PyArchInit o usarne uno esistente
2. **Definire l'area di studio** (poligono MOPR)
3. **Configurare il CRS** del progetto QGIS

### Fase 2: Registrazione UT sul Campo

1. **Apertura scheda UT**
2. **Nuovo record** (click "New Record")
3. **Compilare dati identificativi:**
   ```
   Progetto: Survey Valle del Tevere 2024
   Nr. UT: 25
   ```

4. **Compilare localizzazione:**
   ```
   Regione: Lazio
   Provincia: Roma
   Comune: Fiano Romano
   Località: Colle Alto
   Coord. geografiche: 42.1234, 12.5678
   Quota: 125 m
   Precisione GPS: 3 m
   ```

5. **Compilare descrizione** (usando thesaurus):
   ```
   Definizione: Concentrazione reperti
   Descrizione: Area ellittica di ca. 50x30 m
   con concentrazione di frammenti ceramici
   e laterizi su versante collinare...
   ```

6. **Compilare dati survey** (usando thesaurus):
   ```
   Tipo Survey: Ricognizione intensiva
   Copertura Vegetazione: Rada
   Metodo GPS: GPS differenziale
   Condizione Superficie: Arato
   Accessibilità: Facile accesso
   Condizioni Meteo: Soleggiato
   Visibilità: 80%
   Data: 15/04/2024
   Responsabile: Team A
   ```

7. **Compilare materiali e cronologia:**
   ```
   Dimensioni: 1500 mq
   Rep/mq: 5-8
   Reperti datanti: Ceramica comune,
   sigillata italica, laterizi

   Periodo I: Romano
   Datazione I: I-II sec. d.C.
   Interpretazione I: Villa rustica
   ```

8. **Salvare** (click "Save")

### Fase 3: Creazione Geometrie

1. **Caricare layer** `pyarchinit_ut_polygon`
2. **Attivare editing**
3. **Disegnare** il perimetro dell'UT sulla mappa
4. **Compilare attributi**: progetto, nr_ut
5. **Salvare** il layer

### Fase 4: Analisi

1. **Aprire tab Analisi** nella scheda UT
2. **Verificare** i punteggi calcolati automaticamente
3. **Generare heatmap** se necessario
4. **Esportare report PDF** dell'analisi

### Fase 5: Export GNA (se richiesto)

1. **Verificare completezza dati** per tutte le UT
2. **Preparare poligono MOPR** dell'area di progetto
3. **Eseguire GNA Export**
4. **Validare output** contro specifiche GNA

---

## Tips & Tricks

### Ottimizzazione Workflow

1. **Precompilare i thesaurus** prima di iniziare le ricognizioni
2. **Usare template di progetto** con dati comuni preimpostati
3. **Sincronizzare coordinate** dal GPS al campo `coord_geografiche`
4. **Salvare frequentemente** durante la compilazione

### Migliorare la Qualità dei Dati

1. **Compilare TUTTI i campi** rilevanti per ogni UT
2. **Usare sempre i thesaurus** invece di testo libero
3. **Verificare le coordinate** su mappa prima di salvare
4. **Documentare fotograficamente** ogni UT

### Ottimizzazione Heatmap

1. **Cell size appropriato**: usa 25-50m per aree piccole, 100-200m per aree estese
2. **Metodo KDE** per distribuzioni continue e omogenee
3. **Metodo IDW** quando i valori puntuali sono critici
4. **Verifica sempre** che le coordinate siano corrette prima di generare

### Export GNA Efficiente

1. **Preparare il poligono MOPR** in anticipo come layer separato
2. **Verificare che tutte le UT** abbiano coordinate valide
3. **Calcolare i punteggi** prima dell'export
4. **Usare nomi file** descrittivi per i GeoPackage

### Gestione Multi-Utente

1. **Definire convenzioni** di numerazione UT condivise
2. **Usare database PostgreSQL** per accesso concorrente
3. **Sincronizzare periodicamente** i dati
4. **Documentare le modifiche** nei campi note

---

## Troubleshooting

### Problema: Combobox Thesaurus Vuoti

**Sintomi:** I menu a tendina per survey_type, vegetation, ecc. sono vuoti.

**Cause:**
- Voci thesaurus non presenti nel database
- Codice lingua errato
- Tabella thesaurus non aggiornata

**Soluzioni:**
1. Menu **PyArchInit** > **Database** > **Aggiorna database**
2. Verificare tabella `pyarchinit_thesaurus_sigle` per voci `ut_table`
3. Controllare impostazioni lingua
4. Se necessario, reimportare i thesaurus dal template

### Problema: Coordinate Non Valide

**Sintomi:** Errore nel salvare o coordinate visualizzate in posizione errata.

**Cause:**
- Formato errato (virgola vs punto decimale)
- Sistema di riferimento non corrispondente
- Ordine lat/lon invertito

**Soluzioni:**
1. Formato corretto `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Formato corretto `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Usare sempre il punto come separatore decimale
4. Verificare CRS del progetto QGIS

### Problema: UT Non Visibile su Mappa

**Sintomi:** Dopo aver salvato, l'UT non appare sulla mappa.

**Cause:**
- Geometria non creata nel layer
- Attributi `progetto`/`nr_ut` non corrispondenti
- Layer non caricato o nascosto
- CRS diverso tra layer e progetto

**Soluzioni:**
1. Verificare che esista il layer `pyarchinit_ut_point/polygon`
2. Controllare che gli attributi siano compilati correttamente
3. Attivare la visibilità del layer nel pannello Layer
4. Usare "Zoom to Layer" per verificare l'estensione

### Problema: Heatmap Non Generata

**Sintomi:** Errore "Servono almeno 2 punti con coordinate valide".

**Cause:**
- Meno di 2 UT con coordinate
- Coordinate in formato errato
- Campi coordinate vuoti

**Soluzioni:**
1. Verificare che almeno 2 UT abbiano `coord_geografiche` O `coord_piane` compilati
2. Controllare il formato delle coordinate (punto decimale, ordine corretto)
3. Ricalcolare i punteggi prima di generare la heatmap
4. Verificare che i campi non contengano caratteri speciali

### Problema: Punteggio Potenziale/Rischio Non Calcolato

**Sintomi:** I campi potenziale_score e risk_score sono vuoti o zero.

**Cause:**
- Campi obbligatori non compilati
- Valori thesaurus non riconosciuti
- Errore nel calcolo

**Soluzioni:**
1. Compilare almeno: `def_ut`, `periodo_I`, `visibility_percent`
2. Usare valori dal thesaurus (non testo libero)
3. Salvare il record e riaprirlo
4. Verificare nei log QGIS eventuali errori

### Problema: Export GNA Fallito

**Sintomi:** Il GeoPackage non viene creato o è incompleto.

**Cause:**
- Modulo GNA non disponibile
- Dati UT incompleti
- Poligono MOPR non valido
- Permessi scrittura insufficienti

**Soluzioni:**
1. Verificare che il modulo `modules/gna` sia installato
2. Controllare che tutte le UT abbiano coordinate valide
3. Verificare che il poligono MOPR sia valido (no self-intersections)
4. Controllare permessi sulla cartella di output
5. Verificare spazio disco sufficiente

### Problema: PDF Export con Campi Mancanti

**Sintomi:** Il PDF generato non mostra alcuni campi o mostra valori errati.

**Cause:**
- Campi database non aggiornati
- Versione schema database obsoleta
- Dati non salvati prima dell'export

**Soluzioni:**
1. Salvare il record prima di esportare
2. Aggiornare il database se necessario
3. Verificare che i nuovi campi (v4.9.67+) esistano nella tabella

### Problema: Errore Qt6/QGIS 4.x

**Sintomi:** Plugin non carica su QGIS 4.x con errore `AllDockWidgetFeatures`.

**Cause:**
- Incompatibilità Qt5/Qt6
- File UI non aggiornato

**Soluzioni:**
1. Aggiornare PyArchInit all'ultima versione
2. Il file `UT_ui.ui` deve usare flag espliciti invece di `AllDockWidgetFeatures`

---

## Riferimenti

### Database

- **Tabella**: `ut_table`
- **Classe mapper**: `UT`
- **ID**: `id_ut`

### Tabelle Geometriche

- **Punti**: `pyarchinit_ut_point`
- **Linee**: `pyarchinit_ut_line`
- **Poligoni**: `pyarchinit_ut_polygon`

### File Sorgente

| File | Descrizione |
|------|-------------|
| `gui/ui/UT_ui.ui` | Interfaccia utente Qt |
| `tabs/UT.py` | Controller principale |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Export PDF schede |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Export PDF analisi |
| `modules/analysis/ut_potential.py` | Calcolo potenziale |
| `modules/analysis/ut_risk.py` | Calcolo rischio |
| `modules/analysis/ut_heatmap_generator.py` | Generazione heatmap |
| `modules/gna/gna_exporter.py` | Export GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Mapping vocabolari GNA |

### Codici Thesaurus UT

| Codice | Campo | Descrizione |
|--------|-------|-------------|
| 12.1 | survey_type | Tipo di ricognizione |
| 12.2 | vegetation_coverage | Copertura vegetale |
| 12.3 | gps_method | Metodo GPS |
| 12.4 | surface_condition | Condizione superficie |
| 12.5 | accessibility | Accessibilità |
| 12.6 | weather_conditions | Condizioni meteo |
| 12.7 | def_ut | Definizione UT |

---

## Video Tutorial

### Documentazione Ricognizioni
**Durata**: 15-18 minuti
- Registrazione UT
- Dati survey con thesaurus
- Geolocalizzazione

### Analisi Potenziale e Rischio
**Durata**: 10-12 minuti
- Calcolo automatico punteggi
- Interpretazione risultati
- Generazione heatmap

### Export GNA
**Durata**: 12-15 minuti
- Preparazione dati
- Configurazione export
- Validazione output

### Export Report PDF
**Durata**: 8-10 minuti
- Scheda UT standard
- Elenco UT
- Report analisi con mappe

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit v4.9.68 - Sistema di Gestione Dati Archeologici*
