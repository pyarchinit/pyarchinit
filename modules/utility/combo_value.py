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


def add_items_keeping_text(combo, items):
    """Add to ``combo`` the ``items`` — texts, or ``(text, data)`` pairs —
    its list does not have yet, without changing what the box shows and
    without waking its handlers.

    Adding the first item to an empty box makes it show that item: the
    Periodizzazione sheet filled its list of epochs after showing the first
    record, so the record of «II A.D.» opened with «Età Contemporanea - XXI
    secolo (2001-2023)», the first epoch of the CSV, and saving it wrote
    that (17 October 2026).
    """
    text = combo.currentText()
    blocked = combo.blockSignals(True)
    try:
        for item in items:
            if isinstance(item, (tuple, list)):
                label, data = str(item[0]), item[1]
            else:
                label, data = str(item), None
            if combo.findText(label) != -1:
                continue
            if data is None:
                combo.addItem(label)
            else:
                combo.addItem(label, data)
        if combo.isEditable():
            combo.setEditText(text)
        else:
            combo.setCurrentIndex(combo.findText(text))
    finally:
        combo.blockSignals(blocked)
