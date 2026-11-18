"""EXP-0011: S1-b rerun on EarningsExam v0.2, thinking off, with a 512-token cap.

EXP-0007 (frozen) measured the S1 ladder on v0.1 and found the sign of negative answers
unasked and misread, and a third of thinking-off answers cut off at its 256-token cap. This
rerun changes exactly three things, by the owner's decisions of 2026-11-18:

* items are the same 600 ids, in the same order, taken from v0.2 (EXP-0010): every question
  asks for a minus sign on a negative value;
* answers are graded with ``exp0010.grade``: a parenthesised figure reads as negative;
* thinking off only, at most 512 generated tokens (EXP-0007: 256). Thinking on is not rerun.

Prompt, models, decoding, forced answer, intervals and criteria are EXP-0007's, run by its code.
Pre-registered in research/registry/experiment_registry.md.

    conda run --no-capture-output -n py313 python research/experiments/exp0011_s1b_headroom_v0_2.py prepare
    conda run --no-capture-output -n py313 python research/experiments/exp0011_s1b_headroom_v0_2.py run --model qwen3.5-4b --limit 3
    conda run --no-capture-output -n py313 python research/experiments/exp0011_s1b_headroom_v0_2.py queue
    conda run --no-capture-output -n py313 python research/experiments/exp0011_s1b_headroom_v0_2.py score

Only development items are read; test items are never opened.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0007_s1b_headroom as S  # noqa: E402
import exp0010_earnings_exam_v0_2 as V  # noqa: E402

PREV = S.OUT  # EXP-0007's outputs, read for the draw and the comparison
S.ITEMS = V.OUT / "items_dev.jsonl"
S.OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0011"
S.DRAW = S.OUT / "draw.jsonl"
S.CAP = {"off": 512, "on": 2_048}
S.QUEUE = [(m, "off") for m in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b", "olmoe-1b-7b")]
_old_grade = S.grade
S.grade = V.grade


def prepare(_: argparse.Namespace) -> None:
    """Copy EXP-0007's draw, and confirm every id is in v0.2 with the gold unchanged."""
    S.need_drive()
    if S.DRAW.exists():
        sys.exit(f"{S.DRAW} exists")
    shutil.copy(PREV / "draw.jsonl", S.DRAW)
    shutil.copy(PREV / "draw_summary.json", S.OUT / "draw_summary.json")
    new = S.load_draw()
    S.ITEMS, keep = V.SRC / "items_dev.jsonl", S.ITEMS
    old = S.load_draw()
    S.ITEMS = keep
    assert [i["id"] for i in new] == [i["id"] for i in old]
    assert all(a["gold"] == b["gold"] and a["excerpt"] == b["excerpt"] for a, b in zip(new, old))
    assert all(i["question"].endswith(V.SIGN) for i in new)
    print(f"draw copied: {len(new)} items, ids and gold equal to EXP-0007, every question asks for the sign")


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    for key, mode in S.QUEUE:
        path = S.responses_path(key, mode)
        n_done = len(path.read_text().splitlines()) if path.exists() else 0
        if n_done >= sum(S.QUOTA.values()):
            continue
        print(f"{time.strftime('%H:%M:%S')} {key} {mode}: {n_done} done", flush=True)
        subprocess.run([sys.executable, __file__, "run", "--model", key, "--mode", mode], check=False)


def score(a: argparse.Namespace) -> None:
    """EXP-0007's score, then answer lengths at 256 tokens and the change from EXP-0007."""
    import numpy as np

    S.score(a)
    path = S.OUT / "scores.json"
    out = json.loads(path.read_text())
    items = {it["id"]: it for it in S.load_draw()}
    extra = {}
    for key, mode in S.QUEUE:
        new = [json.loads(l) for l in S.responses_path(key, mode).read_text().splitlines()]
        g = {r["id"]: (V.grade(items[r["id"]], r["response"], mode), r) for r in new}
        right = [r["generated_tokens"] for x, r in g.values() if x["correct"]]
        old_rows = [json.loads(l) for l in (PREV / "responses" / f"{key}-{mode}.jsonl").read_text().splitlines()]
        old = {r["id"]: _old_grade(items[r["id"]], r["response"], mode)["correct"] for r in old_rows}
        delta = {}
        for sec in ("B1", "B2"):
            ids = [i for i in items if items[i]["section"] == sec]
            delta[sec] = round(100 * (np.mean([g[i][0]["correct"] for i in ids]) - np.mean([old[i] for i in ids])), 1)
        neg = [i for i in items if float(items[i]["gold"]) < 0]
        extra[f"{key}/{mode}"] = {
            "correct_within": {b: round(100 * float(np.mean([t <= b for t in right])), 1) for b in (64, 128, 256)} if right else None,
            "accuracy_change_from_exp0007": delta,
            "negative_gold_acc": round(100 * float(np.mean([g[i][0]["correct"] for i in neg])), 1),
        }
    out["exp0011"] = extra
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(extra, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(fn=prepare)
    r = sub.add_parser("run")
    r.add_argument("--model", choices=list(S.MODELS), required=True)
    r.add_argument("--mode", choices=("off",), default="off")
    r.add_argument("--limit", type=int, default=0, help="smoke test on N pre-cutoff items; separate output")
    r.set_defaults(fn=S.run)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
