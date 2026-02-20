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
9. [Flusso di lavoro consigliato](#flusso-di-lavoro-consigliato)
10. [Risoluzione dei problemi](#risoluzione-dei-problemi)
11. [Domande Frequenti](#domande-frequenti)

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

<!-- IMAGE: Sezione computo metrico con i due pulsanti di calcolo -->
> **Fig. 7**: Sezione Computo Metrico della dashboard con le opzioni di calcolo DEM

### Tabella Storico Computi

Nella parte inferiore della dashboard e presente una tabella che elenca tutti i calcoli di computo metrico eseguiti nel tempo per il sito selezionato. Per ogni calcolo vengono mostrati:

- Data e ora del calcolo
- Tipo di calcolo (differenza DEM / DEM + poligono)
- Volume calcolato
- Note aggiuntive

Questa tabella consente di tenere traccia dell'evoluzione volumetrica dello scavo nel tempo.

<!-- IMAGE: Tabella storico dei computi metrici -->
> **Fig. 8**: Tabella con lo storico dei calcoli di computo metrico

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
*Ultimo aggiornamento: Febbraio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../animations/gestione_cantiere_animation.html)
