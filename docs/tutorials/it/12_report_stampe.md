# Tutorial 12: Report e Stampe PDF

## Introduzione

PyArchInit offre un sistema completo di generazione di **report PDF** per tutte le schede archeologiche. Questa funzionalita permette di esportare la documentazione in formato stampabile, conforme agli standard ministeriali e pronti per l'archiviazione.

### Tipologie di Report Disponibili

| Tipo | Descrizione | Scheda Origine |
|------|-------------|----------------|
| Schede US | Report completi US/USM | Scheda US |
| Indice US | Elenco sintetico US | Scheda US |
| Schede Periodizzazione | Report periodi/fasi | Scheda Periodizzazione |
| Schede Struttura | Report strutture | Scheda Struttura |
| Schede Reperti | Report inventario materiali | Scheda Inventario |
| Schede Tomba | Report sepolture | Scheda Tomba |
| Schede Campioni | Report campionature | Scheda Campioni |
| Schede Individui | Report antropologici | Scheda Individui |

## Accesso alla Funzione

### Dal Menu Principale
1. **PyArchInit** nella barra del menu
2. Selezionare **Export PDF**

### Dalla Toolbar
Cliccare sull'icona **PDF** nella toolbar di PyArchInit

## Interfaccia di Esportazione

### Panoramica Finestra

