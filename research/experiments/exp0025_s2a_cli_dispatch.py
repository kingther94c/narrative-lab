"""EXP-0025: a headless backend for sub-study S2's model calls, and its agreement check.

Changelog 2026-11-21 (AGENTS.md rule 7). EXP-0023 carries calls through the session; this script
carries the same outbox through the Claude Code command line instead, one fresh process per
call, with no tool offered and nothing passing through the session:

    claude -p --agent <definition> --tools "" --strict-mcp-config --no-session-persistence
           --output-format json          (prompt on standard input)

1. ``run``: answers the unanswered calls of an EXP-0023 run directory, at most three at a time
   (rule 19), and writes the raw reply and usage to its inbox in EXP-0023's format, plus the full
   JSON of the command line to ``cli/``. EXP-0023's ``ingest`` then applies the same canary check.
2. ``agree-prepare``: draws 20 of EXP-0024's 210 closed-book prompts by seed, under new ids.
3. ``agree-score``: compares the headless answers with EXP-0024's in-session answers to the same
   prompts. An engineering check with no hypothesis: do the two transports give the same model?

    conda run --no-capture-output -n nlab python research/experiments/exp0025_s2a_cli_dispatch.py agree-prepare
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run exp0025_agree --items <items>
    conda run --no-capture-output -n nlab python research/experiments/exp0025_s2a_cli_dispatch.py run --run exp0025_agree
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run exp0025_agree
    conda run --no-capture-output -n nlab python research/experiments/exp0025_s2a_cli_dispatch.py agree-score
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0024_s2b_recall_probe as e24  # noqa: E402

CLAUDE = Path.home() / ".local" / "bin" / "claude"
REPO = Path(__file__).resolve().parents[2]
OUT = e23.DRIVE / "s2" / "exp0025"
SEED = 20261121
WORKERS = 3
TIMEOUT = 600
AGREE_RUN, BASE_RUN, AGREE_N = "exp0025_agree", "exp0024_opus", 20


def one(d: Path, c: dict) -> str:
    cmd = [str(CLAUDE), "-p", "--agent", c["agent"], "--tools", "", "--strict-mcp-config",
           "--no-session-persistence", "--output-format", "json"]
    try:
        p = subprocess.run(cmd, input=c["prompt"], capture_output=True, text=True, timeout=TIMEOUT, cwd=REPO)
        j = json.loads(p.stdout)
    except Exception as err:  # the call stays unanswered and is tried again on the next run
        return f"{c['id']} error: {type(err).__name__}: {str(err)[:100]}"
    (d / "cli").mkdir(exist_ok=True)
    (d / "cli" / f"{c['id']}.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")
    if j.get("is_error") or not isinstance(j.get("result"), str):
        return f"{c['id']} error: {str(j.get('result'))[:100]}"
    u = j.get("usage") or {}
    tokens = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))
    served = sorted((j.get("modelUsage") or {}).keys())
    # No tool is offered; a tool use would also need a second turn.
    usage = {"subagent_tokens": tokens, "tool_uses": (j.get("num_turns") or 1) - 1, "duration_ms": j.get("duration_ms"),
             "transport": "cli", "models": served}
    (d / "inbox" / f"{c['id']}.usage.json").write_text(json.dumps(usage), encoding="utf-8")
    (d / "inbox" / f"{c['id']}.txt").write_text(j["result"], encoding="utf-8")
    return f"{c['id']} ok {tokens}"


def run(a: argparse.Namespace) -> None:
    e23.need_drive()
    d = e23.run_dir(a.run)
    todo = [c for c in e23.calls(d) if not (d / "inbox" / f"{c['id']}.txt").exists()][: a.n]
    print(f"[run] {len(todo)} calls", flush=True)
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for i, msg in enumerate(ex.map(lambda c: one(d, c), todo), 1):
            if "error" in msg or i % 20 == 0 or i == len(todo):
                print(f"[run] {i}/{len(todo)} {msg}", flush=True)


def agree_prepare(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    items = [json.loads(l) for l in (e24.OUT / "items.jsonl").read_text(encoding="utf-8").splitlines() if l]
    chosen = sorted(random.Random(SEED).sample(items, AGREE_N), key=lambda it: it["id"])
    with open(OUT / "agree_items.jsonl", "w", encoding="utf-8") as fh:
        for it in chosen:
            fh.write(json.dumps({"id": "c" + it["id"], "agent": it["agent"], "prompt": it["prompt"]}, ensure_ascii=False) + "\n")
    print(f"[agree-prepare] {len(chosen)} items -> {OUT / 'agree_items.jsonl'}")


def agree_score(_: argparse.Namespace) -> None:
    base = {r["id"]: e24.parse(r["reply"]) for r in e23.records(e23.ROOT / BASE_RUN) if r["canary_ok"]}
    new = [r for r in e23.records(e23.ROOT / AGREE_RUN) if r["canary_ok"]]
    rows = []
    for r in new:
        b, n = base.get(r["id"][1:].split(".")[0]), e24.parse(r["reply"])
        if b:
            rows.append({"id": r["id"], "dir_cli": n["direction"], "dir_session": b["direction"],
                         "g_cli": n["growth"], "g_session": b["growth"]})
    both = [x for x in rows if x["g_cli"] is not None and x["g_session"] is not None]
    rep = {"pairs": len(rows), "canary_failures": sum(1 for r in e23.records(e23.ROOT / AGREE_RUN) if not r["canary_ok"]),
           "direction_agree": sum(x["dir_cli"] == x["dir_session"] for x in rows),
           "both_gave_growth": len(both),
           "median_abs_growth_gap": round(statistics.median(abs(x["g_cli"] - x["g_session"]) for x in both), 2) if both else None,
           "disagreements": [x for x in rows if x["dir_cli"] != x["dir_session"]]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "agree.json").write_text(json.dumps({**rep, "rows": rows}, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run", required=True)
    r.add_argument("-n", type=int, default=10**9)
    r.set_defaults(fn=run)
    sub.add_parser("agree-prepare").set_defaults(fn=agree_prepare)
    sub.add_parser("agree-score").set_defaults(fn=agree_score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
