import pytest
from modules.s3dgraphy.sync.rapporti import (
    parse_rapporti, continuity_label, CONTINUITY_LABELS,
)

_LANGS = ["it", "en", "de", "es", "fr", "pt", "ca", "ro", "ar", "el"]

def test_continuity_labels_cover_ten_languages():
    assert set(CONTINUITY_LABELS) == set(_LANGS)
    for lang in _LANGS:
        fwd = continuity_label(lang, "forward")
        rev = continuity_label(lang, "reverse")
        assert fwd and rev and fwd != rev

@pytest.mark.parametrize("lang", _LANGS)
def test_forward_label_parses_to_is_after_no_swap(lang):
    fwd = continuity_label(lang, "forward")
    parsed = parse_rapporti([[fwd, "US5", "1", "Sito"]])
    assert parsed == [("is_after", "US5", "1", "Sito", False)]

@pytest.mark.parametrize("lang", _LANGS)
def test_reverse_label_parses_to_is_after_with_swap(lang):
    rev = continuity_label(lang, "reverse")
    parsed = parse_rapporti([[rev, "CON_US5", "1", "Sito"]])
    assert parsed == [("is_after", "CON_US5", "1", "Sito", True)]

def test_reverse_label_unknown_lang_falls_back_to_italian():
    assert continuity_label("zz", "forward") == CONTINUITY_LABELS["it"][0]
