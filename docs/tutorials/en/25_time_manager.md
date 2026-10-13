# Tutorial 25: Time Manager (GIS Time Controller)

## Introduction

The **Time Manager** (GIS Time Controller) is an advanced tool for visualizing stratigraphic sequence over time. It allows "navigating" through stratigraphic levels using a temporal control, progressively displaying SU from oldest to most recent (the formation of the site).

### Main Features

- Progressive visualization of stratigraphic levels
- Control via dial/slider
- Cumulative or single level mode
- Automatic printing of the atlas sheets, one per level
- Integration with Harris Matrix

## Access

### From Menu
**PyArchInit** → **Time Manager**

### Prerequisites

- Layer with `order_layer` field (stratigraphic index)
- SU with order_layer filled in
- Layers loaded in QGIS

## Interface

### Main Panel

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Available layers:                                 |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] other_layer                                  |
+--------------------------------------------------+
|              [Circular Dial]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Level: [SpinBox: 0-N]                   |
+--------------------------------------------------+
| [ ] Cumulative Mode (show <= level)             |
+--------------------------------------------------+
| [ ] Display matrix                               |
| [Atlas Print Period Tables]                      |
| [Stop print process]                             |
+--------------------------------------------------+
| [Matrix/Image Preview]                           |
+--------------------------------------------------+
```

### Controls

| Control | Function |
|---------|----------|
| Tabs (top) | **Relative chronology system** (layer list, dial and level) and **Absolute chronology system** (search by years, see "Absolute Chronology") |
| Layer Checkbox | Select layers to control |
| Dial | Navigate between levels (rotation) |
| SpinBox | Direct level input |
| Cumulative Mode | Show all levels up to selected |
| Display matrix | Display synchronized Harris Matrix |

## order_layer Field

### What is order_layer?

The `order_layer` field defines the stratigraphic display order:
- **0** = Oldest level (deep)
- **N** = Most recent level (surface)

This is the convention of **Stratigraphic order** with "Order: Ancient → Recent" checked (the default, see Tutorial 03): if the ordering was calculated the other way round, the Time Manager and the map show the sequence upside down.

### Filling order_layer

In the SU Form, **Help** tab → **Tool Box**, the **Stratigraphic order** button calculates `order_layer` from the stratigraphic relationships (see Tutorial 03); the value of the current SU appears in the field below the button. Rules:
1. 0 for the oldest SU, increasing values towards the most recent (at the surface)
2. Contemporary SU can have the same value
3. Follow the Matrix sequence

### Example

| SU | order_layer | Description |
|----|-------------|-------------|
| SU001 | 4 | Surface humus |
| SU002 | 3 | Plowed layer |
| SU003 | 2 | Collapse |
| SU004 | 1 | Use floor |
| SU005 | 0 | Foundation |

Since 5.13.19-alpha the SU and USM layers that pyArchInit loads on the map (see Tutorial 14, *Style Choice*) are drawn in the same order the Time Manager uses: by period chronology, then by `order_layer` (0 = oldest), so the most recent units are on top.

## Visualization Modes

### Single Level Mode

Checkbox **NOT** active:
- Shows ONLY SU of selected level
- Useful for isolating single layers
- "Slice" visualization

### Cumulative Mode

Checkbox **ACTIVE**:
- Shows all SU from level 0 (oldest) to the selected one
- Shows the formation of the site, from the oldest SU to the most recent
- More realistic visualization

### Absolute Chronology

The window's second tab, **Absolute chronology system**, works on years instead of the `order_layer` levels: you choose a time interval and the SU of the periods that overlap that interval are loaded onto the map. It requires the Periodization to be filled in (see Tutorial 04), with the **Initial Chronology** and **Final Chronology** of each period and phase: a period without years is not found.

**Controls.**

- **Initial chronology** and **Final chronology**: two numeric boxes, read as "Displays the time interval between the year: … and the year …". Years go from `-4,000,000` to `2100`: negative values are BC (268 BC = `-268`), positive values are AD with no sign (1400 AD = `1400`). The older year goes in Initial chronology.
- **View** button: starts the search.

**What View does.**

1. It looks in the Periodization (of all the sites in the database) for the periods and phases whose dating **overlaps** the interval, that is, that do not end before the initial year and do not begin after the final year. If it finds none, it warns "There are no Periods in this time interval" and stops.
2. It takes the SU whose initial period and initial phase match those found. If there are none, it warns "There are no geometries to display".
3. It loads the layers of those SU onto the map, with the same loader as the SU form (see Tutorial 03).
4. It refreshes the Matrix preview, if **Display matrix** is active: the preview follows the ticked layers and the level of the relative tab, not the year interval.

**Difference from the relative tab.** The dial and the cumulative mode **filter** layers that are already loaded; **View**, instead, **adds** a new group of layers to the project at every click (the earlier ones stay in the project). As in the SU form, with a PostgreSQL database the loader filters by site and not by single SU: the layers show the whole site.

## Matrix Integration

### Synchronized Visualization

With **"Display matrix"** checkbox active:
- Harris Matrix appears in panel
- Updates in sync with level
- Highlights current level SU

### Image Generation

Time Manager can generate:
- A sheet for each level, laid out with the chosen layout template (JPG image)
- The Harris Matrix of that level inside the sheet, if **Display matrix** is active

## Printing the Sheets

### Process

1. Select layers to include
2. Activate **Display matrix** if the Matrix must appear on the sheets (otherwise the template's Matrix picture is hidden)
3. Click **Atlas Print Period Tables**
4. In the window that opens, choose the layout template (see the note "Which template to pick" at the bottom) and confirm
5. Choose the folder where the sheets will be saved
6. Answer the question whether to open the Layout Designer to touch up the template before starting
7. Wait: a progress bar shows the sheet being generated and, when it is done, a message says where the sheets were saved
8. To stop the generation click **Stop print process**: the sheets already written stay in the folder

### Output

- One `Tavola_N.jpg` for each level (N is the `order_layer` value), in the chosen folder: the map at that level, in the active mode (cumulative or single level)
- The «Tavola N» title and the Matrix picture appear if the template has them (the Matrix only with **Display matrix** active)
- Levels where no SU has its dating filled in are skipped: those numbers are missing from the sequence of files
- With a two-page template each level produces two images, the second one being `Tavola_N_2.jpg` (see the note "Making any template suitable" at the bottom)

**Sheet labels.** While it generates the atlas sheets, the Time Manager puts the sheet labels on the chosen layers — the unit number in a circle on the SUs, the elevation on the points — and removes them when the generation ends, putting back the ones that were there before. Since 5.13.110-alpha it removes them in any case, even if a sheet fails: before, in that case, they stayed on the project's layers and ended up in the project file when it was saved.

## Typical Workflow

### 1. Preparation

```
1. Open QGIS project with SU layers
2. Verify order_layer is filled in
3. Open Time Manager
```

### 2. Layer Selection

```
1. Select layers to control
2. Usually: pyunitastratigrafiche and/or _usm
```

### 3. Navigation

```
1. Use dial or spinbox
2. Observe visualization change
3. Enable/disable cumulative mode
```

### 4. Documentation

```
1. Enable "Display matrix"
2. Print the sheets with "Atlas Print Period Tables"
3. Check the Tavola_N.jpg files in the chosen folder
```

## Layout Templates

### Template Loading

Time Manager supports QGIS templates for:
- Custom print layouts
- Headers and legends
- Standard formats

### Available Templates

The chooser window lists the `.qpt` files found in the plugin folder, in `resources/dbfiles/` and in `~/pyarchinit_5/bin/profile/template/`:
- `layout_TimeManager`: the Time Manager template, with the «Tavola N» title and the Matrix picture
- the print templates of the pyArchInit profile (for example the «Modello adArte…» ones)
- any other `.qpt`, picked with the **Sfoglia...** (Browse) button

## Best Practices

### 1. order_layer

- Fill in BEFORE using Time Manager
- Use consecutive values
- Contemporary SU = same value

### 2. Visualization

- Start from level 0 (oldest)
- Proceed in ascending order
- Use cumulative mode for presentations

### 3. Documentation

- Capture screenshots at significant levels
- Document phase transitions
- Print the sheets for reports (one per level)

## Troubleshooting

### Layers Not Visible in List

**Cause**: Layer without order_layer field

**Solution**:
- Add order_layer field to layer
- Populate with appropriate values

### No Visual Change

**Causes**:
- order_layer not filled in
- Filter not applied

**Solutions**:
- Verify order_layer values in SU
- Check that layer is selected

### Dial Not Responding

**Cause**: No layer selected

**Solution**: Select at least one layer from list

## References

### Source Files
- `tabs/Gis_Time_controller.py` - Main interface
- `gui/ui/Gis_Time_controller.ui` - UI layout

### Database Field
- `us_table.order_layer` - Stratigraphic index

---

## Video Tutorial

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Contents**:
- order_layer configuration
- Temporal navigation
- Printing the sheets
- Matrix integration

**Expected duration**: 15-18 minutes

---

*Last updated: October 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_timemanager_animation.html)

---

## The matrix, from 5.13.44

The Time Manager's matrix no longer goes through Graphviz. It is drawn by the same layout engine as the **See the matrix** panel, inside QGIS and with no subprocesses.

- **It is immediate.** On the sample site (51 SU, 81 relations) the drawing costs a few milliseconds instead of roughly three tenths of a second, and the `dot` and `tred` processes that occasionally hung are gone. The site's periods are read **once**: before, they were re-read with one query per area and per period, on every click of the dial.
- **In the atlas the matrix is vector.** The picture placed in the sheet is an SVG of a few tens of KB instead of a JPEG of megabytes: it stays readable at any scale and the sheet weighs less.
- **It is the same matrix** as the Extended Matrix panel: same period bands, same symbology, same redundancy reduction. Arrows that **climb** the bands — where stratigraphy contradicts chronology — are drawn in **red**.
- The matrix still holds only the SU visible at the dial's current position.

- Units that are **not visible** at the current position but are cited by a relationship still enter the drawing, **faded**: without them the sequence would look broken, and drawn like the others they would look as if they were on the map.

> **Which template to pick.** In the chooser each template is marked: **✓** has the «Tavola N» title and the matrix picture (that is the Time Manager one, `layout_TimeManager`), **•** has only the map — sheets come out plainer but they come out — **✗** has no map and cannot be used. Picking one without those two items used to make the generator return without a word, and no sheet appeared.

> **Making any template suitable.** Generic templates can be prepared: `scripts/prepare_atlas_templates.py`, run with QGIS's Python, writes beside each one a copy suffixed « + Time Manager» carrying the title and the matrix picture on a **new page**, so nothing already there is covered. The originals are untouched. Each level then produces two images: `Tavola_N.jpg` with the map and `Tavola_N_2.jpg` with the matrix.
