# Tutorial 17: TMA - Tabella Materiali Archeologici

## Introduzione

La **Scheda TMA** (Tabella Materiali Archeologici) e il modulo avanzato di PyArchInit per la gestione dei materiali di scavo secondo gli standard ministeriali italiani. Permette una catalogazione dettagliata conforme alle normative ICCD (Istituto Centrale per il Catalogo e la Documentazione).

### Caratteristiche Principali

- Catalogazione conforme standard ICCD
- Gestione materiali per cassetta/contenitore
- Campi cronologici dettagliati
- Tabella materiali associati
- Gestione media integrata
- Export etichette e schede PDF

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda TMA**

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **TMA**

---

## Panoramica dell'Interfaccia

La scheda presenta un'interfaccia complessa con molti campi.

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | Campi Identificativi | Sito, Area, US, Cassetta |
| 3 | Campi Localizzazione | Collocazione, Vano, Saggio |
| 4 | Campi Cronologici | Fascia, Frazione, Cronologie |
| 5 | Tabella Materiali | Dettaglio materiali associati |
| 6 | Tab Media | Immagini e documenti |

---

## Campi Identificativi

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Sito archeologico (SCAN - Denominazione scavo ICCD).

### Area

**Campo**: `comboBox_area`
**Database**: `area`

Area di scavo.

### US (DSCU)

**Campo**: `comboBox_us`
**Database**: `dscu`

Unita Stratigrafica di provenienza (DSCU = Descrizione Scavo Unita).

### Settore

**Campo**: `comboBox_settore`
**Database**: `settore`

Settore di scavo.

### Inventario

**Campo**: `lineEdit_inventario`
**Database**: `inventario`

Numero di inventario.

### Cassetta

**Campo**: `lineEdit_cassetta`
**Database**: `cassetta`

Numero della cassetta/contenitore.

---

## Campi Localizzazione ICCD

### LDCT - Tipologia Collocazione

**Campo**: `comboBox_ldct`
**Database**: `ldct`

Tipo di luogo di collocazione.

**Valori ICCD:**
- museo
- soprintendenza
- deposito
- laboratorio
- altro

### LDCN - Denominazione Collocazione

**Campo**: `lineEdit_ldcn`
**Database**: `ldcn`

Nome specifico del luogo di conservazione.

### Vecchia Collocazione

**Campo**: `lineEdit_vecchia_coll`
**Database**: `vecchia_collocazione`

Eventuale precedente collocazione.

### SCAN - Denominazione Scavo

**Campo**: `lineEdit_scan`
**Database**: `scan`

Nome ufficiale dello scavo/ricerca.

### Saggio

**Campo**: `comboBox_saggio`
**Database**: `saggio`

Saggio/trincea di riferimento.

### Vano/Locus

**Campo**: `lineEdit_vano`
**Database**: `vano_locus`

Ambiente o locus di provenienza.

---

## Campi Cronologici

### DTZG - Fascia Cronologica

**Campo**: `comboBox_dtzg`
**Database**: `dtzg`

Periodo cronologico generale.

**Esempi ICCD:**
- eta del bronzo
- eta del ferro
- eta romana
- eta medievale

### DTZS - Frazione Cronologica

**Campo**: `comboBox_dtzs`
**Database**: `dtzs`

Suddivisione del periodo.

**Esempi:**
- antico/a
- medio/a
- tardo/a
- finale

### Cronologie

**Campo**: `tableWidget_cronologie`
**Database**: `cronologie`

Tabella per cronologie multiple o dettagliate.

---

## Campi Acquisizione

### AINT - Tipo Acquisizione

**Campo**: `comboBox_aint`
**Database**: `aint`

Modalita di acquisizione dei materiali.

**Valori ICCD:**
- scavo
- ricognizione
- acquisto
- donazione
- sequestro

### AIND - Data Acquisizione

**Campo**: `dateEdit_aind`
**Database**: `aind`

Data dell'acquisizione.

### RCGD - Data Ricognizione

**Campo**: `dateEdit_rcgd`
**Database**: `rcgd`

Data della ricognizione (se applicabile).

### RCGZ - Specifiche Ricognizione

**Campo**: `textEdit_rcgz`
**Database**: `rcgz`

Note sulla ricognizione.

---

## Campi Materiali

### OGTM - Materiale

**Campo**: `comboBox_ogtm`
**Database**: `ogtm`

Materiale principale (Oggetto Tipo Materiale).

**Valori ICCD:**
- ceramica
- vetro
- metallo
- osso
- pietra
- laterizio

### N. Reperti

**Campo**: `spinBox_n_reperti`
**Database**: `n_reperti`

Numero totale di reperti.

### Peso

**Campo**: `doubleSpinBox_peso`
**Database**: `peso`

Peso totale in grammi.

