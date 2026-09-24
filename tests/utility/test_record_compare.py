"""Whether the record on the screen still is the record in the database.

Reported on master 4.9.14 (2026-09-24): the US sheet never kept a change
to "Unità tipo" and Save only answered "Non è stata realizzata alcuna
modifica". Every sheet keeps two lists — the values read from the record
and the values shown by the form — and compares them to know whether
there is anything to save; master read the record with
``eval("unicode(...)")``, a Python 2 leftover that raises NameError on
Python 3, and the error was caught and reported as "no changes", so the
UPDATE never ran.

Once the comparison works again a second trap opens: a column nobody
ever filled in is NULL in the database and an empty box in the form, and
compared as 'None' against '' every record of an imported database looks
modified (101 of 101 US of a real database) and asks to be saved at each
change of record. Pure Python, no Qt.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.record_compare import records_equal, same_value  # noqa: E402


def test_nothing_written_is_nothing_written():
    assert same_value(None) == same_value('') == same_value('None') == ''
    assert same_value(5) == '5' and same_value('USM') == 'USM'


def test_a_record_nobody_touched_is_not_reported_as_modified():
    record = ['Ventena', '1', 'US', None, 'None', 5, 0.0]
    form = ['Ventena', '1', 'US', '', '', '5', '0.0']
    assert records_equal(record, form)


def test_a_real_change_is_recognised():
    assert not records_equal(['Ventena', 'US'], ['Ventena', 'USM'])
    assert not records_equal(['Ventena', None], ['Ventena', 'ora scritto'])
    assert not records_equal(['Ventena', 'era scritto'], ['Ventena', ''])


def test_two_lists_of_different_length_are_never_equal():
    assert not records_equal(['a'], ['a', 'b'])


def test_what_is_not_a_list_is_compared_as_it_is():
    # some sheets park a whole record (an ORM object) in the two fields
    record = object()
    assert records_equal(record, record)
    assert not records_equal(record, object())


def test_no_sheet_compares_the_two_lists_by_itself():
    direct = re.compile(r'^[ \t]*if self\.DATA_LIST_REC_CORR == self\.DATA_LIST_REC_TEMP:', re.M)
    offenders = [p.name for p in sorted((_ROOT / 'tabs').glob('*.py'))
                 if direct.search(p.read_text(encoding='utf-8'))]
    assert not offenders, offenders


def test_no_sheet_reads_a_record_with_the_python_2_unicode():
    offenders = [p.name for p in sorted((_ROOT / 'tabs').glob('*.py'))
                 if 'eval("unicode(' in p.read_text(encoding='utf-8')]
    assert not offenders, offenders
