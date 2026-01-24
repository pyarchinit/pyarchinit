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
| Coord. geografiche | `coord_geografiche` | Lat/Long |
| Coord. piane | `coord_piane` | UTM/Gauss-Boaga |
| Quota | `quota` | Altitudine s.l.m. |
| Precisione coord. | `coordinate_precision` | Accuratezza GPS |

---

## Campi Descrittivi

### Definizione UT ⭐ NUOVO

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

## Campi Survey con Thesaurus ⭐ NUOVO

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

Percentuale di visibilità del suolo (0-100%). Valore numerico.

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

Densità materiali per metro quadro.

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

## Tab Analisi ⭐ NUOVO

Il tab **Analisi** fornisce strumenti avanzati per il calcolo automatico del potenziale e rischio archeologico.

### Potenziale Archeologico

Il sistema calcola un punteggio da 0 a 100 basato su:

| Fattore | Peso | Descrizione |
|---------|------|-------------|
| Definizione UT | 30% | Tipo di evidenza archeologica |
| Periodo storico | 25% | Cronologia dei materiali |
| Densità reperti | 20% | Materiali per mq |
| Condizione superficie | 15% | Visibilità e accessibilità |
| Documentazione | 10% | Qualità della documentazione |

**Visualizzazione:**
- Barra progressiva colorata (verde = alto, giallo = medio, rosso = basso)
- Tabella dettagliata dei fattori con punteggio singolo
- Testo narrativo automatico con interpretazione

### Rischio Archeologico

Valuta il rischio di impatto/perdita del patrimonio:

| Fattore | Peso | Descrizione |
|---------|------|-------------|
| Accessibilità | 25% | Facilità di accesso all'area |
| Uso del suolo | 25% | Attività agricole/edilizie |
| Vincoli esistenti | 20% | Protezioni legali |
| Indagini pregresse | 15% | Stato delle conoscenze |
| Visibilità | 15% | Esposizione del sito |

### Generazione Heatmap

Il pulsante **Genera Heatmap** crea layer raster visualizzando:
- **Heatmap Potenziale**: distribuzione spaziale del potenziale archeologico
- **Heatmap Rischio**: mappa del rischio di impatto

**Metodi disponibili:**
- Kernel Density Estimation (KDE)
- Inverse Distance Weighting (IDW)
- Natural Neighbor

---

## Export PDF ⭐ MIGLIORATO

### Scheda UT Standard

Esporta la scheda UT completa con tutti i campi compilati.

### Report Analisi UT

Genera un report PDF che include:

1. **Dati identificativi** dell'UT
2. **Sezione Potenziale Archeologico**
   - Punteggio con indicatore grafico
   - Testo narrativo descrittivo
   - Tabella fattori con contributi
   - Immagine heatmap potenziale (se generata)
3. **Sezione Rischio Archeologico**
   - Punteggio con indicatore grafico
   - Testo narrativo con raccomandazioni
   - Tabella fattori con contributi
   - Immagine heatmap rischio (se generata)
4. **Sezione Metodologia**
   - Descrizione degli algoritmi utilizzati
   - Note sui pesi dei fattori

Il report è disponibile in tutte le 7 lingue supportate.

---

## Workflow Operativo

### Registrazione Nuova UT

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Dati identificativi**
   ```
   Progetto: Survey Valle del Tevere 2024
   Nr. UT: 25
   ```

4. **Localizzazione**
   ```
   Regione: Lazio
   Provincia: Roma
   Comune: Fiano Romano
   Località: Colle Alto
   Coord.: 42.1234 N, 12.5678 E
   Quota: 125 m
   ```

5. **Descrizione** (usando thesaurus)
   ```
   Definizione: Concentrazione reperti (da thesaurus)
   Descrizione: Area ellittica di ca. 50x30 m
   con concentrazione di frammenti ceramici
   e laterizi su versante collinare esposto
   a sud...
   ```

6. **Dati survey** (usando thesaurus)
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

