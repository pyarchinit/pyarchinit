# Sistema di Importazione TMA (Tabella Materiali Archeologici)

## Panoramica

Il sistema di importazione TMA permette di importare dati da vari formati di file nel database TMA di pyArchInit. Supporta importazioni da Excel, CSV, JSON e XML con mapping automatico o personalizzato dei campi.

## Formati Supportati

- **Excel** (.xlsx, .xls)
- **CSV** (.csv)
- **JSON** (.json)
- **XML** (.xml)
- **DOCX** (.docx) - con parser specializzato per inventari Festos

### Parser Specializzato Festos

Per i file DOCX contenenti inventari archeologici di Festos, è disponibile un parser specializzato che gestisce automaticamente:
- Inventari cassette con range (es. "1-72" → genera record per cassette 1-72)
- Inventari dettagliati con Unità Stratigrafiche (US)
- Estrazione automatica di magazzino e settore dal contesto
- Parsing intelligente di date e anni multipli

Per maggiori dettagli, vedi [FESTOS_IMPORT_README.md](FESTOS_IMPORT_README.md)

## Campi del Database TMA

### Campi Obbligatori
- `sito` - Nome del sito archeologico
- `area` - Area di scavo
- `dscu` - Unità stratigrafica (US)
- `ogtm` - Materiale (valori accettati: CERAMICA, INDUSTRIA LITICA, LITICA, METALLO)
- `ldcn` - Denominazione collocazione
- `cassetta` - Numero cassetta
- `localita` - Località
- `dtzg` - Fascia cronologica
- `macc` - Categoria

### Campi Opzionali

#### Localizzazione
- `ldct` - Tipologia collocazione (Magazzino, Materiali all'aperto, Museo)
- `vecchia_collocazione` - Vecchia collocazione
- `scan` - Denominazione scavo
- `saggio` - Saggio
- `vano_locus` - Vano/Locus
- `dscd` - Data scavo
- `magazzino` - Numero/nome magazzino
- `num_cassetta` - Numero cassetta specifico
- `settore` - Settore di scavo (es. HTR, F)
- `dslgt` - Denominazione sito (nome del sito)
- `anni_scavo` - Anno o anni di scavo
- `dsogt` - Descrizione oggetto/materiale
- `riferimenti` - Riferimenti e note aggiuntive
- `data_schedatura` - Data di catalogazione/schedatura

#### Ricognizione
- `rcgd` - Data ricognizione
- `rcgz` - Specifiche ricognizione
- `aint` - Tipo acquisizione
- `aind` - Data acquisizione

#### Datazione e Quantità
- `dtzs` - Frazione cronologica
- `cronologie` - Cronologie
- `n_reperti` - Numero reperti
- `peso` - Peso

#### Dati Tecnici
- `deso` - Indicazione oggetti
- `madi` - Inventario
- `macl` - Classe
- `macp` - Precisazione tipologica
- `macd` - Definizione
- `cronologia_mac` - Cronologia MAC
- `macq` - Quantità

#### Documentazione
- `ftap` - Tipo fotografia
- `ftan` - Codice foto
- `drat` - Tipo disegno
- `dran` - Codice disegno
- `draa` - Autore disegno

## Utilizzo

### 1. Tramite Interfaccia Grafica

1. Apri la scheda TMA in pyArchInit
2. Clicca sul pulsante di importazione (icona import nella toolbar)
3. Seleziona i file da importare:
   - Per Excel/CSV/JSON/XML: usa i rispettivi pulsanti
   - Per DOCX (inventari Festos): usa "Aggiungi DOCX" e spunta "Usa parser Festos"
4. Opzionalmente configura un mapping personalizzato
5. Clicca su "Importa"

**Nota per inventari Festos**: Quando importi file DOCX di inventari Festos, assicurati di spuntare la casella "Usa parser Festos per file DOCX" per attivare il parser specializzato.

### 2. Tramite Codice Python

```python
from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.utility.tma_import_parser import TMAImportManager

# Connessione al database
conn = Connection()
conn_str = conn.conn_str()
db_manager = Pyarchinit_db_management(conn_str)
db_manager.connection()

# Crea il manager di importazione
import_manager = TMAImportManager(db_manager)

# Importa un file
imported, errors, warnings = import_manager.import_file("path/to/file.xlsx")
```

## Mapping dei Campi

Il sistema riconosce automaticamente molte varianti dei nomi dei campi. Ad esempio:
- "US", "unita_stratigrafica", "stratigraphic_unit" → `dscu`
- "materiale", "material", "tipo_materiale" → `ogtm`
- "peso", "weight", "peso_gr" → `peso`

### Mapping Personalizzato

È possibile definire mapping personalizzati per gestire formati specifici:

```python
custom_mapping = {
    'numero_inventario_museo': 'madi',
    'tipo_di_materiale': 'ogtm',
    'peso_grammi': 'peso'
}

imported, errors, warnings = import_manager.import_file(
    "file.csv", 
    custom_mapping
)
```

## Formato dei File

### Excel/CSV
I file devono avere:
- Prima riga: intestazioni delle colonne
- Righe successive: dati

Esempio:
```
Sito,Area,US,Materiale,Cassetta,Località,Denominazione collocazione,Fascia cronologica,Categoria
Roma,A,101,CERAMICA,C001,Roma Centro,Magazzino 1,I sec. d.C.,Ceramica comune
```

### JSON
Array di oggetti o oggetto singolo:
```json
[
  {
    "sito": "Roma",
    "area": "A",
    "us": "101",
    "materiale": "CERAMICA",
    "cassetta": "C001",
    "localita": "Roma Centro",
    "denominazione_collocazione": "Magazzino 1",
    "fascia_cronologica": "I sec. d.C.",
    "categoria": "Ceramica comune"
  }
]
```

### XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<records>
  <record>
    <sito>Roma</sito>
    <area>A</area>
    <us>101</us>
    <materiale>CERAMICA</materiale>
    <cassetta>C001</cassetta>
    <localita>Roma Centro</localita>
    <denominazione_collocazione>Magazzino 1</denominazione_collocazione>
    <fascia_cronologica>I sec. d.C.</fascia_cronologica>
    <categoria>Ceramica comune</categoria>
  </record>
</records>
```

## Gestione Errori

Il sistema fornisce tre tipi di feedback:

1. **Record importati**: numero di record inseriti con successo
2. **Errori**: problemi che hanno impedito l'importazione (es. campi obbligatori mancanti)
3. **Avvisi**: problemi non bloccanti (es. campi non riconosciuti)

## Documentazione Multipla

Per fotografie e disegni multipli, separare i valori con punto e virgola:

```
ftap: "Generale;Dettaglio;Macro"
ftan: "IMG001;IMG002;IMG003"
```

## Note Importanti

1. I campi obbligatori devono essere sempre presenti
2. Il campo `ogtm` accetta solo: CERAMICA, INDUSTRIA LITICA, LITICA, METALLO
3. Il campo `ldct` accetta solo: Magazzino, Materiali all'aperto, Museo
4. Le date possono essere in formato libero (es. "2023", "15/03/2023", "marzo 2023")
5. I campi numerici devono contenere solo numeri
6. Il sistema è case-insensitive per i nomi dei campi

## Esempi

Vedi il file `examples/tma_import_example.py` per esempi completi di utilizzo.