La finestra di esportazione PDF presenta:

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Sito: [ComboBox selezione sito]    [v]   |
+------------------------------------------+
| Schede da esportare:                      |
| [x] Schede US                             |
| [x] Schede Periodizzazione                |
| [x] Schede Struttura                      |
| [x] Schede Reperti                        |
| [x] Schede Tomba                          |
| [x] Schede Campioni                       |
| [x] Schede Individui                      |
+------------------------------------------+
| [Apri Cartella]  [Esporta PDF]  [Annulla] |
+------------------------------------------+
```

### Selezione Sito

| Campo | Descrizione |
|-------|-------------|
| ComboBox Sito | Lista di tutti i siti nel database |

**Nota**: L'esportazione avviene per singolo sito. Per esportare piu siti, ripetere l'operazione.

### Checkbox Schede

Ogni checkbox abilita l'esportazione di un tipo specifico:

| Checkbox | Genera |
|----------|--------|
| Schede US | Schede complete + Indice US |
| Schede Periodizzazione | Schede periodi + Indice |
| Schede Struttura | Schede strutture + Indice |
| Schede Reperti | Schede materiali + Indice |
| Schede Tomba | Schede sepolture + Indice |
| Schede Campioni | Schede campioni + Indice |
| Schede Individui | Schede antropologiche + Indice |

## Processo di Esportazione

### Step 1: Selezione Dati

```python
# Il sistema esegue per ogni tipo selezionato:
1. Query database per sito selezionato
2. Ordinamento dati (per numero, area, etc.)
3. Preparazione lista per generazione
```

### Step 2: Generazione PDF

Per ogni tipo di scheda:
1. **Scheda singola**: PDF dettagliato per ogni record
2. **Indice**: PDF riepilogativo con tutti i record

### Step 3: Salvataggio

Output nella cartella:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Contenuto dei Report

### Scheda US

Informazioni incluse:
- **Dati identificativi**: Sito, Area, Numero US, Tipo unita
- **Definizioni**: Stratigrafica, Interpretativa
- **Descrizione**: Testo descrittivo completo
- **Interpretazione**: Analisi interpretativa
- **Periodizzazione**: Periodo/Fase iniziale e finale
- **Caratteristiche fisiche**: Colore, consistenza, formazione
- **Misure**: Quote min/max, dimensioni
- **Rapporti**: Elenco relazioni stratigrafiche
- **Documentazione**: Riferimenti grafici e fotografici
- **Dati USM**: (se applicabile) Tecnica muraria, materiali

### Indice US

Tabella riassuntiva con colonne:
| Sito | Area | US | Def. Stratigrafica | Def. Interpretativa | Periodo |

### Scheda Periodizzazione

- Sito
- Numero Periodo
- Numero Fase
- Cronologia iniziale/finale
- Datazione estesa
- Descrizione periodo

### Scheda Struttura

- Dati identificativi (Sito, Sigla, Numero)
- Categoria, Tipologia, Definizione
- Descrizione e Interpretazione
- Periodizzazione
- Materiali impiegati
- Elementi strutturali
- Rapporti struttura
- Misure e quote

### Scheda Reperti

- Sito, Numero inventario
- Tipo reperto, Definizione
- Descrizione
- Provenienza (Area, US)
- Stato conservazione
- Datazione
- Elementi e misurazioni
- Bibliografia

### Scheda Tomba

- Dati identificativi
- Rito (inumazione/cremazione)
- Tipo sepoltura e deposizione
- Descrizione e interpretazione
- Corredo (presenza, tipo, descrizione)
- Periodizzazione
- Quote struttura e individuo
- US associate

### Scheda Campioni

- Sito, Numero campione
- Tipo campione
- Descrizione
- Provenienza (Area, US)
- Luogo conservazione
- Numero cassa

### Scheda Individui

- Dati identificativi
- Sesso, Eta (min/max), Classi eta
- Posizione scheletro
- Orientamento (asse, azimut)
- Stato conservazione
- Osservazioni

## Lingue Supportate

Il sistema genera report in base alla lingua di sistema:

| Lingua | Codice | Template |
|--------|--------|----------|
| Italiano | IT | `build_*_sheets()` |
| Tedesco | DE | `build_*_sheets_de()` |
| Inglese | EN | `build_*_sheets_en()` |

La lingua viene rilevata automaticamente dalle impostazioni QGIS.

## Cartella di Output

### Percorso Standard
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Struttura File Generati

```
pyarchinit_PDF_folder/
├── US_[sito]_schede.pdf           # Schede US complete
├── US_[sito]_indice.pdf           # Indice US
├── Periodizzazione_[sito].pdf     # Schede Periodizzazione
├── Struttura_[sito]_schede.pdf    # Schede Struttura
├── Struttura_[sito]_indice.pdf    # Indice Struttura
├── Reperti_[sito]_schede.pdf      # Schede Reperti
├── Reperti_[sito]_indice.pdf      # Indice Reperti
├── Tomba_[sito]_schede.pdf        # Schede Tomba
├── Campioni_[sito]_schede.pdf     # Schede Campioni
├── Individui_[sito]_schede.pdf    # Schede Individui
└── ...
```

### Apertura Cartella

Il pulsante **"Apri Cartella"** apre direttamente la directory di output nel file manager del sistema.

## Personalizzazione Report

### Template PDF

I template sono definiti nei moduli:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Libreria Utilizzata

I PDF sono generati con **ReportLab**, che permette:
- Layout personalizzabili
- Inserimento immagini
- Tabelle formattate
- Intestazioni/pie pagina

### Font Richiesti

Il sistema utilizza font specifici:
- **Cambria** (font principale)
- Installazione automatica al primo avvio del plugin

## Workflow Consigliato

### 1. Preparazione Dati

```
1. Completare tutte le schede del sito
2. Verificare completezza dei dati
3. Controllare periodizzazione
4. Verificare rapporti stratigrafici
```

### 2. Esportazione

```
1. Aprire Export PDF
2. Selezionare il sito
3. Selezionare i tipi di schede
4. Cliccare "Esporta PDF"
5. Attendere completamento
```

### 3. Verifica

```
1. Aprire cartella output
2. Controllare i PDF generati
3. Verificare formattazione
4. Stampare o archiviare
```

## Risoluzione Problemi

### Errore: "No form to print"

**Causa**: Nessun record trovato per il tipo selezionato

**Soluzione**:
- Verificare che esistano dati per il sito selezionato
- Controllare il database

### PDF Vuoti o Incompleti

**Possibili cause**:
1. Campi obbligatori non compilati
2. Problemi di codifica caratteri
3. Font mancanti

**Soluzioni**:
- Completare i campi obbligatori
- Verificare installazione font Cambria

### Errore Font

**Causa**: Font Cambria non installato

**Soluzione**:
- Il plugin tenta l'installazione automatica
- In caso di problemi, installare manualmente

### Export Lento

**Causa**: Molti record da esportare

**Soluzione**:
- Esportare per tipologia separatamente
- Attendere il completamento

## Best Practices

### 1. Organizzazione

- Esportare regolarmente durante lo scavo
- Creare backup dei PDF generati
- Organizzare per campagna/anno

### 2. Completezza Dati

- Compilare tutti i campi prima dell'export
- Verificare le quote dalle misurazioni GIS
- Controllare i rapporti stratigrafici

### 3. Archiviazione

- Salvare PDF su storage sicuro
- Includere nella documentazione finale
- Allegare alla relazione di scavo

### 4. Stampa

- Usare carta acid-free per archiviazione
- Stampare in formato A4
- Rilegare per campagna

## Integrazione con Altre Funzioni

### Quote da GIS

Il sistema recupera automaticamente:
- Quote minime e massime dalle geometrie
- Riferimenti alle piante GIS

### Documentazione Fotografica

I report possono includere riferimenti a:
- Fotografie collegate
- Disegni e rilievi

### Periodizzazione

I report US includono automaticamente:
- Datazione estesa dal periodo/fase assegnato
- Riferimenti cronologici

## Riferimenti

### File Sorgente
- `tabs/Pdf_export.py` - Interfaccia esportazione
- `modules/utility/pyarchinit_exp_*_pdf.py` - Generatori PDF

### Dipendenze
- ReportLab (generazione PDF)
- Font Cambria

---

## Video Tutorial

### Export PDF Completo
`[Placeholder: video_export_pdf.mp4]`

**Contenuti**:
- Selezione sito e schede
- Processo di esportazione
- Verifica output
- Organizzazione archivio

**Durata prevista**: 10-12 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
