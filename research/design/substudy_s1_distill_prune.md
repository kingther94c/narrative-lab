# Sub-study S1: compressing small models for an earnings exam

**Status: DRAFT v2, 2026-11-14. The owner approved the downloads and EDGAR pulls of §8 the same
day ("全部批准"). The plan itself is not yet frozen, and nothing is pre-registered.**
Once approved, the plan is copied verbatim into `docs/plans/` and the experiments below get
`PRE-REGISTRATION` entries in `research/registry/experiment_registry.md` before any outcome data
is touched.

The owner's requests (2026-11-14, verbatim):

> 现在开始子研究 设计一下方案 研究有没有办法用大模型蒸馏或者专家剪枝的方法变成小模型 或者提升小模型 用作测评的task可以是一套earning相关的考题

> 不一定要追求大 可以用比较小的 然后看压缩的更小 怎么样

v1 of this draft started from gpt-oss-20b and a commercial teacher. v2 follows the second request:
**work down a ladder of small models, and compress them further.**

## 1. Question and why it belongs here

The north star asks where capability for a specialised task should live. The main design covers
four locations: prompt, retrieved context, tools, and weights through fine-tuning. S1 tests a
fifth: **capability compressed into fewer weights**. Three routes are covered: teaching a smaller
model (distillation), cutting layers out of a dense model and healing it (structured pruning),
and cutting experts out of a mixture-of-experts model (expert pruning). Each one deliberately
gives up general ability to keep the specialised one.

**The bar for every route is an off-the-shelf model of the same size**, not the model before
compression. Most compression papers report how little a compressed model loses against its
original. Here the question is whether it beats what can simply be downloaded at that size. One
2026 result (arXiv 2606.08051, read from a search excerpt only) found zero-shot Qwen3.5-4B within
0.4 F1 of a LoRA-tuned Llama 3.1-8B on a narrow financial extraction task.

### Why small first

| Gain | Why |
|---|---|
| The whole pipeline fits | Pruning, healing and distillation all fit the 12 GiB budget at 0.8B to 4B. At 20B only one-shot pruning fits, with no healing |
| Iteration is cheap | Three seeds per arm and a full grid of arms become affordable |
| Logit distillation is possible | The Qwen3.5 0.8B, 4B and 9B tokenizers give identical ids (S1-a.2, done) |
| A ladder shows a trend | Whether the gain from compression grows or shrinks with size says more than one point does |
| The result is usable | An extractor that reads ~10,000 releases a season has to be small and fast |

| Cost | Mitigation |
|---|---|
| Floor effects: a 0.8B model may not do the computation section at all | The headroom run (S1-b) decides which sections each size is tested on |
| Results may not transfer upward | The claim is limited to the sizes tested. gpt-oss-20b stays as an optional top rung |
| Qwen3.5's DeltaNet layers make LoRA memory grow fast with sequence length (EXP-0000) | Measured for 0.8B in S1-a. If healing does not fit, the ladder switches to the Qwen3 family, which has ordinary attention |

## 2. The ladder

| Rung | Model | On disk? | Role |
|---|---|---|---|
| Teacher | Qwen3.5-9B (4-bit) | Yes | Best local model: forced at 8k, 130 of 150 public finance questions (86.7%), `FINANCE_MODEL_SELECTION.md` §8.6 |
| Middle | Qwen3.5-4B (4-bit) | Yes | Student, and the dense model to be pruned |
| Same-size reference | `mlx-community/Qwen3.5-2B-MLX-4bit` (post-trained, Apache-2.0, 1.63 GiB; same quantisation series as the 4B and 9B) | Downloading, approved 2026-11-14 | Off-the-shelf comparison for a 4B pruned to about 2B |
| Bottom | Qwen3.5-0.8B (bf16) | Yes | Smallest student |
| Small MoE | `mlx-community/OLMoE-1B-7B-0125-Instruct-4bit` (Apache-2.0, 3.63 GiB), chosen over Granite-3.1-3B-A800M | Downloading, approved 2026-11-14 | Expert pruning. OLMoE's training data is public, so contamination can be checked against the data itself, not just a cutoff date. From its config: 16 layers, 64 experts per layer, 8 routed per token, 4,096-token context |
| Optional top rung | gpt-oss-20b (24 layers, 32 experts, 4 routed per token; 11.3 GiB resident) | Yes | Expert pruning that brings a model into the budget. Only if the small-MoE result warrants it |
| Optional ceiling | A commercial model | API key needed | A reference score only, not a teacher |

