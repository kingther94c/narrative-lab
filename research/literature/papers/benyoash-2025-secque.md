# SECQUE: A Benchmark for Evaluating Real-World Financial Analysis Capabilities

- **Citation:** Ben Yoash, N., Brief, M., Ovadia, O., Shenderovitz, G., Mishaeli, M., Lemberg, R.
  and Sheetrit, E. (2025). Proceedings of the Fourth Workshop on Generation, Evaluation and Metrics
  (GEM², ACL 2025); arXiv 2504.04596. Version read: v1 (6 April 2025), HTML.
- **Link:** https://arxiv.org/abs/2504.04596 (HTML: https://arxiv.org/html/2504.04596v1)
- **Stream:** 13a
- **Verified against source:** yes, 2026-11-23, against the abstract page and the HTML through an
  automated page reader. Per-category scores are in a figure and were not read.

## Question

How well do LLMs answer analyst-style questions on SEC filings, and can an LLM-judge panel grade
free-text answers reliably?

## Data

- 45 10-K and 10-Q filings of 29 US companies, filed July 2018 to August 2024. Survivors only by
  construction (named large caps).
- 565 expert-written questions with free-text gold answers and supporting page chunks (about five
  per question, mean about 3K to 5K tokens): comparison and trend analysis 220, ratio analysis 188,
  risk factors 85, analyst insights 72. Written by three finance experts, reviewed by two more.
- Dataset on Hugging Face; paper CC BY 4.0; dataset licence not stated in the text read.

## Method

- Gold context in the prompt (no retrieval); four context renderings (HTML or Markdown tables, with
  or without headers); baseline and "financial" prompts; with and without CoT.
- SECQUE-Judge: GPT-4o scores each answer 0 (wrong), 1 (partly right), 2 (right) five times; the sum
  is mapped back to 0/1/2 by thresholds tuned on human labels.
- Human check: 62 questions, 124 answers (GPT-4o and Llama-3.3-70B).

## Outcome variable and horizon

Judge-scored accuracy under two definitions (strict and normalised; definitions not re-checked). No
horizon.

## Result

- Strict / normalised: GPT-4o 0.69 / 0.79; Llama-3.3-70B 0.65 / 0.75; GPT-4o-mini 0.64 / 0.73;
  Qwen2.5-32B 0.61 / 0.72; Phi-4 (14B) 0.56 / 0.66 (16K context limit); Llama-3.1-8B 0.48 / 0.60;
  Mistral-Nemo (12B) 0.46 / 0.55.
- Empirical finding: smaller models struggle most on comparison and trend questions with long
  contexts; analyst insights is the lowest category for all, and the authors call its grading the
  least reliable. Phi-4 does best on risk factors.
- Empirical finding: a finance-flavoured prompt lowered accuracy (GPT-4o-mini 0.64 to 0.38); CoT
  slightly hurt the baseline prompt. Markdown tables were harder for small models.
- Judge validation: panel F1 for the "correct" class 0.85 (precision 0.905, recall 0.80), accuracy
  0.75 over three classes; single GPT-4o judge 0.82 / 0.71; GPT-4o-mini as judge 0.62 / 0.515. The
  judge separates fully correct answers well and partial from wrong poorly.

## Look-ahead and memorisation

Not addressed. Filings up to 2024 with gold context in the prompt, so memorisation would help only
by shortcut; not tested.

## What it settles for us

- The best-documented open set of analyst-style questions on US filings, with a category split
  (trend, ratio, risk, insight) that maps onto an S1 reasoning exam.
- Grading evidence: even a tuned five-call GPT-4o panel reaches only 0.75 three-class agreement with
  humans on 124 answers, and a small judge is much worse. Rubric-graded items should be a minority
  of an S1 exam and must carry their own human-agreement numbers.
- Size evidence: an 8B model reaches about 70% of GPT-4o's strict score on this kind of question,
  less on long-context trend questions.
- Prompt wording can move a small model by 26 points; S1 must fix prompts on a development split.

## Limits

29 companies; judge validated on 124 answers from two models only; free-text gold where several
calculation routes are valid; no model below 8B.
