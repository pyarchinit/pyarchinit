# Tutorial 21: Scheda UT - Unita Topografiche

## Introduzione

La **Scheda UT** (Unita Topografiche) e il modulo di PyArchInit dedicato alla documentazione delle ricognizioni archeologiche di superficie (survey). Permette di registrare i dati relativi alle concentrazioni di materiali, anomalie del terreno e siti individuati durante le prospezioni.

### Concetti Base

**Unita Topografica (UT):**
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

La scheda e ricca di campi per documentare tutti gli aspetti della ricognizione.

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | Campi Identificativi | Progetto, Nr. UT |
| 3 | Localizzazione | Dati geografici e amministrativi |
| 4 | Descrizione | Definizione, descrizione, interpretazione |
| 5 | Dati Survey | Condizioni, metodologia |
| 6 | Cronologia | Periodi e datazioni |

---

## Campi Identificativi

### Progetto

**Campo**: `lineEdit_progetto`
**Database**: `progetto`

Nome del progetto di ricognizione.

### Numero UT

**Campo**: `lineEdit_nr_ut`
**Database**: `nr_ut`

Numero progressivo dell'Unita Topografica.

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
| Frazione | `frazione` | Frazione/localita |
| Localita | `localita` | Toponimo locale |
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
| Metodo GPS | `gps_method` | Tipo rilevamento |

---

## Campi Descrittivi

### Definizione UT

**Campo**: `comboBox_def_ut`
**Database**: `def_ut`

Classificazione tipologica dell'UT.

**Valori:**
- Concentrazione materiali
- Area di frammenti
- Anomalia del terreno
- Struttura affiorante
- Sito archeologico

### Descrizione UT

**Campo**: `textEdit_descrizione`
**Database**: `descrizione_ut`

Descrizione dettagliata dell'Unita Topografica.

**Contenuti:**
- Estensione e forma dell'area
- Densita dei materiali
- Caratteristiche del terreno
- Visibilita e condizioni

### Interpretazione UT

**Campo**: `textEdit_interpretazione`
**Database**: `interpretazione_ut`

Interpretazione funzionale/storica.

---

## Dati Ambientali

### Andamento Terreno

**Campo**: `comboBox_terreno`
**Database**: `andamento_terreno_pendenza`

Morfologia e pendenza.

**Valori:**
- Pianeggiante
- Lieve pendenza
- Media pendenza
- Forte pendenza
- Terrazzato

### Utilizzo Suolo

**Campo**: `comboBox_suolo`
**Database**: `utilizzo_suolo_vegetazione`

Uso del suolo al momento della ricognizione.

**Valori:**
- Arativo
- Prato/pascolo
- Vigneto
- Oliveto
- Incolto
- Bosco
- Urbano

### Descrizione Suolo

**Campo**: `textEdit_suolo`
**Database**: `descrizione_empirica_suolo`

Caratteristiche pedologiche osservate.

### Descrizione Luogo

**Campo**: `textEdit_luogo`
**Database**: `descrizione_luogo`

Contesto paesaggistico.

---

## Dati Survey

### Metodo Ricognizione

**Campo**: `comboBox_metodo`
**Database**: `metodo_rilievo_e_ricognizione`

Metodologia adottata.

**Valori:**
- Ricognizione sistematica
- Ricognizione estensiva
- Ricognizione mirata
- Controllo segnalazione

### Tipo Survey

**Campo**: `comboBox_survey_type`
**Database**: `survey_type`

Tipologia di prospezione.

### Visibilita

**Campo**: `spinBox_visibility`
**Database**: `visibility_percent`

Percentuale di visibilita del suolo (0-100%).

### Copertura Vegetazione

**Campo**: `comboBox_vegetation`
**Database**: `vegetation_coverage`

Grado di copertura vegetale.

### Condizione Superficie

**Campo**: `comboBox_surface`
**Database**: `surface_condition`

Stato della superficie.

**Valori:**
- Arato di fresco
- Arato non fresato
- Erba bassa
- Erba alta
- Stoppie

### Accessibilita

**Campo**: `comboBox_accessibility`
**Database**: `accessibility`

Facilita di accesso all'area.

### Data

**Campo**: `dateEdit_data`
**Database**: `data`

Data della ricognizione.

### Ora/Meteo

**Campo**: `lineEdit_meteo`
**Database**: `ora_meteo`

Condizioni meteo e ora.

### Responsabile

**Campo**: `comboBox_responsabile`
**Database**: `responsabile`

Responsabile della ricognizione.

### Team

**Campo**: `textEdit_team`
**Database**: `team_members`

Componenti del gruppo.

---

## Dati Materiali

### Dimensioni UT

**Campo**: `lineEdit_dimensioni`
**Database**: `dimensioni_ut`

Estensione in mq.

### Reperti per mq

**Campo**: `lineEdit_rep_mq`
**Database**: `rep_per_mq`

Densita materiali.

### Reperti Datanti

**Campo**: `textEdit_rep_datanti`
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

## Altri Campi

### Geometria

**Campo**: `comboBox_geometria`
**Database**: `geometria`

Forma dell'UT.

### Bibliografia

**Campo**: `textEdit_bibliografia`
**Database**: `bibliografia`

Riferimenti bibliografici.

### Documentazione

**Campo**: `textEdit_documentazione`
**Database**: `documentazione`

Documentazione prodotta (foto, disegni).

### Documentazione Foto

**Campo**: `textEdit_photo_doc`
**Database**: `photo_documentation`

Elenco documentazione fotografica.

### Enti Tutela/Vincoli

**Campo**: `textEdit_vincoli`
**Database**: `enti_tutela_vincoli`

Vincoli e soggetti di tutela.

### Indagini Preliminari

**Campo**: `textEdit_indagini`
**Database**: `indagini_preliminari`

Eventuali indagini gia eseguite.

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
   Localita: Colle Alto
   Coord.: 42.1234 N, 12.5678 E
   Quota: 125 m
   ```

5. **Descrizione**
   ```
   Definizione: Concentrazione materiali
   Descrizione: Area ellittica di ca. 50x30 m
   con concentrazione di frammenti ceramici
   e laterizi su versante collinare esposto
   a sud...
   ```

6. **Dati survey**
   ```
   Metodo: Ricognizione sistematica
   Visibilita: 80%
   Condizione: Arato di fresco
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

8. **Salvataggio**
   - Click su "Save"

---

## Integrazione GIS

La scheda UT e strettamente integrata con QGIS:

- **Layer UT**: visualizzazione geometrie
- **Attributi collegati**: dati dalla scheda
- **Selezione da mappa**: click su geometria apre scheda

---

## Export PDF

La scheda supporta l'esportazione in PDF per:
- Schede UT singole
- Elenchi per progetto
- Report di survey

---

## Best Practices

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
- Registrare condizioni di visibilita

### Materiali

- Raccogliere campioni diagnostici
- Stimare densita per area
- Documentare distribuzione spaziale

---

## Troubleshooting

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

---

## Video Tutorial

### Documentazione Ricognizioni
**Durata**: 15-18 minuti
- Registrazione UT
- Dati survey
- Geolocalizzazione

[Placeholder video: video_ut_survey.mp4]

### Integrazione GIS Survey
**Durata**: 10-12 minuti
- Layer e attributi
- Visualizzazione risultati
- Analisi spaziale

[Placeholder video: video_ut_gis.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
