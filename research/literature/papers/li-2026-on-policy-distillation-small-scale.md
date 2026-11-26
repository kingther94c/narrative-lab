# Solving Without Stopping: On-Policy Distillation at Small Scale

- **Citation:** Li, H., Zhu, Y., Li, X., Wu, C., Mammar, S. and Bouvry, P. (2026). arXiv 2609.37326.
  Version read: v1 (29 September 2026), full text of the PDF (main text and Appendices A to E)
  extracted locally; the HTML rendering is truncated. Preprint; no venue.
- **Link:** https://arxiv.org/abs/2609.37326
- **Stream:** 14b (distillation and training methods for small students)
- **Verified against source:** yes, 2026-11-25, against the abstract page, the v1 HTML (partial) and
  the full text extracted from the v1 PDF. Table values re-read from the extracted text (Tables 1, 3,
  4, 9, 10).

## Question

What does on-policy distillation transfer to small students (4B, 1.7B, 0.6B), in thinking and
non-thinking mode, and where does it stop?

## Data

13,597 DAPO-Math-17k problems after cleaning, deduplication and removal of problems that also occur
in AIME 2024 to 2026, AMC23 or MATH. Evaluation: AIME 2026 (30 problems, 48 samples), AMC23 (40, 48),
GSM8K-200 (200, 32); GPQA-Diamond (198, 8) for the non-thinking route only.

## Method

- Teacher Qwen3-8B; students Qwen3 4B, 1.7B, 0.6B.
- **Non-thinking route:** pretrained-only students distilled from the non-thinking teacher for 212
  steps.
- **Thinking route:** students first fine-tuned on 5,878 short external solutions (OpenR1-Math,
  mean 1,530 tokens) or on 1,524 of the teacher's own correct solutions (mean 4,809 tokens), then
  distilled for 142 steps.
- Loss: one sampled response per prompt; the teacher scores the same tokens; each token's advantage
  is a clipped one-sample estimate of the reverse KL (clip at ±1) in a PPO-style update, no task
  reward. 128 prompts per step, learning rate 3e-6, rollout budget 7,168 tokens.
- Hardware: three nodes of four A100-40GB (teacher on one node under vLLM, student on two).
- Scoring separates whether a sample marks an answer, whether it is right, and whether it stops.
  Paired bootstrap intervals over problems, 10,000 resamples.

## Outcome variable and horizon

Lenient p@1 (any marked answer correct), p@n (solved in at least one of n samples), closure and
truncation rates. No horizon.

## Result

Table 1, three-benchmark mean, lenient scoring (teacher p@1: 0.595 non-thinking, 0.857 thinking):

| Route | Student | p@1 start → after | p@n start → after | after p@1 / teacher p@1 |
|---|---|---|---|---|
| Non-thinking | 4B | 0.427 → 0.549 | 0.736 → 0.791 | 0.922 |
| Non-thinking | 1.7B | 0.294 → 0.440 | 0.646 → 0.725 | 0.739 |
| Non-thinking | 0.6B | 0.048 → 0.328 | 0.512 → 0.593 | 0.551 |
| Thinking, external SFT | 0.6B | 0.238 → 0.294 | 0.591 → 0.521 | 0.343 |
| Thinking, teacher SFT | 0.6B | 0.055 → 0.262 | 0.399 → 0.474 | 0.306 |

- Empirical finding (ceiling 1): in all 27 route-size-benchmark cells the distilled p@1 stays below
  the starting student's p@n; it reaches 0.50 to 0.87 of it.
- Empirical finding (ceiling 2): the smaller the student, the further below the teacher.
- Empirical finding (what the 0.6B gain is made of, Table 9): on the non-thinking route the 0.6B's
  marked-answer rate rises by +0.633 [0.598, 0.667] and the accuracy of marked answers by only +0.092
  [0.065, 0.118]. Most of its p@1 gain (+0.280) is learning to give an answer at all.
- Empirical finding (thinking mode harms small students): the share of samples that close their
  reasoning falls at step 6 in every run (0.6B: 0.583 to 0.113). Samples with no marked answer rise
  from 0.328 to 0.579 at 0.6B; they often contain the correct value early (0.240 of unfinished 0.6B
  samples, four to seven times chance) and run on to the limit. From the teacher-SFT start the 1.7B
  and 0.6B mark 185.5 and 150.3 answers per sample and overwrite correct ones.
- Empirical finding (out of domain, Table 10): on GPQA-Diamond the distilled 0.6B rises from 0.049 to
  0.234 committed p@1, which is chance (0.250); only the 4B ends above chance (0.397).
- Majority vote at 0.6B does not change with distillation (0.400 to 0.398).

## Look-ahead and memorisation

Contamination handled: training problems overlapping AIME 2024 to 2026, AMC23 or MATH (1,139) were
removed; AIME 2026 postdates the models. Look-ahead not relevant.

## What it settles for us

- The closest evidence to S1's scale (0.6B student, same-family teacher about thirteen times
  larger; S1's 4B is about five times the 0.8B). On-policy distillation helps a sub-1B student, and in non-thinking mode it does not break
  answering. Thinking-mode distillation into a sub-1B student should not be S1's default.
- A large part of the small student's gain is format (marking an answer), which on S1's R section is
  exactly what C and K2 lost. On-policy distillation from the 4B on R items would push the student
  towards the teacher's label answers on the student's own outputs.
- The ceiling gives S1 a cheap pre-test: sample the 0.8B (B0, and any warm-up checkpoint) n times per
  R development item. If p@n is not well above the target score, on-policy methods cannot reach it and
  off-policy teacher data must add the behaviour first. This holds as stated for numeric templates
  only: on label templates with 2 to 4 options p@n is inflated by guessing, so the per-item share of
  correct samples against chance (or majority vote) is the usable form.
- Reusable: the scoring split (answer marked, answer correct, stopped) and the clipped per-token
  reverse-KL advantage, which needs only one student sample and one teacher scoring pass per prompt.

## Limits

Math only; one teacher; one seed per configuration (two runs for some); A100 cluster, so no cost
figure transferable to MLX; no comparison with SFT-only or RL arms at matched compute; out-of-domain
check only on GPQA-Diamond for one route.
