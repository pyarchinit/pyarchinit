# PyArchInit - GeoArchaeo - Analisi Geostatistica

## Indice
1. [Introduzione](#introduzione)
2. [Accesso allo strumento](#accesso-allo-strumento)
3. [Interfaccia utente](#interfaccia-utente)
4. [Scheda Dati](#scheda-dati)
5. [Scheda Variogramma](#scheda-variogramma)
6. [Scheda Kriging](#scheda-kriging)
7. [Scheda Machine Learning](#scheda-machine-learning)
8. [Scheda Campionamento](#scheda-campionamento)
9. [Scheda Report](#scheda-report)
10. [Flusso di lavoro operativo](#flusso-di-lavoro-operativo)
11. [Risoluzione dei problemi](#risoluzione-dei-problemi)
12. [Note tecniche](#note-tecniche)

---

## Introduzione

**GeoArchaeo** e il modulo di analisi geostatistica integrato in PyArchInit. Fornisce un insieme completo di strumenti per l'analisi spaziale dei dati archeologici, dalla modellazione dei variogrammi all'interpolazione kriging, fino alle predizioni con machine learning e alla progettazione di strategie di campionamento.

<!-- VIDEO: Introduzione a GeoArchaeo -->
> **Video Tutorial**: [Inserire link video introduzione GeoArchaeo]

### Perche l'analisi geostatistica in archeologia?

L'analisi geostatistica permette di:

- **Interpolare** valori tra punti di campionamento noti, creando superfici continue a partire da dati discreti
- **Quantificare** la correlazione spaziale tra i dati archeologici (ad es. densita dei reperti, spessore degli strati)
- **Predire** distribuzioni spaziali in aree non ancora scavate
- **Ottimizzare** le strategie di campionamento per indagini future
- **Generare** report analitici completi per la documentazione scientifica

### Panoramica del flusso di lavoro

```
1. Carica Dati         2. Variogramma        3. Kriging/ML
   (Scheda Dati)          (Scheda Variogramma)   (Scheda Kriging/ML)
        |                      |                      |
   Seleziona layer        Calcola e modella       Interpolazione o
   e campi                variogramma             predizione spaziale
                               |                      |
                          4. Campionamento       5. Report
                             (Scheda Campion.)      (Scheda Report)
                                  |                      |
                             Progetta             Genera report
                             strategia            di analisi
```

---

## Accesso allo strumento

GeoArchaeo e accessibile dalla barra degli strumenti di PyArchInit tramite il menu a tendina degli Strumenti di Analisi.

### Dalla barra degli strumenti

1. Individuare il pulsante **Strumenti di Analisi** (icona a tendina) nella barra degli strumenti di PyArchInit
2. Fare clic sulla freccia del menu a tendina
3. Selezionare **GeoArchaeo** dall'elenco

<!-- IMAGE: Pulsante Strumenti di Analisi nella barra degli strumenti -->
> **Fig. 1**: Il menu a tendina Strumenti di Analisi nella barra degli strumenti di PyArchInit

Il pannello GeoArchaeo appare come un **dock widget** agganciato all'interfaccia di QGIS. E possibile trascinarlo, ridimensionarlo o staccarlo come qualsiasi altro pannello di QGIS.

<!-- IMAGE: Pannello GeoArchaeo agganciato in QGIS -->
> **Fig. 2**: Il pannello GeoArchaeo agganciato nella finestra QGIS

### Selettore di lingua

Il pannello GeoArchaeo include un **selettore di lingua** nella parte superiore, che permette di cambiare la lingua dell'interfaccia senza riavviare QGIS. Le lingue supportate includono italiano, inglese, tedesco, francese, spagnolo, arabo, catalano, romeno, portoghese e greco.

---

## Interfaccia utente

Il pannello GeoArchaeo e organizzato in **6 schede** principali, ciascuna dedicata a una fase dell'analisi geostatistica.

| Scheda | Icona | Funzione |
|--------|-------|----------|
| **Dati** | Tabella | Caricamento ed esplorazione dei dati spaziali dai layer QGIS |
| **Variogramma** | Grafico | Calcolo e modellazione dei variogrammi sperimentali |
| **Kriging** | Griglia | Interpolazione kriging (ordinario, universale) |
| **ML** | Cervello | Predizioni spaziali con machine learning |
| **Campionamento** | Bersaglio | Progettazione di strategie di campionamento |
| **Report** | Documento | Generazione di report di analisi |

<!-- IMAGE: Panoramica delle 6 schede di GeoArchaeo -->
> **Fig. 3**: Le sei schede del pannello GeoArchaeo

### Barra degli strumenti del pannello

Nella parte superiore del pannello si trovano:

- **Selettore lingua**: Menu a tendina per cambiare la lingua dell'interfaccia
- **Carica dati di esempio**: Pulsante per caricare un dataset di prova
- **Guida**: Pulsante per accedere alla documentazione

---

## Scheda Dati

La scheda **Dati** e il punto di partenza per qualsiasi analisi geostatistica. Permette di caricare e visualizzare i dati spaziali disponibili nei layer QGIS.

### Caricamento dei dati

1. Aprire la scheda **Dati**
2. Selezionare un **layer vettoriale** dal menu a tendina (vengono elencati tutti i layer puntuali presenti nel progetto QGIS)
3. Selezionare il **campo di analisi** (il campo numerico da analizzare)
4. Fare clic su **Carica dati**

<!-- IMAGE: Scheda Dati con layer e campo selezionati -->
> **Fig. 4**: La scheda Dati con un layer e un campo di analisi selezionati

### Dati di esempio

Per familiarizzare con lo strumento, e possibile caricare un **dataset di esempio** facendo clic sul pulsante dedicato. Il dataset di esempio contiene dati archeologici simulati con coordinate e valori numerici adatti all'analisi geostatistica.

### Esplorazione dei dati

Dopo il caricamento, la scheda visualizza:

| Informazione | Descrizione |
|--------------|-------------|
| **Numero di punti** | Totale dei punti caricati |
| **Estensione** | Bounding box del dataset (xmin, ymin, xmax, ymax) |
| **Statistiche** | Media, mediana, deviazione standard, min, max |
| **Anteprima** | Tabella con le prime righe del dataset |

### Requisiti dei dati

- Il layer deve essere un layer **vettoriale puntuale**
- Il campo di analisi deve contenere **valori numerici**
- I punti devono avere **coordinate valide** nel sistema di riferimento del progetto
- Si raccomandano almeno **30 punti** per un'analisi geostatistica significativa

---

## Scheda Variogramma

La scheda **Variogramma** permette di calcolare e modellare variogrammi sperimentali, che descrivono la struttura della correlazione spaziale nei dati.

### Cos'e un variogramma?

Un variogramma e un grafico che mostra come la **varianza** tra coppie di punti cambia in funzione della **distanza** che li separa. I parametri chiave sono:

| Parametro | Descrizione |
|-----------|-------------|
| **Nugget** | Varianza a distanza zero (errore di misura + variabilita micro-scala) |
| **Sill** | Varianza massima raggiunta (plateau del variogramma) |
| **Range** | Distanza oltre la quale non c'e piu correlazione spaziale |

### Calcolo del variogramma sperimentale

1. Assicurarsi di aver caricato i dati nella scheda Dati
2. Aprire la scheda **Variogramma**
3. Impostare i parametri:
   - **Numero di lag**: Numero di intervalli di distanza (default: 15)
   - **Distanza massima**: Distanza massima da considerare (default: auto)
   - **Tolleranza angolare**: Per variogrammi direzionali (default: omni-direzionale)
4. Fare clic su **Calcola variogramma**

<!-- IMAGE: Variogramma sperimentale calcolato -->
> **Fig. 5**: Un variogramma sperimentale calcolato dai dati archeologici

### Modellazione del variogramma

Dopo il calcolo del variogramma sperimentale, e possibile adattare un **modello teorico**:

1. Selezionare il **tipo di modello**:
   - **Sferico**: Il modello piu comune, raggiunge il sill a una distanza finita
   - **Esponenziale**: Raggiunge il sill asintoticamente
   - **Gaussiano**: Transizione graduale, adatto a fenomeni molto regolari
   - **Lineare**: Variogramma senza sill definito
2. Fare clic su **Adatta modello**
3. Verificare i parametri stimati (nugget, sill, range) e la bonta di adattamento

<!-- IMAGE: Modello di variogramma adattato -->
> **Fig. 6**: Modello sferico adattato al variogramma sperimentale

### Variogrammi direzionali

Per verificare l'**anisotropia** (variazione della struttura spaziale in direzioni diverse):

1. Impostare una **tolleranza angolare** (ad es. 22.5 gradi)
2. Selezionare le **direzioni** da analizzare (0, 45, 90, 135 gradi)
3. Confrontare i variogrammi nelle diverse direzioni

---

## Scheda Kriging

La scheda **Kriging** permette di eseguire l'interpolazione kriging, il metodo geostatistico per eccellenza per la predizione spaziale ottimale.

### Tipi di kriging disponibili

| Tipo | Descrizione | Quando usarlo |
|------|-------------|---------------|
| **Kriging ordinario** | Assume media locale costante ma sconosciuta | Caso piu comune, dati stazionari |
| **Kriging universale** | Tiene conto di un trend spaziale (drift) | Quando i dati mostrano una tendenza direzionale |

### Esecuzione del kriging

1. Assicurarsi di aver modellato il variogramma nella scheda Variogramma
2. Aprire la scheda **Kriging**
3. Selezionare il **tipo di kriging** (ordinario o universale)
4. Impostare i parametri della griglia di output:
   - **Risoluzione**: Dimensione delle celle della griglia (in unita del CRS)
   - **Estensione**: Automatica dal dataset o personalizzata
5. Impostare i parametri del kriging:
   - **Punti minimi**: Numero minimo di punti vicini da usare
   - **Punti massimi**: Numero massimo di punti vicini da usare
   - **Raggio di ricerca**: Distanza massima per i punti vicini
6. Fare clic su **Esegui kriging**

<!-- IMAGE: Risultato dell'interpolazione kriging -->
> **Fig. 7**: Mappa di interpolazione kriging con la griglia di predizione

### Risultati del kriging

L'analisi produce due layer raster:

- **Predizione**: I valori interpolati sulla griglia
- **Varianza di kriging**: L'incertezza della predizione in ogni cella

I layer vengono aggiunti automaticamente al progetto QGIS e visualizzati sulla mappa.

> **Nota**: L'analisi viene eseguita in un **thread in background**, cosi l'interfaccia di QGIS rimane utilizzabile durante il calcolo. Una barra di progresso indica lo stato dell'elaborazione.

---

## Scheda Machine Learning

La scheda **ML** offre metodi di machine learning per predizioni spaziali, come alternativa o complemento al kriging.

### Algoritmi disponibili

| Algoritmo | Descrizione | Vantaggi |
|-----------|-------------|----------|
| **Random Forest** | Ensemble di alberi decisionali | Robusto, gestisce relazioni non lineari |
| **Gradient Boosting** | Alberi decisionali sequenziali | Alta accuratezza, adatto a pattern complessi |
| **SVR** | Support Vector Regression | Buono con pochi dati, kernel flessibili |

### Flusso di lavoro ML

1. Aprire la scheda **ML**
2. Selezionare l'**algoritmo** desiderato
3. Configurare le **variabili predittive**:
   - Coordinate (X, Y)
   - Campi aggiuntivi dal layer (ad es. quota, pendenza, distanza da un fiume)
4. Impostare i **parametri** dell'algoritmo (o utilizzare i valori predefiniti)
5. Selezionare il metodo di **validazione**:
   - Validazione incrociata k-fold (default: 5 fold)
   - Hold-out (percentuale di test)
6. Fare clic su **Addestra modello**

<!-- IMAGE: Configurazione del modello ML -->
> **Fig. 8**: Configurazione di un modello Random Forest nella scheda ML

### Risultati ML

| Risultato | Descrizione |
|-----------|-------------|
| **Mappa di predizione** | Layer raster con i valori predetti |
| **Importanza variabili** | Grafico dell'importanza relativa delle variabili predittive |
| **Metriche di validazione** | R-squared, RMSE, MAE dalla validazione incrociata |
| **Grafico residui** | Scatter plot dei valori osservati vs predetti |

### Confronto Kriging vs ML

Per confrontare i risultati:

1. Eseguire sia il kriging che il ML sugli stessi dati
2. Confrontare le metriche di validazione nella scheda Report
3. Visualizzare le mappe di differenza

---

## Scheda Campionamento

La scheda **Campionamento** permette di progettare strategie di campionamento ottimali per indagini archeologiche future.

### Strategie di campionamento

| Strategia | Descrizione | Quando usarla |
|-----------|-------------|---------------|
| **Casuale semplice** | Punti distribuiti casualmente nell'area | Quando non si hanno informazioni a priori |
| **Casuale stratificato** | Punti casuali all'interno di strati definiti | Quando l'area ha zone con caratteristiche diverse |
| **Griglia regolare** | Punti su una griglia regolare | Per copertura uniforme dell'area |
| **Ottimizzato** | Punti posizionati per minimizzare la varianza di kriging | Quando si ha un variogramma |

### Progettazione del campionamento

1. Aprire la scheda **Campionamento**
2. Selezionare la **strategia** di campionamento
3. Impostare il **numero di punti** desiderato
4. Definire l'**area di studio**:
   - Dall'estensione del layer corrente
   - Da un layer poligonale
   - Disegnando manualmente sulla mappa
5. Impostare eventuali **vincoli**:
   - Distanza minima tra i punti
   - Aree di esclusione
6. Fare clic su **Genera campionamento**

<!-- IMAGE: Punti di campionamento generati -->
> **Fig. 9**: Punti di campionamento ottimizzato sovrapposti alla mappa dell'area di studio

### Risultati del campionamento

- Un **layer vettoriale puntuale** con i punti di campionamento viene aggiunto al progetto QGIS
- Una **tabella attributi** con le coordinate e gli identificativi dei punti
- Un **report** con le statistiche della strategia (copertura, distanze, etc.)

---

## Scheda Report

La scheda **Report** permette di generare report completi dell'analisi geostatistica.

### Contenuto del report

Il report include automaticamente tutte le analisi eseguite durante la sessione:

| Sezione | Contenuto |
|---------|-----------|
| **Sommario** | Riepilogo del dataset e delle analisi eseguite |
| **Dati** | Statistiche descrittive, distribuzione, mappa dei punti |
| **Variogramma** | Variogramma sperimentale, modello, parametri |
| **Interpolazione** | Mappa di kriging/ML, metriche di validazione |
| **Campionamento** | Strategia, mappa dei punti, statistiche |
| **Conclusioni** | Interpretazione sintetica dei risultati |

### Generazione del report

1. Aprire la scheda **Report**
2. Selezionare le **sezioni** da includere (tutte per default)
3. Impostare il **formato di output**:
   - PDF (consigliato per la documentazione)
   - HTML (per la consultazione interattiva)
   - Markdown (per la modifica successiva)
4. Inserire eventuali **note aggiuntive** o commenti
5. Fare clic su **Genera report**

<!-- IMAGE: Anteprima del report generato -->
> **Fig. 10**: Anteprima di un report di analisi geostatistica generato da GeoArchaeo

### Esportazione

Il report puo essere salvato localmente o esportato nei formati disponibili. Le immagini (grafici, mappe) vengono incorporate direttamente nel report.

---

## Flusso di lavoro operativo

Ecco un flusso di lavoro tipico per un'analisi geostatistica completa in GeoArchaeo:

### Passo 1: Preparazione dei dati

1. Caricare il layer vettoriale puntuale in QGIS
2. Verificare che il campo numerico da analizzare sia presente e corretto
3. Controllare il sistema di riferimento delle coordinate

### Passo 2: Esplorazione dei dati

1. Aprire GeoArchaeo dalla barra degli strumenti
2. Nella scheda **Dati**, selezionare il layer e il campo
3. Esaminare le statistiche descrittive
4. Verificare la distribuzione dei dati (cercare outlier o valori anomali)

### Passo 3: Analisi del variogramma

1. Nella scheda **Variogramma**, calcolare il variogramma sperimentale
2. Provare diversi modelli (sferico, esponenziale, gaussiano)
3. Scegliere il modello con il miglior adattamento
4. Annotare i parametri (nugget, sill, range)

### Passo 4: Interpolazione

1. Nella scheda **Kriging**, impostare i parametri della griglia
2. Eseguire il kriging ordinario
3. Esaminare la mappa di predizione e la varianza
4. Opzionalmente, confrontare con un modello ML nella scheda ML

### Passo 5: Campionamento (opzionale)

1. Nella scheda **Campionamento**, progettare una strategia per indagini future
2. Utilizzare il variogramma per il campionamento ottimizzato

### Passo 6: Report

1. Nella scheda **Report**, generare il report finale
2. Esportare in PDF per la documentazione

---

## Risoluzione dei problemi

### Problemi comuni

| Problema | Causa | Soluzione |
|----------|-------|----------|
| Nessun layer disponibile | Non ci sono layer puntuali nel progetto | Aggiungere un layer vettoriale puntuale al progetto QGIS |
| Nessun campo numerico | Il layer non ha campi numerici | Verificare la tabella attributi del layer |
| Variogramma piatto | Dati senza correlazione spaziale | Verificare i dati, aumentare la distanza massima |
| Kriging fallisce | Modello di variogramma non adattato | Adattare prima un modello nella scheda Variogramma |
| Risultati ML scadenti | Pochi dati o variabili non informative | Aggiungere variabili predittive o aumentare i dati |
| Pannello non visibile | Widget chiuso accidentalmente | Riaccedere dal menu Strumenti di Analisi |

### Errori frequenti

- **"Dati insufficienti"**: Servono almeno 30 punti per un'analisi affidabile
- **"Modello di variogramma non definito"**: Adattare un modello prima di eseguire il kriging
- **"CRS non compatibile"**: Tutti i layer devono usare lo stesso sistema di riferimento

### Prestazioni

- L'analisi viene eseguita in **thread in background**: l'interfaccia QGIS resta utilizzabile
- Per dataset molto grandi (>10.000 punti), l'elaborazione potrebbe richiedere piu tempo
- E possibile monitorare il progresso tramite la barra nella parte inferiore del pannello

---

## Note tecniche

### Dipendenze

GeoArchaeo utilizza le seguenti librerie Python:

| Libreria | Utilizzo |
|----------|----------|
| **NumPy** | Calcoli numerici e matriciali |
| **SciPy** | Ottimizzazione e fitting dei modelli |
| **scikit-learn** | Algoritmi di machine learning |
| **Matplotlib** | Generazione dei grafici |

### Sistemi di riferimento

- GeoArchaeo lavora nel sistema di riferimento del progetto QGIS corrente
- Si raccomanda di utilizzare un **CRS proiettato** (in metri) per l'analisi geostatistica
- Sistemi geografici (in gradi) possono produrre risultati imprecisi

### Esportazione dei risultati

I risultati possono essere esportati in vari formati:

- **Layer raster** (GeoTIFF) per le superfici interpolate
- **Layer vettoriale** (GeoPackage, Shapefile) per i punti di campionamento
- **Grafici** (PNG, SVG) per variogrammi e diagnostiche
- **Report** (PDF, HTML, Markdown) per la documentazione

### Integrazione con QGIS

- I layer di output vengono aggiunti automaticamente al pannello **Layer** di QGIS
- Lo stile dei layer raster puo essere personalizzato con le proprieta di QGIS
- I risultati sono compatibili con tutti gli strumenti di analisi spaziale di QGIS

---

> **Nota**: GeoArchaeo e in costante sviluppo. Per segnalare bug o suggerire miglioramenti, utilizzare il sistema di issue tracking del progetto PyArchInit su GitHub.
