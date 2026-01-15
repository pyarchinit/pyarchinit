# Tutorial 06: Scheda Tomba

## Introduzione

La **Scheda Tomba** e il modulo di PyArchInit dedicato alla documentazione delle sepolture archeologiche. Questo strumento permette di registrare tutti gli aspetti di una tomba: dalla struttura funeraria al rito, dal corredo agli individui sepolti.

### Concetti Base

**Tomba in PyArchInit:**
- Una tomba e una struttura funeraria che contiene uno o piu individui
- E collegata alla Scheda Struttura (la struttura fisica della sepoltura)
- E collegata alla Scheda Individui (per i dati antropologici)
- Documenta rito, corredo e caratteristiche della deposizione

**Relazioni:**
```
Tomba → Struttura (contenitore fisico)
     → Individuo/i (resti umani)
     → Corredo (oggetti di accompagnamento)
     → Inventario Materiali (reperti associati)
```

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda Tomba** (o **Grave form**)

![Menu accesso](images/06_scheda_tomba/02_menu_accesso.png)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Tomba** (simbolo sepoltura)

![Toolbar accesso](images/06_scheda_tomba/03_toolbar_accesso.png)

---

## Panoramica dell'Interfaccia

La scheda presenta un layout organizzato in sezioni funzionali:

![Interfaccia completa](images/06_scheda_tomba/04_interfaccia_completa.png)

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | DB Info | Stato record, ordinamento, contatore |
| 3 | Campi Identificativi | Sito, Area, N. Scheda, Struttura |
| 4 | Campi Individuo | Collegamento all'individuo |
| 5 | Area Tab | Tab tematici per dati specifici |

---

## Toolbar DBMS

La toolbar principale fornisce gli strumenti per la gestione dei record.

![Toolbar DBMS](images/06_scheda_tomba/05_toolbar_dbms.png)

### Pulsanti di Navigazione

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![First](../../resources/icons/5_leftArrows.png) | First rec | Vai al primo record |
| ![Prev](../../resources/icons/4_leftArrow.png) | Prev rec | Vai al record precedente |
| ![Next](../../resources/icons/6_rightArrow.png) | Next rec | Vai al record successivo |
| ![Last](../../resources/icons/7_rightArrows.png) | Last rec | Vai all'ultimo record |

### Pulsanti CRUD

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![New](../../resources/icons/newrec.png) | New record | Crea un nuovo record tomba |
| ![Save](../../resources/icons/b_save.png) | Save | Salva le modifiche |
| ![Delete](../../resources/icons/delete.png) | Delete | Elimina il record corrente |

### Pulsanti di Ricerca

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![New Search](../../resources/icons/new_search.png) | New search | Avvia nuova ricerca |
| ![Search](../../resources/icons/search.png) | Search!!! | Esegui ricerca |
| ![Sort](../../resources/icons/sort.png) | Order by | Ordina risultati |
| ![View All](../../resources/icons/view_all.png) | View all | Visualizza tutti i record |

### Pulsanti Speciali

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![GIS](../../resources/icons/GIS.png) | GIS | Carica tomba su mappa |
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Esporta in PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Apri cartella export |

---

## Campi Identificativi

I campi identificativi definiscono univocamente la tomba nel database.

![Campi identificativi](images/06_scheda_tomba/06_campi_identificativi.png)

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Seleziona il sito archeologico di appartenenza.

### Area

**Campo**: `comboBox_area`
**Database**: `area`

Area di scavo all'interno del sito.

### Numero Scheda

**Campo**: `lineEdit_nr_scheda`
**Database**: `nr_scheda_taf`

Numero progressivo della scheda tomba. Viene proposto automaticamente il prossimo numero disponibile.

### Sigla e Numero Struttura

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Sigla struttura | `sigla_struttura` | Sigla della struttura (es. TM, TB) |
| Nr struttura | `nr_struttura` | Numero della struttura |

Questi campi collegano la tomba alla corrispondente Scheda Struttura.

