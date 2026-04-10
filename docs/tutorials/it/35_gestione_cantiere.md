# PyArchInit - Gestione Cantiere

## Indice
1. [Introduzione](#introduzione)
2. [Accesso al modulo](#accesso-al-modulo)
3. [Dashboard Cantiere](#dashboard-cantiere)
4. [Personale](#personale)
5. [Presenze](#presenze)
6. [Attrezzature](#attrezzature)
7. [Budget](#budget)
8. [Computo Metrico e Calcolo DEM](#computo-metrico-e-calcolo-dem)
9. [Visualizzazione 2D e 3D del Computo Metrico](#visualizzazione-2d-e-3d-del-computo-metrico)
10. [Esportazione PDF e CSV del Cruscotto](#esportazione-pdf-e-csv-del-cruscotto)
11. [Flusso di lavoro consigliato](#flusso-di-lavoro-consigliato)
12. [Risoluzione dei problemi](#risoluzione-dei-problemi)
13. [Domande Frequenti](#domande-frequenti)

---

## Introduzione

Il modulo **Gestione Cantiere** e un insieme di strumenti introdotti a partire dalla versione **5.1** di PyArchInit per la gestione operativa e amministrativa di un cantiere di scavo archeologico. Il modulo consente di monitorare in tempo reale budget, personale, presenze, attrezzature e calcoli volumetrici (computo metrico) direttamente all'interno dell'ambiente QGIS.

Tradizionalmente queste informazioni vengono gestite con fogli di calcolo esterni e strumenti separati. Con il modulo Gestione Cantiere, tutto e centralizzato nel database di PyArchInit (PostgreSQL o SQLite), garantendo coerenza, tracciabilita e integrazione diretta con i dati di scavo.

<!-- VIDEO: Introduzione al modulo Gestione Cantiere -->
> **Video Tutorial**: [Inserire link video introduzione Gestione Cantiere]

### Componenti del modulo

Il modulo e composto da cinque sotto-moduli, ciascuno con una propria finestra:

| Sotto-modulo | Descrizione |
|--------------|-------------|
| **Dashboard Cantiere** | Pannello riepilogativo centrale con grafici e indicatori |
| **Personale** | Anagrafica del personale impiegato nello scavo |
| **Presenze** | Registro giornaliero di presenze, ferie, malattie e ore lavorate |
| **Attrezzature** | Inventario delle attrezzature con stato e manutenzioni |
| **Budget** | Gestione del budget per categorie e voci di spesa |

---

## Accesso al modulo

Il modulo Gestione Cantiere e accessibile dalla **barra degli strumenti dedicata** di PyArchInit.

### Dalla barra degli strumenti

Nella barra degli strumenti di PyArchInit e presente un gruppo di **5 icone** dedicate alla Gestione Cantiere:

1. **Dashboard** -- Apre il pannello riepilogativo del cantiere
2. **Personale** -- Apre la scheda CRUD per la gestione del personale
3. **Presenze** -- Apre la scheda CRUD per la registrazione delle presenze
4. **Attrezzature** -- Apre la scheda CRUD per la gestione delle attrezzature
5. **Budget** -- Apre la scheda CRUD per la gestione del budget

<!-- IMAGE: Barra degli strumenti Gestione Cantiere con le 5 icone -->
> **Fig. 1**: Le cinque icone del modulo Gestione Cantiere nella barra degli strumenti di PyArchInit

<!-- IMAGE: Menu di accesso al modulo Gestione Cantiere -->
> **Fig. 2**: Accesso al modulo Gestione Cantiere dal menu principale

---

## Dashboard Cantiere

La **Dashboard Cantiere** (controller: `Cantiere.py`) e il pannello di controllo centrale del modulo. Offre una panoramica immediata dello stato del cantiere attraverso riepiloghi numerici, grafici e tabelle.

### Selezione Sito e Anno

Nella parte superiore della dashboard sono presenti due selettori:

| Controllo | Widget | Funzionamento |
|-----------|--------|---------------|
| **Sito** | `comboBox_sito` | Elenco dei siti presenti nel database. Se nelle impostazioni di PyArchInit e configurato un sito predefinito, questo viene selezionato automaticamente all'apertura |
| **Anno** | `comboBox_anno` | Anno di riferimento per i dati visualizzati nella dashboard |

Modificando il sito o l'anno, tutti i riepiloghi e i grafici della dashboard vengono aggiornati automaticamente.

<!-- IMAGE: Selettori sito e anno nella dashboard -->
> **Fig. 3**: I selettori del sito e dell'anno nella parte superiore della Dashboard Cantiere

### Riepilogo Budget

La sezione budget della dashboard mostra:

- **Importo totale previsto**: La somma di tutti gli importi previsti per il sito e l'anno selezionati
- **Importo totale effettivo**: La somma di tutti gli importi effettivamente spesi
- **Barra di progresso**: Indicatore visivo della percentuale di budget consumato rispetto al previsto
- **Grafico a torta**: Distribuzione della spesa effettiva per categoria di budget

La barra di progresso cambia colore in base alla percentuale:

| Percentuale | Colore | Significato |
|-------------|--------|-------------|
| 0% -- 70% | Verde | Spesa nella norma |
| 70% -- 90% | Giallo | Attenzione, ci si avvicina al limite |
| 90% -- 100% | Rosso | Budget quasi esaurito o superato |

<!-- IMAGE: Sezione budget della dashboard con barra di progresso e grafico a torta -->
> **Fig. 4**: Riepilogo budget con barra di progresso e grafico a torta della distribuzione per categorie

### Riepilogo Personale

La sezione personale mostra le statistiche aggiornate alla giornata corrente:

| Indicatore | Descrizione |
|------------|-------------|
| **Presenti oggi** | Numero di persone con tipo_giornata = "lavorativa" per la data odierna |
| **In ferie** | Numero di persone con tipo_giornata = "ferie" |
| **In malattia** | Numero di persone con tipo_giornata = "malattia" |
| **Ore mensili totali** | Somma delle ore ordinarie e straordinarie del mese corrente |
| **Costo mensile** | Somma dei costi giornalieri per il mese corrente |

<!-- IMAGE: Sezione personale della dashboard con indicatori -->
> **Fig. 5**: Riepilogo del personale nella Dashboard Cantiere

### Riepilogo Attrezzature

La sezione attrezzature mostra una panoramica dello stato dell'inventario:

| Indicatore | Descrizione |
|------------|-------------|
| **Totale attrezzature** | Numero complessivo di attrezzature registrate per il sito |
| **In uso** | Attrezzature con stato = "in_uso" |
| **In manutenzione** | Attrezzature con stato = "manutenzione" |
| **Fuori uso** | Attrezzature con stato = "fuori_uso" |
| **Manutenzioni scadute** | Attrezzature la cui data_prossima_manutenzione e precedente alla data odierna |

Le **manutenzioni scadute** vengono evidenziate con un'icona di allerta per richiamare l'attenzione dell'operatore.

<!-- IMAGE: Sezione attrezzature della dashboard con alert manutenzione -->
> **Fig. 6**: Riepilogo delle attrezzature con evidenziazione delle manutenzioni scadute

### Computo Metrico (Quantity Surveying)

La sezione computo metrico nella dashboard consente di eseguire calcoli volumetrici direttamente dai dati GIS. Sono disponibili due modalita di calcolo:

1. **Differenza DEM**: Calcola la differenza volumetrica tra due modelli digitali del terreno (DEM) -- utile per quantificare il volume di terra rimossa tra due campagne di scavo
2. **DEM + Poligono**: Calcola il volume all'interno di un poligono specificato rispetto a un DEM di riferimento -- utile per stimare il volume di uno specifico settore di scavo

I risultati dei calcoli vengono **salvati automaticamente nel database** e visualizzati nella **tabella storico computi** in basso nella dashboard.

A partire dalla versione 5.1, accanto al pulsante **Calcola** sono disponibili anche i pulsanti **Mostra 2D**, **Mostra 3D** e **Crea mesh 3D** per visualizzare il risultato del computo direttamente sulla mappa e in una vista tridimensionale interattiva. Per i dettagli vedi la sezione [Visualizzazione 2D e 3D del Computo Metrico](#visualizzazione-2d-e-3d-del-computo-metrico).

<!-- IMAGE: Sezione computo metrico con i pulsanti di calcolo e visualizzazione 2D/3D -->
> **Fig. 7**: Sezione Computo Metrico della dashboard con le opzioni di calcolo DEM e i nuovi pulsanti di visualizzazione 2D / 3D

### Tabella Storico Computi

Nella parte inferiore della dashboard e presente una tabella che elenca tutti i calcoli di computo metrico eseguiti nel tempo per il sito selezionato. Per ogni calcolo vengono mostrati:

- Data e ora del calcolo
- Tipo di calcolo (differenza DEM / DEM + poligono)
- Volume calcolato
- Note aggiuntive

Questa tabella consente di tenere traccia dell'evoluzione volumetrica dello scavo nel tempo.

<!-- IMAGE: Tabella storico dei computi metrici -->
> **Fig. 8**: Tabella con lo storico dei calcoli di computo metrico

### Nuovo layout a schede della Dashboard Cantiere

A partire dalla versione corrente, la finestra **Cruscotto Cantiere** e stata riorganizzata in **tre schede** per fare spazio al nuovo pannello di **Analisi dei Costi** senza appesantire la vista. L'intestazione con **Sito**, **Anno** e il pulsante **Aggiorna** rimane visibile sopra le schede, in modo da poter cambiare sito o anno in qualsiasi momento: tutte le schede vengono aggiornate automaticamente.

| Scheda | Contenuto |
|--------|-----------|
| **Riepilogo** | E la vista mostrata all'apertura della dashboard. In alto, a tutta larghezza, il **Riepilogo Budget** (barra di progresso e grafico a torta); sotto, affiancati, i riepiloghi **Personale** e **Attrezzature** |
| **Computo Metrico** | Raccoglie tutto il flusso di calcolo DEM: combo **DEM Pre**, **DEM Post** e **Poligono**, radio **Differenza DEM** / **DEM su Poligono**, pulsante **Calcola**, etichette di **area** e **volume**, il nuovo gruppo **Analisi dei Costi** (EUR/m3, m3/giorno -> costo totale, giorni stimati, costo giornaliero), pulsante **Salva Record**, pulsanti **Mostra 2D** / **Mostra 3D** / **Esporta 2DM + 3D** e la **tabella storico** dei computi in basso |
| **Esportazione** | I pulsanti di **esportazione PDF** e **CSV** dei dati del cruscotto, accompagnati da una breve descrizione |

<!-- IMAGE: Nuovo layout a schede del Cruscotto Cantiere (Riepilogo / Computo Metrico / Esportazione) -->
> **Fig. 8a**: Il nuovo layout a schede della Dashboard Cantiere con l'intestazione Sito / Anno / Aggiorna sempre visibile

**Fix**: i DEM non spariscono piu quando si preme **Calcola** (regressione della 5.0.13-alpha in cui l'auto-refresh dei combo resettava la selezione corrente).

---

## Personale

La scheda **Personale** (controller: `Personale.py`) consente la gestione dell'anagrafica del personale impiegato nel cantiere di scavo. Come tutte le schede CRUD di PyArchInit, dispone della toolbar DBMS standard per la navigazione e la gestione dei record.

### Campi della scheda

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|:------------:|
| **Sito** | Testo | Sito di riferimento | Si |
| **Nome** | Testo | Nome del membro del personale | Si |
| **Cognome** | Testo | Cognome del membro del personale | Si |
| **Qualifica** | Testo | Qualifica professionale (es. archeologo, operaio, restauratore) | No |
| **Ruolo** | Testo | Ruolo nel cantiere (es. direttore, responsabile settore, scavatore) | No |
| **Data assunzione** | Data | Data di inizio attivita nel cantiere | No |
| **Data fine** | Data | Data di fine attivita nel cantiere | No |
| **Costo giornaliero** | Numerico | Costo giornaliero in euro | No |
| **Note** | Testo lungo | Annotazioni libere | No |

### Operazioni principali

- **Inserimento**: Compilare i campi e fare clic su **Salva** (icona dischetto) nella toolbar DBMS
- **Modifica**: Navigare al record desiderato, modificare i campi e fare clic su **Aggiorna**
- **Eliminazione**: Navigare al record e fare clic su **Elimina** -- verra chiesta conferma
- **Ricerca**: Compilare uno o piu campi e fare clic su **Cerca** per filtrare i record

<!-- IMAGE: Scheda Personale con i campi compilati -->
> **Fig. 9**: La scheda Personale con un esempio di record compilato

<!-- IMAGE: Toolbar DBMS della scheda Personale -->
> **Fig. 10**: Toolbar DBMS per la navigazione e gestione dei record del personale

---

## Presenze

La scheda **Presenze** (controller: `Presenze.py`) gestisce il registro giornaliero delle presenze del personale. E collegata alla scheda Personale tramite il campo `id_personale`.

### Campi della scheda

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|:------------:|
| **Sito** | Testo | Sito di riferimento | Si |
| **ID Personale** | Numerico | Identificativo del membro del personale (collegamento alla scheda Personale) | Si |
| **Data** | Data | Data della presenza | Si |
| **Tipo giornata** | Selezione | Tipo di giornata registrata | Si |
| **Ore ordinarie** | Numerico | Ore di lavoro ordinario | No |
| **Ore straordinario** | Numerico | Ore di lavoro straordinario | No |
| **Costo giornata** | Numerico | Costo calcolato per la giornata in euro | No |
| **Note** | Testo lungo | Annotazioni libere | No |

### Tipi di giornata

Il campo **Tipo giornata** supporta i seguenti valori:

| Valore | Descrizione |
|--------|-------------|
| **lavorativa** | Giornata di lavoro regolare |
| **ferie** | Giorno di ferie |
| **malattia** | Assenza per malattia |
| **permesso** | Assenza per permesso |

### Suggerimenti operativi

- Registrare le presenze **quotidianamente** per mantenere aggiornata la dashboard
- Il campo **Costo giornata** puo essere compilato manualmente oppure calcolato a partire dal costo giornaliero definito nella scheda Personale
- E possibile cercare tutte le presenze di un singolo membro del personale inserendo il suo ID nel campo di ricerca

<!-- IMAGE: Scheda Presenze con un esempio di registrazione -->
> **Fig. 11**: La scheda Presenze con un esempio di registrazione giornaliera

---

## Attrezzature

La scheda **Attrezzature** (controller: `Attrezzature.py`) consente di gestire l'inventario delle attrezzature presenti in cantiere, monitorandone lo stato e le scadenze di manutenzione.

### Campi della scheda

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|:------------:|
| **Sito** | Testo | Sito di riferimento | Si |
| **Nome** | Testo | Nome o denominazione dell'attrezzatura | Si |
| **Tipo** | Testo | Tipologia (es. strumento topografico, macchina movimento terra, utensile manuale) | No |
| **Marca** | Testo | Marca del produttore | No |
| **Modello** | Testo | Modello specifico | No |
| **Stato** | Selezione | Stato operativo corrente | Si |
| **Data acquisto** | Data | Data di acquisto dell'attrezzatura | No |
| **Costo acquisto** | Numerico | Costo di acquisto in euro | No |
| **Data ultima manutenzione** | Data | Data dell'ultima manutenzione effettuata | No |
| **Data prossima manutenzione** | Data | Data prevista per la prossima manutenzione | No |
| **Note** | Testo lungo | Annotazioni libere | No |

### Valori dello stato

| Valore | Descrizione |
|--------|-------------|
| **in_uso** | L'attrezzatura e operativa e attualmente in uso |
| **manutenzione** | L'attrezzatura e in fase di manutenzione o riparazione |
| **fuori_uso** | L'attrezzatura e dismessa o non piu utilizzabile |

### Gestione delle manutenzioni

Il campo **Data prossima manutenzione** e particolarmente importante: la dashboard confronta questa data con la data odierna e segnala le manutenzioni scadute. Si consiglia di:

1. Compilare sempre la data di prossima manutenzione al momento dell'inserimento o dopo ogni manutenzione effettuata
2. Consultare regolarmente la dashboard per verificare eventuali alert
3. Dopo aver effettuato la manutenzione, aggiornare sia la data di ultima manutenzione sia quella di prossima manutenzione

<!-- IMAGE: Scheda Attrezzature con i campi compilati -->
> **Fig. 12**: La scheda Attrezzature con un esempio di attrezzatura registrata

---

## Budget

La scheda **Budget** (controller: `Budget.py`) consente di pianificare e monitorare il budget del cantiere, organizzato per anno, categorie e voci di spesa.

### Campi della scheda

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|:------------:|
| **Sito** | Testo | Sito di riferimento | Si |
| **Anno** | Numerico | Anno di riferimento del budget | Si |
| **Categoria** | Testo | Categoria di spesa (es. personale, attrezzature, trasporti, materiali di consumo) | Si |
| **Voce di spesa** | Testo | Descrizione specifica della voce (es. noleggio escavatore, acquisto teli, diaria personale) | Si |
| **Importo previsto** | Numerico | Importo previsto in euro per la voce di spesa | No |
| **Importo effettivo** | Numerico | Importo effettivamente speso in euro | No |
| **Note** | Testo lungo | Annotazioni libere | No |

### Suggerimenti per la compilazione

- Creare le voci di budget **all'inizio della campagna di scavo** con l'importo previsto
- Aggiornare l'**importo effettivo** man mano che le spese vengono sostenute
- Utilizzare categorie coerenti per ottenere un grafico a torta leggibile nella dashboard
- E possibile avere piu voci di spesa per la stessa categoria

### Esempio di struttura del budget

| Categoria | Voce di spesa | Importo previsto | Importo effettivo |
|-----------|---------------|:----------------:|:-----------------:|
| Personale | Diaria archeologi | 15.000,00 | 12.350,00 |
| Personale | Diaria operai | 8.000,00 | 7.200,00 |
| Attrezzature | Noleggio stazione totale | 3.000,00 | 3.000,00 |
| Attrezzature | Acquisto teli di copertura | 500,00 | 480,00 |
| Trasporti | Carburante | 2.000,00 | 1.800,00 |
| Materiali | Sacchetti, etichette, schede | 300,00 | 250,00 |

<!-- IMAGE: Scheda Budget con voci di spesa compilate -->
> **Fig. 13**: La scheda Budget con un esempio di voci di spesa

---

## Computo Metrico e Calcolo DEM

Il modulo Gestione Cantiere integra strumenti di **Quantity Surveying** (computo metrico) basati sull'analisi di modelli digitali del terreno (DEM). Questa funzionalita e accessibile direttamente dalla Dashboard Cantiere.

### Differenza DEM

Il calcolo della **differenza DEM** confronta due raster DEM (ad esempio, il DEM prima e dopo una campagna di scavo) per quantificare il volume di terra rimossa o aggiunta.

#### Procedura

1. Aprire la **Dashboard Cantiere**
2. Nella sezione **Computo Metrico**, selezionare la modalita **Differenza DEM**
3. Selezionare il **DEM iniziale** (stato precedente del terreno)
4. Selezionare il **DEM finale** (stato attuale del terreno)
5. Fare clic su **Calcola**
6. Il risultato (volume in metri cubi) viene visualizzato e salvato automaticamente nel database
7. Il calcolo appare nella **tabella storico computi**

### DEM + Poligono

Il calcolo **DEM + Poligono** calcola il volume di terreno all'interno di un'area poligonale definita dall'utente, rispetto a un piano di riferimento derivato dal DEM.

#### Procedura

1. Aprire la **Dashboard Cantiere**
2. Nella sezione **Computo Metrico**, selezionare la modalita **DEM + Poligono**
3. Selezionare il **DEM di riferimento**
4. Selezionare il **layer poligonale** che delimita l'area di interesse
5. Fare clic su **Calcola**
6. Il risultato viene visualizzato e salvato nel database
7. Il calcolo appare nella **tabella storico computi**

### Applicazioni pratiche

- **Stima dei volumi di scavo**: Confrontando i DEM tra campagne successive si ottiene il volume totale scavato
- **Pianificazione della rimozione terra**: Stimare il volume residuo da scavare in un settore specifico
- **Documentazione progressiva**: Lo storico dei calcoli fornisce una registrazione cronologica dell'avanzamento dei lavori

<!-- IMAGE: Risultato di un calcolo di differenza DEM nella dashboard -->
> **Fig. 14**: Esempio di risultato di un calcolo di differenza DEM con il volume calcolato

---

## Visualizzazione 2D e 3D del Computo Metrico

A partire dalla versione 5.1, dopo aver premuto il pulsante **Calcola** nel pannello Computo Metrico, il Cruscotto Cantiere non si limita piu a mostrare i valori numerici (area e volume), ma crea automaticamente una serie di layer cartografici e rende disponibile una vista 3D interattiva.

### Cosa succede quando premi "Calcola"

Al termine del calcolo della differenza DEM, il Cruscotto esegue automaticamente le seguenti operazioni:

1. **Salvataggio permanente del raster di differenza**: il raster risultante (DEM post - DEM pre) viene salvato in modo permanente nella cartella `<PYARCHINIT_HOME>/site_dashboard/<nome sito>/` come file GeoTIFF. In questo modo il raster non viene perso alla chiusura di QGIS e puo essere riutilizzato in qualsiasi momento.
2. **Aggiunta al progetto QGIS**: il raster viene aggiunto al pannello layer dentro un gruppo dedicato chiamato **"Cruscotto Cantiere - Computi"**, per tenere ordinati tutti i calcoli eseguiti.
3. **Stile automatico**: al raster viene applicata una **rampa di colori divergente**:
   - **Rosso** per le zone di scavo (valori negativi, terreno rimosso)
   - **Blu** per le zone di riporto (valori positivi, terreno aggiunto)
   - **Trasparente / neutro** per le zone con variazione trascurabile (|diff| <= 1 cm)
4. **Poligonizzazione dell'area di intervento**: le celle raster in cui la variazione di quota supera 1 cm vengono poligonalizzate in un layer vettoriale di tipo poligono, aggiunto anch'esso al gruppo "Cruscotto Cantiere - Computi" con uno stile evidenziato, per mostrare a colpo d'occhio l'estensione complessiva dell'intervento.
5. **Zoom automatico**: la vista principale della mappa di QGIS viene inquadrata automaticamente sull'estensione del calcolo.

### Prerequisiti

Per poter utilizzare le nuove visualizzazioni 2D / 3D del Computo Metrico e necessario:

- Avere **due layer raster DEM** caricati nel progetto QGIS (tipicamente un DEM **pre**-scavo e un DEM **post**-scavo)
- Selezionarli correttamente nei combobox **DEM Pre** e **DEM Post** della sezione Computo Metrico
- Il sistema di riferimento (CRS) dei due raster deve essere coerente

### Nuovi pulsanti

Accanto al pulsante **Calcola** sono ora disponibili tre nuovi pulsanti:

| Pulsante | Descrizione |
|----------|-------------|
| **Mostra 2D** | Ricentra la mappa di QGIS sull'estensione dell'ultimo calcolo eseguito. Utile dopo aver lavorato su altre aree per tornare rapidamente al Computo Metrico attivo. |
| **Mostra 3D** | Apre una finestra di dialogo 3D interattiva che utilizza il DEM pre come terreno, con il raster di differenza sovrapposto ("drape"). Include: spinbox per l'**esagerazione verticale**, checkbox per attivare / disattivare i singoli layer e pulsante di **reset vista**. |
| **Crea mesh 3D** | Costruisce mesh TIN a partire dai DEM pre e post (tramite gli algoritmi di QGIS Processing). Le mesh possono essere visualizzate all'interno del visualizzatore 3D, permettendo di apprezzare visivamente le due superfici e il volume compreso tra esse. |

<!-- IMAGE: I tre nuovi pulsanti Mostra 2D, Mostra 3D, Crea mesh 3D accanto al pulsante Calcola -->
> **Fig. 15**: I nuovi pulsanti **Mostra 2D**, **Mostra 3D** e **Crea mesh 3D** affiancati al pulsante **Calcola** nel pannello Computo Metrico

<!-- IMAGE: Finestra di dialogo 3D con il DEM pre come terreno e il raster di differenza drappeggiato -->
> **Fig. 16**: La finestra 3D interattiva del Computo Metrico con esagerazione verticale e controllo dei layer

### Flusso di lavoro tipico

1. Caricare nel progetto QGIS i due raster DEM (pre e post scavo)
2. Aprire il **Cruscotto Cantiere**
3. Nella sezione **Computo Metrico**, selezionare i due DEM nei combobox **DEM Pre** e **DEM Post**
4. Premere **Calcola**: il raster di differenza e il poligono di intervento vengono creati automaticamente e la mappa viene inquadrata sull'estensione
5. Leggere i valori numerici (area, volume, scavo, riporto) direttamente nel pannello
6. Premere **Mostra 3D** per aprire la visualizzazione tridimensionale
7. (Opzionale) Premere **Crea mesh 3D** per generare e visualizzare le mesh TIN dei due DEM
8. Salvare il risultato nello storico con **Salva Computo**

### Organizzazione dei file su disco

Tutti i raster e i layer generati vengono salvati in:

```
<PYARCHINIT_HOME>/site_dashboard/<nome sito>/
```

dove `<PYARCHINIT_HOME>` e la cartella di lavoro configurata nelle impostazioni di PyArchInit e `<nome sito>` e il nome del sito selezionato nella dashboard. Questo consente di conservare uno storico fisico dei computi e di riutilizzarli anche in progetti QGIS diversi.

### Aggiornamento: "Mostra 2D" -- Sezione analitica

A partire dalla release successiva, il pulsante **Mostra 2D** del pannello Computo Metrico non si limita piu a ricentrare la mappa sull'ultimo calcolo: apre una finestra di dialogo analitica basata su **matplotlib** che mostra in un colpo d'occhio i risultati dello scavo come sezione archeologica classica.

La finestra e disponibile **solo quando il calcolo e stato eseguito in modalita "Differenza DEM"** (con DEM pre e DEM post). Se hai usato la modalita **DEM + Poligono**, il pulsante si comporta come prima e si limita a fare zoom sull'estensione del calcolo nella mappa di QGIS.

Quando disponibile, la finestra contiene i seguenti pannelli:

| Pannello | Descrizione |
|----------|-------------|
| **Heat-map differenza DEM** | Mappa di calore bidimensionale del raster differenza con rampa colore divergente (scavo / riporto) |
| **Istogramma** | Distribuzione delle profondita di **scavo** e delle altezze di **riporto**, per avere subito la statistica dei volumi movimentati |
| **Sezione longitudinale (E-W)** | La classica sezione archeologica: il **DEM pre** e disegnato in **blu**, il **DEM post** in **rosso** e il volume asportato e **riempito** fra le due linee |
| **Sezione trasversale (N-S)** | Stessa logica della sezione E-W ma lungo la direzione Nord-Sud |
| **Spinbox riga / colonna** | Permettono di scorrere la posizione delle due sezioni sul raster, per esplorare interattivamente tutto lo scavo |
| **Pulsante "Salva PNG"** | Esporta l'intera figura (heat-map, istogramma e due sezioni) come immagine PNG, pronta per essere inclusa nella relazione di scavo |

<!-- IMMAGINE: Finestra analitica di Mostra 2D con heat-map, istogramma e sezioni E-W / N-S -->
> **Fig. 17**: La nuova finestra analitica di **Mostra 2D** con heat-map della differenza DEM, istogramma di scavo / riporto e le due sezioni longitudinale e trasversale (DEM pre in blu, DEM post in rosso, volume asportato riempito fra le due linee)

### Aggiornamento: "Mostra 3D" -- Fallback matplotlib

Il pulsante **Mostra 3D** ora gestisce in automatico due scenari a seconda del tipo di build di QGIS installata:

1. **QGIS con modulo 3D nativo (Qt3D disponibile)**: si apre come prima la finestra `Qgs3DMapCanvas` embedded, con terreno basato sul DEM pre, esagerazione verticale e controllo dei layer.
2. **QGIS senza modulo 3D (errore "QGIS 3D module not available")**: il Cruscotto effettua automaticamente il **fallback a un visualizzatore 3D basato su matplotlib**, che fa parte delle dipendenze gia installate dal plugin, quindi funziona sempre -- anche sui QGIS minimali o compilati senza supporto 3D.

Il visualizzatore di fallback offre:

| Controllo | Descrizione |
|-----------|-------------|
| **Modalita di visualizzazione** | Tre modalita selezionabili: **Pre + Post** (entrambe le superfici sovrapposte), **Differenza** (solo la superficie di scavo / riporto), **Solo Pre** (il DEM pre come superficie di riferimento) |
| **Esagerazione verticale** | Slider per enfatizzare la differenza di quota fra le due superfici, utile quando lo scavo ha spessori ridotti |
| **Rotazione interattiva** | Trascinando con il mouse e possibile ruotare la scena 3D in tempo reale per esplorare lo scavo da qualsiasi angolazione |

<!-- IMMAGINE: Visualizzatore 3D matplotlib di fallback in modalita Pre + Post -->
> **Fig. 18**: Il visualizzatore 3D matplotlib di fallback quando QGIS non dispone del modulo Qt3D: mostra la superficie pre e la superficie post con esagerazione verticale regolabile

### Aggiornamento: "Crea mesh 3D" -- Stile automatico del terreno

Il pulsante **Crea mesh 3D** applica ora in automatico una **rampa di colori tipo terreno** al *dataset group* di elevazione della mesh (`Bed Elevation`). La mesh passa quindi dal colore di default (spesso un grigio piatto, poco leggibile) a una vera e propria mappa di quota:

- **Verde** per le quote piu basse
- **Arancione** per le quote intermedie
- **Marrone** per le quote piu alte

In questo modo la mesh risulta subito visibile e significativa nel canvas di QGIS, anche prima di aprire la vista 3D. Dopo averla costruita, e sufficiente premere **Mostra 3D** per vederla renderizzata come superficie tridimensionale, sia con il modulo 3D nativo di QGIS sia tramite il visualizzatore matplotlib di fallback descritto sopra.

<!-- IMMAGINE: Mesh 3D con la nuova rampa terreno verde / arancione / marrone -->
> **Fig. 19**: La mesh 3D con la nuova rampa colore tipo terreno applicata automaticamente al dataset group di elevazione

### Aggiornamento: poligono come maschera di ritaglio

Se nel pannello Computo Metrico, oltre ai due DEM, si seleziona anche un layer vettoriale nel combobox **Layer Poligono** lasciando attiva la modalita **Differenza DEM**, il poligono viene ora utilizzato come **maschera di ritaglio**: entrambi i DEM vengono ritagliati sul poligono prima del calcolo della differenza, cosi che la sezione analitica 2D, il fallback 3D matplotlib e la mesh TIN lavorino esclusivamente sull'area di intervento. Il flusso tipico e: disegnare un poligono attorno allo scavo, selezionare i DEM pre e post, scegliere il poligono nel combobox **Layer Poligono** e premere **Calcola**. I due raster ritagliati vengono aggiunti automaticamente al gruppo **"Cruscotto Cantiere - Computi"** nel pannello layer, pronti per essere riutilizzati.

### Aggiornamento: "Crea mesh 3D" -- niente piu crash

Le versioni precedenti potevano far crashare QGIS su alcune build a causa di un segfault C++ interno agli algoritmi di Processing usati per costruire la mesh. La generazione e stata riscritta in **Python puro**: il Cruscotto legge il DEM con GDAL e scrive direttamente un file 2DM con una **mesh di quad a griglia regolare**, senza dipendere dagli algoritmi nativi. Il risultato e sicuro su qualunque versione di QGIS. Le mesh con piu di circa **15 000 celle** vengono automaticamente ricampionate per mantenere la costruzione rapida e il file leggero, mentre le celle con valore nodata vengono saltate: se e attiva una maschera poligonale di ritaglio, la mesh segue quindi esattamente la forma dell'area di intervento. Nel raro caso in cui la generazione fallisca per altri motivi (disco pieno, permessi), la finestra di dialogo suggerisce ora di aprire direttamente **Mostra 3D**, che usa il visualizzatore matplotlib di fallback e non richiede alcun layer mesh.

### Aggiornamento: auto-refresh dei combo al click di "Calcola"

Il pannello Computo Metrico ora **aggiorna automaticamente le liste DEM e poligono ogni volta che si clicca "Calcola"**: non e piu necessario chiudere e riaprire il Cruscotto dopo aver caricato un nuovo raster o disegnato un nuovo poligono nel progetto. Basta caricare il layer in QGIS, tornare sul pannello e premere **Calcola** -- i combobox **DEM Pre**, **DEM Post** e **Layer Poligono** vengono ripopolati al volo con lo stato corrente del progetto. L'eventuale diagnostica del clip (successo, CRS non compatibile, intersezione vuota) viene mostrata nella **barra dei messaggi di QGIS**, in modo che sia sempre chiaro quali layer sono stati effettivamente usati nel calcolo.

### Aggiornamento: bottone rinominato "Esporta 2DM + 3D"

Il bottone precedentemente chiamato **Crea mesh 3D** e stato rinominato in **Esporta 2DM + 3D** per riflettere il suo nuovo comportamento: **non** carica piu la mesh come layer nel progetto QGIS (l'API mesh nativa puo crashare su alcune build di QGIS) e si limita a due operazioni sicure e complementari. Scrive su disco i file **2DM** a partire dai DEM pre e post (utili per l'import in software di post-processing esterni) e apre direttamente la **vista 3D matplotlib** sui DEM clippati, cosi da poter valutare subito visivamente il risultato. In questo modo il rischio di crash e completamente eliminato, perche l'API mesh di QGIS non viene mai toccata.

### Aggiornamento: clip del poligono con diagnostica visibile

Quando si seleziona un layer nel combobox **Layer Poligono** insieme ai due DEM, il ritaglio dei raster sul poligono viene ora **tracciato nella barra messaggi di QGIS**: in caso di successo compare l'elenco dei file clippati scritti su disco, mentre in caso di fallimento viene riportato il motivo specifico (ad esempio poligono in un CRS diverso dai DEM, nessuna intersezione geometrica tra poligono e raster, file sorgente non trovato o non leggibile). In questo modo e immediato capire perche un clip non e stato applicato e quali correzioni fare (riproiettare il poligono, spostarlo sopra l'area dei DEM, controllare il percorso del file), senza dover aprire log o console Python.

### Aggiornamento: clip del poligono anche in modalita "DEM su Poligono"

Il clip del poligono funziona ora anche quando si seleziona il radio button **DEM su Poligono** (modalita zonal-stats con un solo DEM): il raster viene ritagliato sull'estensione del poligono **prima** di essere passato ai visualizzatori **Mostra 2D**, **Mostra 3D** ed **Esporta 2DM + 3D**, cosi la sezione e la vista 3D mostrano esclusivamente l'area di intervento anziche l'intero DEM come avveniva prima. Il messaggio di diagnostica del clip compare nella **barra messaggi di QGIS** esattamente come in modalita Differenza DEM. In questo scenario a singolo DEM, il visualizzatore **Mostra 2D** si adatta automaticamente: la heat-map mostra le quote con una rampa **terrain**, l'istogramma rappresenta la distribuzione delle quote con la linea della media, e le due sezioni longitudinale/trasversale tracciano una sola linea di quota (senza il fill tra pre e post, perche il post non esiste).

### Aggiornamento: Analisi Costi del Computo Metrico

Nel pannello Computo Metrico del Cruscotto Cantiere e stato aggiunto un nuovo riquadro **Analisi Costi** con due parametri di input: **Costo unitario** (espresso in euro/m3) e **Produttivita** (espressa in m3/giorno). Ad ogni pressione del pulsante **Calcola**, il pannello aggiorna automaticamente tre valori derivati visibili a colpo d'occhio: **Costo totale** (volume x costo unitario), **Giorni stimati** (volume / produttivita) e **Costo giornaliero** (costo unitario x produttivita). I due input sono salvati automaticamente **per-sito** nelle impostazioni di QGIS (chiavi `pyArchInit/site_dashboard/costs/<sito>/...`), quindi basta inserirli una volta per ciascun cantiere: cambiando sito i valori vengono ricaricati senza doverli reinserire, e i tre totali si ricalcolano in tempo reale ad ogni nuovo computo.

### Aggiornamento: clip allineato pre/post

Il calcolo della differenza DEM richiede che le due DEM (pre e post) siano esattamente allineate sulla stessa griglia di pixel. Nelle versioni precedenti, quando si usava un poligono di clip, le due DEM ritagliate potevano finire su griglie leggermente diverse e il calcolo di `pre - post` risultava errato o vuoto. Ora entrambi i clip usano la **risoluzione nativa della DEM pre** come riferimento (stessa `xRes` / `yRes` e stesso allineamento della griglia), cosi che i due raster clippati siano sempre pixel-perfect e la differenza produca un risultato valido. Anche le trincee minime in cui sono stati tolti solo "10 secchi di terra" (circa 1 m3) vengono ora catturate correttamente dal computo.

### Aggiornamento: nuovo combo "Muri / Strutture"

Nel pannello Computo Metrico e stato aggiunto un secondo combo **Muri / Strutture** che permette di selezionare un layer di poligoni rappresentanti muri, strutture in elevato, pilastri o altre parti costruite che **non devono essere conteggiate** nel calcolo dei metri cubi di scavo. Quando si preme **Calcola**, i poligoni dei muri vengono rasterizzati come NODATA sul raster differenza clippato e le loro celle vengono escluse dal totale di volume; la diagnostica viene mostrata nella barra messaggi di QGIS (per esempio `walls masked: muri_trincea_42`). Il tipico flusso di lavoro archeologico e: caricare DEM pre + DEM post + poligono dell'area di scavo + poligono dei muri rinvenuti, selezionare entrambi nei due combo e premere **Calcola** -- il volume scavato esclude automaticamente il volume delle strutture.

---

## Esportazione PDF e CSV del Cruscotto

Il Cruscotto Cantiere permette di esportare un riepilogo completo dei dati gestionali in due formati: **PDF** (documento impaginato, ideale per la consegna al committente o per l'archiviazione cartacea) e **CSV** (ideale per analisi successive in Excel o altri fogli di calcolo).

### Esportazione PDF

Il pulsante **Esporta PDF** presente nel Cruscotto Cantiere genera un report completo dello stato del cantiere. A partire dalla versione 5.1 il PDF include:

- **Copertina rinnovata** con nome del sito, anno di riferimento e data di generazione
- **Riepilogo Budget** con tabelle dettagliate per categoria e totali (previsto vs effettivo)
- **Riepilogo Personale** con statistiche di presenza, ore lavorate e costi
- **Riepilogo Attrezzature** con lo stato dell'inventario e le manutenzioni scadute
- **Nuova sezione "Computo Metrico"** con:
  - Tabella dettagliata di tutti i calcoli salvati
  - **Totali**: area totale (m2) e volume totale (m3)
  - **Statistiche**: volume di scavo, volume di riporto, area interessata
- **Nuova sezione "Analisi Costi"** (inserita fra **Computo Metrico** e **Statistiche**) con parameter card dei valori impostati (costo unitario in euro/m3 e produttivita in m3/giorno), tabella dettagliata per record (data, tipo, volume, costo, giorni stimati, costo giornaliero) e riga di **totali** a fondo tabella; il blocco **Statistiche** e stato esteso con **costo totale** e **giorni totali** di cantiere
- **Supporto completo per i caratteri speciali**: il rendering dei PDF e stato corretto per tutte le lingue supportate, incluse le lettere accentate del rumeno (**a**, **a**, **i**, **s**, **t**), i caratteri **greci**, **arabi**, **portoghesi** e **catalani**.

### Esportazione CSV

Il pulsante **Esporta CSV** genera un file CSV compatibile con i principali fogli di calcolo. Dalla versione 5.1:

- **Codifica UTF-8 con BOM**: garantisce che Excel (in particolare la versione europea) apra correttamente il file senza corrompere le lettere accentate e i caratteri speciali
- **Separatore `;`** (punto e virgola): compatibile con la localizzazione europea di Excel
- **Sezione COMPUTO METRICO**: include tutti i dati di computo metrico, con tipologia, area, volume e note di ogni calcolo
- **Nuova sezione `=== ANALISI COSTI ===`**: riporta in testa i due parametri (costo unitario in euro/m3 e produttivita in m3/giorno) e di seguito la tabella dettagliata per record (data, tipo, volume, costo, giorni stimati, costo giornaliero), pronta per essere filtrata o aggregata in Excel
- **Blocco SUMMARY finale esteso**: un riepilogo aggregato con totali e statistiche, utile per analisi rapide senza dover creare formule; ora include anche **Totale costo** e **Giorni totali** calcolati a partire dalla nuova Analisi Costi

<!-- IMAGE: Esempio di PDF esportato dal Cruscotto con la nuova sezione Computo Metrico -->
> **Fig. 17**: Esempio di PDF esportato con la nuova sezione **Computo Metrico** contenente tabella, totali e statistiche

<!-- IMAGE: Esempio di CSV esportato aperto in Excel con la sezione COMPUTO METRICO e il blocco SUMMARY -->
> **Fig. 18**: Esempio di CSV esportato aperto in Excel con la sezione **COMPUTO METRICO** e il blocco **SUMMARY** finale

---

## Flusso di lavoro consigliato

Per ottenere il massimo dal modulo Gestione Cantiere, si consiglia il seguente flusso di lavoro:

### Fase iniziale (prima dello scavo)

1. **Configurare il sito** nella scheda Sito di PyArchInit (se non gia presente)
2. **Inserire il personale**: Registrare tutti i membri del team nella scheda Personale con qualifica, ruolo e costo giornaliero
3. **Inserire le attrezzature**: Registrare tutte le attrezzature in dotazione con stato e date di manutenzione
4. **Definire il budget**: Creare tutte le voci di spesa previste per la campagna con gli importi pianificati

### Fase operativa (durante lo scavo)

1. **Registrare le presenze quotidianamente**: Ogni giorno, compilare la scheda Presenze per ciascun membro del personale
2. **Aggiornare il budget**: Man mano che le spese vengono sostenute, aggiornare gli importi effettivi
3. **Aggiornare lo stato delle attrezzature**: Registrare cambi di stato (in_uso, manutenzione, fuori_uso) e manutenzioni effettuate
4. **Consultare la dashboard**: Verificare regolarmente la dashboard per monitorare l'avanzamento del budget e lo stato del cantiere

### Fase di chiusura (fine scavo)

1. **Eseguire i calcoli volumetrici**: Utilizzare il computo metrico per documentare i volumi scavati
2. **Verificare il budget finale**: Controllare la corrispondenza tra importi previsti ed effettivi
3. **Aggiornare le date di fine**: Compilare la data di fine per il personale non piu impiegato

```
Inizio campagna         Durante lo scavo           Fine campagna
 +-----------+          +----------------+         +-----------+
 | Personale |   --->   | Presenze       |   --->  | Computo   |
 | Attrezz.  |          | (quotidiane)   |         | metrico   |
 | Budget    |          | Budget         |         | Budget    |
 | (previsto)|          | (effettivo)    |         | (finale)  |
 +-----------+          +----------------+         +-----------+
                              |
                        Dashboard Cantiere
                        (monitoraggio continuo)
```

---

## Risoluzione dei problemi

### La dashboard non mostra dati

- Verificare che il **sito** e l'**anno** selezionati nei selettori siano corretti
- Controllare che nel database siano presenti record per il sito e l'anno selezionati
- Assicurarsi che la connessione al database sia attiva (controllare la barra di stato di PyArchInit)

### Il grafico a torta del budget e vuoto

- Il grafico viene generato solo se esistono record di budget con **importo effettivo** maggiore di zero per il sito e l'anno selezionati
- Verificare di aver inserito almeno una voce di budget con importo effettivo compilato

### Le manutenzioni scadute non vengono segnalate

- Assicurarsi che il campo **Data prossima manutenzione** sia compilato nelle schede Attrezzature
- L'alert si attiva solo quando la data di prossima manutenzione e **precedente** alla data odierna

### Il calcolo DEM restituisce un errore

- Verificare che i layer DEM selezionati siano **raster validi** e caricati nel progetto QGIS
- Per il calcolo DEM + Poligono, assicurarsi che il layer poligonale sia un **layer vettoriale** con geometria di tipo poligono
- Verificare che i sistemi di riferimento (CRS) dei layer siano coerenti

### Il campo ID Personale nella scheda Presenze non corrisponde

- L'ID Personale nella scheda Presenze deve corrispondere all'identificativo numerico del record nella scheda Personale
- Verificare l'ID corretto consultando la scheda Personale e navigando al record desiderato

---

## Domande Frequenti

### Il modulo Gestione Cantiere funziona sia con PostgreSQL che con SQLite?

**Si.** Come tutti i moduli di PyArchInit, la Gestione Cantiere funziona con entrambi i backend di database supportati. Le tabelle vengono create automaticamente alla prima connessione se non sono ancora presenti.

### Posso gestire piu cantieri contemporaneamente?

**Si.** Ogni record e associato a un sito specifico tramite il campo **Sito**. E possibile gestire cantieri diversi semplicemente selezionando il sito appropriato nei selettori. La dashboard mostra i dati relativi al sito selezionato.

### Il budget della dashboard e collegato ai costi del personale?

La dashboard mostra le informazioni di budget e personale in sezioni separate. Il budget viene calcolato dalla scheda Budget, mentre il costo del personale viene calcolato dalla scheda Presenze (somma dei costi giornalieri). Non esiste un collegamento automatico tra le due sezioni, ma si consiglia di inserire una voce di budget per la categoria "Personale" per confrontare il costo previsto con quello effettivo derivante dalle presenze.

### Come posso esportare i dati di budget o presenze?

I dati sono memorizzati nelle tabelle del database PyArchInit. E possibile esportarli utilizzando gli strumenti standard di esportazione di QGIS o tramite query SQL dirette al database.

### E possibile personalizzare le categorie di budget?

**Si.** Il campo **Categoria** nella scheda Budget e un campo di testo libero. E possibile definire qualsiasi categorizzazione si ritenga opportuna per il proprio cantiere. Si consiglia tuttavia di mantenere una nomenclatura coerente per ottenere grafici leggibili nella dashboard.

### Come funziona la selezione automatica del sito nella dashboard?

Se nelle impostazioni di PyArchInit e configurato un **sito predefinito**, la dashboard lo seleziona automaticamente all'apertura. In caso contrario, viene mostrato il primo sito disponibile nell'elenco. E sempre possibile cambiare sito manualmente tramite il selettore.

### I calcoli del computo metrico vengono persi se chiudo QGIS?

**No.** I risultati dei calcoli vengono salvati nel database di PyArchInit. La tabella storico computi nella dashboard mostra tutti i calcoli eseguiti nel tempo, anche dopo aver chiuso e riaperto QGIS.

### Posso eliminare un calcolo di computo metrico dallo storico?

I calcoli salvati nello storico sono record del database. Al momento non e prevista l'eliminazione diretta dalla dashboard, ma e possibile rimuoverli tramite query SQL al database se necessario.

---

*Documentazione PyArchInit - Gestione Cantiere*
*Versione: 5.1*
*Ultimo aggiornamento: Aprile 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../animations/gestione_cantiere_animation.html)
