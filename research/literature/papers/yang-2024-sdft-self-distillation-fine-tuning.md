# Self-Distillation Bridges Distribution Gap in Language Model Fine-Tuning (SDFT)

- **Citation:** Yang, Z., Pang, T., Feng, H., Wang, H., Chen, W., Zhu, M. and Liu, Q. (2024).
  ACL 2024 (per arXiv comments). arXiv 2402.13669. Version read: v2 (28 May 2024), HTML, main text
  and Appendix A. Earlier version: v1 21 February 2024.
- **Link:** https://arxiv.org/abs/2402.13669 (HTML: https://arxiv.org/html/2402.13669v2)
- **Stream:** 14b (distillation and training methods for small students)
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v2 HTML, read
  through an automated page reader in two passes. Table values as returned; not re-keyed from the PDF.
  Code: https://github.com/sail-sg/sdft (not run).

## Question

Fine-tuning a chat model on a task dataset erodes its other abilities and its safety alignment. Is
the cause the gap between the dataset's response distribution and the model's own, and does closing
it help?

## Data

GSM8K, OpenFunctions, MagiCoder (scored on HumanEval), Alpaca, Dolly, LIMA, OpenHermes; 2,000
sampled examples for the large sets (20,000 for OpenHermes), full train sets for GSM8K, LIMA and
OpenFunctions. Safety: AdvBench raw and with fixed jailbreak suffixes; helpfulness: AlpacaEval win
rate. No financial text.

## Method

- **SDFT:** before fine-tuning, the seed model rewrites each gold response with a template that
  shows the gold answer as a reference ("Using the reference answer as a guide, write your own
  response"). For math, the rewrite is kept only if its extracted final answer equals the gold one;
  otherwise the original response is used. The model is then fine-tuned on the rewrites with the
  usual likelihood loss.
- Main setup: Llama-2-7b-chat, LoRA rank 8 on query and value, learning rate 1e-4 with cosine decay,
  batch 8, 2 or 5 epochs. Checks: full fine-tuning of Llama-2-7b-chat on GSM8K; Llama-3-8B-Instruct
  with LoRA.
- Distribution shift measured by similarity of fine-tuned to seed outputs (BLEU-4, ROUGE-L,
  Sentence-BERT) and by parameter-shift norm.

## Outcome variable and horizon

Target-task accuracy; accuracy on the other tasks; safe-response rates; AlpacaEval win rate.
No horizon.

## Result

Table 1 (Llama-2-7b-chat, LoRA; OpenFunctions / GSM8K / HumanEval):

| Training set | Seed | Vanilla fine-tuning | SDFT |
|---|---|---|---|
| OpenFunctions | 19.6 / 29.4 / 13.4 | 34.8 / 21.5 / 9.8 | 36.6 / 29.1 / 15.2 |
| GSM8K | same | 17.9 / 31.9 / 12.2 | 17.9 / 34.4 / 14.6 |
| MagiCoder | same | 3.6 / 23.2 / 18.9 | 8.0 / 24.9 / 18.3 |

- Empirical finding (full fine-tuning on GSM8K, Table 5): GSM8K 34.87 (vanilla) against 35.03 (SDFT);
  OpenFunctions 5.36 against 16.07 (seed 19.60); jailbreak-safe rate 37.31 against 63.46 (seed 88.85);
  AlpacaEval win rate 23.04 against 61.19 (seed 66.04).
- Empirical finding (LoRA, safety and helpfulness after GSM8K): raw safe 82.12 against 87.12;
  jailbreak safe 54.81 against 65.58; win rate 23.38 against 66.73 (seed 99.81 / 88.85 / 66.04).
- Empirical finding: more training samples lower the similarity of outputs to the seed's and raise
  forgetting; a larger share of self-distilled data does the reverse. The authors conclude
  distribution shift correlates with forgetting.
- Not universal: on MagiCoder SDFT is slightly below vanilla on the target (18.3 against 18.9).
- No seeds or intervals reported.

## Look-ahead and memorisation

Not relevant; contamination not discussed.

## What it settles for us

- The cheapest fix for forgetting that keeps the target gain, and it worked with full fine-tuning,
  which is S1's setting: the target score was unchanged and the off-target task recovered most of the
  way (5.36 to 16.07 against a seed of 19.60).
- For S1 the "gold response" would be the 4B's answer and the rewriter the 0.8B itself. Open
  question: whether a 0.8B can rewrite a 4B answer faithfully. The 7B rewriter here is strong; a
  related on-policy variant (Shenfeld et al. 2026, triaged) loses to plain SFT at 3B because small
  models follow demonstrations poorly. S1's D2 arm (the 0.8B's own correct answers) is the
  no-reference limit of this idea and already exists.
- Consistent with the finance evidence in stream 13a: self-distilled SFT +1.0 to +2.8 against plain
  SFT −3.2 to −4.0 on retained ability (Hayrapetyan et al. 2026).

## Limits

Mostly Llama-2-7b-chat with LoRA; one full fine-tuning experiment; no model below 7B; safety measured
on AdvBench with fixed suffixes only; filtering rule given for math only.
