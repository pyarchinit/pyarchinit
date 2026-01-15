# Tutorial 04: Scheda Periodizzazione

## Indice
1. [Introduzione](#introduzione)
2. [Accesso alla Scheda](#accesso-alla-scheda)
3. [Interfaccia Utente](#interfaccia-utente)
4. [Concetti Fondamentali](#concetti-fondamentali)
5. [Campi della Scheda](#campi-della-scheda)
6. [Toolbar DBMS](#toolbar-dbms)
7. [Funzionalita GIS](#funzionalita-gis)
8. [Export PDF](#export-pdf)
9. [Integrazione AI](#integrazione-ai)
10. [Workflow Operativo](#workflow-operativo)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduzione

La **Scheda Periodizzazione** e uno strumento fondamentale per la gestione delle fasi cronologiche di uno scavo archeologico. Permette di definire i periodi e le fasi che caratterizzano la sequenza stratigrafica del sito, associando a ciascuna coppia periodo/fase una datazione cronologica e una descrizione.

### Scopo della Scheda

- Definire la sequenza cronologica dello scavo
- Associare periodi e fasi alle unita stratigrafiche
- Gestire la cronologia assoluta (anni) e relativa (periodi storici)
- Visualizzare le US per periodo/fase sulla mappa GIS
- Generare report PDF della periodizzazione

### Relazione con altre Schede

La Scheda Periodizzazione e strettamente collegata a:
- **Scheda US/USM**: Ogni US viene assegnata a un periodo e una fase
- **Scheda Sito**: I periodi sono specifici per ciascun sito
- **Matrix di Harris**: I periodi colorano il Matrix per fase cronologica

![Panoramica Scheda Periodizzazione](images/04_scheda_periodizzazione/01_panoramica.png)
*Figura 1: Vista generale della Scheda Periodizzazione*

---

## Accesso alla Scheda

### Da Menu

1. Aprire QGIS con il plugin PyArchInit attivo
2. Menu **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

![Menu Periodizzazione](images/04_scheda_periodizzazione/02_menu_accesso.png)
*Figura 2: Accesso alla scheda dal menu*

### Da Toolbar

1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Periodizzazione** (icona sito con orologio)

![Toolbar Periodizzazione](images/04_scheda_periodizzazione/03_toolbar_accesso.png)
*Figura 3: Icona nella toolbar*

---

## Interfaccia Utente

L'interfaccia della Scheda Periodizzazione e organizzata in modo semplice e lineare:

![Interfaccia Completa](images/04_scheda_periodizzazione/04_interfaccia_completa.png)
*Figura 4: Layout completo dell'interfaccia*

### Aree Principali

| Area | Descrizione |
|------|-------------|
| **1. DBMS Toolbar** | Barra strumenti per navigazione e gestione record |
| **2. Indicatori Stato** | DB Info, Status, Ordinamento |
| **3. Dati Identificativi** | Sito, Periodo, Fase, Codice periodo |
| **4. Dati Descrittivi** | Descrizione testuale del periodo |
| **5. Cronologia** | Anni iniziale e finale |
| **6. Datazione Estesa** | Selezione da vocabolario epoche storiche |

---

## Concetti Fondamentali

### Periodo e Fase

Il sistema di periodizzazione in PyArchInit si basa su una struttura gerarchica a due livelli:

#### Periodo
Il **Periodo** rappresenta una macro-fase cronologica dello scavo. E identificato da un numero intero (1, 2, 3, ...) e rappresenta le grandi suddivisioni della sequenza stratigrafica.

Esempi di periodi:
- Periodo 1: Eta contemporanea
- Periodo 2: Eta medievale
- Periodo 3: Eta romana imperiale
- Periodo 4: Eta romana repubblicana

#### Fase
La **Fase** rappresenta una suddivisione interna del periodo. Anche questa e identificata da un numero intero e permette di dettagliare ulteriormente la sequenza.

Esempi di fasi nel Periodo 3 (Eta romana imperiale):
- Fase 1: III-IV secolo d.C.
- Fase 2: II secolo d.C.
- Fase 3: I secolo d.C.

### Codice Periodo

Il **Codice Periodo** e un identificatore numerico univoco che collega la coppia periodo/fase alle US. Quando si assegna un periodo/fase a una US nella Scheda US, viene utilizzato questo codice.

> **Importante**: Il codice periodo deve essere univoco per ogni combinazione sito/periodo/fase.

### Schema Concettuale

```
Sito
└── Periodo 1 (Eta contemporanea)
│   ├── Fase 1 → Codice 101
│   └── Fase 2 → Codice 102
├── Periodo 2 (Eta medievale)
│   ├── Fase 1 → Codice 201
│   ├── Fase 2 → Codice 202
│   └── Fase 3 → Codice 203
└── Periodo 3 (Eta romana)
    ├── Fase 1 → Codice 301
    └── Fase 2 → Codice 302
```

---

## Campi della Scheda

### Campi Identificativi

#### Sito
- **Tipo**: ComboBox (sola lettura in modalita browse)
- **Obbligatorio**: Si
- **Descrizione**: Seleziona il sito archeologico a cui appartiene la periodizzazione
- **Note**: Se e impostato un sito predefinito nella configurazione, questo campo sara precompilato e non modificabile

![Campo Sito](images/04_scheda_periodizzazione/05_campo_sito.png)
*Figura 5: Campo selezione sito*

#### Periodo
- **Tipo**: ComboBox editabile
- **Obbligatorio**: Si
- **Valori**: Numeri interi da 1 a 15 (predefiniti) o valori personalizzati
- **Descrizione**: Numero del periodo cronologico
- **Note**: I numeri bassi indicano periodi piu recenti, i numeri alti periodi piu antichi

#### Fase
- **Tipo**: ComboBox editabile
- **Obbligatorio**: Si
- **Valori**: Numeri interi da 1 a 15 (predefiniti) o valori personalizzati
- **Descrizione**: Numero della fase all'interno del periodo

![Campi Periodo e Fase](images/04_scheda_periodizzazione/06_campi_periodo_fase.png)
*Figura 6: Campi Periodo e Fase*

#### Codice Periodo
- **Tipo**: LineEdit (testo)
- **Obbligatorio**: No (ma fortemente consigliato)
- **Descrizione**: Codice numerico univoco per identificare la coppia periodo/fase
- **Suggerimento**: Usare una convenzione come `[periodo][fase]` (es. 101, 102, 201, 301)

![Campo Codice Periodo](images/04_scheda_periodizzazione/07_codice_periodo.png)
*Figura 7: Campo Codice Periodo*

### Campi Descrittivi

#### Descrizione
- **Tipo**: TextEdit (multilinea)
- **Obbligatorio**: No
- **Descrizione**: Descrizione testuale del periodo/fase
- **Contenuto suggerito**:
  - Caratteristiche generali del periodo
  - Eventi storici correlati
  - Tipologie di strutture/materiali attesi
  - Riferimenti bibliografici

![Campo Descrizione](images/04_scheda_periodizzazione/08_campo_descrizione.png)
*Figura 8: Campo descrizione*

### Campi Cronologici

#### Cronologia Iniziale
- **Tipo**: LineEdit (numerico)
- **Obbligatorio**: No
- **Formato**: Anno numerico
- **Note**:
  - Valori positivi = d.C.
  - Valori negativi = a.C.
  - Esempio: `-100` per 100 a.C., `200` per 200 d.C.

#### Cronologia Finale
- **Tipo**: LineEdit (numerico)
- **Obbligatorio**: No
- **Formato**: Anno numerico (stesse convenzioni di Cronologia Iniziale)

![Campi Cronologia](images/04_scheda_periodizzazione/09_campi_cronologia.png)
*Figura 9: Campi Cronologia iniziale e finale*

#### Datazione Estesa (Epoche Storiche)
- **Tipo**: ComboBox editabile con vocabolario precaricato
- **Obbligatorio**: No
- **Descrizione**: Selezione da un vocabolario di epoche storiche predefinite
- **Funzionalita automatica**: Selezionando un'epoca, i campi Cronologia Iniziale e Finale vengono compilati automaticamente

![Datazione Estesa](images/04_scheda_periodizzazione/10_datazione_estesa.png)
*Figura 10: ComboBox Datazione Estesa con epoche precaricate*

### Vocabolario Epoche Storiche

Il vocabolario include una vasta gamma di periodi storici:

| Categoria | Esempi |
|-----------|--------|
| **Eta Contemporanea** | XXI secolo, XX secolo |
| **Eta Moderna** | XIX-XVI secolo |
| **Eta Medievale** | XV-VIII secolo |
| **Eta Antica** | VII-I secolo |
| **Impero Romano** | Periodi specifici (Giulio-Claudio, Flavio, ecc.) |
| **Impero Bizantino** | Periodi specifici |
| **Preistoria** | Paleolitico, Mesolitico, Neolitico, Eta del Bronzo, Eta del Ferro |

---

## Toolbar DBMS

La toolbar DBMS permette la gestione completa dei record:

![Toolbar DBMS](images/04_scheda_periodizzazione/11_toolbar_dbms.png)
*Figura 11: Toolbar DBMS completa*

### Pulsanti di Navigazione

| Icona | Nome | Funzione | Scorciatoia |
|-------|------|----------|-------------|
| ![First](images/icons/first.png) | First | Vai al primo record | - |
| ![Prev](images/icons/prev.png) | Prev | Vai al record precedente | - |
| ![Next](images/icons/next.png) | Next | Vai al record successivo | - |
| ![Last](images/icons/last.png) | Last | Vai all'ultimo record | - |

### Pulsanti di Gestione Record

| Icona | Nome | Funzione |
|-------|------|----------|
| ![New](images/icons/new.png) | New record | Crea un nuovo record |
| ![Save](images/icons/save.png) | Save | Salva le modifiche |
| ![Delete](images/icons/delete.png) | Delete | Elimina il record corrente |
| ![View All](images/icons/view_all.png) | View all | Visualizza tutti i record |

### Pulsanti di Ricerca

| Icona | Nome | Funzione |
|-------|------|----------|
| ![New Search](images/icons/new_search.png) | New search | Attiva modalita ricerca |
| ![Search](images/icons/search.png) | Search!!! | Esegue la ricerca |
| ![Sort](images/icons/sort.png) | Order by | Ordina i record |

### Indicatori di Stato

![Indicatori Stato](images/04_scheda_periodizzazione/12_indicatori_stato.png)
*Figura 12: Indicatori di stato*

| Indicatore | Descrizione |
|------------|-------------|
| **Status** | Modalita corrente: "Usa" (browse), "Trova" (ricerca), "Nuovo Record" |
| **Ordinamento** | "Non ordinati" o "Ordinati" |
| **record n.** | Numero del record corrente |
| **record tot.** | Numero totale di record |

---

## Funzionalita GIS

La Scheda Periodizzazione offre potenti funzionalita di visualizzazione GIS per vedere le US associate a ciascun periodo/fase.

### Pulsanti GIS

![Pulsanti GIS](images/04_scheda_periodizzazione/13_pulsanti_gis.png)
*Figura 13: Pulsanti per visualizzazione GIS*

#### Visualizza Periodo Singolo (Icona GIS)
- **Funzione**: Carica sulla mappa QGIS tutte le US associate al periodo/fase corrente
- **Requisito**: Il campo Codice Periodo deve essere compilato
- **Layer caricati**: US e USM filtrate per codice periodo

#### Visualizza Tutti i Periodi - US (Icona Layer multipli)
- **Funzione**: Carica sulla mappa tutti i periodi come layer separati (solo US)
- **Risultato**: Un layer per ogni combinazione periodo/fase

#### Visualizza Tutti i Periodi - USM (Icona GIS3)
- **Funzione**: Carica sulla mappa tutti i periodi come layer separati (solo USM)
- **Risultato**: Un layer per ogni combinazione periodo/fase per le unita murarie

### Visualizzazione su Mappa

![Mappa con Periodi](images/04_scheda_periodizzazione/14_mappa_periodi.png)
*Figura 14: US visualizzate per periodo sulla mappa QGIS*

Quando si caricano i layer per periodo:
- Ogni periodo/fase ha un colore distintivo
- Le US sono filtrate in base al codice periodo assegnato
- E possibile attivare/disattivare i singoli layer

---

## Export PDF

La scheda offre due modalita di export PDF:

### Export Scheda Singola

![Pulsante PDF Scheda](images/04_scheda_periodizzazione/15_pulsante_pdf_scheda.png)
*Figura 15: Pulsante export PDF scheda*

- **Icona**: PDF
- **Funzione**: Genera un PDF con i dati del periodo/fase corrente
- **Contenuto**:
  - Informazioni identificative (Sito, Periodo, Fase)
  - Cronologia (iniziale, finale, datazione estesa)
  - Descrizione completa

### Export Lista Periodizzazione

![Pulsante PDF Lista](images/04_scheda_periodizzazione/16_pulsante_pdf_lista.png)
*Figura 16: Pulsante export PDF lista*

- **Icona**: Foglio/Sheet
- **Funzione**: Genera un PDF con l'elenco di tutti i periodi/fasi del sito
- **Contenuto**: Tabella riepilogativa con tutti i periodi

### Esempio PDF Generato

![Esempio PDF](images/04_scheda_periodizzazione/17_esempio_pdf.png)
*Figura 17: Esempio di PDF generato*

---

## Integrazione AI

La Scheda Periodizzazione include un'integrazione con GPT per ottenere suggerimenti automatici sulla descrizione dei periodi storici.

### Pulsante Suggerimenti

![Pulsante Suggerimenti](images/04_scheda_periodizzazione/18_pulsante_suggerimenti.png)
*Figura 18: Pulsante Suggerimenti AI*

### Funzionamento

1. Selezionare un'epoca storica dal campo **Datazione Estesa**
2. Cliccare sul pulsante **Suggerimenti**
3. Selezionare il modello GPT da utilizzare (gpt-4o o gpt-4)
4. Il sistema genera automaticamente:
   - Una descrizione del periodo storico
   - 3 link Wikipedia pertinenti
5. Il testo generato puo essere inserito nel campo Descrizione

### Configurazione API Key

Per utilizzare questa funzionalita:
1. Ottenere una API Key da OpenAI
2. Al primo utilizzo, il sistema chiede di inserire la chiave
3. La chiave viene salvata in `PYARCHINIT_HOME/bin/gpt_api_key.txt`

> **Nota**: Questa funzionalita richiede una connessione internet e un account OpenAI con crediti disponibili.

---

## Workflow Operativo

### Creazione di una Nuova Periodizzazione

#### Passo 1: Accesso alla Scheda
1. Aprire la Scheda Periodizzazione dal menu o dalla toolbar
2. Verificare la connessione al database (indicatore Status)

![Workflow Step 1](images/04_scheda_periodizzazione/19_workflow_step1.png)
*Figura 19: Apertura scheda*

#### Passo 2: Nuovo Record
1. Cliccare sul pulsante **New record**
2. Lo Status cambia in "Nuovo Record"
3. I campi diventano editabili

![Workflow Step 2](images/04_scheda_periodizzazione/20_workflow_step2.png)
*Figura 20: Click su New record*

#### Passo 3: Selezione Sito
1. Se non preimpostato, selezionare il **Sito** dal menu a tendina
2. Il sito deve gia esistere nella Scheda Sito

![Workflow Step 3](images/04_scheda_periodizzazione/21_workflow_step3.png)
*Figura 21: Selezione sito*

#### Passo 4: Definizione Periodo e Fase
1. Selezionare o digitare il numero del **Periodo**
2. Selezionare o digitare il numero della **Fase**
3. Inserire il **Codice Periodo** univoco

![Workflow Step 4](images/04_scheda_periodizzazione/22_workflow_step4.png)
*Figura 22: Definizione periodo e fase*

#### Passo 5: Cronologia
1. Selezionare la **Datazione Estesa** dal vocabolario epoche
2. I campi Cronologia Iniziale e Finale si compilano automaticamente
3. Oppure inserire manualmente gli anni

![Workflow Step 5](images/04_scheda_periodizzazione/23_workflow_step5.png)
*Figura 23: Impostazione cronologia*

#### Passo 6: Descrizione
1. Compilare il campo **Descrizione** con le informazioni sul periodo
2. Opzionale: usare il pulsante **Suggerimenti** per ottenere un testo AI

![Workflow Step 6](images/04_scheda_periodizzazione/24_workflow_step6.png)
*Figura 24: Compilazione descrizione*

#### Passo 7: Salvataggio
1. Cliccare sul pulsante **Save**
2. Il record viene salvato nel database
3. Lo Status torna a "Usa"

![Workflow Step 7](images/04_scheda_periodizzazione/25_workflow_step7.png)
*Figura 25: Salvataggio*

### Schema di Periodizzazione Consigliato

Per uno scavo tipico, si consiglia di creare la periodizzazione seguendo questo schema:

| Periodo | Fase | Codice | Descrizione |
|---------|------|--------|-------------|
| 1 | 1 | 101 | Eta contemporanea - Arativo |
| 1 | 2 | 102 | Eta contemporanea - Abbandono |
| 2 | 1 | 201 | Eta medievale - Fase tarda |
| 2 | 2 | 202 | Eta medievale - Fase centrale |
| 2 | 3 | 203 | Eta medievale - Fase iniziale |
| 3 | 1 | 301 | Eta romana - Fase imperiale |
| 3 | 2 | 302 | Eta romana - Fase repubblicana |
| 4 | 1 | 401 | Eta preromana |

---

## Best Practices

### Convenzioni di Numerazione

1. **Periodi**: Numerare dal piu recente (1) al piu antico
2. **Fasi**: Numerare dalla piu recente (1) alla piu antica all'interno del periodo
3. **Codici**: Usare la formula `[periodo * 100 + fase]` per codici univoci

### Descrizioni Efficaci

Una buona descrizione del periodo dovrebbe includere:
- Inquadramento cronologico
- Caratteristiche principali del periodo
- Tipi di strutture/materiali attesi
- Confronti con altri siti coevi
- Riferimenti bibliografici

### Gestione della Cronologia

- Usare sempre anni numerici per le cronologie
- Per date a.C., usare numeri negativi
- Verificare la coerenza: la cronologia finale deve essere >= iniziale (in valore assoluto per a.C.)

### Collegamento con le US

Dopo aver creato la periodizzazione:
1. Aprire la Scheda US
2. Nel tab **Periodizzazione**, assegnare Periodo iniziale/finale e Fase iniziale/finale
3. Il sistema associera automaticamente la US alla periodizzazione

---

## Troubleshooting

### Problemi Comuni

#### "Period code not add"
- **Causa**: Il campo Codice Periodo e vuoto
- **Soluzione**: Compilare il campo Codice Periodo prima di usare le funzioni GIS

#### Cronologia non si compila automaticamente
- **Causa**: L'epoca selezionata non ha dati associati
- **Soluzione**: Verificare che l'epoca sia presente nel file CSV delle epoche storiche

#### Errore nel salvataggio: record duplicato
- **Causa**: Esiste gia un record con la stessa combinazione Sito/Periodo/Fase
- **Soluzione**: Verificare i valori e usare una combinazione univoca

#### Le US non appaiono nella visualizzazione GIS
- **Causa**: Le US non hanno il codice periodo assegnato
- **Soluzione**:
  1. Verificare nella Scheda US che i campi Periodo/Fase siano compilati
  2. Verificare che il Codice Periodo corrisponda

#### Suggerimenti AI non funziona
- **Causa**: API Key mancante o non valida
- **Soluzione**:
  1. Verificare la connessione internet
  2. Controllare la validita della API Key
  3. Reinstallare le librerie: `pip install --upgrade openai pydantic`

---

## Video Tutorial

### Video 1: Panoramica Scheda Periodizzazione
*Durata: 3-4 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Apertura della scheda
- Descrizione dell'interfaccia
- Navigazione tra i record

### Video 2: Creazione Periodizzazione Completa
*Durata: 5-6 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Creazione di una nuova periodizzazione
- Compilazione di tutti i campi
- Utilizzo del vocabolario epoche
- Salvataggio

### Video 3: Visualizzazione GIS per Periodo
*Durata: 3-4 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Utilizzo dei pulsanti GIS
- Visualizzazione delle US per periodo
- Gestione dei layer caricati

---

## Riepilogo Campi

| Campo | Tipo | Obbligatorio | Database |
|-------|------|--------------|----------|
| Sito | ComboBox | Si | sito |
| Periodo | ComboBox | Si | periodo |
| Fase | ComboBox | Si | fase |
| Codice Periodo | LineEdit | No | cont_per |
| Descrizione | TextEdit | No | descrizione |
| Cronologia Iniziale | LineEdit | No | cron_iniziale |
| Cronologia Finale | LineEdit | No | cron_finale |
| Datazione Estesa | ComboBox | No | datazione_estesa |

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sketches of Sketches*
