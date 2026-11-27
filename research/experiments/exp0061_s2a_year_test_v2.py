"""EXP-0061: year test v2 for the Alpha Vantage replies (two-digit years), and EXP-0045's call texts on it (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0061 (2026-11-26). Openings such as
"Second Quarter 26" or "Fiscal 26" print a two-digit year; EXP-0042's test then fell back to the
year printed most often (2025 or 2027 from comparisons and outlook). This runs EXP-0060's check
and redoes the year test with two-digit years read after "quarter", "fiscal", "FY" or "Q1".."Q4".

    conda run --no-capture-output -n nlab python research/experiments/exp0061_s2a_year_test_v2.py check
    conda run --no-capture-output -n nlab python research/experiments/exp0061_s2a_year_test_v2.py calls
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0042_s2a_av_transcripts_v3 as e42  # noqa: E402
import exp0043_s2a_av_transcripts_all as e43  # noqa: E402
import exp0045_s2a_call_texts as e45  # noqa: E402
import exp0060_s2a_name_test_v2 as e60  # noqa: E402

OUT = e40.DRIVE / "s2" / "exp0061"
CHECKED = e40.OUT / "checked_v5.jsonl"
TWO_DIGIT = re.compile(r"\b(?:quarter|fiscal(?: year)?|fy|q[1-4])\s*['’]?\s*(\d{2})\b", re.I)


def year_v2(text: str) -> int | None:
    head = text[:600]
    m = re.search(r"\b(20[0-3]\d)\b", head)
    if m:
        return int(m[1])
    m = TWO_DIGIT.search(head)
    if m:
        return 2000 + int(m[1])
    return e42.year_named(text)[1]


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    e60.check(argparse.Namespace())
    ts = {}
    for r in e43.load():
        ts.setdefault((r["cik"], r["av_quarter"]), r)
    rows, changed = [], []
    for line in open(e60.CHECKED, encoding="utf-8"):
        x = json.loads(line)
        r = ts[(x["cik"], x["av_quarter"])]
        d = json.loads(e43.e41.raw_for(x["cik"], x["av_quarter"]).read_text(encoding="utf-8"))
        ok = year_v2(e40.text_of(d)) == int(r["fy"])
        if ok != x["year_ok"]:
            changed.append((x["symbol"], x["av_quarter"], x["year_ok"], ok))
        x["year_ok"] = ok
        x["usable"] = x["full"] and x["name_seen"] and x["quarter_ok"] and ok
        if "same_call" in x:
            x["usable"] = x["usable"] or (x["full"] and x["same_call"])
        rows.append(x)
    CHECKED.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    rep = {"rows": len(rows), "usable": sum(x["usable"] for x in rows), "year_test_changed": changed,
           "full_not_usable": [(x["symbol"], x["av_quarter"], x["name_seen"], x["quarter_ok"], x["year_ok"]) for x in rows if x["full"] and not x["usable"]]}
    (OUT / "check_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def calls(_: argparse.Namespace) -> None:
    e45.CHECKED = CHECKED  # EXP-0045's build, reading this check
    e45.build(argparse.Namespace())
    e45.check(argparse.Namespace())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=check)
    sub.add_parser("calls").set_defaults(fn=calls)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
