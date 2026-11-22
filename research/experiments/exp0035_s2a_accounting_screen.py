"""EXP-0035: do as-filed accounting items add to the comparison base? (S2-a, code only)

Pre-registration: research/registry/experiment_registry.md, EXP-0035 (2026-11-22). EXP-0034's
episodes and its five-lag logistic (R3) as the base; ten balance-sheet, margin and sector items as
first filed; increments in out-of-fold log loss and accuracy, bootstrapped by company.

    conda run --no-capture-output -n nlab python research/experiments/exp0035_s2a_accounting_screen.py run
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import random
import statistics
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as e5  # noqa: E402
import exp0020_s2a_episodes as e20  # noqa: E402
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0034_s2a_base_effect as e34  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0035"
SEED_BOOT = 20261130
DRAWS = 2000
INSTANT = {  # balance-sheet items; the first concept a company tags wins
    "inventory": ["InventoryNet", "InventoryGross"],
    "receivables": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent", "AccountsAndOtherReceivablesNetCurrent"],
    "contract_liab": ["ContractWithCustomerLiabilityCurrent", "ContractWithCustomerLiability", "DeferredRevenueCurrent", "DeferredRevenue"],
    "rpo": ["RevenueRemainingPerformanceObligation"],
}
DURATION = {  # quarterly flows; a fourth quarter is derived as in EXP-0020
    "gross_profit": ["GrossProfit"],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "sga": ["SellingGeneralAndAdministrativeExpense"],
    "operating_income": ["OperatingIncomeLoss"],
    "pretax": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
               "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
}
FEATURES = ("inv_gap", "ar_gap", "cl_gap", "rpo_gap", "gm_chg", "sga_gap", "om_chg", "nonop_chg", "sec_g0", "rel_g0")


# ---------------------------------------------------------------------------------------------
# As-filed items


def instants(gaap: dict, concepts: list[str]) -> dict[str, tuple[float, str]]:
    """end -> (value, filed) from the first filing that reports a balance at that date."""
    for c in concepts:
        rows = [r for r in gaap.get(c, {}).get("units", {}).get("USD", [])
                if "start" not in r and r.get("form") in e20.FORMS and r["end"] <= r["filed"]]
        if rows:
            out: dict[str, tuple[float, str]] = {}
            for r in sorted(rows, key=lambda r: r["filed"]):
                out.setdefault(r["end"], (r["val"], r["filed"]))
            return out
    return {}


def at(table: dict[str, tuple[float, str]], end: str, filed_by: str, back: int = 0) -> float | None:
    for e, (v, f) in table.items():
        if abs(e5.days(e, end) - back) <= (12 if back else 5) and f <= filed_by:
            return v
    return None


def flows(gaap: dict, concepts: list[str]) -> tuple[dict, list]:
    per: dict[str, dict[str, list[dict]]] = {}
    every: list[dict] = []
    for c in concepts:
        for r in gaap.get(c, {}).get("units", {}).get("USD", []):
            if "start" not in r or r.get("form") not in e20.FORMS or r["end"] > r["filed"]:
                continue
            per.setdefault(r["accn"], {}).setdefault(c, []).append(r)
            every.append(r)
    return {a: next(cs[c] for c in concepts if c in cs) for a, cs in per.items()}, every


def items(gaap: dict, recs: list[dict]) -> dict[str, dict]:
    ins = {k: instants(gaap, cs) for k, cs in INSTANT.items()}
    fl = {k: flows(gaap, cs) for k, cs in DURATION.items()}
    out = {}
    for r in recs:
        x = {}
        for k, t in ins.items():
            x[k], x[k + "_ya"] = at(t, r["end"], r["filed"]), at(t, r["end"], r["filed"], back=365)
        for k, (rows, every) in fl.items():
            q = e20.quarter_of(rows[r["accn"]], every, r["form"]) if r["accn"] in rows else None
            ok = q is not None and abs(e5.days(q["end"], r["end"])) <= 5
            x[k], x[k + "_ya"] = (q["cur"], q["prior"]) if ok else (None, None)
        out[r["end"]] = x
    return out


def pct(a, b):
    return a / b - 1 if a is not None and b is not None and b > 0 and a >= 0 else None


def gap(a, b, g):
    p = pct(a, b)
    return None if p is None or g is None else max(-1.0, min(1.0, p - g))


def ratio(num, rev):
    return None if num is None or not rev or rev <= 0 else num / rev


def change(a, b):
    return None if a is None or b is None else max(-0.5, min(0.5, a - b))


def accounting(x: dict, rec: dict) -> dict:
    g, rev, rev_ya = rec["g"], rec["rev"], rec["rev_prior"]

    def gp(cur: bool):
        s = "" if cur else "_ya"
        r = rev if cur else rev_ya
        if x["gross_profit" + s] is not None:
            return x["gross_profit" + s]
        return r - x["cost_of_revenue" + s] if x["cost_of_revenue" + s] is not None and r else None

    def nonop(cur: bool):
        s = "" if cur else "_ya"
        p, o = x["pretax" + s], x["operating_income" + s]
        return None if p is None or o is None else p - o

    return {
        "inv_gap": gap(x["inventory"], x["inventory_ya"], g),
        "ar_gap": gap(x["receivables"], x["receivables_ya"], g),
        "cl_gap": gap(x["contract_liab"], x["contract_liab_ya"], g),
        "rpo_gap": gap(x["rpo"], x["rpo_ya"], g),
        "gm_chg": change(ratio(gp(True), rev), ratio(gp(False), rev_ya)),
        "sga_gap": gap(x["sga"], x["sga_ya"], g),
        "om_chg": change(ratio(x["operating_income"], rev), ratio(x["operating_income_ya"], rev_ya)),
        "nonop_chg": change(ratio(nonop(True), rev), ratio(nonop(False), rev_ya)),
    }


def calendar_quarter(end: str) -> str:
    d = dt.date.fromisoformat(end) - dt.timedelta(days=10)  # 52/53-week years end a few days into the next month
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


# ---------------------------------------------------------------------------------------------
# Episodes


def episodes(by: dict[str, list[dict]]) -> list[dict]:
    """EXP-0034's episodes, with the earnings-side labels kept."""
    rows = []
    for ep in e20.episodes(by):
        if ep["y_accelerates"] is None:
            continue
        back = {e22.quarters_between(r["end"], ep["end"]): r for r in by[ep["cik"]] if r["end"] <= ep["end"]}
        g = [back[k]["g"] if k in back and back[k]["g"] is not None and back[k]["filed"] <= ep["filed"] else None for k in range(5)]
        if None in g:
            continue
        rows.append({"cik": ep["cik"], "end": ep["end"], "filed": ep["filed"], "y": ep["y_accelerates"], "g": g,
                     "y_margin_up": ep["y_margin_up"], "y_income_up": ep["y_income_up"],
                     "x_margin_up": ep["x_margin_up"], "x_income_up": ep["x_income_up"]})
    return rows