## 3. The exam: EarningsExam v0

A set of auto-graded questions on earnings releases. Section B is the instrument; section A
measures what is given up.

| Section | Content | Gold label | Contamination label | Role |
|---|---|---|---|---|
| **B1 Lookup** | An excerpt of an 8-K earnings release (Exhibit 99.1) and a question asking for one reported figure: revenue, GAAP or adjusted EPS, net income, a segment figure, for a stated period | Two sources must agree: a rule parser reading the release's table, and the as-first-filed XBRL value in the 10-Q or 10-K for the same period. Disagreements are dropped and counted | Clean when the release postdates every model's cutoff | Primary |
| **B2 Computation** | The same excerpts; growth rates, margins, per-share arithmetic, scale and units ("in thousands"), GAAP against non-GAAP | Computed by rule from B1-verified figures | As B1 | Primary |
| **B3 Guidance reading** (optional) | An outlook passage; extract the range for a named metric and period | Rule parser v2 proposes; owner checks | As B1 | Secondary, only if the owner has the time |
| **A Off-target** | FinQA, CFA-Easy, FinanceIQ (Chinese professional exams) through the existing `learnai/finbench` harness | The datasets' own answers | Contaminated: public and pre-cutoff. Used only to measure change from each model's own baseline | What is given up |

Design rules:

1. **Excluded: revision labels across consecutive releases.** That is Benchmark v0's job, and its
   test gold must not be spent here.
2. **Splits use company split v1** (`research/experiments/split_v1.py`, fixed 2026-11-15 and
   shared with the main programme; census in `data_audit.md` §8a). Training items come from
   pre-cutoff releases of training companies. Development items come from development companies,
   and their post-cutoff releases make a clean development set. Test items come from post-cutoff
   releases of test companies. A model compressed here is then company-disjoint from Benchmark v0's test.
3. **Some templates are held out.** Some question templates appear only in the test set; results
   are reported on seen and unseen templates separately.
4. **Excerpts are capped at 400 tokens**, so that question, excerpt and a short worked answer fit
   the LoRA limits of the Qwen3.5 rungs. Whether 0.8B allows longer is measured in S1-a.
5. **Answers go in `\boxed{}`**, graded by the existing tolerant numeric grader. How invalid
   output is scored is fixed before any run.
6. **Planned test size: about 1,500 B items from at least 400 companies.** With 15% disagreement
   between two systems, 1,000 paired items detect about 3.3 points at 80% power. Intervals are
   clustered by company.
7. **Headroom gate per size.** A section is dropped for a model scoring above 95% zero-shot
   (ceiling) or below 20% (floor).

## 4. Experiments

Numbers are provisional. Each gets its pre-registration, with numeric thresholds and seeds, once
the headroom run (S1-b) has supplied the rates.

### S1-a Feasibility (engineering, no hypothesis)

1. Exam generator yield: how many B1 and B2 items survive the two-source agreement, by filer size.
   CPU and network work; runs beside other MLX jobs.
2. **Done 2026-11-14:** whether the tokenizers of Qwen3.5-0.8B, 4B and 9B are identical.
   Empirical finding: the base vocabulary and the 247,587 merges are identical. The 4B and 9B
   add seven audio and speech special tokens (ids 248,070 to 248,076) that the 0.8B lacks; they
   never occur in text and are masked in logit distillation. On 4,245 tokens of release text,
   Chinese text and chat markup, all three give identical ids. **Chat templates differ:** the
   0.8B thinks only when `enable_thinking=true`, while the 4B and 9B think unless
   `enable_thinking=false`. Every run therefore sets thinking explicitly; left at the defaults, a
   size comparison would also be a comparison between thinking and not thinking. Checked with a
   scratch script, not yet an experiment script.
3. LoRA and full fine-tuning memory for Qwen3.5-0.8B at 512, 1k and 2k tokens; LoRA on a 4B with
   layers removed.
4. Removing layers from Qwen3.5-4B in MLX, keeping the full-attention and DeltaNet pattern valid.
5. Removing experts from the small MoE in MLX: slice the stacked expert tensors and the router's
   rows, then check the output against the reference path.

### S1-b Headroom (descriptive)

Every rung zero-shot, with the forced-answer cue, on exam development items. Output: accuracy per
section and size, the gaps between rungs, the disagreement rate that sizes the test set, and
tokens per answer.

