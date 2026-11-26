"""EXP-0052: pull the training companies' earnings releases, 2019 to the cutoff (S1 re-plan, data factory).

Approved by the owner on 2026-11-26 (decision 2 of ``research/design/s1_finance_distillation_replan.md``
§5, "全案推荐来"). The factory generates training data from these releases only. An engineering step:
it reports counts, with no hypothesis and no model.

Scope, fixed here:

* **Companies:** split v1 "train" side only. A company must be "train" both under EXP-0005's group map
  (the one EarningsExam and section R were built with) and under a group map rebuilt here from every
  earnings 8-K in the bulk archive, so no co-registrant link can move a test or development company
  into the pull.
* **Filings:** 8-K with Item 2.02, filing date on or after 2019-01-01, accepted on or before 2026-06-30
  (the roster's latest knowledge cutoff). Recent and overflow files of the bulk submissions archive
  (2026-11-12) are both read. One copy per accession (co-registrants share one).
* **Text:** the press release exhibit, chosen as EXP-0003 chose it (``press_release_url``: an .htm whose
  description matches RELEASE or whose type is EX-99.1, EX-99 or EX-99.01), parsed to text with
  edgartools. A release already on the drive from EXP-0003 is copied, not fetched.
* **Requests:** identity from ``EDGAR_IDENTITY`` (never written here), at most 4 requests a second,
  errors retried on the next run. XBRL company facts are already on the drive
  (``edgar/xbrl/companyfacts-2026-11-14.zip``) and are not pulled.

    conda run --no-capture-output -n nlab python research/experiments/exp0052_s1f_release_pull.py targets
    conda run --no-capture-output -n nlab python research/experiments/exp0052_s1f_release_pull.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0052_s1f_release_pull.py count
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0002_edgar_census as e2  # noqa: E402  (frozen; archive paths and the earnings item)
import exp0003_guidance_pairs as e3  # noqa: E402  (frozen; press_release_url)
import split_v1  # noqa: E402

ROOT = e2.ROOT  # .../narrative_lab/edgar
OUT = ROOT.parent / "s1" / "exp0052"
TEXTS = ROOT / "releases_train"
OLD_TEXTS = ROOT / "releases"  # EXP-0003's texts, read only
OLD_TARGETS = ROOT / "pairs" / "targets.json"  # EXP-0005's group map is built from these
FROM, CUTOFF = "2019-01-01", "2026-06-30"
MAX_RPS = 4.0


def filings(d: dict):
    keys = ("form", "filingDate", "acceptanceDateTime", "items", "accessionNumber")
    for vals in zip(*(d.get(k, []) for k in keys)):
        yield dict(zip(keys, vals))


def earnings(d: dict) -> list[dict]:
    return [r for r in filings(d) if r["form"] == "8-K" and e2.EARNINGS_ITEM in (r["items"] or "")]


def targets(_: argparse.Namespace) -> None:
    e2.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    names, pairs, rows = {}, [], []
    with zipfile.ZipFile(e2.BULK) as zf:
        members = set(zf.namelist())
        for k, name in enumerate(sorted(members)):
            if not name.endswith(".json") or "-submissions-" in name:
                continue
            try:
                d = json.loads(zf.read(name))
            except Exception:
                continue
            f = d.get("filings") or {}
            got = earnings(f.get("recent") or {})
            for extra in f.get("files") or []:
                if extra.get("name") in members:
                    got += earnings(json.loads(zf.read(extra["name"])))
            if not got:
                continue
            cik = split_v1.cik10(d.get("cik"))
            names[cik] = d.get("name")
            for r in got:
                pairs.append((r["accessionNumber"], cik))
                rows.append({"cik": cik, **r})
            if k % 100_000 == 0:
                print(f"[targets] {k} archive files, {len(rows)} earnings 8-Ks, {time.time() - t0:.0f}s", flush=True)
    new_map = split_v1.groups(pairs)
    old = json.loads(OLD_TARGETS.read_text(encoding="utf-8"))
    old_map = split_v1.groups((t["accession"], t["cik"]) for t in old)
    why = collections.Counter()
    out, seen = [], set()
    for r in sorted(rows, key=lambda r: (r["cik"], r["acceptanceDateTime"])):
        if split_v1.assign(r["cik"], new_map) != "train" or split_v1.assign(r["cik"], old_map) != "train":
            why["not train"] += 1
            continue
        if not (FROM <= r["filingDate"] and r["acceptanceDateTime"][:10] <= CUTOFF):
            why["outside dates"] += 1
            continue
        if r["accessionNumber"] in seen:
            why["co-registrant copy"] += 1
            continue
        seen.add(r["accessionNumber"])
        out.append({"cik": r["cik"], "name": names[r["cik"]], "accession": r["accessionNumber"],
                    "filing_date": r["filingDate"], "acceptance": r["acceptanceDateTime"]})
    (OUT / "targets.json").write_text(json.dumps(out), encoding="utf-8")
    rep = {"earnings_8k_in_archive": len(rows), "kept": len(out), "companies": len({t["cik"] for t in out}),
           "dropped": dict(why), "by_year": dict(sorted(collections.Counter(t["filing_date"][:4] for t in out).items())),
           "seconds": round(time.time() - t0)}
    (OUT / "targets_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


class Throttle:
    def __init__(self, rps: float):
        self.gap, self.last = 1.0 / rps, 0.0

    def wrap(self, fn):
        def get(*a, **k):
            wait = self.last + self.gap - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            return fn(*a, **k)
        return get


def fetch(_: argparse.Namespace) -> None:
    e2.need_drive()
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    from edgar.documents import parse_html
    from edgar.httprequests import download_file

    get = Throttle(MAX_RPS).wrap(download_file)
    TEXTS.mkdir(parents=True, exist_ok=True)
    tg = json.loads((OUT / "targets.json").read_text(encoding="utf-8"))
    log = OUT / "fetch_log.jsonl"
    done = set()
    if log.exists():
        done = {r["accession"] for r in map(json.loads, log.read_text(encoding="utf-8").splitlines())
                if not r["status"].startswith("error")}
    todo = [t for t in tg if t["accession"] not in done]
    print(f"[fetch] {len(tg)} targets, {len(todo)} to do", flush=True)
    t0, n = time.time(), 0
    with open(log, "a", encoding="utf-8") as fh:
        for t in todo:
            acc, cik = t["accession"], int(t["cik"])
            path = TEXTS / f"{t['cik']}_{acc}.txt"
            old = OLD_TEXTS / f"{t['cik']}_{acc}.txt"
            status = "ok"
            try:
                if old.exists() and old.stat().st_size > 0:
                    path.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
                    status = "reused"
                else:
                    url = e3.press_release_url(cik, acc, get)
                    if url is None:
                        status = "no_press_release"
                        path.write_text("", encoding="utf-8")
                    else:
                        path.write_text(parse_html(get(url, as_text=True)).text() or "", encoding="utf-8")
            except Exception as err:  # mostly SEC 503s; retried next run
                status = f"error: {type(err).__name__}: {str(err)[:120]}"
            fh.write(json.dumps({"accession": acc, "status": status, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
            fh.flush()
            n += 1
            if n % 250 == 0:
                print(f"[fetch] {n} of {len(todo)}, {n / (time.time() - t0):.2f} releases/s", flush=True)
    print(f"[fetch] finished: {n} this run, {time.time() - t0:.0f}s", flush=True)


def count(_: argparse.Namespace) -> None:
    tg = json.loads((OUT / "targets.json").read_text(encoding="utf-8"))
    last = {}
    log = OUT / "fetch_log.jsonl"
    if log.exists():
        for r in map(json.loads, log.read_text(encoding="utf-8").splitlines()):
            last[r["accession"]] = r["status"].split(":")[0]
    st = collections.Counter(last.get(t["accession"], "not tried") for t in tg)
    nonempty = sum(1 for t in tg if (TEXTS / f"{t['cik']}_{t['accession']}.txt").exists()
                   and (TEXTS / f"{t['cik']}_{t['accession']}.txt").stat().st_size > 0)
    rep = {"targets": len(tg), "status": dict(st), "texts_nonempty": nonempty}
    (OUT / "fetch_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("targets", targets), ("fetch", fetch), ("count", count)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
