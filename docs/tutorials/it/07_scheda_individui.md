# Tutorial 07: Scheda Individui

## Introduzione

La **Scheda Individui** e il modulo di PyArchInit dedicato alla documentazione antropologica dei resti umani rinvenuti durante lo scavo. Questa scheda registra informazioni sul sesso, l'eta, la posizione del corpo e lo stato di conservazione dello scheletro.

### Concetti Base

**Individuo in PyArchInit:**
- Un individuo e un insieme di resti ossei attribuibili a una singola persona
- E collegato alla Scheda Tomba (contesto sepolcrale)
- E collegato alla Scheda Struttura (struttura fisica)
- Puo essere collegato all'Archeozoologia per analisi specifiche

**Dati Antropologici:**
- Stima del sesso biologico
- Stima dell'eta alla morte
- Posizione e orientamento del corpo
- Stato di conservazione e completezza

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda Individui** (o **Individual form**)

![Menu accesso](images/07_scheda_individui/02_menu_accesso.png)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Individui** (figura umana)

![Toolbar accesso](images/07_scheda_individui/03_toolbar_accesso.png)

---

## Panoramica dell'Interfaccia

La scheda presenta un layout organizzato in sezioni funzionali:

![Interfaccia completa](images/07_scheda_individui/04_interfaccia_completa.png)

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | DB Info | Stato record, ordinamento, contatore |
| 3 | Campi Identificativi | Sito, Area, US, Nr. Individuo |
| 4 | Collegamento Struttura | Sigla e numero struttura |
| 5 | Area Tab | Tab tematici per dati specifici |

---

## Toolbar DBMS

La toolbar principale fornisce gli strumenti per la gestione dei record.

![Toolbar DBMS](images/07_scheda_individui/05_toolbar_dbms.png)

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
| ![New](../../resources/icons/newrec.png) | New record | Crea un nuovo record individuo |
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
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Esporta in PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Apri cartella export |

---

## Campi Identificativi

I campi identificativi definiscono univocamente l'individuo nel database.

![Campi identificativi](images/07_scheda_individui/06_campi_identificativi.png)

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Seleziona il sito archeologico di appartenenza.

### Area

**Campo**: `comboBox_area`
**Database**: `area`

Area di scavo all'interno del sito. I valori sono popolati dal thesaurus.

### US

**Campo**: `comboBox_us`
**Database**: `us`

Unita Stratigrafica di riferimento.

### Numero Individuo

**Campo**: `lineEdit_individuo`
**Database**: `nr_individuo`

Numero progressivo dell'individuo. Viene proposto automaticamente il prossimo numero disponibile.

**Note:**
- La combinazione Sito + Area + US + Nr. Individuo deve essere univoca
- Il numero viene assegnato automaticamente alla creazione

### Collegamento Struttura

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Sigla struttura | `sigla_struttura` | Sigla della struttura (es. TM) |
| Nr struttura | `nr_struttura` | Numero della struttura |

Questi campi collegano l'individuo alla struttura funeraria.

---

## Dati di Schedatura

![Dati schedatura](images/07_scheda_individui/07_dati_schedatura.png)

### Data Schedatura

**Campo**: `dateEdit_schedatura`
**Database**: `data_schedatura`

Data di compilazione della scheda.

### Schedatore

**Campo**: `comboBox_schedatore`
**Database**: `schedatore`

Nome dell'operatore che compila la scheda.

---

## Tab Dati Descrittivi

Il primo tab contiene i dati antropologici fondamentali.

![Tab Dati Descrittivi](images/07_scheda_individui/08_tab_descrittivi.png)

### Stima del Sesso

**Campo**: `comboBox_sesso`
**Database**: `sesso`

Stima del sesso biologico basata su caratteri morfologici.

**Valori:**
| Valore | Descrizione |
|--------|-------------|
| Maschio | Caratteri maschili evidenti |
| Femmina | Caratteri femminili evidenti |
| Maschio probabile | Prevalenza caratteri maschili |
| Femmina probabile | Prevalenza caratteri femminili |
| Indeterminato | Non determinabile |

**Criteri di determinazione:**
- Morfologia del bacino
- Morfologia del cranio
- Robustezza generale dello scheletro
- Dimensioni delle ossa

### Stima dell'Eta alla Morte

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Eta minima | `eta_min` | Limite inferiore della stima |
| Eta massima | `eta_max` | Limite superiore della stima |

**Metodi di stima:**
- Sinfisi pubica
- Superficie auricolare
- Suture craniche
- Sviluppo dentario (per subadulti)
- Epifisi ossee (per subadulti)

### Classi di Eta

**Campo**: `comboBox_classi_eta`
**Database**: `classi_eta`

