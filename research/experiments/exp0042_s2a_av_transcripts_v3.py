"""EXP-0042: Alpha Vantage call transcripts, second fix forward of EXP-0040 (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0042 (2026-11-23). Same targets,
ledger, daily limit and folder as EXP-0040 (`s2/exp0040/`). Changes from EXP-0041: no retry with
another quarter label (EXP-0041's two retries returned the previous fiscal year's call and are
void); a year test joins the quarter test; the name test strips apostrophes.

    conda run --no-capture-output -n nlab python research/experiments/exp0042_s2a_av_transcripts_v3.py fetch --max 25
    conda run --no-capture-output -n nlab python research/experiments/exp0042_s2a_av_transcripts_v3.py check
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0041_s2a_av_transcripts_v2 as e41  # noqa: E402

OUT = e40.OUT
_plan41 = e41.plan


def plan_no_retry(ts: list[dict], log: list[dict]) -> list[tuple[dict, str, bool]]:
    """EXP-0041's plan with every retry removed: each episode is asked only under its fiscal label."""
    return [p for p in _plan41(ts, log) if not p[2]]


def fetch(a: argparse.Namespace) -> None:
    e41.plan = plan_no_retry  # EXP-0041's fetch loop, driven by the no-retry plan
    e41.fetch(a)


def letters(s: str) -> str:
    return re.sub(r"[’'`]", "", s.lower())


def year_named(text: str) -> tuple[int | None, int | None]:
    """(first year in the opening 600 characters, most frequent year in the first 6,000)."""
    m = re.search(r"\b(20[0-3]\d)\b", text[:600])
    c = collections.Counter(int(y) for y in re.findall(r"\b(20[0-3]\d)\b", text[:6000]))
    return (int(m[1]) if m else None), (c.most_common(1)[0][0] if c else None)


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    ts = e41.load_targets()
    by_key: dict = {}
    for r in ts:
        by_key.setdefault((r["cik"], r["av_quarter"]), r)
    rows, seen = [], set()
    for x in e40.ledger():
        quarter = x.get("quarter", x["av_quarter"])
        k = (x["cik"], quarter)
        if x["status"] not in ("ok", "empty") or k in seen or x.get("retry"):  # retries are void
            continue
        seen.add(k)
        r = by_key[(x["cik"], x["av_quarter"])]
        d = json.loads(e41.raw_for(x["cik"], quarter).read_text(encoding="utf-8"))
        text = e40.text_of(d)
        low = letters(text)
        turns = d.get("transcript", [])
        word = next((w for w in re.findall(r"[a-z]+", letters(r["name"] or ""))
                     if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
        q_open, q_freq = e41.opening_quarter(text), e40.quarter_named(text)
        q = q_open if q_open is not None else q_freq
        y_open, y_freq = year_named(text)
        y = y_open if y_open is not None else y_freq
        d_text = e40.e39.first_date(text)
        delta = (d_text - dt.date.fromisoformat(r["release_date"])).days if d_text else None
        row = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], "symbol": r["symbol"],
               "av_quarter": r["av_quarter"], "rank": r["rank"], "turns": len(turns), "chars": len(text),
               "full": len(turns) >= 10 and len(text) >= 5000,
               "name_seen": bool(word and word in low[:5000]) or any(re.search(rf"\b{re.escape(t.lower())}\b", low[:5000]) for t in r["tickers"]),
               "quarter_open": q_open, "quarter_freq": q_freq, "quarter_ok": q == int(r["av_quarter"][-1]),
               "year_open": y_open, "year_freq": y_freq, "year_ok": y == int(r["fy"]),
               "qa_markers": len(re.findall(r"question-and-answer|questions? and answers?|\boperator\b", low)),
               "date_in_text": d_text.isoformat() if d_text else None, "days_after_release": delta,
               "date_flag": delta is not None and not (-1 <= delta <= 3)}
        row["usable"] = row["full"] and row["name_seen"] and row["quarter_ok"] and row["year_ok"]
        if r["ir_file"]:
            ir_text = (e40.e39.TEXTS / (Path(r["ir_file"]).stem + ".txt")).read_text(encoding="utf-8")
            a, b = e40.grams(text), e40.grams(ir_text)
            row["ir_overlap"] = round(len(a & b) / len(a), 3) if a else None
            row["same_call"] = row["ir_overlap"] is not None and row["ir_overlap"] >= e40.SAME_CALL
        rows.append(row)
    (OUT / "checked_v3.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    ok_keys = {(x["cik"], x["av_quarter"]) for x in rows if x["usable"]}
    eps = [r for r in ts if (r["cik"], r["av_quarter"]) in ok_keys]
    ir_eps = [r for r in ts if r["ir_file"]]
    both = {r["episode"] for r in eps} | {r["episode"] for r in ir_eps}
    lg = e40.ledger()
    distinct = {(r["cik"], r["av_quarter"]) for r in ts if r["av_quarter"] and r["symbol"]}
    asked = {(x["cik"], x["av_quarter"]) for x in lg if x["status"] in ("ok", "empty") and not x.get("retry")}
    rep = {"requests": len(lg), "by_status": dict(collections.Counter(x["status"] for x in lg)),
           "by_day": dict(collections.Counter(x["eastern_date"] for x in lg)),
           "distinct_asked": len(asked & distinct), "distinct_total": len(distinct),
           "full": sum(x["full"] for x in rows), "usable": len(ok_keys),
           "episodes_usable": len(eps), "episodes_usable_top250": sum(r["rank"] <= 250 for r in eps),
           "episodes_with_av_or_ir": len(both),
           "episodes_with_av_or_ir_top250": sum(1 for r in ts if r["episode"] in both and r["rank"] <= 250),
           "empty": [x["symbol"] for x in rows if not x["turns"]],
           "full_not_usable": [(x["symbol"], x["av_quarter"], x["name_seen"], x["quarter_open"], x["quarter_freq"], x["year_open"], x["year_freq"])
                               for x in rows if x["full"] and not x["usable"]],
           "date_flags": [(x["symbol"], x["date_in_text"]) for x in rows if x["date_flag"]],
           "ir_overlap": [(x["symbol"], x["ir_overlap"]) for x in rows if "ir_overlap" in x]}
    (OUT / "summary_v3.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--max", type=int, default=e40.DAILY)
    f.set_defaults(fn=fetch)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
