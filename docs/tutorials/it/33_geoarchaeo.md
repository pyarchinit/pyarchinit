# PyArchInit - GeoArchaeo - Analisi Geostatistica

## Indice
1. [Introduzione](#introduzione)
2. [Accesso allo strumento](#accesso-allo-strumento)
3. [Interfaccia utente](#interfaccia-utente)
4. [Scheda Dati](#scheda-dati)
5. [Scheda Variogramma](#scheda-variogramma)
6. [Scheda Kriging](#scheda-kriging)
7. [Scheda Pattern (ML)](#scheda-pattern-ml)
8. [Scheda Campionamento](#scheda-campionamento)
9. [Scheda Report](#scheda-report)
10. [Flusso di lavoro operativo](#flusso-di-lavoro-operativo)
11. [Risoluzione dei problemi](#risoluzione-dei-problemi)
12. [Note tecniche](#note-tecniche)

---

## Introduzione

**GeoArchaeo** è il modulo di analisi geostatistica integrato in PyArchInit e corrisponde alla versione **1.3.1** del plugin GeoArchaeo. Lavora su qualsiasi layer di punti del progetto QGIS che abbia un campo numerico (numero di frammenti, misure geofisiche, analisi del suolo, misure delle tombe…) e accompagna l'analisi dalle statistiche descrittive al variogramma, all'interpolazione con il kriging ordinario e la sua incertezza, alla ricerca di gruppi e anomalie con il machine learning, alla proposta di nuovi punti di campionamento, fino a un report finale.

<!-- VIDEO: Introduzione a GeoArchaeo -->
> **Video Tutorial**: [Inserire link video introduzione GeoArchaeo]

### Perché l'analisi geostatistica in archeologia?

L'analisi geostatistica permette di:

- **Descrivere** la distribuzione dei valori misurati (media, dispersione, asimmetria, valori anomali)
- **Quantificare** la correlazione spaziale, cioè fino a che distanza i valori si somigliano (variogramma)
- **Interpolare** i valori tra i punti noti, ottenendo una superficie continua accompagnata dalla sua incertezza (kriging)
- **Riconoscere** gruppi di punti simili e anomalie (machine learning)
- **Pianificare** dove campionare o scavare nelle campagne successive
- **Documentare** le analisi in un report

### Panoramica del flusso di lavoro

```
Dati di input: layer di punti + campo numerico (scelti in alto, una volta sola)
  │
  ├─ 1 Dati ............ statistiche descrittive, istogramma
  ├─ 2 Variogramma ..... nugget, sill, range, anisotropia
  ├─ 3 Kriging ......... raster della stima e dell'incertezza, cross-validation
  ├─ 4 Pattern (ML) .... gruppi e anomalie (layer di punti)
  ├─ 5 Campionamento ... nuovi punti proposti (layer di punti)
  └─ 6 Report .......... documento HTML con grafici interattivi, oppure PDF
```

### Novità della versione 1.3.1

- Layer e campo si scelgono **una sola volta** in alto e valgono per tutte le schede; ogni scheda conserva i propri risultati
- I grafici compaiono nel pannello anche senza QtWebEngine (anteprima statica e pulsante per aprirli nel browser)
- Il kriging produce anche il **raster dell'incertezza**, applica la rampa di colori e calcola una vera **cross-validation leave-one-out**
- L'anisotropia si verifica con veri **variogrammi direzionali**; nugget, sill e range si possono fissare a mano
- Variogramma e kriging sono molto più veloci (ricerca dei vicini con KD-tree): griglie fino a **500 × 500 celle**
- I valori NULL non bloccano più le statistiche né il kriging; il report contiene i grafici; i dati di esempio vengono dalla cartella del modulo
- La lingua del pannello resta salvata nelle impostazioni di QGIS

---

## Accesso allo strumento

GeoArchaeo fa parte del gruppo degli strumenti di analisi di PyArchInit.

### Dalla barra degli strumenti

1. Nella barra degli strumenti di PyArchInit individuare il pulsante a tendina degli **strumenti di analisi** (lo stesso gruppo che contiene, tra gli altri, SAM, Pottery Tools e MoveCost)
2. Fare clic sulla freccia accanto al pulsante: l'icona visibile può essere quella di un altro strumento del gruppo
3. Scegliere **GeoArchaeo - Analisi Geostatistica**

<!-- IMAGE: Pulsante a tendina degli strumenti di analisi nella barra degli strumenti -->
> **Fig. 1**: Il menu a tendina degli strumenti di analisi nella barra degli strumenti di PyArchInit

La stessa voce si trova nel menu **pyArchInit** della barra dei menu di QGIS e nel menu dei plugin, sotto **pyArchInit - Archaeological GIS Tools**.

Il pannello GeoArchaeo si apre come **pannello agganciato (dock)** sul lato destro della finestra di QGIS: si può spostare, ridimensionare o staccare come qualsiasi pannello di QGIS. Se lo si chiude, la stessa voce lo riapre con i risultati della sessione ancora presenti.

<!-- IMAGE: Pannello GeoArchaeo agganciato sul lato destro di QGIS -->
> **Fig. 2**: Il pannello GeoArchaeo agganciato sul lato destro della finestra di QGIS

### Selettore di lingua

In alto a destra la tendina **«Lingua:»** offre **Italiano** ed **English**, le sole due lingue dell'interfaccia di GeoArchaeo. Il cambio è immediato, senza riavviare QGIS, e la scelta resta salvata nelle impostazioni di QGIS. Finché non si sceglie, il pannello segue la lingua di QGIS: italiano se QGIS è in italiano, inglese in tutti gli altri casi.

---

## Interfaccia utente

Il pannello contiene, dall'alto in basso: l'intestazione con i pulsanti, il gruppo **«Dati di input (usati da tutte le schede)»**, le **6 schede** dell'analisi e, durante i calcoli, la barra di avanzamento con il pulsante **«Annulla»**.

### Intestazione

| Elemento | Funzione |
|----------|----------|
| **«Carica dati di esempio»** | Apre l'elenco dei dataset di prova inclusi nel modulo (vedi la scheda Dati) |
| **«Tutorial»** | Apre la guida integrata di GeoArchaeo, in italiano o in inglese, consultabile anche nel browser |
| **«Lingua:»** | Tendina Italiano / English |

### Dati di input

Nel gruppo **«Dati di input (usati da tutte le schede)»** si scelgono una sola volta:

- **«Layer punti:»**: un layer vettoriale di punti del progetto
- **«Campo valore (numerico):»**: il campo da analizzare (la tendina elenca solo i campi numerici)

Sotto compare un riepilogo con i punti validi sul totale, il CRS e l'estensione del layer, per esempio «500 punti validi su 500 · CRS EPSG:32633 · …». I punti senza valore (NULL o testo non numerico) non sono contati tra i validi. Il riepilogo avvisa anche se nel progetto non ci sono layer di punti, se il layer non ha campi numerici o se il CRS è geografico (gradi).

Quando si cambia layer, il pannello propone anche la distanza massima del variogramma e la risoluzione del kriging e, se nella scheda Pattern (ML) non è selezionato nessun layer, vi preseleziona questo.

### Le sei schede

| Scheda | Funzione | Risultato |
|--------|----------|-----------|
| **Dati** | Statistiche descrittive del campo | Tabella delle statistiche, istogramma con box plot |
| **Variogramma** | Struttura spaziale dei valori | Nugget, sill, range, anisotropia, grafico |
| **Kriging** | Interpolazione su una griglia regolare | Raster della stima e dell'incertezza, cross-validation |
| **Pattern (ML)** | Gruppi e anomalie con il machine learning | Layer di punti con l'etichetta del gruppo |
| **Campionamento** | Proposta di nuovi punti da campionare | Layer di punti e tabella delle coordinate |
| **Report** | Raccolta delle analisi della sessione | File HTML con grafici interattivi, oppure PDF |

<!-- IMAGE: Intestazione, gruppo Dati di input e le sei schede di GeoArchaeo -->
> **Fig. 3**: L'intestazione, il gruppo «Dati di input» e le sei schede del pannello GeoArchaeo

### Risultati e grafici

Ogni scheda mostra i risultati in un **riquadro** sotto il pulsante di calcolo, che resta visibile finché non si ripete l'analisi, e il **grafico** nel pannello:

- se QGIS dispone di QtWebEngine, il grafico Plotly è interattivo direttamente nel pannello (zoom, valori al passaggio del mouse)
- altrimenti compare un'**anteprima statica** con la nota «Anteprima statica (QtWebEngine non disponibile in questa installazione di QGIS).»
- in entrambi i casi il pulsante **«Apri grafico interattivo nel browser»** apre la versione interattiva nel browser web

Le schede Dati, Variogramma e Kriging terminano con un collegamento al passo successivo, per esempio **«Prossimo passo: Variogramma →»**.

### Analisi in corso

Variogramma, kriging, pattern recognition e campionamento vengono calcolati in un **thread separato**: QGIS resta utilizzabile e in fondo al pannello compaiono la **barra di avanzamento** (in percentuale per il kriging) e il pulsante **«Annulla»**. Si esegue un'analisi alla volta: avviandone un'altra compare «Un'analisi è già in corso: attendi che finisca o annullala.»

---

## Scheda Dati

La scheda **Dati** («1. Analisi esplorativa») descrive la distribuzione dei valori prima di interpolarli.

### Calcolo delle statistiche

1. Nel gruppo «Dati di input» scegliere il layer di punti e il campo numerico
2. Aprire la scheda **Dati**
3. Fare clic su **«Calcola statistiche»**

<!-- IMAGE: Scheda Dati con statistiche e istogramma -->
> **Fig. 4**: La scheda Dati con la tabella delle statistiche e l'istogramma del campo scelto

### Statistiche e interpretazione

| Statistica | Descrizione |
|------------|-------------|
| **Numero valori**, **Valori mancanti** | Punti con un valore valido e punti esclusi (NULL o testo non numerico) |
| **Minimo**, **Massimo**, **Media**, **Mediana** | Intervallo e posizione dei valori |
| **Dev. standard**, **Coeff. di variazione** | Dispersione assoluta e relativa |
| **Primo quartile (Q1)**, **Terzo quartile (Q3)** | Limiti del 50% centrale dei valori |
| **Asimmetria (skewness)**, **Curtosi** | Forma della distribuzione |

Sotto la tabella il pannello aggiunge una lettura in parole:

- asimmetria maggiore di 1: distribuzione asimmetrica a destra (pochi valori molto alti); conviene valutare una trasformazione logaritmica prima del kriging, per esempio creando un nuovo campo con il Calcolatore di campi
- asimmetria minore di -1: distribuzione asimmetrica a sinistra (pochi valori molto bassi)
- negli altri casi: distribuzione circa simmetrica, adatta al kriging
- il numero di possibili valori anomali, cioè oltre 3 deviazioni standard dalla media

Il grafico mostra l'**istogramma** dei valori con un **box plot** (nell'anteprima statica solo l'istogramma).

### Dati di esempio

Il pulsante **«Carica dati di esempio»** apre la finestra «Dati di esempio GeoArchaeo» con i dataset della cartella `test_layers` del modulo; il percorso è indicato in **«Cartella:»** e si può cambiare con **«Sfoglia…»**. GeoPackage e GeoJSON sono già spuntati. I CSV compaiono solo se non esiste un GeoPackage o un GeoJSON con lo stesso nome, vanno spuntati a mano e vengono caricati come testo delimitato (campi `x` e `y`, EPSG:32633). Con **OK** i layer vengono aggiunti al progetto e il primo layer di punti caricato diventa il layer di input del pannello.

| Dataset | Punti | Campi numerici principali | Uso consigliato |
|---------|-------|---------------------------|-----------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Statistiche, variogramma, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Gli stessi di `villa_ceramica` | Prova di tutte le schede |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, prova su un dataset grande |
| `necropoli` (GeoPackage) | 120 tombe | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN o K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging delle proprietà del suolo |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging della densità, campionamento |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variogramma e kriging con pochi punti |
| `area_studio` (GeoJSON) | 1 poligono | — | Area di studio per il campionamento |

Tra i CSV, `magnetometria_grid` (2500 punti, campo `mag_nT`) contiene anomalie magnetiche simulate (due muri, una fossa, una fornace). Tutti i dati sono simulati e in EPSG:32633 (UTM 33N, metri). Il poligono `area_studio` copre la zona di `ricognizione_survey`, `unita_scavo_ceramica` e `magnetometria_grid`, non quella degli altri dataset.

### Requisiti dei dati

- Il layer deve essere un layer vettoriale di **punti** (per i multipunto si usa il primo punto)
- Il campo deve essere **numerico**: un campo di testo che contiene numeri va convertito con il Calcolatore di campi
- I valori NULL o non numerici vengono esclusi automaticamente e contati come mancanti
- Servono almeno **5 punti** con un valore valido per variogramma e kriging (1 per le statistiche); un variogramma affidabile richiede di norma alcune decine di punti
- Si raccomanda un **CRS proiettato** in metri (per esempio UTM): con un CRS geografico il riepilogo avvisa e variogramma e kriging chiedono conferma

---

## Scheda Variogramma

La scheda **Variogramma** («2. Variogramma») misura come la differenza tra i valori cresce con la distanza: descrive la struttura spaziale dei dati e guida il kriging.

### Cos'è un variogramma?

Il variogramma mette in relazione la **semivarianza** delle coppie di punti con la **distanza** che li separa. I parametri del modello sono:

| Parametro | Descrizione |
|-----------|-------------|
| **Nugget** | Variabilità a distanza quasi nulla: errore di misura e variabilità a piccola scala |
| **Sill** | Varianza totale raggiunta dal modello (il "plateau") |
| **Range** | Distanza oltre la quale i valori non sono più correlati; in GeoArchaeo è il range pratico (95% del sill) |

### Calcolo del variogramma

1. Aprire la scheda **Variogramma**
2. Nel gruppo **«Parametri»** controllare **«Distanza massima:»**: il pulsante **«Auto»** propone circa 1/3 della diagonale dell'area occupata dai punti (lo stesso valore viene proposto quando si cambia layer)
3. Scegliere il **«Modello teorico:»**
4. Se serve, spuntare **«Verifica anisotropia (variogrammi direzionali)»**
5. Fare clic su **«Calcola variogramma»**

Le coppie di punti vengono raggruppate in **15 classi di distanza** (lag) tra zero e la distanza massima; il numero di classi non si modifica dal pannello. Oltre i **3000 punti** il variogramma viene calcolato su un sottocampione casuale di 3000 punti, perché il numero di coppie cresce con il quadrato dei punti. Il modello viene adattato con i minimi quadrati pesati sul numero di coppie di ogni classe.

<!-- IMAGE: Scheda Variogramma con parametri e risultati -->
> **Fig. 5**: La scheda Variogramma con i parametri, il modello teorico e il riquadro dei risultati

### Modelli teorici

| Modello | Andamento | Quando usarlo |
|---------|-----------|---------------|
| **«Sferico (consigliato)»** | Cresce fino al range e poi resta costante | Il più usato: densità di reperti, distribuzioni con limiti netti |
| **«Esponenziale»** | Cresce rapidamente vicino all'origine e raggiunge il sill gradualmente | Fenomeni a decadimento continuo, per esempio elementi chimici nel suolo |
| **«Gaussiano»** | Molto regolare vicino all'origine | Fenomeni molto "lisci" (superfici); da usare con cautela |
| **«Matérn»** | Intermedio tra esponenziale e gaussiano (ν = 1,5) | Alternativa flessibile |

Regola pratica: iniziare con il modello sferico e confrontare l'RMSE del fit con quello degli altri modelli. Il kriging usa l'**ultimo** variogramma calcolato: dopo i confronti, ricalcolare quello scelto.

### Parametri manuali

Il gruppo **«Parametri manuali (opzionale)»**, disattivato per default, permette di fissare **«Nugget (effetto pepita):»**, **«Sill (varianza totale):»** e **«Range (distanza di correlazione):»**. Con il gruppo attivo, i valori diversi da zero restano fissi e quelli lasciati su «Auto» (zero) vengono stimati.

### Lettura dei risultati

Il riquadro dei risultati riporta:

- il modello con **Nugget**, **Sill**, **Range** (nelle unità del CRS) e l'**RMSE** del fit
- il numero di coppie di punti e di classi di distanza, con l'eventuale sottocampione usato
- una lettura del range: fino a quella distanza i valori sono spazialmente correlati, oltre non si influenzano
- il rapporto nugget/sill: sotto il 25% forte continuità a piccola scala, fino al 60% continuità moderata, oltre il 60% molta variabilità a piccola scala o errore di misura (il kriging sarà poco informativo)

Il grafico mostra i punti del variogramma sperimentale (più grandi dove le coppie sono più numerose), la curva del modello e le linee di nugget, sill e range.

<!-- IMAGE: Variogramma sperimentale con il modello adattato -->
> **Fig. 6**: Variogramma sperimentale e modello sferico con le linee di nugget, sill e range

### Variogrammi direzionali (anisotropia)

Con **«Verifica anisotropia (variogrammi direzionali)»** attiva, GeoArchaeo calcola anche i variogrammi nelle direzioni **0°, 45°, 90° e 135°** (angoli misurati da Est in senso antiorario, tolleranza ±22,5°). Nugget e sill restano quelli del variogramma complessivo; per ogni direzione si stima il range.

- Se il rapporto tra il range maggiore e quello minore supera **2**, il riquadro segnala l'anisotropia e la direzione maggiore (per esempio lungo un muro, una strada o un pendio)
- Altrimenti riporta «Nessuna anisotropia rilevante» con il rapporto calcolato
- Con poche coppie per direzione compare «Coppie insufficienti per i variogrammi direzionali.»

Nel grafico interattivo i variogrammi direzionali sono voci della legenda nascoste all'inizio: fare clic su 0°, 45°, 90° o 135° per mostrarli (nell'anteprima statica sono sempre disegnati). Il kriging del pannello usa il modello omnidirezionale: l'anisotropia serve all'interpretazione.

---

## Scheda Kriging

La scheda **Kriging** («3. Kriging ordinario») interpola i valori su una griglia regolare usando il variogramma, produce anche la mappa dell'incertezza e aggiunge i raster al progetto.

### Il kriging ordinario

Il pannello esegue il **kriging ordinario** (media locale costante ma sconosciuta), adatto alla maggior parte dei dati archeologici. Per ogni cella usa i **20 punti più vicini**, trovati con un KD-tree; questo numero non si modifica dal pannello. Co-kriging, kriging spazio-temporale e kriging a blocchi per dataset molto grandi esistono solo come algoritmi Processing del plugin GeoArchaeo autonomo e non sono disponibili in PyArchInit.

### Esecuzione del kriging

1. Aprire la scheda **Kriging** e leggere la riga di stato del variogramma (vedi sotto); il pulsante **«← Vai al Variogramma»** riporta alla scheda precedente
2. Impostare **«Risoluzione cella:»**, cioè la dimensione della cella nelle unità del CRS: il pannello propone circa 100 celle sul lato maggiore del layer e mostra sotto la griglia risultante («Griglia: … × … = … celle»)
3. Lasciare attiva **«Usa il variogramma calcolato»** per usare il variogramma della scheda precedente; se è disattiva, il variogramma viene stimato automaticamente
4. Lasciare attiva **«Crea anche il raster dell'incertezza (dev. standard)»** se serve la mappa dell'incertezza
5. Fare clic su **«Esegui kriging»**: la barra di avanzamento mostra la percentuale e **«Annulla»** interrompe il calcolo

La riga di stato può indicare:

- «Variogramma disponibile: …, range … ✓»: viene usato il variogramma calcolato sullo stesso layer e campo
- «Nessun variogramma calcolato: verrà stimato automaticamente (modello sferico).»
- «Il variogramma è stato calcolato su un altro layer/campo: verrà ricalcolato.» (anche in questo caso con una stima automatica)

> **Griglia**: la griglia copre l'estensione del layer di punti ed è limitata a **500 celle per lato**. Se la risoluzione scelta è troppo fine, la dimensione della cella viene aumentata automaticamente e la riga della griglia lo segnala («risoluzione minima … (max 500 celle per lato)»). Oltre **40.000 celle** la riga diventa arancione e all'avvio il pannello chiede conferma, perché il calcolo può richiedere alcuni minuti.

<!-- IMAGE: Raster del kriging e metriche di cross-validation -->
> **Fig. 7**: I raster della stima e dell'incertezza sulla mappa, con il riquadro dei risultati e la cross-validation

### Risultati del kriging

Il kriging aggiunge al progetto due raster GeoTIFF nel CRS del layer di punti:

| Layer | Contenuto | Stile |
|-------|-----------|-------|
| `Kriging_<campo>` | Valore stimato in ogni cella | Rampa di colori dal blu al rosso passando per il giallo; visibile |
| `Kriging_<campo>_incertezza` | Deviazione standard della stima (incertezza) | Rampa dal giallo chiaro al rosso; aggiunto in cima all'elenco dei layer ma nascosto |

Con il pannello in inglese il secondo raster si chiama `Kriging_<campo>_uncertainty`. I file vengono scritti in una **cartella temporanea**: per conservarli, esportarli dal menu contestuale del layer (**Esporta**).

Il riquadro dei risultati riassume punti usati, dimensioni della griglia, risoluzione, modello e range; il grafico mostra la mappa dei valori stimati e quella dell'incertezza con i punti campione sovrapposti.

### Cross-validation leave-one-out

Dopo il kriging, GeoArchaeo esegue una **validazione incrociata leave-one-out**: ogni punto viene tolto e ristimato dagli altri (su un massimo di 200 punti scelti a caso nei dataset più grandi). Le metriche compaiono nel riquadro dei risultati:

| Metrica | Significato | Valore desiderabile |
|---------|-------------|---------------------|
| **RMSE** | Errore tipico della stima | Il più basso possibile, rispetto alla dev. standard dei dati |
| **MAE** (errore assoluto medio) | Errore medio in valore assoluto | Il più basso possibile |
| **ME** (errore medio, bias) | Sovrastima o sottostima sistematica | Vicino a 0 |
| **R²** (quota di varianza spiegata) | Capacità predittiva | Da 0,5 in su buona, sotto 0,2 bassa |
| **MSDR** (errore standardizzato) | Realismo dell'incertezza stimata | Circa 1; sopra 1,5 incertezza sottostimata, sotto 0,5 sovrastimata |

Il pannello aggiunge un giudizio in parole sulla capacità predittiva (buona, moderata o bassa) e, quando serve, sull'MSDR.

> **Nota**: il kriging viene eseguito in un **thread in background**, quindi QGIS resta utilizzabile durante il calcolo; la barra di avanzamento indica lo stato dell'elaborazione.

---

## Scheda Pattern (ML)

La scheda **Pattern (ML)** («4. Pattern recognition (machine learning)») raggruppa i punti per posizione e attributi numerici, oppure individua le anomalie, e crea un layer con l'etichetta di ogni punto.

### Metodi disponibili

| Metodo (voce della tendina) | Cosa fa | Parametri |
|-----------------------------|---------|-----------|
| **«K-Means – gruppi per similarità»** | Divide i punti in K gruppi simili per posizione e attributi | **«Numero di gruppi (0 = automatico):»**; con 0 il numero viene scelto in base ai punti (da 2 a 5) |
| **«DBSCAN – gruppi per densità (trova anche punti isolati)»** | Trova gruppi per densità senza fissarne il numero; i punti isolati formano il gruppo «Isolati / rumore» | Automatici |
| **«Isolation Forest – rilevamento anomalie»** | Segnala come «Anomalia» circa il 10% dei punti più diversi dagli altri; i restanti sono «Normale» | Automatici |

### Esecuzione

1. Aprire la scheda **Pattern (ML)**
2. Nell'elenco **«Layer di punti da analizzare (uno o più):»** selezionare uno o più layer di punti (se l'elenco non ha selezioni, viene preselezionato il layer di input)
3. Scegliere il **«Metodo:»**
4. Solo per K-Means, impostare **«Numero di gruppi (0 = automatico):»**
5. Fare clic su **«Avvia pattern recognition»**

Le variabili analizzate sono le **coordinate X e Y** e **tutti i campi numerici** dei layer selezionati, standardizzati; i valori mancanti vengono sostituiti con la media del campo. Non si usa solo il campo valore scelto in alto: entrano tutti i campi numerici, compresi identificativi e numeri progressivi, e se falsano i gruppi conviene analizzare una copia del layer con i soli campi utili. Analizzando più layer insieme, conviene che abbiano gli stessi campi numerici nello stesso ordine e lo stesso CRS (il layer creato usa il CRS del primo layer selezionato).

<!-- IMAGE: Scheda Pattern (ML) con il layer dei gruppi -->
> **Fig. 8**: La scheda Pattern (ML) con il grafico dei gruppi e il layer `Gruppi_ML` sulla mappa

### Risultati

- Il riquadro dei risultati riporta il metodo, il numero di gruppi e quanti punti cadono in ciascuno (per esempio «Gruppo A (n=42)»)
- Il grafico mostra i punti nel piano delle prime due componenti principali (PC1, PC2) delle variabili, colorati per gruppo
- Viene creato un layer di punti temporaneo, `Gruppi_ML` (K-Means, DBSCAN) oppure `Anomalie_ML` (Isolation Forest), con una legenda per categoria: grigio per i punti isolati, rosso e più grande per le anomalie; con il pannello in inglese i nomi sono `ML_groups` e `ML_anomalies`

| Campo | Contenuto |
|-------|-----------|
| `cluster_id` | Numero del gruppo (-1 = isolati con DBSCAN; 1 = anomalia e 0 = normale con Isolation Forest) |
| `cluster_name` | Nome leggibile, per esempio «Gruppo A (n=42)», «Isolati / rumore (n=5)», «Anomalia (n=12)» |
| `cluster_size` | Numero di punti del gruppo |
| `method` | Metodo usato |
| `x_coord`, `y_coord` | Coordinate del punto |

### Classificazione supervisionata

Sotto il metodo, il pannello ricorda che la classificazione supervisionata (Random Forest con un campo di etichette) si trova in **Processing → GeoArchaeo**. Quell'algoritmo appartiene al plugin GeoArchaeo autonomo: in PyArchInit il provider Processing di GeoArchaeo non viene registrato, quindi la Random Forest non è disponibile. Per usarla serve il plugin GeoArchaeo separato.

---

## Scheda Campionamento

La scheda **Campionamento** («5. Nuovi punti di campionamento») suggerisce dove campionare o scavare in futuro partendo dai punti esistenti e crea un layer con i punti proposti.

### Criteri di campionamento

| Criterio (voce della tendina) | Come sceglie i punti | Quando usarlo |
|-------------------------------|----------------------|---------------|
| **«Copertura (maximin)»** | Ogni nuovo punto è il più lontano possibile da tutti gli altri | Riempire i vuoti in modo uniforme |
| **«Riduzione incertezza (varianza di kriging)»** | Ogni nuovo punto va dove la varianza di kriging è massima | Ridurre l'errore del kriging dove è più alto |
| **«Griglia stratificata»** | Una posizione per cella di una griglia regolare, con una leggera perturbazione casuale | Copertura regolare di un'area definita |
| **«Adattivo (zone meno dense)»** | Estrazione casuale con probabilità maggiore dove ci sono pochi punti | Privilegiare le zone meno campionate mantenendo una componente casuale |

Il criterio «Riduzione incertezza» usa il variogramma calcolato se riguarda lo stesso layer e campo e se nella scheda Kriging è attiva «Usa il variogramma calcolato»; altrimenti usa un modello generico basato sulla distanza tipica tra i punti.

### Progettazione del campionamento

1. Controllare **«Punti esistenti:»**: è il layer scelto in alto nel gruppo «Dati di input» (per il campionamento il campo numerico non serve)
2. Facoltativo: scegliere in **«Area di studio (poligono, opzionale):»** un layer poligonale; tutti i suoi poligoni vengono uniti e riproiettati nel CRS dei punti, anche se il layer è in un altro CRS
3. Impostare **«Nuovi punti da proporre:»** (da 1 a 500, predefinito 10)
4. Scegliere il **«Criterio:»**: sotto la tendina compare la sua descrizione
5. Fare clic su **«Calcola nuovi punti»**

Senza area di studio, i punti vengono cercati nel rettangolo che contiene i punti esistenti, allargato del 20% su ogni lato.

<!-- IMAGE: Nuovi punti di campionamento proposti -->
> **Fig. 9**: I nuovi punti di campionamento (stelle gialle) proposti dentro l'area di studio

### Risultati del campionamento

- Il riquadro dei risultati indica quanti punti sono stati proposti e con quale criterio; sotto, la tabella «Coordinate dei punti proposti:» elenca numero, X e Y
- Viene creato il layer di punti temporaneo `Nuovi_punti_campionamento` (`New_sampling_points` con il pannello in inglese), con simbolo a stella gialla e i campi `point_id`, `x_coord`, `y_coord` e `type` (valore `suggested`)

---

## Scheda Report

La scheda **Report** («6. Report») riunisce in un unico documento le analisi eseguite in questa sessione: statistiche, grafici interattivi, parametri e validazione.

### Contenuto del report

Nel gruppo **«Sezioni da includere»** ogni sezione è indicata come «disponibile» o «non ancora calcolato»; le sezioni non calcolate non si possono scegliere.

| Sezione | Contenuto |
|---------|-----------|
| **Statistiche descrittive** | Layer e campo, tabella delle statistiche con la lettura in parole, istogramma |
| **Variogramma** | Modello, nugget, sill, range, RMSE, distanza massima, interpretazione, grafico |
| **Kriging e cross-validation** | Metodo, risoluzione, dimensioni della griglia, metriche di cross-validation, grafico |
| **Pattern recognition** | Layer analizzati, gruppi con il numero di punti, grafico |
| **Nuovi punti di campionamento** | Criterio, layer, tabella delle coordinate |

Ogni sezione contiene l'**ultima** analisi del suo tipo eseguita nella sessione.

### Generazione del report

1. Eseguire le analisi desiderate nelle altre schede
2. Aprire la scheda **Report** e lasciare spuntate le sezioni da includere (sono spuntate per default)
3. Fare clic su **«Salva report HTML»** oppure su **«Salva report PDF»** e scegliere il nome del file

Al salvataggio il pannello mostra anche un'anteprima del report senza grafici; la nota «Anteprima: i grafici interattivi sono inclusi nel file HTML salvato.» ricorda dove si trovano.


<!-- IMAGE: Report HTML di GeoArchaeo aperto nel browser -->
> **Fig. 10**: Un report HTML di GeoArchaeo con i grafici interattivi, aperto nel browser

### Esportazione

| Formato | Contenuto | Note |
|---------|-----------|------|
| **HTML** (`geoarchaeo_report.html`) | Testo, tabelle e **grafici interattivi** | Il file è autonomo (la libreria dei grafici è inclusa, funziona anche senza rete) e si apre subito nel browser |
| **PDF** (`geoarchaeo_report.pdf`) | Testo e tabelle, **senza grafici** | Se il PDF non si crea, salvare il report HTML e stamparlo in PDF dal browser |

Se non è stata eseguita nessuna analisi compare «Nessuna analisi disponibile: esegui prima almeno un'analisi.»; se nessuna sezione è spuntata, «Seleziona almeno una sezione».

---

## Flusso di lavoro operativo

Un esempio completo con i dati di esempio inclusi nel modulo.

### Passo 1: Preparazione dei dati

1. Aprire GeoArchaeo dalla barra degli strumenti di PyArchInit
2. Fare clic su **«Carica dati di esempio»** e confermare con **OK** (vengono caricati i GeoPackage e i GeoJSON)
3. Nel gruppo «Dati di input» scegliere il layer `villa_ceramica` e il campo `ceramic_count`
4. Controllare il riepilogo: 500 punti validi su 500, CRS EPSG:32633

### Passo 2: Esplorazione dei dati

1. Scheda **Dati** → **«Calcola statistiche»**
2. Leggere asimmetria e valori anomali; con una forte asimmetria a destra valutare una trasformazione logaritmica

### Passo 3: Analisi del variogramma

1. Scheda **Variogramma** → **«Auto»** per la distanza massima, modello **«Sferico (consigliato)»** → **«Calcola variogramma»**
2. Ripetere con **«Esponenziale»** e confrontare l'RMSE del fit
3. Facoltativo: ricalcolare con **«Verifica anisotropia (variogrammi direzionali)»**
4. Ricalcolare per ultimo il modello scelto e annotare nugget, sill e range

### Passo 4: Interpolazione

1. Scheda **Kriging**: verificare la riga «Variogramma disponibile … ✓»
2. Lasciare la risoluzione proposta oppure impostare 1 (metro)
3. **«Esegui kriging»**
4. Esaminare i raster `Kriging_ceramic_count` e `Kriging_ceramic_count_incertezza` e i valori di R² e MSDR

### Passo 5: Pattern e campionamento (facoltativi)

1. Scheda **Pattern (ML)**: nell'elenco lasciare selezionato solo `necropoli`, metodo DBSCAN → **«Avvia pattern recognition»**; il layer `Gruppi_ML` mostra i gruppi di tombe e i punti isolati
2. In alto scegliere il layer `ricognizione_survey` (campo `densita_mq`); scheda **Campionamento**: area di studio `area_studio`, 10 punti, criterio «Copertura (maximin)» → **«Calcola nuovi punti»**

### Passo 6: Report

1. Scheda **Report**: lasciare spuntate le sezioni disponibili
2. **«Salva report HTML»**: il report si apre nel browser con i grafici interattivi
3. Esportare i raster e i layer temporanei che si vogliono conservare

---

## Risoluzione dei problemi

### Problemi comuni

| Problema | Causa | Soluzione |
|----------|-------|-----------|
| «Nessun layer di punti nel progetto: caricane uno o usa i dati di esempio.» | Nel progetto non ci sono layer di punti | Aggiungere un layer di punti o usare **«Carica dati di esempio»** |
| «Il layer non ha campi numerici…» | Il campo da analizzare è di tipo testo | Convertirlo in numero con il Calcolatore di campi |
| «Servono almeno 5 punti con valore valido (trovati …)» | Troppi valori NULL o non numerici | Controllare la tabella attributi o scegliere un altro campo |
| Avviso «CRS geografico (gradi)» | Il layer non è in un CRS proiettato | Riproiettare il layer, per esempio in UTM, e ripetere l'analisi |
| Errore «No point pairs within the maximum distance…» | Distanza massima del variogramma troppo piccola | Aumentare **«Distanza massima:»** o usare **«Auto»** |
| «Coppie insufficienti per i variogrammi direzionali.» | Troppe poche coppie per direzione | Aumentare la distanza massima o rinunciare alla verifica dell'anisotropia |
| Kriging lento, richiesta di conferma o «Memoria insufficiente: aumenta la dimensione della cella.» | Griglia con troppe celle | Aumentare **«Risoluzione cella:»** |
| R² basso nella cross-validation | Poca correlazione spaziale o troppo rumore | Considerare la mappa solo indicativa e consultare il raster dell'incertezza |
| DBSCAN mette quasi tutti i punti in «Isolati / rumore» | Densità uniforme o troppe variabili | Provare K-Means o ridurre i campi numerici |
| «Machine Learning features not available. Please install scikit-learn.» | Manca scikit-learn | Installare scikit-learn nell'ambiente Python di QGIS |
| «Plotly visualization not available. Please install plotly.» | Manca Plotly | Installare plotly nell'ambiente Python di QGIS |
| Grafico solo come immagine statica | QtWebEngine non disponibile | Usare **«Apri grafico interattivo nel browser»** |
| «Impossibile creare il PDF…» | Errore nella stampa del PDF | Salvare il report HTML e stamparlo dal browser |
| Pannello non visibile | Pannello chiuso | Riaprirlo dalla barra degli strumenti o dal menu pyArchInit: i risultati della sessione sono ancora lì |

### Errori frequenti

- **«Un'analisi è già in corso: attendi che finisca o annullala.»**: attendere la fine del calcolo o premere «Annulla»
- **«Analisi annullata»**: l'analisi è stata interrotta con «Annulla» e non ha prodotto risultati
- **«Seleziona almeno un layer»** (scheda Pattern): selezionare almeno un layer nell'elenco
- **«Seleziona il layer dei punti esistenti (in alto)»** (scheda Campionamento): scegliere il layer nel gruppo «Dati di input»
- **«Seleziona un layer di punti e un campo numerico (in alto nel pannello)»**: completare la scelta nel gruppo «Dati di input»

### Prestazioni

- Le analisi girano in un **thread in background**: QGIS resta utilizzabile e si può annullare il calcolo
- Il variogramma usa al massimo 3000 punti (sottocampione casuale), la cross-validation al massimo 200
- Il kriging usa i 20 punti più vicini a ogni cella: il tempo dipende soprattutto dal numero di celle
- La griglia è limitata a 500 × 500 celle; oltre 40.000 celle il pannello chiede conferma
- Con dataset grandi (per esempio i 4800 punti di `geofisica_survey`) aumentare la dimensione della cella

---

## Note tecniche

### Versione e origine

- Il modulo `modules/geoarchaeo/` è allineato a **GeoArchaeo 1.3.1**, il plugin autonomo di Enzo Cocca (github.com/enzococca/GeoArchaeo)
- In PyArchInit è integrato il solo pannello: il provider Processing di GeoArchaeo (co-kriging, kriging spazio-temporale, kriging a blocchi, analisi composizionale, Random Forest) **non** viene registrato
- Il modulo è compatibile con QGIS 3 (Qt5) e QGIS 4 (Qt6)

### Dipendenze

| Libreria | Utilizzo |
|----------|----------|
| **NumPy** | Calcoli numerici |
| **SciPy** | Fit dei modelli di variogramma, ricerca dei vicini (KD-tree), statistiche |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, componenti principali (necessaria per la scheda Pattern) |
| **Plotly** | Grafici interattivi nel pannello e nel report HTML |
| **Matplotlib** | Anteprime statiche dei grafici quando QtWebEngine non è disponibile |
| **QtWebEngine** (facoltativo) | Grafici interattivi direttamente nel pannello |
| **threadpoolctl** (facoltativo) | Limita i thread di calcolo durante le analisi in background |
| **GDAL** | Scrittura dei raster GeoTIFF (incluso in QGIS) |

### Sistemi di riferimento

- Le distanze (distanza massima, range, risoluzione della cella) sono espresse nelle **unità del CRS del layer di punti**
- Usare un **CRS proiettato** in metri: con un CRS geografico il riepilogo avvisa e variogramma e kriging chiedono conferma
- I raster del kriging e i layer creati usano il CRS del layer di punti (nella scheda Pattern, quello del primo layer selezionato)
- L'area di studio viene riproiettata automaticamente nel CRS dei punti

### Layer e file prodotti

| Prodotto | Tipo | Dove si trova |
|----------|------|---------------|
| `Kriging_<campo>`, `Kriging_<campo>_incertezza` | Raster GeoTIFF (compressione LZW) | Cartella temporanea del sistema |
| `Gruppi_ML` / `Anomalie_ML` | Layer di punti temporaneo (in memoria) | Solo nel progetto aperto |
| `Nuovi_punti_campionamento` | Layer di punti temporaneo (in memoria) | Solo nel progetto aperto |
| Report | HTML o PDF | Percorso scelto al salvataggio |

Raster e layer temporanei vanno esportati (menu contestuale del layer → **Esporta**) per non perderli alla chiusura del progetto. I nomi dei layer seguono la lingua del pannello al momento del calcolo.

### Impostazioni

- La lingua del pannello è salvata nelle impostazioni di QGIS (chiave `GeoArchaeo/language`)
- I risultati restano in memoria finché QGIS è aperto: chiudere il pannello non li cancella

---

> **Nota**: GeoArchaeo è in costante sviluppo. Per segnalare bug o suggerire miglioramenti, utilizzare il sistema di issue tracking del progetto PyArchInit su GitHub.