Classificazione per fasce d'eta.

**Valori tipici:**
| Classe | Eta approssimativa |
|--------|-------------------|
| Infans I | 0-6 anni |
| Infans II | 7-12 anni |
| Juvenis | 13-20 anni |
| Adultus | 21-40 anni |
| Maturus | 41-60 anni |
| Senilis | >60 anni |

### Osservazioni

**Campo**: `textEdit_osservazioni`
**Database**: `osservazioni`

Campo testuale per note antropologiche specifiche.

**Contenuti consigliati:**
- Patologie osservate
- Traumi
- Marcatori occupazionali
- Anomalie scheletriche
- Note sulla determinazione del sesso e dell'eta

---

## Tab Orientamento e Posizione

Questo tab documenta la posizione e l'orientamento del corpo.

![Tab Orientamento](images/07_scheda_individui/09_tab_orientamento.png)

### Stato di Conservazione

| Campo | Database | Valori |
|-------|----------|--------|
| Completo | `completo_si_no` | Si / No |
| Disturbato | `disturbato_si_no` | Si / No |
| In connessione | `in_connessione_si_no` | Si / No |

**Definizioni:**
- **Completo**: tutti i distretti anatomici sono rappresentati
- **Disturbato**: evidenze di rimaneggiamento post-deposizionale
- **In connessione**: le articolazioni sono preservate

### Lunghezza Scheletro

**Campo**: `lineEdit_lunghezza`
**Database**: `lunghezza_scheletro`

Lunghezza misurata dello scheletro in situ (in cm o m).

### Posizione dello Scheletro

**Campo**: `comboBox_posizione_scheletro`
**Database**: `posizione_scheletro`

Posizione generale del corpo.

**Valori:**
- Supino (sulla schiena)
- Prono (a faccia in giu)
- Laterale destro
- Laterale sinistro
- Rannicchiato
- Irregolare

### Posizione del Cranio

**Campo**: `comboBox_posizione_cranio`
**Database**: `posizione_cranio`

Orientamento della testa.

**Valori:**
- Rivolto a destra
- Rivolto a sinistra
- Rivolto in alto
- Rivolto in basso
- Non determinabile

### Posizione Arti Superiori

**Campo**: `comboBox_arti_superiori`
**Database**: `posizione_arti_superiori`

Posizione delle braccia.

**Valori:**
- Distesi lungo i fianchi
- Sul bacino
- Sul torace
- Incrociati sul torace
- Misti
- Non determinabile

### Posizione Arti Inferiori

**Campo**: `comboBox_arti_inferiori`
**Database**: `posizione_arti_inferiori`

Posizione delle gambe.

**Valori:**
- Distesi
- Flessi
- Incrociati
- Divaricati
- Non determinabile

### Orientamento Asse

**Campo**: `comboBox_orientamento_asse`
**Database**: `orientamento_asse`

Orientamento dell'asse longitudinale del corpo.

**Valori:**
- N-S (testa a Nord)
- S-N (testa a Sud)
- E-W (testa a Est)
- W-E (testa a Ovest)
- NE-SW, NW-SE, etc.

### Orientamento Azimut

**Campo**: `lineEdit_azimut`
**Database**: `orientamento_azimut`

Valore numerico dell'azimut in gradi (0-360).

---

## Tab Resti Osteologici

Questo tab e dedicato alla documentazione dei distretti anatomici.

![Tab Resti Osteologici](images/07_scheda_individui/10_tab_osteologici.png)

### Documentazione dei Distretti

Permette di registrare:
- Presenza/assenza dei singoli elementi ossei
- Stato di conservazione per distretto
- Lato (destro/sinistro) per elementi pari

**Distretti principali:**
| Distretto | Elementi |
|-----------|----------|
| Cranio | Calvaria, mandibola, denti |
| Rachide | Vertebre cervicali, toraciche, lombari, sacro |
| Torace | Costole, sterno |
| Arti superiori | Clavicole, scapole, omeri, radio, ulna, mani |
| Bacino | Coxali |
| Arti inferiori | Femori, tibia, perone, piedi |

---

## Tab Altre Caratteristiche

Questo tab contiene informazioni aggiuntive.

![Tab Altre Caratteristiche](images/07_scheda_individui/11_tab_altre.png)

### Contenuti

- Caratteristiche metriche specifiche
- Indici antropometrici
- Patologie dettagliate
- Relazioni con altri individui

---

## Export e Stampa

### Export PDF

Il pulsante PDF apre un pannello con opzioni:

| Opzione | Descrizione |
|---------|-------------|
| Elenco Individui | Lista sintetica |
| Schede Individui | Schede complete dettagliate |
| Stampa | Genera il PDF |

