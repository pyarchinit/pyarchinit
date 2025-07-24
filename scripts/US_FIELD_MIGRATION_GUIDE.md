
PyArchInit US Field Migration Instructions
==========================================

This migration changes the US (Unità Stratigrafica) field from INTEGER to STRING
to support alphanumeric values (e.g., "US001", "US-A", "2024/001").

DATABASE MIGRATION:
------------------
1. BACKUP YOUR DATABASE FIRST!
2. Run the appropriate migration script:
   - PostgreSQL: migration_us_to_string.sql
   - SQLite: migration_us_to_string_sqlite.sql

ENTITY CLASSES:
---------------
Run: python update_entities_us_field.py
This will automatically update all SQLAlchemy table structures.

FORM UPDATES:
-------------
The following manual changes are needed in the form classes:


### US_USM.py - Main US/USM form

Method: insert_new_rec
  Replace: int(self.lineEdit_us.text())
  With:    str(self.lineEdit_us.text())
  Note:    Change US field from int to str in insert

Method: on_pushButton_search_go_pressed
  Replace: int(self.lineEdit_us.text())
  With:    str(self.lineEdit_us.text())
  Note:    Change US search from int to str

Method: fill_fields
  Replace: str(self.DATA_LIST[self.rec_num].us)
  With:    self.DATA_LIST[self.rec_num].us
  Note:    Remove str() conversion as field is already string

Method: data_error_check
  Note:    Remove integer validation for US field

### Campioni.py - Samples form

Method: insert_new_rec
  Replace: int(self.lineEdit_us.text())
  With:    str(self.lineEdit_us.text())
  Note:    Change US field from int to str

Method: fill_fields
  Replace: str(self.DATA_LIST[self.rec_num].us)
  With:    self.DATA_LIST[self.rec_num].us
  Note:    Remove str() conversion

### pyarchinit_Pottery_mainapp.py - Pottery form

Method: insert_new_rec
  Replace: int(self.lineEdit_us.text())
  With:    str(self.lineEdit_us.text())
  Note:    Change US field from int to str

### Inv_Materiali.py - Materials inventory form
Note: Already handles US as text - no changes needed

### Schedaind.py - Individual form
Note: Already handles US as text - no changes needed


VALIDATION UPDATES:

# Old validation (remove this):
if EC.data_is_int(self.lineEdit_us.text()) == 0:
    QMessageBox.warning(self, "ATTENZIONE", "Campo US. Il valore deve essere di tipo numerico", QMessageBox.Ok)
    test = 1

# New validation (add this):
if EC.data_is_empty(self.lineEdit_us.text()) == 0:
    QMessageBox.warning(self, "ATTENZIONE", "Campo US. Il campo non deve essere vuoto", QMessageBox.Ok)
    test = 1


SEARCH AND FILTER UPDATES:
-------------------------
1. Update any numeric comparisons (>, <, >=, <=) to string comparisons
2. Update ORDER BY clauses to handle alphanumeric sorting
3. Consider adding a natural sort function for US values

TESTING CHECKLIST:
-----------------
[ ] Test inserting new US records with alphanumeric values
[ ] Test searching for US records
[ ] Test sorting US records
[ ] Test relationships with other tables
[ ] Test GIS views and joins
[ ] Test data export/import functions
[ ] Test report generation

ROLLBACK PROCEDURE:
------------------
If issues arise, restore from backup and run the reverse migration scripts.
