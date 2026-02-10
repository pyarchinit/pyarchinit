# Tutorial 11: Matrix di Harris

## Introduzione

Il **Matrix di Harris** (o diagramma stratigrafico) e uno strumento fondamentale in archeologia per rappresentare graficamente le relazioni stratigrafiche tra le diverse Unita Stratigrafiche (US). PyArchInit genera automaticamente il Matrix di Harris a partire dai rapporti stratigrafici inseriti nelle schede US.

### Cos'e il Matrix di Harris?

Il Matrix di Harris e un diagramma che rappresenta:
- La **sequenza temporale** delle US (dal piu recente in alto al piu antico in basso)
- Le **relazioni fisiche** tra le US (copre/coperto da, taglia/tagliato da, si lega a)
- La **periodizzazione** dello scavo (raggruppamento per periodi e fasi)

### Tipi di Relazioni Rappresentate

| Relazione | Significato | Rappresentazione |
|-----------|-------------|------------------|
| Copre/Covered by | Sovrapposizione fisica | Linea continua verso il basso |
| Taglia/Cuts | Azione negativa (interfaccia) | Linea tratteggiata |
| Si lega a/Same as | Contemporaneita | Linea orizzontale bidirezionale |
| Riempie/Fills | Riempimento di taglio | Linea continua |
| Si appoggia a/Abuts | Appoggio strutturale | Linea continua |

## Accesso alla Funzione

### Dal Menu Principale
1. **PyArchInit** nella barra del menu
2. Selezionare **Matrix di Harris**

### Dalla Scheda US
1. Aprire la Scheda US
2. Tab **Map**
3. Pulsante **"Esporta Matrix"** o **"View Matrix"**

### Prerequisiti
- Database connesso correttamente
- US con rapporti stratigrafici compilati
- Periodizzazione definita (opzionale ma consigliato)
- Graphviz installato nel sistema

## Configurazione del Matrix

### Finestra di Impostazioni (Setting_Matrix)

Prima della generazione, appare una finestra di configurazione:

#### Tab Generale

| Campo | Descrizione | Valore Consigliato |
|-------|-------------|-------------------|
| DPI | Risoluzione dell'immagine | 150-300 |
| Mostra Periodi | Raggruppa US per periodo/fase | Si |
| Mostra Legenda | Includi legenda nel grafico | Si |

#### Tab Nodi "Ante/Post" (Relazioni Normali)

| Parametro | Descrizione | Opzioni |
|-----------|-------------|---------|
| Forma nodo | Forma geometrica | box, ellipse, diamond |
| Colore riempimento | Colore interno | white, lightblue, etc. |
| Stile | Aspetto bordo | solid, dashed |
| Spessore linea | Larghezza bordo | 0.5 - 2.0 |
| Tipo freccia | Punta della freccia | normal, diamond, none |
| Dimensione freccia | Grandezza punta | 0.5 - 1.5 |

#### Tab Nodi "Negative" (Tagli)

| Parametro | Descrizione | Opzioni |
|-----------|-------------|---------|
| Forma nodo | Forma geometrica | box, ellipse, diamond |
| Colore riempimento | Colore distintivo | gray, lightcoral |
| Stile linea | Aspetto connessione | dashed (tratteggiato) |

#### Tab Nodi "Contemporaneo"

| Parametro | Descrizione | Opzioni |
|-----------|-------------|---------|
| Forma nodo | Forma geometrica | box, ellipse |
| Colore riempimento | Colore distintivo | lightyellow, white |
| Stile linea | Aspetto connessione | solid |
| Freccia | Tipo connessione | none (bidirezionale) |

#### Tab Connessioni Speciali (">", ">>")

Per relazioni stratigrafiche speciali o connessioni documentative:

| Parametro | Descrizione |
|-----------|-------------|
| Forma | box, ellipse |
| Colore | lightgreen, etc. |
| Stile | solid, dashed |

## Tipi di Export

### 1. Export Matrix Standard

