"""EXP-0049: the December company-facts snapshot and EXP-0020's series rebuilt from it (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0049 (2026-11-24; approved by the
owner 2026-11-20). For label coverage of filers whose September quarter came after the November
snapshot (2026-11-14) and for later labels; EXP-0048's build does not need it. No model.

    conda run --no-capture-output -n nlab python research/experiments/exp0049_s2a_december_facts.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0049_s2a_december_facts.py series --zip <path>
    conda run --no-capture-output -n nlab python research/experiments/exp0049_s2a_december_facts.py compare
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0020_s2a_episodes as e20  # noqa: E402

DRIVE = e20.DRIVE
OUT = DRIVE / "s2" / "exp0049"
URL = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"


def fetch(_: argparse.Namespace) -> None:
    ident = os.environ.get("EDGAR_IDENTITY")
    if not ident:
        sys.exit("EDGAR_IDENTITY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    day = dt.date.today().isoformat()
    dest = DRIVE / "edgar" / "xbrl" / f"companyfacts-{day}.zip"
    if dest.exists():
        sys.exit(f"{dest} exists")
    tmp = dest.with_suffix(".part")
    h = hashlib.sha256()
    req = urllib.request.Request(URL, headers={"User-Agent": ident, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fh:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)
            h.update(chunk)
    tmp.rename(dest)
    with zipfile.ZipFile(dest) as zf:
        n = len(zf.namelist())
    rec = {"file": str(dest), "bytes": dest.stat().st_size, "sha256": h.hexdigest(), "members": n,
           "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (OUT / "fetch.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps(rec, indent=2))


def series(a: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    uni = e20.universe()
    zf = zipfile.ZipFile(a.zip)
    names = set(zf.namelist())
    n_co = n_rec = 0
    with open(OUT / "series.jsonl", "w", encoding="utf-8") as f:
        for cik, co in sorted(uni.items()):
            name = f"CIK{cik}.json"
            if name not in names:
                continue
            gaap = json.loads(zf.read(name)).get("facts", {}).get("us-gaap", {})
            recs = e20.company_series(gaap)
            if not recs:
                continue
            n_co += 1
            n_rec += len(recs)
            for rec in recs:
                f.write(json.dumps({"cik": cik, "side": co["side"], "size_band": co["size_band"], **rec}) + "\n")
    rep = {"zip": str(a.zip), "companies_in_universe": len(uni), "companies_with_series": n_co, "quarters": n_rec}
    (OUT / "series_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def compare(_: argparse.Namespace) -> None:
    def load(p):
        by = {}
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            by[(r["cik"], r["end"])] = r
        return by
    old, new = load(e20.OUT / "series.jsonl"), load(OUT / "series.jsonl")
    key = [json.loads(line) for line in open(DRIVE / "s2" / "exp0048" / "key.jsonl", encoding="utf-8")]
    have_old = sum(any(c == k["cik"] and abs(e20.e5.days(e, k["quarter_end"])) <= 5 for c, e in old) for k in key)
    have_new = sum(any(c == k["cik"] and abs(e20.e5.days(e, k["quarter_end"])) <= 5 for c, e in new) for k in key)
    changed = [(k, old[k]["rev"], new[k]["rev"]) for k in old if k in new and old[k]["accn"] == new[k]["accn"] and old[k]["rev"] != new[k]["rev"]]
    rep = {"exp0048_episodes": len(key), "september_quarter_in_november_series": have_old,
           "september_quarter_in_december_series": have_new, "same_filing_different_value": changed[:20], "n_changed": len(changed)}
    (OUT / "compare.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch").set_defaults(fn=fetch)
    s = sub.add_parser("series")
    s.add_argument("--zip", required=True)
    s.set_defaults(fn=series)
    sub.add_parser("compare").set_defaults(fn=compare)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
