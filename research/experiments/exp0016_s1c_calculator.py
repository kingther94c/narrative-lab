"""EXP-0016: S1-c calculator. The distilled 0.8B (EXP-0014's D3) and the 4B, both with a calculator.

Pre-registered in research/registry/experiment_registry.md. Nothing is trained. The calculator
watches decoding: when a model writes written arithmetic followed by ``=`` or ``\\approx``, decoding
stops, the expression is evaluated by an arithmetic-only parser, the value is appended and
decoding resumes. A second, "chained" rule (added on development, for the 4B's layout) fires when a
line opens with a short label and a trigger and the previous line ends in ``= <arithmetic>``. The
same code serves every arm; prompts are unchanged.

  check      parser cases (no model)
  dev        a calculator configuration on the 600 EXP-0007 development items
  devreport  call rates and accuracy on development, against the tool-free runs already on disk
  draw       the test draw from releases EXP-0014 did not use (ids only; counts and a hash)
  test       a configuration on the test draw
  seca       a calculator configuration on section A
  queue      test and section A in the registered order
  score      HC1 to HC3, the error analysis and the reported slices, to scores.json

Configurations: D3-s1, D3-s2 (tool-free), C-s1, C-s2 (D3 with the calculator), 4B (tool-free),
4C (the 4B with the calculator). Test items are read by the program only; nothing here prints
their text.

    conda run --no-capture-output -n py313 python research/experiments/exp0016_s1c_calculator.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0016_s1c_calculator.py dev --config C-s1
    conda run --no-capture-output -n py313 python research/experiments/exp0016_s1c_calculator.py devreport
    conda run --no-capture-output -n py313 python research/experiments/exp0016_s1c_calculator.py draw
    conda run --no-capture-output -n py313 python research/experiments/exp0016_s1c_calculator.py queue
"""

from __future__ import annotations

import argparse
import ast
import collections
import hashlib
import json
import operator
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as E  # noqa: E402

S, V = E.S, E.V
OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0016"
TEST_DRAW = OUT / "test_draw.jsonl"
DEV_DRAW = E.DEV_DRAW
EXP0014_DRAW = E.OUT / "test_draw.jsonl"
TARGET = {"B1": 1500, "B2": 1500}
PER_COMPANY = 3
MAX_CALLS = 8
BOOT, BOOT_SEED = 10_000, 20261121
CONFIGS = ["D3-s1", "D3-s2", "C-s1", "C-s2", "4B", "4C"]
TOOL_FREE_DEV = {  # tool-free development runs already on disk
    "D3-s1": E.OUT / "dev" / "D3-s1-e2.jsonl",
    "D3-s2": E.OUT / "dev" / "D3-s2-e2.jsonl",
    "4B": S.DRIVE / "narrative_lab" / "s1" / "exp0011" / "responses" / "qwen3.5-4b-off.jsonl",
}

# ------------------------------------------------------------------ the calculator

_TOK = (r"\\d?frac|\\times|\\cdot|\\div|\\left|\\right|\\,|\\%|\\\$"
        r"|[0-9.,+\-*/×÷(){}\s$%]")
