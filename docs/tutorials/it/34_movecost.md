# PyArchInit - MoveCost - Analisi Percorsi di Minor Costo

## Indice

1. [Introduzione](#introduzione)
2. [Accesso allo Strumento](#accesso-allo-strumento)
3. [Prerequisiti](#prerequisiti)
4. [Interfaccia Utente](#interfaccia-utente)
5. [Scheda Algoritmi](#scheda-algoritmi)
6. [Scheda Risultati](#scheda-risultati)
7. [Scheda Esportazione](#scheda-esportazione)
8. [Scheda Impostazioni](#scheda-impostazioni)
9. [Flusso di Lavoro Operativo](#flusso-di-lavoro-operativo)
10. [Risoluzione dei Problemi](#risoluzione-dei-problemi)
11. [Note Tecniche](#note-tecniche)

---

## Introduzione

**MoveCost** e uno strumento autonomo di PyArchInit per l'analisi dei percorsi di minor costo (Least-Cost Path Analysis, LCPA) basato su script R. L'analisi dei percorsi di minor costo e una metodologia fondamentale in archeologia del paesaggio che consente di modellare i percorsi piu probabili tra localita, tenendo conto della topografia del terreno e del costo energetico del movimento.

### Storia

In precedenza, la funzionalita MoveCost era integrata direttamente nella scheda Sito (Site form) di PyArchInit. A partire dalla versione corrente, MoveCost e stato estratto come **strumento di analisi indipendente**, accessibile tramite un QDialog dedicato. Questa separazione offre diversi vantaggi:

- **Interfaccia dedicata**: Un dialogo con 4 schede organizzate per funzione
- **Migliore organizzazione**: Algoritmi, risultati, esportazione e impostazioni ben separati
- **Accesso rapido**: Disponibile dalla barra degli strumenti senza aprire la scheda Sito
- **Espandibilita**: Struttura modulare che facilita l'aggiunta di nuovi algoritmi

### Cos'e l'Analisi dei Percorsi di Minor Costo?

L'analisi dei percorsi di minor costo calcola il percorso ottimale tra due o piu punti su una superficie di costo derivata da un modello digitale del terreno (DTM). Il costo del movimento dipende dalla pendenza del terreno ed e calcolato utilizzando funzioni di costo anisotropiche che tengono conto della direzione del movimento (salita vs discesa).

<!-- IMAGE: Esempio di percorso di minor costo su DTM -->
> **Fig. 1**: Esempio di percorso di minor costo calcolato su un modello digitale del terreno

---

## Accesso allo Strumento

### Dalla Barra degli Strumenti

1. Individuare il pulsante **Strumenti di Analisi** (Analysis Tools) nella barra degli strumenti di PyArchInit -- e un pulsante a discesa con un'icona di grafico/analisi
2. Fare clic sulla freccia del menu a discesa
3. Selezionare **MoveCost** dal menu

<!-- IMAGE: Pulsante Analysis Tools nella toolbar -->
> **Fig. 2**: Il pulsante Analysis Tools nella barra degli strumenti di PyArchInit con il menu a discesa aperto

### Finestra di Dialogo

Al clic, si apre un **QDialog** modale con quattro schede:

```
+-----------------------------------------------------------+
|  MoveCost - Least-Cost Path Analysis                       |
+-----------------------------------------------------------+
| [Algoritmi] | [Risultati] | [Esportazione] | [Impostaz.] |
+-----------------------------------------------------------+
|                                                           |
|              (Contenuto della scheda attiva)               |
|                                                           |
+-----------------------------------------------------------+
|                              [Chiudi]                      |
+-----------------------------------------------------------+
```

---

## Prerequisiti

Prima di utilizzare MoveCost, verificare che i seguenti componenti siano installati e configurati:

### 1. R (Linguaggio Statistico)

| Requisito | Dettaglio |
|-----------|-----------|
| **Software** | R (versione >= 4.0 consigliata) |
| **Download** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verifica** | Aprire un terminale e digitare `R --version` |

### 2. Pacchetto R `movecost`

Installare il pacchetto dall'interno di R:

```r
install.packages("movecost")
```

Dipendenze principali installate automaticamente: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Requisito | Dettaglio |
|-----------|-----------|
| **Plugin** | Processing R Provider |
| **Installazione** | QGIS > Plugin > Gestisci e Installa Plugin > Cerca "Processing R Provider" |
| **Configurazione** | Impostazioni di Processing > Provider > R > Percorso cartella R |

### 4. Dati di Input

- **DTM/DEM**: Un raster del modello digitale del terreno nell'area di studio
- **Layer di punti**: Punti di origine e destinazione per l'analisi
- **Layer di poligoni**: (Opzionale) Per le varianti "by polygon" degli algoritmi

### Verifica Rapida dei Prerequisiti

```
+-------------------------------------------+
| Checklist Prerequisiti                     |
+-------------------------------------------+
| [x] R installato e nel PATH              |
| [x] Pacchetto movecost installato in R   |
| [x] Processing R Provider attivo in QGIS |
| [x] DTM caricato nel progetto QGIS       |
| [x] Layer punti con origini/destinazioni  |
+-------------------------------------------+
```

---

## Interfaccia Utente

Il dialogo MoveCost e organizzato in **4 schede** (tab), ciascuna con una funzione specifica.

### Panoramica delle Schede

| Scheda | Icona | Funzione |
|--------|-------|----------|
| **Algoritmi** | Ingranaggio | Selezionare e lanciare i 14 algoritmi di analisi |
| **Risultati** | Grafico | Visualizzare statistiche dei costi e grafici R |
| **Esportazione** | Disco | Esportare risultati in CSV, PDF o HTML |
| **Impostazioni** | Chiave inglese | Configurare script R, lingua, organizzazione layer |

<!-- IMAGE: Panoramica del dialogo MoveCost con le 4 schede -->
> **Fig. 3**: Il dialogo MoveCost con le quattro schede visibili

---

## Scheda Algoritmi

La scheda **Algoritmi** e il cuore dello strumento MoveCost. Contiene **14 algoritmi** basati su script R, organizzati in **3 gruppi funzionali**.

### Gruppo 1: Superficie di Costo e Percorsi

Algoritmi per il calcolo della superficie di costo accumulata e dei percorsi di minor costo.

| Algoritmo | Descrizione |
|-----------|-------------|
| **movecost** | Calcola la superficie di costo accumulata anisotropica dipendente dalla pendenza e i percorsi di minor costo da un punto di origine |
| **movecost by polygon** | Come sopra, ma utilizzando un'area poligonale per definire l'estensione del DTM |
| **movebound** | Calcola i confini di costo di spostamento dipendenti dalla pendenza attorno a localita puntuali |
| **movebound by polygon** | Come sopra, ma utilizzando un poligono per definire l'estensione |

### Gruppo 2: Analisi di Corridoi e Reti

Algoritmi per l'analisi di corridoi di costo e reti di percorsi ottimali.

| Algoritmo | Descrizione |
|-----------|-------------|
| **movecorr** | Calcola il corridoio di minor costo tra localita puntuali |
| **movecorr by polygon** | Come sopra, ma utilizzando un poligono |
| **movealloc** | Calcola l'allocazione di costo di spostamento dipendente dalla pendenza rispetto alle origini |
| **movealloc by polygon** | Come sopra, ma utilizzando un poligono |
| **movenetw** | Calcola la rete di percorsi di minor costo tra piu punti |
| **movenetw by polygon** | Come sopra, ma utilizzando un poligono |

### Gruppo 3: Confronto e Classificazione

Algoritmi per confrontare funzioni di costo e classificare destinazioni.

| Algoritmo | Descrizione |
|-----------|-------------|
| **movecomp** | Confronta percorsi di minor costo generati utilizzando diverse funzioni di costo |
| **movecomp by polygon** | Come sopra, ma utilizzando un poligono |
| **moverank** | Classifica le destinazioni in base al costo di spostamento da un'origine |
| **moverank by polygon** | Come sopra, ma utilizzando un poligono |

### Come Lanciare un Algoritmo

1. Selezionare l'algoritmo desiderato dalla lista
2. L'interfaccia di Processing di QGIS si apre con i parametri specifici dell'algoritmo
3. Configurare i parametri di input:
   - **DTM/DEM**: Selezionare il raster del terreno
   - **Punto/i di origine**: Selezionare il layer di punti
   - **Poligono** (se variante "by polygon"): Selezionare l'area di studio
   - **Funzione di costo**: Scegliere tra le funzioni disponibili (Tobler, Minetti, ecc.)
4. Fare clic su **Esegui**
5. I risultati vengono aggiunti automaticamente al progetto QGIS

<!-- IMAGE: Scheda Algoritmi con i 3 gruppi -->
> **Fig. 4**: La scheda Algoritmi con i tre gruppi di algoritmi evidenziati

<!-- IMAGE: Interfaccia Processing per un algoritmo movecost -->
> **Fig. 5**: L'interfaccia di QGIS Processing per l'algoritmo movecost con i parametri configurati

### Varianti "by polygon"

Le varianti "by polygon" di ciascun algoritmo consentono di:
- **Limitare l'area di analisi** a una regione specifica
- **Ridurre i tempi di calcolo** lavorando su un DTM ritagliato
- **Focalizzare l'analisi** su un'area di interesse archeologico

---

## Scheda Risultati

La scheda **Risultati** consente di visualizzare i risultati delle analisi eseguite.

### Riepilogo dei Costi (Cost Summary)

Un'area di testo (QTextEdit) mostra le statistiche riassuntive dei layer di costo generati:

| Statistica | Descrizione |
|------------|-------------|
| **Minimo** | Valore minimo di costo nella superficie |
| **Massimo** | Valore massimo di costo nella superficie |
| **Media** | Valore medio di costo |
| **Dev. Standard** | Deviazione standard dei valori di costo |

```
+---------------------------------------------------+
| Riepilogo Costi                                    |
+---------------------------------------------------+
| Layer: movecost_accumulated_cost                   |
| Minimo: 0.00                                       |
| Massimo: 15234.56                                  |
| Media: 4521.89                                     |
| Dev. Standard: 2103.45                             |
|                                                    |
| Layer: movecost_back_link                          |
| Minimo: 0.00                                       |
| Massimo: 8.00                                      |
| Media: 4.12                                        |
+---------------------------------------------------+
```

### Visualizzatore Grafici R (R Plot Viewer)

Il visualizzatore grafici R mostra l'ultimo grafico generato dagli script R:

| Funzione | Descrizione |
|----------|-------------|
| **Visualizzazione automatica** | Mostra l'ultimo grafico R dalla directory temporanea |
| **Aggiorna** | Ricarica l'ultimo grafico disponibile |
| **Salva** | Salva il grafico corrente in un file immagine (PNG, JPG) |
| **Selezione manuale** | Permette di aprire un grafico R specifico da qualsiasi posizione |

<!-- IMAGE: Scheda Risultati con riepilogo costi e grafico R -->
> **Fig. 6**: La scheda Risultati che mostra il riepilogo statistico dei costi e un grafico R

### Posizione dei Grafici R

I grafici R vengono salvati nelle directory temporanee di QGIS/R. Il visualizzatore cerca automaticamente nelle seguenti posizioni:

- Directory temporanea di QGIS Processing
- Directory temporanea di R (`tempdir()`)
- Cartella di output specificata dall'utente

---

## Scheda Esportazione

La scheda **Esportazione** offre tre opzioni per esportare i risultati dell'analisi.

### Esporta Tabella Costi (CSV)

Esporta le statistiche dei layer di costo in un file CSV:

1. Fare clic su **Esporta Tabella Costi**
2. Selezionare la posizione e il nome del file
3. Il file CSV contiene: nome layer, minimo, massimo, media, deviazione standard

| Colonna | Descrizione |
|---------|-------------|
| `layer_name` | Nome del layer di costo |
| `min_value` | Valore minimo |
| `max_value` | Valore massimo |
| `mean_value` | Valore medio |
| `std_dev` | Deviazione standard |

### Esporta Report (PDF)

> **Nota**: Questa funzionalita e attualmente in fase di sviluppo (stub). Sara disponibile in una versione futura.

### Esporta Report (HTML)

Genera un report HTML completo e stilizzato che include:

- **Intestazione** con titolo del progetto e data
- **Parametri dell'analisi** utilizzati
- **Statistiche dei layer** di costo in formato tabellare
- **Grafici R** incorporati come immagini
- **Stile CSS** integrato per una presentazione professionale

1. Fare clic su **Esporta Report (HTML)**
2. Selezionare la posizione e il nome del file
3. Il report si apre automaticamente nel browser predefinito

<!-- IMAGE: Esempio di report HTML esportato -->
> **Fig. 7**: Un esempio di report HTML generato da MoveCost con statistiche e grafici

---

## Scheda Impostazioni

La scheda **Impostazioni** consente di configurare lo strumento MoveCost.

### Installa Script R

| Funzione | Descrizione |
|----------|-------------|
| **Installa Script R** | Copia gli script R di movecost nella directory di processing di QGIS |

Questa operazione e necessaria alla **prima configurazione** o dopo un aggiornamento del plugin. Gli script vengono copiati nella cartella degli script R del provider di Processing:

```
{QGIS_HOME}/processing/rscripts/
```

### Selezione Lingua

MoveCost supporta **5 lingue** per l'interfaccia:

| Lingua | Codice |
|--------|--------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

La lingua selezionata si applica a:
- Etichette dell'interfaccia del dialogo
- Messaggi di stato e di errore
- Intestazioni delle tabelle dei risultati

### Organizzazione Layer

| Funzione | Descrizione |
|----------|-------------|
| **Organizza Layer** | Organizza e applica stili automaticamente ai layer di output di movecost |

Questa funzione:
1. Raggruppa i layer di output in gruppi logici nel pannello Layer di QGIS
2. Applica stili di colorazione predefiniti (rampe di colore per superfici di costo)
3. Rinomina i layer con nomi descrittivi

### Documentazione

| Funzione | Descrizione |
|----------|-------------|
| **Aiuto** | Apre la documentazione inline dello strumento |

<!-- IMAGE: Scheda Impostazioni con tutte le opzioni -->
> **Fig. 8**: La scheda Impostazioni di MoveCost con le opzioni di configurazione

---

## Flusso di Lavoro Operativo

### Esempio Passo-Passo: Calcolo di un Percorso di Minor Costo

Questo esempio mostra come calcolare un percorso di minor costo tra un insediamento e una fonte d'acqua.

### Passo 1: Preparazione dei Dati

```
1. Caricare il DTM dell'area di studio nel progetto QGIS
2. Creare un layer di punti con:
   - Punto di origine (insediamento)
   - Punto/i di destinazione (fonte d'acqua)
3. Verificare che il sistema di riferimento sia coerente
```

### Passo 2: Verifica dei Prerequisiti

```
1. Aprire MoveCost dalla barra degli strumenti
2. Andare alla scheda Impostazioni
3. Fare clic su "Installa Script R" (se prima volta)
4. Verificare che non vengano segnalati errori
```

### Passo 3: Esecuzione dell'Analisi

```
1. Tornare alla scheda Algoritmi
2. Selezionare "movecost" dal Gruppo 1
3. Nella finestra di Processing:
   - DTM: selezionare il raster del terreno
   - Origine: selezionare il punto dell'insediamento
   - Destinazione: selezionare il punto della fonte d'acqua
   - Funzione di costo: Tobler (consigliata per default)
4. Fare clic su Esegui
5. Attendere il completamento dell'elaborazione
```

### Passo 4: Analisi dei Risultati

```
1. Passare alla scheda Risultati
2. Consultare il Riepilogo dei Costi per le statistiche
3. Esaminare il grafico R per la visualizzazione
4. Nel canvas di QGIS, osservare:
   - La superficie di costo accumulata (raster colorato)
   - Il percorso di minor costo (linea vettoriale)
```

### Passo 5: Esportazione

```
1. Passare alla scheda Esportazione
2. Esportare la tabella costi in CSV per analisi ulteriori
3. Generare il report HTML per la documentazione
4. Salvare il grafico R dalla scheda Risultati
```

### Passo 6: Organizzazione

```
1. Tornare alla scheda Impostazioni
2. Fare clic su "Organizza Layer" per ordinare i risultati
3. I layer vengono raggruppati e stilizzati automaticamente
```

<!-- IMAGE: Flusso di lavoro completo con screenshot annotati -->
> **Fig. 9**: Il flusso di lavoro completo da preparazione dati a risultati finali

---

## Risoluzione dei Problemi

### R non trovato

**Sintomo**: Messaggio di errore "R non trovato" o "R is not installed"

**Soluzioni**:
1. Verificare che R sia installato: aprire un terminale e digitare `R --version`
2. Verificare il percorso di R nelle impostazioni di Processing:
   - **QGIS** > **Impostazioni** > **Opzioni** > **Processing** > **Provider** > **R**
   - Impostare il **percorso della cartella R** correttamente
3. Su macOS, R potrebbe trovarsi in `/Library/Frameworks/R.framework/Resources/`
4. Su Windows, tipicamente in `C:\Program Files\R\R-4.x.x\`
5. Su Linux, verificare con `which R`

### Script R mancanti

**Sintomo**: Gli algoritmi non appaiono nel toolbox di Processing

**Soluzioni**:
1. Aprire MoveCost > Impostazioni > fare clic su **Installa Script R**
2. Riavviare QGIS dopo l'installazione degli script
3. Verificare che il Processing R Provider sia attivo:
   - **QGIS** > **Plugin** > **Gestisci e Installa Plugin** > Verificare "Processing R Provider"
4. Controllare la cartella degli script R: `{QGIS_HOME}/processing/rscripts/`

### Grafici R non visualizzati

**Sintomo**: La scheda Risultati non mostra alcun grafico

**Soluzioni**:
1. Fare clic su **Aggiorna** nella scheda Risultati
2. Utilizzare **Selezione manuale** per navigare alla cartella dei grafici
3. Verificare che l'analisi sia stata completata con successo
4. Controllare le directory temporanee:
   - macOS/Linux: `/tmp/` o `$TMPDIR`
   - Windows: `%TEMP%`
5. Alcuni algoritmi potrebbero non generare grafici

### Pacchetto movecost non installato in R

**Sintomo**: Errore "there is no package called 'movecost'"

**Soluzioni**:
1. Aprire R o RStudio
2. Eseguire: `install.packages("movecost")`
3. Verificare: `library(movecost)` -- non deve dare errori
4. Se ci sono problemi di dipendenze: `install.packages("movecost", dependencies = TRUE)`

### Analisi molto lenta

**Sintomo**: L'elaborazione richiede tempi molto lunghi

**Soluzioni**:
1. Utilizzare le varianti **"by polygon"** per limitare l'area di calcolo
2. Ridurre la risoluzione del DTM (ricampionamento)
3. Verificare le dimensioni del DTM:
   - DTM molto grandi (>10000x10000 pixel) richiedono tempi significativi
   - Ritagliare il DTM all'area di interesse prima dell'analisi
4. Chiudere altre applicazioni per liberare memoria RAM

### Errore di proiezione / CRS

**Sintomo**: Risultati incoerenti o errore di sistema di riferimento

**Soluzioni**:
1. Verificare che DTM e layer di punti abbiano lo **stesso CRS**
2. Utilizzare un **CRS proiettato** (metriche), non geografico
3. CRS consigliati: UTM (es. EPSG:32632 per Italia centro)
4. Riproiettare i layer se necessario prima dell'analisi

---

## Note Tecniche

### Architettura dello Strumento

MoveCost e implementato come un **QDialog** indipendente (`MoveCostDialog`) che:
- Si interfaccia con QGIS Processing Framework per l'esecuzione degli algoritmi R
- Legge i risultati dai layer caricati nel progetto
- Gestisce la visualizzazione dei grafici R tramite QLabel/QPixmap
- Genera report HTML utilizzando template predefiniti

### File Sorgente

| File | Descrizione |
|------|-------------|
| `tabs/MoveCost.py` | Dialogo principale e logica dell'interfaccia |
| `gui/ui/MoveCost.ui` | Layout dell'interfaccia Qt Designer |
| `resources/r_scripts/` | Script R per gli algoritmi movecost |

### Funzioni di Costo Supportate

Il pacchetto R `movecost` supporta diverse funzioni di costo anisotropiche:

| Funzione | Autore | Descrizione |
|----------|--------|-------------|
| **Tobler** | Tobler (1993) | Funzione di costo escursionistica classica |
| **Minetti** | Minetti et al. (2002) | Basata sul costo metabolico |
| **Herzog** | Herzog (2010) | Variante modificata |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Modello energetico |
| **Altre** | Vari | Consultare la documentazione del pacchetto R |

### Riferimenti Bibliografici

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilita

| Componente | Versione Minima |
|------------|-----------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Pacchetto movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Video Tutorial

### MoveCost - Analisi Percorsi di Minor Costo
`[Placeholder: video_movecost.mp4]`

**Contenuti**:
- Configurazione di R e del pacchetto movecost
- Installazione degli script R in QGIS
- Esecuzione dell'algoritmo movecost base
- Visualizzazione dei risultati e grafici R
- Esportazione dei report

**Durata prevista**: 20-25 minuti

---

*Documentazione PyArchInit - MoveCost*
*Versione: 5.0.x*
*Ultimo aggiornamento: Febbraio 2026*
