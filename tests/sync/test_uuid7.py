"""Tests for the local UUID v7 generator (RFC 9562 §5.7).

Will be removed when the project minimum bumps to Python 3.14+ and we can
switch to stdlib uuid.uuid7().
"""
from __future__ import annotations

import time
import uuid

from s3dgraphy.sync.uuid7 import uuid7


def test_returns_uuid_object():
    assert isinstance(uuid7(), uuid.UUID)


def test_version_field_is_7():
    u = uuid7()
    assert u.version == 7


def test_variant_is_rfc4122():
    u = uuid7()
    # Top two bits of byte 8 must be '10' (RFC 4122 variant).
    assert (u.bytes[8] & 0xC0) == 0x80


def test_monotonically_ordered_per_call_burst():
    ids = [uuid7() for _ in range(1024)]
    assert ids == sorted(ids)


def test_timestamp_within_recent_window():
    before_ms = int(time.time() * 1000)
    u = uuid7()
    after_ms = int(time.time() * 1000)
    # First 48 bits = Unix-epoch ms timestamp (RFC 9562 §5.7).
    ts_ms = int.from_bytes(u.bytes[:6], "big")
    assert before_ms - 1 <= ts_ms <= after_ms + 1
