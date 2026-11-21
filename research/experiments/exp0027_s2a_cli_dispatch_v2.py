"""EXP-0027: the headless backend of EXP-0025, fixed forward to keep the session's context out.

EXP-0025 ran `claude -p` inside the repository. On 2026-11-21 the first calls of EXP-0026 came
back in Chinese: the project's auto-memory index (which holds the owner's name and "Chinese
replies") had reached the model under evaluation, and so had the repository's CLAUDE.md, although
the definitions say `omitClaudeMd`. This version runs each call from an empty directory outside
the repository, passes the agent definition inline (`--agents`), reads no settings
(`--setting-sources ""`) and switches auto-memory off. Checked by asking the model to quote its
context: what remains is attached by the harness and cannot be removed without an API key: one
fixed sentence of the Agent SDK before the definition's prompt, the account's e-mail address,
today's date, "Assistant knowledge cutoff is June 2026", and the working-directory path.
Everything else is EXP-0025's `run`. A first form of this script (`--setting-sources project`
only) made five calls, all voided, before this one.

    conda run --no-capture-output -n nlab python research/experiments/exp0027_s2a_cli_dispatch_v2.py run --run NAME
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0025_s2a_cli_dispatch as e25  # noqa: E402

FLAGS = ["--tools", "", "--strict-mcp-config", "--no-session-persistence", "--setting-sources", "",
         "--output-format", "json"]
CWD = Path.home() / ".cache" / "empty_cwd"
ENV = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}


def definition(agent: str) -> str:
    """The agent definition file as the JSON `--agents` takes."""
    _, front, body = (e25.REPO / ".claude" / "agents" / f"{agent}.md").read_text(encoding="utf-8").split("---", 2)
    m = dict(l.split(": ", 1) for l in front.strip().splitlines())
    return json.dumps({m["name"]: {"description": m["description"], "prompt": body.strip(), "model": m["model"], "effort": m["effort"]}})


def one(d: Path, c: dict) -> str:
    cmd = [str(e25.CLAUDE), "-p", "--agents", definition(c["agent"]), "--agent", c["agent"], *FLAGS]
    try:
        CWD.mkdir(parents=True, exist_ok=True)
        p = subprocess.run(cmd, input=c["prompt"], capture_output=True, text=True, timeout=e25.TIMEOUT, cwd=CWD, env=ENV)
        j = json.loads(p.stdout)
    except Exception as err:  # the call stays unanswered and is tried again on the next run
        return f"{c['id']} error: {type(err).__name__}: {str(err)[:100]}"
    (d / "cli").mkdir(exist_ok=True)
    (d / "cli" / f"{c['id']}.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")
    if j.get("is_error") or not isinstance(j.get("result"), str):
        return f"{c['id']} error: {str(j.get('result'))[:100]}"
    u = j.get("usage") or {}
    tokens = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))
    usage = {"subagent_tokens": tokens, "tool_uses": (j.get("num_turns") or 1) - 1, "duration_ms": j.get("duration_ms"),
             "transport": "cli-v2-isolated", "models": sorted((j.get("modelUsage") or {}).keys())}
    (d / "inbox" / f"{c['id']}.usage.json").write_text(json.dumps(usage), encoding="utf-8")
    (d / "inbox" / f"{c['id']}.txt").write_text(j["result"], encoding="utf-8")
    return f"{c['id']} ok {tokens}"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run", required=True)
    r.add_argument("-n", type=int, default=10**9)
    a = p.parse_args()
    e25.one = one  # EXP-0025's run loop, this version's call
    e25.run(a)


if __name__ == "__main__":
    main()
