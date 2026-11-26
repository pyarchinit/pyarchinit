"""Same number, different type (s3dgraphy#40): told before sending."""
from __future__ import annotations

import sqlite3

from modules.stratigraph.room_checks import ambiguous_numbers


def test_a_number_shared_by_two_types_and_the_rapporti_towards_it(tmp_path):
    db = tmp_path / "s.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE us_table (sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, rapporti TEXT)")
    con.executemany("INSERT INTO us_table VALUES (?, ?, ?, ?, ?)", [
        ("S", "1", "900", "US", "[]"),
        ("S", "1", "900", "Combinar", "[]"),
        ("S", "2", "900", "US", "[]"),                                   # another area: not the same
        ("S", "1", "104", "USVn", "[['>>', '900', '1', 'S']]"),
        ("S", "1", "5", "US", "[['Copre', '900', '', '']]"),              # empty area = its own
        ("S", "1", "6", "US", "[['Copre', '900', '2', 'S']]"),            # area 2: unambiguous
    ])
    con.commit(); con.close()
    assert ambiguous_numbers(f"sqlite:///{db}", "S") == [
        {"area": "1", "us": "900", "types": ["Combinar", "US"], "referenced_by": ["US 5", "USVn 104"]}]


def test_nothing_to_say_on_a_clean_site(tmp_path):
    db = tmp_path / "s.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE us_table (sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, rapporti TEXT)")
    con.execute("INSERT INTO us_table VALUES ('S', '1', '1', 'US', '[]')")
    con.commit(); con.close()
    assert ambiguous_numbers(f"sqlite:///{db}", "S") == []