### DESO - Indicazione Oggetti

**Campo**: `textEdit_deso`
**Database**: `deso`

Descrizione sintetica degli oggetti.

---

## Tabella Materiali Dettaglio

**Widget**: `tableWidget_materiali`
**Tabella associata**: `tma_materiali`

Permette di registrare i singoli materiali contenuti nella cassetta.

### Colonne

| Campo ICCD | Descrizione |
|------------|-------------|
| MADI | Inventario materiale |
| MACC | Categoria |
| MACL | Classe |
| MACP | Precisazione tipologica |
| MACD | Definizione |
| Cronologia | Datazione specifica |
| MACQ | Quantita |

### Gestione Righe

| Pulsante | Funzione |
|----------|----------|
| + | Aggiungi materiale |
| - | Rimuovi materiale |

---

## Campi Documentazione

### FTAP - Tipo Fotografia

**Campo**: `comboBox_ftap`
**Database**: `ftap`

Tipo di documentazione fotografica.

### FTAN - Codice Foto

**Campo**: `lineEdit_ftan`
**Database**: `ftan`

Codice identificativo della foto.

### DRAT - Tipo Disegno

**Campo**: `comboBox_drat`
**Database**: `drat`

Tipo di documentazione grafica.

### DRAN - Codice Disegno

**Campo**: `lineEdit_dran`
**Database**: `dran`

Codice identificativo del disegno.

### DRAA - Autore Disegno

**Campo**: `lineEdit_draa`
**Database**: `draa`

Autore del disegno.

---

## Tab Media

Gestione di immagini associate alla cassetta/TMA.

### Funzionalita

- Visualizzazione miniature
- Drag & drop per aggiungere immagini
- Doppio click per visualizzare
- Collegamento a database media

---

## Tab Table View

Vista tabellare di tutti i record TMA per una consultazione rapida.

### Funzionalita

- Visualizzazione a griglia
- Ordinamento per colonna
- Filtri rapidi
- Selezione multipla

---

## Export e Stampa

### Export PDF

| Opzione | Descrizione |
|---------|-------------|
| Scheda TMA | Scheda completa |
| Etichette | Etichette per cassette |

### Etichette Cassette

Generazione automatica di etichette per:
- Identificazione cassette
- Contenuto sintetico
- Dati di provenienza
- Codice a barre (opzionale)

---

## Workflow Operativo

### Registrazione Nuova TMA

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Dati identificativi**
   ```
   Sito: Villa Romana
   Area: 1000
   US: 150
   Cassetta: C-001
   ```

4. **Localizzazione**
   ```
   LDCT: deposito
   LDCN: Deposito Soprintendenza Roma
   SCAN: Scavi Villa Romana 2024
   ```

5. **Cronologia**
   ```
   DTZG: eta romana
   DTZS: imperiale
   ```

6. **Materiali** (tabella)
   ```
   | Inv | Cat | Classe | Def | Q.ta |
   |-----|-----|--------|-----|------|
   | 001 | ceramica | comune | olla | 5 |
   | 002 | ceramica | sigillata | piatto | 3 |
   | 003 | vetro | - | unguentario | 1 |
   ```

7. **Salvataggio**
   - Click su "Save"

---

## Best Practices

### Standard ICCD

- Utilizzare i vocabolari controllati ICCD
- Rispettare le sigle ufficiali
- Mantenere coerenza terminologica

### Organizzazione Cassette

- Numerazione progressiva univoca
- Una TMA per cassetta fisica
- Separare per US quando possibile

### Documentazione

- Collegare sempre foto e disegni
- Usare codici univoci per i media
- Registrare autore e data

---

## Troubleshooting

### Problema: Vocabolari ICCD non disponibili

**Causa**: Thesaurus non configurato.

**Soluzione**:
1. Importare i vocabolari ICCD standard
2. Verificare la configurazione del thesaurus

### Problema: Materiali non salvati

**Causa**: Tabella materiali non sincronizzata.

**Soluzione**:
1. Verificare che tutti i campi obbligatori siano compilati
2. Salvare la scheda principale prima di aggiungere materiali

---

## Riferimenti

### Database

- **Tabella principale**: `tma_materiali_archeologici`
- **Tabella dettaglio**: `tma_materiali`
- **Classe mapper**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### File Sorgente

- **UI**: `gui/ui/Tma.ui`
- **Controller**: `tabs/Tma.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etichette**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Video Tutorial

### Catalogazione TMA
**Durata**: 15-18 minuti
- Standard ICCD
- Compilazione completa
- Gestione materiali

[Placeholder video: video_tma_catalogazione.mp4]

### Generazione Etichette
**Durata**: 5-6 minuti
- Configurazione etichette
- Stampa batch
- Personalizzazione

[Placeholder video: video_tma_etichette.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
