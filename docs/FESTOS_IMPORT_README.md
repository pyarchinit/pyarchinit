# Importazione Inventari Festos

Questa guida descrive come utilizzare il sistema di importazione specializzato per gli inventari archeologici di Festos.

## Formati Supportati

Il parser Festos supporta due formati principali di inventario trovati nei file DOCX:

### 1. Formato Cassette (Inventario generale)
Tabelle con struttura:
- **Cassette**: Numero o range di cassette (es. "1-72", "457")
- **Descrizione**: Descrizione del contenuto
- **Anno**: Anno di scavo/catalogazione

Esempio:
```
Festos - Magazzini 3-4
--------------------------------------------
Cassette | Descrizione              | Anno
---------|--------------------------|------
1-72     | Chalara                  | 1960
73-150   | Chalara                  | 1961
155-230  | Colmata Medio Minoica... | 1965
```

### 2. Formato US Dettagliato (Unità Stratigrafiche)
Tabelle con struttura:
- **Magazzino**: Numero del magazzino
- **Cassetta**: Numero della cassetta
- **Scomparto**: Suddivisione interna (es. "3a", "3b")
- **DATA**: Date di scavo (formato gg/mm/aa)
- **US**: Unità Stratigrafica

Esempio:
```
SAGGIO 2
--------------------------------------------------------
Magazzino | Cassetta | Scomparto | DATA      | US
----------|----------|-----------|-----------|----------
Mag. 5    | 1        | 1         | 11/07/22  | 2001
Mag. 5    | 2        | 2         | 12/07/22  | 2004
```

## Come Utilizzare

### 1. Da Interfaccia Grafica (QGIS)

1. Apri il dialog TMA dal menu o dalla toolbar
2. Clicca sul pulsante di importazione
3. Seleziona "Aggiungi DOCX"
4. Scegli i file di inventario Festos
5. **Importante**: Spunta la casella "Usa parser Festos per file DOCX"
6. Clicca su "Importa"

### 2. Da Script Python

```python
from modules.utility.festos_inventory_parser import FestosInventoryParser
from modules.db_manager import DBManager

# Crea connessione al database
db_manager = DBManager()

# Crea il parser
parser = FestosInventoryParser(db_manager.session)

# Importa il file
success_count, errors, warnings = parser.parse_file("inventario_festos.docx")

# Salva i dati se non ci sono errori
if success_count > 0 and not errors:
    parser.commit_changes()
    print(f"Importati {success_count} record")
```

### 3. Importazione Batch

Per importare multipli file DOCX:

```python
from examples.festos_import_example import batch_import_festos

# Importa tutti i file DOCX da una directory
batch_import_festos("/percorso/alla/directory/")
```

## Mapping dei Campi

Il parser mappa automaticamente i dati nei seguenti campi TMA:

### Dal formato Cassette:
- **Cassette** → `num_cassetta`
- **Descrizione** → `dsogt` (descrizione oggetto)
- **Anno** → `anni_scavo`
- **Magazzino** → `magazzino` (estratto dal titolo)
- **Settore** → `settore` (HTR o F, estratto dal contesto)
- **Sito** → `dslgt` (sempre "Festos")

### Dal formato US:
- **Magazzino** → `magazzino`
- **Cassetta** → `num_cassetta`
- **Scomparto** → parte di `riferimenti`
- **DATA** → `data_schedatura`
- **US** → `dscu` (denominazione scavo/unità stratigrafica)
- **Saggio** → `settore` (es. "SAGGIO 2")

## Gestione Speciale

### Range di Cassette
Il parser gestisce automaticamente i range:
- "1-72" → crea 72 record (da cassetta 1 a 72)
- "878a-919" → gestito come singola entry se i suffissi sono diversi

### Date Multiple
Le date multiple vengono conservate come stringa:
- "11,12,18/07/22" → salvato come "11,12,18/07/2022"

### Anni Multipli
Gli anni vengono normalizzati:
- "1954 e 1959" → "1954-1959"
- "1965-66" → "1965-1966"

## Controlli e Validazione

Il parser esegue automaticamente:
- Validazione della struttura delle tabelle
- Parsing intelligente di range e date
- Gestione di caratteri speciali e apostrofi
- Creazione di riferimenti strutturati

## Risoluzione Problemi

### Errori Comuni

1. **"Tabella non riconosciuta"**
   - Verifica che le intestazioni delle colonne corrispondano ai formati supportati
   - I nomi delle colonne devono essere esattamente: Cassette, Descrizione, Anno (o Magazzino, Cassetta, Scomparto, DATA, US)

2. **"Errore nel parsing del file"**
   - Verifica che il file DOCX non sia corrotto
   - Assicurati che le tabelle siano formattate correttamente

3. **Nessun record importato**
   - Controlla i log per errori specifici
   - Verifica che i campi obbligatori siano presenti

### Log e Debug

Il parser produce log dettagliati con:
- Numero di record importati per tabella
- Avvisi per dati mancanti o ambigui
- Errori specifici per ogni riga

## Esempi

Vedi `examples/festos_import_example.py` per esempi completi di:
- Importazione singolo file
- Importazione batch
- Test con dati di esempio
- Gestione errori

## Note Importanti

1. **Backup**: Sempre fare un backup del database prima di importazioni massive
2. **Test**: Testa prima con un piccolo sottoinsieme di dati
3. **Verifica**: Controlla sempre i log per avvisi ed errori
4. **Unicità**: Il parser non controlla duplicati - verificare prima di importare
