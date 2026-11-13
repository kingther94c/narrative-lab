# All That Glisters Is Not Gold: A Benchmark for Reference-Free Counterfactual Financial Misinformation Detection

- **Citation:** Jiang, Y., Liu, Z., Cao, Y., He, Y., Xu, Z., Xu, C., Deng, Z., Tiwari, P., Chen, X., Lopez-Lira, A., Huang, J., Tsujii, J., and Ananiadou, S. (2026). arXiv preprint 2601.04160. Version read: v3 (9 January 2026), HTML, main text and appendices. No peer-reviewed venue is named.
- **Link:** https://arxiv.org/abs/2601.04160 (data: https://huggingface.co/datasets/CarolynJiang/RFC-Bench-Dataset; code: https://github.com/lzw108/FMD)
- **Stream:** 04 Financial NLP benchmarks and data sets
- **Verified against source:** yes, 2026-11-12

## Question

Can LLMs tell that a paragraph of financial news has been minimally altered when they see only the
altered paragraph, and how much easier is the task when the original is shown beside it?

## Data

- Text source: 1,404 Yahoo Finance articles (title and summary) on 223 listed stocks, published
  25 April to 15 December 2025. News, not company disclosures. Delisting is not relevant here.
- RFC-BENCH: 1,826 pairs of an original paragraph and a perturbed one, down from 2,042 before
  adjudication. By type: numerical perturbation 703, directional flipping 532, causal distortion
  338, sentiment amplification 253.
- Release: rewritten text plus ticker, date and source URL. The original article text is not
  redistributed. A set of hard cases is released separately.
- Licence: the Hugging Face card and the code repository are tagged MIT. The paper states only
  that the data is for academic use.

## Method

- Generation: GPT-4.1 with one prompt per perturbation type and low temperature.
- Constraints on each rewrite: no new entities or facts; a bounded length ratio to the original
  (for example 0.85 to 1.25 for numerical edits); a FinBERT polarity check for sentiment edits.
  Numerical edits must change every numeric expression, keep the direction, and leave dates,
  identifiers and all non-numeric content alone. Directional flips keep entities, dates and
  numbers. Sentiment edits keep every fact and number. Causal edits change only the stated cause.
- Validation, in three layers:
  1. Expert A (a doctoral student with finance and machine-learning degrees) reviewed and
     corrected every rewrite.
  2. Expert B (a finance professional) audited a stratified sample: 10% of flipping and numerical
     items, 15% of sentiment and causal items. Pass rates were 96.4% (flipping), 96.1%
     (numerical), 93.2% (causal) and 80.9% (sentiment). A batch below 80% went back for revision.
  3. Two trained annotators (master's students) rated each item on category correctness and on
     rewrite validity. Borderline cases went to expert adjudication.
- Agreement: category correctness, accuracy 0.988 and Gwet's AC1 0.989 (the authors note Cohen's
  kappa is unstable here because the labels are highly imbalanced). Rewrite validity, accuracy
  0.937, Cohen's kappa 0.720, AC1 0.896. Kappa by type: numerical 0.855, flipping 0.708, sentiment
  0.686, causal 0.632.
- Retention after adjudication: flipping 95.5%, numerical 90.7%, causal 85.6%, sentiment 80.3%.
- Two tasks. Task 1: reference-free binary detection on a single paragraph. Task 2: the model sees
  the original and the perturbed paragraph and names the manipulation type (four classes).
  Fourteen models, zero-shot, with few-shot variants for Task 1.

## Outcome variable and horizon

Accuracy, macro-F1 and MCC per task, plus the count of invalid (unparseable) outputs. No market
outcome and no horizon.

## Result

All are empirical findings. No intervals are reported.

- Task 1, single paragraph: accuracy across the fourteen models lies between 45.2% and 53.6%,
  with MCC near zero or negative. Few-shot prompting lifts GPT-4.1 only to 58.4%.
- Task 2, paired: GPT-5 Mini 97.7%, GPT-4.1 96.9%, GPT-5.2 96.8%, DeepSeek-reasoner 93.6%,
  Qwen2.5-72B 92.1%, LLaMA 3.1-8B 57.5%.
- The gap between the two framings is about 44 points for GPT-4.1 (52.7% to 96.9%).
- Invalid outputs are a large part of small-model failure: LLaMA 3.1-8B returned 1,099 invalid
  answers in Task 1 and 886 in Task 2; Qwen2.5-72B 975 in Task 1.
- Not reported in the text read: accuracy by perturbation type, the Task 1 class balance, and a
  false-positive rate on unaltered paragraphs.

## Look-ahead and memorisation

Not addressed. The collection window is stated but is not related to any model's training cutoff.
The rewrites are synthetic and cannot have been memorised, but the originals are public news, so a
model could in principle spot an altered figure by recall; the paper does not test this. One error
case shows a model treating a 2025 claim as unverifiable because it assumed an earlier current
year.

## What it settles for us

- **Do minimal pairs exist in financial NLP? Yes (verified fact), but not for our purpose.** They
  exist for news and for detecting manipulation. None was found for company disclosures, for
  guidance, or for testing whether a label stays put or moves when only numbers or only wording
  change.
- **Sub-task 3, minimal pairs (supports the design and gives a recipe).** Controlled rewriting
  under explicit invariance constraints, with an expert audit, is an accepted way to build pairs
  whose label is known by construction. The four constraint sets map onto our two arms: the
  numerical type is our numbers-only edit; the sentiment type is our wording-only edit.
- **Where human checking is needed (changes the pilot).** Numeric edits were the most reliable
  (kappa 0.855, 96.1% audit pass, 90.7% retained); wording edits the least (kappa 0.686, 80.9%
  pass, 80.3% retained). Budget for losing about a fifth of wording-only candidates, and check
  that arm more heavily than the numeric one.
- **Framing decides difficulty (changes the endpoint wording).** Strong models are near chance on
  a single paragraph and near ceiling when shown both. Our consistency endpoint should present
  each member of a pair separately and compare the two labels afterwards. Showing both together
  would measure reading a diff, which large models already do.
- **Goal C.** An 8B model scores 57.5% where large models score above 92%, and much of the loss is
  invalid output. A paired financial task can separate small from large models, and output
  validity needs its own pre-registered rule (count as wrong, or report separately).
- **Gold labels checked by one human (partly contradicts).** Even for labels known by
  construction this paper used two experts and two annotators and still removed about 11% of
  items. One checker is below the convention here; test-retest has to carry that weight.
- Reuse: the perturbation taxonomy and constraint lists (Appendices S and T); the two-question
  check per item (is the category right, is the rewrite valid); AC1 next to kappa when one class
  dominates. The data itself is news and is useful only as an out-of-domain probe.

## Limits

- News summaries, not filings or press releases; English and US market only.
- One generator (GPT-4.1), which is also among the evaluated models.
- Counts are inconsistent across sections (1,826 pairs against 1,845 instances in an appendix;
  123 against 122 hard cases; two different "best" Task 1 figures).
- Paragraphs are judged in isolation; no retrieval and no per-type results in the text read.