**Gate:** distillation goes ahead only if 9B leads 4B, or 4B leads 0.8B, by at least 5 points on
some B section. With a smaller gap there is nothing to distil.

### S1-c Distillation down the ladder (RQ1)

Pairs: 9B → 4B, 9B → 0.8B and 4B → 0.8B. The last asks whether a closer teacher teaches better.

| Arm | Training signal (same items, same count, same development budget) |
|---|---|
| D0 | None: zero-shot with the forced-answer cue (a free trick that lifted DianJin from 324 to 344 of 450) |
| D1 | Gold answer only, by rule: fine-tuning without a teacher |
| D2 | The student's own worked answers, kept when correct: rejection-sampling fine-tuning, "self" |
| D3 | The teacher's worked answers, kept when correct by gold, length-capped |
| D4 | Logit distillation: the teacher's top-k token log-probabilities over D3's text. Needs identical tokenizers (S1-a.2) |

- **H1 (the teacher adds something):** D3 or D4 beats D2 on B test by at least 3 points. Without
  D2, any gain could be fine-tuning on the task, not the teacher.
- **H2 (a small model reaches a bigger one):** the best distilled 0.8B is non-inferior to
  zero-shot 4B on B test, with a 3-point margin. That is five times smaller for this task.
- **H3 (efficiency):** the distilled arm cuts median answer tokens by at least 50% against D0
  without losing more than 2 points.
- **H4 (the price, descriptive):** change in section A accuracy against D0, by exam and language.

### S1-d Structured pruning of a dense model (RQ2)

Qwen3.5-4B → about 2B (and 3B). Score the importance of each layer on calibration text of equal
token count from three sources: domain (pre-cutoff releases of training companies), general, and
a 50/50 mix. Remove the least important layers, keeping the hybrid pattern valid. Then heal: LoRA
or full fine-tuning on the exam training items, with the unpruned 4B as teacher (logit
distillation) and gold alone as a control.

- **H5 (the decisive comparison):** pruned-and-healed 4B at about 2B beats both off-the-shelf
  Qwen3.5-2B (if it exists; otherwise interpolated between 0.8B and 4B) and the best distilled
  0.8B from S1-c on B test, each at its best arm.
- **H6 (specialisation, exploratory):** domain calibration beats general calibration on B and
  loses more on section A, most of all on Chinese FinanceIQ. The literature points both ways
  (MixCal, EACL 2026, for domain calibration; arXiv 2610.15578 against, for MoE). Neither has
  been read beyond search excerpts.

### S1-e Expert pruning of a small MoE (RQ3)

On the small MoE of §2. Criteria: REAP (router weight times expert activation norm; Lasby et al.,
ICLR 2026), routing frequency, and random as a sanity floor. Calibration sets as in S1-d. Pruning
ratios 25% and 50% of experts per layer. With and without a short healing step.

- **H7:** 50% REAP with domain calibration is non-inferior to the unpruned MoE on B, with a
  3-point margin.
- **H8 (the decisive comparison):** the pruned MoE beats the dense rung of the same resident
  memory on B test.

If H7 holds, the same recipe can be tried on gpt-oss-20b as an optional top rung. That needs a
one-off memory exception for its calibration pass, around 12.4 GiB.

## 5. Analysis

- Paired on the same items. Bootstrap intervals clustered by company.
- **Confirmatory contrasts: H1, H2, H5, H8**, Holm-corrected. H3 and H7 are secondary; H4 and H6
  are descriptive or exploratory.
- Each arm gets the same development set and the same number of development evaluations.
  Checkpoint choice, LoRA search and pruning-ratio choice count as evaluations.
- Every trained arm runs three seeds, and the seed spread is reported beside the effect.
- Results reported by section (B1, B2), by seen and unseen templates, by filer size, and per rung.
- Every number traceable to a script, the model repo and revision, and the raw request and
  response.

## 6. Leakage

- Test items postdate the cutoff of every model involved (after 2026-06-30 today). Every teacher
  here is a local model on the roster, so no commercial cutoff enters unless the optional ceiling
  is used.
- The teacher sees only pre-cutoff training excerpts. Its worked answers are filtered for
  references to dates after the excerpt's own. This filtering is a judgement call, and the design
  document says so.
- Distillation moves a student's clean boundary to its teacher's cutoff. Within one family the two
  are close, but they are not guaranteed equal.
