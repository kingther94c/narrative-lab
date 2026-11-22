# Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting

- **Citation:** Miles Turpin, Julian Michael, Ethan Perez and Samuel R. Bowman (2023). NeurIPS
  2023. arXiv 2305.04388, v2 of 9 December 2023.
- **Link:** https://arxiv.org/abs/2305.04388
- **Stream:** 12, forecast prompting (reasons and rationalisation)
- **Verified against source:** yes, 2026-11-22. arXiv HTML of v2 read as extracted text:
  abstract, sections 1 to 7 including Limitations, Tables 1, 3 and 5 as text. Appendix tables
  not read.

## Question
Do chain-of-thought explanations report the real reasons for a model's answer? The test: add a
feature to the input that pushes the answer one way, and see whether the answer moves while the
explanation never mentions the feature.

## Data
- BIG-Bench Hard: 13 tasks, up to 330 examples each, 3,299 examples in all.
- BBQ (bias benchmark for QA): 2,592 ambiguous questions, each given weak evidence in two
  versions that swap who the evidence is about.
- Models: GPT-3.5 (OpenAI) and Claude 1.0 (Anthropic); the exact endpoints are in an appendix
  not read.

## Method
- Biasing features on BBH: "Answer is Always A" (the few-shot examples are reordered so the right
  answer is always A) and "Suggested Answer" (the prompt says a given option might be right).
- Settings: chain of thought ("Let's think step by step") against no chain of thought; zero-shot
  against few-shot.
- Unfaithfulness is measured as the accuracy drop from the unbiased to the biased context, when
  the explanations do not mention the bias. 426 explanations that support biased answers were
  read; one mentioned the bias.
- On BBQ, an explanation set is unfaithful if the model uses the same weak evidence differently
  when the people are swapped; the share of such pairs that favour the stereotype is reported.

## Outcome variable and horizon
Accuracy on BBH; share of unfaithful explanation pairs explained by stereotype on BBQ. Not a
forecasting task.

## Result
Empirical findings.

- **Large, unverbalised influence.** With zero-shot chain of thought, the Suggested Answer bias
  cuts GPT-3.5's accuracy by up to 36.3 points; Claude 1.0's by 30.6. Few-shot examples reduce
  these drops to 24.1 and 21.5. Answer is Always A: -18.7 for GPT-3.5 and -4.7 for Claude 1.0.
  Intervals on these differences are about ±1.6 to ±2.4 points.
- **Explanations rationalise.** Of 104 hand-annotated unfaithful explanations, 73% argue for the
  bias-consistent answer; 15% contain no obvious error and reach the wrong answer through
  inconsistent subjective judgements or ambiguity in the task.
- **Chain of thought can make bias worse.** Without bias, chain of thought helps on average
  (57.1 to 59.6% for GPT-3.5, 59.2 to 65.3% for Claude 1.0). With the Suggested Answer bias,
  zero-shot chain of thought lowers accuracy (39.5 to 23.3% for GPT-3.5; 37.3 to 34.7% for Claude
  1.0): the reasoning steers the model to a biased answer it would have avoided when answering
  directly. Few-shot chain of thought reduces sensitivity (35.0 to 51.7%; 38.9 to 60.1%).
- **Evidence weighed inconsistently.** On BBQ, up to 62.5% (Claude 1.0, few-shot) and 59.2%
  (GPT-3.5, zero-shot) of unfaithful pairs favour the stereotype. An explicit debiasing
  instruction almost removes the Claude effect (62.5 to 50.6%) and does little for GPT-3.5
  zero-shot (59.2 to 60.0%).
- **Authors' limit (convention).** The test can show unfaithfulness; it cannot prove
  faithfulness.

## Look-ahead and memorisation
Not addressed (not a temporal task). The biasing feature plays the role that a remembered outcome
plays in S2.

## What it settles for us
- **The S2 result has a published precedent.** In EXP-0029, reasons first raised the
  old-minus-clean readout from 0.155 to 0.236, and the cited document evidence already leaned
  towards the remembered outcome. Turpin et al. show the same pattern with an injected bias: a
  hidden influence moves the answer, the reasoning argues for it, and zero-shot reasoning can
  amplify the influence rather than correct it. The remembered outcome is an unverbalised biasing
  feature.
- **Stated reasons cannot audit the call.** Plausible, error-free explanations still
  rationalised a biased answer. Any playbook output (lists of one-off items, evasiveness flags)
  is a product of the same process and cannot certify that the probability came from the text.
- **Instructions help only partly.** A debiasing instruction worked for one model and not the
  other; EXP-0029's "judge from the text alone" halved the gap. Do not plan on an instruction to
  remove the leak.
- **Test design to reuse.** Paired inputs that differ only in the suspected influence, with the
  answer change as the measure. For S2: the same release with and without a feature the model
  could recall (company identity, period) and the playbook on or off.

## Limits
- 2023 models; multiple-choice tasks; the biasing features are artificial.
- Few-shot examples were model-generated and hand-edited, which may shape style.
- No probability outputs, so nothing on calibration.
