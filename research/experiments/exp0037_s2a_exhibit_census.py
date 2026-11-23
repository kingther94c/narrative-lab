"""EXP-0037: census of company-written text furnished with earnings 8-Ks (S2-a, no network)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0037 (2026-11-23). Reads the
filing index pages already cached on the drive for the training and development companies'
earnings 8-Ks (EXP-0020's release list) and classes every exhibit other than the press release,
XBRL files and graphics by its description and file name. No network, no model.

    conda run --no-capture-output -n nlab python research/experiments/exp0037_s2a_exhibit_census.py run
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0003_guidance_pairs as e3  # noqa: E402
import exp0020_s2a_episodes as e20  # noqa: E402

DRIVE = e20.DRIVE
CACHE = DRIVE / "edgar" / "_tcache" / "www.sec.gov"
LIST = DRIVE / "s2" / "exp0020" / "releases.jsonl"
OUT = DRIVE / "s2" / "exp0037"
TOP = 500

NAME = re.compile(r"^Archives-edgar-data-(\d+)-(\d+)-(\d{10}-\d{2}-\d{6})-index\.html-[0-9a-f]+$")
COMPANY = re.compile(r'<span class="companyName">\s*([^<(]+)')

# Classes, tried in this order on description + file name; fixed before the run.
CLASSES = (
    ("transcript", re.compile(r"transcript", re.I)),
    ("prepared remarks or script", re.compile(r"prepared|remarks|script", re.I)),
    ("cfo commentary", re.compile(r"commentary", re.I)),
    ("shareholder letter", re.compile(r"letter", re.I)),
    ("presentation", re.compile(r"presentation|slides?\b|deck", re.I)),
    ("supplemental financial data", re.compile(
        r"supplement|financial data|financial information|statistic|fact ?sheet|data ?book|tables|reconciliation|trend", re.I)),
)
COMMENTARY = {"transcript", "prepared remarks or script", "cfo commentary", "shareholder letter"}
BARE = re.compile(r"^(ex|exhibit)?[-_ ]?99[._-]?\d*$", re.I)


def classify(desc: str, doc: str) -> str:
    stem = re.sub(r"\.[a-z]+$", "", doc.lower())
    text = f"{desc} {re.sub(r'[_.-]', ' ', stem)}"
    for name, rx in CLASSES:
        if rx.search(text):
            return name
    if not desc.strip() or BARE.match(desc.replace(" ", "")) or desc.upper().startswith("EX-99"):
        return "unlabelled"
    return "other"


def index_pages() -> dict[tuple[str, str], Path]:
    out = {}
    for p in CACHE.iterdir():
        m = NAME.match(p.name)
        if m:
            out[(m.group(1), m.group(3))] = p
    return out


def read(p: Path) -> str:
    b = p.read_bytes()
    try:
        return gzip.decompress(b).decode("utf-8", "ignore")
    except OSError:
        return b.decode("utf-8", "ignore")


def exhibits(page: str) -> tuple[list[dict], dict | None]:
    """Exhibit rows other than the press release, and the press release row (EXP-0003's rule)."""
    t = e3.IndexTable()
    t.feed(page)
    rows, release = [], None
    for row in t.rows:
        if len(row) < 4:
            continue
        desc, (doc, _), typ = row[1][0], row[2], row[3][0]
        if not doc:
            continue
        r = {"type": typ, "description": desc, "document": doc}
        if release is None and doc.lower().endswith(".htm") and (re.match(".*RELEASE", desc) or typ in ("EX-99.1", "EX-99", "EX-99.01")):
            release = r
            continue
        if typ.upper().startswith("EX-99"):
            rows.append(r)
    return rows, release


def run(_: argparse.Namespace) -> None:
    if not CACHE.exists():
        sys.exit("drive not mounted")
    OUT.mkdir(parents=True, exist_ok=True)
    by = e20.load_series()
    ranked = sorted(by, key=lambda c: -max(r["rev"] for r in by[c][-4:]))
    rank = {c: i for i, c in enumerate(ranked)}
    pages = index_pages()
    rel = [json.loads(line) for line in open(LIST, encoding="utf-8")]
    filings, names = [], {}
    for r in rel:
        p = pages.get((str(int(r["cik"])), r["accession"]))
        if p is None:
            continue
        page = read(p)
        m = COMPANY.search(page)
        if m:
            names[r["cik"]] = m.group(1).strip()
        xs, release = exhibits(page)
        for x in xs:
            x["class"] = classify(x["description"], x["document"])
        filings.append({"cik": r["cik"], "accession": r["accession"], "filing_date": r["filing_date"],
                        "post_cutoff": r["post_cutoff"], "top": rank.get(r["cik"], 10**6) < TOP,
                        "release": release, "release_class": classify(release["description"], release["document"]) if release else None,
                        "exhibits": xs})
    with open(OUT / "filings.jsonl", "w", encoding="utf-8") as fh:
        for f in filings:
            fh.write(json.dumps(f) + "\n")

    rep: dict = {"releases_listed": len(rel), "index_pages_found": len(filings)}
    for top in (True, False):
        for post in (False, True):
            fs = [f for f in filings if f["top"] == top and f["post_cutoff"] == post]
            cls = collections.Counter(c for f in fs for c in {x["class"] for x in f["exhibits"]})
            rep[f"{'top500' if top else 'rest'} {'post' if post else 'pre'}-cutoff"] = {
                "filings": len(fs),
                "any_extra_exhibit": sum(bool(f["exhibits"]) for f in fs),
                "any_commentary": sum(any(x["class"] in COMMENTARY for x in f["exhibits"]) for f in fs),
                "release_document_is_commentary": sum(f["release_class"] in COMMENTARY for f in fs),
                "filings_by_class": dict(cls.most_common()),
            }
    comp = collections.defaultdict(lambda: {"filings": 0, "commentary": collections.Counter(), "top": False})
    for f in filings:
        c = comp[f["cik"]]
        c["filings"] += 1
        c["top"] = f["top"]
        for k in {x["class"] for x in f["exhibits"] if x["class"] in COMMENTARY}:
            c["commentary"][k] += 1
        if f["release_class"] in COMMENTARY:
            c["commentary"]["release document: " + f["release_class"]] += 1
    for top in (True, False):
        cs = {k: v for k, v in comp.items() if v["top"] == top}
        rep[f"companies {'top500' if top else 'rest'}"] = {
            "with_index_pages": len(cs),
            "with_any_commentary": sum(bool(v["commentary"]) for v in cs.values()),
        }
    rep["top500_companies_with_commentary"] = sorted(
        ({"cik": k, "name": names.get(k), "rank": rank.get(k), "filings": v["filings"], "commentary": dict(v["commentary"])}
         for k, v in comp.items() if v["top"] and v["commentary"]), key=lambda x: x["rank"])
    desc = collections.defaultdict(collections.Counter)
    for f in filings:
        for x in f["exhibits"]:
            desc[x["class"]][x["description"][:60] or f"(none) {x['document'][:40]}"] += 1
    rep["descriptions_by_class"] = {k: dict(v.most_common(12)) for k, v in desc.items()}
    (OUT / "census.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run").set_defaults(fn=run)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
