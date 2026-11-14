# Sub-study S1: distillation and expert pruning for a small earnings model

**Status: DRAFT for the owner's review, 2026-11-14. Nothing here is approved or pre-registered.**
Once approved, the plan is copied verbatim into `docs/plans/` and the experiments below get
`PRE-REGISTRATION` entries in `research/registry/experiment_registry.md` before any outcome data
is touched. The owner's request (2026-11-14, verbatim):

> 现在开始子研究 设计一下方案 研究有没有办法用大模型蒸馏或者专家剪枝的方法变成小模型 或者提升小模型 用作测评的task可以是一套earning相关的考题

## 1. Question and why it belongs here

The north star asks where capability for a specialised task should live. The main design covers
four locations: prompt, retrieved context, tools, and weights through fine-tuning. S1 tests a
fifth: **a large model's capability compressed into small weights**, either by teaching a small
model (distillation) or by cutting a large mixture-of-experts model down to the experts the task
uses (expert pruning). Both deliberately give up general ability to keep the specialised one.

Two research questions, each judged against the right bar:

- **RQ1, distillation.** Does a small student trained on a large teacher's worked answers to
  earnings questions beat the same student trained without the teacher, at the same data and
  development budget?
- **RQ2, expert pruning.** Can gpt-oss-20b, pruned to the experts that earnings text routes to,
  fit the 12 GiB budget, keep its earnings accuracy and beat the best dense model of the same
  memory?

**The bar is the obvious alternative, not the uncompressed model.** Most compression papers
report how little the compressed model loses against the original. The question that matters
here is whether it beats what is already on disk at the same memory, or a newer base model used
zero-shot. One 2026 result (arXiv 2606.08051, read from a search excerpt only) found zero-shot
Qwen3.5-4B within 0.4 F1 of a LoRA-tuned Llama 3.1-8B on a narrow financial extraction task.

## 2. What is already known on this machine

All measured, from `../learning_ai/docs/FINANCE_MODEL_SELECTION.md` and `feasibility.md`:

| Fact | Consequence for S1 |
|---|---|
| On 150 public finance questions (FinQA, CFA-Easy, FinanceIQ) local models score 73 to 77%; Claude offline 92% | A teacher-student gap of about 15 points exists on public exams |
| Most of the gap for the Qwens is not finishing within the token cap (the 9B: 27 of 30 lost questions) | Distilling short worked answers could buy efficiency as much as accuracy |
| Forcing an answer at the cap lifts DianJin-R1-7B from 324 to 344 of 450, for free | This free trick is a baseline every method has to beat |
| gpt-oss-20b: 24 layers, 32 experts per layer, 4 routed per token (local `config.json`); weights 11.3 GiB resident, 12.4 GiB peak at batch 1 | Out of the budget as it stands; pruning half its experts should bring the weights to roughly 6 to 7 GiB (estimate: experts hold about 19 of its 21 billion parameters) |
| `mlx_lm` stores gpt-oss experts stacked in one `SwitchGLU` with a `router` linear layer (`mlx_lm/models/gpt_oss.py`) | Removing experts means slicing the leading axis of the expert tensors and the router's rows; still to be shown for MXFP4-quantised tensors |
| LoRA within 12 GiB: Qwen3.5-4B up to 512 tokens, Gemma 4 12B up to 2,048, DianJin-R1-7B up to 4,096 | Worked-answer distillation needs DianJin, Gemma or a new base; Qwen3.5-4B can learn short answers only |
| Qwen3.5-9B forced at 8k: 130 of 150 (86.7%), the best local model | A local teacher with the same tokenizer as Qwen3.5-4B and 0.8B, so logit distillation is possible |

## 3. The exam: EarningsExam v0

A set of auto-graded questions on earnings releases. Section B is the instrument; section A
measures what is given up.

| Section | Content | Gold label from | Contamination label | Role |
|---|---|---|---|---|
| **B1 Lookup** | An excerpt of an 8-K earnings release (Exhibit 99.1) and a question asking for one reported figure: revenue, GAAP or adjusted EPS, net income, a segment figure, for a stated period | Two sources must agree: a rule parser reading the release's table, and the as-first-filed XBRL value in the 10-Q or 10-K for the same period. Disagreements are dropped and counted | Clean when the release postdates every model's cutoff, the teacher's included | Primary |
| **B2 Computation** | The same excerpts; growth rates, margins, per-share arithmetic, scale and units ("in thousands"), GAAP against non-GAAP | Computed by rule from B1-verified figures | As B1 | Primary |
| **B3 Guidance reading** (optional) | An outlook passage; extract the range for a named metric and period | Rule parser v2 proposes; owner checks | As B1 | Secondary, only if the owner has the time |
| **A Off-target** | FinQA, CFA-Easy, FinanceIQ (Chinese professional exams) through the existing `learnai/finbench` harness | The datasets' own answers | Contaminated: public and pre-cutoff. Used only to measure change from each model's own baseline | What is given up |

Design rules for the exam:

1. **Excluded: revision labels across consecutive releases.** That is Benchmark v0's job, and its
   test gold must not be spent here.
