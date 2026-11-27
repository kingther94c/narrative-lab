"""EXP-0059: S1 main experiment, distilling financial analysis into the 0.8B (pre-registered in the registry).

One script for the whole run, each step resumable, one MLX process at a time (``queue``):

  chains     the teacher's chains on the first GEN_ITEMS pool items in kind-balanced order (EXP-0071's teacher)
  verify     EXP-0071's checks on those chains
  fetch      GSM8K's training split from Hugging Face to the drive, once (never into git)
  math, bstd EXP-0071's math answers and EXP-0070's B answers, by their own scripts (see queue)
  sets       training sets F1, F2-2k, F2-8k
  train      full fine-tuning of the 0.8B for one arm (EXP-0014's setup, 640 tokens, one epoch)
  devdraw    the development R items: v1 counterparts of EXP-0050's 450 drawn base items
  draw       the R v1 test draw (ids only; prints counts and a hash, never item text)
  run        one arm on one set: rdev, bdev, rtest, twins, btest, seca
  queue      every step in the registered order
  score      the hypotheses and the reported slices, to scores.json (aggregates only)

Test items are read by the program only; nothing here prints their text.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0050_s1r_headroom as R  # noqa: E402  (frozen; R grading, R score, bootstrap, answer with forced cue)
import exp0053_s1r_build_v1 as V1  # noqa: E402  (frozen; section R v1 items)
import exp0070_s1f_factory_v2 as F  # noqa: E402  (frozen; pool, B answers, chat template, 640-token fit)
import exp0071_s1f_factory_v21 as F71  # noqa: E402  (frozen once run; chains and math answers)

C, E, S = R.C, R.E, R.S  # exp0016 (answer), exp0014 (training, B, section A), exp0007 (models, budget)
D14 = E
X56, I55 = F.X56, F.I55
OUT = R.NL / "exp0059"
D14.OUT = OUT  # EXP-0014's run_training reads OUT/sets and writes OUT/checkpoints
D14.SEQ = F.SEQ  # 640
SEED = 1
FACTORY = {"F1": 8000, "F2-2k": 2000, "F2-8k": 8000}
GENERAL_SHARE = 0.25  # general examples per factory example: 20% of the total
TRAINED = list(FACTORY)
ARMS_TEST = ["P0", "P2B", "T", "F1", "F2-2k", "F2-8k"]
ARMS_TWINS = ["P0", "F2-8k"]
ARMS_RETAIN = ["P0", "F1", "F2-2k", "F2-8k"]
IN_FAMILY = ["R1.1", "R1.2", "R1.3", "R1.6", "R1.7", "R1.8", "R1.9"]
HELD_OUT = ["R1.4", "R1.5"]
PER_TEMPLATE, DRAW_SEED = 167, "exp0059"
AVG_A = 0.5
STD_R, CAP = R.STD_R, R.CAP
HF2_TWIN_MARGIN, HF3_MARGIN = 5.0, 3.0
CHAINS_DIR, MATH_DIR, BSTD_DIR = "main", "main", "main"
GEN_ITEMS, GEN_K, GEN_BATCH = 11_000, 4, 16  # items in kind-balanced order given to the teacher
MATH_N, B_N = 2_400, 1_500  # problems and B items answered; the sets take the first 1,000 kept of each
GSM8K_REPO, GSM8K_FILE = "openai/gsm8k", "main/train-00000-of-00001.parquet"  # MIT licence
GSM8K_DIR = F.E.DRIVE / "external" / "gsm8k"
GSM8K_JSONL = GSM8K_DIR / "gsm8k_main_train.jsonl"
MATH_FILES = [GSM8K_JSONL]  # GSM8K's full training split (owner-approved download, 2026-11-27)
ITEMS_TEST = V1.V0.OUT / "items_test.jsonl"
ITEMS_DEV = V1.V0.OUT / "items_dev.jsonl"


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8")] if path.exists() else []


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ------------------------------------------------------------------ training sets


def gold_text(it: dict) -> str:
    """F1's target: the item's gold written in its answer format."""
    g = it["gold"]
    if it["atype"] == "table":
        return "\n".join(f"{c}: {v}" for c, v in g.items())
    if it["atype"] == "number":
        tol = it["tol"]["abs"]
        dec = next(d for d in range(0, 8) if abs(round(g, d) - g) <= tol / 2)
        v = f"{round(g, dec):.{dec}f}"
        return {"boxed": f"\\boxed{{{v}}}", "answer_line": f"Answer: {v}", "json": json.dumps({"answer": float(v)})}[it["format"]]
    return {"boxed": f"\\boxed{{{g}}}", "answer_line": f"Answer: {g}", "json": json.dumps({"answer": g}),
            "sentence": f"The answer is {g}."}[it["format"]]


def balanced(items: list[dict]) -> list[dict]:
    """Items reordered so that every prefix follows EXP-0055's kind quotas as far as the kinds last:
    at each step the next item, in rank order, of the kind furthest behind its quota share (ties in
    QUOTA's order); a kind with no item left is skipped."""
    by = collections.defaultdict(list)
    for it in sorted(items, key=lambda r: r["rank"]):
        by[it["kind"]].append(it)
    kinds = [k for k in I55.QUOTA if by[k]]
    pos, got, out = collections.Counter(), collections.Counter(), []
    while kinds:
        k = min(kinds, key=lambda k: (got[k] / I55.QUOTA[k], list(I55.QUOTA).index(k)))
        out.append(by[k][pos[k]])
        pos[k] += 1
        got[k] += 1
        if pos[k] == len(by[k]):
            kinds.remove(k)
    return out


def chains(_: argparse.Namespace) -> None:
    S.need_drive()
    model, tok = E.load_model(E.TEACHER)
    base = OUT / "chains" / CHAINS_DIR
    base.mkdir(parents=True, exist_ok=True)
    path = base / "samples.jsonl"
    done = {r["id"] for r in jl(path)}
    jobs, skipped = [], 0
    for it in balanced(X56.pool())[:GEN_ITEMS]:
        if it["id"] in done:
            continue
        cap = F.room(len(tok.encode(F.chat(tok, it["prompt"]))))
        if cap < F.MIN_ROOM:
            skipped += 1
            continue
        jobs += [{"key": {"id": it["id"]}, "prompt": F.chat(tok, F71.teacher_text(it)), "cap": cap, "sample": s}
                 for s in range(GEN_K)]
    st = F.generate(model, tok, jobs, GEN_BATCH, path, F.sampled)
    print(json.dumps({**st, "items skipped, prompt too long": skipped}), flush=True)


def verify(_: argparse.Namespace) -> None:
    F.OUT = OUT  # EXP-0070's verify reads OUT/chains/<dir>, with EXP-0071's arithmetic check in place
    F.verify(argparse.Namespace(dir=CHAINS_DIR))


def sets(_: argparse.Namespace) -> None:
    from transformers import AutoTokenizer

    S.need_drive()
    tok = AutoTokenizer.from_pretrained(str(S.model_path(E.STUDENT)))
    items = {it["id"]: it for it in X56.pool()}
    kept = collections.defaultdict(list)
    for r in jl(OUT / "chains" / CHAINS_DIR / "kept.jsonl"):
        kept[r["id"]].append(r)
    first = {i: min(rs, key=lambda r: r["sample"]) for i, rs in kept.items()}
    order = [it["id"] for it in balanced([items[i] for i in first])]
    math_rows = jl(F71.OUT / "math" / MATH_DIR / "kept.jsonl")
    seen, math_first = set(), []
    for r in math_rows:  # one answer a problem, in the problems' seeded order
        if r["id"] not in seen:
            seen.add(r["id"])
            math_first.append(r)
    probs_order = {p["id"]: k for k, p in enumerate(F.math_problems(MATH_FILES))}
    math_first.sort(key=lambda r: probs_order.get(r["id"], 10 ** 9))
    border = [it["id"] for it in jl(E.TRAIN)]
    random.Random(F.SEED0).shuffle(border)
    bpos = {i: k for k, i in enumerate(border)}
    bkept = sorted(jl(F.OUT / "bstd" / BSTD_DIR / "kept.jsonl"), key=lambda r: bpos[r["id"]])
    btrain = {it["id"]: it for it in jl(E.TRAIN)}

    def seq(prompt_text: str, response: str) -> dict | None:
        pt = tok.encode(prompt_text)
        ct = tok.encode(response) + [tok.eos_token_id]
        if len(pt) + len(ct) > F.SEQ:
            return None
        return {"tokens": pt + ct, "offset": len(pt)}

    summary = {}
    (OUT / "sets").mkdir(parents=True, exist_ok=True)
    for arm, n in FACTORY.items():
        g = round(n * GENERAL_SHARE / 2)
        if len(order) < n or len(math_first) < g or len(bkept) < g:
            sys.exit(f"{arm}: {len(order)} chains, {len(math_first)} math, {len(bkept)} B; need {n}, {g}, {g}")
        rows, drop = [], collections.Counter()
        for i in order[:n]:
            it = items[i]
            resp = gold_text(it) if arm == "F1" else first[i]["response"]
            s = seq(F.chat(tok, it["prompt"]), resp)
            if s is None:
                drop["factory"] += 1
                continue
            rows.append({**s, "src": "factory", "id": i})
        for r in math_first[:g]:
            s = seq(F.chat(tok, r["prompt"]), r["response"])
            drop["math"] += s is None
            if s:
                rows.append({**s, "src": "math", "id": r["id"]})
        for r in bkept[:g]:
            s = seq(E.prompt_for(tok, btrain[r["id"]], E.STANDARD), r["response"])
            drop["B"] += s is None
            if s:
                rows.append({**s, "src": "B", "id": r["id"]})
        if sum(drop.values()):
            sys.exit(f"{arm}: sequences over {F.SEQ} tokens: {dict(drop)}")
        random.Random(SEED).shuffle(rows)
        with open(OUT / "sets" / f"{arm}.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        lens = sorted(len(r["tokens"]) for r in rows)
        summary[arm] = {"examples": len(rows), "by source": dict(collections.Counter(r["src"] for r in rows)),
                        "kinds": dict(collections.Counter(items[r["id"]]["kind"] for r in rows if r["src"] == "factory")),
                        "tokens median / p90 / max": [lens[len(lens) // 2], lens[9 * len(lens) // 10], lens[-1]],
                        "sha256_ids": sha("".join(r["id"] for r in rows))}
    (OUT / "sets" / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def train(a: argparse.Namespace) -> None:
    S.need_drive()
    if (OUT / "checkpoints" / f"{a.arm}-s{SEED}" / "train_log.json").exists():
        return
    info = D14.run_training(a.arm, SEED, 1)
    print(json.dumps({k: v for k, v in info.items() if k != "log"}))


def weights(arm: str) -> Path:
    return OUT / "checkpoints" / f"{arm}-s{SEED}" / "final.safetensors"


# ------------------------------------------------------------------ evaluation sets


def devdraw(_: argparse.Namespace) -> None:
    """Development R items: the v1 counterparts of EXP-0050's 450 drawn base items (same release, template, variant)."""
    v0 = R.items_by_id()
    drawn = [v0[r["id"]] for r in R.jl(R.DRAW)]
    key = lambda i: (i["accession"], i["template"], i["variant"])  # noqa: E731
    v1 = {key(i): i for i in jl(ITEMS_DEV) if not i.get("twin_of")}
    got = [v1[key(i)] for i in drawn if key(i) in v1]
    (OUT).mkdir(parents=True, exist_ok=True)
    with open(OUT / "dev_draw.jsonl", "w") as fh:
        for i in got:
            fh.write(json.dumps({"id": i["id"], "template": i["template"], "cik": i["cik"]}) + "\n")
    rep = {"EXP-0050 base items": len(drawn), "v1 counterparts": len(got),
           "by template": dict(sorted(collections.Counter(i["template"] for i in got).items()))}
    (OUT / "dev_draw.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


def draw(_: argparse.Namespace) -> None:
    """R v1 test draw: PER_TEMPLATE base items a template, at most one a company a template, strata in turn."""
    S.need_drive()
    allit = jl(ITEMS_TEST)
    base = [i for i in allit if not i.get("twin_of") and i["post_cutoff"]]
    picked, report = [], {}
    for t in R.TEMPLATES:
        pool = collections.defaultdict(list)
        for i in sorted((i for i in base if i["template"] == t), key=lambda i: sha(f"{DRAW_SEED}:{i['id']}")):
            pool[R.stratum(i)].append(i)
        keys = sorted(pool)
        per_co, got = set(), []
        while len(got) < PER_TEMPLATE and any(pool[k] for k in keys):
            for k in keys:
                while pool[k]:
                    i = pool[k].pop(0)
                    if i["cik"] not in per_co:
                        got.append(i)
                        per_co.add(i["cik"])
                        break
                if len(got) >= PER_TEMPLATE:
                    break
        picked += got
        report[t] = {"items": len(got), "companies": len(per_co),
                     "strata": dict(sorted(collections.Counter(R.stratum(i) for i in got).items()))}
    ids = [i["id"] for i in picked]
    pos = {k: n for n, k in enumerate(ids)}
    twins = sorted((i for i in allit if i.get("twin_of") in pos), key=lambda i: (pos[i["twin_of"]], R.TWIN_ORDER[i["twin"]]))
    with open(OUT / "test_draw.jsonl", "w") as fh:
        for i in picked:
            fh.write(json.dumps({"id": i["id"], "template": i["template"], "cik": i["cik"]}) + "\n")
    with open(OUT / "test_twins.jsonl", "w") as fh:
        for i in twins:
            fh.write(json.dumps({"id": i["id"], "twin_of": i["twin_of"], "twin": i["twin"], "template": i["template"]}) + "\n")
    report["total"] = {"base": len(ids), "companies": len({i["cik"] for i in picked}),
                       "twins": dict(collections.Counter(i["twin"] for i in twins)),
                       "sha256_base_ids": sha("".join(ids)), "sha256_twin_ids": sha("".join(i["id"] for i in twins))}
    (OUT / "test_draw.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report["total"], indent=1))


def load_by_ids(draw_path: Path, items_path: Path) -> list[dict]:
    want = [r["id"] for r in jl(draw_path)]
    by = {}
    for r in map(json.loads, open(items_path, encoding="utf-8")):
        by[r["id"]] = r
    return [by[i] for i in want]


def eval_set(name: str) -> list[dict]:
    if name == "rdev":
        return load_by_ids(OUT / "dev_draw.jsonl", ITEMS_DEV)
    if name == "rtest":
        return load_by_ids(OUT / "test_draw.jsonl", ITEMS_TEST)
    if name == "twins":
        return load_by_ids(OUT / "test_twins.jsonl", ITEMS_TEST)
    if name == "bdev":
        return E.load_ids(E.DEV_DRAW, E.V.OUT / "items_dev.jsonl")
    if name == "btest":
        return E.load_ids(E.TEST_DRAW, E.TEST_ITEMS)
    raise KeyError(name)


# ------------------------------------------------------------------ running arms


def load_arm(arm: str):
    import mlx.core as mx
    from mlx.utils import tree_flatten

    if arm == "P0":
        return E.load_model(E.STUDENT)
    if arm == "P2B":
        return E.load_model("qwen3.5-2b")
    if arm == "T":
        return E.load_model(E.TEACHER)
    if arm in TRAINED:
        return E.load_model(E.STUDENT, weights(arm))
    if arm == "avg":  # F2-8k averaged with the released weights, as EXP-0051
        model, tok = E.load_model(E.STUDENT)
        base = dict(tree_flatten(model.parameters()))
        trained = mx.load(str(weights("F2-8k")))
        new = [(k, ((1 - AVG_A) * base[k].astype(mx.float32) + AVG_A * t.astype(mx.float32)).astype(t.dtype))
               for k, t in trained.items()]
        model.load_weights(new, strict=False)
        mx.eval(model.parameters())
        return model, tok
    raise KeyError(arm)


def run(a: argparse.Namespace) -> None:
    import mlx.core as mx

    S.need_drive()
    path = OUT / "runs" / a.set / f"{a.arm}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if a.set == "seca":
        from learnai.finbench import load_problems

        done = {r["uid"] for r in jl(path)}
        probs = [p for p in load_problems(E.SECA_N, seed=E.BOOT_SEED) if p.uid not in done]
        if not probs:
            return
        model, tok = load_arm(a.arm)
        for p in probs:
            prompt = F.chat(tok, p.prompt)
            t0 = time.time()
            out, n, reason = E.gen(model, tok, prompt, 512)
            E.append(path, {"uid": p.uid, "generated_tokens": n, "finish": reason, "response": out,
                            "seconds": round(time.time() - t0, 2), "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})
        return
    items = eval_set(a.set)
    done = {r["id"] for r in jl(path)}
    todo = [i for i in items if i["id"] not in done]
    if not todo:
        return
    model, tok = load_arm(a.arm)
    for it in todo:
        if a.set in ("bdev", "btest"):
            row = E.answer(model, tok, it, E.STANDARD, 512)
        else:
            row = C.answer(model, tok, it, STD_R, CAP, False)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        E.append(path, row)


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%Y-%m-%d %H:%M:%S"), *args, flush=True)
        if subprocess.run(me + list(args)).returncode != 0:
            sys.exit(f"step failed: {args}")

    def other(script, *args):
        print(time.strftime("%Y-%m-%d %H:%M:%S"), script, *args, flush=True)
        if subprocess.run([sys.executable, str(Path(__file__).parent / script)] + list(args)).returncode != 0:
            sys.exit(f"step failed: {script} {args}")

    if not (OUT / "sets" / "summary.json").exists():
        step("chains")
        step("verify")
        other("exp0071_s1f_factory_v21.py", "math", "--n", str(MATH_N), "--dir", MATH_DIR,
              "--files", ",".join(str(f) for f in MATH_FILES))
        other("exp0070_s1f_factory_v2.py", "bstd", "--n", str(B_N), "--dir", BSTD_DIR)
        step("sets")
    for arm in ["F2-8k", "F1", "F2-2k"]:
        step("train", "--arm", arm)
    step("devdraw")
    for arm in TRAINED + ["avg", "P0"]:
        step("run", "--arm", arm, "--set", "rdev")
        step("run", "--arm", arm, "--set", "bdev")
    step("draw")
    for arm in ARMS_TEST:
        step("run", "--arm", arm, "--set", "rtest")
    for arm in ARMS_TWINS:
        step("run", "--arm", arm, "--set", "twins")
    for arm in ARMS_RETAIN:
        step("run", "--arm", arm, "--set", "btest")
        step("run", "--arm", arm, "--set", "seca")
    step("score")


# ------------------------------------------------------------------ score


def graded(set_name: str, arm: str, items: list[dict]) -> dict:
    rows = {r["id"]: r for r in jl(OUT / "runs" / set_name / f"{arm}.jsonl")}
    if len(rows) != len(items) or any(i["id"] not in rows for i in items):
        sys.exit(f"{set_name} {arm}: {len(rows)} of {len(items)} responses")
    return {i["id"]: {**rows[i["id"]], **R.grade_r(i, rows[i["id"]]["response"])} for i in items}


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from learnai.finbench import grade as fgrade, problem_for

    S.need_drive()
    res: dict = {}
    # development
    dev = eval_set("rdev")
    bdev = eval_set("bdev")
    devR = {}
    for arm in TRAINED + ["avg", "P0"]:
        g = graded("rdev", arm, dev)
        brows = {r["id"]: r for r in jl(OUT / "runs" / "bdev" / f"{arm}.jsonl")}
        devR[arm] = {"R": round(R.macro(dev, [g[i["id"]]["correct"] for i in dev]), 1),
                     "B": round(100 * np.mean([E.V.grade(i, brows[i["id"]]["response"], "off")["correct"] for i in bdev]), 1)}
    res["development"] = devR
    chosen = max(["F2-2k", "F2-8k"], key=lambda a: (devR[a]["R"], a == "F2-2k"))  # ties to the smaller set
    res["HF3 student, chosen on development"] = chosen
    res["B development more than 10 under P0"] = [a for a in TRAINED if devR[a]["B"] < devR["P0"]["B"] - 10]

    # test, R
    base = eval_set("rtest")
    twins = eval_set("twins")
    G = {a: graded("rtest", a, base) for a in ARMS_TEST}
    boot = R.Boot([i["cik"] for i in base + twins])
    W = boot.weights([i["cik"] for i in base])

    def part(templates):
        its = [i for i in base if i["template"] in templates]
        return its, boot.weights([i["cik"] for i in its])

    def corr(a, its):
        return np.array([G[a][i["id"]]["correct"] for i in its], float)

    fam, Wf = part(IN_FAMILY)
    hel, Wh = part(HELD_OUT)
    tab = {}
    for a in ARMS_TEST:
        tab[a] = {"R": round(R.macro(base, corr(a, base)), 1), "R_ci": R.ci(R.macro(base, corr(a, base), W)),
                  "in_family": round(R.macro(fam, corr(a, fam)), 1), "held_out": round(R.macro(hel, corr(a, hel)), 1),
                  "by_template": {t: round(R.macro([i for i in base if i["template"] == t],
                                                   corr(a, [i for i in base if i["template"] == t])), 1) for t in R.TEMPLATES},
                  "forced": round(100 * np.mean([G[a][i["id"]]["forced"] for i in base]), 1),
                  "valid_box": round(100 * np.mean([G[a][i["id"]]["valid"] for i in base]), 1),
                  "generated_tokens_mean": round(float(np.mean([G[a][i["id"]]["generated_tokens"] for i in base])), 1)}
    res["test"] = {"n": {"base": len(base), "companies": len({i["cik"] for i in base}), "twins": len(twins)}, "scores": tab}

    def diff(x, y, its, Wx):
        d = R.macro(its, corr(x, its), Wx) - R.macro(its, corr(y, its), Wx)
        return round(R.macro(its, corr(x, its)) - R.macro(its, corr(y, its)), 1), R.ci(d)

    hf = {}
    d, c = diff("F2-8k", "F1", fam, Wf)
    hf["HF1"] = {"F2-8k - F1, in-family": d, "ci95": c, "supported": bool(c[0] > 0)}
    dh, ch = diff("F2-8k", "P0", hel, Wh)
    df, cf = diff("F2-8k", "P0", fam, Wf)
    # twins
    by = {i["id"]: i for i in base}
    tw = {}
    for a in ARMS_TWINS:
        gt = graded("twins", a, twins)
        cnt = collections.defaultdict(collections.Counter)
        for t_it in twins:
            b_it = by[t_it["twin_of"]]
            rb, rt = G[a][b_it["id"]], gt[t_it["id"]]
            k = t_it["twin"]
            cnt[k]["n"] += 1
            if k == "flip" and rb["correct"]:
                cnt[k]["base_right"] += 1
                cnt[k]["follows"] += rt["correct"]
            if k == "hold":
                cnt[k]["same"] += R.same_answer(b_it, rb["answer"], rt["answer"])
            if k == "mirror":
                cnt[k]["contradiction"] += bool(rb["answer"] in b_it["options"] and rb["answer"] == rt["answer"])
        tw[a] = {"flip_rate": round(100 * cnt["flip"]["follows"] / max(1, cnt["flip"]["base_right"]), 1),
                 "hold_stability": round(100 * cnt["hold"]["same"] / max(1, cnt["hold"]["n"]), 1),
                 "mirror_contradiction": round(100 * cnt["mirror"]["contradiction"] / max(1, cnt["mirror"]["n"]), 1),
                 "n": {k: c_["n"] for k, c_ in cnt.items()}}
    res["twins"] = tw
    twin_ok = (tw["F2-8k"]["flip_rate"] >= tw["P0"]["flip_rate"] - HF2_TWIN_MARGIN
               and tw["F2-8k"]["hold_stability"] >= tw["P0"]["hold_stability"] - HF2_TWIN_MARGIN)
    hf["HF2"] = {"F2-8k - P0, held-out": dh, "ci95": ch, "F2-8k - P0, in-family": df, "in_family_ci95": cf,
                 "held-out gain at least half the in-family gain": bool(dh >= 0.5 * df),
                 "twins no more than 5 points worse": bool(twin_ok),
                 "supported": bool(ch[0] > 0 and dh >= 0.5 * df and twin_ok)}
    d3, c3 = diff(chosen, "P2B", base, W)
    hf["HF3"] = {f"{chosen} - P2B, all templates": d3, "ci95": c3, "supported": bool(c3[0] > -HF3_MARGIN)}
    res["hypotheses"] = hf
    fam6, Wf6 = part([t for t in IN_FAMILY if t != "R1.7"])  # R1.7 kept against EXP-0057's rule (owner, 2026-11-27)
    res["descriptive"] = {"F2-8k - F2-2k": dict(zip(["R", "ci95"], diff("F2-8k", "F2-2k", base, W))),
                          "T - " + chosen: dict(zip(["R", "ci95"], diff("T", chosen, base, W))),
                          "HF1 without R1.7": dict(zip(["F2-8k - F1", "ci95"], diff("F2-8k", "F1", fam6, Wf6)))}

    # retention
    bt = eval_set("btest")
    ret = {}
    for a in ARMS_RETAIN:
        rows = {r["id"]: r for r in jl(OUT / "runs" / "btest" / f"{a}.jsonl")}
        sa = collections.defaultdict(list)
        for r in jl(OUT / "runs" / "seca" / f"{a}.jsonl"):
            p = problem_for(r["uid"])
            sa[p.source].append(fgrade(p, r["response"], thinking=False)["correct"])
        ret[a] = {"B_test": round(100 * np.mean([E.V.grade(i, rows[i["id"]]["response"], "off")["correct"] for i in bt]), 1),
                  "section_A": {s: round(100 * sum(v) / len(v), 1) for s, v in sa.items()}}
    res["retention"] = ret
    res["sets"] = json.loads((OUT / "sets" / "summary.json").read_text())
    res["training"] = {a: {k: v for k, v in json.loads((OUT / "checkpoints" / f"{a}-s{SEED}" / "train_log.json").read_text()).items()
                           if k != "log"} for a in TRAINED}
    (OUT / "scores.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("development", "hypotheses", "retention")}, indent=1))


# ------------------------------------------------------------------ fetch


def fetch(_: argparse.Namespace) -> None:
    """GSM8K's training split to the drive: the parquet as served, the same rows as jsonl, a manifest."""
    S.need_drive()
    if GSM8K_JSONL.exists():
        print(json.dumps(json.loads((GSM8K_DIR / "manifest.json").read_text()), indent=1))
        return
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download

    GSM8K_DIR.mkdir(parents=True, exist_ok=True)
    rev = HfApi().dataset_info(GSM8K_REPO, token=False).sha
    path = Path(hf_hub_download(GSM8K_REPO, GSM8K_FILE, repo_type="dataset", revision=rev,
                                local_dir=GSM8K_DIR / "raw", token=False))
    rows = pq.read_table(path).to_pylist()
    assert rows and all(set(r) == {"question", "answer"} for r in rows), "unexpected columns"
    tmp = GSM8K_JSONL.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"question": r["question"], "answer": r["answer"]}, ensure_ascii=False) + "\n")
    tmp.rename(GSM8K_JSONL)
    usable = F.math_problems([GSM8K_JSONL])
    man = {"repo": GSM8K_REPO, "file": GSM8K_FILE, "revision": rev, "licence": "MIT",
           "parquet sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "jsonl sha256": hashlib.sha256(GSM8K_JSONL.read_bytes()).hexdigest(),
           "rows": len(rows), "rows with a numeric answer": len(usable),
           "fetched": time.strftime("%Y-%m-%d %H:%M:%S %z")}
    (GSM8K_DIR / "manifest.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man, indent=1))


# ------------------------------------------------------------------ check


def check(_: argparse.Namespace) -> None:
    from learnai.finbench import last_boxed  # noqa: F401  (the grader's import works)

    assert D14.SEQ == 640 and D14.OUT == OUT and set(IN_FAMILY) | set(HELD_OUT) == set(R.TEMPLATES)
    assert not set(IN_FAMILY) & set(HELD_OUT)
    pool = X56.pool() if (I55.OUT / "pool.jsonl").exists() else []
    bad = [it["id"] for it in pool if not X56.grade(it, gold_text(it))["correct"]]
    assert not bad, f"{len(bad)} items whose written gold does not grade right, e.g. {bad[:3]}"
    for arm, n in FACTORY.items():
        assert round(n * GENERAL_SHARE / 2) * 2 / (n + round(n * GENERAL_SHARE / 2) * 2) == 0.2
    if pool:
        pre = collections.Counter(it["kind"] for it in balanced(pool)[:GEN_ITEMS])
        share = {k: round(100 * pre[k] / GEN_ITEMS, 1) for k in I55.QUOTA}
    else:
        share = {}
    toy = [{"id": str(n), "kind": k, "rank": n} for n, k in enumerate(["growth"] * 30 + ["table"] * 2 + ["extract"] * 30)]
    assert [it["kind"] for it in balanced(toy)][:5] == ["extract", "growth", "table", "growth", "extract"]
    probs = F.math_problems(MATH_FILES) if GSM8K_JSONL.exists() else []
    assert not probs or all(p["source"] == "gsm8k" for p in probs)
    print(json.dumps({"checks": "pass", "pool items whose written gold grades right": len(pool),
                      "kind shares (%) of the first GEN_ITEMS in balanced order": share,
                      "GSM8K problems with a numeric answer": len(probs)}, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    sub.add_parser("check").set_defaults(fn=check)
    sub.add_parser("fetch").set_defaults(fn=fetch)
    sub.add_parser("chains").set_defaults(fn=chains)
    sub.add_parser("verify").set_defaults(fn=verify)
    sub.add_parser("sets").set_defaults(fn=sets)
    t = sub.add_parser("train"); t.add_argument("--arm", required=True, choices=TRAINED); t.set_defaults(fn=train)
    sub.add_parser("devdraw").set_defaults(fn=devdraw)
    sub.add_parser("draw").set_defaults(fn=draw)
    r = sub.add_parser("run"); r.add_argument("--arm", required=True, choices=ARMS_TEST + ["avg"])
    r.add_argument("--set", required=True, choices=["rdev", "bdev", "rtest", "twins", "btest", "seca"]); r.set_defaults(fn=run)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
