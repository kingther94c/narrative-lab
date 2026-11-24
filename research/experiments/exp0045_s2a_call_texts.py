"""EXP-0045: earnings-call texts in one form, from Alpha Vantage (EXP-0040 to 0044) and IR sites (EXP-0039)

Registry: research/registry/experiment_registry.md, Reserved, EXP-0045 (2026-11-23). No model and no
network. Each target episode with call text gets one document: prepared remarks and the
questions-and-answers part, with source, partial flag, lengths and a token estimate. Outputs stay
on the drive (rule 12). Rebuilt as the daily collection adds transcripts.

    conda run --no-capture-output -n nlab python research/experiments/exp0045_s2a_call_texts.py build
    conda run --no-capture-output -n nlab python research/experiments/exp0045_s2a_call_texts.py check
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import statistics
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0039_s2a_ir_transcripts as e39  # noqa: E402
import exp0040_s2a_av_transcripts as e40  # noqa: E402
import exp0041_s2a_av_transcripts_v2 as e41  # noqa: E402

OUT = e39.DRIVE / "s2" / "exp0045"
DOCS = OUT / "calls"
TARGETS = e40.OUT / "targets_all.jsonl"
CHECKED = e40.OUT / "checked_all.jsonl"
SEED = 20261126
IR_RANK = {"transcript": 0, "prepared_remarks": 1, "cfo_commentary": 2, "letter": 3}

BOILER = re.compile(
    r"copyright ©|©\s*\d{4}|all rights reserved|callstreet\.com|1-877-factset|corrected transcript\s*$|"
    r"lseg streetevents|www\.lseg\.com|republication or redistribution|incommconferencing\.com|"
    r"^\s*page \d+ of \d+\s*$|^\s*\d+\s*$|standardandpoors\.com|ratingsdirect|globalcreditportal",
    re.I)
# phrases removed from inside long lines (some PDFs come out as a few lines of several thousand characters)
BOILER_SUB = re.compile(
    r"copyright ©[^.\n]{0,160}?(llc|inc\.?|reserved\.?)|©\s*\d{4},?\s*lseg\.[^\n]{0,260}?(prohibited without the prior written consent of lseg\.?|reserved\.?)|"
    r"\d-877-factset\s+www\.callstreet\.com|corrected transcript|total pages:\s*\d+|page \d+ of \d+|"
    r"lseg streetevents \| www\.lseg\.com \| contact us|www\.incommconferencing\.com|"
    r"disclaimer\s+the information herein is based on sources.*?subject matter hereof\.?|"
    r"the contents and appearance of this report are copyrighted factset callstreet.*?all rights reserved\.?", re.I)
STRICT_FIRST_Q = re.compile(r"(our |the )?first question (today )?(comes|is|will come|will be) from", re.I)
QA_HEAD_WORDS = {"questionandanswer", "questionandanswersection", "questionandanswersession", "questionsandanswers", "q&a", "q&asession"}
# where the questions start, searched only after the first 15% of the text (openings announce the Q&A too)
FIRST_Q = re.compile(r"(our |the )?first question (today )?(comes|is|will come|will be) from|"
                     r"(begin|open|start|now conduct|now be conducting) (the |a )?question[- ]and[- ]answer (session|portion|period)|"
                     r"we will (now )?(take|begin|open)[^.]{0,40}questions|"
                     r"(ready to|now) take (your )?questions|turn (it|the call) over (to the operator )?for questions|"
                     r"\(operator instructions\)", re.I)


def ir_clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # ligatures such as "ﬁ"
    lines = [ln.rstrip() for ln in text.splitlines()]
    n = len(lines)
    for i in range(int(n * 0.85), n):  # a closing disclaimer block, not the spoken safe harbour
        if re.fullmatch(r"\s*disclaimer\s*", lines[i], re.I):
            lines = lines[:i]
            break
    keep = []
    for ln in lines:
        if len(ln) <= 300:
            if not BOILER.search(ln):
                keep.append(ln)
        else:  # a long line: drop the boilerplate phrases, keep the speech
            keep.append(BOILER_SUB.sub(" ", ln))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(keep)).strip()


def ir_split(text: str) -> tuple[str, str, str]:
    """(prepared, qa, how the split was found)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if i > 5 and re.sub(r"[^a-z&]", "", ln.lower()) in QA_HEAD_WORDS:  # also "Q U E S T I O N S  A N D ..."
            return "\n".join(lines[:i]).strip(), "\n".join(lines[i + 1:]).strip(), "heading"
        m = re.search(r"q\s*u\s*e\s*s\s*t\s*i\s*o\s*n\s*s\s+a\s*n\s*d\s+a\s*n\s*s\s*w\s*e\s*r\s*s", ln, re.I) if len(ln) > 300 else None
        if m:  # a spaced heading inside a long line
            pos = sum(len(x) + 1 for x in lines[:i]) + m.start()
            return text[:pos].strip(), text[pos + len(m[0]):].strip(), "heading"
    m = FIRST_Q.search(text, int(len(text) * 0.15))
    if m:
        start = max(text.rfind("\n", 0, m.start()) + 1, text.rfind(". ", 0, m.start()) + 2 if m.start() - text.rfind(". ", 0, m.start()) < 400 else 0)
        return text[:start].strip(), text[start:].strip(), "first-question line"
    m = STRICT_FIRST_Q.search(text)  # a file that holds the Q&A session only (e.g. Hershey, Snap)
    if m:
        start = text.rfind("\n", 0, m.start()) + 1
        return text[:start].strip(), text[start:].strip(), "first-question line, Q&A-only file"
    return text.strip(), "", "none"


