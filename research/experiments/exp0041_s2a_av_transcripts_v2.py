"""EXP-0041: Alpha Vantage call transcripts, fix forward of EXP-0040 (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0041 (2026-11-23). Same targets,
ledger, daily limit and output folder as EXP-0040 (`s2/exp0040/`). Changes: a request already sent
is never sent again (also within a run); one retry with the calendar year for episodes whose
fiscal-year label runs ahead of the calendar year and came back empty; the quarter check reads the
opening line first.

    conda run --no-capture-output -n nlab python research/experiments/exp0041_s2a_av_transcripts_v2.py fetch --max 25
    conda run --no-capture-output -n nlab python research/experiments/exp0041_s2a_av_transcripts_v2.py check
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0040_s2a_av_transcripts as e40  # noqa: E402

OUT, RAW = e40.OUT, e40.RAW
FIRST_RETRIES = ("MOD", "FLEX")  # asked first; both empty -> no other retry
LIMIT_STATUSES = ("limit", "fail")  # not data; may be asked again on a later day


def load_targets() -> list[dict]:
    return [json.loads(line) for line in open(OUT / "targets.jsonl", encoding="utf-8")]


def ahead(r: dict) -> bool:
    return bool(r["fy"]) and int(r["fy"]) > int(r["quarter_end"][:4])


def retry_quarter(r: dict) -> str:
    return f"{r['quarter_end'][:4]}Q{r['av_quarter'][-1]}"


def raw_for(cik: str, quarter: str) -> Path:
    return RAW / f"{cik}_{quarter}.json"


def plan(ts: list[dict], log: list[dict]) -> list[tuple[dict, str, bool]]:
    """The requests still to send, in order: (target, quarter asked, is_retry)."""
    asked = {(x["cik"], x["quarter"]) for x in log if x["status"] not in LIMIT_STATUSES}
    status = {(x["cik"], x["quarter"]): x["status"] for x in log if x["status"] not in LIMIT_STATUSES}
    seen: set = set()
    first, rest = [], []
    retry_cands = [r for r in ts if ahead(r) and r["symbol"] and status.get((r["cik"], r["av_quarter"])) == "empty"]
    probe = [r for s in FIRST_RETRIES for r in retry_cands if r["symbol"] == s]
    probe_status = [status.get((r["cik"], retry_quarter(r))) for r in probe]
    retry_ok = not (len(probe) == len(FIRST_RETRIES) and all(s == "empty" for s in probe_status))
    for r in probe:
        k = (r["cik"], retry_quarter(r))
        if k not in asked and k not in seen:
            first.append((r, k[1], True))
            seen.add(k)
    probes_done = all(s is not None for s in probe_status)
    for r in ts:
        if not r["av_quarter"] or not r["symbol"]:
            continue
        k = (r["cik"], r["av_quarter"])
        if k not in asked and k not in seen:
            rest.append((r, k[1], False))
            seen.add(k)
        if retry_ok and probes_done and r in retry_cands and r not in probe:
            k2 = (r["cik"], retry_quarter(r))
            if k2 not in asked and k2 not in seen:
                rest.append((r, k2[1], True))
                seen.add(k2)
    return first + rest


def fetch(a: argparse.Namespace) -> None:
    e40.need_drive()
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        sys.exit("ALPHA_VANTAGE_API_KEY is not set in the nlab environment")
    if (OUT / "STOP").exists():
        sys.exit(f"stopped by rule: {(OUT / 'STOP').read_text(encoding='utf-8').strip()}")
    ts = load_targets()
    today = e40.eastern_today()
    sent = 0
    with open(OUT / "ledger.jsonl", "a", encoding="utf-8") as fh:
        while True:
            log = e40.ledger()
            used = sum(1 for x in log if x["eastern_date"] == today)
            if sent >= a.max or used >= e40.DAILY:
                break
            todo = plan(ts, log)  # re-planned after every request, so nothing is sent twice
            if not todo:
                print("[fetch] nothing left to ask", flush=True)
                break
            r, quarter, is_retry = todo[0]
            q = {"function": "EARNINGS_CALL_TRANSCRIPT", "symbol": r["symbol"], "quarter": quarter}
            rec = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], **q,
                   "av_quarter": r["av_quarter"], "retry": is_retry, "script": "exp0041", "eastern_date": today,
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
                    raw_for(r["cik"], quarter).write_bytes(body)
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
            print(r["order"], r["stage"], r["symbol"], quarter, "retry" if is_retry else "", rec["status"], rec.get("turns", ""), flush=True)
            if rec["status"] == "limit":
                print("[fetch] limit reported; stopping", flush=True)
                break
    print(f"[fetch] sent {sent}; {sum(1 for x in e40.ledger() if x['eastern_date'] == today)} used on {today} US Eastern", flush=True)


def opening_quarter(text: str) -> int | None:
    head = text[:600].lower()
    m = re.search(r"\b(first|second|third|fourth)[- ](?:fiscal[- ])?quarter\b|\bq([1-4])\b|\bquarter ([1-4])\b", head)
    if not m:
        return None
    return e40.ORDINALS[m[1]] if m[1] else int(m[2] or m[3])


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    ts = load_targets()
    by_key: dict = {}
    for r in ts:  # the first target of a (cik, fiscal quarter) is the one that was asked
        by_key.setdefault((r["cik"], r["av_quarter"]), r)
    rows, seen = [], set()
    for x in e40.ledger():
        quarter = x.get("quarter", x["av_quarter"])
        k = (x["cik"], quarter)
        if x["status"] not in ("ok", "empty") or k in seen:
            continue
        seen.add(k)
        r = by_key[(x["cik"], x["av_quarter"])]
        d = json.loads(raw_for(x["cik"], quarter).read_text(encoding="utf-8"))
        text = e40.text_of(d)
        low = text.lower()
        turns = d.get("transcript", [])
        word = next((w for w in re.findall(r"[a-z]+", (r["name"] or "").lower())
                     if len(w) > 2 and w not in ("the", "inc", "corp", "group", "company")), "")
        want = int(r["av_quarter"][-1])
        q_open, q_freq = opening_quarter(text), e40.quarter_named(text)
        q = q_open if q_open is not None else q_freq
        d_text = e40.e39.first_date(text)
        delta = (d_text - dt.date.fromisoformat(r["release_date"])).days if d_text else None
        row = {"order": r["order"], "stage": r["stage"], "episode": r["episode"], "cik": r["cik"], "symbol": r["symbol"],
               "av_quarter": r["av_quarter"], "asked": quarter, "retry": bool(x.get("retry")), "rank": r["rank"],
               "turns": len(turns), "chars": len(text), "full": len(turns) >= 10 and len(text) >= 5000,
               "name_seen": bool(word and word in low[:5000]) or any(re.search(rf"\b{re.escape(t.lower())}\b", low[:5000]) for t in r["tickers"]),
               "quarter_open": q_open, "quarter_freq": q_freq, "quarter_ok": q == want, "quarter_ok_freq_rule": q_freq == want,
               "qa_markers": len(re.findall(r"question-and-answer|questions? and answers?|\boperator\b", low)),
               "date_in_text": d_text.isoformat() if d_text else None, "days_after_release": delta,
               "date_flag": delta is not None and not (-1 <= delta <= 3)}
        row["usable"] = row["full"] and row["name_seen"] and row["quarter_ok"]
        if r["ir_file"]:
            ir_text = (e40.e39.TEXTS / (Path(r["ir_file"]).stem + ".txt")).read_text(encoding="utf-8")
            a, b = e40.grams(text), e40.grams(ir_text)
            row["ir_overlap"] = round(len(a & b) / len(a), 3) if a else None
            row["same_call"] = row["ir_overlap"] is not None and row["ir_overlap"] >= e40.SAME_CALL
        rows.append(row)
    (OUT / "checked_v2.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    usable = {x["cik"] for x in rows if x["usable"]}
    eps_usable = [r for r in ts if r["cik"] in usable and any(x["usable"] and x["cik"] == r["cik"] and x["av_quarter"] == r["av_quarter"] for x in rows)]
    ir_eps = [r for r in ts if r["ir_file"]]
    lg = e40.ledger()
    distinct = {(r["cik"], r["av_quarter"]) for r in ts if r["av_quarter"] and r["symbol"]}
    rep = {"requests": len(lg), "by_status": dict(collections.Counter(x["status"] for x in lg)),
           "by_day": dict(collections.Counter(x["eastern_date"] for x in lg)),
           "distinct_asked": len({(x["cik"], x["av_quarter"]) for x in lg if x["status"] in ("ok", "empty")} & distinct),
           "distinct_total": len(distinct),
           "usable_transcripts": len([x for x in rows if x["usable"]]),
           "episodes_usable": len(eps_usable), "episodes_usable_top250": sum(r["rank"] <= 250 for r in eps_usable),
           "episodes_with_av_or_ir": len({r["episode"] for r in eps_usable} | {r["episode"] for r in ir_eps}),
           "retries": [(x["symbol"], x["asked"], x["turns"], x["quarter_ok"]) for x in rows if x["retry"]],
           "empty": [(x["symbol"], x["asked"]) for x in rows if not x["turns"]],
           "quarter_mismatch": [(x["symbol"], x["av_quarter"], x["quarter_open"], x["quarter_freq"]) for x in rows if x["full"] and not x["quarter_ok"]],
           "freq_rule_disagrees": [(x["symbol"], x["quarter_open"], x["quarter_freq"]) for x in rows if x["full"] and x["quarter_ok"] != x["quarter_ok_freq_rule"]],
           "name_missing": [x["symbol"] for x in rows if x["full"] and not x["name_seen"]],
           "date_flags": [(x["symbol"], x["date_in_text"]) for x in rows if x["date_flag"]],
           "ir_overlap": [(x["symbol"], x["ir_overlap"]) for x in rows if "ir_overlap" in x]}
    (OUT / "summary_v2.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
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
