"""EXP-0044: Alpha Vantage call transcripts, EXP-0043 with the key scrubbed from the ledger (S2-a)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0044 (2026-11-23). Alpha Vantage's
limit message quotes the API key, and EXP-0043 logs that message. This wrapper runs EXP-0043's
fetch and scrubs the key from the ledger before and after; targets and check are EXP-0043's.

    conda run --no-capture-output -n nlab python research/experiments/exp0044_s2a_av_transcripts_redact.py fetch --max 25
    conda run --no-capture-output -n nlab python research/experiments/exp0044_s2a_av_transcripts_redact.py check
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0043_s2a_av_transcripts_all as e43  # noqa: E402


def scrub() -> int:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    p = e40.OUT / "ledger.jsonl"
    if not key or not p.exists():
        return 0
    s = p.read_text(encoding="utf-8")
    n = s.count(key)
    if n:
        p.write_text(s.replace(key, "***"), encoding="utf-8")
    return n


def fetch(a: argparse.Namespace) -> None:
    scrub()
    try:
        e43.fetch(a)
    finally:
        n = scrub()
        if n:
            print(f"[fetch] key scrubbed from {n} ledger line(s)", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--max", type=int, default=e40.DAILY)
    f.set_defaults(fn=fetch)
    sub.add_parser("check").set_defaults(fn=e43.check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
