"""Regression for LLMProviderManager._annotate_error.

It must not crash on SDK exceptions whose ``__init__`` takes keyword-only
required arguments (the ``anthropic.APIStatusError`` family,
``__init__(self, message, *, response, body)``). The old implementation rebuilt
the exception via ``type(exc)(msg)``, which raised the cryptic
``__init__() missing 2 required keyword-only arguments: 'response' and 'body'``
and *hid* the real cause of a failed AI/RAG query.
"""
from __future__ import annotations

from types import SimpleNamespace

from modules.utility.llm_providers import LLMProviderManager


class _KwOnlyError(Exception):
    """Mimics anthropic.APIStatusError: __init__(self, message, *, response, body)."""

    def __init__(self, message, *, response, body):
        super().__init__(message)


def _cfg():
    return SimpleNamespace(
        provider=SimpleNamespace(value="anthropic"),
        base_url=None,
        model="claude-sonnet-4-6",
    )


def test_annotate_error_survives_keyword_only_exception():
    exc = _KwOnlyError("Error code: 401 - invalid x-api-key", response=object(), body=None)
    out = LLMProviderManager._annotate_error(_cfg(), exc)  # must not raise
    assert isinstance(out, Exception)
    assert "401 - invalid x-api-key" in str(out)   # real cause preserved
    assert "provider=anthropic" in str(out)        # context appended


def test_annotate_error_preserves_plain_exception_type():
    out = LLMProviderManager._annotate_error(_cfg(), ValueError("boom"))
    assert isinstance(out, ValueError)             # type kept when constructible
    assert "boom" in str(out)
