# S1 re-plan: distilling financial analysis into a small model

**Status: approved by the owner, 2026-11-26** ("全案推荐来": the four decisions of §5 as
recommended). It replaces, for the rest of S1's window (to 2026-12-15), the steps after S1-c of
the frozen S1 plan (`docs/plans/2026-11-15_substudy_s1_plan.md`); `changelog.md` records the
change. Arms, measures and hypotheses are fixed in the main experiment's pre-registration, not
here. Written 2026-11-25. Sources: S1's experiments to EXP-0050 (registry), literature streams 14a
(`../literature/streams/14a_synthetic_data_small_specialists.md`), 14b
(`../literature/streams/14b_distillation_methods_small_students.md`) and 14c
(`../literature/streams/14c_finance_specialists_analyst_reasoning.md`), written 2026-11-25, plus
13a and 13b.

The owner's request (2026-11-25, verbatim):

> 我觉得更重要的是这个在金融方面的应用。我们现在非常在乎它在金融方面的应用，它读一些东西，它最后能不能有这种很好的逻辑，形成一种体系？我们需要，我们想蒸馏的是从大模型里面的这些东西，然后看看能不能在小模型里面浮现出来。大模型可能是各个领域的专家，但我们希望这个小模型能够，呃，更好的在一个具体的领域上面啊、呃、有突出的能力。嗯，对，然后有没有可能就是用这个大一点的模型多生成很多的数据，然后用小模型去学习，或者是有什么其他的思路？

## 1. Where S1 stands

What is established (registry entries EXP-0005 to EXP-0050):

1. **The exam works.** EarningsExam v0.2 (B1 lookups, B2 computations) and section R v0 (checkable
   reasoning items with twins) grade by rule against XBRL.
2. **A 4B teacher teaches a 0.8B a narrow skill.** Teacher answers beat the student's own by 6.5
   points (EXP-0014, H1). The student matches the 4B on lookups. With a calculator it is 3 to 4
   points behind the 4B overall, 9 to 12 on computations, where it reads the wrong column
   (EXP-0016 to 0018).
3. **What it learned is a template, not a skill.** On section R the distilled 0.8B boxes a number
   on 300 of 300 label items and scores under 1, against 56 for the untrained 0.8B and 82 for the
   4B (EXP-0050). FinQA fell from 38 to about 10 after training (EXP-0014, H4). Hints do not help
   the 0.8B.
4. **Against the untrained 0.8B, the 4B's lead on R is 26 points, on B 34.** The headroom is real
   on five templates (R1.1, R1.3, R1.4, R1.5, R1.8).

So far S1 has shown that a small model can be drilled; the owner's question is whether it can be
*taught*: whether a larger model's way of reading a release can emerge in a small one, carry over
to questions it was not trained on, and hold together.

## 2. The question, restated

**Can a 0.8B model, trained on what a larger model generates from earnings releases, analyse a
release better than any model of its size, on question types it was never trained on, with
answers that are consistent with each other and follow the figures, and at what cost to what else
it can do?**

"A framework (体系) rather than a template" is made measurable as five checks (14c §2, 14a §2):

| Check | What it rules out |
|---|---|
| **Held-out families**: whole R families never asked, and their indicators never computed, in training | Memorising question types |
| **Held-out combinations**: trained steps combined in a new order | Memorising chains |
| **Twins**: flip (years swapped), hold (irrelevant row added), mirror (subjects swapped) | Answers not driven by the figures |
| **Within-release coherence**: the labels a model gives on one release must be mutually consistent (for example, operating margin expanded if and only if operating expenses grew slower than revenue, given the reported figures) | A set of unrelated guesses |
| **Whole-release analysis in one pass**: the model fills the full condition table for a release; every cell is checked by rule | Skill only when the question names the step |

Holistic grading of free-text analysis is not used for any verdict: human raters of analyst
reports agree at kappa 0.17, and LLM judges prefer generated reports to analysts' 71 to 100% of
the time (14c §3).

## 3. What the literature says (streams 14a to 14c)

Evidence is mostly maths and code, at 1.5B and above; finance below 3.8B is untested (14a §7,
14c §1). The findings that shape the design:

1. **Our collapse has a name, format specialisation, and a known cure: variety.** A model trained
   on one answer format answers everything in it (ProMoT, ICLR 2024: TriviaQA 17.6 to 0.2).
   Fewer than about 300 distinct instructions give no transfer to unseen tasks; from about 1,000
   there is transfer (14a §2). Multi-task training turns a −2.1 unseen-task change into +2.5
   (14b §1).
2. **More data of one kind deepens one skill and does not widen it.** TinyGSM's 12.3M problems
   lift a 1.3B to 68 on GSM8K, with marginal gains from the last third. Finance curves flatten
   by about 3,000 items (Harsha 2025, synthetic FinQA, 3.8B) (14a §1). Volume pays only when it
   is spread over many task types and documents.