- No model labels test items. B gold is by rule from two sources; B3 gold is the owner's.

## 7. Compute, order and cost (estimates)

| Block | Kind | Rough size |
|---|---|---|
| Exam build, XBRL matching | CPU and network; runs beside an MLX job | days of work, no GPU |
| S1-a probes | MLX | a few hours |
| S1-b headroom, 5 to 6 models | MLX | about 10 to 15 hours |
| Teacher generation, 9B and 4B, about 1,500 items | MLX | about 6 to 10 hours |
| S1-c: 3 pairs × 4 trained arms × 3 seeds, about 1,000 items, short sequences | MLX | about 30 to 50 hours |
| S1-d: 2 sizes × 3 calibration sets, healing × 3 seeds | MLX | about 20 to 30 hours |
| S1-e: 3 criteria × 3 calibration sets × 2 ratios | MLX | about 10 to 20 hours |

So about 80 to 125 GPU hours, against 120 to 180 in v1, with more seeds. With one MLX job at a
time, that is one and a half to three weeks of the machine. WP5 (sealing before 2027-01-10) and
the WP3 headroom pilot come first. **Proposed order:** exam build and the S1-a probes now; S1-b
when the machine is free between WP3 runs; the trained arms after EXP-0001 is sealed, from
mid-January 2027.

## 8. Decisions for the owner

1. ~~**EDGAR pulls.**~~ Approved 2026-11-14. XBRL company facts: SEC's bulk `companyfacts.zip`
   (1.33 GiB, snapshot of 2026-11-14). Each fact carries its filing date and accession number, so
   first-filed values can be rebuilt from it. Older pre-cutoff 8-K releases of training companies
   are pulled once the company split is fixed (§3 rule 2).
2. ~~**Downloads.**~~ Approved 2026-11-14: the two models of §2 and, as the general calibration
   text, one shard of C4 (`allenai/c4`, `en/c4-validation.00000-of-00008.json.gz`, 40 MB,
   ODC-BY). All on the external drive.
3. **Commercial ceiling: deferred.** The commercial part is set aside for now (changelog,
   2026-11-14). S1 needs no commercial model; the ceiling would only show how far the ladder is
   from a frontier model on this exam.
4. **Priority.** Trained arms after the EXP-0001 sealing (proposed), or earlier at the cost of
   the WP3 pilot.
5. **B3 guidance reading:** include it, at about 200 owner-checked items, or leave it out. It
   competes with WP4 labelling time.

## 9. What would change this plan

- **No gap of 5 points between rungs on B:** distillation has nothing to transfer on this exam.
  Either harder templates are written (computation, units, GAAP against non-GAAP), or S1-c stops
  and S1-d/e are judged on memory alone.
- **0.8B is at the floor on B2:** the bottom rung is tested on B1 only, and the 4B → 2B pruning
  becomes the main small target.
- **LoRA on pruned Qwen3.5 does not fit at 400 tokens:** the ladder moves to the Qwen3 family
  (0.6B, 1.7B, 4B, 8B, ordinary attention). Its 0.6B is on disk; the rest are downloads.
- **D2 matches D3 (H1 refuted):** the finding is that fine-tuning on the task, not the teacher,
  carries the gain. That is a result, and it simplifies the factorial's fine-tuning level.

## Sources to read in full before any of this enters `research/literature/`

Seen only as search excerpts on 2026-11-14:
[REAP, arXiv 2510.13999](https://arxiv.org/abs/2510.13999);
[MixCal, arXiv 2502.18424](https://arxiv.org/abs/2502.18424);
[MoE calibration, arXiv 2610.15578](https://arxiv.org/abs/2610.15578);
[task-specific distillation scaling laws, quantitative finance, arXiv 2606.24747](https://arxiv.org/abs/2606.24747);
[LoRA on 270M to 8B models for merchant extraction, arXiv 2606.08051](https://arxiv.org/abs/2606.08051).
Model facts checked against the Hugging Face API on 2026-11-14: Qwen3.5-2B exists (base and
post-trained); the licence tags and sizes in §2. Downloads finished the same day at revisions
`93760be4f1f6` (Qwen3.5-2B) and `e23844197887` (OLMoE). The C4 shard passes `gzip -t`.
`companyfacts.zip` holds 20,588 company files and passes the zip CRC check. OLMoE's
training-data cutoff is still to be read from its card.
