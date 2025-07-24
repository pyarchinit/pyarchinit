# PyArchInit - Migrazione Campo US da INTEGER a STRING

## Panoramica

Questa migrazione converte il campo US (Unità Stratigrafica) da INTEGER a STRING in tutto il database PyArchInit. Questo permetterà di utilizzare valori alfanumerici come "US001", "US-A", "2024/001", etc.

## Motivazione

- Supportare sistemi di numerazione più flessibili per le US
- Permettere prefissi e suffissi alfanumerici
- Allinearsi con standard archeologici che prevedono codifiche complesse
- Mantenere compatibilità con sistemi esterni che usano US alfanumeriche

## Tabelle Interessate

### Tabelle con campo US (INTEGER → STRING):
- `us_table` - campo `us`
- `campioni_table` - campo `us`
- `pottery_table` - campo `us`
- `us_table_toimp` - campo `us`

### Tabelle GIS correlate:
- `pyarchinit_quote` - campo `us_q`
- `pyarchinit_quote_usm` - campo `us_q`
- `pyunitastratigrafiche` - campo `us_s`
- `pyunitastratigrafiche_usm` - campo `us_s`
- `pyuscaratterizzazioni` - campo `us_c`
- `pyarchinit_us_negative_doc` - campo `us_n`

### Tabelle già con US come TEXT (nessun cambiamento):
- `inventario_materiali_table`
- `individui_table`

## Procedura di Migrazione

### 1. Backup del Database

**IMPORTANTE**: Fare sempre un backup completo prima di procedere!

```bash
# PostgreSQL
pg_dump -U username -d pyarchinit_db > backup_pyarchinit_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp pyarchinit.sqlite pyarchinit_backup_$(date +%Y%m%d_%H%M%S).sqlite
```

### 2. Eseguire lo Script di Migrazione Database

#### Per PostgreSQL:
```sql
psql -U username -d pyarchinit_db -f migration_us_to_string.sql
```

#### Per SQLite:
```sql
sqlite3 pyarchinit.sqlite < migration_us_to_string_sqlite.sql
```

### 3. Aggiornare le Entity Classes

```bash
cd /path/to/pyarchinit/scripts
python update_entities_us_field.py
```

### 4. Aggiornare i Form (Manuale)

Vedere il file `US_FIELD_MIGRATION_GUIDE.md` per i dettagli sulle modifiche necessarie nei form.

Principali modifiche:
- Rimuovere conversioni `int()` per il campo US
- Aggiornare validazioni da controllo numerico a controllo stringa
- Modificare ordinamenti per gestire valori alfanumerici

## Test da Eseguire

- [ ] Inserimento nuove US con valori alfanumerici
- [ ] Ricerca US per valore
- [ ] Ordinamento lista US
- [ ] Relazioni con altre tabelle (campioni, materiali, etc.)
- [ ] Funzionamento viste GIS
- [ ] Export/Import dati
- [ ] Generazione report PDF

## Rollback

In caso di problemi, utilizzare lo script di rollback:

```sql
-- PostgreSQL
psql -U username -d pyarchinit_db -f rollback_us_to_integer.sql

-- SQLite
sqlite3 pyarchinit.sqlite < rollback_us_to_integer_sqlite.sql
```

**NOTA**: Il rollback fallirà se sono stati inseriti valori non numerici!

## Considerazioni Importanti

1. **Ordinamento**: Con US alfanumeriche, l'ordinamento diventa lessicografico. Considerare l'implementazione di un ordinamento naturale.

2. **Validazione**: Definire regole chiare per il formato accettabile delle US (es. regex pattern).

3. **Compatibilità**: Verificare che tutti i plugin e script esterni siano compatibili con il nuovo tipo di dato.

4. **Performance**: Gli indici su campi TEXT potrebbero avere performance diverse rispetto a INTEGER.

## Supporto

Per problemi o domande sulla migrazione, contattare il team PyArchInit o aprire una issue su GitHub.