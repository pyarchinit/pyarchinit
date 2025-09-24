# Inventario Materiali Fixes - January 2025

## Issues Fixed

### 1. Compilatore ComboBox Not Saving to Schedatore Field
- **Problem**: The comboBox_compilatore was not populated with values from the thesaurus, so it couldn't save data to the schedatore field
- **Solution**: Added code in `charge_list()` to populate comboBox_compilatore from thesaurus using code '3.14'
- **SQL Required**: Run `add_compilatore_thesaurus.sql` to add the thesaurus entries for compilatore/schedatore

### 2. Tipologia ComboBox Maintaining Same Value Across Records
- **Problem**: The comboBox_tipologia was not properly mapped to the database field, causing it to show the same value for all records
- **Solution**: Changed the field mapping so comboBox_tipologia is used for the "tipo" field (position 24/25) instead of comboBox_tipo_reperto being used twice

### 3. Measurements Table Data Disappearing After Save
- **Problem**: Table data (misurazioni, elementi_reperto, etc.) was saved as string but not properly loaded back
- **Solution**: Added `ast.literal_eval()` to convert string data back to lists when loading from database in `fill_fields()`

### 4. Datazione ComboBox Should Read from Thesaurus
- **Problem**: The datazione field was populated from US table datazione values instead of using thesaurus
- **Solution**: Changed to load datazione from thesaurus using code '10.4' (same as TMA dtzg field)

## Files Modified
- `/tabs/Inv_Materiali.py` - Main form controller with all fixes applied

## Database Changes Required
Execute the following SQL to add compilatore thesaurus entries:
```sql
-- Run add_compilatore_thesaurus.sql
```

## Testing Checklist
- [ ] Verify compilatore combobox populates with values from thesaurus
- [ ] Verify compilatore saves to schedatore field in database
- [ ] Verify tipologia combobox shows correct value for each record
- [ ] Verify measurements table data persists after save and reload
- [ ] Verify datazione combobox shows thesaurus values
- [ ] Test navigation between records - all fields should load correctly