"""EXP-0050: S1 reasoning exam, step R-b. Headroom on development section R items.

Pre-registered in research/registry/experiment_registry.md. Design:
``research/design/s1_reasoning_exam.md`` (§6, step R-b). Nothing is trained. Five arms answer the
same development items of section R v0 (EXP-0019), in three conditions:

* plain: base items, no hint;
* hint: base items with the template's one-line hint after the question (not R1.9, which has none);
* twin: every flip, hold and mirror twin of the drawn base items, no hint.

Arms (thinking off, greedy, at most 512 generated tokens, inserted calculator values free, then
EXP-0007's forced answer if no box was written):

* 4B  Qwen3.5-4B, no tool, standard instruction;
* 4I  Qwen3.5-4B with EXP-0018's calculator (inline rule only), standard instruction;
* B0  Qwen3.5-0.8B as released, no tool, standard instruction;
* C   EXP-0014's D3-s1 with the calculator (inline rule only), terse instruction;
* K2  EXP-0017's K2-s1 with the calculator (inline rule only), terse instruction.

The only change to the instructions: "final number" becomes "final answer", because most R items
want a label. Grading is by rule (``grade_r``): a label must equal one option after normalisation or
contain exactly one; "cannot be determined" is read wherever it appears in the box; numbers use
EXP-0010's ``read_number`` and the item's tolerance.

  check   grader cases, the two instructions and one assembled development prompt (no model)
  draw    the development draw (counts and hashes)
  run     one arm, all three conditions, resumable
  queue   every arm in the registered order, then score
  score   the registered criteria and the descriptive slices, to scores.json

Every item here is a development item; Claude may read them and the responses.

    conda run --no-capture-output -n py313 python research/experiments/exp0050_s1r_headroom.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0050_s1r_headroom.py draw
    conda run --no-capture-output -n py313 python research/experiments/exp0050_s1r_headroom.py queue
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0018_s1c_calculator_inline as I  # noqa: E402  (importing it sets the calculator to the inline rule)

C, E, S, V = I.C, I.E, I.S, I.V
NL = S.DRIVE / "narrative_lab" / "s1"
ITEMS = NL / "exam_r_v0" / "items_dev.jsonl"
OUT = NL / "exp0050"
DRAW, TWINS = OUT / "draw.jsonl", OUT / "twins.jsonl"
TEMPLATES = [f"R1.{k}" for k in range(1, 10)]
Q, PER_COMPANY = 50, 2
CAP = 512
BOOT, BOOT_SEED = 10_000, 20261124
ARMS = ["B0", "C", "K2", "4B", "4I"]
CONDS = ["plain", "hint", "twin"]
TWIN_ORDER = {"flip": 0, "hold": 1, "mirror": 2}
STD_R = E.STANDARD.replace("final number", "final answer")
TERSE_R = E.TERSE.replace("final number", "final answer")
CBD = "cannot be determined"
B_DEV = {  # each arm's responses on the 600 B development items (EXP-0007's draw, v0.2), already on disk
    "4B": NL / "exp0011" / "responses" / "qwen3.5-4b-off.jsonl",
    "4I": NL / "exp0016" / "dev_v1" / "4C.jsonl",  # made before the chained rule existed: inline rule only
    "B0": NL / "exp0011" / "responses" / "qwen3.5-0.8b-off.jsonl",
    "C": NL / "exp0016" / "dev_v1" / "C-s1.jsonl",
    "K2": NL / "exp0017" / "dev" / "K2-s1-e2.jsonl",
}
GATE_PAIR = ("4I", "K2")
SIZE_PAIRS = [("4I", "K2"), ("4I", "C")]


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def jl(path: Path) -> list[dict]:
    return E.jl(path) if path.exists() else []


# ------------------------------------------------------------------ arms and prompts


def arm(name: str):
    """(model key, weights, instruction, calculator)"""
    if name in ("4B", "4I"):
        return E.TEACHER, None, STD_R, name == "4I"
    if name == "B0":
        return E.STUDENT, None, STD_R, False
    if name == "C":
        return E.STUDENT, Path(json.loads((E.OUT / "dev" / "chosen.json").read_text())["D3-s1"]), TERSE_R, True
    if name == "K2":
        return E.STUDENT, Path(json.loads((NL / "exp0017" / "dev" / "chosen.json").read_text())["K2-s1"]), TERSE_R, True
    raise KeyError(name)


def shown(item: dict, cond: str) -> dict:
    it = dict(item)
    if cond == "hint":
        it["question"] = f"{item['question']} Hint: {item['hint']}"
    return it


# ------------------------------------------------------------------ grading


def norm(s: str) -> str:
    for _ in range(3):
        s = re.sub(r"\\(?:text|mathrm|textbf)\{([^{}]*)\}", r"\1", s)
    s = s.replace("\\&", "&").replace("\\,", " ").replace("\\%", "%").lower()
    s = re.sub(r"[^a-z0-9&%.\- ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip(" .")


def read_label(box: str, options: list[str]) -> str | None:
    b = norm(box)
    if CBD in b:
        return CBD
    opts = {norm(o): o for o in options}
    if b in opts:
        return opts[b]
    hits = [o for n, o in opts.items() if re.search(rf"(?<![a-z]){re.escape(n)}(?![a-z])", b)]
    return hits[0] if len(hits) == 1 else None


def grade_r(item: dict, response: str) -> dict:
    from learnai.finbench import last_boxed

    box = last_boxed(response)
    if box is None:
        return {"boxed": None, "answer": None, "valid": False, "correct": False}
    if item["kind"] == "label":
        a = read_label(box, item["options"])
        ok = a == item["gold"]
    elif item["kind"] == "undetermined":
        a = CBD if CBD in norm(box) else norm(box)
        ok = a == CBD
    else:
        if CBD in norm(box):
            a, ok = CBD, False
        else:
            a = V.read_number(box)
            ok = a is not None and abs(a - float(item["gold"])) <= item["tolerance"]["abs"]
    return {"boxed": box, "answer": a, "valid": a is not None, "correct": bool(ok)}


def same_answer(item: dict, a, b) -> bool:
    if a is None or b is None:
        return False
    if item["kind"] == "number" and isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= item["tolerance"]["abs"]
    return a == b


def figures(item: dict) -> list[float]:
    """The figures an item's step chain uses, as the excerpt shows them."""
    st = item.get("steps") or {}
    if item["template"] == "R1.9":
        return []
    if item["template"] == "R1.7":
        return [st["ytd_shown"], st["quarter_shown"]]
    out = []
    for f in st.get("figures", []):
        out += [f["current"], f["prior"]]
    return out


