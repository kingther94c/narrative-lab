# narrative-lab: house rules

One file, so Claude and any other coding agent read the same thing. `CLAUDE.md` points here.

## 1. Start of every session

Read [`research/registry/01_roadmap.md`](research/registry/01_roadmap.md). It says which phase is
open, which work packages are in flight, and which decisions are waiting on the owner.

## 2. Where things live

| What | Where |
|---|---|
| The owner's proposal, one file per version | `docs/proposal/` |
| Plans as the owner approved them, verbatim | `docs/plans/` |
| Roadmap, methodology, experiments, graveyard, feature evidence, changelog | `research/registry/` |
| Paper notes, evidence matrix, gap analysis | `research/literature/` |
| Data audit, feasibility numbers, labelling codebook, research design | `research/design/` |
| Hash manifests of sealed forecasts | `research/ledger/` |
| Experiment scripts (`expNNNN_*.py`), frozen once run | `research/experiments/` |
| Corpus, gold labels, sealed forecast contents, run outputs, adapters | `/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab/`, outside git, created on first use |
| Model checkpoints | `/Volumes/Seagate Backup Plus Drive/DATA/huggingface`, shared with `learning_ai` |

## 3. Standing rules

The reasoning behind the research rules is in
[`research/registry/00_master_methodology.md`](research/registry/00_master_methodology.md).

### Research validity

1. **One clock.** A document exists for this research from its SEC EDGAR acceptance timestamp and
   not before. Every index, retrieval step and tool filters on it. Fundamentals are used as first
   filed, never as restated.
2. **Clean tests only.** Test documents are dated after the knowledge cutoff of every model on the
   evaluation roster (after 2026-06-30 as of this writing). Training and development data are
   earlier and come from different companies. Masking is not used: it removes the numbers that
   are the label, and ResearchOS showed that large caps stay identifiable after it.
3. **Every result carries a contamination label**: clean, bounded, contaminated or prospective.
4. **Pre-register, then look.** A hypothesis gets a `PRE-REGISTRATION` entry in
   `experiment_registry.md`, committed before any outcome data is touched. The verdict cites that
   commit. A refutation is a result. A local commit is not an independent time stamp:
   registrations and sealed manifests are pushed or externally time-stamped, in the way the owner
   decides.
5. **The test set is opened once per frozen configuration.** Development happens on the
   development set, with the same number of evaluations for every method being compared.
6. **No model on the evaluation roster touches gold test labels**, as annotator or as
   pre-annotator. Tuples are entered by the owner; revision labels are computed by rule and
   checked by the owner. A rule-based parser may propose tuples.
7. **Evaluated models get no web access.** Their inputs come only from the frozen corpus.
8. **Simple baselines first.** A rule-based baseline sets the bar before any model result is read.
9. **Every number is traceable** to a script and a run record: the command, the model repo and
   revision or the commercial model ID, and the date. Keep the raw request and response of every
   model call.
10. **Say what kind of claim it is**: verified fact, empirical finding, convention, hypothesis,
    open question or judgement.
11. **Check citations against the source.** No paper is cited from memory.

### Repository

12. **Nothing licensed, gold or secret goes into git.** That covers third-party text such as
    transcripts and vendor data, gold test labels, the contents of sealed forecasts, API keys and
    contact strings. Hash manifests are fine.
13. **Do not push** until the owner has decided the repo's visibility. `origin` is public as of
    2026-11-12.
14. **Commit only when the owner asks.** Experiment scripts are frozen once run: fix forward in a
    new numbered script.
15. **English by default** for documents, comments and commit messages. The owner's own Chinese
    text is kept verbatim, with its date.

### This machine

16. **One MLX job at a time.** On this 32 GB Mac two concurrent jobs end in `[METAL] Insufficient
    Memory` or a silent `Killed: 9`. Queue long runs as resumable background jobs. Read
    `learning_ai/CLAUDE.md` and `learning_ai/docs/FINANCE_MODEL_SELECTION.md` before running one.
17. **Download no model and pull no data set without the owner's say-so.** SEC EDGAR requests need
    the contact string the owner chooses. It is read from an environment variable and never
    written into the repo.
18. **Change no system setting.**
19. **At most three research agents in parallel.** Eight at once exhausted the usage allowance
    on 2026-11-12.

## 4. Environment

- Until the project gets its own environment in Phase I, use the conda env `py313` (Python 3.13,
  arm64, `mlx_lm` 0.32.2): `conda run --no-capture-output -n py313 python ...`. Never a bare
  `python3`, which is a different interpreter on this machine.
- Checkpoints already on the external drive: `mlx-community/Qwen3.5-4B-MLX-4bit`,
  `mlx-community/Qwen3.5-9B-MLX-4bit`, `mlx-community/gemma-4-12B-it-4bit`, `DianJin/DianJin-R1-7B`
  (4-bit, quantised locally), `mlx-community/gpt-oss-20b-MXFP4-Q8`.
- If the external drive is not mounted, stop and say so. Do not fall back to the internal disk.

## 5. Code to reuse before writing new

| Need | Where |
|---|---|
| Model loading and memory budget | `../learning_ai/learnai/openweights.py` |
| Batched generation, prefill cache, token log-probabilities, activation recording | `../learning_ai/learnai/weightedit.py` |
| Run-record format and resumable queue | `../learning_ai/tools/finance_model_select.py` |
| Brier score, calibration table, log loss | `../Foundry/tools/tools/stats.py` |
| Event return, abnormal return, max drawdown | `../Foundry/tools/tools/returns.py` |
| Paired comparison and bootstrap interval | `../Foundry/ResearchOS/researchos/compare.py` (resamples cases; panels need clustering by company and quarter) |
| Seal-then-reveal layout on disk | `../Foundry/ResearchOS/researchos/cases.py` |
| Structured output and prompt caching for the commercial model | `../Foundry/ResearchOS/researchos/llm.py` |

Whether these become dependencies or are copied in is decided in the research design (work
package 6). Do not modify the sibling repos from here.