def build() -> list[dict]:
    by = e20.load_series()
    tier = e20.tier_of(by)
    sic = {}
    for line in open(e20.SPLIT, encoding="utf-8"):
        r = json.loads(line)
        sic[r["cik"]] = (r.get("sic") or "")[:2]
    rows = episodes(by)
    assert len(rows) == 22373, len(rows)  # EXP-0034's count
    zf = zipfile.ZipFile(e20.FACTS_ZIP)
    want = collections.defaultdict(set)
    for r in rows:
        want[r["cik"]].add(r["end"])
    feats: dict[tuple[str, str], dict] = {}
    for n, (cik, ends) in enumerate(sorted(want.items())):
        gaap = json.loads(zf.read(f"CIK{cik}.json")).get("facts", {}).get("us-gaap", {})
        recs = [r for r in by[cik] if r["end"] in ends]
        xs = items(gaap, recs)
        for r in recs:
            feats[(cik, r["end"])] = accounting(xs[r["end"]], r)
        if n % 200 == 0:
            print(f"[build] {n}/{len(want)} companies", flush=True)
    peers = collections.defaultdict(list)  # (sic2, calendar quarter) -> [(filed, cik, g)]
    for cik, recs in by.items():
        if sic.get(cik):
            for r in recs:
                if r["g"] is not None:
                    peers[(sic[cik], calendar_quarter(r["end"]))].append((r["filed"], cik, r["g"]))
    for r in rows:
        r.update(feats[(r["cik"], r["end"])])
        r["tier"] = tier.get(r["cik"], "the rest")
        ps = [g for f, c, g in peers.get((sic.get(r["cik"], ""), calendar_quarter(r["end"])), [])
              if c != r["cik"] and f <= r["filed"]] if sic.get(r["cik"]) else []
        r["sec_g0"] = max(-1.0, min(2.0, statistics.median(ps))) if len(ps) >= 5 else None
        r["rel_g0"] = None if r["sec_g0"] is None else max(-1.0, min(1.0, r["g"][0] - r["sec_g0"]))
    return rows


