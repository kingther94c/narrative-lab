"""EXP-0048: S2 prospective arm, sealed calls on the October and November 2026 releases

Pre-registration: research/registry/experiment_registry.md, EXP-0048 (approved 2026-11-24). The
184 "next" episodes of EXP-0046 (training and development companies). Stages:

1. ``prepare_r``: EXP-0036's reader (R) on each release; its form feeds the code facts.
2. ``build --series <series.jsonl>``: once R is ingested and the December company-facts series
   exists, EXP-0036's code facts per episode, then A1 (EXP-0036's A1 prompt) for all and A1C
   (EXP-0047's prompt) where EXP-0045 holds a full call document.
3. ``seal``: drops any company that has filed an earnings 8-K (Item 2.02) after its October or
   November release, writes the forecasts on the drive and a manifest of SHA-256 hashes into
   ``research/registry/seals/`` (hashes only) to be committed and pushed before 2027-01-10.

Scoring waits for the December quarter's filings (about March 2027) and is a later script.

    conda run --no-capture-output -n nlab python research/experiments/exp0048_s2_prospective.py prepare_r
    (exp0023 emit --run exp0048 --items s2/exp0048/items_r.jsonl; exp0027 run; exp0023 ingest)
    conda run --no-capture-output -n nlab python research/experiments/exp0048_s2_prospective.py build --series <path>
    (emit, run, ingest: items_ax.jsonl)
    conda run --no-capture-output -n nlab python research/experiments/exp0048_s2_prospective.py seal
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402
import exp0031_s2b_rewrite as e31  # noqa: E402
import exp0032_s2b_rewrite_v2 as e32  # noqa: E402
import exp0036_s2b_skill_v1 as e36  # noqa: E402
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0045_s2a_call_texts as e45  # noqa: E402
import exp0047_s2b_call_pilot as e47  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0048"
RUN = "exp0048"
SEALS = Path(__file__).resolve().parents[1] / "registry" / "seals"
DEADLINE = "2027-01-10"


def episodes() -> list[dict]:
    rel = {json.loads(line)["accession"]: json.loads(line) for line in open(e22.LIST, encoding="utf-8")}
    out = []
    for line in open(e40.OUT / "targets_all.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["stage"] != "next":
            continue
        x = rel[r["release_accession"]]
        out.append({"episode": r["episode"], "n": len(out), "cik": r["cik"], "symbol": r["symbol"], "rank": r["rank"],
                    "accession": x["accession"], "filing_date": x["filing_date"], "acceptance": x.get("acceptance"),
                    "quarter_end": x["quarter_end"], "fy": r["fy"], "fp": r["fp"]})
    return out


def release(ep: dict) -> str:
    p = e22.text_path(ep)
    if p is None:
        raise SystemExit(f"release text missing for {ep['episode']}")
    return e22.clean(p.read_text(encoding="utf-8"))


def prepare_r(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    allx = episodes()
    no_text = [ep for ep in allx if e22.text_path(ep) is None]  # dropped: no release text on the drive
    eps = [ep for ep in allx if e22.text_path(ep) is not None]
    with open(OUT / "items_r.jsonl", "w", encoding="utf-8") as fh:
        for ep in eps:
            fh.write(json.dumps({"id": f"r{ep['n']:03d}", "agent": e26.PM, "prompt": e36.R_PROMPT + release(ep)}, ensure_ascii=False) + "\n")
    (OUT / "key.jsonl").write_text("".join(json.dumps(ep) + "\n" for ep in eps), encoding="utf-8")
    rep = {"episodes": len(eps), "dropped_no_release_text": [(ep["symbol"], ep["filing_date"], ep["accession"]) for ep in no_text],
           "release_months": dict(collections.Counter(ep["filing_date"][:7] for ep in eps)),
           "skill_block_sha256_16": e36.considerations()[1]}
    (OUT / "prepare_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def replies() -> dict[str, str]:
    return {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / RUN) if r["canary_ok"]}


def load_series(path: Path) -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = collections.defaultdict(list)
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        by[r["cik"]].append(r)
    return by


def build(a: argparse.Namespace) -> None:
    e23.need_drive()
    got = replies()
    series = load_series(Path(a.series))
    lines, eps_pool = e36.pool()
    key = e26.load(OUT / "key.jsonl")
    docs = {}
    for line in open(e45.OUT / "calls.jsonl", encoding="utf-8"):
        x = json.loads(line)
        if x["stage"] == "next" and not x["partial"]:
            docs[x["episode"]] = x
    built, tot, bad, items = {}, collections.Counter(), [], []
    for k in key:
        rel = release(k)
        j = e31.as_json(got.get(f"r{k['n']:03d}", ""))
        form = None
        if j is not None:  # as EXP-0036's build
            v, log = e31.verify(j, rel)
            b = e32.bases(series.get(k["cik"], []), k["quarter_end"])
            for tag, f in (("next_quarter", "next_quarter_revenue_guidance_amount"), ("full_year", "full_year_revenue_guidance_amount")):
                if v[f"{tag}_guidance_growth_low"] is not None or v[f"{tag}_guidance_growth_high"] is not None:
                    v[f"{tag}_guidance_source"] = "stated"
                    continue
                lo, hi = e32.amount(j, f, rel, log)
                glo, ghi = e32.implied(lo, hi, b[tag], log, tag)
                if glo is not None:
                    v[f"{tag}_guidance_growth_low"], v[f"{tag}_guidance_growth_high"] = glo, ghi
                    v[f"{tag}_guidance_source"] = "implied"
            v.update(e36.verify_extra(j, rel, log))
            tot.update(log)
            form = v
        else:
            bad.append(k["episode"])
        ftext, used = e36.facts(k, series.get(k["cik"], []), lines, eps_pool, form, rel)
        built[k["episode"]] = {"facts": ftext, "facts_used": used, "form": form}
        tot.update({f"facts_{x}": n for x, n in used.items()})
        items.append({"id": f"a{k['n']:03d}", "agent": e26.PM, "prompt": e47.a_prompt(rel, ftext)})
        d = docs.get(k["episode"])
        if d:
            call = (e45.DOCS / d["file"]).read_text(encoding="utf-8")
            items.append({"id": f"x{k['n']:03d}", "agent": e26.PM, "prompt": e47.x_prompt(rel, ftext, call)})
    (OUT / "built.json").write_text(json.dumps(built, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "items_ax.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), encoding="utf-8")
    rep = {"episodes": len(key), "reader_unparsed": bad, "a1": sum(x["id"][0] == "a" for x in items),
           "a1c": sum(x["id"][0] == "x" for x in items), "series": str(a.series), "log": dict(tot)}
    (OUT / "build_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def later_earnings_8k(cik: str, after: str) -> list[str]:
    """Earnings 8-Ks (Item 2.02) the company filed after a date, from EDGAR via edgartools."""
    from edgar import Company, set_identity
    set_identity(os.environ["EDGAR_IDENTITY"])
    out = []
    for f in Company(int(cik)).get_filings(form="8-K", filing_date=f"{after}:"):
        items = str(getattr(f, "items", "") or "")
        if "2.02" in items and str(f.filing_date) > after:
            out.append(str(f.filing_date))
    return out


def seal(_: argparse.Namespace) -> None:
    e23.need_drive()
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    now = dt.datetime.now(dt.timezone.utc)
    if now.date().isoformat() >= DEADLINE:
        sys.exit(f"past the sealing deadline {DEADLINE}")
    got = replies()
    key = e26.load(OUT / "key.jsonl")
    dropped, rows = [], []
    for k in key:
        later = later_earnings_8k(k["cik"], k["filing_date"])
        if later:
            dropped.append({"episode": k["episode"], "symbol": k["symbol"], "later_8k": later})
            continue
        for tag in ("a", "x"):
            rid = f"{tag}{k['n']:03d}"
            if rid in got:
                rows.append({"id": rid, "arm": "A1" if tag == "a" else "A1C", "episode": k["episode"], "cik": k["cik"],
                             "symbol": k["symbol"], "release_date": k["filing_date"],
                             "reply_sha256": hashlib.sha256(got[rid].encode()).hexdigest(), "reply": got[rid]})
    fpath = OUT / "forecasts.jsonl"
    fpath.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    manifest = {"experiment": "EXP-0048", "sealed_utc": now.isoformat(timespec="seconds"), "forecasts": len(rows),
                "episodes": len({r["episode"] for r in rows}), "dropped_for_later_release": dropped,
                "forecasts_file_sha256": hashlib.sha256(fpath.read_bytes()).hexdigest(),
                "items_file_sha256": hashlib.sha256((OUT / "items_ax.jsonl").read_bytes()).hexdigest(),
                "skill_block_sha256_16": e36.considerations()[1],
                "per_forecast": [{"id": r["id"], "episode": r["episode"], "reply_sha256": r["reply_sha256"]} for r in rows]}
    SEALS.mkdir(parents=True, exist_ok=True)
    (SEALS / "exp0048_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "per_forecast"}, indent=2))
    print(f"commit and push {SEALS / 'exp0048_manifest.json'} before {DEADLINE}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare_r").set_defaults(fn=prepare_r)
    b = sub.add_parser("build")
    b.add_argument("--series", required=True, help="quarterly series built from the December company-facts snapshot")
    b.set_defaults(fn=build)
    sub.add_parser("seal").set_defaults(fn=seal)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
