# Tutorial 25: Time Manager (GIS Time Controller)

## Introduzione

Il **Time Manager** (GIS Time Controller) e uno strumento avanzato per visualizzare la sequenza stratigrafica nel tempo. Permette di "navigare" attraverso i livelli stratigrafici usando un controllo temporale, visualizzando progressivamente le US dalla piu antica alla piu recente (la formazione del sito).

### Funzionalita Principali

- Visualizzazione progressiva dei livelli stratigrafici
- Controllo tramite dial/slider
- Modalita cumulativa o singolo livello
- Stampa automatica delle tavole dell'atlante, una per livello
- Integrazione con Matrix di Harris

## Accesso

### Dal Menu
**PyArchInit** → **Time Manager**

### Prerequisiti

- Layer con campo `order_layer` (indice stratigrafico)
- US con order_layer compilato
- Layer caricati in QGIS

## Interfaccia

### Pannello Principale

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Layer disponibili:                                |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] altro_layer                                  |
+--------------------------------------------------+
|              [Dial Circolare]                    |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Livello: [SpinBox: 0-N]                 |
+--------------------------------------------------+
| [x] Modalita Cumulativa (mostra <= livello)     |
+--------------------------------------------------+
| [ ] Visualizza matrix                            |
| [Atlas Stampa Tavole Periodo]                    |
| [Arresta processo stampa]                        |
+--------------------------------------------------+
| [Preview Matrix/Immagine]                        |
+--------------------------------------------------+
```

### Controlli

| Controllo | Funzione |
|-----------|----------|
| Checkbox Layer | Seleziona layer da controllare |
| Dial | Naviga tra i livelli (rotazione) |
| SpinBox | Inserimento diretto livello |
| Modalita Cumulativa | Mostra tutti i livelli fino al selezionato |
| Visualizza matrix | Visualizza Matrix di Harris sincronizzato |

## Campo order_layer

### Cos'e order_layer?

Il campo `order_layer` definisce l'ordine stratigrafico di visualizzazione:
- **0** = Livello piu antico (profondo)
- **N** = Livello piu recente (superficiale)

E la convenzione dell'**Ordine stratigrafico** con «Ordine: Antico → Recente» attivo (impostazione predefinita, vedi Tutorial 03): se l'ordinamento e stato calcolato al contrario, il Time Manager e la mappa mostrano la sequenza capovolta.

### Compilazione order_layer

Nella Scheda US, tab **Help** → **Tool Box**, il pulsante **Ordine stratigrafico** calcola `order_layer` dai rapporti stratigrafici (vedi Tutorial 03); il valore della US corrente compare nel campo sotto il pulsante. Regole:
1. 0 alle US piu antiche, valori crescenti verso le piu recenti (in superficie)
2. US contemporanee possono avere lo stesso valore
3. Seguire la sequenza del Matrix

### Esempio

| US | order_layer | Descrizione |
|----|-------------|-------------|
| US001 | 4 | Humus superficiale |
| US002 | 3 | Strato arativo |
| US003 | 2 | Crollo |
| US004 | 1 | Piano d'uso |
| US005 | 0 | Fondazione |

Dalla 5.13.19-alpha i layer US e USM che pyArchInit carica sulla mappa (vedi Tutorial 14, *Scelta dello Stile*) vengono disegnati nello stesso ordine usato dal Time Manager: per cronologia del periodo, poi per `order_layer` (0 = piu antico), cosi le unita piu recenti stanno sopra.

## Modalita di Visualizzazione

### Modalita Singolo Livello

Checkbox **NON** attivo:
- Mostra SOLO le US del livello selezionato
- Utile per isolare singoli strati
- Visualizzazione "a fette"

### Modalita Cumulativa

Checkbox **ATTIVO**:
- Mostra tutte le US dal livello 0 (piu antico) a quello selezionato
- Mostra la formazione del sito, dalle US piu antiche alle piu recenti
- Visualizzazione piu realistica

## Integrazione Matrix

### Visualizzazione Sincronizzata

Con checkbox **"Visualizza matrix"** attivo:
- Il Matrix di Harris appare nel pannello
- Si aggiorna in sincrono con il livello
- Evidenzia le US del livello corrente

### Generazione Immagini

Il Time Manager puo generare:
- Una tavola per ogni livello, impaginata con il modello di layout scelto (immagine JPG)
- La Matrix di Harris di quel livello dentro la tavola, se **Visualizza matrix** è attivo

## Stampa delle tavole

### Processo

1. Selezionare layer da includere
2. Attivare **Visualizza matrix** se la Matrix deve comparire nelle tavole (altrimenti l'immagine della Matrix del modello viene nascosta)
3. Cliccare **Atlas Stampa Tavole Periodo**
4. Nella finestra che si apre scegliere il modello di layout (vedi la nota «Quale template scegliere» in fondo) e confermare
5. Scegliere la cartella dove salvare le tavole
6. Rispondere alla domanda se aprire il Layout Designer per ritoccare il modello prima di cominciare
7. Attendere: una barra di avanzamento mostra la tavola in lavorazione e, a lavoro finito, un messaggio dice dove sono state salvate
8. Per fermare la generazione cliccare **Arresta processo stampa**: le tavole già scritte restano nella cartella

### Output

- Una `Tavola_N.jpg` per ogni livello (N è il valore di `order_layer`), nella cartella scelta: la mappa a quel livello, nella modalità attiva (cumulativa o singolo livello)
- Il titolo «Tavola N» e l'immagine della Matrix compaiono se il modello li prevede (la Matrix solo con **Visualizza matrix** attivo)
- I livelli in cui nessuna US ha la datazione compilata vengono saltati: nella sequenza dei file mancano quei numeri
- Con un modello a due pagine escono due immagini per livello, la seconda è `Tavola_N_2.jpg` (vedi la nota «Rendere adatto un modello qualunque» in fondo)

**Etichette della tavola.** Mentre genera le tavole dell'atlante, il Time Manager mette sui layer scelti le etichette della tavola — il numero dell'unità in un cerchio sulle US, la quota sui punti — e a generazione finita le toglie, rimettendo quelle che c'erano prima. Dalla 5.13.110-alpha le toglie comunque, anche se una tavola salta: prima, in quel caso, restavano sui layer del progetto e finivano nel file del progetto quando lo si salvava.

## Workflow Tipico

### 1. Preparazione

```
1. Aprire progetto QGIS con layer US
2. Verificare che order_layer sia compilato
3. Aprire Time Manager
```

### 2. Selezione Layer

```
1. Selezionare i layer da controllare
2. Di solito: pyunitastratigrafiche e/o _usm
```

### 3. Navigazione

```
1. Usare il dial o spinbox
2. Osservare cambiamento visualizzazione
3. Attivare/disattivare modalita cumulativa
```

### 4. Documentazione

```
1. Attivare "Visualizza matrix"
2. Stampare le tavole con "Atlas Stampa Tavole Periodo"
3. Controllare i file Tavola_N.jpg nella cartella scelta
```

## Templates di Layout

### Caricamento Template

Il Time Manager supporta template QGIS per:
- Layout di stampa personalizzati
- Intestazioni e legende
- Formati standard

### Template Disponibili

La finestra di scelta elenca i file `.qpt` trovati nella cartella del plugin, in `resources/dbfiles/` e in `~/pyarchinit_5/bin/profile/template/`:
- `layout_TimeManager`: il modello del Time Manager, con il titolo «Tavola N» e l'immagine della Matrix
- i modelli di stampa del profilo pyArchInit (per esempio i «Modello adArte…»)
- qualunque altro `.qpt`, scelto con il pulsante **Sfoglia...**

## Best Practices

### 1. order_layer

- Compilare PRIMA di usare Time Manager
- Usare valori consecutivi
- US contemporanee = stesso valore

### 2. Visualizzazione

- Iniziare dal livello 0 (piu antico)
- Procedere in ordine crescente
- Usare modalita cumulativa per presentazioni

### 3. Documentazione

- Catturare screenshot ai livelli significativi
- Documentare passaggi di fase
- Stampare le tavole per le relazioni (una per livello)

## Risoluzione Problemi

### Layer Non Visibili nella Lista

**Causa**: Layer senza campo order_layer

**Soluzione**:
- Aggiungere campo order_layer al layer
- Popolarlo con valori appropriati

### Nessun Cambiamento Visivo

**Cause**:
- order_layer non compilato
- Filtro non applicato

**Soluzioni**:
- Verificare valori order_layer nelle US
- Controllare che layer sia selezionato

### Dial Non Risponde

**Causa**: Nessun layer selezionato

**Soluzione**: Selezionare almeno un layer dalla lista

## Riferimenti

### File Sorgente
- `tabs/Gis_Time_controller.py` - Interfaccia principale
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Campo Database
- `us_table.order_layer` - Indice stratigrafico

---

## Video Tutorial

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Contenuti**:
- Configurazione order_layer
- Navigazione temporale
- Generazione video
- Integrazione Matrix

**Durata prevista**: 15-18 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../animations/pyarchinit_timemanager_animation.html)

---

## La matrice, dalla 5.13.44

Il Matrix del Time Manager non passa più da Graphviz. Lo disegna lo stesso impaginatore del pannello **Vedi la matrice**, dentro QGIS e senza sottoprocessi.

Cosa cambia per chi lo usa:

- **È immediato.** Sul sito di esempio (51 US, 81 rapporti) il disegno costa qualche millisecondo invece di circa tre decimi di secondo, e non ci sono più i processi `dot` e `tred` che ogni tanto restavano appesi. I periodi del sito si leggono **una volta sola**: prima li si rileggeva, con una query per ogni area e per ogni periodo, a ogni scatto della manopola.
- **Nell'atlante la matrice è vettoriale.** L'immagine inserita nella tavola è un SVG di qualche decina di KB invece di un JPEG di megabyte: si legge a qualunque scala e la tavola pesa meno.
- **È la stessa matrice** del pannello Extended Matrix: stesse fasce dei periodi, stessa simbologia, stessa riduzione delle ridondanze. Le frecce che **risalgono** le fasce — dove la stratigrafia contraddice la cronologia — sono disegnate in **rosso**.
- La matrice contiene solo le US visibili alla posizione corrente del cursore, come prima.

- Le US che **non sono visibili** alla posizione corrente ma che un rapporto cita entrano comunque nel disegno, **sbiadite**: senza di loro la sequenza sembrerebbe spezzata, e disegnate come le altre sembrerebbero sulla mappa.

> **Quale template scegliere.** Nella finestra di scelta i modelli sono marcati: **✓** ha il titolo «Tavola N» e l'immagine della matrice (è quello del Time Manager, `layout_TimeManager`), **•** ha solo la mappa — le tavole escono più spoglie ma escono — **✗** non ha nemmeno la mappa e non si può usare. Prima sceglierne uno senza i due elementi faceva tornare indietro il generatore senza dire niente, e le tavole non si vedevano.

> **Rendere adatto un modello qualunque.** I modelli generici si possono preparare: lo script `scripts/prepare_atlas_templates.py`, eseguito col Python di QGIS, scrive accanto a ognuno una copia col suffisso « + Time Manager» che ha il titolo e l'immagine della matrice su una **pagina nuova** — così non copre niente di quello che c'era. Gli originali non si toccano. Ogni livello produce allora due immagini: `Tavola_N.jpg` con la mappa e `Tavola_N_2.jpg` con la matrice.
