# modules/db/sync_postgres_permissions.py

## Overview

This file contains 32 documented elements.

## Classes

### PostgresPermissionSync

Synchronize PyArchInit permissions with PostgreSQL

#### Methods

##### __init__(self, db_manager)

##### create_postgres_user(self, username, password, role)

Create a PostgreSQL user if it doesn't exist

Args:
    username: Username to create
    password: Password for the user
    role: PyArchInit role (admin, archeologo, studente, guest)

##### sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete)

Sync permissions for a specific table

Args:
    username: Username
    table_name: Table name
    can_view: SELECT permission
    can_insert: INSERT permission
    can_update: UPDATE permission
    can_delete: DELETE permission

##### sync_all_permissions(self)

Sync all permissions from pyarchinit_permissions table to PostgreSQL

##### apply_role_based_permissions(self, username, role)

Apply default permissions based on role

Args:
    username: Username
    role: Role (admin, archeologo, studente, guest)

### PostgresPermissionSync

Synchronize PyArchInit permissions with PostgreSQL

#### Methods

##### __init__(self, db_manager)

##### create_postgres_user(self, username, password, role)

Create a PostgreSQL user if it doesn't exist

Args:
    username: Username to create
    password: Password for the user
    role: PyArchInit role (admin, archeologo, studente, guest)

##### sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete)

Sync permissions for a specific table

Args:
    username: Username
    table_name: Table name
    can_view: SELECT permission
    can_insert: INSERT permission
    can_update: UPDATE permission
    can_delete: DELETE permission

##### sync_all_permissions(self)

Sync all permissions from pyarchinit_permissions table to PostgreSQL

##### apply_role_based_permissions(self, username, role)

Apply default permissions based on role

Args:
    username: Username
    role: Role (admin, archeologo, studente, guest)

### PostgresPermissionSync

Synchronize PyArchInit permissions with PostgreSQL

#### Methods

##### __init__(self, db_manager)

##### create_postgres_user(self, username, password, role)

Create a PostgreSQL user if it doesn't exist

Args:
    username: Username to create
    password: Password for the user
    role: PyArchInit role (admin, archeologo, studente, guest)

##### sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete)

Sync permissions for a specific table

Args:
    username: Username
    table_name: Table name
    can_view: SELECT permission
    can_insert: INSERT permission
    can_update: UPDATE permission
    can_delete: DELETE permission

##### sync_all_permissions(self)

Sync all permissions from pyarchinit_permissions table to PostgreSQL

##### apply_role_based_permissions(self, username, role)

Apply default permissions based on role

Args:
    username: Username
    role: Role (admin, archeologo, studente, guest)

### PostgresPermissionSync

Synchronize PyArchInit permissions with PostgreSQL

#### Methods

##### __init__(self, db_manager)

##### create_postgres_user(self, username, password, role)

Create a PostgreSQL user if it doesn't exist

Args:
    username: Username to create
    password: Password for the user
    role: PyArchInit role (admin, archeologo, studente, guest)

##### sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete)

Sync permissions for a specific table

Args:
    username: Username
    table_name: Table name
    can_view: SELECT permission
    can_insert: INSERT permission
    can_update: UPDATE permission
    can_delete: DELETE permission

##### sync_all_permissions(self)

Sync all permissions from pyarchinit_permissions table to PostgreSQL

##### apply_role_based_permissions(self, username, role)

Apply default permissions based on role

Args:
    username: Username
    role: Role (admin, archeologo, studente, guest)

## Functions

### sync_permissions_from_ui(db_manager)

Function to be called from PyArchInit UI after creating/modifying users

**Parameters:**
- `db_manager`

### sync_permissions_from_ui(db_manager)

Function to be called from PyArchInit UI after creating/modifying users

**Parameters:**
- `db_manager`

### sync_permissions_from_ui(db_manager)

Function to be called from PyArchInit UI after creating/modifying users

**Parameters:**
- `db_manager`

### sync_permissions_from_ui(db_manager)

Function to be called from PyArchInit UI after creating/modifying users

**Parameters:**
- `db_manager`

