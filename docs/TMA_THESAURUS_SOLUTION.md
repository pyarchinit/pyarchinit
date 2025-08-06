# TMA Thesaurus Table Naming Solution

## Problem
The TMA form was looking for thesaurus entries with table names like `'TMA materiali archeologici'` but the database might have entries with the actual database table names like `'tma_table'` and `'tma_materiali_table'`. This causes dropdowns to not populate correctly.

## Solution
We've implemented a backward-compatible solution that:

1. **Uses friendly UI names** in the thesaurus instead of database table names
2. **Maintains backward compatibility** with forms that might still use the old names
3. **Provides migration scripts** to update existing databases

## Key Changes

### 1. Correct Table Names
- `tma_table` → `TMA materiali archeologici`
- `tma_materiali_table` → `TMA Materiali Ripetibili` (note the capital M and R)

### 2. Updated Files

#### scripts/insert_tma_thesaurus_alias.sql
- Now inserts entries with friendly UI names
- Cleans up old entries with database table names

#### scripts/migrate_tma_table_names.sql
- Migration script to update existing databases
- Updates all variations of table names to the correct ones

#### modules/db/pyarchinit_db_update_thesaurus.py
- Added mappings for TMA tables to the automatic update system
- Handles case variations

#### modules/utility/pyarchinit_thesaurus_compatibility.py
- New compatibility layer for handling table name variations
- Provides helper functions for backward compatibility

#### tabs/Tma.py
- Updated to use the correct case: `'TMA Materiali Ripetibili'`

## How to Apply

### For New Installations
The correct table names will be used automatically.

### For Existing Databases
Run the migration script:
```sql
-- In your database client, execute:
scripts/migrate_tma_table_names.sql
```

Or the update will happen automatically when the plugin loads if pyarchinit_db_update_thesaurus is triggered.

## Testing
Use `test_tma_thesaurus_compatibility.py` to verify your database has the correct table names.

## Backward Compatibility
The system now handles these variations:
- `tma_table` / `TMA materiali archeologici` / `tma_materiali_archeologici`
- `tma_materiali_table` / `TMA Materiali Ripetibili` / `TMA materiali ripetibili` / `tma_materiali_ripetibili`

All forms should work regardless of which variation they use, but new code should use the friendly UI names.