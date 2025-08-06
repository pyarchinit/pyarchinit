# TMA Thesaurus Synchronization Updates

## Important: Understanding Table Names and Type Codes

### Table Names in Thesaurus
- Areas from `us_table` are saved with `nome_tabella = 'US'`
- Areas from TMA tables are saved with `nome_tabella = 'TMA materiali archeologici'`
- Sectors from `us_table` are saved with `nome_tabella = 'US'`
- Sectors from TMA are saved with `nome_tabella = 'TMA materiali archeologici'`

### Type Codes (tipologia_sigla)
- US areas use code `2.43`
- TMA areas use code `10.7`
- US sectors use code `2.21` 
- TMA sectors use code `10.15`

## Summary of Changes

### 1. Enhanced Area and Settore Synchronization

The sync functions have been updated to:

- **Add source tracking**: When syncing areas and settori, the source table is now tracked in the `descrizione` field
- **Prevent duplicates**: Check existing records by comparing `sigla`, `sigla_estesa`, and `descrizione` fields
- **Update descriptions**: If a record already exists, the description is updated to show all source tables

### 2. New Sync Methods

Added two new comprehensive sync methods:

- `sync_all_areas_to_thesaurus()`: Syncs all areas from all relevant tables (us_table, inventario_materiali_table, tomba_table, individui_table, tma_materiali_archeologici)
- `sync_all_settori_to_thesaurus()`: Syncs all settori from us_table and tma_materiali_archeologici

### 3. Updated Sync Functions

Modified `sync_area_to_thesaurus()` and `sync_settore_to_thesaurus()` to:

- Accept optional `source_table` parameter for tracking origin
- Check for existing records using all three fields (sigla, sigla_estesa, descrizione)
- Update description field if record exists to track multiple sources
- Convert area/settore values to string to handle numeric areas

### 4. UI Integration

Updated the Thesaurus tab sync button to use the new comprehensive methods instead of iterating through tables manually.

## Usage

When you click the "Sincronizza Thesaurus TMA" button in the Thesaurus interface:

1. All areas from all tables will be synchronized to the thesaurus
2. All settori from us_table and tma will be synchronized
3. All material fields from inventario_materiali will be synchronized
4. The description field will show which table(s) the value was synchronized from

## Example

If area "7" exists in both us_table and tma_materiali_archeologici:
- First sync from us_table: description = "Sincronizzato da us_table"
- Second sync from tma: description = "Sincronizzato da us_table; Sincronizzato anche da tma_materiali_archeologici"

## Testing

To verify the synchronization is working properly:

1. Open QGIS and load the PyArchInit plugin
2. Go to the Thesaurus interface
3. Click "Sincronizza Thesaurus TMA"
4. Check the QGIS message log for sync results
5. Query the thesaurus for area/settore records to see the source tracking in descriptions