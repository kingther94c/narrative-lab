"""Company split v1: the one assignment of companies to test, development and training.

Shared by the main programme (Benchmark v0) and sub-study S1. Fixed on 2026-11-15 by the owner's
decision to split companies by a hash of their CIK. FROZEN: never edit the salt, the cut points or
the hash. A changed split is ``split_v2.py``, and every result says which split it used.

Rule:

- A company is keyed by its SEC CIK, as a 10-digit zero-padded string.
- ``u`` is the first 8 bytes of SHA-256(SALT + ":" + cik10), read big-endian and divided by 2**64,
  so ``u`` is uniform on [0, 1) and does not depend on anything observed about the company.
- ``u < 0.60`` is test, ``0.60 <= u < 0.70`` is development, the rest is training.
- Companies that share a filing (co-registrants: a utility and its holding company, an airline and
  its parent) form one group. The whole group takes the assignment of its smallest CIK, so one
  document never lands on two sides.

Why 60/10/30: the scarce resource is clean test pairs, which exist only after the cutoff, while
training and development can draw on many years of each company's earlier releases. At 60% the
test side keeps about 1,000 to 1,300 of the estimated 1,700 to 2,200 numeric pairs
(``research/design/data_audit.md`` §8). That is above the 785 pairs one comparison needs at 25%
disagreement.

Known limit: a company that changes CIK (a successor after a reorganisation) gets a fresh draw.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

SALT = "narrative-lab company split v1"
TEST_BELOW = 0.60
DEV_BELOW = 0.70


def cik10(cik: str | int) -> str:
    return f"{int(cik):010d}"


def u_value(cik: str | int) -> float:
    digest = hashlib.sha256(f"{SALT}:{cik10(cik)}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def side_of_u(u: float) -> str:
    if u < TEST_BELOW:
        return "test"
    if u < DEV_BELOW:
        return "dev"
    return "train"


def groups(filings: Iterable[tuple[str, str | int]]) -> dict[str, str]:
    """Map each CIK to its group key (the smallest CIK it shares any filing with, transitively).

    ``filings`` yields (accession, cik) pairs, one per company listed on a filing.
    """
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    first: dict[str, str] = {}
    for acc, cik in filings:
        c = cik10(cik)
        find(c)
        if acc in first:
            a, b = find(first[acc]), find(c)
            if a != b:
                parent[max(a, b)] = min(a, b)
        else:
            first[acc] = c
    return {c: find(c) for c in parent}


def assign(cik: str | int, group_of: dict[str, str] | None = None) -> str:
    """Return "test", "dev" or "train" for a company, by its group's key if a map is given."""
    c = cik10(cik)
    key = (group_of or {}).get(c, c)
    return side_of_u(u_value(key))