# ---------------------------------------------------------------------------------------------
# Scoring


def oof(X: np.ndarray, y: np.ndarray, folds: np.ndarray) -> np.ndarray:
    p = np.zeros(len(y))
    for f in range(5):
        tr = folds != f
        w = e34.fit(X[tr], y[tr])
        p[~tr] = 1 / (1 + np.exp(-X[~tr] @ w))
    return np.clip(p, 1e-6, 1 - 1e-6)


def losses(p: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return -(y * np.log(p) + (1 - y) * np.log(1 - p)), ((p > 0.5) == (y > 0.5)).astype(float)


def boot(d: np.ndarray, ciks: list[str], rng: random.Random) -> dict:
    by = collections.defaultdict(list)
    for v, c in zip(d, ciks):
        by[c].append(v)
    groups = [np.array(v) for v in by.values()]
    est = float(np.mean(d))
    draws = []
    for _ in range(DRAWS):
        pick = [groups[rng.randrange(len(groups))] for _ in groups]
        draws.append(float(np.concatenate(pick).mean()))
    draws.sort()
    p = 2 * min(sum(x <= 0 for x in draws), sum(x >= 0 for x in draws)) / DRAWS
    return {"est": round(est, 5), "ci90": [round(draws[int(0.05 * DRAWS)], 5), round(draws[int(0.95 * DRAWS) - 1], 5)], "p": round(min(1.0, p), 4)}


def base_design(rows: list[dict], label: str) -> np.ndarray:
    g = np.clip(np.array([r["g"] for r in rows], dtype=float), -1, 2)
    cols = [np.ones((len(rows), 1)), g]
    if label != "y":  # earnings-side labels: own persistence and the operating margin change
        x = "x_margin_up" if label == "y_margin_up" else "x_income_up"
        cols.append(np.array([[float(r[x])] for r in rows]))
        cols.append(np.array([[r["om_chg"]] for r in rows], dtype=float))
    return np.hstack(cols)


def screen(rows: list[dict], label: str, fold: dict[str, int], rng: random.Random) -> dict:
    if label != "y":
        x = "x_margin_up" if label == "y_margin_up" else "x_income_up"
        rows = [r for r in rows if r[label] is not None and r[x] is not None and r["om_chg"] is not None]
    y_all = np.array([float(r[label]) for r in rows])
    out: dict = {"episodes": len(rows), "base_rate": round(float(y_all.mean()), 4)}
    for name in FEATURES:
        if label != "y" and name == "om_chg":
            continue
        sub = [r for r in rows if r[name] is not None]
        if len(sub) < 500:
            out[name] = {"n": len(sub)}
            continue
        y = np.array([float(r[label]) for r in sub])
        folds = np.array([fold[r["cik"]] for r in sub])
        Xb = base_design(sub, label)
        Xf = np.hstack([Xb, np.array([[r[name]] for r in sub], dtype=float)])
        lb, ab = losses(oof(Xb, y, folds), y)
        lf, af = losses(oof(Xf, y, folds), y)
        res = {"n": len(sub), "companies": len({r["cik"] for r in sub}), "acc_base": round(float(ab.mean()), 4), "acc_with": round(float(af.mean()), 4)}
        for scope, keep in (("all", lambda r: True), ("top 250", lambda r: r["tier"] != "the rest")):
            idx = [i for i, r in enumerate(sub) if keep(r)]
            if len(idx) < 200:
                continue
            ck = [sub[i]["cik"] for i in idx]
            res[scope] = {"n": len(idx), "logloss_gain": boot(lb[idx] - lf[idx], ck, rng), "acc_gain": boot(af[idx] - ab[idx], ck, rng)}
        w = e34.fit(Xf, y)
        res["coef_full_sample"] = round(float(w[-1]), 4)
        out[name] = res
    # combined: all features, missing -> 0 with an indicator
    folds = np.array([fold[r["cik"]] for r in rows])
    Xb = base_design(rows, label)
    extra = []
    for name in FEATURES:
        if label != "y" and name == "om_chg":
            continue
        v = [r[name] for r in rows]
        extra.append(np.array([[0.0 if x is None else x, float(x is None)] for x in v]))
    Xc = np.hstack([Xb] + extra)
    lb, ab = losses(oof(Xb, y_all, folds), y_all)
    lc, ac = losses(oof(Xc, y_all, folds), y_all)
    comb = {}
    for scope, keep in (("all", lambda r: True), ("top 250", lambda r: r["tier"] != "the rest")):
        idx = [i for i, r in enumerate(rows) if keep(r)]
        ck = [rows[i]["cik"] for i in idx]
        comb[scope] = {"n": len(idx), "acc_base": round(float(ab[idx].mean()), 4), "acc_with": round(float(ac[idx].mean()), 4),
                       "logloss_gain": boot(lb[idx] - lc[idx], ck, rng), "acc_gain": boot(ac[idx] - ab[idx], ck, rng)}
    out["combined"] = comb
    return out


def bh(ps: dict[str, float], q: float = 0.10) -> set[str]:
    order = sorted(ps, key=ps.get)
    m, keep = len(order), 0
    for k, name in enumerate(order, 1):
        if ps[name] <= q * k / m:
            keep = k
    return set(order[:keep])


def run(_: argparse.Namespace) -> None:
    e23.need_drive()
    rows = build()
    rng = random.Random(e34.SEED)
    ciks = sorted({r["cik"] for r in rows})
    rng.shuffle(ciks)
    fold = {c: i % 5 for i, c in enumerate(ciks)}  # EXP-0034's folds
    brng = random.Random(SEED_BOOT)
    cover = {name: {"all": round(sum(r[name] is not None for r in rows) / len(rows), 3),
                    "top 250": round(sum(r[name] is not None for r in rows if r["tier"] != "the rest") / sum(r["tier"] != "the rest" for r in rows), 3)}
             for name in FEATURES}
    rep: dict = {"episodes": len(rows), "coverage": cover}
    rep["revenue_acceleration"] = screen(rows, "y", fold, brng)
    rev = rep["revenue_acceleration"]
    ps = {n: rev[n]["all"]["logloss_gain"]["p"] for n in FEATURES if "all" in rev.get(n, {})}
    passed = bh(ps)
    rep["criterion_1"] = {n: ("adds" if n in passed and rev[n]["all"]["acc_gain"]["est"] >= 0 else "nothing found") for n in ps}
    c = rev["combined"]["top 250"]["acc_gain"]
    rep["criterion_2"] = ("worth stating in the brief" if c["est"] >= 0.01 and c["ci90"][0] > 0
                          else "no material gain" if c["ci90"][1] < 0.01 else "undecided")
    rep["exploratory_operating_margin_up"] = screen(rows, "y_margin_up", fold, brng)
    rep["exploratory_net_income_up"] = screen(rows, "y_income_up", fold, brng)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run").set_defaults(fn=run)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
