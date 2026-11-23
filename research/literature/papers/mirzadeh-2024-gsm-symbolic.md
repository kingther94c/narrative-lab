# GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models

- **Citation:** Iman Mirzadeh, Keivan Alizadeh, Hooman Shahrokhi, Oncel Tuzel, Samy Bengio and
  Mehrdad Farajtabar (2024). arXiv 2410.05229; v2 of 27 August 2025 marked "ICLR camera ready"
  (v1, 7 October 2024). Version read: v2, HTML.
- **Link:** https://arxiv.org/abs/2410.05229 (HTML read: https://arxiv.org/html/2410.05229)
- **Stream:** 13b, reasoning item design (item generation by template and perturbation)
- **Verified against source:** yes, 2026-11-23. Abstract page and the HTML main text and
  appendices up to part of Appendix B, read through a machine extraction (first 100,000 of
  103,763 characters). Figure 4 (names-only against numbers-only) read by its description only.

## Question
Do benchmark scores on grade-school maths word problems (GSM8K) measure reasoning, or do they
reflect patterns matched from training data? Test: regenerate each question from a symbolic
template and see whether accuracy holds when names, numbers or the number of clauses change.

## Data
100 GSM8K test questions as seeds. Each becomes a template with typed variables, value ranges and
validity conditions (for example divisibility so the answer is a whole number). 50 instances per
template, arranged as 50 datasets of 100 questions (5,000 items per variant). More than 20 open
models from 2B to 27B, plus GPT-4o-mini, GPT-4o, o1-mini and o1-preview (about 25 models, nearly
500 evaluations).

## Method
- Template checks: no original value left in the template; the original values satisfy all
  conditions and reproduce the original answer; every generated question answered correctly by
  at least two models or re-reviewed by hand; 10 random instances per template checked manually.
- Variants: names only, numbers only, both; M1 (one clause removed), P1 and P2 (one or two
  clauses added); NoOp (a plausible but irrelevant statement added).
- 8-shot chain of thought, greedy decoding (o1 models excepted, since their APIs did not allow
  it). One-sample t-test of the 50 dataset scores against the original 100-question score.

## Outcome variable and horizon
Exact-answer accuracy per dataset; its mean and standard deviation across the 50 datasets. Not a
forecasting task.

## Result
Empirical findings.

- **Variance across instances of the same templates is large.** Gemma2-9B's best and worst
  dataset differ by more than 12 points, Phi-3.5-mini's by about 15. For 21 of 25 models the
  original GSM8K score sits more than one standard deviation above the centre of the
  GSM-Symbolic distribution.
- **Numbers matter more than names.** Changing only names gives lower variance and smaller drops
  than changing only numbers (figure-level finding; exact values not in the text).
- **Difficulty by clause count (Table 1, mean over 50 datasets).** Llama3-8B: 74.6 on
  GSM-Symbolic, 53.8 on P1, 12.3 on P2. Phi-3-mini: 80.7, 63.4, 37.5. GPT-4o: 94.9, 93.9, 88.0.
  o1-preview: 92.7, 95.4, 94.0.
- **Irrelevant information (NoOp).** Phi-3-mini 18.0, Gemma2-9B 22.3, GPT-4o 63.1, o1-preview
  77.4, against 80.7, 79.1, 94.9 and 92.7 on the base variant. The abstract reports drops of up
  to 65%.
- **Not arithmetic.** For Gemma2-9B-it, the arithmetic steps alone stay at 97 to 99% correct on
  every variant, so the P2 drop is not computation errors (Table 2).
- **Training on the harder variant does not transfer.** Fine-tuning on P1 helps P1 and lowers
  P2; P1 examples as shots do not help P2.

## Look-ahead and memorisation
Contamination of GSM8K is offered as one explanation, not demonstrated. The design itself is the
defence: instances are fresh draws, so a memorised seed answer is not reusable.

## What it settles for us
- **The template-and-variant design is the standard way to separate procedure from recall.** For
  S1, every reasoning item should be a template with typed slots, validity conditions and the
  answer computed from the slots, which is how EarningsExam B2 already works. What is new is the
  family of controlled variants.
- **Two controls to copy.** (i) A numbers-only variant: same release wording, different figures
  that keep the statements adding up. (ii) A NoOp variant: an irrelevant line inserted (a
  footnote, a non-recurring item that does not affect the asked quantity). The first measures
  dependence on the numbers; the second measures whether the model picks the relevant facts,
  which is closer to the owner's "integrating several pieces of information".
- **Report a distribution, not a point.** Score several instantiations per template and report
  the spread; a 0.8B against 4B gap of three points is inside the across-instance spread these
  authors found for 9B models (our inference; S1 already clusters by company, and should also
  cluster by template).
- **Clause count is a usable difficulty axis.** Adding one or two required facts degraded small
  models far more than frontier ones; this is the dimension on which a distilled student is
  likely to fall behind its teacher (hypothesis).

## Limits
- Grade-school arithmetic, not finance; the "reasoning" tested is short procedural composition.
- The authors acknowledge the significance tests rest on i.i.d. and normality assumptions that
  may not hold; with a two-sample test the differences would not be significant (Ivanova et al.,
  as cited by the authors).
- Added or removed clauses do not map one-to-one onto reasoning steps.
- Templates were written by annotators; that cost scales with the number of templates, not
  instances.
