"""EXP-0034: does the comparison base alone predict revenue acceleration? (S2-a, code only)

Pre-registration: research/registry/experiment_registry.md, EXP-0034 (2026-11-22). EXP-0020's
as-filed series and label; three rules: R1 reversal (EXP-0020's best), R2 comparison base
(g(t-3) < g(t-4)), R3 logistic regression on g(t)..g(t-4), five folds grouped by company.

    conda run --no-capture-output -n nlab python research/experiments/exp0034_s2a_base_effect.py run
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0020_s2a_episodes as e20  # noqa: E402
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0034"
SEED = 20261129


def features(by: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for ep in e20.episodes(by):
        if ep["y_accelerates"] is None:
            continue
        back = {e22.quarters_between(r["end"], ep["end"]): r for r in by[ep["cik"]] if r["end"] <= ep["end"]}
        g = [back[k]["g"] if k in back and back[k]["g"] is not None and back[k]["filed"] <= ep["filed"] else None for k in range(5)]
        if None in g:
            continue
        rows.append({"cik": ep["cik"], "end": ep["end"], "y": ep["y_accelerates"], "g": g})
    return rows


def fit(X: np.ndarray, y: np.ndarray, iters: int = 50, ridge: float = 1e-3) -> np.ndarray:
    w = np.zeros(X.shape[1])
    for _ in range(iters):  # Newton steps
        p = 1 / (1 + np.exp(-X @ w))
        H = X.T @ (X * (p * (1 - p))[:, None]) + ridge * np.eye(X.shape[1])
        w -= np.linalg.solve(H, X.T @ (p - y) + ridge * w)
    return w


def design(rows: list[dict]) -> np.ndarray:
    g = np.clip(np.array([r["g"] for r in rows], dtype=float), -1, 2)  # cap a few extreme growth rates
    return np.hstack([np.ones((len(rows), 1)), g])


def run(_: argparse.Namespace) -> None:
    e23.need_drive()
    by = e20.load_series()
    tier = e20.tier_of(by)
    rows = features(by)
    rng = random.Random(SEED)
    ciks = sorted({r["cik"] for r in rows})
    rng.shuffle(ciks)
    fold = {c: i % 5 for i, c in enumerate(ciks)}
    X, y = design(rows), np.array([float(r["y"]) for r in rows])
    p3 = np.zeros(len(rows))
    coefs = []
    for f in range(5):
        tr = np.array([fold[r["cik"]] != f for r in rows])
        w = fit(X[tr], y[tr])
        coefs.append(w.round(3).tolist())
        p3[~tr] = 1 / (1 + np.exp(-X[~tr] @ w))
    for r, p in zip(rows, p3):
        g = r["g"]
        r["r1"] = g[0] < g[1]
        r["r2"] = g[3] < g[4]
        r["r3"] = bool(p > 0.5)

    def acc(sel: list[dict]) -> dict:
        if not sel:
            return {"n": 0}
        out = {"n": len(sel), "base_rate": round(statistics.mean(float(r["y"]) for r in sel), 3)}
        for k in ("r1", "r2", "r3"):
            v = [float(r[k] == r["y"]) for r in sel]
            d = sorted(statistics.mean(rng.choices(v, k=len(v))) for _ in range(2000))
            out[k] = {"acc": round(statistics.mean(v), 3), "ci90": [round(d[99], 3), round(d[1899], 3)]}
        return out

    rep = {"episodes": len(rows), "companies": len(ciks), "coef_folds": coefs,
           "all": acc(rows), "top 250": acc([r for r in rows if tier.get(r["cik"]) in ("top 50", "51 to 250")]),
           "top 50": acc([r for r in rows if tier.get(r["cik"]) == "top 50"])}
    key = e26.load(e26.OUT / "key.jsonl")
    idx = {(r["cik"], r["end"]): r for r in rows}
    p26 = {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / e26.RUN) if r["canary_ok"]}

    def call(reply: str | None) -> bool | None:
        m = e26.PROB.search(reply or "")
        return None if not m or int(m.group(1)) == 50 else int(m.group(1)) > 50

    for g in ("old", "clean"):
        sel, model = [], {"raw": [], "prior": []}
        for k in key:
            if k["group"] != g:
                continue
            r = idx.get((k["cik"], k["quarter_end"]))
            if r is None:
                # the clean quarters' series rows may be filed after the snapshot; rebuild from the key's own numbers
                continue
            sel.append(r)
            for arm, rid in (("raw", f"v{k['episode']:03d}-0"), ("prior", f"n{k['episode']:03d}")):
                c = call(p26.get(rid))
                if c is not None:
                    model[arm].append(float(c == k["accelerates"]))
        rep[f"exp0026_{g}"] = {**acc(sel), "covered": f"{len(sel)} of {sum(1 for k in key if k['group'] == g)}",
                              "model_raw_acc_same": round(statistics.mean(model["raw"]), 3) if model["raw"] else None,
                              "model_prior_acc_same": round(statistics.mean(model["prior"]), 3) if model["prior"] else None}
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