3. **Generate from the documents.** Turning source text into many synthetic tasks and passages
   puts domain knowledge into the weights where raw text does not (EntiGraph: 39.5 to 56.2;
   Instruction Pre-Training in finance: 70.1 to 74.7 for an 8B) (14a §3). Synthetic finance QA
   transferred to another data set better than real QA (84.3 against 81.2 on TATQA).
4. **A close teacher beats a strong one for a small student.** Below about 3B, smaller teachers
   and short traces teach better (li-2025). Same-family teachers did best; one fit puts the best
   teacher near 2.5 times the student (14a §4). For us: the 4B (5×, same tokenizer) as the main
   teacher, the 9B as a pilot.
5. **Off-policy SFT is what causes the forgetting; on-policy data limits it.** At 1 to 1.5B, SFT
   on a 70B teacher's answers cost 6 to 30 points elsewhere; regenerating data from the current
   model each epoch gave mild or no forgetting (Chen et al. 2025, "Retaining by doing") (14b §3).
6. **On-policy distillation beats RL, at a tenth of the cost, but has a ceiling at small size.**
   Qwen3 built every model from 0.6B to 14B by strong-to-weak distillation (off-policy, then
   on-policy logits). From the same checkpoint, on-policy distillation reaches AIME'24 74.4
   against 67.6 for RL, at 1,800 against 17,920 GPU hours. At 0.6B most of the gain is learning to
   finish an answer; it does not exceed what the student's own samples reach (Li et al. 2026)
   (14b §4). RL on small models adds little and is contested (14b §5).
7. **A procedure can be distilled when its steps are verified and merged.** DianJin-R1: a 72B
   works a checklist step by step, the steps are merged into one chain, and the 7B student
   reaches 94.5 in one call against 95.0 for the 72B over 8 calls (in distribution only).
   Answer-only training fell below the base (83.7 to 75.8); chains reached 86.0 (14c §1, §2).
8. **Cheap repairs for forgetting:** averaging the trained weights with the base model (the best
   trade-off among the methods compared at 3B), rewriting targets in the student's words (SDFT),
   LoRA instead of full fine-tuning in some domains, and 10 to 20% general or gold data mixed in
   (14a §6, 14b §2).
9. **Size limits that will not move:** small models extract from varied layouts and handle
   derived periods poorly (FinAR-Bench, BizFinBench), and next-period outcome prediction is near
   chance even for frontier models (EDINET-Bench, AUC 0.40 to 0.65). Outcome prediction is not a
   target for this sub-study (14c §4, §5).

## 4. Proposed design

### 4.1 The data factory

