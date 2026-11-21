"""EXP-0023: the transport for sub-study S2's subagent calls (step S2-a).

Design: docs/plans/2026-11-20_substudy_s2_plan.md, §11 (`s2a_dispatch`). An engineering tool with
no hypothesis. Commercial models are called only as fresh no-tool subagents, one item per call
(AGENTS.md rule 7). A script cannot start a subagent, so the session carries each call:

1. ``emit``: reads an items file written by an experiment's ``prepare`` step (id, agent, prompt;
   never a label or a key) and writes one JSON per call to ``outbox/``, with a canary: the prompt
   ends by asking for a last line ``ITEM <code>``.
2. ``pending``: prints the next calls not yet answered, prompt verbatim, for the session to pass
   to the named agent. At most three are in flight at once (rule 19).
3. The session writes each raw reply to ``inbox/<id>.txt`` and the harness's usage figures
   (subagent tokens, tool uses, duration) to ``inbox/<id>.usage.json``.
4. ``ingest``: checks the canary and that the call used no tool, and appends ``record.jsonl``. A
   reply that fails either check is kept and its call is emitted again under a new id. The
   definitions disallow every tool by name, but on 2026-11-20 the subagents still reported some
   harness tools (artifacts, plugin search, messaging), so the per-call count is the evidence.
5. ``check`` and ``usage``: counts, canary failures, tokens and time per agent.

    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run NAME --items FILE
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py pending --run NAME -n 3
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run NAME
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py check --run NAME
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py usage --run NAME
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
ROOT = DRIVE / "s2" / "dispatch"
AGENTS = {"s2-recall-claude-opus-5-5", "s2-recall-claude-sonnet-5-5", "roster-claude-opus-5-5", "roster-claude-sonnet-5-5"}
CANARY = "\n\nEnd your reply with one more line, exactly: ITEM {code}"


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")


def run_dir(name: str) -> Path:
    if not re.fullmatch(r"[a-z0-9_\-]+", name):
        sys.exit("run names are lower-case letters, digits, - and _")
    d = ROOT / name
    (d / "outbox").mkdir(parents=True, exist_ok=True)
    (d / "inbox").mkdir(parents=True, exist_ok=True)
    return d


def code_for(item_id: str) -> str:
    return hashlib.sha256(item_id.encode()).hexdigest()[:8].upper()


def emit(a: argparse.Namespace) -> None:
    need_drive()
    d = run_dir(a.run)
    n = 0
    for line in Path(a.items).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if set(it) - {"id", "agent", "prompt"}:
            sys.exit(f"an item carries more than id, agent and prompt: {sorted(set(it))}")
        if it["agent"] not in AGENTS:
            sys.exit(f"unknown agent {it['agent']}")
        path = d / "outbox" / f"{it['id']}.json"
        if path.exists():
            continue
        code = code_for(it["id"])
        call = {"id": it["id"], "agent": it["agent"], "prompt": it["prompt"] + CANARY.format(code=code),
                "canary": code, "emitted": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        path.write_text(json.dumps(call, ensure_ascii=False), encoding="utf-8")
        n += 1
    print(f"[emit] {n} new calls in {d / 'outbox'}")


def calls(d: Path) -> list[dict]:
    return sorted((json.loads(p.read_text(encoding="utf-8")) for p in (d / "outbox").glob("*.json")), key=lambda c: c["id"])


def pending(a: argparse.Namespace) -> None:
    d = run_dir(a.run)
    todo = [c for c in calls(d) if not (d / "inbox" / f"{c['id']}.txt").exists()]
    print(f"[pending] {len(todo)} calls without a reply")
    for c in todo[: a.n]:
        print(f"\n=== {c['id']} -> {c['agent']}\n{c['prompt']}\n=== end {c['id']}")


def ingest(a: argparse.Namespace) -> None:
    d = run_dir(a.run)
    rec_path = d / "record.jsonl"
    done = set()
    if rec_path.exists():
        done = {json.loads(l)["id"] for l in rec_path.read_text(encoding="utf-8").splitlines() if l}
    new, bad = 0, 0
    with open(rec_path, "a", encoding="utf-8") as fh:
        for c in calls(d):
            rp = d / "inbox" / f"{c['id']}.txt"
            if c["id"] in done or not rp.exists():
                continue
            reply = rp.read_text(encoding="utf-8")
            up = d / "inbox" / f"{c['id']}.usage.json"
            usage = json.loads(up.read_text(encoding="utf-8")) if up.exists() else None
            last = [l.strip() for l in reply.strip().splitlines()][-1:] or [""]
            # A call counts only if its canary came back and the harness reports that no tool was
            # used: the definitions' "no tools" is enforced per call, not taken on trust.
            ok = last[0] == f"ITEM {c['canary']}" and bool(usage) and usage.get("tool_uses") == 0
            fh.write(json.dumps({"id": c["id"], "agent": c["agent"], "reply": reply, "usage": usage,
                                 "canary_ok": ok, "ingested": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")},
                                ensure_ascii=False) + "\n")
            new += 1
            if not ok:
                bad += 1
                k = 1
                while (d / "outbox" / f"{c['id']}.r{k}.json").exists():
                    k += 1
                rid = f"{c['id']}.r{k}"
                prompt = c["prompt"].rsplit(CANARY.format(code=c["canary"]), 1)[0]
                code = code_for(rid)
                (d / "outbox" / f"{rid}.json").write_text(json.dumps(
                    {"id": rid, "agent": c["agent"], "prompt": prompt + CANARY.format(code=code), "canary": code,
                     "emitted": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "retry_of": c["id"]},
                    ensure_ascii=False), encoding="utf-8")
    print(f"[ingest] {new} replies recorded, {bad} without their canary (emitted again)")


def records(d: Path) -> list[dict]:
    p = d / "record.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l] if p.exists() else []


def check(a: argparse.Namespace) -> None:
    d = run_dir(a.run)
    cs, rs = calls(d), records(d)
    ids = [r["id"] for r in rs]
    report = {"calls": len(cs), "recorded": len(rs), "unanswered": sum(1 for c in cs if c["id"] not in set(ids)),
              "duplicate_records": len(ids) - len(set(ids)), "canary_failures": sum(1 for r in rs if not r["canary_ok"]),
              "missing_usage": sum(1 for r in rs if not r["usage"]),
              "by_agent": dict(collections.Counter(c["agent"] for c in cs))}
    print(json.dumps(report, indent=2))


def usage(a: argparse.Namespace) -> None:
    d = run_dir(a.run)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in records(d):
        for k, v in (r["usage"] or {}).items():
            if isinstance(v, (int, float)):
                by[r["agent"]][k].append(v)
    out = {ag: {k: {"n": len(v), "mean": round(statistics.mean(v), 1), "total": sum(v)} for k, v in m.items()} for ag, m in by.items()}
    print(json.dumps(out, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit")
    e.add_argument("--run", required=True)
    e.add_argument("--items", required=True)
    e.set_defaults(fn=emit)
    q = sub.add_parser("pending")
    q.add_argument("--run", required=True)
    q.add_argument("-n", type=int, default=3)
    q.set_defaults(fn=pending)
    for name, fn in (("ingest", ingest), ("check", check), ("usage", usage)):
        s = sub.add_parser(name)
        s.add_argument("--run", required=True)
        s.set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
