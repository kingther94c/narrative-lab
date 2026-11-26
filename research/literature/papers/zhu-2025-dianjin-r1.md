# DianJin-R1: Evaluating and Enhancing Financial Reasoning in Large Language Models

- **Citation:** Zhu, J., Chen, Q., Dou, H., Li, J., Guo, L., Chen, F. and Zhang, C. (2025). arXiv
  2504.15716 (cs.AI), Qwen DianJin team (Alibaba Cloud) and Soochow University. Version read: v1
  (22 April 2025), the only version listed; HTML, main text, tables 1-6 and the ethics statement.
- **Link:** https://arxiv.org/abs/2504.15716 (HTML: https://arxiv.org/html/2504.15716v1)
- **Stream:** 14c (stream 13a triaged the abstract only)
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v1 HTML through
  an automated page reader. Figure 1 (the workflow example) was not readable as text. No number was
  checked against a typeset PDF.

## Question

Does reasoning-augmented SFT followed by GRPO make a 7B or 32B model a better financial reasoner
than its instruct base and than general reasoning models, and can one model call replace a
multi-agent workflow on a rule-based compliance task?

## Data

- DianJin-R1-Data, SFT part: CFLUE multiple choice 26,672 (from 38,638; Chinese), CFLUE open-ended
  5,045 (MCQs rewritten by GPT-4o), FinQA 4,851 (from 8,281; English), CCC 1,800 (in-house Chinese
  customer-service compliance dialogues, roughly balanced, not public).
- Reasoning written by DeepSeek-R1 for CFLUE and FinQA. Filters: drop questions under 15 tokens;
  drop questions both Llama-3.1-8B and Qwen2.5-7B-Instruct answer correctly (keeps the hard ones);
  GPT-4o removes ambiguous items. GPT-4o checks answer match and consistency with the reference
  explanation, up to three attempts; items that never pass are kept as answer-only "hard" samples.
- **CCC synthesis (the part that matters here):** compliance guidelines are turned into a workflow
  of condition nodes between a start node and two outcomes (violation, no violation). Qwen2.5-72B
  runs one agent per node and writes an intermediate chain of thought; if the outcome matches the
  gold label, GPT-4o merges the node chains into one chain of thought; otherwise retry. The nodes
  themselves are not listed in the text.
- RL set: 4,096 hard CFLUE MCQs. Test sets: CFLUE 3,864, FinQA 1,147, CCC 200.

## Method

Qwen2.5-7B-Instruct and Qwen2.5-32B-Instruct; SFT (lr 1e-5, 16K context, 3 epochs), then GRPO (8
rollouts, 5 epochs) with a format reward and an accuracy reward applied only to CFLUE MCQs.
Grading: CFLUE, MATH-500, GPQA by rule; FinQA and CCC by GPT-4o with a judge prompt.

## Outcome variable and horizon

Accuracy. No horizon.

## Result

| Model | CFLUE | FinQA | CCC | MATH-500 | GPQA-D |
|---|---|---|---|---|---|
| Qwen2.5-7B-Instruct | 69.37 | 66.70 | 55.00 | 71.40 | 33.84 |
| R1-Distill-Qwen-7B | 48.39 | 66.09 | 41.50 | 90.20 | 45.96 |
| DianJin-R1-7B (SFT only) | 75.48 | 80.28 | 93.00 | 74.87 | 34.85 |
| DianJin-R1-7B (SFT+RL) | 80.32 | 77.72 | 94.50 | 76.60 | 37.54 |
| Qwen2.5-72B-Instruct | 79.46 | 77.94 | 55.50 | 82.20 | 39.90 |
| DeepSeek-R1 | 86.64 | 79.81 | 67.50 | 94.80 | 66.16 |
| DianJin-R1-32B | 86.74 | 80.82 | 96.00 | 88.20 | 58.59 |

- **Empirical finding (workflow internalised).** On CCC, Qwen2.5-72B alone scores 55.50; the same
  model run as the multi-agent workflow scores 95.00 at 8.15 API calls per item; DianJin-R1-7B,
  trained on the merged workflow chains, scores 94.50 in one call (32B: 96.00).
- **Empirical finding (SFT mix).** 7B average without RL: base 59.26; CFLUE only 65.67; CFLUE +
  FinQA 67.48; CFLUE + CCC 70.71; all three 71.70.
- **Empirical finding (RL is small and can hurt off-language).** RL adds +4.84 on CFLUE and +1.5 on
  CCC but costs 2.56 on FinQA (80.28 to 77.72); the authors suspect the Chinese-only RL data.
- **Empirical finding (general reasoning does not transfer).** R1-Distill-Qwen-7B is below the plain
  instruct model on all three finance sets (CFLUE 48.39 against 69.37, CCC 41.50 against 55.00),
  while far above it on MATH-500 (90.20 against 71.40).
- No evaluation of reasoning quality; all results are answer accuracy. No out-of-distribution test
  of the CCC workflow.

## Look-ahead and memorisation

Not addressed. No overlap check between FinQA training items and the FinQA test set reported. CCC
test items come from the same in-house pool and guidelines as training, so the CCC result is
in-distribution by construction. Labels are not outcomes, so outcome recall does not arise.

## What it settles for us

- The closest published analogue to "distil a framework (体系) into a small model": an explicit,
  finite procedure (a graph of conditions) run by a large model node by node, each node's chain
  kept only if the final outcome is right, then merged into one chain for the student. A 7B student
  then matches the multi-call workflow in one call. For S1 this suggests building the R teacher
  data the same way: the 4B/9B teacher runs a fixed analysis graph over a release (extract, compute,
  judge conditions, conclude), each node checked against XBRL by rule, merged into one trace.
- It does not show that the student learned the framework rather than the CCC distribution: test
  items share guidelines with training. S1 must add held-out combinations of nodes.
- The R1-Distill result repeats 13a: a general reasoning teacher's style does not carry finance
  skill. The teacher has to run the finance procedure itself.
- RL adds a few points at best and can cost an untargeted task: supports 13a's prior for R-d.

## Limits

In-house CCC data and workflow not published; node list not given; GPT-4o grades CCC and FinQA;
single run, no intervals; 7B is the smallest student (nothing near 0.8B); no contamination check.
