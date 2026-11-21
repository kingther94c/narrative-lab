# A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs

- **Citation:** Humzah Merchant and Bradford Levy (2025). Preprint (University of Chicago),
  marked as submitted to a workshop on generative AI in finance. arXiv 2512.06607. Version read:
  v2 (the page gives 23 September 2026), HTML full text.
- **Link:** https://arxiv.org/abs/2512.06607
- **Stream:** 08, blind replay
- **Verified against source:** yes, 2026-11-19 (the whole HTML page of v2, appendices A and B
  included, read through a machine extraction answering targeted questions, in two passes;
  sections 1, 2, 3.1, 3.2 and Tables 1 to 3 covered; Figures 1, 2, 4 and 5 are images, so the
  finance results are known only as the text describes them; no number was checked against the
  PDF)

## Question
Retraining a frontier model with a chosen knowledge cutoff is too costly. Can a large model be
made to behave at inference time as if it had not seen a given body of text, without changing
its weights?

## Data
- **MUSE news benchmark** for unlearning (section 3.1), with Sheared-LLaMA 1.3B and 2.7B and
  trigram language models as the small models.
- **Mergers and acquisitions (3.2.1, Appendix B.3.1).** WRDS SDC deals, 1 January 2010 to
  1 August 2024. 294 deals after filters; 41 kept, those where Gemma 27B names the true target in
  at least 3 of 4 runs and Gemma 4B in at most 1 of 4. Split by alternating date order into set A
  (20 deals) and set B (21).
- **Airlines (3.2.2).** Reports on Southwest and United: 2014 to 2016 for the model of what is to
  be forgotten, 2022 to 2024 for the model of what is to be kept.
- **Models:** google/gemma-3-27b-it as the large model, google/gemma-3-4b-it for the two small
  ones. No knowledge cutoff is stated for any model.
- Delisted firms: not applicable.

## Method
- **Divergence decoding.** Two small models are fine-tuned, one on the text to forget and one on
  the text to retain. At each token the large model's logits are adjusted by their difference.
  - Linear form (Eq. 1): l_P + α · (l_q − l_p).
  - Rank form (Eq. 2): the k tokens on which the two small models differ most are blocked.
  - The linear form is a product of experts, P · (q/p)^α, and is exact only if the gap between
    the large model and the target model is linear in logit space.
- **Access needed.** Token-level logits of the large model at every step, plus forward passes
  through both small models. The large model's weights are unchanged. Trigram models can stand in
  for the small models at negligible cost.
- **Black-box use.** Not discussed. An API is used only to generate fine-tuning data and a
  baseline portfolio.
- **Tasks.** In the M&A task the model is asked to suggest a target for a given acquirer and
  year; naming the true target counts as recall. In the airline task the model builds a long-only
  portfolio of two stocks in each of three sectors; the baseline is the unmodified model run 30
  times at temperature 1.0.

## Outcome variable and horizon
Verbatim recall, question-answer knowledge and retained utility on MUSE; rate of naming the true
acquisition target; portfolio composition; MMLU accuracy as a check on general ability.

## Result
Empirical findings. The finance results are stated in words; the page gives no effect size or
interval for them.

- **MUSE.** The method "matches or pushes the frontier of unlearning while preserving model
  utility". The rank form is stronger on verbatim recall, the linear form on question answering.
- **M&A.** "A significant reduction in the memorization of M&A deals" for both forms.
- **Airlines.** The method "successfully reduces" a bias in which a long record of good
  performance drives the choice even when later news points the other way.
- **General ability (Table 3, MMLU with chain of thought).** 77.94 for the unmodified model;
  77.58 with α = 2; 75.09 with the rank form at k = 250.
- **Cost (Appendix A.2).** Inference cost rises from about 2N to 2(N + 2n) floating-point
  operations, N and n being the sizes of the large and small models.

## Look-ahead and memorisation
The paper's subject. Recall is measured directly (does the model name the real target) and the
method is judged by how far that rate falls. There is no post-cutoff test and no forecast
outcome.

## What it settles for us
- **Not usable with a commercial model.** The method edits logits at every token. With no logit
  access there is nothing to apply. This is a verified fact about the method as published.
- **Strategy G: weakened in its strong form.** Both published ways of subtracting memory at the
  output (this paper and FinCAD) work on logits. Neither offers a tested black-box version.
- **It removes knowledge of a named body of text, not knowledge of the future.** We would have to
  hold the text to forget, which for outcomes after an earnings release means collecting the
  later news we want the model not to know. That is our inference, and it makes the method a poor
  fit even for the local models.
- **Reusable.** The selection rule for a recall test set: keep items the large model recalls in
  at least 3 of 4 runs and a small model in at most 1 of 4. The same rule, reversed, picks
  episodes for strategy C (large model fails to recall).
- **Open question.** Whether an output-side correction changes forecasts of fundamentals. The
  paper never scores a forecast.

## Limits
- 41 deals and two airlines.
- The introduction assigns "forget" to later data and "retain" to earlier data; the airline
  experiment assigns them the other way round. The page does not reconcile the two.
- Small models whose output format differs from the large model's can give a diluted or noisy
  signal (Appendix A.3).
- The comparison methods (GradDiff, NPO, SimNPO) appear only as hyperparameter settings; their
  results are in figures that could not be read.
