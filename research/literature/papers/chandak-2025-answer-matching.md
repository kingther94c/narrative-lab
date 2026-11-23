# Answer Matching Outperforms Multiple Choice for Language Model Evaluation

- **Citation:** Nikhil Chandak, Shashwat Goel, Ameya Prabhu, Moritz Hardt and Jonas Geiping
  (2025). arXiv 2507.02856 v1, 3 July 2025. No venue stated. Version read: v1, HTML.
- **Link:** https://arxiv.org/abs/2507.02856 (HTML read: https://arxiv.org/html/2507.02856)
- **Stream:** 13b, reasoning item design (cheap grading of free-form answers)
- **Verified against source:** yes, 2026-11-23. Abstract page and HTML up to part of Appendix B
  (first 100,000 of 131,136 characters) through a machine extraction. Figure 5, which holds the
  per-matcher agreement values on MMLU-Pro and GPQA, was read by its description only.

## Question
Is multiple choice a valid way to grade language models, and can free-form answers be graded
automatically as reliably as humans grade them?

## Data
MATH (Level 5, with MATH-Verify as ground truth); MMLU-Pro (questions filtered for a unique
answer: about 5,500 of 12,000 kept; 800 sampled; 493 in the final set); GPQA-Diamond (198
questions; 126 in the final set). Four answering models for the human-graded sets; 17 models for
ranking comparisons.

## Method
- Choice-only shortcut test: fine-tune Qwen3-4B to pick the right option without seeing the
  question.
- Answer matching: the evaluated model answers without options; a matcher model sees the
  question, the response and the reference answer and decides whether they are equivalent.
  Compared with multiple choice, multiple-choice verification, cloze, and an LLM judge with no
  reference.
- Human grades from two authors annotating independently; agreement by Scott's pi.

## Outcome variable and horizon
Agreement with human (or MATH-Verify) grades; model rankings; cost.

## Result
Empirical findings.

- **Multiple choice can often be answered from the options alone.** Choice-only accuracy: 41% on
  MMLU-Pro (chance 10%), 39% on MMLU (chance 25%), 83% on TruthfulQA-v2, 93% on GoldenSwag. The
  authors call these lower bounds.
- **A small matcher with a reference agrees with ground truth almost perfectly on maths.** Scott's
  pi: Qwen3-1.7B matcher 0.97, DeepSeek-V3 matcher 0.98, DeepSeek-V3 as a judge without the
  reference 0.72, multiple choice 0.26 (85% of its errors false positives).
- **On MMLU-Pro and GPQA, small matchers such as Qwen3-4B reach agreement within the range of
  human-human agreement** (figure-level finding). Judges without a reference err mostly (80%+) by
  false positives.
- **Rankings change** between multiple choice and answer matching; GPQA-Diamond accuracy falls by
  more than 20 points for all models under generative grading.
- **Cost is not higher:** matching with DeepSeek-V3 costs no more than multiple choice for 17
  models, because models write long multiple-choice responses.

## Look-ahead and memorisation
Not addressed.

## What it settles for us
- **Make reasoning items have a unique, short answer and grade by matching against a reference**,
  instead of options or open scoring. For S1 that means questions whose answer is a direction, a
  named segment, a ranking or a number: the evaluated model writes freely, the grader only checks
  equivalence with the gold. Most S1 reasoning items can be graded by rule; a small matcher
  covers the remainder (empirical finding transferred by our inference).
- **Do not build multiple choice from options a model can game.** If multiple choice is used for
  speed, test a choice-only baseline first.
- **Grading without a reference is the unreliable case**, and its errors are lenient. Any
  open-ended S1 analysis item needs item-specific references or criteria.
- **Filtering for specificity removes over half of questions**; expect a similar loss when
  turning open analysis prompts into unique-answer items.

## Limits
- Human grades from two authors; some items needed expertise they may lack.
- Robustness of matchers to adversarial or hedged answers was not tested.
- Applies only where a unique correct answer exists; analysis writing needs rubrics instead, as
  the authors say.
