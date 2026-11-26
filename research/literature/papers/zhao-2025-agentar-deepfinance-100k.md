# Agentar-DeepFinance-100K: A Large-Scale Financial Dataset via Systematic Chain-of-Thought Synthesis Optimization

- **Citation:** Zhao, X., Zhou, Z., Chen, L., Wang, L., Huang, Z., Zheng, K., Zheng, Y., Du, X.,
  Liao, L., Liu, J., Qi, X., Zhang, B., Zhang, P., Wang, W. and Li, Z. (2025). arXiv 2507.12901
  (cs.CE), Ant Group. Version read: v3 (9 November 2025); HTML, main text and tables 1-6.
- **Link:** https://arxiv.org/abs/2507.12901 (HTML: https://arxiv.org/html/2507.12901v3)
- **Stream:** 14c
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v3 HTML through
  an automated page reader. Figures (task-domain counts, the incorrect-sample comparison) were not
  readable as text. No number was checked against a typeset PDF.

## Question

Which choices in synthesising chain-of-thought data from large reasoning models make a better
financial student: whether to include the chain at all (by difficulty and task type), how long
it should be, and which model should write it?

## Data

- Sources (Table 1): FinCorpus 61,574; FinCUGE 18,527; Finance-Instruct-500K 10,343; FinQA 5,012;
  FinancialData 4,047; Quant-Trading-Instruct 89; in-house FinCAS 15,190; in-house FinRA (count
  not printed). The table sums to about 115K; the text says 99K open plus 16K in-house; the title
  says 100K. Mostly Chinese.
- Six task domains: Knowledge QA, NLP, Analysis & Interpretation, Math, Compliance & Security, Text
  Generation. Knowledge QA and NLP are over 70%; Text Generation under 1%.
- Chains written by QwQ-Plus (chosen after comparing DeepSeek-R1 and Qwen3-235B-A22B). Items with
  LLM-rated quality under 8 dropped; sampled answers checked against gold by a lightweight model
  (unnamed).
- Question creation ("multi-perspective knowledge extraction"): harvested QA pairs (Q2A),
  counterfactual answers with generated questions (A2Q), and QA pairs mined from summarised
  chains (T2Q). Failed samples are repaired by "self-corrective rewriting": the model reflects on
  the gap to the gold answer and rewrites, iterating.

## Method

All student runs: Qwen2.5-7B-Instruct, 3 epochs, a 60K subset. Evaluation: FinQA (LLM judge,
unnamed), Fin-Eva (Ant split; rule-graded MCQ and true/false), a 10% held-out slice of each task
subset, MATH-500, GPQA-Diamond.

## Outcome variable and horizon

Accuracy. No horizon.

## Result

- **Empirical finding (chains matter more on hard items).** FinQA / Fin-Eva: base 63.47 / 83.70;
  easy items without chain 67.65 / 84.21, with chain 68.96 / 85.01; hard items without chain
  63.03 / 75.80 (below base), with chain 69.31 / 85.96.
- **Empirical finding (by task type, held-out 10% slices; answer-only to with-chain).** Math 31.71
  to 61.15; Text Generation 74.55 to 83.64; Analysis & Interpretation 81.36 to 88.05; Compliance
  91.25 to 92.02; Knowledge QA 78.32 to 79.01; NLP 76.71 to 77.21. Average 72.32 to 80.18. How
  these slices are graded is not stated.
- **Empirical finding (the best model is not the best teacher).** As chain writers on the same
  questions, DeepSeek-R1 is the strongest teacher (FinQA 75.41) but its student scores 66.52;
  QwQ-Plus as teacher scores 72.97 and its student 68.79 (+2.27 FinQA, +0.21 Fin-Eva over the R1
  student). Qwen3-235B-A22B student 66.43.
- **Empirical finding (long chains better for a 7B student).** Training on long, medium and short
  QwQ chains (average 1,352, 1,248, 1,020 tokens): FinQA 68.79, 65.13, 65.56; Fin-Eva 85.53,
  85.40, 85.19.
- **Empirical finding (repair).** On FinQA, 1,337 of the training items had no correct sample in
  four; training on the 862 repaired by self-corrective rewriting added +1.74.
- **Empirical finding (question mining).** Fin-Eva: Q2A alone +3.09; adding T2Q +1.12; adding A2Q
  +1.47 (baselines not fully stated).
- Distilled students also rise on MATH-500 (73.20 to 80.00-81.60) and GPQA (37.88 to
  41.41-42.42).

## Look-ahead and memorisation

The paper says instances overlapping benchmark test sets were removed from the open data, without
naming method or counts. FinQA is both a training source and a test set; no explicit statement that
the FinQA test split was excluded. In-house data unchecked. No outcome labels, so outcome recall
does not arise.

## What it settles for us

- Supports training R-d on rationale plus answer, never answer only: at 7B, answer-only training on
  hard items fell below the base model (Fin-Eva 83.70 to 75.80), the same failure shape as
  EXP-0050's distilled 0.8B arms boxing a number on every label item.
- "Analysis & Interpretation" gains +6.7 from chains, Math +29.4, classification-like NLP +0.5:
  the chain earns its keep where several steps are combined, which is section R.
- Teacher choice must be made by training a student and testing it on dev, not by the teacher's own
  score. For S1: compare 4B, 9B and gpt-oss-20b traces by the 0.8B's dev result.
- Chain length: long beat short at 7B, while `li-2025` (13a) found students up to 3B learn better
  from short chains. The 0.8B sits on the other side of that line; the length mix stays an
  experiment, not a default.
- Repair of failed items (reflect, rewrite, re-verify) is a cheap way to keep hard items, which in
  S1 can be verified by rule against XBRL instead of a model judge.

## Limits

One student (7B); a 60K subset rather than the full set; no final model on all data; held-out slices
are from the same pools; judge and verifier unnamed; table counts disagree with the text; mostly
Chinese data; single runs.
