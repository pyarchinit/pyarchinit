# gui/pyarchinit_splash.py

## Overview

This file contains 21 documented elements.

## Classes

### Particle

A single particle in the field.

#### Methods

##### __init__(self, w, h)

Initializes a new `Particle` instance with randomized spatial and motion attributes derived from the provided canvas dimensions `w` and `h`. Position (`x`, `y`) is distributed uniformly across the canvas, depth `z` is sampled from the range `[0.2, 1.0]`, and velocity components (`vx`, `vy`) are computed from a random angle and a speed scaled by `z`. Visual properties including `size`, `alpha`, and `color_idx` are also randomized, while `life` is set to `0.0` and `max_life` is assigned a random duration between `3.0` and `8.0`.

### OrbitalRing

An orbiting ring around the logo.

#### Methods

##### __init__(self, radius, speed, tilt, width, dot_count)

Initializes an `OrbitalRing` instance with the given orbital parameters. The `radius`, `speed`, `tilt`, `width`, and `dot_count` arguments are assigned directly to their corresponding attributes, while `angle` is set to a random value in the range `[0, 360)` and `color_phase` is set to a random value in the range `[0, 2π)`. The `width` parameter defaults to `1.5` and `dot_count` defaults to `0` if not provided.

### FuturisticSplashWidget

Widget rendering the futuristic animated splash content.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes the widget by calling the parent constructor with the optional `parent` argument and setting a minimum size of 700×500 pixels. Establishes all animation state variables, including time-tracking counters, a particle system (capped at 90 particles), four `OrbitalRing` instances, five randomly parameterized energy nodes, a scanning grid offset, a hexagonal wave phase, and a logo pulse value. Loads the primary logo from `logo_pyarchinit.png` (falling back to `IconPAI.png`) and two partner logos (`logo_cnr_ispc.png`, `logo_horizon_stratigraph.png`) from the `resources/icons` directory, then configures a `QTimer` with `PreciseTimer` type connected to `_tick` for driving the animation loop.

##### start_animation(self)

*No description available.*
Initializes and starts the animation loop by recording the current time via `time.perf_counter()` into both `_t0` and `_last_t`, then starts the internal `QTimer` with a 16-millisecond interval (approximately 60 FPS). Each timer tick triggers the `_tick` callback connected during setup.

##### stop_animation(self)

*No description available.*
Stops the animation by halting the internal timer. This effectively ceases the periodic updates that drive the animation loop, which was previously started at approximately 60 FPS.

##### set_status(self, text)

Sets the status text to be displayed, triggering a reset of the animated text output. If the provided `text` differs from the current `_status_text`, the method updates `_status_text`, clears `_displayed_text` to an empty string, and resets the character timer `_char_timer` to `0.0`. No action is taken if `text` is identical to the existing status text.

##### paintEvent(self, event)

Handles the widget's paint event by constructing the full splash screen frame using a `QPainter` instance configured with antialiasing and smooth pixmap transform render hints. It renders all visual layers in order: a deep-space radial gradient background, a scanning grid, a particle field, energy wave rings, orbital rings, energy nodes, a central logo with glow, title text, status text, bottom info, partner logos, and corner accents. The elapsed time value `self._elapsed` is passed to each drawing subroutine to drive time-based animations across all layers.

### PyArchInitSplash

Splash screen dialog for PyArchInit.

Displays a futuristic, always-in-motion splash with particle effects,
orbital rings, and dynamic animations.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, message, modal)

Initializes the splash screen dialog with a frameless, always-on-top window that remains translucent against its background. Accepts an optional parent widget, a display message defaulting to `"Loading PyArchInit..."`, and a boolean `modal` flag defaulting to `False`. After applying window flags and attributes, delegates UI construction to `init_ui` with the provided message.

##### init_ui(self, message)

Initialize the UI components.

##### center_on_screen(self)

Center the splash screen on the primary screen.

##### set_message(self, message)

Update the status message.

##### showEvent(self, event)

Handles the show event for the widget by delegating to the parent class implementation via `super().showEvent(event)`. After the parent handler completes, it starts the splash widget's animation by calling `self.splash_widget.start_animation()`.

##### hideEvent(self, event)

Handles the widget's hide event by stopping the splash widget's animation before delegating to the parent class implementation. This ensures the animation is cleanly halted whenever the widget becomes hidden. The method follows the standard Qt event override pattern, invoking `super().hideEvent(event)` after performing its own cleanup logic.

##### closeEvent(self, event)

*No description available.*
Handles the window close event by stopping the splash widget's animation before delegating to the parent class implementation via `super().closeEvent(event)`. This ensures that any running animation is properly halted when the window is closed.

## Functions

### show_splash_during_operation(operation_func, message, parent)

Show the splash screen while executing an operation.

Args:
    operation_func: Function to execute while showing splash
    message: Initial message to display
    parent: Parent widget

Returns:
    The result of operation_func

**Parameters:**
- `operation_func`
- `message`
- `parent`

### update_message()

Schedules a sequential series of status messages to be displayed on the splash screen at 2-second intervals using `QTimer.singleShot`. The messages cycle through initialization steps — including database scanning, module loading, GIS calibration, and data layer synchronization — before closing the splash screen after all messages have been shown. This function is called once immediately after the splash screen is displayed to simulate application startup progress.