7. **Materiali e cronologia**
   ```
   Dimensioni: 1500 mq
   Rep/mq: 5-8
   Reperti datanti: Ceramica comune,
   sigillata italica, laterizi

   Periodo I: Romano
   Datazione I: I-II sec. d.C.
   Interpretazione I: Villa rustica
   ```

8. **Analisi** (tab Analisi)
   - Verificare punteggio Potenziale
   - Verificare punteggio Rischio
   - Generare Heatmap se necessario

9. **Salvataggio**
   - Click su "Save"

---

## Integrazione GIS

La scheda UT è strettamente integrata con QGIS:

- **Layer UT**: visualizzazione geometrie
- **Attributi collegati**: dati dalla scheda
- **Selezione da mappa**: click su geometria apre scheda
- **Heatmap come layer**: le mappe generate sono salvate come layer raster

---

## Best Practices

### Utilizzo Thesaurus

- Preferire sempre i valori da thesaurus per garantire coerenza
- I valori sono automaticamente tradotti nella lingua dell'utente
- Per nuovi valori, aggiungerli prima nel thesaurus

### Nomenclatura

- Numerazione progressiva per progetto
- Usare suffissi per suddivisioni
- Documentare le convenzioni

### Geolocalizzazione

- Usare GPS differenziale quando possibile
- Indicare sempre il metodo e la precisione
- Verificare le coordinate su mappa

### Documentazione

- Fotografare ogni UT
- Produrre schizzi planimetrici
- Registrare condizioni di visibilità

### Analisi

- Verificare sempre i punteggi calcolati
- Generare heatmap per progetti completi
- Esportare report per documentazione

---

## Codici Thesaurus UT

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

## Troubleshooting

### Problema: Combobox vuoti

**Causa**: Voci thesaurus non presenti nel database.

**Soluzione**:
1. Aggiornare il database tramite "Aggiorna database"
2. Verificare che la tabella `pyarchinit_thesaurus_sigle` contenga le voci per `ut_table`
3. Controllare il codice lingua nelle impostazioni

### Problema: Coordinate non valide

**Causa**: Formato errato o sistema di riferimento.

**Soluzione**:
1. Verificare il formato (DD o DMS)
2. Controllare il sistema di riferimento
3. Usare lo strumento di conversione QGIS

### Problema: UT non visibile su mappa

**Causa**: Geometria non associata.

**Soluzione**:
1. Verificare che esista il layer UT
2. Controllare che il record abbia geometria
3. Verificare la proiezione del layer

### Problema: Heatmap non generata

**Causa**: Dati insufficienti o errore nel calcolo.

**Soluzione**:
1. Verificare che ci siano almeno 3 UT con dati completi
2. Controllare che le geometrie siano valide
3. Verificare lo spazio disponibile su disco

---

## Riferimenti

### Database

- **Tabella**: `ut_table`
- **Classe mapper**: `UT`
- **ID**: `id_ut`

### File Sorgente

- **UI**: `gui/ui/UT_ui.ui`
- **Controller**: `tabs/UT.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_UTsheet_pdf.py`
- **Analisi PDF**: `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Calcolo Potenziale**: `modules/analysis/ut_potential.py`
- **Calcolo Rischio**: `modules/analysis/ut_risk.py`
- **Heatmap Generator**: `modules/analysis/ut_heatmap_generator.py`

---

## Video Tutorial

### Documentazione Ricognizioni
**Durata**: 15-18 minuti
- Registrazione UT
- Dati survey con thesaurus
- Geolocalizzazione

[Placeholder video: video_ut_survey.mp4]

### Analisi Potenziale e Rischio
**Durata**: 10-12 minuti
- Calcolo automatico punteggi
- Interpretazione risultati
- Generazione heatmap

[Placeholder video: video_ut_analysis.mp4]

### Export Report PDF
**Durata**: 8-10 minuti
- Scheda UT standard
- Report analisi con mappe
- Personalizzazione output

[Placeholder video: video_ut_pdf.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit v4.9.68 - Sistema di Gestione Dati Archeologici*
