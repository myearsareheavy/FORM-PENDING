"""Mulberry32-style seeded RNG. Same seed always yields the same sequence."""

from __future__ import annotations


def _u32(n: int) -> int:
    return n & 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return _u32(a * b)


def hash_seed(value) -> int:
    text = str(value if value is not None else "")
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = _imul(h, 16777619)
    return _u32(h) or 1


def normalize_seed(value) -> int:
    if value is None or value == "":
        import time
        n = _u32(int(time.time() * 1000) ^ 0xA5A5A5A5)
        return n or 1
    if isinstance(value, bool):
        return 1 if value else 1
    if isinstance(value, int):
        return _u32(value) or 1
    if isinstance(value, float) and value == value:
        return _u32(int(value)) or 1
    return hash_seed(value)


class Rng:
    def __init__(self, seed):
        self.seed = normalize_seed(seed)
        self._a = self.seed

    def next(self) -> float:
        self._a = _u32(self._a + 0x6D2B79F5)
        t = _imul(self._a ^ (self._a >> 15), 1 | self._a)
        t = _u32(t + _imul(t ^ (t >> 7), 61 | t)) ^ t
        return _u32(t ^ (t >> 14)) / 4294967296.0

    def float(self, lo: float = 0.0, hi: float = 1.0) -> float:
        return lo + self.next() * (hi - lo)

    def int(self, lo: int, hi: int) -> int:
        """Inclusive integer in [lo, hi]."""
        if hi < lo:
            lo, hi = hi, lo
        return int(self.float(lo, hi + 1 - 1e-9))

    def bool(self, p: float = 0.5) -> bool:
        return self.next() < p

    def pick(self, seq):
        if not seq:
            raise ValueError("rng.pick on empty sequence")
        return seq[self.int(0, len(seq) - 1)]

    def pick_n(self, seq, n: int):
        copy = list(seq)
        self.shuffle(copy)
        return copy[: min(n, len(copy))]

    def shuffle(self, seq):
        for i in range(len(seq) - 1, 0, -1):
            j = self.int(0, i)
            seq[i], seq[j] = seq[j], seq[i]
        return seq

    def fork(self, label) -> "Rng":
        return Rng(hash_seed(f"{self.seed}:{label}"))
