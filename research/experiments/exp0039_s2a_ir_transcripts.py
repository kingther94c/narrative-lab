"""EXP-0039: earnings-call text from company IR sites for EXP-0036's clean episodes (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0039 (2026-11-23). Subagents
find file addresses on each company's own IR site; this script lists the targets, downloads the
files to the drive, extracts their text and checks the call date against the release date.
Nothing it writes enters git (rule 12).

    conda run --no-capture-output -n nlab python research/experiments/exp0039_s2a_ir_transcripts.py targets
    # subagents' answers are saved as s2/exp0039/found_<batch>.json
    conda run --no-capture-output -n nlab python research/experiments/exp0039_s2a_ir_transcripts.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0039_s2a_ir_transcripts.py extract
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0002_edgar_census as e2  # noqa: E402

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
OUT = DRIVE / "s2" / "exp0039"
FILES = OUT / "files"
TEXTS = OUT / "texts"
KEY36 = DRIVE / "s2" / "exp0036" / "key.jsonl"
RELEASES = DRIVE / "s2" / "exp0020" / "releases.jsonl"
SEED = 20261124
BATCH = 24
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
KINDS = ("transcript", "prepared_remarks", "cfo_commentary", "letter")
MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
PRODUCERS = re.compile(r"factset|callstreet|refinitiv|lseg|streetevents|thomson reuters|s&p global|viavid|notified|q4 inc|nasdaq|choruscall|chorus call|seeking alpha", re.I)


def need_drive() -> None:
    if not DRIVE.exists():
        sys.exit("drive not mounted")


def targets(_: argparse.Namespace) -> None:
    need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    key = [json.loads(line) for line in open(KEY36, encoding="utf-8")]
    clean = [k for k in key if k["group"] == "clean"]
    acc = {json.loads(line)["accession"]: json.loads(line) for line in open(RELEASES, encoding="utf-8")}
    ciks = {k["cik"] for k in clean}
    ident = {}
    for co in e2.companies():
        c = str(co["cik"]).zfill(10)
        if c in ciks:
            ident[c] = {"name": co["name"], "tickers": co["tickers"]}
    rows = []
    for k in sorted(clean, key=lambda k: (k["cik"], k["filing_date"])):
        r = acc.get(k["accession"], {})
        rows.append({"cik": k["cik"], "name": ident.get(k["cik"], {}).get("name"), "tickers": ident.get(k["cik"], {}).get("tickers", []),
                     "accession": k["accession"], "release_date": k["filing_date"], "acceptance": r.get("acceptance"),
                     "quarter_end": k["quarter_end"], "episode": k["i"]})
    with open(OUT / "targets.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    by: dict[str, dict] = {}
    for r in rows:  # one entry per company; a company with two clean episodes lists both releases
        c = by.setdefault(r["cik"], {"cik": r["cik"], "name": r["name"], "tickers": r["tickers"], "releases": []})
        c["releases"].append({"release_date": r["release_date"], "quarter_end": r["quarter_end"]})
    cos = sorted(by.values(), key=lambda c: c["cik"])
    random.Random(SEED).shuffle(cos)
    for b in range(0, len(cos), BATCH):
        (OUT / f"batch_{b // BATCH + 1}.json").write_text(json.dumps(cos[b:b + BATCH], indent=1), encoding="utf-8")
    print(f"{len(rows)} episodes, {len(ciks)} companies, {sum(1 for _ in OUT.glob('batch_*.json'))} batches; names missing: "
          f"{sum(r['name'] is None for r in rows)}")


def found() -> list[dict]:
    """Subagents' answers; a later pass (found_9 onward, the browser recheck) replaces a company's earlier entry."""
    out: dict[str, dict] = {}
    for p in sorted(OUT.glob("found_*.json"), key=lambda p: int(p.stem.split("_")[1])):
        for r in json.loads(p.read_text(encoding="utf-8")):
            r["batch"] = p.stem
            out[r["cik"]] = r
    return list(out.values())


def file_path(cik: str, kind: str, n: int, url: str) -> Path:
    ext = re.search(r"\.(pdf|htm|html|docx|txt)(?:$|\?)", url.lower())
    return FILES / f"{cik}_{kind}_{n}.{ext.group(1) if ext else 'bin'}"


def fetch(_: argparse.Namespace) -> None:
    need_drive()
    FILES.mkdir(parents=True, exist_ok=True)
    log = OUT / "fetch_log.jsonl"
    done = set()
    if log.exists():
        done = {r["url"] for r in map(json.loads, log.read_text(encoding="utf-8").splitlines()) if r["status"] == "ok"}
    with open(log, "a", encoding="utf-8") as fh:
        for r in found():
            for n, f in enumerate(r.get("files") or []):
                url = (f.get("url") or "").strip()
                if not url.startswith("http") or url in done or f.get("kind") not in KINDS:
                    continue
                p = file_path(r["cik"], f["kind"], n, url)
                rec = {"cik": r["cik"], "kind": f["kind"], "url": url, "path": p.name}
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        body = resp.read()
                        rec["content_type"] = resp.headers.get("Content-Type")
                    p.write_bytes(body)
                    rec.update(status="ok", bytes=len(body), sha256=hashlib.sha256(body).hexdigest()[:16])
                except Exception as err:  # noqa: BLE001  (a refusal is recorded, not worked around)
                    rec["status"] = f"error: {type(err).__name__}: {str(err)[:120]}"
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                print(r["cik"], f["kind"], rec["status"], rec.get("bytes"), flush=True)
                time.sleep(1.0)


def to_text(p: Path, content_type: str | None) -> str:
    body = p.read_bytes()
    if body[:5] == b"%PDF-":
        from pdfminer.high_level import extract_text
        return extract_text(str(p)) or ""
    if body[:2] == b"PK":
        return ""  # .docx: not read; the subagent is asked for the HTML or PDF form instead
    html = body.decode("utf-8", "ignore")
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", html)).replace("&nbsp;", " ").replace("&amp;", "&")


def first_date(text: str) -> dt.date | None:
    head = text[:4000]
    pats = (
        (r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? (\d{1,2}),? (20\d\d)\b", lambda m: (int(m[3]), MONTHS[m[1].lower()[:3]], int(m[2]))),
        (r"\b(\d{1,2})[- ](jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[- ](20\d\d)\b", lambda m: (int(m[3]), MONTHS[m[2].lower()[:3]], int(m[1]))),
        (r"\b(20\d\d)-(\d\d)-(\d\d)\b", lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    )
    best = None
    for rx, conv in pats:
        for m in re.finditer(rx, head, re.I):
            try:
                d = dt.date(*conv(m))
            except ValueError:
                continue
            pos = m.start()
            if best is None or pos < best[0]:
                best = (pos, d)
            break
    return best[1] if best else None


def extract(_: argparse.Namespace) -> None:
    need_drive()
    TEXTS.mkdir(parents=True, exist_ok=True)
    tg: dict[str, list[dict]] = collections.defaultdict(list)
    for line in open(OUT / "targets.jsonl", encoding="utf-8"):
        t = json.loads(line)
        tg[t["cik"]].append(t)
    recs = {}
    for line in open(OUT / "fetch_log.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["status"] == "ok":
            recs[r["path"]] = r
    rows = []
    for name, r in sorted(recs.items()):
        p = FILES / name
        text = to_text(p, r.get("content_type"))
        (TEXTS / (p.stem + ".txt")).write_text(text, encoding="utf-8")
        d = first_date(text)
        rels = [dt.date.fromisoformat(t["release_date"]) for t in tg.get(r["cik"], [])]
        rel = min(rels, key=lambda x: abs((d - x).days)) if d and rels else (rels[0] if rels else None)  # nearest listed release
        delta = (d - rel).days if d and rel else None
        low = text.lower()
        name = (tg[r["cik"]][0]["name"] or "") if r["cik"] in tg else ""
        word = next((w for w in re.findall(r"[a-z]+", name.lower()) if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
        tickers = [x.lower() for x in (tg[r["cik"]][0]["tickers"] if r["cik"] in tg else [])]
        rows.append({"cik": r["cik"], "kind": r["kind"], "file": name and r["path"] or r["path"], "chars": len(text), "call_date": d.isoformat() if d else None,
                     "release_date": rel.isoformat() if rel else None, "days_after_release": delta,
                     "name_seen": bool(word and word in low[:5000]) or any(re.search(rf"\b{re.escape(x)}\b", low[:5000]) for x in tickers),
                     "date_flag": delta is None or not (-1 <= delta <= 3),
                     "qa_markers": len(re.findall(r"question-and-answer|questions? and answers?|\boperator\b", low)),
                     "producer": sorted({m.lower() for m in PRODUCERS.findall(text[:6000] + text[-3000:])})})
    (OUT / "extracted.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    fs = found()
    rep = {
        "companies_searched": len({r["cik"] for r in fs}),
        "status": dict(collections.Counter(r.get("status") for r in fs)),
        "files_ok": len(rows),
        "by_kind": dict(collections.Counter(x["kind"] for x in rows)),
        "companies_with_transcript_text": len({x["cik"] for x in rows if x["kind"] == "transcript" and x["chars"] > 5000}),
        "companies_with_any_text": len({x["cik"] for x in rows if x["chars"] > 2000}),
        "date_flags": [x["file"] for x in rows if x["date_flag"]],
        "short_texts": [x["file"] for x in rows if x["chars"] <= 2000],
        "producers": dict(collections.Counter(p for x in rows for p in x["producer"])),
    }
    (OUT / "summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("targets", targets), ("fetch", fetch), ("extract", extract)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
