# Tutorial 25: Time Manager (GIS Time Controller)

## Introduzione

Il **Time Manager** (GIS Time Controller) e uno strumento avanzato per visualizzare la sequenza stratigrafica nel tempo. Permette di "navigare" attraverso i livelli stratigrafici usando un controllo temporale, visualizzando progressivamente le US dalla piu recente alla piu antica.

### Funzionalita Principali

- Visualizzazione progressiva dei livelli stratigrafici
- Controllo tramite dial/slider
- Modalita cumulativa o singolo livello
- Generazione automatica di immagini/video
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
|         Livello: [SpinBox: 1-N]                 |
+--------------------------------------------------+
| [x] Modalita Cumulativa (mostra <= livello)     |
+--------------------------------------------------+
| [ ] Mostra Matrix          [Stop] [Genera Video] |
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
| Mostra Matrix | Visualizza Matrix di Harris sincronizzato |

## Campo order_layer

### Cos'e order_layer?

Il campo `order_layer` definisce l'ordine stratigrafico di visualizzazione:
- **1** = Livello piu recente (superficiale)
- **N** = Livello piu antico (profondo)

### Compilazione order_layer

Nella Scheda US, campo **"Indice Stratigrafico"**:
1. Assegnare valori crescenti dalla superficie
2. US contemporanee possono avere stesso valore
3. Seguire la sequenza del Matrix

### Esempio

| US | order_layer | Descrizione |
|----|-------------|-------------|
| US001 | 1 | Humus superficiale |
| US002 | 2 | Strato arativo |
| US003 | 3 | Crollo |
| US004 | 4 | Piano d'uso |
| US005 | 5 | Fondazione |

## Modalita di Visualizzazione

### Modalita Singolo Livello

Checkbox **NON** attivo:
- Mostra SOLO le US del livello selezionato
- Utile per isolare singoli strati
- Visualizzazione "a fette"

### Modalita Cumulativa

Checkbox **ATTIVO**:
- Mostra tutte le US fino al livello selezionato
- Simula lo scavo progressivo
- Visualizzazione piu realistica

## Integrazione Matrix

### Visualizzazione Sincronizzata

Con checkbox **"Mostra Matrix"** attivo:
- Il Matrix di Harris appare nel pannello
- Si aggiorna in sincrono con il livello
- Evidenzia le US del livello corrente

### Generazione Immagini

Il Time Manager puo generare:
- Screenshot per ogni livello
- Sequenza di immagini
- Video time-lapse

## Generazione Video/Immagini

### Processo

1. Selezionare layer da includere
2. Configurare range livelli (min-max)
3. Cliccare **"Genera Video"**
4. Attendere elaborazione
5. Output in cartella designata

### Output

- Immagini PNG per ogni livello
- Opzionale: video MP4 compilato

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
1. Attivare "Mostra Matrix"
2. Generare screenshot significativi
3. Opzionale: generare video
```

## Templates di Layout

### Caricamento Template

Il Time Manager supporta template QGIS per:
- Layout di stampa personalizzati
- Intestazioni e legende
- Formati standard

### Template Disponibili

Nella cartella `resources/templates/`:
- Template base
- Template con Matrix
- Template per video

## Best Practices

### 1. order_layer

- Compilare PRIMA di usare Time Manager
- Usare valori consecutivi
- US contemporanee = stesso valore

### 2. Visualizzazione

- Iniziare da livello 1 (superficiale)
- Procedere in ordine crescente
- Usare modalita cumulativa per presentazioni

### 3. Documentazione

- Catturare screenshot ai livelli significativi
- Documentare passaggi di fase
- Generare video per relazioni

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
