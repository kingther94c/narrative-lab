"""EXP-0008: EarningsExam v0.1, the EXP-0005 generator with column headings kept.

EXP-0005 (frozen) could elide the line naming each column's period: when an excerpt was over its
token budget it kept the first 8 raw lines of the table header, blank lines included, and dropped
the rest. A smoke test for EXP-0007 found an item whose gold sat in the second of two unlabelled
columns (changelog 2026-11-17). A rough count put about 19% of development items without a
period label above their data.

This script imports EXP-0005 unchanged and replaces only ``excerpt``:

* it finds the table's column-heading line: the nearest line above the first needed row carrying
  a period label (a year, a quarter such as 1Q26 or Q1 2026, or FY26) for each of the row's first
  two columns, and no other figure of three or more digits;
* it keeps that line and up to two heading lines just above it (multi-line headings such as
  "Three Months Ended" / "April 30," / "2026 2025") whatever else is elided;
* if no such line is found within 60 lines, the item is dropped and counted.

Everything else (gold, tolerance, splits, templates, held-out templates, the 400-token budget,
item ids) is EXP-0005's. Outputs go to ``s1/exam_v0_1`` beside v0, which is kept.

    conda run --no-capture-output -n py313 python research/experiments/exp0008_earnings_exam_v0_1.py build --sides train,dev
    conda run --no-capture-output -n py313 python research/experiments/exp0008_earnings_exam_v0_1.py build --sides test
    conda run --no-capture-output -n py313 python research/experiments/exp0008_earnings_exam_v0_1.py show --side dev --n 12
    conda run --no-capture-output -n py313 python research/experiments/exp0008_earnings_exam_v0_1.py audit --side dev

``audit`` prints counts only and refuses nothing, since it shows no item text.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as E  # noqa: E402

E.OUT = E.DRIVE / "s1" / "exam_v0_1"
HEADING_WINDOW = 60
PTOK = re.compile(
    r"\b(?:19|20)\d{2}\b|\b[1-4]Q\s?'?\d{2}\b|\bQ[1-4](?:\s?'?\d{2,4})?\b|\bFY\s?'?\d{2,4}\b", re.I
)
DROPPED: collections.Counter = collections.Counter()


def is_heading(line: str, need_cols: int) -> bool:
    if len(PTOK.findall(line)) < need_cols:
        return False
    rest = PTOK.sub(" ", line)
    return not re.search(r"\d[\d,]{2,}", rest)  # no other figure of three or more digits


def heading_block(lines: list[str], lo: int) -> list[int] | None:
    """Line indices of the column heading above row ``lo``: the heading line and up to two
    non-blank, non-numeric lines just above it."""
    row = next((r for r in E.table_rows(lines) if r[0] == lo), None)
    need_cols = min(2, len(row[2])) if row else 1
    for h in range(lo - 1, max(-1, lo - HEADING_WINDOW), -1):
        if lines[h].strip() and is_heading(lines[h], need_cols):
            block = [h]
            j = h - 1
            while j >= 0 and len(block) < 3 and h - j <= 4:
                s = lines[j].strip()
                if s and not re.search(r"\d[\d,]{2,}", PTOK.sub(" ", s)) and not E.TITLE.search(s):
                    block.insert(0, j)
                elif s:
                    break
                j -= 1
            return block
    return None


def excerpt(lines: list[str], need: list[int], count) -> tuple[str, int] | None:
    lines = [l if E.keep(l) else "" for l in lines]
    lo, hi = min(need), max(need)
    heading = heading_block(lines, lo)
    if heading is None:
        DROPPED["no column heading"] += 1
        return None
    _, sline = E.scale_for(lines, lo)
    start = max(0, (sline if sline is not None else lo) - 4)
    for j in range(start, max(-1, start - 6), -1):
        if lines[j].strip() == "":
            start = j + 1
            break
    start = min(start, heading[0])
    end = hi + 1
    text = "\n".join(l.rstrip() for l in lines[start:end] if l.strip())
    n = count(text)
    if n > E.MAX_TOKENS:
        # keep the first 8 non-blank header lines, the column heading and the needed rows
        head = [i for i in range(start, lo) if lines[i].strip()][:8]
        keep_idx = sorted(set(head) | set(heading) | set(range(lo, end)))
        parts, prev = [], None
        for i in keep_idx:
            if not lines[i].strip():
                continue
            if prev is not None and i > prev + 1 and any(lines[k].strip() for k in range(prev + 1, i)):
                parts.append("[...]")
            parts.append(lines[i].rstrip())
            prev = i
        text = "\n".join(parts)
        n = count(text)
        if n > E.MAX_TOKENS:
            DROPPED["over budget"] += 1
            return None
    k = end
    while k < len(lines) and k < end + 12:
        if not lines[k].strip():
            if k + 1 < len(lines) and not lines[k + 1].strip():
                break
            k += 1
            continue
        if not E.NUM.search(lines[k]) and (E.TITLE.search(lines[k]) or lines[k].strip().isupper()):
            break
        cand = text + "\n" + lines[k].rstrip()
        m = count(cand)
        if m > E.MAX_TOKENS:
            break
        text, n, k = cand, m, k + 1
    return text, n


E.excerpt = excerpt
_build = E.build


def build(a) -> None:
    _build(a)
    path = E.OUT / f"dropped_{'_'.join(sorted(a.sides.split(',')))}.json"
    path.write_text(json.dumps(dict(DROPPED), indent=1))
    print("items dropped by excerpt:", dict(DROPPED))


def audit(a) -> None:
    """Counts only: items whose excerpt has a heading line above the first data row."""
    items = [json.loads(l) for l in open(E.OUT / f"items_{a.side}.jsonl", encoding="utf-8")]
    c: collections.Counter = collections.Counter()
    for it in items:
        lines = it["excerpt"].split("\n")
        ok = any(is_heading(l, 1) for l in lines)
        c[(it["section"], ok)] += 1
    print(json.dumps({f"{k[0]} heading={k[1]}": v for k, v in sorted(c.items())}, indent=1))


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build")
    b.add_argument("--sides", default="train,dev")
    b.set_defaults(fn=build)
    s = sub.add_parser("show")
    s.add_argument("--side", default="dev")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=E.show)
    u = sub.add_parser("audit")
    u.add_argument("--side", default="dev")
    u.set_defaults(fn=audit)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
