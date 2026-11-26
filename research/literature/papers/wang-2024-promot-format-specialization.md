# Two-stage LLM Fine-tuning with Less Specialization and More Generalization (ProMoT)

- **Citation:** Wang, Y., Si, S., Li, D., Lukasik, M., Yu, F., Hsieh, C.-J., Dhillon, I. S. and
  Kumar, S. (2024). ICLR 2024 (per arXiv comments). arXiv 2211.00635. Version read: v3 (12 March
  2024), HTML, main text and appendix tables. Earlier versions: v1 1 November 2022, v2 4 October 2023.
- **Link:** https://arxiv.org/abs/2211.00635 (HTML: https://arxiv.org/html/2211.00635v3)
- **Stream:** 14b (distillation and training methods for small students)
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v3 HTML, read
  through an automated page reader in two passes. Table values as returned; not re-keyed from the PDF.

## Question

Why does fine-tuning a model on one task destroy its in-context ability on other tasks, and can the
loss be avoided without giving up target-task accuracy?

## Data

- Fine-tuning tasks: RTE (binary entailment, answers "True"/"False") and WMT14 En-Fr; SNLI and
  OpenbookQA in the appendix.
- Out-of-domain evaluation (1-shot, "Norm. Avg."): CB, WiC, TriviaQA, web_questions, WMT16 En-De and
  En-Ro, XSum, WikiLingua/en; scores normalised to 0-100 and averaged (BIG-bench convention).
- No financial text.

## Method

- Main model mT5-XXL (13B); checks on T5.1.1-XXL, mT5-XL and PaLM 8B.
- **Format specialisation** is defined as the model overfitting to "the common characteristics of
  the sequences in fine-tuning task", such as language, length, style and special tokens.
- **ProMoT:** stage 1 trains a 100-token soft prompt on the target task with the model frozen
  (5,000 steps); stage 2 freezes that prompt and fine-tunes the model with it attached (1,000 steps).
  The prompt is used only on inputs of the target task's format and removed otherwise, so the format
  is meant to live in the prompt rather than in the weights.
- Compared: standard fine-tuning, prompt tuning, joint prompt-and-model tuning, a random fixed soft
  prompt, LoRA in stage 1, multi-task fine-tuning, 1-shot prompts during fine-tuning.

## Outcome variable and horizon

Target-task accuracy or BLEU; normalised average of the eight unseen tasks. No horizon.

## Result

- Empirical finding (the symptom): after fine-tuning on RTE, about 90% of 1-shot TriviaQA outputs are
  "True" or "False" after 300 steps; over 99% of 1-shot WMT16 En-De outputs after 500 steps. TriviaQA
  1-shot exact match falls from 17.58 to 0.15. Only tasks sharing RTE's format (CB, WiC) survive.
- Unseen-task normalised average (1-shot): pretrained 17.52; after RTE fine-tuning 15.43 (−2.10),
  ProMoT 20.10 (+2.58), ProMoT + 1-shot 22.26. After WMT14 fine-tuning 9.15 (−8.37), ProMoT 18.87.
- Target task, 0-shot (standard fine-tuning against ProMoT): RTE 92.06 / 92.78; WMT14 BLEU 41.80 /
  41.30; SNLI 88.91 / 89.62; OpenbookQA 77.2 / 81.6.
- Multi-task fine-tuning also helps (normalised average 20.06, +2.54); multi-task ProMoT 25.88
  (+8.35).
- Ablations: joint tuning of prompt and model keeps the specialisation (TriviaQA 0.75); a random fixed
  prompt does not help; LoRA in stage 1 absorbs less of the format than a soft prompt (TriviaQA
  4.98-5.19 against 13.63 on the WMT14 setting).
- Not universal: on PaLM 8B (WMT14) ProMoT still lowers the unseen-task average (26.09 to 22.37).
- No seeds or intervals reported in the parts read.

## Look-ahead and memorisation

Not relevant; contamination not discussed.

## What it settles for us

- Names and measures the failure S1 hit. C and K2 box a number on 300 of 300 R items after training
  only on `\boxed{number}` targets; RTE-tuned mT5 answers "True"/"False" to TriviaQA. The literature's
  reading: the model learned the output format of the training set, not that it lost the reasoning.
- Hypothesis for S1: the fastest test is format diversity, not a new method. Train on B and R formats
  together (and other answer shapes), which the paper's multi-task result supports (+2.54 against
  −2.10 for single-task), before concluding the 0.8B cannot learn R.
- ProMoT itself needs prompt tuning, which `mlx-lm` does not provide; it is a custom loop and was
  shown on 8B to 13B models only, not below 1B. Lower priority than mixing formats.

## Limits

Models 8B to 13B (mT5, T5, PaLM); classification, QA and translation tasks; no theoretical guarantee
that the prompt absorbs the format; the method does not help on PaLM 8B; no comparison with weight
averaging or replay of general data.
