# modules/s3dgraphy/spatial_grouping_manager.py

## Overview

This file contains 19 documented elements.

## Classes

### SpatialGroupingManager

Manages spatial/functional groupings of stratigraphic units
for Extended Matrix visualization

#### Methods

##### __init__(self)

Initializes a new instance of the stratigraphic unit groupings manager. Sets up an empty `groupings` dictionary to store group name-to-unit list mappings, and populates the `grouping_types` dictionary with five predefined grouping categories: `'area'`, `'settore'`, `'struttura'`, `'funzione'`, and `'custom'`, each mapped to its corresponding display label.

##### create_area_based_groups(self, us_data)

Create groups based on area field

##### create_sector_based_groups(self, us_data)

Create groups based on settore field

##### create_structure_based_groups(self, us_data)

Create groups based on struttura field or interpretation

##### create_custom_groups(self, us_data, custom_rules)

Create custom groups based on user-defined rules

Args:
    us_data: List of US records
    custom_rules: Dict of {group_name: [list of US numbers or patterns]}

##### apply_grouping_to_dot(self, dot_content, groupings)

Modify DOT content to add subgraph clusters for groupings

### SpatialGroupingDialog

Dialog for configuring spatial/functional groupings

**Inherits from**: QDialog

#### Methods

##### __init__(self, us_data, parent)

Initializes the dialog for configuring spatial/functional groupings, accepting a list of unit dictionaries (`us_data`) and an optional parent widget. Sets the instance attributes `us_data`, `manager` (a `SpatialGroupingManager` instance), and `selected_groupings` (an empty dictionary). Configures the window title to `"Configurazione Raggruppamenti Spaziali/Funzionali"`, sets the minimum window size to 800×600, and invokes `setupUI()` to build the interface.

##### setupUI(self)

Initialises and assembles the complete user interface for the spatial/functional grouping configuration dialog. It constructs a vertical layout containing a title label, a horizontal splitter with a left panel (grouping type selector, preview button, and a conditionally visible custom groupings panel with an input field and table) and a right panel (preview list and group details list), a predefined location groupings section with a grid of fifteen checkboxes, and a bottom button row with "Applica" and "Annulla" buttons. Widget references are stored as instance attributes and signals are connected to their respective handler methods (`on_grouping_type_changed`, `preview_groupings`, `add_custom_group`, `apply_location_groupings`, `show_group_details`, `accept`, and `reject`).

##### on_grouping_type_changed(self)

Handle grouping type change

##### preview_groupings(self)

Preview groupings based on selected type

##### update_preview_list(self)

Update the preview list with current groupings

##### show_group_details(self)

Show details of selected group

##### add_custom_group(self)

Add a custom group

##### get_custom_rules(self)

Get custom grouping rules from table

##### apply_location_groupings(self)

Apply groupings based on location keywords

##### get_groupings(self)

Get the configured groupings