Genera il matrix base con:
- Tutti i rapporti stratigrafici
- Raggruppamento per periodo/fase
- Layout verticale (TB - Top to Bottom)

**Output**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Export Matrix 2ED (Esteso)

Versione estesa con:
- Informazioni aggiuntive nei nodi (US + definizione + datazione)
- Connessioni speciali (>, >>)
- Export anche in formato GraphML

**Output**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. View Matrix (Visualizzazione Rapida)

Per visualizzazione veloce senza opzioni di configurazione:
- Usa impostazioni predefinite
- Generazione piu rapida
- Ideale per controlli rapidi

## Processo di Generazione

### Step 1: Raccolta Dati

Il sistema raccoglie automaticamente:
```
Per ogni US nel sito/area selezionato:
  - Numero US
  - Tipo unita (US/USM)
  - Rapporti stratigrafici
  - Periodo e fase iniziale
  - Definizione interpretativa
```

### Step 2: Costruzione Grafo

Creazione delle relazioni:
```
Sequenza (Ante/Post):
  US1 -> US2 (US1 copre US2)

Negativo (Tagli):
  US3 -> US4 (US3 taglia US4)

Contemporaneo:
  US5 <-> US6 (US5 si lega a US6)
```

### Step 3: Clustering per Periodi

Raggruppamento gerarchico:
```
Sito
  └── Area
      └── Periodo 1 : Fase 1 : "Eta Romana"
          ├── US101
          ├── US102
          └── US103
      └── Periodo 1 : Fase 2 : "Tardo Antico"
          ├── US201
          └── US202
```

### Step 4: Riduzione Transitiva (tred)

Il comando `tred` di Graphviz rimuove le relazioni ridondanti:
- Se US1 -> US2 e US2 -> US3, rimuove US1 -> US3
- Semplifica il diagramma
- Mantiene solo relazioni dirette

### Step 5: Rendering Finale

Generazione immagine con formati multipli:
- DOT (sorgente Graphviz)
- JPG (immagine compressa)
- PNG (immagine lossless)

## Interpretazione del Matrix

### Lettura Verticale

```
     [US piu recenti]
           ↓
        US 001
           ↓
        US 002
           ↓
        US 003
           ↓
     [US piu antiche]
```

### Lettura dei Cluster

I box colorati rappresentano periodi/fasi:
- **Azzurro chiaro**: Cluster di periodo
- **Giallo**: Cluster di fase
- **Grigio**: Sfondo sito

### Tipi di Connessioni

```
─────────→  Linea continua = Copre/Riempie/Si appoggia
- - - - →  Linea tratteggiata = Taglia
←────────→  Bidirezionale = Contemporaneo/Uguale a
```

### Colori dei Nodi

| Colore | Significato Tipico |
|--------|-------------------|
| Bianco | US deposito normale |
| Grigio | US negativa (taglio) |
| Giallo | US contemporanee |
| Azzurro | US con relazioni speciali |

## Risoluzione Problemi

### Errore: "Loop Detected"

**Causa**: Esistono cicli nelle relazioni (A copre B, B copre A)

**Soluzione**:
1. Aprire la Scheda US
2. Verificare i rapporti delle US indicate
3. Correggere le relazioni circolari
4. Rigenerare il matrix

### Errore: "tred command not found"

**Causa**: Graphviz non installato

**Soluzione**:
- **Windows**: Installare Graphviz da graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matrix Non Generato

**Possibili cause**:
1. Nessun rapporto stratigrafico inserito
2. US senza periodo/fase assegnato
3. Problemi di permessi nella cartella di output

**Verifica**:
1. Controllare che le US abbiano rapporti
2. Verificare la periodizzazione
3. Controllare i permessi di `pyarchinit_Matrix_folder`

### Matrix Troppo Grande

**Problema**: Immagine illeggibile con molte US

**Soluzioni**:
1. Ridurre il DPI (100-150)
2. Filtrare per area specifica
3. Usare il View Matrix per singole aree
4. Esportare in formato vettoriale (DOT) e aprire con yEd

