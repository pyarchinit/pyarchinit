# modules/gui/pyarchinit_form_base.py

## Overview

This file contains 64 documented elements.

## Classes

### PyArchInitFormMixin

Mixin class for PyArchInit forms providing common functionality
This should be inherited by all PyArchInit forms to ensure consistent behavior

#### Methods

##### setup_refresh_timer(self)

Setup refresh timer for checking concurrent modifications
This method should be called during form initialization

##### stop_refresh_timer(self)

Stop the refresh timer
Should be called when form is closed or hidden

##### closeEvent(self, event)

Handle form close event
Ensures timer is stopped when form closes

##### hideEvent(self, event)

Handle form hide event
Stops timer when form is hidden/minimized

##### showEvent(self, event)

Handle form show event
Restarts timer when form is shown again

##### check_for_updates_safe(self)

Wrapper around check_for_updates that checks if form is active
Prevents notifications from appearing when form is closed

##### handle_permission_error(self, error, operation)

Centralized permission error handler
Returns True if error was handled, False otherwise

##### get_operation_name_it(self, operation)

Get Italian translation for operations

##### handle_database_error(self, error, context)

Centralized database error handler
Shows user-friendly messages without SQL details

### FormStateManager

Manages form state to prevent false modification notifications

#### Methods

##### __init__(self, form)

##### capture_state(self)

Capture current form state

##### has_changes(self)

Check if form has changes

##### set_loading(self, loading)

Set loading state

### PyArchInitFormMixin

Mixin class for PyArchInit forms providing common functionality
This should be inherited by all PyArchInit forms to ensure consistent behavior

#### Methods

##### setup_refresh_timer(self)

Setup refresh timer for checking concurrent modifications
This method should be called during form initialization

##### stop_refresh_timer(self)

Stop the refresh timer
Should be called when form is closed or hidden

##### closeEvent(self, event)

Handle form close event
Ensures timer is stopped when form closes

##### hideEvent(self, event)

Handle form hide event
Stops timer when form is hidden/minimized

##### showEvent(self, event)

Handle form show event
Restarts timer when form is shown again

##### check_for_updates_safe(self)

Wrapper around check_for_updates that checks if form is active
Prevents notifications from appearing when form is closed

##### handle_permission_error(self, error, operation)

Centralized permission error handler
Returns True if error was handled, False otherwise

##### get_operation_name_it(self, operation)

Get Italian translation for operations

##### handle_database_error(self, error, context)

Centralized database error handler
Shows user-friendly messages without SQL details

### FormStateManager

Manages form state to prevent false modification notifications

#### Methods

##### __init__(self, form)

##### capture_state(self)

Capture current form state

##### has_changes(self)

Check if form has changes

##### set_loading(self, loading)

Set loading state

### PyArchInitFormMixin

Mixin class for PyArchInit forms providing common functionality
This should be inherited by all PyArchInit forms to ensure consistent behavior

#### Methods

##### setup_refresh_timer(self)

Setup refresh timer for checking concurrent modifications
This method should be called during form initialization

##### stop_refresh_timer(self)

Stop the refresh timer
Should be called when form is closed or hidden

##### closeEvent(self, event)

Handle form close event
Ensures timer is stopped when form closes

##### hideEvent(self, event)

Handle form hide event
Stops timer when form is hidden/minimized

##### showEvent(self, event)

Handle form show event
Restarts timer when form is shown again

##### check_for_updates_safe(self)

Wrapper around check_for_updates that checks if form is active
Prevents notifications from appearing when form is closed

##### handle_permission_error(self, error, operation)

Centralized permission error handler
Returns True if error was handled, False otherwise

##### get_operation_name_it(self, operation)

Get Italian translation for operations

##### handle_database_error(self, error, context)

Centralized database error handler
Shows user-friendly messages without SQL details

### FormStateManager

Manages form state to prevent false modification notifications

#### Methods

##### __init__(self, form)

##### capture_state(self)

Capture current form state

##### has_changes(self)

Check if form has changes

##### set_loading(self, loading)

Set loading state

### PyArchInitFormMixin

Mixin class for PyArchInit forms providing common functionality
This should be inherited by all PyArchInit forms to ensure consistent behavior

#### Methods

##### setup_refresh_timer(self)

Setup refresh timer for checking concurrent modifications
This method should be called during form initialization

##### stop_refresh_timer(self)

Stop the refresh timer
Should be called when form is closed or hidden

##### closeEvent(self, event)

Handle form close event
Ensures timer is stopped when form closes

##### hideEvent(self, event)

Handle form hide event
Stops timer when form is hidden/minimized

##### showEvent(self, event)

Handle form show event
Restarts timer when form is shown again

##### check_for_updates_safe(self)

Wrapper around check_for_updates that checks if form is active
Prevents notifications from appearing when form is closed

##### handle_permission_error(self, error, operation)

Centralized permission error handler
Returns True if error was handled, False otherwise

##### get_operation_name_it(self, operation)

Get Italian translation for operations

##### handle_database_error(self, error, context)

Centralized database error handler
Shows user-friendly messages without SQL details

### FormStateManager

Manages form state to prevent false modification notifications

#### Methods

##### __init__(self, form)

##### capture_state(self)

Capture current form state

##### has_changes(self)

Check if form has changes

##### set_loading(self, loading)

Set loading state

