# Stream 14b: distillation and training methods beyond off-policy SFT, for small students

Sources checked 2026-11-25, for sub-study S1 (`../../design/substudy_s1_distill_prune.md`). 20 rows
in `14b_distillation_methods_small_students.csv`: 5 deep notes and 15 triaged rows. That is two
above the 12 to 18 target: the 2026 papers on on-policy distillation at 0.6B and the 2026 rebuttal of
"SFT memorizes, RL generalizes" turned up late, and each changes a recommendation. Deep notes:
`../papers/yang-2025-qwen3-strong-to-weak-distillation.md`,
`../papers/li-2026-on-policy-distillation-small-scale.md`,
`../papers/chen-2026-retaining-by-doing.md`,
`../papers/wang-2024-promot-format-specialization.md`,
`../papers/yang-2024-sdft-self-distillation-fine-tuning.md`.
Already covered elsewhere and cited, not repeated: Li et al. 2025 (short against long traces, small
against large teacher), Fino1 and Fin-R1 (SFT then RL in finance), Yue et al. 2025 (RL bounded by
base pass@k) and Hayrapetyan et al. 2026 (retention-aware financial post-training), all in stream
13a; Mosbach et al. 2023 (checkpoint selection) in stream 05; Sprague et al. 2025 (where chain of
thought helps) in stream 12. Stream 14a covers synthetic-data scale and diversity in parallel; three
rows appear in both CSVs (GKD, DeepSeek-R1, Qwen3) and should be reconciled at merge. Most
papers were read through an automated page reader; table values are as it returned them and were
not re-keyed from PDFs. Not merged into `../matrix.csv`.

The question: S1's off-policy SFT of Qwen3.5-0.8B on the 4B's terse boxed answers (full fine-tuning,
about 1,850 items) brought the 0.8B to the 4B on lookups, but (a) on the new R section, whose answers
are labels, the distilled checkpoints box a number on 300 of 300 items (R 0.7 to 0.9 against 55.9 for
the untrained 0.8B and 82.0 for the 4B; EXP-0050); (b) section A fell (FinQA 38 to 10); (c) a
calculator fixed arithmetic. Can a larger model's financial reasoning be distilled into a 0.8B by
something other than off-policy SFT, on one 12 GiB MLX machine, by 2026-12-15?

## What the stream establishes

**1. The R collapse is a known failure with a name: format specialisation**

- **Empirical finding.** Fine-tuning mT5-XXL (13B) on RTE (answers "True"/"False") makes about 90%
  of 1-shot TriviaQA outputs "True" or "False" after 300 steps; TriviaQA exact match falls from 17.58
  to 0.15 (`wang-2024`). Fine-tuning on one format overwrites the output format of unrelated tasks
  while target accuracy rises.
- **Empirical finding (same pattern in reasoning distillation, small students).** FlanT5 250M to 11B
  specialised on GSM8K chains of thought from code-davinci-002 gain 8.9 to 13.3 points on GSM8K while
  BIG-Bench Hard with chain of thought falls from 25.9-41.8 to 0.0-0.3 (Fu et al. 2023). PaD students
  (60M to 770M) fall from 12.0-28.1 to 1.7-2.0 on BIG-Bench Hard (Zhu et al. 2024). Qwen2.5-7B
  after SFT on 15.6K math solutions from Qwen3-14B scores 1.1 on MMLU-Pro against 45.7 after RL
  (Hou et al. 2026). Chu et al. (2025): SFT drops out-of-distribution rule variants from 11.5 to 3.4
  (GeneralPoints) and 80.8 to 1.3 (V-IRL), and RL started from an overfitted SFT checkpoint "collapses
  to the training rule".
- **Hypothesis (S1 reading).** C and K2 learned "the answer is `\boxed{number}`", not that R is
  beyond a 0.8B. The untrained 0.8B scores 55.9 on R. The C and K2 checkpoints are the overfitted
  case: Chu et al. found RL could not rescue overfitted SFT checkpoints, so any further arm should
  restart from the released 0.8B or from a mixed-format warm-up, not from C or K2.

**2. Cheap mitigations of narrowing and forgetting, with sizes**

