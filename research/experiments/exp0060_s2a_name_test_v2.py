"""EXP-0060: name test v2 for the Alpha Vantage replies, and EXP-0045's call texts rebuilt on it (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0060 (2026-11-24). EXP-0042's
name test strips apostrophes ("FNF's" -> "fnfs") and knows no brand names ("Wabtec"). This check
is EXP-0043's with the name test passing on the apostrophe-stripped text, the text without
possessive 's, or a hand-checked alias in s2/exp0060/aliases.json. The daily fetch is unchanged.

    conda run --no-capture-output -n nlab python research/experiments/exp0060_s2a_name_test_v2.py check
    conda run --no-capture-output -n nlab python research/experiments/exp0060_s2a_name_test_v2.py calls
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

OUT = e40.DRIVE / "s2" / "exp0060"
CHECKED = e40.OUT / "checked_v4.jsonl"


def name_seen(text: str, name: str | None, tickers: list[str], symbol: str | None, aliases: dict) -> bool:
    head = text[:5000]
    variants = (e42.letters(head), re.sub(r"['’]s\b", "", head).lower())
    word = next((w for w in re.findall(r"[a-z]+", e42.letters(name or ""))
                 if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
    alias = (aliases.get(symbol or "") or {}).get("alias")
    for v in variants:
        if word and word in v:
            return True
        if any(re.search(rf"\b{re.escape(t.lower())}\b", v) for t in tickers):
            return True
        if alias and alias in v:
            return True
    return False


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    aliases = json.loads((OUT / "aliases.json").read_text(encoding="utf-8"))
    e43.check(argparse.Namespace())  # EXP-0043's tests and summary, then the name test redone
    ts = {}
    for r in e43.load():
        ts.setdefault((r["cik"], r["av_quarter"]), r)
    rows, changed = [], []
    for line in open(e40.OUT / "checked_all.jsonl", encoding="utf-8"):
        x = json.loads(line)
        r = ts[(x["cik"], x["av_quarter"])]
        d = json.loads(e43.e41.raw_for(x["cik"], x["av_quarter"]).read_text(encoding="utf-8"))
        seen = name_seen(e40.text_of(d), r["name"], r["tickers"], r["symbol"], aliases)
        if seen != x["name_seen"]:
            changed.append((x["symbol"], x["av_quarter"], x["name_seen"], seen))
        x["name_seen"] = seen
        x["usable"] = x["full"] and seen and x["quarter_ok"] and x["year_ok"]
        if "same_call" in x:
            x["usable"] = x["usable"] or (x["full"] and x["same_call"])
        rows.append(x)
    CHECKED.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    rep = {"rows": len(rows), "usable": sum(x["usable"] for x in rows), "name_test_changed": changed,
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
