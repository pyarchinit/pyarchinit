# Tutorial 26: Pottery Tools

## Introduzione

**Pottery Tools** e un modulo avanzato per l'elaborazione di immagini ceramiche. Offre strumenti per estrarre immagini da PDF, generare layout di tavole, processare disegni con AI (PotteryInk) e altre funzionalita specializzate per la documentazione ceramica.

### Funzionalita Principali

- Estrazione immagini da PDF
- Generazione layout tavole ceramiche
- Elaborazione immagini con AI
- Conversione formato disegni
- Integrazione con Scheda Pottery

## Accesso

### Dal Menu
**PyArchInit** → **Pottery Tools**

## Interfaccia

### Pannello Principale

```
+--------------------------------------------------+
|              Pottery Tools                        |
+--------------------------------------------------+
| [Tab: Estrazione PDF]                            |
| [Tab: Layout Generator]                          |
| [Tab: Image Processing]                          |
| [Tab: PotteryInk AI]                             |
+--------------------------------------------------+
| [Progress Bar]                                   |
| [Log Messages]                                   |
+--------------------------------------------------+
```

## Tab Estrazione PDF

### Funzione

Estrae automaticamente le immagini da documenti PDF contenenti tavole ceramiche.

### Utilizzo

1. Selezionare file PDF sorgente
2. Specificare cartella destinazione
3. Cliccare **"Estrai"**
4. Le immagini vengono salvate come file separati

### Opzioni

| Opzione | Descrizione |
|---------|-------------|
| DPI | Risoluzione estrazione (150-600) |
| Formato | PNG, JPG, TIFF |
| Pagine | Tutte o range specifico |

## Tab Layout Generator

### Funzione

Genera automaticamente tavole di ceramica con layout standardizzato.

### Tipi di Layout

| Layout | Descrizione |
|--------|-------------|
| Griglia | Immagini in griglia regolare |
| Sequenza | Immagini in sequenza numerata |
| Confronto | Layout per comparazione |
| Catalogo | Formato catalogo con didascalie |

### Utilizzo

1. Selezionare immagini da includere
2. Scegliere tipo layout
3. Configurare parametri (dimensioni, margini)
4. Generare tavola

### Parametri Layout

| Parametro | Descrizione |
|-----------|-------------|
| Dimensione pagina | A4, A3, Custom |
| Orientamento | Verticale, Orizzontale |
| Margini | Spazio bordi |
| Spaziatura | Distanza tra immagini |
| Didascalie | Testo sotto immagini |

## Tab Image Processing

### Funzione

Elaborazione batch di immagini ceramiche.

### Operazioni Disponibili

| Operazione | Descrizione |
|------------|-------------|
| Ridimensiona | Scala immagini |
| Ritaglia | Crop automatico/manuale |
| Ruota | Rotazione gradi |
| Converti | Cambio formato |
| Ottimizza | Compressione qualita |

### Elaborazione Batch

1. Selezionare cartella sorgente
2. Scegliere operazioni da applicare
3. Specificare destinazione
4. Eseguire elaborazione

## Tab PotteryInk AI

### Funzione

Utilizza intelligenza artificiale per:
- Conversione foto → disegno tecnico
- Riconoscimento forme ceramiche
- Suggerimenti classificazione
- Misurazione automatica

### Requisiti

- Ambiente virtuale Python configurato
- Modelli AI scaricati (YOLO, etc.)
- GPU consigliata (ma non obbligatoria)

### Modelli AI