def found(fig: float, nums: list[float]) -> bool:
    """A figure counts as written if a number in the response equals it, or it divided or multiplied by 1,000."""
    for n in nums:
        for v in (fig, fig / 1000, fig * 1000):
            if abs(abs(n) - abs(v)) <= max(0.0051, 1e-4 * abs(v)):
                return True
    return False


# ------------------------------------------------------------------ check


GRADE_CASES = [  # (kind, options, gold, tolerance, response, expected answer, expected correct)
    ("label", ["expanded", "contracted", "flat"], "expanded", None, "so \\boxed{expanded}", "expanded", True),
    ("label", ["expanded", "contracted", "flat"], "contracted", None, "\\boxed{\\text{Contracted}}", "contracted", True),
    ("label", ["both rose", "both fell", "revenue rose and operating income fell", "revenue fell and operating income rose"],
     "both rose", None, "\\boxed{Both rose.}", "both rose", True),
    ("label", ["both rose", "both fell", "revenue rose and operating income fell", "revenue fell and operating income rose"],
     "revenue rose and operating income fell", None, "\\boxed{\\text{Revenue rose and operating income fell}}",
     "revenue rose and operating income fell", True),
    ("label", ["faster", "slower"], "faster", None, "\\boxed{faster or slower}", None, False),
    ("label", ["faster", "slower"], "slower", None, "\\boxed{Slower}", "slower", True),
    ("label", ["faster", "slower"], "slower", None, "\\boxed{\\text{cannot be determined}}", CBD, False),
    ("label", ["cost of revenue", "gross profit", "selling, general and administrative expense"],
     "selling, general and administrative expense", None, "\\boxed{Selling, General and Administrative Expense}",
     "selling, general and administrative expense", True),
    ("label", ["cost of revenue", "gross profit", "selling, general and administrative expense"],
     "selling, general and administrative expense", None, "\\boxed{SG\\&A}", None, False),
    ("undetermined", None, CBD, None, "\\boxed{\\text{Cannot be determined}}", CBD, True),
    ("undetermined", None, CBD, None, "\\boxed{1,234}", "1 234", False),
    ("number", None, -3488.0, {"abs": 1.01}, "\\boxed{-3,488}", -3488.0, True),
    ("number", None, 6.2869, {"abs": 0.15}, "\\boxed{6.29\\%}", 6.29, True),
    ("number", None, 6.2869, {"abs": 0.15}, "\\boxed{cannot be determined}", CBD, False),
    ("number", None, 6.2869, {"abs": 0.15}, "no box", None, False),
]


