# PyArchInit - Scheda Sito

## Indice
1. [Introduzione](#introduzione)
2. [Accesso alla Scheda](#accesso-alla-scheda)
3. [Interfaccia Utente](#interfaccia-utente)
4. [Dati Descrittivi del Sito](#dati-descrittivi-del-sito)
5. [Toolbar DBMS](#toolbar-dbms)
6. [Funzionalita GIS](#funzionalita-gis)
7. [Generazione Schede US](#generazione-schede-us)
8. [MoveCost - Analisi Percorsi](#movecost---analisi-percorsi)
9. [Esportazione Report](#esportazione-report)
10. [Workflow Operativo](#workflow-operativo)

---

## Introduzione

La **Scheda Sito** e il punto di partenza per la documentazione di uno scavo archeologico in PyArchInit. Ogni progetto archeologico inizia con la creazione di un sito, che funge da contenitore principale per tutte le altre informazioni (Unita Stratigrafiche, Strutture, Reperti, ecc.).

Un **sito archeologico** in PyArchInit rappresenta un'area geografica definita dove si svolgono le attivita di ricerca archeologica. Puo essere uno scavo, un'area di survey, un monumento, ecc.

<!-- VIDEO: Introduzione alla Scheda Sito -->
> **Video Tutorial**: [Inserire link video introduzione scheda sito]

---

## Accesso alla Scheda

Per accedere alla Scheda Sito:

1. Menu **PyArchInit** → **Archaeological record management** → **Site**
2. Oppure dalla toolbar PyArchInit, cliccare sull'icona **Sito**

<!-- IMMAGINE: Screenshot menu accesso scheda sito -->
![Accesso Scheda Sito](images/02_scheda_sito/01_menu_scheda_sito.png)
*Figura 1: Accesso alla Scheda Sito dal menu PyArchInit*

<!-- IMMAGINE: Screenshot toolbar con icona sito -->
![Toolbar Sito](images/02_scheda_sito/02_toolbar_sito.png)
*Figura 2: Icona Scheda Sito nella toolbar*

---

## Interfaccia Utente

La Scheda Sito e divisa in diverse aree funzionali:

<!-- IMMAGINE: Screenshot completo scheda sito con aree numerate -->
![Interfaccia Scheda Sito](images/02_scheda_sito/03_interfaccia_completa.png)
*Figura 3: Interfaccia completa della Scheda Sito*

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Barra degli strumenti per navigazione e gestione record |
| 2 | **Dati Descrittivi** | Campi per inserire le informazioni del sito |
| 3 | **Generatore US** | Strumento per creare schede US in batch |
| 4 | **GIS Viewer** | Controlli per visualizzazione cartografica |
| 5 | **MoveCost** | Strumenti di analisi spaziale avanzata |
| 6 | **Help** | Documentazione e video tutorial |

---

## Dati Descrittivi del Sito

### Tab Dati Descrittivi

<!-- IMMAGINE: Screenshot tab dati descrittivi -->
![Tab Dati Descrittivi](images/02_scheda_sito/04_tab_dati_descrittivi.png)
*Figura 4: Tab Dati Descrittivi*

#### Campi Obbligatori

| Campo | Descrizione | Note |
|-------|-------------|------|
| **Sito** | Nome identificativo del sito | Campo obbligatorio, deve essere univoco |

#### Campi Geografici

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| **Nazione** | Stato in cui si trova il sito | Italia |
| **Regione** | Regione amministrativa | Lazio |
| **Provincia** | Provincia | Roma |
| **Comune** | Comune | Roma |

<!-- IMMAGINE: Screenshot campi geografici compilati -->
![Campi Geografici](images/02_scheda_sito/05_campi_geografici.png)
*Figura 5: Esempio di compilazione campi geografici*

#### Campi Descrittivi

| Campo | Descrizione |
|-------|-------------|
| **Nome** | Nome esteso/descrittivo del sito |
| **Definizione** | Tipologia del sito (da thesaurus) |
| **Descrizione** | Campo testuale libero per descrizione dettagliata |
| **Cartella** | Percorso alla cartella locale del progetto |

<!-- IMMAGINE: Screenshot campo descrizione -->
![Campo Descrizione](images/02_scheda_sito/06_campo_descrizione.png)
*Figura 6: Campo descrizione testuale*

### Definizione Sito (Thesaurus)

Il campo **Definizione** utilizza un vocabolario controllato (thesaurus). Le opzioni disponibili includono:

| Definizione | Descrizione |
|-------------|-------------|
| Area di scavo | Zona sottoposta a indagine stratigrafica |
| Survey area | Area di ricognizione di superficie |
| Sito archeologico | Localita con evidenze archeologiche |
| Monumento | Struttura monumentale singola |
| Necropoli | Area sepolcrale |
| Insediamento | Area abitativa |
| Santuario | Area sacra/cultuale |
| ... | Altre definizioni dal thesaurus |

<!-- IMMAGINE: Screenshot dropdown definizione sito -->
![Definizione Sito](images/02_scheda_sito/07_definizione_sito.png)
*Figura 7: Selezione definizione sito da thesaurus*

### Cartella Progetto

Il campo **Cartella** permette di associare una directory locale al sito per organizzare i file del progetto.

<!-- IMMAGINE: Screenshot selezione cartella -->
![Selezione Cartella](images/02_scheda_sito/08_selezione_cartella.png)
*Figura 8: Selezione cartella progetto*

| Bottone | Funzione |
|---------|----------|
| **...** | Sfoglia per selezionare la cartella |
| **Apri** | Apre la cartella nel file manager |

---

## Toolbar DBMS

La toolbar DBMS fornisce tutti i controlli per la gestione dei record.

<!-- IMMAGINE: Screenshot toolbar DBMS -->
![Toolbar DBMS](images/02_scheda_sito/09_toolbar_dbms.png)
*Figura 9: Toolbar DBMS*

### Indicatori di Stato

| Indicatore | Descrizione |
|------------|-------------|
| **DB Info** | Mostra il tipo di database connesso (SQLite/PostgreSQL) |
| **Status** | Stato corrente: `Usa` (browse), `Trova` (search), `Nuovo Record` |
| **Ordinamento** | Indica se i record sono ordinati |
| **record n.** | Numero del record corrente |
| **record tot.** | Totale dei record |

<!-- IMMAGINE: Screenshot indicatori stato -->
![Indicatori Stato](images/02_scheda_sito/10_indicatori_stato.png)
*Figura 10: Indicatori di stato*

### Navigazione Record

| Bottone | Icona | Funzione | Shortcut |
|---------|-------|----------|----------|
| **First rec** | |< | Vai al primo record | - |
| **Prev rec** | < | Vai al record precedente | - |
| **Next rec** | > | Vai al record successivo | - |
| **Last rec** | >| | Vai all'ultimo record | - |

<!-- IMMAGINE: Screenshot bottoni navigazione -->
![Navigazione](images/02_scheda_sito/11_navigazione_record.png)
*Figura 11: Bottoni di navigazione*

### Gestione Record

| Bottone | Funzione | Descrizione |
|---------|----------|-------------|
| **New record** | Crea nuovo | Prepara il form per inserire un nuovo sito |
| **Save** | Salva | Salva le modifiche o il nuovo record |
| **Delete record** | Elimina | Elimina il record corrente (con conferma) |
| **View all records** | Visualizza tutti | Mostra tutti i record nel database |

<!-- IMMAGINE: Screenshot bottoni gestione -->
![Gestione Record](images/02_scheda_sito/12_gestione_record.png)
*Figura 12: Bottoni gestione record*

### Ricerca e Ordinamento

| Bottone | Funzione | Descrizione |
|---------|----------|-------------|
| **new search** | Nuova ricerca | Avvia modalita ricerca |
| **search !!!** | Esegui ricerca | Esegue la ricerca con i criteri inseriti |
| **Order by** | Ordina | Apre pannello ordinamento |

<!-- IMMAGINE: Screenshot ricerca -->
![Ricerca](images/02_scheda_sito/13_ricerca.png)
*Figura 13: Funzioni di ricerca*

#### Come Effettuare una Ricerca

1. Cliccare **new search** - lo status cambia in "Trova"
2. Compilare i campi con i criteri di ricerca
3. Cliccare **search !!!** per eseguire
4. I risultati vengono mostrati e si puo navigare tra essi

<!-- IMMAGINE: Screenshot esempio ricerca -->
![Esempio Ricerca](images/02_scheda_sito/14_esempio_ricerca.png)
*Figura 14: Esempio di ricerca per regione*

<!-- VIDEO: Come effettuare ricerche -->
> **Video Tutorial**: [Inserire link video ricerca]

#### Pannello Ordinamento

Cliccando **Order by** si apre un pannello per ordinare i record:

<!-- IMMAGINE: Screenshot pannello ordinamento -->
![Pannello Ordinamento](images/02_scheda_sito/15_pannello_ordinamento.png)
*Figura 15: Pannello di ordinamento*

| Opzione | Descrizione |
|---------|-------------|
| **Campo** | Seleziona il campo per l'ordinamento |
| **Ascendente** | Ordine A-Z, 0-9 |
| **Discendente** | Ordine Z-A, 9-0 |

---

## Funzionalita GIS

La Scheda Sito offre diverse funzionalita di integrazione GIS.

<!-- IMMAGINE: Screenshot sezione GIS -->
![Sezione GIS](images/02_scheda_sito/16_sezione_gis.png)
*Figura 16: Sezione funzionalita GIS*

### Caricamento Layer

| Bottone | Funzione |
|---------|----------|
| **GIS viewer** | Carica tutti i layer per inserire geometrie |
| **Carica layer sito** (icona globo) | Carica solo i layer del sito corrente |
| **Carica tutti i siti** (icona globo multiplo) | Carica i layer di tutti i siti |

<!-- IMMAGINE: Screenshot bottoni GIS -->
![Bottoni GIS](images/02_scheda_sito/17_bottoni_gis.png)
*Figura 17: Bottoni per caricamento layer GIS*

### Geocoding - Ricerca Indirizzo

La funzione di geocoding permette di localizzare un indirizzo sulla mappa.

<!-- IMMAGINE: Screenshot geocoding -->
![Geocoding](images/02_scheda_sito/18_geocoding.png)
*Figura 18: Campo ricerca indirizzo*

1. Inserire l'indirizzo nel campo di testo
2. Cliccare **Zoom on**
3. La mappa si centra sulla posizione trovata

| Campo | Descrizione |
|-------|-------------|
| **Indirizzo** | Inserire via, citta, nazione |
| **Zoom on** | Centra la mappa sull'indirizzo |

### Modalita GIS Attiva

Il toggle **Abilita il caricamento delle ricerche** attiva/disattiva la visualizzazione automatica dei risultati di ricerca sulla mappa.

<!-- IMMAGINE: Screenshot toggle GIS -->
![Toggle GIS](images/02_scheda_sito/19_toggle_gis.png)
*Figura 19: Toggle modalita GIS*

- **Attivo**: Le ricerche vengono visualizzate automaticamente sulla mappa
- **Disattivo**: Le ricerche non modificano la visualizzazione mappa

### WMS Vincoli Archeologici

Il bottone WMS carica il layer dei vincoli archeologici dal Ministero della Cultura italiano.

<!-- IMMAGINE: Screenshot WMS vincoli -->
![WMS Vincoli](images/02_scheda_sito/20_wms_vincoli.png)
*Figura 20: Layer WMS vincoli archeologici*

### Base Maps

Il bottone Base Maps permette di caricare mappe di base (Google Maps, OpenStreetMap, ecc.).

<!-- IMMAGINE: Screenshot base maps -->
![Base Maps](images/02_scheda_sito/21_base_maps.png)
*Figura 21: Selezione base maps*

---

## Generazione Schede US

Questa funzionalita permette di creare automaticamente un numero arbitrario di schede US per il sito corrente.

<!-- IMMAGINE: Screenshot generatore US -->
![Generatore US](images/02_scheda_sito/22_generatore_us.png)
*Figura 22: Sezione generazione schede US*

### Parametri

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| **Numero Area** | Numero dell'area di scavo | 1 |
| **Numero di scheda US da cui partire** | Numero iniziale US | 1 |
| **Numero di schede da creare** | Quante US generare | 100 |
| **Tipo** | US o USM | US |

### Procedura

1. Assicurarsi di essere sul sito corretto
2. Inserire il numero dell'area
3. Inserire il numero US di partenza
4. Inserire quante schede creare
5. Selezionare il tipo (US o USM)
6. Cliccare **Genera US**

<!-- IMMAGINE: Screenshot esempio generazione -->
![Esempio Generazione](images/02_scheda_sito/23_esempio_generazione.png)
*Figura 23: Esempio generazione 50 US partendo da US 101*

<!-- VIDEO: Come generare schede US in batch -->
> **Video Tutorial**: [Inserire link video generazione US]

---

## MoveCost - Analisi Percorsi

La sezione **MovecostToPyarchinit** integra funzioni R per l'analisi dei percorsi di minor costo (Least Cost Path Analysis).

<!-- IMMAGINE: Screenshot sezione MoveCost -->
![MoveCost](images/02_scheda_sito/24_movecost_sezione.png)
*Figura 24: Sezione MoveCost*

### Prerequisiti

- **R** installato sul sistema
- Package R **movecost** installato
- **Processing R Provider** plugin attivo in QGIS

### Funzioni Disponibili

| Funzione | Descrizione |
|----------|-------------|
| **movecost** | Calcola il costo di movimento e percorsi di minor costo da un punto origine |
| **movecost by polygon** | Come sopra, usando un poligono per scaricare il DTM |
| **movebound** | Calcola i confini del costo di cammino attorno a punti |
| **movebound by polygon** | Come sopra, usando un poligono |
| **movcorr** | Calcola corridoi di minor costo tra punti |
| **movecorr by polygon** | Come sopra, usando un poligono |
| **movalloc** | Allocazione territoriale basata sui costi |
| **movealloc by polygon** | Come sopra, usando un poligono |

<!-- IMMAGINE: Screenshot esempio movecost -->
![Esempio MoveCost](images/02_scheda_sito/25_esempio_movecost.png)
*Figura 25: Esempio output analisi MoveCost*

### Add Scripts

Il bottone **Add scripts** installa automaticamente gli script R necessari nel profilo QGIS.

<!-- VIDEO: Analisi MoveCost -->
> **Video Tutorial**: [Inserire link video MoveCost]

---

## Esportazione Report

### Esporta Relazione di Scavo

Il bottone **Esporta** genera un PDF con la relazione di scavo per il sito corrente.

<!-- IMMAGINE: Screenshot esportazione -->
![Esportazione](images/02_scheda_sito/26_esportazione.png)
*Figura 26: Bottone esportazione relazione*

**Nota**: Questa funzione e in versione di sviluppo e potrebbe contenere bug.

Il report include:
- Dati identificativi del sito
- Elenco delle US
- Sequenza stratigrafica
- Matrix di Harris (se disponibile)

<!-- IMMAGINE: Screenshot esempio PDF -->
![Esempio PDF](images/02_scheda_sito/27_esempio_pdf.png)
*Figura 27: Esempio di relazione PDF generata*

---

## Workflow Operativo

### Creare un Nuovo Sito

<!-- VIDEO: Workflow creazione nuovo sito -->
> **Video Tutorial**: [Inserire link video workflow nuovo sito]

#### Step 1: Aprire la Scheda Sito
<!-- IMMAGINE: Step 1 -->
![Workflow Step 1](images/02_scheda_sito/28_workflow_step1.png)
*Figura 28: Step 1 - Apertura scheda*

#### Step 2: Cliccare "New record"
Lo status cambia in "Nuovo Record" e i campi si svuotano.

<!-- IMMAGINE: Step 2 -->
![Workflow Step 2](images/02_scheda_sito/29_workflow_step2.png)
*Figura 29: Step 2 - Nuovo record*

#### Step 3: Compilare i Dati Obbligatori
Inserire almeno il nome del sito (campo obbligatorio).

<!-- IMMAGINE: Step 3 -->
![Workflow Step 3](images/02_scheda_sito/30_workflow_step3.png)
*Figura 30: Step 3 - Compilazione dati*

#### Step 4: Compilare i Dati Geografici
Inserire nazione, regione, provincia, comune.

<!-- IMMAGINE: Step 4 -->
![Workflow Step 4](images/02_scheda_sito/31_workflow_step4.png)
*Figura 31: Step 4 - Dati geografici*

#### Step 5: Selezionare la Definizione
Scegliere la tipologia del sito dal thesaurus.

<!-- IMMAGINE: Step 5 -->
![Workflow Step 5](images/02_scheda_sito/32_workflow_step5.png)
*Figura 32: Step 5 - Definizione sito*

#### Step 6: Aggiungere Descrizione
Compilare il campo descrizione con informazioni dettagliate.

<!-- IMMAGINE: Step 6 -->
![Workflow Step 6](images/02_scheda_sito/33_workflow_step6.png)
*Figura 33: Step 6 - Descrizione*

#### Step 7: Salvare
Cliccare **Save** per salvare il nuovo sito.

<!-- IMMAGINE: Step 7 -->
![Workflow Step 7](images/02_scheda_sito/34_workflow_step7.png)
*Figura 34: Step 7 - Salvataggio*

#### Step 8: Verificare
Il sito e stato creato, lo status torna a "Usa".

<!-- IMMAGINE: Step 8 -->
![Workflow Step 8](images/02_scheda_sito/35_workflow_step8.png)
*Figura 35: Step 8 - Verifica creazione*

### Modificare un Sito Esistente

1. Navigare al sito da modificare
2. Modificare i campi desiderati
3. Cliccare **Save**
4. Confermare il salvataggio delle modifiche

### Eliminare un Sito

**Attenzione**: L'eliminazione di un sito NON elimina automaticamente le US, strutture e reperti associati.

1. Navigare al sito da eliminare
2. Cliccare **Delete record**
3. Confermare l'eliminazione

<!-- IMMAGINE: Screenshot conferma eliminazione -->
![Conferma Eliminazione](images/02_scheda_sito/36_conferma_eliminazione.png)
*Figura 36: Dialog conferma eliminazione*

---

## Tab Help

La scheda Help fornisce accesso rapido alla documentazione.

<!-- IMMAGINE: Screenshot tab help -->
![Tab Help](images/02_scheda_sito/37_tab_help.png)
*Figura 37: Tab Help*

| Risorsa | Link |
|---------|------|
| Video Tutorial | YouTube |
| Documentazione | pyarchinit.github.io |
| Community | Facebook UnaQuantum |

---

## Gestione Concorrenza (PostgreSQL)

Quando si usa PostgreSQL in ambiente multi-utente, il sistema gestisce automaticamente i conflitti di modifica:

- **Indicatore di blocco**: Mostra se il record e in modifica da un altro utente
- **Controllo versione**: Rileva modifiche concorrenti
- **Risoluzione conflitti**: Permette di scegliere quale versione mantenere

<!-- IMMAGINE: Screenshot indicatore concorrenza -->
![Concorrenza](images/02_scheda_sito/38_concorrenza.png)
*Figura 38: Indicatore di record bloccato*

---

## Risoluzione Problemi

### Il sito non viene salvato
- Verificare che il campo "Sito" sia compilato
- Verificare che il nome non esista gia nel database

### I layer GIS non si caricano
- Verificare la connessione al database
- Verificare che esistano geometrie associate al sito

### Errore nel geocoding
- Verificare la connessione internet
- Controllare che l'indirizzo sia scritto correttamente

### MoveCost non funziona
- Verificare che R sia installato
- Verificare che il plugin Processing R Provider sia attivo
- Installare il package movecost in R

---

## Note Tecniche

- **Tabella database**: `site_table`
- **Campi database**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Layer GIS associati**: PYSITO_POLYGON, PYSITO_POINT
- **Thesaurus**: tipologia_sigla = '1.1'

---

## Lista Immagini da Inserire

| Nome File | Descrizione |
|-----------|-------------|
| `01_menu_scheda_sito.png` | Menu accesso scheda sito |
| `02_toolbar_sito.png` | Toolbar con icona sito |
| `03_interfaccia_completa.png` | Interfaccia completa con aree numerate |
| `04_tab_dati_descrittivi.png` | Tab dati descrittivi |
| `05_campi_geografici.png` | Campi geografici compilati |
| `06_campo_descrizione.png` | Campo descrizione |
| `07_definizione_sito.png` | Dropdown definizione sito |
| `08_selezione_cartella.png` | Selezione cartella progetto |
| `09_toolbar_dbms.png` | Toolbar DBMS completa |
| `10_indicatori_stato.png` | Indicatori di stato |
| `11_navigazione_record.png` | Bottoni navigazione |
| `12_gestione_record.png` | Bottoni gestione record |
| `13_ricerca.png` | Funzioni ricerca |
| `14_esempio_ricerca.png` | Esempio ricerca |
| `15_pannello_ordinamento.png` | Pannello ordinamento |
| `16_sezione_gis.png` | Sezione GIS |
| `17_bottoni_gis.png` | Bottoni GIS |
| `18_geocoding.png` | Campo geocoding |
| `19_toggle_gis.png` | Toggle modalita GIS |
| `20_wms_vincoli.png` | WMS vincoli |
| `21_base_maps.png` | Base maps |
| `22_generatore_us.png` | Generatore US |
| `23_esempio_generazione.png` | Esempio generazione |
| `24_movecost_sezione.png` | Sezione MoveCost |
| `25_esempio_movecost.png` | Output MoveCost |
| `26_esportazione.png` | Bottone esportazione |
| `27_esempio_pdf.png` | PDF generato |
| `28_workflow_step1.png` - `35_workflow_step8.png` | Steps workflow |
| `36_conferma_eliminazione.png` | Conferma eliminazione |
| `37_tab_help.png` | Tab Help |
| `38_concorrenza.png` | Indicatore concorrenza |

## Lista Video da Inserire

| Placeholder | Descrizione |
|-------------|-------------|
| Video introduzione scheda sito | Panoramica della scheda |
| Video ricerca | Come effettuare ricerche |
| Video generazione US | Come generare US in batch |
| Video MoveCost | Analisi percorsi |
| Video workflow nuovo sito | Creazione nuovo sito passo-passo |

---

*Documentazione PyArchInit - Scheda Sito*
*Versione: 4.9.x*
*Ultimo aggiornamento: Gennaio 2026*
