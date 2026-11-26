"""EXP-0051: two diagnostics before the S1 distillation re-plan, no training (development items only).

Pre-registered in research/registry/experiment_registry.md. Design:
``research/design/s1_finance_distillation_replan.md`` §4.4, approved by the owner 2026-11-26
("全案推荐来", decision 4).

1. **Weight averaging.** C (EXP-0014's D3-s1) and K2 (EXP-0017's K2-s1) averaged with the released
   Qwen3.5-0.8B, W = (1 - a) * W_base + a * W_trained over every tensor the checkpoint holds: K2 at
   a = 0.25, 0.5 and 0.75, C at a = 0.5. Each averaged model answers the 450 plain development R base
   items of EXP-0050 exactly as C and K2 did there (terse instruction with "final answer", the inline
   calculator, 512 tokens, forced answer), and the 600 B development items exactly as C and K2 did on
   B (terse instruction, the inline calculator, 160 tokens, forced answer).
2. **Sampling ceiling.** The released 0.8B (EXP-0050's B0: standard instruction with "final answer", no
   tool, 512 tokens, forced answer) answers each of the 450 plain base items 8 times, sampled at
   EXP-0014's temperature 0.7 and top-p 0.95, seed 20261126 + item index, in batches of 8.

Grading is EXP-0050's (``grade_r``) and EXP-0010's (``V.grade``). Every item here is a development
item; Claude may read them and the responses.

  check    averaging identities (a = 0 and 1), one a = 1 response against K2's own on R and on B, and
           one batched sample (speed, memory)
  avg      one averaged arm, R then B, resumable
  sample   the 8 samples per item, resumable
  queue    avg arms in the registered order, then sample, then score
  score    the registered rules and the descriptive slices, to scores.json

    conda run --no-capture-output -n py313 python research/experiments/exp0051_s1f_diagnostics.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0051_s1f_diagnostics.py queue
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0050_s1r_headroom as R  # noqa: E402  (frozen; importing it sets the calculator to the inline rule)

C, E, S, V = R.C, R.E, R.S, R.V
OUT = R.NL / "exp0051"
AVG = ["K2@0.25", "K2@0.5", "K2@0.75", "C@0.5"]  # run order
R_CAP, B_CAP = R.CAP, E.LABEL_CAP  # 512 on R (EXP-0050), 160 on B (EXP-0016 and 0017)
K, SEED0 = 8, 20261126
TEMP, TOP_P = E.TEMP, E.TOP_P  # 0.7, 0.95 (EXP-0014)
LABEL_TEMPLATES = [f"R1.{k}" for k in range(1, 7)]
OPEN_TEMPLATES = ["R1.7", "R1.8", "R1.9"]  # number or "cannot be determined": no guessing among options
REPAIR_R_MARGIN, REPAIR_B_MARGIN, ROOM = 5.0, 3.0, 10.0


def r_items() -> list[dict]:
    return R.sets()["plain"]


def b_items() -> list[dict]:
    return E.load_ids(E.DEV_DRAW, V.OUT / "items_dev.jsonl")


# ------------------------------------------------------------------ averaged models


def averaged(name: str):
    """(model, tokenizer, R instruction) for 'K2@0.5' and the like."""
    import mlx.core as mx
    from mlx.utils import tree_flatten

    src, a = name.split("@")
    a = float(a)
    key, w, ins, calc = R.arm(src)
    assert calc and key == E.STUDENT
    model, tok = E.load_model(key)
    base = dict(tree_flatten(model.parameters()))
    trained = mx.load(str(w))
    missing = [k for k in trained if k not in base]
    if missing:
        sys.exit(f"{len(missing)} checkpoint tensors not in the model, e.g. {missing[:3]}")
    new = []
    for k, t in trained.items():
        b = base[k]
        if b.shape != t.shape:
            sys.exit(f"shape mismatch at {k}: {b.shape} against {t.shape}")
        new.append((k, ((1 - a) * b.astype(mx.float32) + a * t.astype(mx.float32)).astype(t.dtype)))
    model.load_weights(new, strict=False)
    mx.eval(model.parameters())
    return model, tok, ins


def avg(a: argparse.Namespace) -> None:
    import mlx.core as mx

    S.need_drive()
    model = tok = ins = None
    for part, items, cap in (("R", r_items(), R_CAP), ("B", b_items(), B_CAP)):
        path = OUT / "avg" / a.arm / f"{part}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        done = {r["id"] for r in R.jl(path)}
        todo = [i for i in items if i["id"] not in done]
        if not todo:
            continue
        if model is None:
            model, tok, ins = averaged(a.arm)
        instruction = ins if part == "R" else E.TERSE
        for it in todo:
            row = C.answer(model, tok, it, instruction, cap, True)
            row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
            E.append(path, row)


# ------------------------------------------------------------------ sampling


def sample_batch(model, tok, item: dict, seed: int) -> list[dict]:
    import mlx.core as mx
    from learnai.finbench import last_boxed
    from mlx_lm.generate import batch_generate
    from mlx_lm.sample_utils import make_sampler

    prompt = E.prompt_for(tok, item, R.STD_R)
    ids = tok.encode(prompt)
    mx.random.seed(seed)
    t0 = time.time()
    res = batch_generate(model, tok, [ids] * K, max_tokens=R_CAP, sampler=make_sampler(temp=TEMP, top_p=TOP_P),
                         return_token_ids=True)
    secs = time.time() - t0
    rows = []
    for k, (text, toks) in enumerate(zip(res.texts, res.token_ids)):
        finish = "length" if len(toks) >= R_CAP else "stop"
        forced, cont, nf = None, "", 0
        if finish == "length" and last_boxed(text) is None:
            forced = S.CUE
            cont, nf, _ = E.gen(model, tok, prompt + text + forced, S.FORCE_TOKENS)
        rows.append({"id": item["id"], "sample": k, "seed": seed, "prompt_tokens": len(ids),
                     "generated_tokens": len(toks), "finish": finish, "forced": bool(forced), "forced_tokens": nf,
                     "response": text + (forced or "") + cont, "batch_seconds": round(secs, 2)})
    return rows


def sample(_: argparse.Namespace) -> None:
    import mlx.core as mx

    S.need_drive()
    path = OUT / "samples" / "B0.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in R.jl(path)}
    items = r_items()
    model, tok = E.load_model(E.STUDENT)
    for n, it in enumerate(items):
        if it["id"] in done:
            continue
        for row in sample_batch(model, tok, it, SEED0 + n):
            row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
            E.append(path, row)


# ------------------------------------------------------------------ checks


def check(_: argparse.Namespace) -> None:
    import mlx.core as mx
    from mlx.utils import tree_flatten

    S.need_drive()
    # 1. a = 0 gives the base, a = 1 gives K2, tensor by tensor
    for a, ref in ((0.0, "base"), (1.0, "K2")):
        m, tok, _ = averaged(f"K2@{a}")
        got = dict(tree_flatten(m.parameters()))
        if ref == "base":
            want = dict(tree_flatten(E.load_model(E.STUDENT)[0].parameters()))
        else:
            want = mx.load(str(R.arm("K2")[1]))
        worst = max(float(mx.max(mx.abs(got[k].astype(mx.float32) - want[k].astype(mx.float32)))) for k in want
                    if k in got)
        print(f"[check] a={a}: max |difference| against {ref} over {len(want)} tensors = {worst:.3g}")
        assert worst == 0.0
        if a == 1.0:
            # 2. a = 1 reproduces K2's EXP-0050 response on the first R item and EXP-0017's on the first B item
            ri, bi = r_items()[0], b_items()[0]
            r_ref = {r["id"]: r for r in R.jl(R.OUT / "runs" / "K2" / "plain.jsonl")}[ri["id"]]["response"]
            b_ref = {r["id"]: r for r in E.jl(R.B_DEV["K2"])}[bi["id"]]["response"]
            r_new = C.answer(m, tok, ri, R.TERSE_R, R_CAP, True)["response"]
            b_new = C.answer(m, tok, bi, E.TERSE, B_CAP, True)["response"]
            print(f"[check] a=1 R response equal to EXP-0050's K2: {r_new == r_ref}")
            print(f"[check] a=1 B response equal to EXP-0017's K2: {b_new == b_ref}")
            assert r_new == r_ref and b_new == b_ref
        del m
        mx.clear_cache()
    # 3. one batch of 8 samples from the released 0.8B
    m, tok = E.load_model(E.STUDENT)
    mx.reset_peak_memory()
    rows = sample_batch(m, tok, r_items()[0], SEED0)
    g = [R.grade_r(r_items()[0], r["response"]) for r in rows]
    print(f"[check] batch of {K}: {rows[0]['batch_seconds']}s, tokens {[r['generated_tokens'] for r in rows]}, "
          f"distinct responses {len({r['response'] for r in rows})}, correct {sum(x['correct'] for x in g)}, "
          f"peak {mx.get_peak_memory() / S.GIB:.2f} GiB")
    rows2 = sample_batch(m, tok, r_items()[0], SEED0)
    print(f"[check] same seed reproduces the batch: {[r['response'] for r in rows] == [r['response'] for r in rows2]}")


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%H:%M:%S"), *args, flush=True)
        if subprocess.run(me + list(args)).returncode != 0:
            sys.exit(f"step failed: {args}")

    for name in AVG:
        step("avg", "--arm", name)
    step("sample")
    step("score")


# ------------------------------------------------------------------ score


def is_number_box(item: dict, response: str) -> bool:
    from learnai.finbench import last_boxed

    box = last_boxed(response)
    return box is not None and R.read_label(box, item["options"]) is None and V.read_number(box) is not None


def score(_: argparse.Namespace) -> None:
    import numpy as np

    S.need_drive()
    ri, bi = r_items(), b_items()
    old = R.load_runs()
    bdev = {a: {r["id"]: r for r in E.jl(p)} for a, p in R.B_DEV.items()}
    boot = R.Boot([i["cik"] for i in ri] + [i["cik"] for i in bi])
    Wr, Wb = boot.weights([i["cik"] for i in ri]), boot.weights([i["cik"] for i in bi])
    labels = [i for i in ri if i["kind"] == "label"]

    def r_vec(rows):
        return np.array([rows[i["id"]]["correct"] for i in ri], float)

    def b_vec(rows):
        return np.array([V.grade(i, rows[i["id"]]["response"], "off")["correct"] for i in bi], float)

    def numbox(rows):
        return round(100 * np.mean([is_number_box(i, rows[i["id"]]["response"]) for i in labels]), 1)

    ref = {a: {"R": r_vec(old[a]["plain"]), "B": b_vec(bdev[a]), "rows": old[a]["plain"]} for a in ("B0", "C", "K2")}
    arms = {}
    for name in AVG:
        rr = {r["id"]: {**r, **R.grade_r(next(i for i in ri if i["id"] == r["id"]), r["response"])}
              for r in R.jl(OUT / "avg" / name / "R.jsonl")}
        bb = {r["id"]: r for r in R.jl(OUT / "avg" / name / "B.jsonl")}
        if len(rr) != len(ri) or len(bb) != len(bi):
            sys.exit(f"{name}: {len(rr)} R and {len(bb)} B responses")
        arms[name] = {"R": r_vec(rr), "B": b_vec(bb), "rows": rr}
    res: dict = {"n": {"R": len(ri), "B": len(bi), "R_companies": len({i["cik"] for i in ri})}}

    # 1. weight averaging
    tab = {}
    for name, v in {**{a: ref[a] for a in ("B0", "C", "K2")}, **arms}.items():
        rows = v["rows"]
        tab[name] = {
            "R": round(R.macro(ri, v["R"]), 1), "R_ci": R.ci(R.macro(ri, v["R"], Wr)),
            "B": round(100 * v["B"].mean(), 1), "B_ci": R.ci(100 * (Wb * v["B"]).sum(1) / Wb.sum(1)),
            "label_items_number_boxed_pct": numbox(rows),
            "per_template": {t: round(R.macro([i for i in ri if i["template"] == t],
                                                [rows[i["id"]]["correct"] for i in ri if i["template"] == t]), 1)
                             for t in R.TEMPLATES},
        }
        if name in arms:
            src = name.split("@")[0]
            dR = R.macro(ri, v["R"], Wr) - R.macro(ri, ref["B0"]["R"], Wr)
            dB = 100 * (Wb * (v["B"] - ref[src]["B"])).sum(1) / Wb.sum(1)
            tab[name].update({
                "R_minus_B0": round(tab[name]["R"] - R.macro(ri, ref["B0"]["R"]), 1), "R_minus_B0_ci": R.ci(dR),
                "B_minus_source": round(100 * (v["B"] - ref[src]["B"]).mean(), 1), "B_minus_source_ci": R.ci(dB),
                "mean_generated_tokens_R": round(np.mean([r["generated_tokens"] for r in rows.values()]), 1),
                "forced_R_pct": round(100 * np.mean([r["forced"] for r in rows.values()]), 1),
            })
    res["averaging"] = tab
    repaired = [n for n in AVG if tab[n]["R_minus_B0"] >= -REPAIR_R_MARGIN and tab[n]["B_minus_source"] >= -REPAIR_B_MARGIN]
    res["rule_1"] = {"repaired_arms": repaired, "repair_works": bool(repaired),
                     "consequence": "+avg is a full arm on test; general mix 10%" if repaired
                     else "+avg descriptive on development only; general mix 20%"}

    # 2. sampling ceiling of the released 0.8B
    samp = collections.defaultdict(list)
    by = {i["id"]: i for i in ri}
    for r in R.jl(OUT / "samples" / "B0.jsonl"):
        samp[r["id"]].append({**r, **R.grade_r(by[r["id"]], r["response"])})
    if len(samp) != len(ri) or any(len(v) != K for v in samp.values()):
        sys.exit(f"samples: {len(samp)} items")
    share = np.array([np.mean([s["correct"] for s in samp[i["id"]]]) for i in ri])
    anyc = np.array([float(any(s["correct"] for s in samp[i["id"]])) for i in ri])

    def vote(i):
        answers = [s["answer"] for s in samp[i["id"]]]
        counts = collections.Counter(R.norm(str(x)) if x is not None else None for x in answers)
        counts.pop(None, None)
        if not counts:
            return 0.0
        top = max(counts.values())
        for s in samp[i["id"]]:  # ties go to the earliest sample
            if s["answer"] is not None and counts[R.norm(str(s["answer"]))] == top:
                return float(s["correct"])
        return 0.0

    maj = np.array([vote(i) for i in ri])
    greedy = ref["B0"]["R"]
    t4 = r_vec(old["4I"]["plain"])
    per_t = {}
    for t in R.TEMPLATES:
        ix = [k for k, i in enumerate(ri) if i["template"] == t]
        its = [ri[k] for k in ix]
        m = len(its[0]["options"]) if its[0]["kind"] == "label" else 0
        per_t[t] = {"greedy": round(R.macro(its, greedy[ix]), 1), "mean_at_8": round(R.macro(its, share[ix]), 1),
                    "maj_at_8": round(R.macro(its, maj[ix]), 1), "pass_at_8": round(R.macro(its, anyc[ix]), 1),
                    "4I": round(R.macro(its, t4[ix]), 1)}
        if m:
            per_t[t]["chance_pass_at_8"] = round(100 * (1 - (1 - 1 / m) ** K), 1)
    oi = [k for k, i in enumerate(ri) if i["template"] in OPEN_TEMPLATES]
    open_items = [ri[k] for k in oi]
    ceil = {"open_greedy": round(R.macro(open_items, greedy[oi]), 1),
            "open_pass_at_8": round(R.macro(open_items, anyc[oi]), 1),
            "open_pass_at_8_ci": R.ci(R.macro(open_items, anyc[oi], boot.weights([i["cik"] for i in open_items]))),
            "open_4I": round(R.macro(open_items, t4[oi]), 1),
            "all_mean_at_8": round(R.macro(ri, share), 1), "all_maj_at_8": round(R.macro(ri, maj), 1),
            "all_greedy": round(R.macro(ri, greedy), 1)}
    room = ceil["open_pass_at_8"] - ceil["open_greedy"]
    res["sampling"] = {"per_template": per_t, "summary": ceil,
                       "forced_pct": round(100 * np.mean([s["forced"] for v in samp.values() for s in v]), 1),
                       "mean_generated_tokens": round(np.mean([s["generated_tokens"] for v in samp.values() for s in v]), 1),
                       "seconds_per_batch": round(np.mean([v[0]["batch_seconds"] for v in samp.values()]), 2)}
    res["rule_2"] = {"room_open_points": round(room, 1), "F3_stays": bool(room >= ROOM),
                     "below_teacher": bool(ceil["open_pass_at_8"] < ceil["open_4I"])}
    (OUT / "scores.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("rule_1", "rule_2")}, indent=1))
    for n, v in tab.items():
        print(n, {k: v[k] for k in ("R", "R_ci", "B", "B_ci", "label_items_number_boxed_pct")})
    print(json.dumps(ceil))


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=check)
    s = sub.add_parser("avg")
    s.add_argument("--arm", choices=AVG, required=True)
    s.set_defaults(fn=avg)
    for name, fn in (("sample", sample), ("queue", queue), ("score", score)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
