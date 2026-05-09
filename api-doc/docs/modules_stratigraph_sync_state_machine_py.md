# modules/stratigraph/sync_state_machine.py

## Overview

This file contains 8 documented elements.

## Classes

### SyncState

Possible states in the sync lifecycle.

**Inherits from**: Enum

### SyncStateMachine

State machine governing the sync lifecycle.

Persists current state and transition history via QgsSettings.
Emits Qt signals on every transition for UI reactivity.

**Inherits from**: QObject

#### Methods

##### __init__(self, parent)

Initializes the instance by calling the parent class constructor with the optional `parent` argument. Instantiates a `QgsSettings` object assigned to `_settings` and loads the persisted state via `_load_state()`, storing the result in `_state`.

##### current_state(self)

*No description available.*
**Type:** `property`  
**Returns:** `SyncState`

Returns the current synchronization state of the instance. This read-only property exposes the internal `_state` attribute as part of the public API.

##### transition(self, new_state, context)

Attempt a state transition.

Args:
    new_state: Target state.
    context: Optional metadata stored in transition history.

Returns:
    True if the transition succeeded, False otherwise.

##### get_transition_history(self, limit)

Return the most recent *limit* transition entries (newest first).

##### reset(self)

Reset to OFFLINE_EDITING and clear history.