def check(_: argparse.Namespace) -> None:
    bad = 0
    for kind, opts, gold, tol, resp, want_a, want_ok in GRADE_CASES:
        g = grade_r({"kind": kind, "options": opts, "gold": gold, "tolerance": tol}, resp)
        ok = g["answer"] == want_a and g["correct"] == want_ok
        bad += not ok
        print("ok " if ok else "BAD", repr(resp), "->", g["answer"], g["correct"])
    print(f"{len(GRADE_CASES) - bad} of {len(GRADE_CASES)} grader cases pass")
    fig_cases = [(508.8, [508.8], True), (1176350.0, [1176.35], True), (0.63, [0.63, 0.65], True),
                 (379.8, [380.0], False), (2530.0, [2.53], True), (4290.0, [429.0], False)]
    for fig, nums, want in fig_cases:
        got = found(fig, nums)
        bad += got != want
        print("ok " if got == want else "BAD", "figure", fig, nums, "->", got)
    print("standard:", STD_R)
    print("terse:   ", TERSE_R)
    assert STD_R != E.STANDARD and TERSE_R != E.TERSE
    I.check(argparse.Namespace())  # the inline rule's parser cases
    if S.DRIVE.is_dir() and DRAW.exists():
        from transformers import AutoTokenizer  # tokenizer only, no weights

        tok = AutoTokenizer.from_pretrained(str(S.model_path(E.TEACHER)))
        it = next(i for i in items_by_id().values() if i["id"] == E.jl(DRAW)[0]["id"])
        print("---- one development prompt, hint condition ----")
        print(E.prompt_for(tok, shown(it, "hint"), STD_R)[-900:])
    if bad:
        sys.exit(1)


# ------------------------------------------------------------------ draw


def items_by_id() -> dict[str, dict]:
    with open(ITEMS, encoding="utf-8") as fh:
        return {r["id"]: r for r in map(json.loads, fh)}


def stratum(it: dict) -> str:
    return it["gold"] if it["kind"] == "label" else it["variant"]


