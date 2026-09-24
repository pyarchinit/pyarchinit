"""Show in a combo box a value that comes from another sheet.

Period and phase of the US sheet are chosen, not typed: the list is
filled from the Periodizzazione sheet. The four boxes were made editable
at start-up (customize_GUI) only because fill_fields writes the value of
the record into them with setEditText(), which does nothing on a combo
box that is not editable — the same reason why "Unità tipo" never showed
the type held in the record (2026-09-24). Choosing the value instead of
writing it lets the boxes stay closed to free typing, so a period that
Periodizzazione does not know cannot be typed in by mistake.

Two things a database holds that the list may not have: a value saved
before its period was renamed or removed in Periodizzazione, and a
database whose Periodizzazione was never filled in at all (485 US of a
real database hold periods 1..7 with an empty Periodizzazione table).
Such a value is added to the list of that box, so the sheet keeps
showing what the record holds and saving the record does not wipe it.

The value is set without waking the handlers of the box: they recompute
the dating from Periodizzazione and would make a record nobody touched
look modified.
"""


def show_value(combo, value):
    """Show ``value`` in ``combo``, adding it to the list when the list
    does not have it; an empty value leaves the box empty. Returns True
    when a value is shown."""
    text = '' if value is None else str(value).strip()
    blocked = combo.blockSignals(True)
    try:
        if not text:
            if combo.isEditable():
                combo.setEditText('')
            combo.setCurrentIndex(-1)
            return False
        index = combo.findText(text)
        if index < 0:
            combo.addItem(text)
            index = combo.findText(text)
        combo.setCurrentIndex(index)
        if combo.isEditable():
            combo.setEditText(text)
        return True
    finally:
        combo.blockSignals(blocked)
