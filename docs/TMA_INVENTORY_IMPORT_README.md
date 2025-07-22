# Sistema di Importazione Inventari TMA

## Panoramica

Il sistema di importazione TMA è stato esteso per supportare l'importazione di inventari cassette archeologiche da file DOCX con il formato tipico di Festos e altri siti archeologici.

## Correzioni Applicate

### 1. Fix Errore SQLAlchemy

**Problema**: `Column expression or FROM clause expected, got .`

**Causa**: `MAPPER_TABLE_CLASS` era impostato come stringa invece che come classe.

**Soluzione**: In `tabs/Tma.py`:
```python
# Prima (ERRATO):
MAPPER_TABLE_CLASS = "TMA"

# Dopo (CORRETTO):
from ..modules.db.entities.TMA import TMA
MAPPER_TABLE_CLASS = TMA
ID_TABLE = "id_tma"  # Corretto anche questo
```

### 2. Parser Inventario Cassette

Creato un sistema di parsing specializzato per file DOCX con tabelle di inventario:

#### Struttura File Supportata

Il parser riconosce automaticamente file DOCX con:
- Titoli contenenti "Magazzino" o "Magazzini"
- Tabelle con colonne: Cassette | Descrizione | Anno

Esempio:
```
**Festos - Magazzino 3-4**

| Cassette | Descrizione | Anno |
|----------|-------------|------|
| 1-72     | Chalara     | 1960 |
| 73-150   | Chalara     | 1961 |
```

#### Funzionalità

1. **Parsing Range Cassette**:
   - `1-72` → genera 72 record (uno per cassetta)
   - `246d-259` → trattato come cassetta singola
   - `457` → singola cassetta

2. **Estrazione Automatica**:
   - **Sito**: dal titolo o nome file
   - **Magazzino**: dal titolo
   - **Tipo Materiale**: dalla descrizione (ceramica, fauna, metallo, etc.)
   - **Area**: estratta da pattern come "Vano XCIV", "Settore A"
   - **Numero Reperti**: se presente nella descrizione
   - **Fascia Cronologica**: basata su descrizione e anno

3. **Valori Default**:
   - `ogtm`: CERAMICA
   - `ldct`: Magazzino
   - `macc`: ND (non determinato)
   - `dtzg`: ND o dedotto dall'anno

## Come Usare

### 1. Da Interfaccia Grafica

1. Apri la scheda TMA in pyArchInit
2. Clicca sul pulsante "Import" nella toolbar
3. Nel dialog di importazione:
   - Clicca "Aggiungi DOCX"
   - Seleziona il file inventario
   - Spunta "Usa parser Festos per file DOCX"
   - Clicca "Importa"

### 2. Da Script Python

```python
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.utility.tma_import_parser_extended import TMAImportManagerExtended

# Setup database
db_manager = Pyarchinit_db_management()
db_manager.connection()

# Crea import manager
import_manager = TMAImportManagerExtended(db_manager)

# Importa file
file_path = 'inventario_festos.docx'
imported, errors, warnings = import_manager.import_file(file_path)

print(f"Importati: {imported} record")
if errors:
    print("Errori:", errors)
if warnings:
    print("Avvisi:", warnings)
```

### 3. Test del Sistema

Esegui lo script di test:
```bash
python test_tma_import_inventory.py
```

## Mapping Campi

Il parser mappa automaticamente:

| Campo Inventario | Campo TMA | Note |
|-----------------|-----------|------|
| Numero cassetta | dscu | Formato: "Cassetta N" |
| Descrizione | deso | Testo completo |
| Anno | cronologie | Anno o range anni |
| Magazzino | scan, ldcn | Localizzazione |
| (dedotto) | ogtm | Tipo materiale dalla descrizione |
| (dedotto) | area | Area/Vano dalla descrizione |
| (dedotto) | n_reperti | Numero dalla descrizione |
| (dedotto) | dtzg | Fascia cronologica |
| (dedotto) | macc | Categoria materiale |

## Gestione Campi Obbligatori

Per gli inventari, la validazione è meno restrittiva:

**Campi Obbligatori**:
- `sito`: Nome del sito
- `dscu`: Identificativo cassetta

**Campi Consigliati** (generano solo warning se mancanti):
- `ogtm`: Tipo materiale
- `ldct`: Tipo localizzazione
- `localita`: Località
- `cassetta`: Numero cassetta
- `dtzg`: Fascia cronologica
- `macc`: Categoria

**Campi con Default**:
- `ldct`: "Magazzino"
- `ogtm`: "CERAMICA"
- `macc`: "ND"
- `dtzg`: "ND" o dedotto

## Esempi di Descrizioni Riconosciute

Il parser riconosce automaticamente:

- **Materiali**: "frammenti ceramici" → CERAMICA
- **Fauna**: "ossa e conchiglie" → FAUNA/MALACOFAUNA  
- **Litica**: "macine in pietra" → INDUSTRIA LITICA
- **Metallo**: "oggetti in ferro" → METALLO
- **Costruzione**: "blocchi di astraki" → MATERIALE DA COSTRUZIONE

## Troubleshooting

### "Campo obbligatorio mancante"
Solo `sito` e `dscu` sono veramente obbligatori per inventari.

### "File non riconosciuto come inventario"
Il file deve contenere "Cassette" o "Magazzino" per essere riconosciuto.

### "Errore nel commit dei dati"
Verifica la connessione al database e i permessi di scrittura.

### Performance con molti record
Per inventari con migliaia di cassette (range molto ampi), l'importazione può richiedere tempo. Considera di:
- Suddividere per magazzino
- Usare importazione batch da script
- Importare in orari di basso carico

## File del Sistema

- `modules/utility/tma_import_parser.py` - Parser base
- `modules/utility/tma_import_parser_extended.py` - Estensioni per inventari
- `modules/utility/festos_inventory_parser.py` - Parser specializzato Festos
- `gui/tma_import_dialog.py` - Interfaccia grafica
- `tabs/Tma.py` - Scheda TMA con fix mapper

## Note Tecniche

1. Il parser genera un record per ogni cassetta in un range
2. I campi vuoti vengono impostati come stringhe vuote ''
3. La validazione è differenziata tra inventari e altri formati
4. Il sistema mantiene compatibilità con tutti i formati esistenti