| Mitigation | Evidence (model size) | Effect size | Cost here |
|---|---|---|---|
| Mix formats and tasks in the SFT set | ProMoT multi-task (13B); Fu et al. (250M-11B); Hsieh et al. (220M-11B) | Unseen-task average +2.54 multi-task against −2.10 single-task; training on in-context-format data keeps zero-shot ability while zero-shot-format data loses in-context ability, so mix formats; rationale and label as two tasks beats one combined output (ANLI 49.58 against 43.50 at 220M) | Data only |
| Self-distilled targets (SDFT: the student rewrites the teacher's answer) | Llama-2-7b-chat, LoRA and full FT (`yang-2024`); finance (Hayrapetyan 2026, 13a) | Full FT on GSM8K: target 34.87 against 35.03, off-target OpenFunctions 5.36 against 16.07 (seed 19.60); finance: plain SFT −3.2 to −4.0, self-distilled +1.0 to +2.8 | One student generation per item |
| Weight averaging with the starting model (WiSE-FT style) | OpenLLaMA-3B, Mistral-7B (Lin et al. 2024) | Pareto front above nearly all other methods tried (early stopping, L1/L2, LoRA, KD, moving average), beating experience replay on 2 of 3 benchmarks; α = 0.2 kept alignment reward; layer-wise variant improved every metric on Zephyr-7B-β (win rate 8.10 to 9.32, reading 37.47 to 38.93) | None: arithmetic on checkpoints already on disk |
| LoRA instead of full FT | Llama-2-7B (Biderman et al. 2024); Qwen3-1.7B (Liu et al. 2026) | Code IFT: retained-ability average 0.509 (LoRA r=64) against 0.414 (full); math IFT under 1 point apart; LoRA r=16 learns less (GSM8K 0.580 against 0.642). LoRA warm-up keeps out-of-domain ability better than full-SFT warm-up before on-policy distillation | Less memory than full FT |
| Soft prompt absorbs the format (ProMoT) | mT5-XXL 13B; fails on PaLM 8B (`wang-2024`) | TriviaQA 0.15 (standard) against 17.64 (ProMoT); unseen-task average +2.58 | Custom prompt-tuning loop; untested below 8B |
| Replay of general data | Lin et al. 2024 only (3B) | Beaten by weight averaging on 2 of 3 benchmarks | Needs general data in S1's formats |

- **Empirical finding.** The self-teacher variants need a capable student: on-policy SDFT with a
  demonstration-conditioned copy of the model as teacher beats SFT by about 4 points at 7B and 7 at
  14B but loses to SFT at 3B (Shenfeld et al. 2026). A 0.8B rewriter is untested (open question).
- **Gap.** No quantified replay-ratio study below 3B was found.

**3. On-policy data, not the RL objective, is what limits forgetting**

- **Empirical finding (`chen-2026`, 1B and 1.5B).** SFT on a 70B teacher's correct answers costs 6.2
  to 29.5 points of non-target accuracy; GRPO costs −0.6 to 1.6. Self-SFT on the model's own correct
  answers, generated once (S1's D2), still costs 3.0 to 34.6. REINFORCE forgets as little as GRPO and
  dropping the KL term changes little: the on-policy sampling carries the effect. Regenerating the
  self data at the start of each epoch (Iterative-SFT) gives SFT-level target gains with "mild to no"
  forgetting (figure only).
- **Empirical finding (`li-2026`, 0.6B).** On-policy distillation does not stop a small student from
  answering in non-thinking mode, but in thinking mode the 0.6B loses its stops (closure 0.583 to
  0.113; samples with no answer 0.328 to 0.579).
- **Consequence for S1 (hypothesis).** A round-based scheme (student samples, teacher scores, student
  trains, repeat) should give most of the retention benefit of fully on-policy training and fits a
  12 GiB machine because the two models never need to be resident together.

**4. On-policy (logit) distillation beats RL for same-family small students, up to a ceiling**

- **Empirical finding (`yang-2025`, Qwen3-8B).** From the same off-policy-distilled checkpoint, on-policy
  distillation from a 32B or 235B teacher reaches AIME'24 74.4 and AIME'25 65.5 against 67.6 and 55.5
  for RL, at 1,800 against 17,920 GPU hours, and raises pass@64 (90.0 to 93.3) where RL does not.
  Every Qwen3 model from 0.6B to 14B was built by off-policy then on-policy distillation.
- **Empirical finding (sub-1B students).** MiniLLM (reverse KL, on-policy) at GPT-2 120M: 44.7 GPT-4
  score on DollyEval against 38.6 SFT, 40.3 word-level KD, 41.2 sequence KD (Gu et al. 2024). GKD with
  T5 students from 77M: at least 25% on-policy data needed, fully on-policy usually best, sampling
  costs 1.8 to 2.2 times a fixed dataset (Agarwal et al. 2024; most numbers in figures only). On
  exposure bias, MiniLLM's accumulated error stops growing after about 150 tokens while the
  baselines' keeps growing (figure only).
- **Empirical finding (the ceiling, `li-2026`).** Qwen3-8B into Qwen3-0.6B, non-thinking: lenient p@1
  0.048 to 0.328 against a teacher 0.595. Of that, the marked-answer rate rose +0.633 and the accuracy
  of marked answers only +0.092. In all 27 cells the distilled p@1 stays below the starting student's
  p@n (0.6B: 0.512). The 0.6B ends at chance on GPQA-Diamond (0.234 against 0.250).
- **Empirical finding (closest teacher ratio to S1).** Qwen3-0.6B thinking with Qwen3-4B-Thinking as
  teacher: in-domain 42.36 after on-policy distillation, 43.81 with a LoRA warm-up first; Qwen3-1.7B
  non-thinking with a 4B teacher: in-domain 12.81 to 38.34 and out-of-domain 40.51 to 47.43 (Liu et
  al. 2026, Simple-OPD; no seeds). Incorrect teacher traces warm up as well as correct ones
  (35.2-36.5), so the warm-up transfers a pattern, not answers.
- **Open question.** Every on-policy distillation result read is math, code or instruction following.
  None is on label-answer analytical items, and none uses a quantised teacher.

**5. RL with verifiable rewards on small models: smaller gains, larger cost, contested generalisation**

- **Empirical finding.** DeepSeek-R1: RL for 10K+ steps on Qwen-32B-Base reaches AIME 47.0; SFT on R1
  outputs reaches 72.6. The 1.5B distilled by SFT alone (800K samples, no RL) scores 28.9 AIME and
  83.9 MATH-500 (Guo et al. 2025).
- **Empirical finding.** Zero-RL on Qwen2.5-0.5B lifts a six-benchmark math average from 12.1 to 20.9
  (GSM8K 36.7 to 49.5; AIME 0 to 0); strict format rewards slowed learning at 7-8B (Zeng et al.
  2025). In finance (13a): RL after SFT adds 1.4 (Fin-o1) and 3.3 (Fin-R1).
- **Empirical finding (generalisation, contested).** Chu et al. (2025, Llama-3.2-Vision-11B): RL
  +3.5 and +11.0 on out-of-distribution rule variants where SFT loses 8.1 and 79.5; SFT is still
  needed first to fix the output format. Hou et al. (2026, Qwen2.5-7B): with matched rollout budgets
  SFT generalises about as well as RL, and SFT data sampled from the RL-tuned model itself, or a mix,
  beats data from a larger model (MMLU-Pro 21.3 for a 70/30 mix, 19.4 on RL-model data, 1.1 on
  Qwen3-14B data, 45.7 for RL).
- **Empirical finding (caution for Qwen).** Random rewards lift Qwen2.5-Math-7B on MATH-500 by 21.4
  points against 29.1 for true rewards, with no such effect on Llama3 or OLMo2 (Shao et al. 2025). RL
  gains on Qwen students can be elicitation of existing behaviour.
- **Hypothesis (S1).** R's label items have 2 to 4 options: a reward on them pays a guessing student
  25-50% of the time, and the 0.8B already scores 55.9. RL is a comparison arm at most, with a
  random-reward control and balanced-accuracy scoring. For the same reason pass@k is inflated by
  guessing on label items (16 samples over 3 options almost always hit the label), so the ceiling
  diagnostics of `li-2026` and Yue et al. apply directly only to S1's numeric templates.

**6. What "teaching a framework" looks like in the distillation literature**

- **Empirical finding.** Multi-task rationale and label (separate prefixes; rationale not generated at
  test) beats label-only and beats rationale-then-label in one output: 220M T5 ANLI 49.58 against
  43.58 and 43.50 (Hsieh et al. 2023).
- **Empirical finding.** Programs beat free-text chains for 60M-770M students with the same teacher:
  GSM8K 21.7 against 13.46 at 770M; full PaD 44.9 against 7.5 for fine-tuning (Zhu et al. 2024). S1's
  calculator already supplies the executable part.
- **Empirical finding.** Labelling each teacher step with one of 7 discourse-level signals and training
  the student to predict the signal and then the step lifts a 0.5B from about 0.49 (CoT SFT) to 0.61
  on a five-task average, at 2.9 to 6.9 times the tokens, with GPT-4.1 labelling and a change to the
  model (Wen et al. 2025).
- **Empirical finding (13a, `li-2025`).** Up to 3B, short traces teach better than long ones; up to
  1.5B, a small teacher teaches better than a large one. `li-2026`: thinking-mode distillation into 0.6B breaks stopping.
- **Hypothesis (S1).** The evidence-backed form of a "framework" for a 0.8B is a short, fixed-shape
  rationale (which lines, which comparison, which direction) written by the 4B in non-thinking mode,
  trained as a separate task beside the label. Discourse scaffolds are a later option. No paper tests
  analytical frameworks in finance below 1.5B (gap).

**7. Cost on one 12 GiB MLX machine (estimates)**

Local timings: full FT of the 0.8B at sequence 512, batch 1, gradient checkpointing, about 5.5 s a
step, peak 7.4-8.1 GiB, about 5.5 hours for two epochs of 1,850 items (EXP-0014, EXP-0017); greedy
generation per R item 4.7 s for the 4-bit 4B, 2.7 s for the released 0.8B, 0.7 s for the terse
distilled 0.8B (EXP-0050). `mlx-lm` provides LoRA, DoRA and full SFT with prompt masking, gradient
checkpointing and adapter fusing, but no distillation, DPO or RL objective
([LORA.md](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md)); anything beyond SFT is a
custom loop. The times below are hypotheses scaled from those timings for about 2,000 items.

| Method | Teacher passes | Student samples | Memory | Rough time |
|---|---|---|---|---|
| Weight averaging of C or K2 with B0 | 0 | 0 | evaluation only | about 0.5 h per α on R and B development |
| Mixed-format off-policy SFT (B + R + general, short rationale + label) | 1 generation per item | 0 | 8.1 GiB peak, as now | labels 1-3 h, training about 6 h |
| SDFT rewrite before SFT | 0 | 1 generation per item | as SFT | +1-1.5 h |
| Offline top-k logit KD on teacher text (D4) | 1 prefill per item, top-20 saved | 0 | teacher and student not co-resident | +about 1 h scoring |
| Round-based on-policy distillation (sample, score, train; 2-3 rounds) | 1 prefill per student sample per round | 1 per prompt per round | not co-resident | about 4-5 h per round |
| Fully on-policy distillation | 1 prefill per step | 1 per prompt per step | 4-bit 4B (about 3 GiB) + 0.8B full FT (8.1 GiB): tight; LoRA student easier | similar per sample; both models in one process |
| GRPO / RLVR | 0 | 5-8 per prompt | as SFT | about 8-10 times SFT per prompt per epoch (8 generations and 8 training sequences): 25-40 h for 2,000 prompts |

The Qwen3 GPU-hour ratio (RL about ten times on-policy distillation) points the same way.

## Look-ahead and memorisation across the stream

Not relevant to these method papers, which train and test on public math, code and NLP sets. Only
`li-2026` removes training problems that overlap the evaluation sets (1,139) and uses a benchmark
newer than the models (AIME 2026). DeepSeek-R1 and Qwen3 report no overlap checks. For S1 the
contamination rules already in force (pre-cutoff training releases, post-cutoff test releases, no
model labels a test item) carry over unchanged to every method here.

## Design implications for S1 (R-c and beyond)

1. **First, two zero-training diagnostics (about 2-3 hours).** (a) Interpolate C and K2 with the
   released 0.8B at α in {0.2, 0.4, 0.6, 0.8} and score R and B development: if R labels return while
   B holds, the collapse sits in a direction weight averaging can undo (Lin et al. 2024). (b) Sample
   B0 n = 8-16 times per R development item (temperature 0.6-1.0). On numeric templates report p@n:
   on-policy methods cannot lift p@1 above it (`li-2026`; Yue et al. 2025). On label templates p@n is
   inflated by guessing, so report the per-item share of correct samples against chance and the
   majority-vote score instead. If many items are answered right well above chance in some samples,
   on-policy distillation has something to sharpen; if not, off-policy teacher data must add the
   behaviour first.
2. **Default warm-up: mixed-format off-policy SFT from the 4B, restarted from B0.** B and R items
   together, each with a short non-thinking rationale and the answer in its own format (number or
   label), rationale and answer as two tasks (Hsieh et al. 2023), plus a slice of general items in
   other formats (Fu et al. 2023; `wang-2024`). Hold out R families. Compare LoRA against full FT, or
   full FT followed by averaging with B0, on section A (Biderman et al. 2024; Lin et al. 2024).
3. **Main new arm: round-based on-policy distillation from the 4B**, same tokenizer, non-thinking
   mode, per-token reverse KL or top-k forward KL on the student's own samples (`yang-2025`; Gu et al.
   2024; Agarwal et al. 2024), two or three regenerate-score-train rounds (`chen-2026`). Check the loop
   against a reference on 10 items as planned for D4. Teacher: the 4B, not the 9B (`li-2025`), with the
   9B 4-bit as an ablation only; gpt-oss-20b has a different tokenizer and can supply text only.
4. **RL only as a comparison arm**, from the warm-up checkpoint, with a random-reward control (Shao
   et al. 2025), balanced-accuracy reward on label items and a cap on rollouts. Expect a few points at
   most (13a) at about eight to ten times the cost per prompt (table in point 7).
5. **Every arm reports** R by family (seen and held out), B, section A, and the student's KL to B0 on
   R prompts (`chen-2026`), with checkpoints selected on R development only (Fu et al. 2023 show
   in-distribution selection does not pick the best out-of-distribution checkpoint; stream 05).
6. **Prior (hypothesis).** Mixed-format SFT should restore R to at least B0's 56 while keeping most of
   B; on-policy distillation should add a few points on R and lose least on section A. Reaching the
   4B's 82 would be new evidence: no paper shows a sub-1B student matching a 5-times-larger teacher
   outside its training format.

## Reusable

- Clipped per-token reverse-KL advantage from one student sample and one teacher scoring pass
  (`li-2026`, Eq. 1); the answer-marked / correct / stopped scoring split.
- Iterative-SFT schedule (`chen-2026`); code at https://github.com/princeton-pli/retaining-by-doing.
- SDFT rewrite template and filtering rule (`yang-2024`); code at https://github.com/sail-sg/sdft.
- Layer-wise model averaging (Lin et al. 2024); code linked from the paper.
- MiniLLM and GKD reference implementations, for checking an MLX distillation loop.

## Gaps that suggest an experiment

- No on-policy distillation or RL study on label-answer or analytical items, in finance or elsewhere,
  below 1.5B.
- No test of distillation from a 4-bit quantised teacher's logits.
- No quantified replay ratio for sub-3B students; no weight-averaging study below 3B.
- No study of whether a 0.8B can rewrite a 4B answer (SDFT) without degrading it.

## Not triaged

- Excluded by rule (blog posts): DeepScaleR; the Thinking Machines on-policy distillation post that
  `li-2026` follows.
- Read in part but not kept as rows, to stay near the triage cap, because a kept row makes the same
  point: RL's Razor (Shenfeld, Pari and Agrawal 2025, arXiv 2509.04259; RL forgets less than SFT at
  Qwen2.5-3B, as `chen-2026` shows at 1B and 1.5B); Tina (arXiv 2504.15777; LoRA RL on a 1.5B,
  abstract only); Dang and Ngo (arXiv 2503.16219; GRPO on a 1.5B, abstract only). Nothing in the
  synthesis rests on them.
- Seen in search results only, nothing claimed: Struct-SQL, D-CoT, Reopold, Trust Region On-Policy
  Distillation, CaMOPD (multi-teacher recovery of general ability after domain tuning), "RL
  Fine-Tuning Heals OOD Forgetting in SFT", and an on-policy distillation survey (arXiv 2604.00626).