### US Non Raggruppate per Periodo

**Causa**: Manca la periodizzazione o non e abilitata

**Soluzione**:
1. Compilare la Scheda Periodizzazione
2. Assegnare periodo/fase iniziale alle US
3. Abilitare "Mostra Periodi" nelle impostazioni

## Output e File Generati

### Cartella di Output

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Sorgente Graphviz
├── Harris_matrix_tred.dot      # Dopo riduzione transitiva
├── Harris_matrix_tred.dot.jpg  # Immagine finale JPG
├── Harris_matrix_tred.dot.png  # Immagine finale PNG
├── Harris_matrix2ED.dot        # Versione estesa
├── Harris_matrix2ED_graphml.dot # Per export GraphML
└── matrix_error.txt            # Log errori
```

### Utilizzo dei File

| File | Utilizzo |
|------|----------|
| *.jpg/*.png | Inserimento in relazioni |
| *.dot | Modifica con editor Graphviz |
| _graphml.dot | Import in yEd per editing avanzato |

## Best Practices

### 1. Prima della Generazione

- Verificare completezza rapporti stratigrafici
- Controllare assenza di cicli
- Assegnare periodo/fase a tutte le US
- Compilare la definizione interpretativa

### 2. Durante la Compilazione US

- Inserire rapporti bidirezionali corretti
- Usare terminologia consistente
- Verificare area corretta nei rapporti

### 3. Ottimizzazione Output

- Per stampa: DPI 300
- Per schermo: DPI 150
- Per scavi complessi: suddividere per aree

### 4. Controllo Qualita

- Confrontare matrix con documentazione di scavo
- Verificare sequenze logiche
- Controllare raggruppamenti per periodo

## Workflow Completo

### 1. Preparazione Dati

```
1. Completare schede US con tutti i rapporti
2. Compilare scheda Periodizzazione
3. Assegnare periodo/fase alle US
4. Verificare consistenza dati
```

### 2. Generazione Matrix

```
1. Menu PyArchInit → Matrix di Harris
2. Configurare impostazioni (DPI, colori)
3. Abilitare cluster per periodi
4. Generare il matrix
```

### 3. Verifica e Correzione

```
1. Controllare il matrix generato
2. Identificare eventuali errori
3. Correggere rapporti nelle schede US
4. Rigenerare se necessario
```

### 4. Utilizzo Finale

```
1. Inserire in relazione di scavo
2. Esportare per pubblicazione
3. Archiviare con documentazione
```

## Integrazione con Altri Strumenti

### Export per yEd

Il file `_graphml.dot` puo essere aperto in yEd per:
- Editing manuale del layout
- Aggiunta di annotazioni
- Export in formati diversi

### Export per s3egraph

PyArchInit supporta l'export per il sistema s3egraph:
- Formato compatibile
- Mantiene relazioni stratigrafiche
- Supporto per visualizzazione 3D

## Riferimenti

### File Sorgente
- `tabs/Interactive_matrix.py` - Interfaccia interattiva
- `modules/utility/pyarchinit_matrix_exp.py` - Classi HarrisMatrix e ViewHarrisMatrix

### Database
- `us_table` - Dati US e rapporti
- `periodizzazione_table` - Periodi e fasi

### Dipendenze
- Graphviz (dot, tred)
- Python graphviz library

---

## Video Tutorial

### Matrix di Harris - Generazione Completa
`[Placeholder: video_matrix_harris.mp4]`

**Contenuti**:
- Configurazione impostazioni
- Generazione matrix
- Interpretazione risultati
- Risoluzione problemi comuni

**Durata prevista**: 15-20 minuti

### Matrix di Harris - Editing Avanzato con yEd
`[Placeholder: video_matrix_yed.mp4]`

**Contenuti**:
- Export per yEd
- Modifica layout
- Aggiunta annotazioni
- Re-export

**Durata prevista**: 10-12 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../animations/harris_matrix_animation.html)