### Numero Individuo

**Campo**: `comboBox_nr_individuo`
**Database**: `nr_individuo`

Numero dell'individuo sepolto. Collega la tomba alla Scheda Individui.

**Note:**
- Una tomba puo contenere piu individui (sepoltura multipla)
- Il menu mostra gli individui disponibili per la struttura selezionata

---

## Tab Dati Descrittivi

Il primo tab contiene i campi fondamentali per descrivere la sepoltura.

![Tab Dati Descrittivi](images/06_scheda_tomba/07_tab_descrittivi.png)

### Rito

**Campo**: `comboBox_rito`
**Database**: `rito`

Tipo di rituale funerario praticato.

**Valori tipici:**
| Rito | Descrizione |
|------|-------------|
| Inumazione | Deposizione del corpo intero |
| Cremazione | Incinerazione dei resti |
| Incinerazione primaria | Cremazione sul posto |
| Incinerazione secondaria | Cremazione altrove e deposizione |
| Misto | Combinazione di riti |
| Indeterminato | Non determinabile |

### Tipo Sepoltura

**Campo**: `comboBox_tipo_sepoltura`
**Database**: `tipo_sepoltura`

Classificazione tipologica della sepoltura.

**Esempi:**
- Tomba a fossa semplice
- Tomba a cassa
- Tomba a camera
- Tomba alla cappuccina
- Tomba a enchytrismos
- Sarcofago
- Ossario

### Tipo Deposizione

**Campo**: `comboBox_tipo_deposizione`
**Database**: `tipo_deposizione`

Modalita di deposizione del corpo.

**Valori:**
- Primaria (deposizione diretta)
- Secondaria (riduzione/spostamento)
- Multipla simultanea
- Multipla successiva

### Stato di Conservazione

**Campo**: `comboBox_stato_conservazione`
**Database**: `stato_di_conservazione`

Valutazione dello stato conservativo.

**Scala:**
- Ottimo
- Buono
- Mediocre
- Cattivo
- Pessimo

### Descrizione

**Campo**: `textEdit_descrizione`
**Database**: `descrizione_taf`

Descrizione dettagliata della tomba.

**Contenuti consigliati:**
- Forma e dimensioni della fossa
- Orientamento
- Profondita
- Caratteristiche del riempimento
- Stato al momento dello scavo

### Interpretazione

**Campo**: `textEdit_interpretazione`
**Database**: `interpretazione_taf`

Interpretazione storico-archeologica della sepoltura.

---

## Caratteristiche della Tomba

### Segnacoli

**Campo**: `comboBox_segnacoli`
**Database**: `segnacoli`

Presenza e tipo di segnacoli funerari.

**Valori:**
- Assente
- Stele
- Cippo
- Tumulo
- Recinto
- Altro

### Canale Libatorio

**Campo**: `comboBox_canale_libatorio`
**Database**: `canale_libatorio_si_no`

Presenza di canale per libagioni rituali.

**Valori:** Si / No

### Copertura

**Campo**: `comboBox_copertura_tipo`
**Database**: `copertura_tipo`

Tipo di copertura della tomba.

**Esempi:**
- Tegole
- Lastre di pietra
- Tavole lignee
- Terra
- Assente

### Contenitore Resti

**Campo**: `comboBox_tipo_contenitore`
**Database**: `tipo_contenitore_resti`

Tipo di contenitore per i resti.

**Esempi:**
- Fossa terragna
- Cassa lignea
- Cassa litica
- Anfora
- Urna
- Sarcofago

### Oggetti Esterni

**Campo**: `comboBox_oggetti_esterno`
**Database**: `oggetti_rinvenuti_esterno`

Oggetti rinvenuti all'esterno della tomba ma ad essa associati.

---

## Tab Corredo

Questo tab gestisce la documentazione del corredo funerario.

![Tab Corredo](images/06_scheda_tomba/08_tab_corredo.png)

### Presenza Corredo

**Campo**: `comboBox_corredo_presenza`
**Database**: `corredo_presenza`

