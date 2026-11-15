"""EXP-0004: census of company split v1 on the EXP-0003 universe.

Applies ``split_v1`` to every company in EXP-0003's targets (earnings 8-Ks from 2026-07-01 to
2026-11-10, plus each company's last release before the cutoff). Counts companies, releases and
pairs per side, using EXP-0003's rule flags only (no outcomes, no labels). It writes the
assignment of every company to the external drive.

An engineering measurement with no hypothesis and no verdict.

    conda run --no-capture-output -n nlab python research/experiments/exp0004_company_split.py
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import split_v1  # noqa: E402

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
PAIRS = DRIVE / "edgar" / "pairs"
OUT = DRIVE / "splits"
SIDES = ("test", "dev", "train")


def main() -> None:
    if not DRIVE.exists():
        sys.exit("external drive not mounted")
    OUT.mkdir(exist_ok=True)
    targets = json.loads((PAIRS / "targets.json").read_text(encoding="utf-8"))
    group_of = split_v1.groups((t["accession"], t["cik"]) for t in targets)
    linked = {c for c, g in group_of.items() if c != g}
    side = {c: split_v1.assign(c, group_of) for c in group_of}

    with open(OUT / "split_v1_exp0003_companies.jsonl", "w", encoding="utf-8") as fh:
        meta = {t["cik"]: t for t in targets}
        for c in sorted(side):
            t = meta[c]
            fh.write(json.dumps({"cik": c, "group": group_of[c], "u": split_v1.u_value(group_of[c]),
                                 "side": side[c], "size_band": t["size_band"], "sic": t["sic"]}) + "\n")

    rep: dict = {"salt": split_v1.SALT, "cut_points": [split_v1.TEST_BELOW, split_v1.DEV_BELOW],
                 "companies_linked_to_a_smaller_cik": len(linked)}
    rep["companies"] = dict(collections.Counter(side.values()))

    bands = collections.defaultdict(collections.Counter)
    for c, s in side.items():
        bands[meta[c]["size_band"]][s] += 1
    rep["companies_by_size_band"] = {b: dict(v) for b, v in sorted(bands.items())}

    # Pairs, as EXP-0003 counts them (its flags already drop co-registrants).
    rows = [json.loads(l) for l in open(PAIRS / "flags_v2.jsonl", encoding="utf-8")]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["cik"]].append(r)
    c = collections.Counter()
    missing = ("unavailable", "no_press_release")
    for cik, rs in by.items():
        s = side[split_v1.cik10(cik)]
        for r in rs:
            if r["post_cutoff"]:
                c[(s, "post-cutoff releases")] += 1
                c[(s, f"post-cutoff releases flagged {r['kind']}")] += 1
        rs.sort(key=lambda r: r["acceptance"])
        for p0, p1 in zip(rs, rs[1:]):
            if not p1["post_cutoff"] or p0["kind"] in missing or p1["kind"] in missing:
                continue
            both = p0["post_cutoff"]
            num = p0["kind"] == "numeric" and p1["kind"] == "numeric"
            c[(s, "pairs, later after cutoff")] += 1
            c[(s, "numeric in both, later after cutoff")] += num
            if both:
                c[(s, "pairs, both after cutoff")] += 1
                c[(s, "numeric in both, both after cutoff")] += num
    keys = sorted({k for _, k in c})
    rep["counts"] = {k: {s: c[(s, k)] for s in SIDES} for k in keys}

    (OUT / "split_v1_exp0003_census.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
