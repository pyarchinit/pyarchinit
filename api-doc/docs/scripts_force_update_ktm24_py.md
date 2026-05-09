# scripts/force_update_ktm24.py

## Overview

This file contains 3 documented elements.

## Functions

### main()

Forza l'aggiornamento del database ktm24.sqlite

### force_update()

*No description available.*
A locally defined function that bypasses the standard `check_and_update_database` method by directly invoking `updater.update_database()`. It is used to temporarily override the updater's normal check-and-confirm workflow, forcing an immediate database update without prompting the user for confirmation. This function is assigned to `updater.check_and_update_database` for the duration of the operation.