- **Documents.** 8-K earnings releases of training companies only, accepted before 2026-06-30.
  On the drive: 3,277 train-company releases (2026 only). The SEC submissions index lists at least
  30,301 earnings 8-Ks (Item 2.02) for the 1,160 training companies from 2019 to mid-2026. Fetching
  them is a data pull and needs the owner's approval. Test and development companies are never
  read by the factory. (Approved 2026-11-26; EXP-0052 counts 40,266 releases from 1,862 companies
  with the archive's overflow files read.)
- **The analysis graph** (the framework the student should learn). For each release:
  1. extract both periods for revenue, cost of revenue or gross profit, operating expenses,
     operating income, pre-tax income, tax, net income, diluted EPS and diluted shares;
  2. compute growth rates, margins, margin changes in points, the effective tax rate and the
     share-count change (with the calculator);
  3. mark the conditions: margin direction, operating leverage, cost against sales, EPS against
     net income, tax effect, biggest mover, derived periods, what the excerpt does not give;
  4. write a two- to four-sentence account of what drove earnings, using only verified conditions.
  The teacher works through the graph; every extracted figure and computed number is checked
  against XBRL or the rule parser. Failed traces are retried or dropped, and passing steps are
  merged into one short chain (DianJin-R1's recipe, 14c §2). Traces are written forward from the
  release, never from the gold label.
- **Task variety.** From each release's graph, items of many kinds under fixed quotas: numbers,
  direction labels, which-line, true-or-false claims, "cannot be determined", one- to
  two-sentence explanations, the full condition table, and short relation passages between line
  items (EntiGraph style). At least 1,000 distinct question phrasings. No single answer template.
- **Volume.** Several teacher samples per item (4 to 8, filtered). Two size levels, about 5,000
  and 20,000 training examples, so the effect of scale is measured, not assumed.
- **Held out from the factory entirely:** two R families with their indicators (chosen in the
  pre-registration, for example R1.5 tax line and R1.4 EPS against net income), so transfer is
  tested on reasoning the student never saw.
- **Teacher.** Qwen3.5-4B with the inline calculator (4I) writes traces. The 9B is run on a
  pilot and used only if the 0.8B learns better from it on development items. gpt-oss-20b
  (different tokenizer) may write and check question phrasings, not traces.

### 4.2 Arms (every student starts from the released Qwen3.5-0.8B, not from C or K2)

| Arm | Training | What it isolates |
|---|---|---|
| P0 | Released 0.8B, no training | The size bar |
| P2B | Released Qwen3.5-2B, no training (on disk) | "Better than its size": can the 0.8B beat a 2.5× larger model? |
| T | 4I, the teacher | The ceiling |
| F1 | SFT on the same items, mixed formats, answers only | Learning the formats alone |
| F2 | SFT on teacher chains, mixed formats, 5,000 and 20,000 examples | Learning the reasoning; effect of scale |
| F3 | F2 plus 2 to 3 rounds of on-policy logit distillation from the 4B | Whether on-policy data adds reasoning and limits forgetting |
| +avg | Each trained arm averaged with the base weights (no training) | Cheap repair of forgetting |

10 to 20% general and B items are mixed into F1 to F3. One seed per arm, with a second seed for
the best arm if time allows. RL is out of scope before 2026-12-15 (8 to 10 times the cost per
prompt, small gains for small models, 14b §5).

### 4.3 Measures and working hypotheses (fixed in the pre-registration, not here)

Test: section R test items (EXP-0019, fresh draw; R1.7 reworded and R1.8 limited to sensible
margins by a new builder first), their twins, the held-out families, and the whole-release
condition table. Retention: B test, section A (FinQA, CFA-Easy, FinanceIQ). Step accuracy and
answer accuracy reported separately.

- **HF1, reasoning beyond format:** F2 beats F1 on in-family R items.
- **HF2, a framework, not a template:** on held-out families, F2 beats P0 and keeps at least half
  of its in-family gain; twins and coherence are no worse than P0's.
- **HF3, better than its size:** the best student is at least level with P2B on R.
- **HF4, on-policy:** F3 beats F2, on R and on retention.
- Descriptive: the 5,000 against 20,000 curve; the cost on section A and B; averaging's effect.

### 4.4 Two diagnostics first, no training (about 3 hours, development items only)

1. Average C's and K2's weights with the released 0.8B. If R labels come back while B holds,
   forgetting is cheap to repair and F-arms can be lighter (14b §2).
2. Sample the released 0.8B several times per development R item. The share of items it ever
   gets right bounds what on-policy distillation can reach (14b §4).

### 4.5 Machine time and calendar (estimates)

Measured rates: 4B generation 53 tokens per second single-stream, 9B 30 (EXP-0011); 0.8B full
fine-tuning about 1,260 examples an hour at batch 1, 8.1 GiB (EXP-0017); 4B answers on R about 8
seconds an item (EXP-0050).

| Step | Machine hours |
|---|---|
| Diagnostics | 3 |
| Generation, 20,000 examples with 4 to 8 samples and verification (batching untested; could halve) | 35–60 |
| SFT: F1, F2 at two sizes | 40–50 |
| On-policy rounds (custom MLX loop, verified first against a reference) | 15 |
| Development checkpoints | 5 |
| Test: students, P2B, the teacher on R test and twins; retention | 30 |
| **Total** | **about 130–165** |

| Dates | Work |
|---|---|
| 11-26 to 11-28 | Diagnostics; EDGAR pull if approved; factory v1 and the R test builder fix; speed checks; pre-registration |
| 11-29 to 12-03 | Generation |
| 12-03 to 12-09 | Training and development choice |
| 12-09 to 12-12 | Test |
| 12-12 to 12-15 | S1 report |

The binding constraint is engineering, not machine time: the factory and the on-policy loop are
new code. F3 is last and is dropped first if the calendar slips.

## 5. What this replaces, and decisions for the owner

- **S1-d (layer pruning) and S1-e (expert pruning)** do not fit before 2026-12-15 with this
  design. Proposed: defer both beyond the window, or close them as not done in the S1 report.
- **R-c as written in EXP-0050's verdict** (about 9,400 items, 4I against K2) is replaced by this
  design's test. C and K2 are retired as arms.
- Decisions (asked 2026-11-25; the owner took all four as recommended on 2026-11-26, "全案推荐来"):
  1. Adopt this direction for the rest of S1's window. **Adopted;** S1-d and S1-e deferred beyond
     the window.
  2. Approve the EDGAR pull of training-company releases from 2019 to mid-2026 (about 30,000
     earnings 8-Ks and their XBRL), or use the 3,277 on the drive. **Pull approved** (EXP-0052:
     40,266 releases from 1,862 companies once overflow files and companies that no longer file
     are counted; XBRL company facts were already on the drive).
  3. Teachers: local open-weight models only (Qwen3.5-4B, with the 9B as a pilot). A commercial
     model as teacher would need its terms of use checked for training other models first.
     **Local open-weight teachers only.**
  4. Run the two diagnostics now. **Approved** (EXP-0051).

## 6. Risks

- Below 1.5B, no paper shows on-policy distillation or synthetic data teaching transferable
  reasoning; a negative result is plausible and would itself answer the question.
- A fixed analysis graph may become a longer template; only the held-out families and
  combinations can tell.
- The 4B is wrong on about 18% of R items; filtering by rule removes wrong labels, but wrong
  reasoning with a right answer can pass.
- Distillation from a 4-bit teacher's logits is untested; `mlx-lm` supports SFT only.
- Generating from many releases risks the student memorising figures; only training companies
  before the cutoff are used, and test companies are disjoint.
