"""EXP-0046: fix forward of EXP-0043's next-quarter targets (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0046 (2026-11-23). EXP-0043 took
the release of the quarter *before* each clean quarter (exp0005.days arguments reversed). This
rewrites the "next" rows of `s2/exp0040/targets_all.jsonl` with the following quarter's release,
keeps the clean and old rows unchanged and in order, and saves the old file alongside.

    conda run --no-capture-output -n nlab python research/experiments/exp0046_s2a_next_targets.py targets
"""

from __future__ import annotations

import argparse
import collections
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as e5  # noqa: E402
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0043_s2a_av_transcripts_all as e43  # noqa: E402

BACKUP = e40.OUT / "targets_all_exp0043.jsonl"


def targets(_: argparse.Namespace) -> None:
    e40.need_drive()
    if not BACKUP.exists():
        shutil.copyfile(e43.TARGETS, BACKUP)
    old_all = [json.loads(line) for line in open(BACKUP, encoding="utf-8")]
    clean = [r for r in old_all if r["stage"] in ("validation", "no_ir", "ir")]
    old = [r for r in old_all if r["stage"] == "old"]
    rel: dict[str, list[dict]] = collections.defaultdict(list)
    for line in open(e43.RELEASES, encoding="utf-8"):
        r = json.loads(line)
        rel[r["cik"]].append(r)
    nxt, seen, missing = [], set(), []
    for r in clean:
        if not r["symbol"] or not r["av_quarter"] or (r["cik"], r["av_quarter"]) in seen:
            continue
        seen.add((r["cik"], r["av_quarter"]))
        fy, q = int(r["fy"]), int(r["av_quarter"][-1])
        fy2, q2 = (fy + 1, 1) if q == 4 else (fy, q + 1)
        cands = sorted((x for x in rel[r["cik"]] if x.get("quarter_end")
                        and 60 <= e5.days(r["quarter_end"], x["quarter_end"]) <= 120), key=lambda x: x["filing_date"])
        if not cands:
            missing.append(r["symbol"])
            continue
        x = cands[0]
        nxt.append({**{k: r[k] for k in ("cik", "name", "tickers", "symbol", "rank")},
                    "episode": f"next_{r['episode']}", "clean_episode": r["episode"], "release_date": x["filing_date"],
                    "release_accession": x["accession"], "release_on_drive": bool(x.get("on_drive")),
                    "quarter_end": x["quarter_end"], "fy": fy2, "fp": f"Q{q2}", "fiscal_accn": None,
                    "av_quarter": f"{fy2}Q{q2}", "calendar_fiscal": None, "ir_file": None, "stage": "next"})
    nxt.sort(key=lambda r: (r["rank"], r["cik"]))
    rows = clean + nxt + old
    for n, r in enumerate(rows):
        r["order"] = n
    e43.TARGETS.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"clean": len(clean), "next": len(nxt), "old": len(old), "next_missing": missing,
                      "next_release_months": dict(collections.Counter(r["release_date"][:7] for r in nxt)),
                      "next_release_on_drive": sum(r["release_on_drive"] for r in nxt),
                      "distinct_requests": len({(r["cik"], r["av_quarter"]) for r in rows if r["symbol"] and r["av_quarter"]})}, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("targets").set_defaults(fn=targets)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