2. **Splits use the main programme's company split.** Train and development items come from
   pre-cutoff releases of training companies; test items from post-cutoff releases of test
   companies. A student trained in S1 is then company-disjoint from Benchmark v0's test and can
   enter the factorial later.
3. **Some templates are held out.** Some question templates appear only in the test set, so a
   student that has learned templates rather than reading is caught out. Results are reported on
   seen and unseen templates separately.
4. **Excerpts are length-capped**, at 400 tokens for the Qwen3.5-4B arm and 1,800 tokens for the
   others, so the training items fit the LoRA limits above.
5. **Answers go in `\boxed{}`**, graded by the existing tolerant numeric grader. How invalid
   output is scored is fixed before any run.
6. **Planned test size: about 1,500 B items from at least 400 companies.** With 15% disagreement
   between two systems, 1,000 paired items detect about 3.3 points at 80% power
   (`00_master_methodology.md` §6). Intervals are clustered by company.
7. **Headroom gate.** If the best small model scores above 95% on a B section zero-shot, that
   section is dropped as at ceiling.

## 4. Experiments

Numbers are provisional. Each gets its pre-registration, with numeric thresholds and seeds, once
the headroom run (S1-b) has supplied the rates.

### S1-a Feasibility (engineering, no hypothesis). CPU/network work can run beside other MLX jobs

1. Exam generator yield: how many B1 and B2 items survive the two-source agreement, by filer
   size.
2. Expert slicing on gpt-oss-20b in MLX: remove k experts per layer, check the output on a fixed
   prompt matches the reference path, measure resident memory at 25% and 50% pruning.
3. Peak memory of a calibration pass on unpruned gpt-oss-20b at 512 and 1,024 tokens. If it
   exceeds 12 GiB, either the owner grants a one-off exception or the pass streams layer by layer.
4. LoRA memory for Qwen3.5-0.8B at 1k, 2k and 4k tokens.

### S1-b Headroom (descriptive)

Zero-shot, with the forced-answer cue, on exam development items: Qwen3.5-0.8B, 4B, 9B, Gemma 4
12B, DianJin-R1-7B, gpt-oss-20b (unpruned, batch 1) and the teacher(s). Output: accuracy per
section, the teacher-student gap, the disagreement rate that sizes the test set, and tokens per
answer.

**Gate:** RQ1 goes ahead only if the teacher leads the best student by at least 5 points on some
B section. RQ2 goes ahead only if unpruned gpt-oss-20b is at least level with Qwen3.5-9B on B. If
it is not, pruning cannot win the decisive comparison (H6).

### S1-c Distillation (RQ1)

Students: DianJin-R1-7B (4k LoRA), Qwen3.5-0.8B (if S1-a shows it fits), Qwen3.5-4B (short
answers only). Teacher: see decision 1.

| Arm | Training signal (same items, same count, same development budget) |
|---|---|
| D0 | None: zero-shot with the forced-answer cue |
| D1 | Gold answer only, by rule (supervised fine-tuning without a teacher) |
| D2 | The student's own worked answers, kept when correct (rejection-sampling fine-tuning, "self") |
| D3 | The teacher's worked answers, kept when correct by gold, length-capped |
| D4 | Logit distillation from Qwen3.5-9B (same tokenizer), Qwen students only, optional |

Proposed hypotheses (thresholds to be fixed at pre-registration):

- **H1 (the teacher adds something):** D3 beats D2 on B test by at least 3 points. Without D2, any
  gain could be fine-tuning on the task, not the teacher.
- **H2 (efficiency):** D3 cuts median answer tokens by at least 50% against D0 and is
  non-inferior in accuracy, with a margin of 2 points.
- **H3 (the price, descriptive):** change in section A accuracy against D0, by exam and language.

Each LoRA arm is trained with three seeds; seed spread is reported beside the effect.

### S1-d Expert pruning (RQ2)

On gpt-oss-20b. Criteria: REAP (router weight times expert activation norm; Lasby et al., ICLR
2026), routing frequency, and random as a sanity floor. Calibration sets of equal token count:
domain (pre-cutoff earnings releases of training companies), general text, and a 50/50 mix.
Pruning ratios: 25% and 50% of experts per layer.

- **H4 (domain kept):** 50% REAP with domain calibration is non-inferior to unpruned on B, with a
  3-point margin, and its peak at batch 4 stays within 12 GiB.
- **H5 (specialisation, exploratory):** domain calibration beats general calibration on B and
  loses more on section A, most of all on Chinese FinanceIQ. The literature points both ways
  (MixCal, EACL 2026, for domain calibration; arXiv 2610.15578 against, for MoE). Neither has
  been read beyond search excerpts.
- **H6 (the decisive comparison):** the best pruned configuration beats the best dense model at
  no more memory (Qwen3.5-9B or DianJin, each in its best D-arm) on B test.

### S1-e Prune, then heal (conditional on S1-d)

LoRA on the pruned model with its unpruned self as teacher (self-distillation). It runs only if
S1-d leaves a gap worth closing and the pruned model's LoRA fits the budget. Exploratory.

