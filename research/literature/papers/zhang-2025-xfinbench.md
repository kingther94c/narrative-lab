# XFinBench: Benchmarking LLMs in Complex Financial Problem Solving and Reasoning

- **Citation:** Zhang, Z., Cao, Y. and Liao, L. (2025). Findings of ACL 2025, pp. 8715-8758, doi
  10.18653/v1/2025.findings-acl.457. Version read: arXiv 2508.15861v1, HTML (first two-thirds of the
  page; the remaining appendix was not read).
- **Link:** https://aclanthology.org/2025.findings-acl.457/ (HTML: https://arxiv.org/html/2508.15861v1)
- **Stream:** 13a
- **Verified against source:** yes, 2026-11-23, against the ACL Anthology page and the HTML through an
  automated page reader.

## Question

Which kinds of graduate-level financial reasoning do LLMs handle, and where do they fall short of
human experts?

## Data

- 4,235 items (1,000 validation, 3,235 test) from end-of-chapter questions in three graduate
  textbooks (corporate finance, derivatives, money and banking). GPT-4o rewrote open questions into
  closed ones under generate-then-verify; 35.2% of generated items discarded. Experts tagged each
  item with one to three finance terms; three raters scored quality.
- Formats: statement judging (true/false) 1,795; three-option MCQ 761 (146 with images); numeric
  calculation 1,679 (330 with tables). A 3,032-term knowledge bank comes with it.
- Capabilities (share): terminology 56.1%, temporal reasoning 21.7%, future forecasting 5.0%,
  scenario planning 7.6%, numerical modelling 17.2%.
- Test answers withheld. Dataset licence not stated in the text read.

## Method

CoT for all formats, program-of-thought for calculation. 18 models. Calculation scored within 0.5%
of the answer by default. Retrieval arms (BM25, embeddings, oracle terms). Three master's-level
finance experts answered a 1,000-item subset closed-book under time limits.

## Outcome variable and horizon

Accuracy per format and capability. No horizon.

## Result

- Overall: o1 67.3 (best text-only), Claude 3.5 Sonnet 64.1, GPT-4o 63.6, Llama-3.1-8B 45.5,
  Llama-3-8B 42.9, Mixtral 8×7B 16.6; experts 79.8.
- Per capability (terminology / temporal / forecasting / scenario / numerical):
  - o1-preview 88.9 / 59.1 / 74.7 / 60.1 / 66.5
  - GPT-4o 85.4 / 41.4 / 63.6 / 46.3 / 58.7
  - Llama-3.1-8B 68.0 / 11.7 / 49.5 / 22.3 / 27.1
  - experts 91.0 / 79.5 / 86.2 / 75.8 / 78.0
- Empirical finding: models match experts on terminology and trail most on temporal reasoning and
  scenario planning. The 8B model's deficit is largest exactly there (temporal 11.7 against 59.1).
- Empirical finding: program-of-thought often hurt because programs failed to run; calculation
  errors came mostly from rounding intermediate steps and misapplied formulas.
- Empirical finding: oracle knowledge helps most on terminology and least, or negatively, on
  forecasting; the 8B model gains most.
- Three-option MCQ and true/false have chance rates of 33% and 50%, so the 8B's forecasting 49.5
  may be near chance (the mix of formats within that capability was not read).

## Look-ahead and memorisation

Test answers withheld to limit contamination. Textbook questions are likely in pre-training corpora;
not tested.

## What it settles for us

- One of few benchmarks that labels "temporal reasoning" and "scenario planning" separately and
  grades them automatically (true/false, MCQ, numeric). Those are the categories where an 8B model
  is furthest behind a frontier model, so they are candidate discriminating item types for S1.
- Textbook items test knowledge of finance, not reading a company's release; the format (judge a
  statement, pick among three) transfers, the content does not.
- Chance-corrected scoring is needed for true/false and MCQ when comparing small models.
- Retrieval of definitions helps small models; a formula sheet arm in S1 would play the same role
  as FinIndices' hint arm.

## Limits

Textbook domain; GPT-4o-written item stems; no model under 8B; mixed formats per capability make
capability scores hard to compare with chance.
