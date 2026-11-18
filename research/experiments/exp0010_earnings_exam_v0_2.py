"""EXP-0010: EarningsExam v0.2, v0.1 with the sign asked for and accounting negatives read.

EXP-0007 (S1-b on v0.1) found that 178 of its 600 golds were negative, that only the EPS-change
question told the model to use a minus sign, and that a dropped sign was the largest single error
for the 4B and the 9B. The grader, ``learnai.finbench.parse_number``, also read an accounting
negative such as ``(1,234)`` or ``-(5.6)`` as positive (EXP-0009). Owner's decisions, 2026-11-18:

* every question, of every template and both phrasings, ends with the same sentence
  ``Use a minus sign for a negative value (a loss or a decrease).`` The sentence is the same
  whatever the sign of the gold, so it gives nothing away. EPS change loses its own
  ``; use a minus sign for a decrease`` clause, which the new sentence replaces;
* a boxed number wrapped in parentheses, with or without a leading minus sign, is read as negative
  (``read_number`` below; S1 scripts grade with ``grade`` from this file).

Nothing else changes: ids, excerpts, gold, tolerance, splits and templates are v0.1's. v0.2 is
made from the v0.1 item files, not rebuilt from the releases, so it cannot drift from them.
Test items are rewritten by the program without being shown; ``audit`` prints counts only.

    conda run --no-capture-output -n py313 python research/experiments/exp0010_earnings_exam_v0_2.py build
    conda run --no-capture-output -n py313 python research/experiments/exp0010_earnings_exam_v0_2.py audit
    conda run --no-capture-output -n py313 python research/experiments/exp0010_earnings_exam_v0_2.py check
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
SRC = DRIVE / "s1" / "exam_v0_1"
OUT = DRIVE / "s1" / "exam_v0_2"
SIDES = ("train", "dev", "test")
SIGN = "Use a minus sign for a negative value (a loss or a decrease)."
OLD_EPS_CLAUSE = "; use a minus sign for a decrease."

# "(1,234)", "-(5.6)", "\$(0.16)", "\left( 3.2 \right)", "(4.1\%)": a parenthesised figure.
PAREN = re.compile(r"^\s*-?\s*(?:\\?\$\s*)?(?:\\left)?\s*\(\s*(?P<body>[^()]*?)\s*(?:\\right)?\s*\)\s*(?P<tail>.*)$", re.S)


def rewrite(question: str) -> str:
    q = question.replace(OLD_EPS_CLAUSE, ".")
    assert q.endswith("."), q[-60:]
    assert SIGN not in q
    return f"{q} {SIGN}"


def read_number(boxed: str) -> float | None:
    """The number in a boxed answer, with a parenthesised figure read as negative."""
    from learnai.finbench import parse_number

    m = PAREN.match(boxed)
    if m:
        parsed = parse_number(m["body"] + " " + m["tail"])
        return -abs(parsed[0]) if parsed else None
    parsed = parse_number(boxed)
    return parsed[0] if parsed else None


def grade(item: dict, response: str, mode: str) -> dict:
    """EXP-0007's grade with ``read_number`` in place of ``parse_number``."""
    from learnai.finbench import last_boxed, split_thinking

    reasoning, answer = split_thinking(response, thinking=(mode == "on"))
    boxed = last_boxed(answer if answer is not None else reasoning)
    value = read_number(boxed) if boxed is not None else None
    correct = value is not None and abs(value - float(item["gold"])) <= item["tolerance"]["abs"]
    return {"boxed": boxed, "value": value, "valid": value is not None, "correct": bool(correct)}


def build(_: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for side in SIDES:
        n, digest = 0, hashlib.sha256()
        with open(SRC / f"items_{side}.jsonl", encoding="utf-8") as fin, \
             open(OUT / f"items_{side}.jsonl", "w", encoding="utf-8") as fout:
            for line in fin:
                it = json.loads(line)
                it["question"] = rewrite(it["question"])
                it["exam_version"] = "v0.2"
                fout.write(json.dumps(it) + "\n")
                digest.update(it["id"].encode())
                n += 1
        report[side] = {"items": n, "sha256_of_ids": digest.hexdigest()}
    (OUT / "build.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


def audit(_: argparse.Namespace) -> None:
    """Counts only: every question ends with the sign sentence, ids match v0.1, gold untouched."""
    out = {}
    for side in SIDES:
        old = {json.loads(l)["id"]: json.loads(l) for l in open(SRC / f"items_{side}.jsonl", encoding="utf-8")}
        new = [json.loads(l) for l in open(OUT / f"items_{side}.jsonl", encoding="utf-8")]
        c: collections.Counter = collections.Counter()
        for it in new:
            o = old[it["id"]]
            c["items"] += 1
            c["ends with sign sentence"] += it["question"].endswith(SIGN)
            c["sign sentence once"] += it["question"].count("minus sign") == 1
            c["only question changed"] += all(it[k] == o[k] for k in o if k != "question")
            c["negative gold"] += float(it["gold"]) < 0
        c["ids equal v0.1"] = int({it["id"] for it in new} == set(old))
        out[side] = dict(c)
    print(json.dumps(out, indent=1))


def check(_: argparse.Namespace) -> None:
    """The parser on fixed cases, and three rewritten development questions."""
    cases = {"(1,234)": -1234.0, "-(5.6)": -5.6, "\\$(0.16)": -0.16, "\\left( 3.2 \\right)": -3.2,
             "(4.1\\%)": -4.1, "-1,234": -1234.0, "1,234": 1234.0, "\\$1,234.5": 1234.5,
             "−0.16": -0.16, "-4.1\\%": -4.1, "12.3 million": 12.3, "\\frac{94}{5735}": 94 / 5735,
             "n/a": None}
    bad = {k: (read_number(k), v) for k, v in cases.items()
           if not (read_number(k) == v or (v is not None and read_number(k) is not None and abs(read_number(k) - v) < 1e-9))}
    print("parser cases:", len(cases), "failures:", bad)
    seen = set()
    for line in open(OUT / "items_dev.jsonl", encoding="utf-8"):
        it = json.loads(line)
        t = it["template"].split(":")[1]
        if t in seen:
            continue
        seen.add(t)
        print(f"{it['template']:<26} ...{it['question'][-150:]}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(required=True)
    for name, fn in (("build", build), ("audit", audit), ("check", check)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