Indica se la tomba conteneva corredo.

**Valori:**
- Si
- No
- Probabile
- Asportato

### Tipo Corredo

**Campo**: `comboBox_corredo_tipo`
**Database**: `corredo_tipo`

Classificazione generale del corredo.

**Categorie:**
- Personale (gioielli, fibule)
- Rituale (vasi, lucerne)
- Simbolico (monete, amuleti)
- Strumentale (attrezzi)
- Misto

### Descrizione Corredo

**Campo**: `textEdit_corredo_descrizione`
**Database**: `corredo_descrizione`

Descrizione dettagliata degli oggetti di corredo.

### Tabella Corredo

**Widget**: `tableWidget_corredo_tipo`

Tabella per registrare i singoli elementi del corredo.

**Colonne:**
| Colonna | Descrizione |
|---------|-------------|
| ID Reperto | Numero inventario del reperto |
| ID Indv. | Individuo associato |
| Materiale | Tipo di materiale |
| Posizione del corredo | Dove era collocato nella tomba |
| Posizione nel corredo | Posizione rispetto al corpo |

**Note:**
- Gli elementi sono collegati alla Scheda Inventario Materiali
- La tabella si popola automaticamente con i reperti della struttura

---

## Tab Altre Caratteristiche

Questo tab contiene informazioni aggiuntive sulla sepoltura.

![Tab Altre Caratteristiche](images/06_scheda_tomba/09_tab_altre.png)

### Periodizzazione

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Periodo iniziale | `periodo_iniziale` | Periodo di inizio uso |
| Fase iniziale | `fase_iniziale` | Fase nel periodo |
| Periodo finale | `periodo_finale` | Periodo di fine uso |
| Fase finale | `fase_finale` | Fase nel periodo |
| Datazione estesa | `datazione_estesa` | Datazione letterale |

I valori sono popolati in base alla Scheda Periodizzazione del sito.

---

## Tab Tools

Il tab Tools contiene funzionalita aggiuntive.

![Tab Tools](images/06_scheda_tomba/10_tab_tools.png)

### Gestione Media

Permette di:
- Visualizzare immagini associate
- Aggiungere nuove foto tramite drag & drop
- Cercare media nel database

### Export

Opzioni per l'esportazione:
- Elenco Tombe (lista sintetica)
- Schede Tombe (schede complete)
- Conversione PDF to Word

---

## Integrazione GIS

### Visualizzazione su Mappa

| Pulsante | Funzione |
|----------|----------|
| GIS Toggle | Attiva/disattiva caricamento automatico |
| Load to GIS | Carica la tomba sulla mappa |

### Layer GIS

La scheda utilizza layer specifici per le tombe:
- **pyarchinit_tomba**: geometria delle tombe
- Collegamento con layer strutture e US

---

## Export e Stampa

### Export PDF

Il pulsante PDF apre un pannello con opzioni:

| Opzione | Descrizione |
|---------|-------------|
| Elenco Tombe | Lista sintetica delle tombe |
| Schede Tombe | Schede complete dettagliate |
| Stampa | Genera il PDF |

### Contenuto Scheda PDF

La scheda PDF include:
- Dati identificativi
- Rito e tipo sepoltura
- Descrizione e interpretazione
- Dati del corredo
- Periodizzazione
- Immagini associate

---

## Workflow Operativo

### Creazione Nuova Tomba

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"
   - Il numero scheda viene proposto automaticamente

3. **Dati identificativi**
   ```
   Sito: Necropoli di Isola Sacra
   Area: 1
   N. Scheda: 45
   Sigla struttura: TM
   Nr struttura: 45
   ```

4. **Collegamento individuo**
   ```
   Nr Individuo: 1
   ```

5. **Dati descrittivi** (Tab 1)
   ```
   Rito: Inumazione
   Tipo sepoltura: Tomba a fossa semplice
   Tipo deposizione: Primaria
   Stato conservazione: Buono

   Descrizione: Fossa rettangolare con angoli
   arrotondati, orientata E-W...

   Segnacoli: Cippo
   Copertura: Tegole alla cappuccina
   ```