**Modelli di inchiostrazione (PotteryInk).** Nella scheda **🏺 PotteryInk**, gruppo **Enhancement Settings**, la tendina **Model:** elenca i modelli di PyPotteryInk 2.1.2; il pulsante **Download** accanto scarica il modello selezionato da Hugging Face (`lrncrd/PyPotteryInk`) nella cartella `~/pyarchinit_5/bin/models/` (se il file c'è già, chiede se riscaricarlo). Ogni modello pesa circa 38 MB.

| Modello (voce della tendina) | File | Uso |
|------------------------------|------|-----|
| 10k Model (General) | `model_10k.pkl` | Modello generico per disegni di ceramica |
| 6h-MCG Model (Bronze Age) | `6h-MCG.pkl` | Disegni dell'età del Bronzo |
| 6h-MC Model (Protohistoric) | `6h-MC.pkl` | Disegni protostorici e storici |
| 4h-PAINT Model (Historic/Painted) | `4h-PAINT.pkl` | Ceramica storica e dipinta |
| 5h-PAPERGRID Model (Paper grid tables) | `5h_PAPERGRID.pkl` | Disegni su carta millimetrata (tavole a griglia); non supporta le ombre |

**Rilevatore dei disegni (YOLO).** Il modello `BasicModelv8_v01.pt` di PyPotteryLens, che riconosce i disegni nelle pagine estratte dai PDF (opzione **Auto-detect pottery (ML)** e scheda **2. Apply Model**), si installa con il pulsante **Download YOLO Model** della scheda **PDF Extraction**: se trova una copia locale di PyPotteryLens la copia, altrimenti lo scarica da Hugging Face (`lrncrd/PyPotteryLens`, circa 144 MB) e, se il download non riesce, dal fork GitHub come riserva. Il file viene salvato in `~/pyarchinit_5/bin/`; un download fallito non lascia file a metà.

### Utilizzo

1. Caricare immagine ceramica
2. Selezionare tipo elaborazione
3. Attendere processamento AI
4. Verificare e salvare risultato

### Tipi di Elaborazione AI

| Tipo | Descrizione |
|------|-------------|
| Ink Conversion | Converte foto in disegno tecnico |
| Shape Detection | Riconosce forma del vaso |
| Profile Extraction | Estrae profilo ceramico |
| Decoration Analysis | Analizza decorazioni |

## Ambiente Virtuale

### Setup Automatico

Al primo avvio, Pottery Tools:
1. Crea ambiente virtuale in `~/pyarchinit_5/bin/pottery_venv/`
2. Installa dipendenze necessarie
3. Scarica modelli AI (se richiesti)

### Dipendenze

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Verifica Installazione

Il log mostra lo stato:
```
✓ Virtual environment created
✓ Dependencies installed
✓ Models downloaded
✓ Pottery Tools initialized successfully!
```

## Integrazione Database

### Collegamento a Scheda Pottery

Le immagini processate possono essere:
- Collegate automaticamente a record Pottery
- Salvate con metadati appropriati
- Organizzate per sito/inventario

## Best Practices

### 1. Qualita Immagini Input

- Risoluzione minima: 300 DPI
- Illuminazione uniforme
- Sfondo neutro (bianco/grigio)
- Scala metrica visibile

### 2. Elaborazione AI

- Verificare sempre risultati AI
- Correggere manualmente se necessario
- Salvare originali e elaborati

### 3. Organizzazione Output

- Usare naming consistente
- Organizzare per sito/campagna
- Mantenere tracciabilita

## Risoluzione Problemi

### Ambiente Virtuale Non Creato

**Cause**:
- Python non trovato
- Permessi insufficienti

**Soluzioni**:
- Verificare installazione Python
- Controllare permessi cartella

### Elaborazione AI Lenta

**Cause**:
- Nessuna GPU disponibile
- Immagini troppo grandi

**Soluzioni**:
- Ridurre dimensione immagini
- Usare CPU (piu lento ma funziona)

### Estrazione PDF Fallita

**Cause**:
- PDF protetto
- Formato non supportato

**Soluzioni**:
- Verificare protezione PDF
- Provare con altro software PDF

## Riferimenti

### File Sorgente
- `tabs/Pottery_tools.py` - Interfaccia principale
- `modules/utility/pottery_utilities.py` - Utility elaborazione
- `modules/utility/pottery_models.py` - Registro dei modelli (PotteryInk e rilevatore YOLO)
- `gui/ui/Pottery_tools.ui` - Layout UI

### Cartelle
- `~/pyarchinit_5/bin/pottery_venv/` - Ambiente virtuale
- `~/pyarchinit_5/bin/models/` - Modelli PotteryInk (`.pkl`)
- `~/pyarchinit_5/bin/BasicModelv8_v01.pt` - Rilevatore YOLO

---

## Video Tutorial

### Pottery Tools Completo
`[Placeholder: video_pottery_tools.mp4]`

**Contenuti**:
- Estrazione da PDF
- Generazione layout
- Elaborazione AI
- Integrazione database

**Durata prevista**: 20-25 minuti

---

*Ultimo aggiornamento: Ottobre 2026*