### Contenuto Scheda PDF

La scheda PDF include:
- Dati identificativi
- Dati antropologici (sesso, eta)
- Posizione e orientamento
- Stato di conservazione
- Osservazioni

---

## Workflow Operativo

### Creazione Nuovo Individuo

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"
   - Il numero individuo viene proposto automaticamente

3. **Dati identificativi**
   ```
   Sito: Necropoli di Isola Sacra
   Area: 1
   US: 150
   Nr. Individuo: 1
   Sigla struttura: TM
   Nr struttura: 45
   ```

4. **Dati schedatura**
   ```
   Data: 15/03/2024
   Schedatore: M. Rossi
   ```

5. **Dati antropologici** (Tab 1)
   ```
   Sesso: Maschio
   Eta min: 35
   Eta max: 45
   Classe eta: Adultus

   Osservazioni: Statura stimata 170 cm.
   Artrosi lombare. Carie multiple.
   ```

6. **Orientamento e Posizione** (Tab 2)
   ```
   Completo: Si
   Disturbato: No
   In connessione: Si
   Lunghezza: 165 cm
   Posizione: Supino
   Cranio: Rivolto a destra
   Arti superiori: Distesi lungo i fianchi
   Arti inferiori: Distesi
   Orientamento: E-W
   Azimut: 90
   ```

7. **Resti osteologici** (Tab 3)
   - Documentare i distretti presenti

8. **Salvataggio**
   - Click su "Save"

### Ricerca Individui

1. Click su "New Search"
2. Compilare criteri:
   - Sito
   - Sesso
   - Classe eta
   - Posizione
3. Click su "Search"
4. Navigare tra i risultati

---

## Relazioni con Altre Schede

| Scheda | Relazione |
|--------|-----------|
| **Scheda Sito** | Il sito contiene gli individui |
| **Scheda Struttura** | La struttura contiene l'individuo |
| **Scheda Tomba** | La tomba documenta il contesto |
| **Archeozoologia** | Per analisi osteologiche specifiche |

### Flusso di Lavoro Consigliato

1. Creare la **Scheda Struttura** per la tomba
2. Creare la **Scheda Tomba**
3. Creare la **Scheda Individui** per ogni scheletro
4. Collegare individuo alla tomba e struttura

---

## Best Practices

### Determinazione del Sesso

- Utilizzare piu indicatori morfologici
- Indicare il grado di affidabilita
- Specificare i criteri utilizzati nelle osservazioni

### Stima dell'Eta

- Fornire sempre un range (min-max)
- Indicare i metodi utilizzati
- Per subadulti, specificare sviluppo dentario ed epifisario

### Posizione e Orientamento

- Documentare con foto prima del prelievo
- Usare riferimenti cardinali
- Misurare l'azimut con bussola

### Conservazione

- Distinguere perdite tafonomiche da asportazioni antiche
- Documentare le perturbazioni post-deposizionali
- Registrare condizioni di recupero

---

## Troubleshooting

### Problema: Numero individuo duplicato

**Causa**: Esiste gia un individuo con lo stesso numero.

**Soluzione**:
1. Verificare la numerazione esistente
2. Usare il numero proposto automaticamente
3. Controllare area e US

### Problema: Struttura non trovata

**Causa**: La struttura non esiste o ha sigla diversa.

**Soluzione**:
1. Verificare l'esistenza della Scheda Struttura
2. Controllare sigla e numero
3. Creare prima la struttura se necessario

### Problema: Classi eta non disponibili

**Causa**: Thesaurus non configurato.

**Soluzione**:
1. Verificare la configurazione del thesaurus
2. Controllare la lingua impostata
3. Contattare l'amministratore

---

## Riferimenti

### Database

- **Tabella**: `individui_table`
- **Classe mapper**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### File Sorgente

- **UI**: `gui/ui/Schedaind.ui`
- **Controller**: `tabs/Schedaind.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Video Tutorial

### Panoramica Scheda Individui
**Durata**: 5-6 minuti
- Presentazione dell'interfaccia
- Campi principali
- Navigazione tra i tab

[Placeholder video: video_panoramica_individui.mp4]

### Schedatura Antropologica Completa
**Durata**: 12-15 minuti
- Creazione nuovo record
- Determinazione sesso ed eta
- Documentazione posizione
- Registrazione resti osteologici

[Placeholder video: video_schedatura_individui.mp4]

### Collegamento Tomba-Individuo
**Durata**: 5-6 minuti
- Relazione tra schede
- Flusso di lavoro corretto
- Best practices

[Placeholder video: video_collegamento_tomba_individuo.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
