# Fix e Miglioramenti Sistema Import Inventari TMA

## Problemi Risolti

### 1. ❌ ERRORE SQLAlchemy: "Column expression or FROM clause expected, got ."

**File**: `tabs/Tma.py`

**Problema**: `MAPPER_TABLE_CLASS` era una stringa invece della classe

**Fix applicati**:
```python
# Aggiunto import della classe TMA
from ..modules.db.entities.TMA import TMA

# Corretto MAPPER_TABLE_CLASS
MAPPER_TABLE_CLASS = TMA  # Era "TMA" (stringa)

# Corretto ID_TABLE  
ID_TABLE = "id_tma"  # Era "id"

# Aggiornato CONVERSION_DICT
CONVERSION_DICT = {
    ID_TABLE: ID_TABLE,
    "ID": "id_tma",  # Aggiunto mapping per ID
    ...
}

# Corretto max_num_id in insert_new_rec
self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)  # Era 'TMA'
```

### 2. 📄 Parser per Inventari Cassette DOCX

**Files creati/modificati**:
- `modules/utility/festos_inventory_parser.py` - Parser specializzato per Festos
- `modules/utility/tma_import_parser_extended.py` - Estensione del parser base
- `gui/tma_import_dialog.py` - Aggiornato per usare il manager esteso

**Funzionalità aggiunte**:
- Riconoscimento automatico formato inventario (cerca "Cassette", "Magazzino")
- Parsing range cassette (1-72 → 72 record)
- Estrazione automatica tipo materiale dalla descrizione
- Estrazione area/vano (es. "Vano XCIV" → area = "XCIV")
- Validazione meno restrittiva per inventari
- Dialog di completamento dati mancanti

### 3. 🔄 Miglioramento Import Dialog

**File**: `gui/tma_import_dialog.py`

**Modifiche**:
- Usa `TMAImportManagerExtended` invece di `TMAImportManager`
- Checkbox "Usa parser Festos" per file DOCX
- Gestione speciale per inventari

### 4. 🔧 Correzioni ID Campo

**Files**: Vari parser e manager

**Fix**: Tutti i riferimenti a `max_num_id` ora usano `'id_tma'` invece di `'id'`

## File Creati/Modificati

### Nuovi File
1. `modules/utility/festos_inventory_parser.py` - Parser Festos
2. `docs/TMA_INVENTORY_IMPORT_README.md` - Documentazione completa
3. `test_tma_import_inventory.py` - Script di test
4. `examples/import_festos_inventory.py` - Esempio pratico
5. `INVENTORY_IMPORT_FIXES.md` - Questo file

### File Modificati
1. `tabs/Tma.py` - Fix MAPPER_TABLE_CLASS e ID_TABLE
2. `modules/utility/tma_import_parser.py` - Fix max_num_id
3. `modules/utility/tma_import_parser_extended.py` - Riscritta completamente
4. `gui/tma_import_dialog.py` - Aggiornato import manager

## Come Testare

### 1. Test Rapido Parser
```bash
python test_tma_import_inventory.py
```

### 2. Import da Script
```bash
python examples/import_festos_inventory.py path/to/inventory.docx
```

### 3. Import da GUI
1. Apri pyArchInit
2. Vai alla scheda TMA
3. Clicca pulsante "Import"
4. Seleziona file DOCX
5. Spunta "Usa parser Festos"
6. Clicca "Importa"

## Struttura File Inventario Supportata

```
**Festos - Magazzino 3-4**

| Cassette | Descrizione | Anno |
|----------|-------------|------|
| 1-72     | Chalara     | 1960 |
| 457      | Frammenti scelti... | 1965-66 |
```

## Mapping Automatico

| Descrizione | → | Tipo Materiale |
|-------------|---|----------------|
| "frammenti ceramici" | → | CERAMICA |
| "ossa" | → | FAUNA |
| "pietra", "macine" | → | INDUSTRIA LITICA |
| "ferro", "bronzo" | → | METALLO |

## Campi Gestiti

### Obbligatori (solo 2!)
- `sito` - Nome del sito archeologico
- `dscu` - Identificativo cassetta (es. "Cassetta 1")

### Con Default
- `ogtm` = "CERAMICA"
- `ldct` = "Magazzino"
- `macc` = "ND"
- `dtzg` = "ND" o dedotto

### Estratti Automaticamente
- `area` - Da pattern come "Vano XCIV"
- `n_reperti` - Da "72 frammenti"
- `cassetta` - Numero cassetta
- `cronologie` - Anno o range

## Performance

- **1-100 cassette**: Immediato
- **100-1000 cassette**: ~10-30 secondi
- **1000+ cassette**: Considera suddivisione per magazzino

## Troubleshooting

### "Campo obbligatorio mancante"
Solo `sito` e `dscu` sono richiesti per inventari

### "max_num_id() takes 2 positional arguments"
Assicurati che tutti i file siano aggiornati con le correzioni

### Import lento
Per range grandi (es. 1-1000), l'operazione può richiedere tempo

## Note Importanti

1. **Backup**: Sempre fare backup del DB prima di import massivi
2. **Test**: Testare con piccoli file prima di import completi
3. **Memoria**: Per file molto grandi, aumentare memoria Python
4. **Commit**: Il sistema fa commit automatico dopo ogni import riuscito