def is_analyst(turn: dict) -> bool:
    return "analyst" in (turn.get("title") or "").lower()


def is_operator(turn: dict) -> bool:
    return "operator" in ((turn.get("title") or "") + " " + (turn.get("speaker") or "")).lower()


def av_doc(d: dict) -> tuple[str, str, dict]:
    turns = d.get("transcript", [])
    first = next((i for i, t in enumerate(turns) if is_analyst(t)), None)
    if first is not None and first > 0 and is_operator(turns[first - 1]):
        first -= 1

    def render(ts):
        return "\n\n".join(f"[{t.get('speaker', '').strip()}, {t.get('title', '').strip()}]: {t.get('content', '').strip()}" for t in ts)

    prep, qa = (turns, []) if first is None else (turns[:first], turns[first:])
    meta = {"turns": len(turns), "analyst_turns": sum(is_analyst(t) for t in turns), "split": "analyst turn" if first is not None else "none"}
    return render(prep), render(qa), meta


def build(_: argparse.Namespace) -> None:
    e40.need_drive()
    DOCS.mkdir(parents=True, exist_ok=True)
    ts = [json.loads(line) for line in open(TARGETS, encoding="utf-8")]
    usable = {(x["cik"], x["av_quarter"]) for x in map(json.loads, open(CHECKED, encoding="utf-8")) if x["usable"]}
    ir: dict[str, dict] = {}
    for line in open(e39.OUT / "extracted.jsonl", encoding="utf-8"):
        x = json.loads(line)
        if x["kind"] not in IR_RANK or x["chars"] <= 2000:
            continue
        cur = ir.get(x["cik"])
        if cur is None or IR_RANK[x["kind"]] < IR_RANK[cur["kind"]]:
            ir[x["cik"]] = x
    rows = []
    for r in ts:
        clean = r["stage"] in ("validation", "no_ir", "ir")
        doc = None
        if (r["cik"], r["av_quarter"]) in usable:
            d = json.loads(e41.raw_for(r["cik"], r["av_quarter"]).read_text(encoding="utf-8"))
            prep, qa, meta = av_doc(d)
            doc = {"source": "alpha_vantage", "kind": "transcript", "partial": False, **meta}
        elif clean and r["cik"] in ir and (r.get("ir_file") or ir[r["cik"]]["kind"] != "transcript"):
            x = ir[r["cik"]]
            text = ir_clean((e39.TEXTS / (Path(x["file"]).stem + ".txt")).read_text(encoding="utf-8"))
            prep, qa, how = ir_split(text) if x["kind"] == "transcript" else (text, "", "not a transcript")
            doc = {"source": "ir_site", "kind": x["kind"], "partial": x["kind"] != "transcript", "split": how,
                   "producer": x.get("producer")}
        if doc is None:
            continue
        stage = "clean" if clean else r["stage"]
        name = f"{r['episode']}.txt"
        (DOCS / name).write_text("PREPARED REMARKS\n\n" + prep + ("\n\nQUESTIONS AND ANSWERS\n\n" + qa if qa else ""), encoding="utf-8")
        rows.append({"episode": r["episode"], "stage": stage, "cik": r["cik"], "symbol": r["symbol"], "rank": r["rank"],
                     "release_date": r["release_date"], "quarter_end": r["quarter_end"], "file": name, **doc,
                     "prepared_chars": len(prep), "qa_chars": len(qa), "qa_found": bool(qa),
                     "approx_tokens": (len(prep) + len(qa)) // 4})
    (OUT / "calls.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    print(f"[build] {len(rows)} documents: " + json.dumps(dict(collections.Counter((x["stage"], x["source"], x["kind"]) for x in rows).most_common()).__repr__()))


def check(_: argparse.Namespace) -> None:
    e40.need_drive()
    rows = [json.loads(line) for line in open(OUT / "calls.jsonl", encoding="utf-8")]
    left = collections.Counter()
    for x in rows:
        text = (DOCS / x["file"]).read_text(encoding="utf-8")
        left[x["source"]] += len(re.findall(r"copyright|all rights reserved|callstreet\.com|lseg\.com", text, re.I))
    rep = {"documents": len(rows), "by_stage_source": {f"{a} / {b}": n for (a, b), n in collections.Counter((x["stage"], x["source"]) for x in rows).items()},
           "partial": sum(x["partial"] for x in rows),
           "qa_found_share_full": round(sum(x["qa_found"] for x in rows if not x["partial"]) / max(1, sum(not x["partial"] for x in rows)), 3),
           "no_qa_full": [(x["symbol"], x["source"], x.get("split")) for x in rows if not x["partial"] and not x["qa_found"]],
           "tokens_median": statistics.median(x["approx_tokens"] for x in rows) if rows else None,
           "tokens_max": max((x["approx_tokens"] for x in rows), default=None),
           "boilerplate_left": dict(left),
           "clean_episodes_with_full_call": sum(1 for x in rows if x["stage"] == "clean" and not x["partial"]),
           "next_episodes_with_full_call": sum(1 for x in rows if x["stage"] == "next" and not x["partial"])}
    (OUT / "summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))
    for x in random.Random(SEED).sample(rows, min(10, len(rows))):
        text = (DOCS / x["file"]).read_text(encoding="utf-8")
        i = text.find("QUESTIONS AND ANSWERS")
        print(f"\n--- {x['symbol']} {x['source']} {x['kind']} split={x.get('split')} prep={x['prepared_chars']} qa={x['qa_chars']}")
        print("  opening:", re.sub(r"\s+", " ", text[17:260]))
        if i >= 0:
            print("  qa starts:", re.sub(r"\s+", " ", text[i + 23:i + 260]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=build)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