def draw(_: argparse.Namespace) -> None:
    S.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    allit = list(items_by_id().values())
    base = [i for i in allit if not i.get("twin_of") and i["post_cutoff"]]
    picked, report = [], {}
    for t in TEMPLATES:
        pool = collections.defaultdict(list)
        for i in sorted((i for i in base if i["template"] == t), key=lambda i: sha("exp0050:" + i["id"])):
            pool[stratum(i)].append(i)
        keys = sorted(pool)
        per_co, rel, got = collections.Counter(), set(), []
        while len(got) < Q and any(pool[k] for k in keys):
            for k in keys:
                while pool[k]:
                    i = pool[k].pop(0)
                    if per_co[i["cik"]] < PER_COMPANY and i["accession"] not in rel:
                        got.append(i)
                        per_co[i["cik"]] += 1
                        rel.add(i["accession"])
                        break
                if len(got) >= Q:
                    break
        picked += got
        report[t] = {"items": len(got), "companies": len(per_co),
                     "strata": dict(sorted(collections.Counter(stratum(i) for i in got).items()))}
    ids = [i["id"] for i in picked]
    pos = {k: n for n, k in enumerate(ids)}
    twins = sorted((i for i in allit if i.get("twin_of") in pos), key=lambda i: (pos[i["twin_of"]], TWIN_ORDER[i["twin"]]))
    with open(DRAW, "w") as fh:
        for i in picked:
            fh.write(json.dumps({"id": i["id"], "template": i["template"], "stratum": stratum(i), "cik": i["cik"]}) + "\n")
    with open(TWINS, "w") as fh:
        for i in twins:
            fh.write(json.dumps({"id": i["id"], "twin_of": i["twin_of"], "twin": i["twin"], "template": i["template"]}) + "\n")
    report["total"] = {"base": len(ids), "companies": len({i["cik"] for i in picked}),
                       "hint": sum(i["template"] != "R1.9" for i in picked),
                       "twins": dict(collections.Counter(i["twin"] for i in twins)),
                       "sha256_base_ids": sha("".join(ids)), "sha256_twin_ids": sha("".join(i["id"] for i in twins))}
    (OUT / "draw.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


def sets() -> dict[str, list[dict]]:
    by = items_by_id()
    base = [by[r["id"]] for r in E.jl(DRAW)]
    return {"plain": base, "hint": [i for i in base if i["hint"]],
            "twin": [by[r["id"]] for r in E.jl(TWINS)]}


# ------------------------------------------------------------------ run


def run(a: argparse.Namespace) -> None:
    import mlx.core as mx

    S.need_drive()
    key, w, ins, calc = arm(a.arm)
    model = tok = None
    for cond, items in sets().items():
        path = OUT / "runs" / a.arm / f"{cond}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        done = {r["id"] for r in jl(path)}
        todo = [i for i in items if i["id"] not in done]
        if not todo:
            continue
        if model is None:
            model, tok = E.load_model(key, w)
        for it in todo:
            row = C.answer(model, tok, shown(it, cond), ins, CAP, calc)
            row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
            E.append(path, row)


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%H:%M:%S"), *args, flush=True)
        if subprocess.run(me + list(args)).returncode != 0:
            sys.exit(f"step failed: {args}")

    for name in ARMS:
        step("run", "--arm", name)
    step("score")


# ------------------------------------------------------------------ score


class Boot:
    """Company-cluster bootstrap weights shared by every arm, so differences are paired."""

    def __init__(self, ciks: list[str]):
        import numpy as np

        self.np = np
        self.comp = sorted(set(ciks))
        self.idx = {c: k for k, c in enumerate(self.comp)}
        rng = np.random.default_rng(BOOT_SEED)
        n = len(self.comp)
        self.W = rng.multinomial(n, [1 / n] * n, size=BOOT).astype(float)

    def weights(self, ciks: list[str]):
        return self.W[:, [self.idx[c] for c in ciks]]


def macro(items: list[dict], correct, W=None):
    """Mean over templates of the template score: balanced accuracy for labels, accuracy otherwise.

    ``correct`` is a vector over ``items``; ``W`` a (resamples x items) weight matrix, or None for the
    point estimate. Returns a scalar or a vector over resamples, in percent."""
    import numpy as np

    correct = np.asarray(correct, float)
    W = np.ones((1, len(items))) if W is None else W
    groups = {}
    for k, it in enumerate(items):
        g = (it["template"], it["gold"] if it["kind"] == "label" else "")
        groups.setdefault(g, []).append(k)
    by_t = collections.defaultdict(list)
    with np.errstate(invalid="ignore", divide="ignore"):
        for (t, _), ks in groups.items():
            w = W[:, ks]
            by_t[t].append((w * correct[ks]).sum(1) / w.sum(1))
        per_t = [np.nanmean(np.vstack(v), 0) for v in by_t.values()]
        out = 100 * np.nanmean(np.vstack(per_t), 0)
    return float(out[0]) if out.shape[0] == 1 and W.shape[0] == 1 else out


def ci(v) -> list[float]:
    import numpy as np

    return [round(float(np.nanpercentile(v, 2.5)), 1), round(float(np.nanpercentile(v, 97.5)), 1)]


def load_runs() -> dict:
    """{arm: {cond: {id: row with grade}}}"""
    by = items_by_id()
    out = {}
    for a in ARMS:
        out[a] = {}
        for cond in CONDS:
            rows = {}
            for r in jl(OUT / "runs" / a / f"{cond}.jsonl"):
                r.update(grade_r(by[r["id"]], r["response"]))
                rows[r["id"]] = r
            out[a][cond] = rows
    return out


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from scipy.stats import norm as N

    S.need_drive()
    st = sets()
    R = load_runs()
    for a in ARMS:
        for cond, items in st.items():
            if len(R[a][cond]) != len(items):
                sys.exit(f"{a} {cond}: {len(R[a][cond])} of {len(items)} responses")
    base, hint_items, twins = st["plain"], st["hint"], st["twin"]
    by = {i["id"]: i for i in base}
    res: dict = {"n": {"base": len(base), "hint": len(hint_items), "twin": len(twins),
                       "companies": len({i["cik"] for i in base})}}

    # B development items, for the gap comparison
    bitems = E.load_ids(E.DEV_DRAW, V.OUT / "items_dev.jsonl")
    bcorr = {}
    for a, p in B_DEV.items():
        rows = {r["id"]: r for r in E.jl(p)}
        bcorr[a] = np.array([V.grade(i, rows[i["id"]]["response"], "off")["correct"] for i in bitems], float)

    boot = Boot([i["cik"] for i in base + twins] + [i["cik"] for i in bitems])
    Wb = boot.weights([i["cik"] for i in base])
    Wh = boot.weights([i["cik"] for i in hint_items])
    WB = boot.weights([i["cik"] for i in bitems])

    def corr(a, cond, items):
        return np.array([R[a][cond][i["id"]]["correct"] for i in items], float)

    # 1. scores per arm, plain and hint, with intervals
    tab = {}
    for a in ARMS:
        cp, ch, chp = corr(a, "plain", base), corr(a, "hint", hint_items), corr(a, "plain", hint_items)
        tab[a] = {"plain": round(macro(base, cp), 1), "plain_ci": ci(macro(base, cp, Wb)),
                  "plain_raw_acc": round(100 * cp.mean(), 1),
                  "hint_8": round(macro(hint_items, ch), 1), "plain_8": round(macro(hint_items, chp), 1),
                  "hint_gain": round(macro(hint_items, ch) - macro(hint_items, chp), 1),
                  "hint_gain_ci": ci(macro(hint_items, ch, Wh) - macro(hint_items, chp, Wh)),
                  "B_dev_acc": round(100 * bcorr[a].mean(), 1)}
    res["scores"] = tab

    # 2. per template, plain and hint, and baselines
    per_t = {}
    for t in TEMPLATES:
        its = [i for i in base if i["template"] == t]
        row = {"n": len(its), "companies": len({i["cik"] for i in its})}
        if its[0]["kind"] == "label":
            labs = collections.Counter(i["gold"] for i in its)
            row["labels"] = dict(labs)
            row["chance_balanced"] = round(100 / len(its[0]["options"]), 1)
            row["majority_raw_acc"] = round(100 * max(labs.values()) / len(its), 1)
        for a in ARMS:
            row[a] = {"plain": round(macro(its, corr(a, "plain", its)), 1)}
            if its[0]["hint"]:
                row[a]["hint"] = round(macro(its, corr(a, "hint", its)), 1)
        per_t[t] = row
    res["per_template"] = per_t

    # 3. criterion 1, the R-d gate; criterion 4's comparison with B
    hi, lo = GATE_PAIR
    d_R = macro(base, corr(hi, "plain", base), Wb) - macro(base, corr(lo, "plain", base), Wb)
    gap = tab[hi]["plain"] - tab[lo]["plain"]
    res["gate"] = {"pair": f"{hi} - {lo}", "gap": round(gap, 1), "ci95": ci(d_R),
                   "passes": bool(gap >= 5.0 and ci(d_R)[0] > 0)}
    comp = {}
    for x, y in [("4I", "K2"), ("4I", "C"), ("4B", "B0")]:
        dR = macro(base, corr(x, "plain", base), Wb) - macro(base, corr(y, "plain", base), Wb)
        dB = 100 * ((WB * (bcorr[x] - bcorr[y])).sum(1) / WB.sum(1))
        gR = tab[x]["plain"] - tab[y]["plain"]
        gB = 100 * (bcorr[x] - bcorr[y]).mean()
        gR_raw = 100 * (corr(x, "plain", base) - corr(y, "plain", base)).mean()
        comp[f"{x} - {y}"] = {"R": round(gR, 1), "R_ci": ci(dR), "R_raw_acc": round(gR_raw, 1),
                              "B": round(gB, 1), "B_ci": ci(dB),
                              "R_minus_B": round(gR - gB, 1), "R_minus_B_ci": ci(dR - dB)}
    res["R_against_B"] = comp

    # 2. criterion 2, item validity flags
    flags = {}
    for t in TEMPLATES:
        its = [i for i in base if i["template"] == t]
        best4 = max(per_t[t]["4B"]["plain"], per_t[t]["4I"]["plain"])
        all_wrong = [i["id"] for i in its if not any(R[a]["plain"][i["id"]]["correct"] for a in ARMS)]
        flags[t] = {"best_4B": best4, "all_arms_wrong": len(all_wrong),
                    "share_all_wrong": round(100 * len(all_wrong) / len(its), 1),
                    "flagged": bool(best4 < 60 or len(all_wrong) > 0.2 * len(its)), "ids_all_wrong": all_wrong}
    res["validity"] = flags

    # 3. criterion 3, ceiling and floor (plan §3 rule 7)
    res["ceiling_floor"] = {a: {t: ("ceiling" if per_t[t][a]["plain"] > 95 else "floor" if per_t[t][a]["plain"] < 20 else "")
                                for t in TEMPLATES} for a in ARMS}

    # 4. criterion 5, R-c size
    z = N.ppf(1 - 0.0125 / 2) + N.ppf(0.80)
    size = {}
    for x, y in SIZE_PAIRS:
        diff = corr(x, "plain", base) - corr(y, "plain", base)
        d = float((diff != 0).mean())
        var_iid = diff.var(ddof=1) / len(diff)
        var_boot = float(np.var((Wb * diff).sum(1) / Wb.sum(1)))
        de = var_boot / var_iid if var_iid > 0 else float("nan")
        size[f"{x} - {y}"] = {"d": round(d, 3), "DE": round(de, 2), "n": int(np.ceil(de * z * z * d / 0.03 ** 2))}
    res["rc_size"] = size

    # 5. twins, descriptive
    tw = {}
    for a in ARMS:
        rows = collections.defaultdict(lambda: collections.Counter())
        for t_it in twins:
            b_it = by[t_it["twin_of"]]
            rb, rt = R[a]["plain"][b_it["id"]], R[a]["twin"][t_it["id"]]
            k = t_it["twin"]
            c = rows[k]
            c["n"] += 1
            c["base_correct"] += rb["correct"]
            c["twin_correct"] += rt["correct"]
            if k == "flip" and rb["correct"]:
                c["follows_given_base_right"] += rt["correct"]
            if k == "hold":
                c["same_answer"] += same_answer(b_it, rb["answer"], rt["answer"])
            if k == "mirror":
                c["contradiction"] += bool(rb["answer"] in b_it["options"] and rb["answer"] == rt["answer"])
        out = {}
        for k, c in rows.items():
            o = {"n": c["n"], "base_acc": round(100 * c["base_correct"] / c["n"], 1),
                 "twin_acc": round(100 * c["twin_correct"] / c["n"], 1)}
            if k == "flip":
                o["follows_given_base_right"] = round(100 * c["follows_given_base_right"] / max(1, c["base_correct"]), 1)
            if k == "hold":
                o["stability"] = round(100 * c["same_answer"] / c["n"], 1)
            if k == "mirror":
                o["contradiction_rate"] = round(100 * c["contradiction"] / c["n"], 1)
            out[k] = o
        tw[a] = out
    res["twins"] = tw

    # 6. step accuracy, descriptive (base items, plain)
    stp = {}
    for a in ARMS:
        n_fig = n_found = right_missing = right = 0
        for i in base:
            figs = figures(i)
            if not figs:
                continue
            r = R[a]["plain"][i["id"]]
            nums = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", r["response"])]
            f = sum(found(x, nums) for x in figs)
            n_fig, n_found = n_fig + len(figs), n_found + f
            if r["correct"]:
                right += 1
                right_missing += f < len(figs)
        stp[a] = {"figures_written": round(100 * n_found / n_fig, 1), "right_answers": right,
                  "right_with_figures_missing": right_missing}
    res["steps"] = stp

    # 7. operations, descriptive
    ops = {}
    for a in ARMS:
        rows = [r for cond in CONDS for r in R[a][cond].values()]
        gt = sorted(r["generated_tokens"] for r in rows)
        ops[a] = {"responses": len(rows), "forced_pct": round(100 * np.mean([r["forced"] for r in rows]), 1),
                  "invalid_pct": round(100 * np.mean([not r["valid"] for r in rows]), 1),
                  "with_call_pct": round(100 * np.mean([bool(r["calls"]) for r in rows]), 1),
                  "gen_tokens_median": gt[len(gt) // 2], "over_160_pct": round(100 * np.mean([g > 160 for g in gt]), 1),
                  "seconds_mean": round(float(np.mean([r["seconds"] for r in rows])), 2),
                  "hours": round(sum(r["seconds"] for r in rows) / 3600, 2),
                  "peak_gib": max(r["peak_gib"] for r in rows)}
    res["operations"] = ops

    (OUT / "scores.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("n", "scores", "gate", "R_against_B", "rc_size")}, indent=1))
    print(json.dumps({t: {k: v for k, v in f.items() if k != "ids_all_wrong"} for t, f in res["validity"].items()}, indent=1))


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=check)
    sub.add_parser("draw").set_defaults(fn=draw)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=ARMS, required=True)
    r.set_defaults(fn=run)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
