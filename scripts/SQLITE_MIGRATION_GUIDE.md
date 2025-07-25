# Guida Migrazione SQLite - US Fields

## Il Problema

La migrazione automatica nel plugin sembra non completarsi correttamente. I campi US e area rimangono come INTEGER e vengono create tabelle temporanee con suffisso `_new` che non vengono rinominate. Inoltre, le viste dipendenti (come `pyarchinit_reperti_view`) possono impedire la migrazione.

## Soluzione 1: Migrazione Sicura con Transazioni (RACCOMANDATA)

Usa questo script che garantisce l'integrità dei dati con transazioni:

```bash
cd /Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts
python safe_sqlite_migration.py /percorso/al/tuo/database.sqlite
```

Questo script:
- Crea un backup automatico
- Usa transazioni per garantire atomicità
- Verifica che tutti i dati siano migrati correttamente
- Ripristina automaticamente in caso di errore
- Gestisce tutte le viste dipendenti

## Soluzione 2: Migrazione Manuale Standard

Se preferisci più controllo sul processo:

### Passaggi:

1. **Chiudi QGIS** completamente

2. **Esegui lo script di migrazione manuale**:
   ```bash
   cd /Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts
   python manual_sqlite_migration.py /percorso/al/tuo/database.sqlite
   ```

3. **Verifica la migrazione**:
   ```bash
   python debug_sqlite_migration.py /percorso/al/tuo/database.sqlite
   ```

## Soluzione 2: Migrazione SQL Diretta

Se preferisci, puoi eseguire la migrazione direttamente con SQLite:

```bash
sqlite3 /percorso/al/tuo/database.sqlite < migration_us_to_string_sqlite_fixed.sql
```

## Tabelle Interessate

Le seguenti tabelle saranno migrate:

| Tabella | Campi da Migrare |
|---------|------------------|
| inventario_materiali_table | us, area |
| tomba_table | area |
| us_table | us, area |
| campioni_table | us, area |
| pottery_table | us, area |

## Verifica Post-Migrazione

Dopo la migrazione, verifica che:
1. I campi siano diventati TEXT
2. Non ci siano più tabelle con suffisso `_new`
3. I dati siano stati preservati correttamente

## Troubleshooting

### Se vedi ancora tabelle _new:

1. Pulisci manualmente:
   ```sql
   DROP TABLE IF EXISTS inventario_materiali_table_new;
   DROP TABLE IF EXISTS tomba_table_new;
   -- etc per tutte le tabelle _new
   ```

2. Riprova la migrazione

### Se i campi sono ancora INTEGER:

Verifica con:
```sql
PRAGMA table_info(inventario_materiali_table);
```

Se il campo `us` o `area` mostra ancora `INTEGER`, la migrazione non è stata completata.

## Backup

**IMPORTANTE**: Fai sempre un backup del database prima di eseguire qualsiasi migrazione:

```bash
cp database.sqlite database.sqlite.backup_$(date +%Y%m%d_%H%M%S)
```