6. **Corredo** (Tab 2)
   ```
   Presenza: Si
   Tipo: Personale
   Descrizione: Fibula in bronzo presso la
   spalla destra, moneta presso la bocca...
   ```

7. **Periodizzazione**
   ```
   Periodo iniziale: II - Fase A
   Periodo finale: II - Fase A
   Datazione: II sec. d.C.
   ```

8. **Salvataggio**
   - Click su "Save"

### Ricerca Tombe

1. Click su "New Search"
2. Compilare criteri:
   - Sito
   - Rito
   - Tipo sepoltura
   - Periodo
3. Click su "Search"
4. Navigare tra i risultati

---

## Relazioni con Altre Schede

| Scheda | Relazione |
|--------|-----------|
| **Scheda Sito** | Il sito contiene le tombe |
| **Scheda Struttura** | La struttura fisica della tomba |
| **Scheda Individui** | I resti umani nella tomba |
| **Scheda Inventario Materiali** | I reperti del corredo |
| **Scheda Periodizzazione** | La cronologia |

### Flusso di Lavoro Consigliato

1. Creare la **Scheda Sito** (se non esiste)
2. Creare la **Scheda Struttura** per la tomba
3. Creare la **Scheda Tomba** collegandola alla struttura
4. Creare la **Scheda Individui** per ogni individuo
5. Registrare il corredo nella **Scheda Inventario Materiali**

---

## Best Practices

### Nomenclatura

- Usare sigle coerenti (TM, TB, SEP)
- Numerazione progressiva all'interno del sito
- Documentare le convenzioni adottate

### Descrizione

- Descrivere sistematicamente forma, dimensioni, orientamento
- Documentare lo stato al momento dello scavo
- Separare osservazioni oggettive da interpretazioni

### Corredo

- Registrare posizione esatta di ogni oggetto
- Collegare ogni elemento all'Inventario Materiali
- Documentare associazioni significative

### Periodizzazione

- Basare la datazione su elementi diagnostici
- Indicare il grado di affidabilita
- Confrontare con sepolture simili

---

## Troubleshooting

### Problema: Individuo non disponibile nel menu

**Causa**: L'individuo non e stato ancora creato o non e associato alla struttura.

**Soluzione**:
1. Verificare che esista la Scheda Individui
2. Controllare che l'individuo sia associato alla stessa struttura

### Problema: Corredo non visualizzato nella tabella

**Causa**: I reperti non sono collegati alla struttura.

**Soluzione**:
1. Aprire la Scheda Inventario Materiali
2. Verificare che i reperti abbiano la struttura corretta
3. Aggiornare la scheda Tomba

### Problema: Tomba non visibile su mappa

**Causa**: Geometria non associata.

**Soluzione**:
1. Verificare che esista il layer tomba
2. Controllare che la struttura abbia geometria
3. Verificare il sistema di riferimento

---

## Riferimenti

### Database

- **Tabella**: `tomba_table`
- **Classe mapper**: `TOMBA`
- **ID**: `id_tomba`

### File Sorgente

- **UI**: `gui/ui/Tomba.ui`
- **Controller**: `tabs/Tomba.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Video Tutorial

### Panoramica Scheda Tomba
**Durata**: 5-6 minuti
- Presentazione dell'interfaccia
- Campi principali
- Navigazione tra i tab

[Placeholder video: video_panoramica_tomba.mp4]

### Schedatura Completa di una Tomba
**Durata**: 10-12 minuti
- Creazione nuovo record
- Compilazione di tutti i campi
- Collegamento individui e corredo

[Placeholder video: video_schedatura_tomba.mp4]

### Gestione Corredo Funerario
**Durata**: 6-8 minuti
- Registrazione elementi del corredo
- Collegamento con Inventario Materiali
- Documentazione posizioni

[Placeholder video: video_corredo_tomba.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
