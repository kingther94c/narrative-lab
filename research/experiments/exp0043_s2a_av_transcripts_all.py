"""EXP-0043: Alpha Vantage call transcripts, scope widened to the next quarter and the old episodes (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0043 (2026-11-23). Replaces
EXP-0042's fetch and check, with the same ledger, daily limit, folder (`s2/exp0040/`) and tests.
Targets: EXP-0040's clean rows, then the following quarter of each clean company ("next"), then
EXP-0036's old episodes ("old"). Run once a day by the owner's scheduled task.

    conda run --no-capture-output -n nlab python research/experiments/exp0043_s2a_av_transcripts_all.py targets
    conda run --no-capture-output -n nlab python research/experiments/exp0043_s2a_av_transcripts_all.py fetch --max 25
    conda run --no-capture-output -n nlab python research/experiments/exp0043_s2a_av_transcripts_all.py check
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0002_edgar_census as e2  # noqa: E402
import exp0005_earnings_exam as e5  # noqa: E402
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0041_s2a_av_transcripts_v2 as e41  # noqa: E402
import exp0042_s2a_av_transcripts_v3 as e42  # noqa: E402

OUT, RAW = e40.OUT, e40.RAW
TARGETS = OUT / "targets_all.jsonl"
RELEASES = e40.e39.RELEASES
NOT_DATA = ("limit", "fail")


# ---------------------------------------------------------------------------------------------
# Targets


def targets(_: argparse.Namespace) -> None:
    e40.need_drive()
    clean = [json.loads(line) for line in open(OUT / "targets.jsonl", encoding="utf-8")]
    rel: dict[str, list[dict]] = collections.defaultdict(list)
    for line in open(RELEASES, encoding="utf-8"):
        r = json.loads(line)
        rel[r["cik"]].append(r)
    nxt, seen = [], set()
    for r in clean:
        if not r["symbol"] or not r["av_quarter"] or (r["cik"], r["av_quarter"]) in seen:
            continue
        seen.add((r["cik"], r["av_quarter"]))
        fy, q = int(r["fy"]), int(r["av_quarter"][-1])
        fy2, q2 = (fy + 1, 1) if q == 4 else (fy, q + 1)
        cands = sorted((x for x in rel[r["cik"]] if x.get("quarter_end")
                        and 60 <= e5.days(x["quarter_end"], r["quarter_end"]) <= 120), key=lambda x: x["filing_date"])
        if not cands:
            continue
        x = cands[0]
        nxt.append({**{k: r[k] for k in ("cik", "name", "tickers", "symbol", "rank")},
                    "episode": f"next_{r['episode']}", "clean_episode": r["episode"], "release_date": x["filing_date"],
                    "release_accession": x["accession"], "quarter_end": x["quarter_end"], "fy": fy2, "fp": f"Q{q2}",
                    "fiscal_accn": None, "av_quarter": f"{fy2}Q{q2}", "calendar_fiscal": None, "ir_file": None, "stage": "next"})
    nxt.sort(key=lambda r: (r["rank"], r["cik"]))
    key = [json.loads(line) for line in open(e40.KEY36, encoding="utf-8")]
    ident = {str(co["cik"]).zfill(10): co for co in e2.companies()}
    zf = zipfile.ZipFile(e5.FACTS_ZIP)
    old = []
    for k in key:
        if k["group"] != "old":
            continue
        co = ident.get(k["cik"], {})
        lab = e40.fiscal_labels(zf, k["cik"], k["quarter_end"])
        fy, fp, accn = lab if lab else (None, None, None)
        q = 4 if fp == "FY" else int(fp[1]) if fp and re.fullmatch(r"Q[1-4]", fp) else None
        tick = co.get("tickers") or []
        old.append({"cik": k["cik"], "name": co.get("name"), "tickers": tick, "symbol": tick[0] if tick else None,
                    "rank": k["rank"], "episode": k["i"], "release_date": k["filing_date"], "quarter_end": k["quarter_end"],
                    "fy": fy, "fp": fp, "fiscal_accn": accn, "av_quarter": f"{fy}Q{q}" if fy and q else None,
                    "calendar_fiscal": None, "ir_file": None, "stage": "old"})
    old.sort(key=lambda r: (r["rank"], r["episode"]))
    rows = clean + nxt + old
    for n, r in enumerate(rows):
        r["order"] = n
    TARGETS.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"clean": len(clean), "next": len(nxt), "old": len(old),
                      "old_no_label": sum(r["av_quarter"] is None for r in old), "old_no_symbol": sum(r["symbol"] is None for r in old),
                      "distinct_requests": len({(r["cik"], r["av_quarter"]) for r in rows if r["symbol"] and r["av_quarter"]})}, indent=1))


# ---------------------------------------------------------------------------------------------
# Fetch


def load() -> list[dict]:
    return [json.loads(line) for line in open(TARGETS, encoding="utf-8")]


def todo(ts: list[dict], log: list[dict]) -> list[dict]:
    asked = {(x["cik"], x.get("quarter", x["av_quarter"])) for x in log if x["status"] not in NOT_DATA}
    out, seen = [], set()
    for r in ts:
        k = (r["cik"], r["av_quarter"])
        if r["symbol"] and r["av_quarter"] and k not in asked and k not in seen:
            out.append(r)
            seen.add(k)
    return out


def fetch(a: argparse.Namespace) -> None:
    e40.need_drive()
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        sys.exit("ALPHA_VANTAGE_API_KEY is not set in the nlab environment")
    ts = load()
    today = e40.eastern_today()
    sent = 0
    with open(OUT / "ledger.jsonl", "a", encoding="utf-8") as fh:
        while sent < a.max:
            log = e40.ledger()
            if sum(1 for x in log if x["eastern_date"] == today) >= e40.DAILY:
                break
            left = todo(ts, log)
            if not left:
                print("[fetch] nothing left to ask", flush=True)
                break
            r = left[0]
            q = {"function": "EARNINGS_CALL_TRANSCRIPT", "symbol": r["symbol"], "quarter": r["av_quarter"]}
            rec = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], **q,
                   "av_quarter": r["av_quarter"], "retry": False, "script": "exp0043", "eastern_date": today,
                   "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            if sent:
                time.sleep(e40.GAP)
            sent += 1
            try:
                req = urllib.request.Request(e40.URL + "?" + urllib.parse.urlencode({**q, "apikey": key}),
                                             headers={"User-Agent": "narrative-lab research script"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = resp.read()
                d = json.loads(body)
                if "transcript" in d:
                    e41.raw_for(r["cik"], r["av_quarter"]).write_bytes(body)
                    rec["status"] = "ok" if d["transcript"] else "empty"
                    rec["turns"] = len(d["transcript"])
                elif "Information" in d or "Note" in d:
                    rec["status"] = "limit"
                    rec["message"] = str(d.get("Information") or d.get("Note"))[:200]
                else:
                    rec["status"] = "error"
                    rec["message"] = str(d.get("Error Message") or d)[:200]
            except Exception as err:  # noqa: BLE001
                rec["status"] = "fail"
                rec["message"] = f"{type(err).__name__}: {str(err)[:160]}".replace(key, "***")
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(r["order"], r["stage"], r["symbol"], r["av_quarter"], rec["status"], rec.get("turns", ""), flush=True)
            if rec["status"] == "limit":
                print("[fetch] limit reported; stopping", flush=True)
                break
    used = sum(1 for x in e40.ledger() if x["eastern_date"] == today)
    print(f"[fetch] sent {sent}; {used} used on {today} US Eastern; {len(todo(ts, e40.ledger()))} requests left", flush=True)


# ---------------------------------------------------------------------------------------------
# Check


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    ts = load()
    by_key: dict = {}
    for r in ts:
        by_key.setdefault((r["cik"], r["av_quarter"]), r)
    rows, seen = [], set()
    for x in e40.ledger():
        quarter = x.get("quarter", x["av_quarter"])
        k = (x["cik"], quarter)
        if x["status"] not in ("ok", "empty") or k in seen or x.get("retry") or k not in by_key:
            continue  # EXP-0041's retries are void
        seen.add(k)
        r = by_key[k]
        d = json.loads(e41.raw_for(x["cik"], quarter).read_text(encoding="utf-8"))
        text = e40.text_of(d)
        low = e42.letters(text)
        turns = d.get("transcript", [])
        word = next((w for w in re.findall(r"[a-z]+", e42.letters(r["name"] or ""))
                     if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
        q_open, q_freq = e41.opening_quarter(text), e40.quarter_named(text)
        y_open, y_freq = e42.year_named(text)
        q = q_open if q_open is not None else q_freq
        y = y_open if y_open is not None else y_freq
        row = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], "symbol": r["symbol"],
               "av_quarter": r["av_quarter"], "rank": r["rank"], "release_date": r["release_date"],
               "turns": len(turns), "chars": len(text), "full": len(turns) >= 10 and len(text) >= 5000,
               "name_seen": bool(word and word in low[:5000]) or any(re.search(rf"\b{re.escape(t.lower())}\b", low[:5000]) for t in r["tickers"]),
               "quarter_open": q_open, "quarter_freq": q_freq, "quarter_ok": q == int(r["av_quarter"][-1]),
               "year_open": y_open, "year_freq": y_freq, "year_ok": y == int(r["fy"]),
               "qa_markers": len(re.findall(r"question-and-answer|questions? and answers?|\boperator\b", low))}
        row["usable"] = row["full"] and row["name_seen"] and row["quarter_ok"] and row["year_ok"]
        if r.get("ir_file"):
            ir_text = (e40.e39.TEXTS / (Path(r["ir_file"]).stem + ".txt")).read_text(encoding="utf-8")
            a, b = e40.grams(text), e40.grams(ir_text)
            row["ir_overlap"] = round(len(a & b) / len(a), 3) if a else None
            row["same_call"] = row["ir_overlap"] is not None and row["ir_overlap"] >= e40.SAME_CALL
            row["usable"] = row["usable"] or (row["full"] and row["same_call"])  # the IR text dates and names the call
        rows.append(row)
    (OUT / "checked_all.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    ok = {(x["cik"], x["av_quarter"]) for x in rows if x["usable"]}
    lg = e40.ledger()
    left = todo(ts, lg)
    rep = {"requests": len(lg), "by_status": dict(collections.Counter(x["status"] for x in lg)),
           "by_day": dict(sorted(collections.Counter(x["eastern_date"] for x in lg).items())), "requests_left": len(left),
           "requests_left_by_stage": dict(collections.Counter(r["stage"] for r in left))}
    for stage in ("clean", "next", "old"):
        sel = [r for r in ts if (r["stage"] in ("validation", "no_ir", "ir")) == (stage == "clean") and (stage == "clean" or r["stage"] == stage)]
        got = [r for r in sel if (r["cik"], r["av_quarter"]) in ok]
        xs = [x for x in rows if (x["stage"] in ("validation", "no_ir", "ir")) == (stage == "clean") and (stage == "clean" or x["stage"] == stage)]
        rep[stage] = {"episodes": len(sel), "asked": len(xs), "usable_episodes": len(got),
                      "usable_top250": sum(r["rank"] <= 250 for r in got), "empty": sum(1 for x in xs if not x["turns"]),
                      "full_not_usable": [(x["symbol"], x["av_quarter"], x["name_seen"], x["quarter_open"], x["quarter_freq"], x["year_open"], x["year_freq"])
                                          for x in xs if x["full"] and not x["usable"]]}
        if stage == "clean":
            rep[stage]["with_av_or_ir"] = len({r["episode"] for r in got} | {r["episode"] for r in sel if r.get("ir_file")})
    (OUT / "summary_all.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("targets").set_defaults(fn=targets)
    f = sub.add_parser("fetch")
    f.add_argument("--max", type=int, default=e40.DAILY)
    f.set_defaults(fn=fetch)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