## 5. Analysis

- Paired on the same items. Bootstrap intervals clustered by company.
- **Confirmatory contrasts: H1, H2, H4, H6**, Holm-corrected. H3 and H5 are descriptive or
  exploratory.
- Each arm gets the same development set and the same number of development evaluations.
  Checkpoint choice and LoRA search count as evaluations.
- Results reported by section (B1, B2), by seen and unseen templates, and by filer size.
- Every number traceable to a script, the model repo and revision (or commercial model ID), and
  the raw request and response.

## 6. Leakage

- Test items postdate the cutoff of every model involved, the teacher included (after 2026-06-30
  today). A commercial teacher makes the label "clean (vendor-stated cutoff)".
- The teacher sees only pre-cutoff training excerpts and writes worked answers to them. That is
  a narrow channel for later knowledge to reach the student, but it is not zero: a worked answer
  can mention what happened later. Worked answers are filtered for references to dates after the
  excerpt's own. This filtering is a judgement call, and the design document says so.
- Distillation moves a student's clean boundary to its teacher's cutoff. That matters for the
  two-tier idea discussed on 2026-11-14 (an old base model bounded by its release date): a
  distilled old model loses that bound.
- No roster model labels test items. B gold is by rule from two sources; B3 gold is the owner's.

## 7. Compute, order and cost (estimates)

| Block | Kind | Rough size |
|---|---|---|
| Exam build, XBRL matching | CPU and network; can run beside an MLX job | days of work, not GPU time |
| S1-b headroom | MLX | about 15 to 25 GPU hours |
| Teacher generation, local 9B, 1,000 to 2,000 items | MLX | about 5 to 10 hours |
| S1-c LoRA: 3 students × 4 arms × 3 seeds, about 1,000 items, 1 epoch | MLX | DianJin at 2k tokens runs about 5.8 s/step, so about 1.6 h per run, about 60 to 90 hours in all |
| S1-d pruning: 3 criteria × 3 calibration sets × 2 ratios, then evaluation | MLX | about 20 to 40 hours |

So about 120 to 180 GPU hours. With one MLX job at a time, that is two to four weeks of the
machine. WP5 (sealing before 2027-01-10) and the WP3 headroom pilot come first. **Proposed
order:** exam build and S1-a now, because they are mostly CPU and network work; GPU-heavy blocks
after EXP-0001 is sealed, from mid-January 2027.

Commercial teacher cost: not estimated yet. It is the per-item cost measurement planned in WP3
item 5.

## 8. Decisions for the owner

1. **Teacher.** (a) A commercial model through an API, which needs the key (open decision 5);
   the largest gap and full traceability. (b) Local Qwen3.5-9B only; free and allows logit
   distillation, but the gap is small (86.7% against 82% on the public screening set).
   (c) Claude through subagents, as in `FINANCE_MODEL_SELECTION.md` §6; usable for a few hundred
   items only, its reasoning not visible, and it eats the usage allowance.
2. **EDGAR pulls.** XBRL company facts (the as-filed values; this is also WP2's open
   "fundamentals as filed" item) and older pre-cutoff 8-K releases of training companies. Size
   still to be checked.
3. **Downloads.** A small general-text corpus for the general calibration set. Optionally
   Qwen2.5-7B-Instruct (open decision 2) as a further student.
4. **A one-off memory exception** for unpruned gpt-oss-20b at batch 1, around 12.4 GiB, with
   nothing else running. Otherwise the calibration pass is written to stream layer by layer,
   which takes longer to build.
5. **Priority.** S1 GPU work after the EXP-0001 sealing (proposed), or earlier at the cost of the
   WP3 pilot.
6. **B3 guidance reading:** include it, at about 200 owner-checked items, or leave it out. It
   competes with WP4 labelling time.

## 9. What would change this plan

- **S1-b shows no teacher-student gap of 5 points on B:** RQ1 is answered "not on this exam".
  Either harder templates are written (computation, units, GAAP against non-GAAP) or RQ1 stops.
- **Expert slicing on MXFP4 tensors fails in MLX:** RQ2 moves to a dense model's structured
  pruning, which needs a healing step that may not fit the budget, or stops.
- **D2 matches D3 (H1 refuted):** the finding is that fine-tuning on the task, not the teacher,
  carries the gain. That is a result, and it simplifies the factorial's fine-tuning level.

## Sources to read in full before any of this enters `research/literature/`

Seen only as search excerpts on 2026-11-14:
[REAP, arXiv 2510.13999](https://arxiv.org/abs/2510.13999);
[MixCal, arXiv 2502.18424](https://arxiv.org/abs/2502.18424);
[MoE calibration, arXiv 2610.15578](https://arxiv.org/abs/2610.15578);
[task-specific distillation scaling laws, quantitative finance, arXiv 2606.24747](https://arxiv.org/abs/2606.24747);
[LoRA on 270M to 8B models for merchant extraction, arXiv 2606.08051](https://arxiv.org/abs/2606.08051).
