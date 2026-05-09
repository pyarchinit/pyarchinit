# modules/db/db_updater.py

## Overview

This file contains 5 documented elements.

## Classes

### DatabaseUpdater

Handles automatic database updates when connecting

#### Methods

##### __init__(self, db_manager)

*No description available.*
Initializes the instance by storing the provided `db_manager` reference and retrieving the `PYARCHINIT_HOME` path from the environment variable of the same name. Sets up the two instance attributes `self.db_manager` and `self.HOME` required by the class that handles automatic database updates when connecting.

##### check_and_update_triggers(self)

Check and update database triggers to ensure they're compatible
with multi-user permission system

##### update_create_doc_trigger(self)

Update the create_doc trigger to handle permission issues

