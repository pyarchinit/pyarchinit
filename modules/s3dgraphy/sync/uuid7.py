"""Local UUID v7 generator (RFC 9562 §5.7).

Monotonic per-process. Will be replaced with stdlib ``uuid.uuid7()`` when
the project minimum Python version bumps to 3.14+.

Layout (RFC 9562 §5.7)::

    0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                           unix_ts_ms                          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |          unix_ts_ms           |  ver  |       rand_a          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |var|                        rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                            rand_b                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

- 48-bit Unix-epoch ms timestamp
- 4-bit version=7
- 12-bit rand_a
- 2-bit variant=10
- 62-bit rand_b

When two calls fall within the same millisecond, the second call increments
the random portion (rand_a || rand_b treated as a single 74-bit integer) so
that the sequence remains monotonically ordered. The global ``_lock``,
``_last_ms`` and ``_last_rand`` make this thread-safe within one process.
"""
from __future__ import annotations

import os
import threading
import time
import uuid

_lock = threading.Lock()
_last_ms: int = -1
_last_rand: int = 0

# Mask widths.
_RAND_BITS = 74          # rand_a (12) + rand_b (62)
_RAND_MASK = (1 << _RAND_BITS) - 1
_RAND_A_BITS = 12
_RAND_A_MASK = (1 << _RAND_A_BITS) - 1
_RAND_B_BITS = 62
_RAND_B_MASK = (1 << _RAND_B_BITS) - 1


def uuid7() -> uuid.UUID:
    """Return a fresh UUID v7. Monotonic across calls in the same process."""
    global _last_ms, _last_rand

    with _lock:
        now_ms = int(time.time() * 1000)
        if now_ms <= _last_ms:
            # Same millisecond (or clock went backwards): bump the random
            # portion to preserve monotonic ordering.
            new_rand = (_last_rand + 1) & _RAND_MASK
            if new_rand == 0:
                # Random space wrapped — advance the timestamp by 1 ms and
                # re-roll. This is astronomically unlikely (>2^74 calls in
                # one ms) but keeps ordering well-defined.
                now_ms = _last_ms + 1
                new_rand = int.from_bytes(os.urandom(10), "big") & _RAND_MASK
            ms = max(now_ms, _last_ms)
        else:
            ms = now_ms
            new_rand = int.from_bytes(os.urandom(10), "big") & _RAND_MASK

        _last_ms = ms
        _last_rand = new_rand

        rand_a = (new_rand >> _RAND_B_BITS) & _RAND_A_MASK
        rand_b = new_rand & _RAND_B_MASK

    # Assemble the 128-bit integer:
    #   [unix_ts_ms 48][ver 4][rand_a 12][var 2][rand_b 62]
    val = (ms & 0xFFFFFFFFFFFF) << 80
    val |= (0x7 & 0xF) << 76
    val |= (rand_a & 0xFFF) << 64
    val |= (0b10 & 0x3) << 62
    val |= rand_b & _RAND_B_MASK
    return uuid.UUID(int=val)
