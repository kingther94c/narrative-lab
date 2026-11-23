"""EXP-0038: what are the earnings 8-K exhibits EXP-0037 could not label? (S2-a census, step 2)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0038 (2026-11-23). For the 500
largest training and development companies, fetches each EX-99 exhibit that EXP-0037 classed as
unlabelled and classes it by its text with the rules below, fixed before the run. Exhibits are
saved on the drive. `check` prints thirty exhibits drawn by seed for a hand check.

    conda run --no-capture-output -n nlab python research/experiments/exp0038_s2a_exhibit_text.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0038_s2a_exhibit_text.py classify
    conda run --no-capture-output -n nlab python research/experiments/exp0038_s2a_exhibit_text.py check
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0003_guidance_pairs as e3  # noqa: E402
import exp0037_s2a_exhibit_census as e37  # noqa: E402

OUT = e37.DRIVE / "s2" / "exp0038"
TEXTS = OUT / "exhibits"
SEED = 20261123

# Rules, tried in this order; fixed before the run. `title` is description + file name, `head` the
# first 4,000 characters of the text, `text` all of it, all lower case.
CLASSES = (
    ("transcript", lambda title, head, text: "transcript" in title or "transcript" in head[:1500]
     or (len(re.findall(r"\boperator\b", text)) >= 2 and re.search(r"question", text) is not None)),
    ("prepared remarks or script", lambda title, head, text: re.search(r"prepared remarks|\bscript\b|remarks", title + " " + head[:1500]) is not None
     or re.search(r"good (morning|afternoon|evening)|thank you for joining|welcome to (our|the)", head[:3000]) is not None),
    ("cfo commentary", lambda title, head, text: re.search(r"commenta", title) is not None
     or re.search(r"cfo commentary|financial commentary|commentary on (the )?(first|second|third|fourth|q[1-4])", head) is not None),
    ("shareholder letter", lambda title, head, text: re.search(r"(stock|share)holde|letter", title) is not None
     or re.search(r"dear (fellow )?(shareholders|stockholders|shareowners|investors)|letter to (our )?(shareholders|stockholders|shareowners)", head) is not None),
    ("presentation", lambda title, head, text: re.search(r"presenta|slide|deck", title) is not None
     or len(re.findall(r"\bpresentation\b", head)) >= 2),
    ("supplemental financial data", lambda title, head, text: re.search(r"supple|statistic|fact ?sheet|data ?book|trend", title) is not None
     or re.search(r"financial supplement|supplemental (financial )?(information|data|schedules)|statistical supplement|financial (and operating )?(data|information) (supplement|package)", head) is not None),
    ("another press release", lambda title, head, text: re.search(r"press release|news release", title) is not None
     or re.search(r"\b(announces|reports|declares|reported)\b", head[:600]) is not None),
)
COMMENTARY = e37.COMMENTARY


def targets() -> list[dict]:
    pages = e37.index_pages()
    out = []
    for line in open(e37.OUT / "filings.jsonl", encoding="utf-8"):
        f = json.loads(line)
        if not f["top"] or not any(x["class"] == "unlabelled" for x in f["exhibits"]):
            continue
        t = e3.IndexTable()
        t.feed(e37.read(pages[(str(int(f["cik"])), f["accession"])]))
        href = {row[2][0]: row[2][1] for row in t.rows if len(row) >= 4 and row[2][0]}
        for x in f["exhibits"]:
            if x["class"] != "unlabelled":
                continue
            h = href.get(x["document"])
            url = "https://www.sec.gov" + h if h and h.startswith("/") else \
                f"https://www.sec.gov/Archives/edgar/data/{int(f['cik'])}/{f['accession'].replace('-', '')}/{x['document']}"
            out.append({"cik": f["cik"], "accession": f["accession"], "filing_date": f["filing_date"], "post_cutoff": f["post_cutoff"],
                        "type": x["type"], "description": x["description"], "document": x["document"], "url": url})
    return out


def path_of(t: dict) -> Path:
    return TEXTS / f"{t['cik']}_{t['accession']}_{re.sub(r'[^A-Za-z0-9._-]', '_', t['document'])}.txt"


def fetch(_: argparse.Namespace) -> None:
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    from edgar.documents import parse_html
    from edgar.httprequests import download_file

    TEXTS.mkdir(parents=True, exist_ok=True)
    ts = targets()
    (OUT / "targets.jsonl").write_text("".join(json.dumps(t) + "\n" for t in ts), encoding="utf-8")
    log = OUT / "fetch_log.jsonl"
    done = set()
    if log.exists():
        done = {r["url"] for r in map(json.loads, log.read_text(encoding="utf-8").splitlines()) if r["status"] in ("ok", "pdf")}
    print(f"[fetch] {len(ts)} exhibits, {len(done)} done before", flush=True)
    with open(log, "a", encoding="utf-8") as fh:
        for n, t in enumerate(ts, 1):
            if t["url"] in done:
                continue
            status = "ok"
            if t["document"].lower().endswith(".pdf"):
                status = "pdf"
            else:
                try:
                    html = download_file(t["url"], as_text=True)
                    path_of(t).write_text(parse_html(html).text() or "", encoding="utf-8")
                except Exception as err:  # noqa: BLE001
                    status = f"error: {type(err).__name__}: {str(err)[:120]}"
            fh.write(json.dumps({"url": t["url"], "status": status}) + "\n")
            fh.flush()
            if n % 50 == 0:
                print(f"[fetch] {n}/{len(ts)}", flush=True)
    print("[fetch] finished", flush=True)


def classify_one(t: dict) -> str:
    if t["document"].lower().endswith(".pdf"):
        return "pdf, not read"
    p = path_of(t)
    if not p.exists():
        return "not fetched"
    text = re.sub(r"\s+", " ", p.read_text(encoding="utf-8")).lower()
    title = f"{t['description']} {re.sub(r'[_.-]', ' ', t['document'].lower())}"
    for name, rule in CLASSES:
        if rule(title, text[:4000], text):
            return name
    return "other"


def classify(_: argparse.Namespace) -> None:
    ts = [json.loads(line) for line in open(OUT / "targets.jsonl", encoding="utf-8")]
    for t in ts:
        t["class"] = classify_one(t)
    (OUT / "classified.jsonl").write_text("".join(json.dumps(t) + "\n" for t in ts), encoding="utf-8")
    # join with EXP-0037's labelled exhibits for the 500 largest companies
    fs = [json.loads(line) for line in open(e37.OUT / "filings.jsonl", encoding="utf-8")]
    fs = [f for f in fs if f["top"]]
    got = {(t["accession"], t["document"]): t["class"] for t in ts}
    rep: dict = {"exhibits_fetched_or_counted": len(ts), "by_class": dict(collections.Counter(t["class"] for t in ts).most_common())}
    comp = collections.defaultdict(collections.Counter)
    for post in (False, True):
        sel = [f for f in fs if f["post_cutoff"] == post]
        com = 0
        for f in sel:
            classes = {got.get((f["accession"], x["document"]), x["class"]) for x in f["exhibits"]}
            if f["release_class"] in COMMENTARY:
                classes.add(f["release_class"])
            if classes & COMMENTARY:
                com += 1
            for c in classes & COMMENTARY:
                comp[f["cik"]][c] += 1
        rep[f"top500 {'post' if post else 'pre'}-cutoff"] = {"filings": len(sel), "any_commentary": com}
    rep["companies_top500"] = len({f["cik"] for f in fs})
    rep["companies_with_commentary"] = len(comp)
    rep["companies_by_kind"] = dict(collections.Counter(k for c in comp.values() for k in c).most_common())
    rep["filings_per_company_with_commentary"] = {
        cik: {"filings": sum(f["cik"] == cik for f in fs), "commentary": dict(c)} for cik, c in sorted(comp.items())}
    (OUT / "census.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items() if k != "filings_per_company_with_commentary"}, indent=2))


def check(_: argparse.Namespace) -> None:
    ts = [json.loads(line) for line in open(OUT / "classified.jsonl", encoding="utf-8")]
    for t in random.Random(SEED).sample([t for t in ts if t["class"] not in ("pdf, not read", "not fetched")], 30):
        p = path_of(t)
        head = re.sub(r"\s+", " ", p.read_text(encoding="utf-8"))[:300] if p.exists() else ""
        print(f"[{t['class']}] {t['document']} | {head}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("fetch", fetch), ("classify", classify), ("check", check)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
