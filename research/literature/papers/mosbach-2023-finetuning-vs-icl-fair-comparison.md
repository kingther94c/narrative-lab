# Few-shot Fine-tuning vs. In-context Learning: A Fair Comparison and Evaluation

- **Citation:** Mosbach, M., Pimentel, T., Ravfogel, S., Klakow, D., Elazar, Y. (2023). Findings of ACL 2023. Version read: arXiv 2305.16938v2 (30 May 2023), HTML full text.
- **Link:** https://arxiv.org/abs/2305.16938 (full text: https://arxiv.org/html/2305.16938v2)
- **Stream:** 05, comparing adaptation methods
- **Verified against source:** yes, 2026-11-12, against the arXiv abstract page and the HTML full text up to Appendix C. Read through an automated page reader; numbers are as it returned them and were not re-keyed from the PDF.

## Question
Earlier work reported that in-context learning (ICL) generalises out of domain better than few-shot fine-tuning (FT). Is that a property of the methods, or of comparisons made under unequal conditions?

## Data
Public English classification sets, no financial text and no firms. In domain: MNLI (neutral class removed), RTE, QQP (1,000 sampled validation items). Out of domain: the HANS lexical-overlap subset and PAWS-QQP.

## Method
- Same model family for both methods: OPT at seven sizes from 125M to 30B, with a Pythia suite (410M to 12B) as a check.
- Same number of examples for both methods: n in {2, 16, 32, 64, 128}; main results at 16. ICL is capped by the 2,048-token context.
- 10 data seeds, up to 3 patterns, so up to 30 runs per method and n.
- FT is pattern-based fine-tuning with a minimal pattern: 40 epochs, learning rate 1e-5, batch size 32, settings taken from the authors' earlier work and not searched. Vanilla FT and LoRA are compared on RTE.
- Three model-selection rules are compared: best in-domain checkpoint, last checkpoint, best out-of-domain checkpoint.
- Welch's t-tests at p < 0.05 between the two methods.
- The paper names the unequal comparisons it is correcting: GPT-3 ICL against much smaller fine-tuned models (Brown et al. 2020; Si et al. 2023, about 500 times the parameters of RoBERTa-large).

## Outcome variable and horizon
Classification accuracy in domain and out of domain. No horizon.

## Result
- Empirical finding: under equal conditions the two methods generalise similarly, and both vary widely with model size and number of examples. The abstract states that fine-tuned models "can in fact generalize well out-of-domain".
- ICL with OPT-30B: MNLI 71.4% on average (maximum 74.9%); RTE 61.7% in domain and 60.5% out of domain; QQP 42.0%.
- FT at 16 examples is similar to ICL in domain. For the 6.7B to 30B models out-of-domain accuracy is often on par with in-domain accuracy. Only 10 of 70 fine-tuned QQP models beat the majority baseline.
- ICL beats FT mainly when a large ICL model is set against a much smaller fine-tuned model.
- The selection rule changes the picture: selecting on in-domain data gives good out-of-domain results only for the largest models, while selecting on out-of-domain data lets small models look strong. The authors call the second rule "not realistic". About 50 evaluation examples were enough to pick robust checkpoints (reported correlation 0.99).
- No intervals on effect sizes; significance is marked per table cell.
- Cost: FT pays once in training and reads only the test item at inference; ICL re-reads every demonstration on every query.

## Look-ahead and memorisation
Not addressed. The benchmarks are public and old enough to sit in any pre-training corpus; the paper does not discuss it.

## What it settles for us
- Supports "same development set and same number of development evaluations per method". The paper shows that the verdict between two methods flips with model size and with the checkpoint-selection rule, so both must be fixed before the comparison.
- Supports running the fine-tuning factor on the same base model as the prompting factor. The authors excluded GPT-3 because its fine-tuning procedure is unknown, which is the same reason the roadmap gives for running commercial models without the fine-tuning factor.
- Leaves open how to equalise effort. Hyperparameters were inherited, not searched under a budget, and no development-evaluation count is reported. Our rule goes further than the paper.
- Reusable: the three selection rules as a sensitivity check; 10 seeds per cell; reporting the maximum next to the mean to show run-to-run spread.

## Limits
Classification with at most 128 examples; one model family; English; two challenge sets; no retrieval, no tools, no commercial model; appendices after C not read.