ARITH_SUFFIX = re.compile(rf"(?:{_TOK})+$")
TRIGGER = re.compile(r"=|\\approx")
FRAC = re.compile(r"\\d?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}")
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def _ev(node):
    if isinstance(node, ast.Expression):
        return _ev(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_ev(node.left), _ev(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _ev(node.operand)
        return -v if isinstance(node.op, ast.USub) else v
    raise ValueError("not arithmetic")


def clean(stretch: str) -> str:
    s = stretch
    while True:
        s2 = FRAC.sub(r"((\1)/(\2))", s)
        if s2 == s:
            break
        s = s2
    for a, b in (("\\times", "*"), ("\\cdot", "*"), ("×", "*"), ("\\div", "/"), ("÷", "/"),
                 ("\\left", ""), ("\\right", ""), ("\\,", ""), ("\\%", ""), ("\\$", ""), ("$", ""),
                 ("%", ""), (",", ""), ("{", "("), ("}", ")")):
        s = s.replace(a, b)
    s = s.strip()
    while s.count("(") > s.count(")") and s.startswith("("):  # "... ($0.90 - $0.64 =" opens before the expression
        s = s[1:].strip()
    return s


def evaluate(stretch: str) -> tuple[str, float] | None:
    """The cleaned expression and its value, or None if it is not arithmetic on two or more numbers."""
    expr = clean(stretch)
    if len(re.findall(r"\d+(?:\.\d+)?|\.\d+", expr)) < 2 or not re.search(r"[\d.)]\s*[-+*/]\s*[-\d.(]", expr):
        return None
    try:
        return expr, _ev(ast.parse(expr, mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError, RecursionError, TypeError):
        return None


def fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


ARITH_ALL = re.compile(rf"(?:{_TOK})+")


def chained(before: str) -> tuple[str, float] | None:
    """A trigger that opens a line after a short label (``$$ \\text{Growth} =``), when the previous line
    ends in ``= <arithmetic>``: the value of that arithmetic. This is how the 4B lays out its working."""
    line_start = before.rfind("\n") + 1
    label = before[line_start:]
    if TRIGGER.search(label) or len(label.strip()) > 80 or line_start == 0:
        return None
    prev = before[:line_start].rstrip()
    prev = prev[prev.rfind("\n") + 1:]
    last = None
    for last in TRIGGER.finditer(prev):
        pass
    if last is None:
        return None
    rhs = re.sub(r"(?:\\\\|\\\]|\\\)|[\s.])+$", "", prev[last.end():])
    if not rhs.strip() or not ARITH_ALL.fullmatch(rhs):
        return None
    return evaluate(rhs)


def find_call(text: str, start: int) -> tuple[int, str, float, str] | None:
    """The first trigger at or after ``start`` with something to evaluate: (end of trigger, expr, value, rule).

    Rule "inline": the written arithmetic right before the trigger. Rule "chained": the trigger follows a
    short label at the start of a line, and the previous line ends in ``= <arithmetic>``."""
    for m in TRIGGER.finditer(text, start):
        before = text[: m.start()]
        suf = ARITH_SUFFIX.search(before)
        if suf:
            stretch = suf.group(0)
            # longest first; if the whole stretch does not parse, start after a line break or a "$"
            starts = [0] + [k for k in range(1, len(stretch)) if stretch[k - 1] in "\n$"]
            for k in starts:
                r = evaluate(stretch[k:])
                if r:
                    return m.end(), r[0], r[1], "inline"
        r = chained(before)
        if r:
            return m.end(), r[0], r[1], "chained"
    return None


def gen_calc(model, tok, prompt: str, cap: int, use_calc: bool) -> dict:
    """Greedy decoding; with ``use_calc``, the calculator appends values. Appended tokens are free."""
    from mlx_lm import stream_generate

    text, n_gen, calls, reason, last_end = "", 0, [], None, 0
    while True:
        scan_from, stopped = max(last_end, len(text) - 8), False
        for r in stream_generate(model, tok, prompt + text, max_tokens=max(1, cap - n_gen)):
            text += r.text
            reason = r.finish_reason
            if use_calc and len(calls) < MAX_CALLS:
                hit = find_call(text, max(0, scan_from))
                if hit:
                    end, expr, value, rule = hit
                    text = text[:end] + " " + fmt(value)
                    last_end = len(text)
                    calls.append({"expr": expr, "value": value, "at": end, "rule": rule})
                    n_gen += r.generation_tokens
                    stopped = True
                    break
        if not stopped:
            n_gen += r.generation_tokens
            break
        if n_gen >= cap:
            reason = "length"
            break
    return {"text": text, "generated_tokens": n_gen, "finish": reason, "calls": calls}


def answer(model, tok, item: dict, instruction: str, cap: int, use_calc: bool) -> dict:
    from learnai.finbench import last_boxed

    prompt = E.prompt_for(tok, item, instruction)
    t0 = time.time()
    g = gen_calc(model, tok, prompt, cap, use_calc)
    out, forced, cont, nf = g["text"], None, "", 0
    if g["finish"] == "length" and last_boxed(out) is None:
        forced = S.CUE
        cont, nf, _ = E.gen(model, tok, prompt + out + forced, S.FORCE_TOKENS)
    return {"id": item["id"], "prompt_tokens": len(tok.encode(prompt)), "generated_tokens": g["generated_tokens"],
            "finish": g["finish"], "calls": g["calls"], "forced": bool(forced), "forced_tokens": nf,
            "response": out + (forced or "") + cont, "seconds": round(time.time() - t0, 2)}


def config(name: str):
    """(model key, weights, instruction, cap, calculator)"""
    if name in ("4B", "4C"):
        return E.TEACHER, None, E.STANDARD, 512, name == "4C"
    arm, seed = name.split("-s")
    best = json.loads((E.OUT / "dev" / "chosen.json").read_text())[f"D3-s{seed}"]
    return E.STUDENT, Path(best), E.TERSE, E.LABEL_CAP, arm == "C"


def run_eval(items: list[dict], path: Path, name: str) -> None:
    import mlx.core as mx

    done = {r["id"] for r in E.jl(path)} if path.exists() else set()
    todo = [i for i in items if i["id"] not in done]
    if not todo:
        return
    key, w, ins, cap, calc = config(name)
    model, tok = E.load_model(key, w)
    for it in todo:
        row = answer(model, tok, it, ins, cap, calc)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        E.append(path, row)


# ------------------------------------------------------------------ parser cases


CASES = [  # (text ending at the trigger, expected value or None)
    ("Calculation: ((234,632 - 187,004) / 187,004) * 100 =", 25.469),
    ("Calculation: (7,777 / 9,828) * 100 =", 79.1311),
    ("$$ 0.1352437 \\times 100 =", 13.5244),
    ("$$151,036 \\div 1,000 =", 151.036),
    ("The change is the 2026 value minus the 2025 value ($0.00 - $0.06 =", -0.06),
    ("$$ \\text{Change} = \\$0.36 - \\$0.10 =", 0.26),
    ("$$ \\text{Change} = -2.66 - 0.43 =", -3.09),
    ("$$ \\frac{1,609.7 - 1,543.4}{1,543.4} \\times 100 \\approx", 4.2957),
    ("$$ \\left( \\frac{50}{200} \\right) \\times 100 \\%  =", 25.0),
    ("To convert from thousands to millions, divide by 1,000.\n    $$5,690,000 / 1,000 =", 5690.0),
    ("$$\n\\frac{2,465}{9,457}\n=", 0.2607),
    ("Row: Total revenues, Column: Three Months Ended September 30, 2026 =", None),
    ("Net income = 1,234 =", None),
    ("x = 5 / 0 =", None),
    ("$$ \\text{Growth} = 1,000 - =", None),
    # chained: the 4B writes "Label = <arithmetic>" and opens the next line with "Label =" or "Label \\approx"
    ("$$ \\text{Change} = (-0.52) - (-0.17) $$\n    $$ \\text{Change} =", -0.35),
    ("$$ \\text{Growth Rate} = \\frac{61,250 - 55,800}{55,800} \\times 100 $$\n    $$ \\text{Growth Rate} \\approx", 9.767),
    ("\\begin{aligned} g &= \\frac{31,500 - 24,000}{24,000} \\times 100 \\\\\n &=", 31.25),
    ("$$ \\text{Change} = \\text{EPS}_{2026} - \\text{EPS}_{2025} $$\n    $$ \\text{Change} =", None),
    ("$$ \\text{Revenue}_{2026} = \\$61,250 \\text{ (in thousands)} $$\n    $$ \\text{Revenue}_{2025} =", None),
    ("$$ x = 3 + 4 = 7 $$\n$$ x =", None),
    ("Growth = (10 - 8) / 8\nSo the growth, written as a long sentence that runs well past the label limit, is =", None),
]


def check(_: argparse.Namespace) -> None:
    bad = 0
    for text, want in CASES:
        hit = find_call(text, text.rfind("\n") + 1)  # the trigger under test is on the last line
        got = None if hit is None else round(hit[2], 4)
        ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) < 1e-4)
        bad += not ok
        print("ok " if ok else "BAD", repr(text[-60:]), "->", None if hit is None else (hit[1], fmt(hit[2])))
    print(f"{len(CASES) - bad} of {len(CASES)} cases pass")
    if bad:
        sys.exit(1)


# ------------------------------------------------------------------ development


def dev(a: argparse.Namespace) -> None:
    S.need_drive()
    items = E.load_ids(DEV_DRAW, V.OUT / "items_dev.jsonl")
    if a.limit:
        items = items[: a.limit]
    run_eval(items, OUT / ("dev_smoke" if a.limit else "dev") / f"{a.config}.jsonl", a.config)


def devreport(_: argparse.Namespace) -> None:
    items = {i["id"]: i for i in E.load_ids(DEV_DRAW, V.OUT / "items_dev.jsonl")}
    out = {}
    for calc, free in (("C-s1", "D3-s1"), ("C-s2", "D3-s2"), ("4C", "4B")):
        p = OUT / "dev" / f"{calc}.jsonl"
        if not p.exists():
            continue
        rows = E.jl(p)
        f = {r["id"]: r for r in E.jl(TOOL_FREE_DEV[free])}
        e = {}
        for sec in ("B1", "B2"):
            rs = [r for r in rows if items[r["id"]]["section"] == sec]
            e[sec] = {"n": len(rs), "with_call": round(100 * sum(bool(r["calls"]) for r in rs) / len(rs), 1),
                      "calls_mean": round(sum(len(r["calls"]) for r in rs) / len(rs), 2),
                      "acc_calc": round(100 * sum(V.grade(items[r["id"]], r["response"], "off")["correct"] for r in rs) / len(rs), 1),
                      "acc_tool_free": round(100 * sum(V.grade(items[r["id"]], f[r["id"]]["response"], "off")["correct"] for r in rs) / len(rs), 1)}
        e["forced"] = sum(r["forced"] for r in rows)
        out[calc] = e
    (OUT / "dev_report.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ test draw


def draw(_: argparse.Namespace) -> None:
    S.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    if TEST_DRAW.exists():
        sys.exit(f"{TEST_DRAW} exists; the draw is made once")
    items = E.jl(E.TEST_ITEMS)
    assert all(i["side"] == "test" and i["post_cutoff"] for i in items)
    used_ids = {r["id"] for r in E.jl(EXP0014_DRAW)}
    used_acc = {i["accession"] for i in items if i["id"] in used_ids}
    pool = [i for i in items if i["accession"] not in used_acc]
    key = lambda r: hashlib.sha256(f"exp0016-test:{r['id']}".encode()).hexdigest()  # noqa: E731
    metrics = {sec: sorted({i["metric"] for i in pool if i["section"] == sec}) for sec in TARGET}
    queues = {(sec, m): sorted((i for i in pool if i["section"] == sec and i["metric"] == m), key=key)
              for sec in TARGET for m in metrics[sec]}
    target = dict(TARGET)
    turn = {sec: 0 for sec in TARGET}
    per_co: collections.Counter = collections.Counter()
    got: collections.Counter = collections.Counter()
    chosen: list[dict] = []
    active = {sec: list(metrics[sec]) for sec in TARGET}
    while any(got[sec] < target[sec] and active[sec] for sec in TARGET):
        for sec in TARGET:
            if got[sec] >= target[sec]:
                continue
            took = False
            while active[sec] and not took:
                m = active[sec][turn[sec] % len(active[sec])]
                q = queues[(sec, m)]
                while q and per_co[q[0]["cik"]] >= PER_COMPANY:
                    q.pop(0)
                if not q:  # metric exhausted: its places go to the others of its section
                    active[sec].remove(m)
                    continue
                r = q.pop(0)
                per_co[r["cik"]] += 1
                got[sec] += 1
                chosen.append(r)
                turn[sec] += 1
                took = True
            if not active[sec] and got[sec] < target[sec]:  # section exhausted: its places go to the other
                other = "B2" if sec == "B1" else "B1"
                target[other] += target[sec] - got[sec]
                target[sec] = got[sec]
    with open(TEST_DRAW, "w", encoding="utf-8") as fh:
        for k, r in enumerate(chosen):
            fh.write(json.dumps({"order": k, "id": r["id"], "template": r["template"], "cik": r["cik"]}) + "\n")
    summary = {"items": len(chosen), "companies": len(per_co), "releases": len({r["accession"] for r in chosen}),
               "by_section": dict(sorted(got.items())),
               "by_template": dict(sorted(collections.Counter(r["template"] for r in chosen).items())),
               "seen": sum(r["template"] in E.SEEN for r in chosen),
               "pool_items": len(pool), "pool_companies": len({i["cik"] for i in pool}),
               "overlap_with_exp0014_releases": len({r["accession"] for r in chosen} & used_acc),
               "sha256_of_ids": hashlib.sha256("\n".join(r["id"] for r in chosen).encode()).hexdigest()}
    (OUT / "test_draw_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


# ------------------------------------------------------------------ test, section A, queue


def test(a: argparse.Namespace) -> None:
    S.need_drive()
    run_eval(E.load_ids(TEST_DRAW, E.TEST_ITEMS), OUT / "test" / f"{a.config}.jsonl", a.config)


def seca(a: argparse.Namespace) -> None:
    import mlx.core as mx
    from learnai.finbench import load_problems

    S.need_drive()
    path = OUT / "seca" / f"{a.config}.jsonl"
    done = {r["uid"] for r in E.jl(path)} if path.exists() else set()
    probs = [p for p in load_problems(E.SECA_N, seed=E.BOOT_SEED) if p.uid not in done]
    if not probs:
        return
    key, w, _, _, calc = config(a.config)
    model, tok = E.load_model(key, w)
    for p in probs:
        prompt = tok.apply_chat_template([{"role": "user", "content": p.prompt}], add_generation_prompt=True,
                                         tokenize=False, enable_thinking=False)
        t0 = time.time()
        g = gen_calc(model, tok, prompt, 512, calc)
        E.append(path, {"uid": p.uid, "generated_tokens": g["generated_tokens"], "finish": g["finish"],
                        "calls": g["calls"], "response": g["text"], "seconds": round(time.time() - t0, 2),
                        "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%H:%M:%S"), *args, flush=True)
        if subprocess.run(me + list(args)).returncode != 0:
            sys.exit(f"step failed: {args}")

    for name in ["D3-s1", "D3-s2", "C-s1", "C-s2", "4B", "4C"]:
        step("test", "--config", name)
    for name in ["C-s1", "C-s2", "4C"]:
        step("seca", "--config", name)
    step("score")


# ------------------------------------------------------------------ score


def _num(s: str) -> list[float]:
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?|\.\d+", s)]


def error_kind(item: dict, g: dict, row: dict) -> str:
    """Why a wrong answer with the calculator is wrong, in the registered order."""
    if not g["valid"]:
        return "no number"
    calls = row.get("calls") or []
    if not calls:
        return "no call on a B2 item" if item["section"] == "B2" else "no call (lookup wrong)"
    ins, gold, tol = calls[-1]["value"], float(item["gold"]), item["tolerance"]["abs"]
    ins_ok = V.grade(item, "\\boxed{" + fmt(ins) + "}", "off")["correct"]
    mags = [abs(ins) * f for f in (1, 100, 0.01, 1e-3, 1e3, 1e-6, 1e6)]
    mag_ok = any(abs(m - abs(gold)) <= tol for m in mags)
    if ins_ok:
        return "copying or rounding"
    if mag_ok:
        return "sign or unit of the box"
    excerpt = set(_num(item["excerpt"]))
    ops = [x for x in _num(calls[-1]["expr"]) if x not in (100.0, 1000.0, 1e6)]
    if any(x not in excerpt for x in ops):
        return "wrong setup: an operand not in the excerpt"
    return "wrong setup: excerpt operands, wrong formula"


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from learnai.finbench import grade as fgrade, problem_for

    items = E.load_ids(TEST_DRAW, E.TEST_ITEMS)
    ids = [i["id"] for i in items]
    by = {i["id"]: i for i in items}
    section = np.array([by[i]["section"] for i in ids])
    seen = np.array([by[i]["template"] in E.SEEN for i in ids])
    metric = np.array([by[i]["metric"] for i in ids])
    cos = sorted({by[i]["cik"] for i in ids})
    co_idx = {c: np.array([k for k, i in enumerate(ids) if by[i]["cik"] == c]) for c in cos}
    rng = np.random.default_rng(BOOT_SEED)
    boot = [np.concatenate([co_idx[cos[j]] for j in rng.integers(0, len(cos), len(cos))]) for _ in range(BOOT)]
    allm = np.ones(len(ids), bool)

    vec, rows, grades = {}, {}, {}
    for name in CONFIGS:
        rows[name] = {r["id"]: r for r in E.jl(OUT / "test" / f"{name}.jsonl")}
        grades[name] = {i: V.grade(by[i], rows[name][i]["response"], "off") for i in ids}
        vec[name] = np.array([float(grades[name][i]["correct"]) for i in ids])
    vec["D3"] = (vec["D3-s1"] + vec["D3-s2"]) / 2
    vec["C"] = (vec["C-s1"] + vec["C-s2"]) / 2

    def stats(d, m=allm):
        bs = np.array([d[b][m[b]].mean() for b in boot])
        return {"value": round(100 * float(d[m].mean()), 2),
                "ci97_5": [round(100 * float(np.percentile(bs, 1.25)), 2), round(100 * float(np.percentile(bs, 98.75)), 2)],
                "p_le_0": round(float(np.mean(bs <= 0)), 5)}

    out: dict = {"test_draw": json.loads((OUT / "test_draw_summary.json").read_text()), "accuracy": {}}
    for name, v in vec.items():
        acc = {"all": allm, "B1": section == "B1", "B2": section == "B2", "seen": seen, "unseen": ~seen}
        acc.update({f"{sec}:{m}": (section == sec) & (metric == m) for sec in ("B1", "B2") for m in sorted(set(metric[section == sec]))})
        out["accuracy"][name] = {k: round(100 * float(v[m].mean()), 1) for k, m in acc.items() if m.any()}
    b2 = section == "B2"
    hc1 = stats(vec["C"] - vec["D3"], b2)
    hc1["supported"] = hc1["value"] >= 5.0 and hc1["p_le_0"] < 0.0125
    hc1["refuted"] = hc1["ci97_5"][1] < 5.0
    hc2 = stats(vec["C"] - vec["4C"])
    hc2["non_inferior"] = hc2["ci97_5"][0] > -3.0
    hc2["refuted"] = hc2["ci97_5"][1] < -3.0
    hc3 = stats((vec["4B"] - vec["D3"]) - (vec["4C"] - vec["C"]))
    hc3["supported"] = hc3["value"] >= 3.0 and hc3["p_le_0"] < 0.0125
    hc3["refuted"] = hc3["ci97_5"][1] < 3.0
    out["HC1"], out["HC2"], out["HC3"] = hc1, hc2, hc3
    out["also"] = {"C-D3 B1": stats(vec["C"] - vec["D3"], section == "B1"),
                   "4C-4B B1": stats(vec["4C"] - vec["4B"], section == "B1"),
                   "4C-4B B2": stats(vec["4C"] - vec["4B"], b2),
                   "C-4C B1": stats(vec["C"] - vec["4C"], section == "B1"),
                   "C-4C B2": stats(vec["C"] - vec["4C"], b2),
                   "C-4B (EXP-0014 H2, tool-free comparator)": stats(vec["C"] - vec["4B"])}
    out["calls"] = {}
    out["forced_invalid"] = {}
    out["errors"] = {}
    for name in CONFIGS:
        rs = rows[name]
        out["forced_invalid"][name] = {"forced": round(100 * float(np.mean([rs[i]["forced"] for i in ids])), 1),
                                       "invalid": round(100 * float(np.mean([not grades[name][i]["valid"] for i in ids])), 1)}
        if name.startswith("C") or name == "4C":
            out["calls"][name] = {sec: {"with_call": round(100 * float(np.mean([bool(rs[i]["calls"]) for i in ids if by[i]["section"] == sec])), 1),
                                        "calls_mean": round(float(np.mean([len(rs[i]["calls"]) for i in ids if by[i]["section"] == sec])), 2)}
                                  for sec in ("B1", "B2")}
            wrong = [i for i in ids if not grades[name][i]["correct"]]
            out["errors"][name] = {sec: dict(collections.Counter(error_kind(by[i], grades[name][i], rs[i])
                                                                 for i in wrong if by[i]["section"] == sec).most_common())
                                   for sec in ("B1", "B2")}
    out["seed_spread"] = {arm: [out["accuracy"][f"{arm}-s{s}"]["all"] for s in E.SEEDS] for arm in ("D3", "C")}
    seca_acc = {}
    for name in ["C-s1", "C-s2", "4C"]:
        p = OUT / "seca" / f"{name}.jsonl"
        if not p.exists():
            continue
        c: dict = collections.defaultdict(list)
        for r in E.jl(p):
            prob = problem_for(r["uid"])
            c[prob.source].append(fgrade(prob, r["response"], thinking=False)["correct"])
        seca_acc[name] = {s: round(100 * sum(v) / len(v), 1) for s, v in c.items()}
    out["section_A"] = seca_acc
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(required=True)
    sub.add_parser("check").set_defaults(fn=check)
    d = sub.add_parser("dev")
    d.add_argument("--config", choices=["C-s1", "C-s2", "4C"], required=True)
    d.add_argument("--limit", type=int, default=0, help="smoke test on the first N items; separate output")
    d.set_defaults(fn=dev)
    sub.add_parser("devreport").set_defaults(fn=devreport)
    sub.add_parser("draw").set_defaults(fn=draw)
    t = sub.add_parser("test")
    t.add_argument("--config", choices=CONFIGS, required=True)
    t.set_defaults(fn=test)
    s = sub.add_parser("seca")
    s.add_argument("--config", choices=["C-s1", "C-s2", "4C"], required=True)
    s.set_defaults(fn=seca)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
