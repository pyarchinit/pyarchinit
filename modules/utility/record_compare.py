"""Whether the record on the screen still is the record in the database.

Every sheet keeps two lists — the values read from the record
(``DATA_LIST_REC_CORR``) and the values shown by the form
(``DATA_LIST_REC_TEMP``) — and compares them to know whether there is
anything to save. A column nobody ever filled in is NULL in the database
and an empty box in the form: compared as 'None' against '', every
record of an imported database looked modified and the sheet asked to
save a record nobody had touched (2026-09-24).

Pure Python, no Qt and no database.
"""


def same_value(v):
    """The value as the comparison sees it: nothing written is nothing
    written, whether the database says NULL or the form says ''."""
    return '' if v is None or v == 'None' else str(v)


def records_equal(corr, temp):
    """True when the record on the screen holds nothing new."""
    if isinstance(corr, (list, tuple)) and isinstance(temp, (list, tuple)):
        return len(corr) == len(temp) and all(
            same_value(a) == same_value(b) for a, b in zip(corr, temp))
    return corr == temp
