# Advanced Financial Reasoning at Scale: A Comprehensive Evaluation of Large Language Models on CFA Level III

- **Citation:** Shetty, P., Upadhayaya, A., Shah, P. M., Nayak, S., Fee, A. J. and Jagabathula, S.
  (2025). FinLLM workshop at IJCAI 2025; arXiv 2507.02954. Version read: v2 (22 September 2025),
  HTML.
- **Link:** https://arxiv.org/abs/2507.02954 (HTML: https://arxiv.org/html/2507.02954v2)
- **Stream:** 13a
- **Verified against source:** yes, 2026-11-23, against the v2 HTML through an automated page reader.
  The full per-model MCQ table was not returned; only the values below were.

## Question

How do 23 LLMs do on CFA Level III, the level built around portfolio management, synthesis and
written justification, and how should the written part be graded?

## Data

Mock Level III exams from a commercial prep provider (official post-2018 questions are not public):
60 multiple-choice questions in 10 vignettes, and 43 essay questions in 11 vignettes worth 149
points. OCR, converted to JSON, reviewed by experts. No licence for redistribution stated.

## Method

- Prompting: zero-shot, chain of thought with self-consistency (N = 3 and 5), Self-Discover.
- MCQ graded by exact match. Essays graded by GPT-4.1 at temperature 0 with a strict integer rubric
  and the reference answer; also cosine similarity and ROUGE-L.
- A certified Level III grader scored all 989 essay answers (43 × 23) for the CoT N = 3 arm only.
- Overall score is the mean of MCQ and essay; pass mark taken as 65%.

## Outcome variable and horizon

Percent correct (MCQ), rubric points normalised to 0-100 (essays). No horizon.

## Result

- Top composites: o4-mini 79.1, Gemini 2.5 Pro 75.9, Claude Opus 4 74.9, DeepSeek-R1 67.4,
  Palmyra-Fin 63.4.
- Empirical finding: MCQ does not separate frontier models (top scores between 71 and 75%); essays
  do.
- Empirical finding, size: human-graded essay scores (CoT N = 3) for open models are Llama 4
  Maverick 67.8, Llama 4 Scout 59.7, Llama 3.3 70B 57.7, Llama 3.1 8B 38.9, against 79.9 to 83.2 for
  the top closed models.
- Empirical finding: reasoning models beat non-reasoning ones by 3.7 points on MCQ (73.1 against
  69.4) and 11.9 on LLM-graded essays (73.7 against 61.8).
- Prompting: Self-Discover helps MCQ (68.6 against 61.8 zero-shot) and hurts essays (46.3 against
  57.4). Self-consistency is the best essay arm, at 3 to 11 times the cost.
- Grader agreement: the human grader averaged 5.6 points above the LLM (68.4 against 62.8) and gave
  the identical score on about 70% of questions. Only three models were graded more leniently by
  the LLM.
- No intervals; 60 MCQ items give about ±12 points per model.

## Look-ahead and memorisation

Argued, not tested: the mock exams are paywalled. No probe.

## What it settles for us

- The clearest public case that written analysis separates models where multiple choice does not;
  an 8B model scores about half of a frontier model on it.
- Grading such answers is the weak link: one LLM judge disagrees with one expert on about 30% of
  questions, with a level shift. Any rubric-graded S1 item needs a human-agreement check (stream
  13b) and should report both graders.
- MCQ vignettes are auto-gradable and cheap but saturate near the top; for a 0.8B against 4B
  comparison they are probably still in the informative range.

## Limits

Mock, not official, items; small item counts; one human grader; LLM judge from the same vendor as
some graded models; no model below 8B.
