"""EXP-0040: earnings-call transcripts from Alpha Vantage for EXP-0036's clean episodes (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0040 (2026-11-23). One request
to EARNINGS_CALL_TRANSCRIPT per clean episode, for the fiscal quarter the company's own 10-Q or
10-K labels. At most 25 requests a US Eastern day (free key), counted in a local ledger. The key
is read from ALPHA_VANTAGE_API_KEY and never written anywhere. Replies stay on the drive (rule 12).

    conda run --no-capture-output -n nlab python research/experiments/exp0040_s2a_av_transcripts.py targets
    conda run --no-capture-output -n nlab python research/experiments/exp0040_s2a_av_transcripts.py fetch --max 25
    conda run --no-capture-output -n nlab python research/experiments/exp0040_s2a_av_transcripts.py check
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as e5  # noqa: E402
import exp0039_s2a_ir_transcripts as e39  # noqa: E402

DRIVE = e39.DRIVE
OUT = DRIVE / "s2" / "exp0040"
RAW = OUT / "raw"
KEY36 = e39.KEY36
SEED = 20261125
DAILY = 25  # free key, per US Eastern day (owner, 2026-11-23)
GAP = 15.0  # seconds between requests
EASTERN = ZoneInfo("America/New_York")
URL = "https://www.alphavantage.co/query"
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
SAME_CALL = 0.5  # share of AV word 8-grams found in the IR text


def need_drive() -> None:
    if not DRIVE.exists():
        sys.exit("drive not mounted")


# ---------------------------------------------------------------------------------------------
# Targets


def fiscal_labels(zf: zipfile.ZipFile, cik: str, quarter_end: str) -> tuple[int, str, str] | None:
    """(fy, fp, accn) of the first 10-Q or 10-K that reports a value for a period ending at quarter_end."""
    try:
        facts = json.loads(zf.read(f"CIK{cik}.json")).get("facts", {})
    except KeyError:
        return None
    best = None
    for ns in facts.values():
        for tag in ns.values():
            for unit in tag.get("units", {}).values():
                for r in unit:
                    if r.get("form") not in ("10-Q", "10-K") or not r.get("fy") or not r.get("fp"):
                        continue
                    if abs(e5.days(r["end"], quarter_end)) > 5 or r["filed"] < quarter_end:
                        continue
                    if best is None or r["filed"] < best[0]:
                        best = (r["filed"], r["fy"], r["fp"], r["accn"])
    return (best[1], best[2], best[3]) if best else None


def targets(_: argparse.Namespace) -> None:
    need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    key = [json.loads(line) for line in open(KEY36, encoding="utf-8")]
    clean = {k["i"]: k for k in key if k["group"] == "clean"}
    t39 = [json.loads(line) for line in open(e39.OUT / "targets.jsonl", encoding="utf-8")]
    ir = {}  # cik -> IR transcript text file, from EXP-0039
    for line in open(e39.OUT / "extracted.jsonl", encoding="utf-8"):
        x = json.loads(line)
        if x["kind"] == "transcript" and x["chars"] > 5000:
            ir.setdefault(x["cik"], x)
    zf = zipfile.ZipFile(e5.FACTS_ZIP)
    rows = []
    for t in t39:
        k = clean[t["episode"]]
        lab = fiscal_labels(zf, t["cik"], t["quarter_end"])
        fy, fp, accn = lab if lab else (None, None, None)
        q = 4 if fp == "FY" else int(fp[1]) if fp and re.fullmatch(r"Q[1-4]", fp) else None
        # calendar quarter of the quarter's end, moved back 15 days so that a 52/53-week quarter
        # ending in the first days of July still counts as the calendar second quarter
        mid = dt.date.fromisoformat(t["quarter_end"]) - dt.timedelta(days=15)
        cal = (mid.month + 2) // 3
        x = ir.get(t["cik"])
        # the IR call belongs to the release EXP-0039 matched it to; a second release of the same
        # quarter (two clean episodes, one quarter) shares that call
        ir_q = next((u["quarter_end"] for u in t39 if x and u["cik"] == t["cik"] and u["release_date"] == x.get("release_date")), None)
        ir_ok = bool(x) and ir_q == t["quarter_end"]
        rows.append({"episode": t["episode"], "cik": t["cik"], "name": t["name"], "tickers": t["tickers"],
                     "symbol": t["tickers"][0] if t["tickers"] else None, "rank": k["rank"],
                     "release_date": t["release_date"], "quarter_end": t["quarter_end"],
                     "fy": fy, "fp": fp, "fiscal_accn": accn, "av_quarter": f"{fy}Q{q}" if fy and q else None,
                     "calendar_fiscal": q == cal if q else None, "ir_file": x["file"] if ir_ok else None})
    with_ir = [r for r in rows if r["ir_file"] and r["av_quarter"] and r["symbol"]]
    rng = random.Random(SEED)
    cal_pool = sorted((r for r in with_ir if r["calendar_fiscal"]), key=lambda r: r["episode"])
    off_pool = sorted((r for r in with_ir if r["calendar_fiscal"] is False), key=lambda r: r["episode"])
    val = rng.sample(cal_pool, min(1, len(cal_pool))) + rng.sample(off_pool, min(2, len(off_pool)))
    if len(val) < 3:  # fewer non-calendar companies than two: fill from the calendar ones
        rest = [r for r in cal_pool if r not in val]
        val += rng.sample(rest, 3 - len(val))
    vids = {r["episode"] for r in val}
    no_ir = sorted((r for r in rows if not r["ir_file"]), key=lambda r: (r["rank"], r["episode"]))
    yes_ir = sorted((r for r in rows if r["ir_file"] and r["episode"] not in vids), key=lambda r: (r["rank"], r["episode"]))
    ordered = [dict(r, stage="validation") for r in val] + [dict(r, stage="no_ir") for r in no_ir] + \
              [dict(r, stage="ir") for r in yes_ir]
    for n, r in enumerate(ordered):
        r["order"] = n
    (OUT / "targets.jsonl").write_text("".join(json.dumps(r) + "\n" for r in ordered), encoding="utf-8")
    print(json.dumps({"episodes": len(ordered), "validation": [(r["episode"], r["symbol"], r["av_quarter"], r["calendar_fiscal"]) for r in val],
                      "no_ir": len(no_ir), "ir_rest": len(yes_ir), "no_fiscal_label": sum(r["av_quarter"] is None for r in ordered),
                      "no_symbol": sum(r["symbol"] is None for r in ordered),
                      "non_calendar": sum(r["calendar_fiscal"] is False for r in ordered)}, indent=1))


# ---------------------------------------------------------------------------------------------
# Fetch


def eastern_today() -> str:
    return dt.datetime.now(EASTERN).date().isoformat()


def ledger() -> list[dict]:
    p = OUT / "ledger.jsonl"
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def raw_path(r: dict) -> Path:
    return RAW / f"{r['cik']}_{r['av_quarter']}.json"


def fetch(a: argparse.Namespace) -> None:
    need_drive()
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        sys.exit("ALPHA_VANTAGE_API_KEY is not set (conda env config vars set ALPHA_VANTAGE_API_KEY=... -n nlab)")
    RAW.mkdir(parents=True, exist_ok=True)
    ts = [json.loads(line) for line in open(OUT / "targets.jsonl", encoding="utf-8")]
    log = ledger()
    done = {(x["cik"], x["av_quarter"]) for x in log if x["status"] in ("ok", "empty", "error")}
    today = eastern_today()
    used = sum(1 for x in log if x["eastern_date"] == today)
    budget = min(a.max, DAILY - used)
    if (OUT / "STOP").exists():
        sys.exit(f"stopped by rule: {(OUT / 'STOP').read_text(encoding='utf-8').strip()}")
    print(f"[fetch] {today} US Eastern: {used} used today, sending at most {budget}", flush=True)
    sent = 0
    with open(OUT / "ledger.jsonl", "a", encoding="utf-8") as fh:
        for r in ts:
            if sent >= budget:
                break
            if not r["av_quarter"] or not r["symbol"] or (r["cik"], r["av_quarter"]) in done:
                continue
            q = {"function": "EARNINGS_CALL_TRANSCRIPT", "symbol": r["symbol"], "quarter": r["av_quarter"]}
            rec = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], **q,
                   "av_quarter": r["av_quarter"], "eastern_date": today, "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            if sent:
                time.sleep(GAP)
            try:
                req = urllib.request.Request(URL + "?" + urllib.parse.urlencode({**q, "apikey": key}),
                                             headers={"User-Agent": "narrative-lab research script"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = resp.read()
                d = json.loads(body)
                sent += 1
                if "transcript" in d:
                    raw_path(r).write_bytes(body)
                    rec["status"] = "ok" if d["transcript"] else "empty"
                    rec["turns"] = len(d["transcript"])
                elif "Information" in d or "Note" in d:  # the limit message: stop, keep nothing as data
                    rec["status"] = "limit"
                    rec["message"] = str(d.get("Information") or d.get("Note"))[:200]
                else:
                    rec["status"] = "error"
                    rec["message"] = str(d.get("Error Message") or d)[:200]
            except Exception as err:  # noqa: BLE001
                sent += 1
                rec["status"] = "fail"
                rec["message"] = f"{type(err).__name__}: {str(err)[:160]}".replace(key, "***")
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(r["order"], r["stage"], r["symbol"], r["av_quarter"], rec["status"], rec.get("turns", ""), flush=True)
            if rec["status"] == "limit":
                print("[fetch] limit reported; stopping", flush=True)
                break
            if r["stage"] == "validation" and all((v["cik"], v["av_quarter"]) in done | {(r["cik"], r["av_quarter"])}
                                                  for v in ts if v["stage"] == "validation"):
                print("[fetch] validation episodes fetched; run `check` before more requests", flush=True)
                break
    print(f"[fetch] sent {sent}", flush=True)


# ---------------------------------------------------------------------------------------------
# Check


def text_of(d: dict) -> str:
    return "\n".join(f"{t.get('speaker', '')}: {t.get('content', '')}" for t in d.get("transcript", []))


def grams(s: str, n: int = 8) -> set:
    w = re.findall(r"[a-z0-9]+", s.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def quarter_named(text: str) -> int | None:
    head = text[:6000].lower()
    c = collections.Counter()
    for m in re.finditer(r"\b(first|second|third|fourth)[- ]quarter\b", head):
        c[ORDINALS[m[1]]] += 1
    for m in re.finditer(r"\bq([1-4])\b", head):
        c[int(m[1])] += 1
    return c.most_common(1)[0][0] if c else None


def check(_: argparse.Namespace) -> None:
    need_drive()
    ts = {(r["cik"], r["av_quarter"]): r for r in map(json.loads, open(OUT / "targets.jsonl", encoding="utf-8"))}
    rows = []
    for x in ledger():
        if x["status"] not in ("ok", "empty"):
            continue
        r = ts[(x["cik"], x["av_quarter"])]
        d = json.loads(raw_path(r).read_text(encoding="utf-8"))
        text = text_of(d)
        low = text.lower()
        turns = d.get("transcript", [])
        word = next((w for w in re.findall(r"[a-z]+", (r["name"] or "").lower())
                     if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
        q = quarter_named(text)
        want = int(r["av_quarter"][-1])
        d_text = e39.first_date(text)
        delta = (d_text - dt.date.fromisoformat(r["release_date"])).days if d_text else None
        row = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], "symbol": r["symbol"],
               "av_quarter": r["av_quarter"], "rank": r["rank"], "turns": len(turns), "chars": len(text),
               "full": len(turns) >= 10 and len(text) >= 5000,
               "name_seen": bool(word and word in low[:5000]) or any(re.search(rf"\b{re.escape(t.lower())}\b", low[:5000]) for t in r["tickers"]),
               "quarter_named": q, "quarter_ok": q == want,
               "qa_markers": len(re.findall(r"question-and-answer|questions? and answers?|\boperator\b", low)),
               "date_in_text": d_text.isoformat() if d_text else None, "days_after_release": delta,
               "date_flag": delta is not None and not (-1 <= delta <= 3)}
        if r["ir_file"]:
            ir_text = (e39.TEXTS / (Path(r["ir_file"]).stem + ".txt")).read_text(encoding="utf-8")
            a, b = grams(text), grams(ir_text)
            row["ir_overlap"] = round(len(a & b) / len(a), 3) if a else None
            row["same_call"] = row["ir_overlap"] is not None and row["ir_overlap"] >= SAME_CALL
        rows.append(row)
    (OUT / "checked.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    val = [x for x in rows if x["stage"] == "validation"]
    fails = [x for x in val if not (x["quarter_ok"] and x.get("same_call"))]
    if len(fails) >= 2 and not (OUT / "STOP").exists():
        (OUT / "STOP").write_text(f"{len(fails)} of {len(val)} validation episodes failed (registry stop rule)", encoding="utf-8")
    lg = ledger()
    rep = {"requests": len(lg), "by_status": dict(collections.Counter(x["status"] for x in lg)),
           "by_day": dict(collections.Counter(x["eastern_date"] for x in lg)),
           "validation": [{k: x.get(k) for k in ("symbol", "av_quarter", "turns", "quarter_named", "quarter_ok", "ir_overlap", "same_call")} for x in val],
           "stopped": (OUT / "STOP").exists(),
           "full": sum(x["full"] for x in rows), "full_top250": sum(x["full"] and x["rank"] <= 250 for x in rows),
           "quarter_mismatch": [(x["symbol"], x["av_quarter"], x["quarter_named"]) for x in rows if x["full"] and not x["quarter_ok"]],
           "name_missing": [x["symbol"] for x in rows if x["full"] and not x["name_seen"]],
           "date_flags": [(x["symbol"], x["date_in_text"]) for x in rows if x["date_flag"]],
           "not_same_call": [(x["symbol"], x["ir_overlap"]) for x in rows if "same_call" in x and not x["same_call"]]}
    (OUT / "summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("targets").set_defaults(fn=targets)
    f = sub.add_parser("fetch")
    f.add_argument("--max", type=int, default=DAILY)
    f.set_defaults(fn=fetch)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
