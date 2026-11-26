"""EXP-0054: verified fact sheets of the training companies' releases (S1 re-plan, data factory step 1).

Input: EXP-0052's releases (training companies only, 2019 to the cutoff) and the XBRL company facts
already on the drive. For each release, the two-source rule of EXP-0005 and EXP-0019 is applied to
the eleven line items of section R (revenue, cost of revenue, gross profit, R&D, SG&A, total
operating expenses, total costs and expenses, operating income, income before taxes, net income,
diluted EPS): a figure is kept only if a table row whose label names it shows it, at the table's
scale, equal to the value first filed in XBRL for the period, with the prior-year figure in the same
row equal to XBRL's prior-year value. This is section R v1's builder (EXP-0053) run over the
releases, so the conditions it can verify (margins, growth, cost against sales, biggest mover,
derived periods, lines absent) are the ones section R tests, checked the same way.

Output per release (``s1/exp0054/sheets.jsonl``): the period, the verified figures with their row
and columns, and for each R template the builder could make, its gold, steps and needed rows (no
question text, no excerpt). The factory's later steps build their own questions and excerpts from
these; R's own wording is not reused. An engineering step with no hypothesis and no model. Every
release is a training company's, accepted before the cutoff; no development or test company is read.

    conda run --no-capture-output -n py313 python research/experiments/exp0054_s1f_sheets.py run
    conda run --no-capture-output -n py313 python research/experiments/exp0054_s1f_sheets.py run --resume
    conda run --no-capture-output -n py313 python research/experiments/exp0054_s1f_sheets.py report
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0052_s1f_release_pull as P52  # noqa: E402  (frozen; targets and texts)
import exp0053_s1r_build_v1 as V1  # noqa: E402  (frozen; section R v1's builder)

V0, E = V1.V0, V1.E
OUT = E.DRIVE / "s1" / "exp0054"
SHEETS = OUT / "sheets.jsonl"
SEED = 20261126
FIG_KEYS = ("metric", "label", "line", "shown", "col", "prior_col", "scale", "dec", "prior_dec", "cur", "prior", "vals", "xbrl")
ITEM_KEYS = ("template", "variant", "kind", "gold", "tolerance", "options", "steps", "need_lines", "excerpt_tokens")


def run(a):
    if not E.DRIVE.exists():
        sys.exit("external drive not mounted")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(glob.glob(f"{E.TOKENIZER}/snapshots/*/tokenizer.json")[0])
    count = lambda s: len(tok.encode(s).ids)  # noqa: E731
    OUT.mkdir(parents=True, exist_ok=True)
    targets = json.loads((P52.OUT / "targets.json").read_text(encoding="utf-8"))
    done = set()
    if a.resume and SHEETS.exists():
        done = {json.loads(l)["accession"] for l in open(SHEETS, encoding="utf-8")}
    elif SHEETS.exists():
        sys.exit("sheets.jsonl exists; use --resume")
    fetched = set()  # logged after the text is written, so no file is read while being written
    for l in open(P52.OUT / "fetch_log.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["status"] in ("ok", "reused"):
            fetched.add(r["accession"])
    facts = E.Facts()
    why, n, t0 = collections.Counter(), 0, time.time()
    cache_cik, gaap = None, {}
    with open(SHEETS, "a", encoding="utf-8") as fh:
        for t in sorted(targets, key=lambda t: (t["cik"], t["acceptance"])):
            if t["accession"] in done or t["accession"] not in fetched:
                continue
            path = P52.TEXTS / f"{t['cik']}_{t['accession']}.txt"
            if not path.exists() or path.stat().st_size == 0:
                continue  # not fetched yet, or no press release; a later --resume picks it up
            assert t["acceptance"][:10] <= P52.CUTOFF
            if t["cik"] != cache_cik:
                cache_cik, gaap = t["cik"], facts.load(t["cik"])
            rec = {k: t[k] for k in ("cik", "name", "accession", "filing_date", "acceptance")}
            if not gaap:
                rec["status"] = "no company facts"
            else:
                b = V1.Builder({**t, "post_cutoff": False}, path.read_text(encoding="utf-8"), gaap, count,
                                rng=random.Random(f"{SEED}|{t['accession']}"), side="train", why=why)
                rec["status"] = b.build()
                if hasattr(b, "P"):
                    rec["period"] = {"start": b.start, "end": b.end, "kind": b.kind}
                    rec["figures"] = {m: {k: p.get(k) for k in FIG_KEYS} for m, p in b.P.items()}
                    rec["r_items"] = [{k: it.get(k) for k in ITEM_KEYS} for it in b.items]
            why[f"release: {rec['status']}"] += 1
            fh.write(json.dumps(rec) + "\n")
            n += 1
            if n % 1000 == 0:
                fh.flush()
                print(f"[sheets] {n} releases, {n / (time.time() - t0):.1f}/s", flush=True)
    (OUT / f"why_{time.strftime('%Y%m%dT%H%M%S')}.json").write_text(json.dumps(dict(sorted(why.items())), indent=1), encoding="utf-8")
    print(f"[sheets] {n} releases this run, {time.time() - t0:.0f}s", flush=True)
    report(a)


def report(_):
    recs = [json.loads(l) for l in open(SHEETS, encoding="utf-8")]
    ok = [r for r in recs if r.get("figures")]
    tmpl = collections.Counter(i["template"] for r in ok for i in r["r_items"])
    figs = collections.Counter(m for r in ok for m in r["figures"])
    nfig = collections.Counter(min(len(r["figures"]), 8) for r in ok)
    rep = {"releases": len(recs), "status": dict(collections.Counter(r["status"] for r in recs)),
           "with a verified figure": len(ok), "companies with a verified figure": len({r["cik"] for r in ok}),
           "releases by verified figure count (8 = 8 or more)": dict(sorted(nfig.items())),
           "verified figures by line item": dict(figs.most_common()),
           "R-template items the builder could make": dict(sorted(tmpl.items())),
           "by year (with a verified figure)": dict(sorted(collections.Counter(r["filing_date"][:4] for r in ok).items())),
           "by period kind": dict(collections.Counter(r["period"]["kind"] for r in ok))}
    (OUT / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    r = sub.add_parser("run"); r.add_argument("--resume", action="store_true"); r.set_defaults(fn=run)
    sub.add_parser("report").set_defaults(fn=report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
