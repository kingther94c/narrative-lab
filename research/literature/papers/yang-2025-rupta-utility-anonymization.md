# Robust Utility-Preserving Text Anonymization Based on Large Language Models

- **Citation:** Tianyu Yang, Xiaodan Zhu and Iryna Gurevych (2025). ACL 2025 main conference.
  arXiv 2407.11770; v1 16 July 2024, v2 18 June 2025. Version read: v2, HTML.
- **Link:** https://arxiv.org/abs/2407.11770 (HTML read: https://arxiv.org/html/2407.11770v2;
  ACL Anthology: https://aclanthology.org/2025.acl-long.1404)
- **Stream:** 09, rewrite blinding (questions 1, 2 and 3)
- **Verified against source:** yes, 2026-11-22 (abstract, sections 3 and 4, Tables 1, 2, 8, 9
  and 10, appendices F and G.1 and the limitations, read through a machine extraction of the
  arXiv HTML; Figure 3 read by its description only)

## Question
Can an LLM rewrite a text so that a strong LLM cannot re-identify the person while a downstream
classifier keeps its accuracy, by optimising for both at once?

## Data
- DB-bio: celebrity biographies from DBpedia; the name is the private information and the
  occupation class is the downstream label. 1,938 train, 243 validation, 239 test (Table 9).
- PersonalReddit: the 525 synthetic comments of Staab et al.; 207 test items; downstream task a
  classification of the text.

## Method
RUPTA has three LLM parts, run for up to T = 5 rounds:

- **P-Evaluator.** Given the anonymised text and the true personal information, it ranks K = 10
  candidates by likelihood and explains "the clues that led to the correct inference".
- **U-Evaluator.** Given the anonymised text and the true downstream label, it returns a
  confidence that the label can still be inferred. It can be replaced by the real downstream
  model.
- **Optimiser.** Edits the text using both evaluations, with privacy first and utility second
  (lexicographic).

GPT-4 is the backbone; Llama-3-70B, Mixtral 8x22B and GPT-3.5 are tried as optimisers. The
method is distilled into Phi-3 and Llama-3-8B by supervised tuning and DPO. Privacy is the
success rate (SR) of an adversarial LLM choosing the true person from the truth mixed with
similar candidates (candidate set size not given in the text read). Utility is the accuracy of a
separate BERT (DB-bio) or RoBERTa-large (PersonalReddit) classifier on the anonymised text.
Baselines: Azure, DEID-GPT, a self-disclosure abstraction model (SD), IncogniText and adversarial
feedback (AF, after Staab et al.).

## Outcome variable and horizon
Re-identification success rate and downstream classification accuracy. No horizon.

## Result
Empirical findings.

- **DB-bio (Table 1), SR / accuracy:** original 100.00 / 99.58; Azure 78.24 / 92.47; DEID-GPT
  77.10 / 91.22; SD 73.21 / 92.96; IncogniText 58.06 / 88.28; AF 52.91 / 92.02; RUPTA with GPT-4
  52.67 / 96.02, with Mixtral 67.78 / 96.23, Llama-3-70B 64.02 / 95.82, GPT-3.5 68.51 / 95.49.
- **PersonalReddit (Table 2), SR / accuracy:** original 49.76 / 58.45; Azure 45.89 / 57.00;
  AF 35.40 / 21.26; IncogniText 37.55 / 13.47; RUPTA with GPT-4 35.75 / 35.75, with Mixtral
  35.27 / 43.48. Methods that reach low SR here lose most of the downstream accuracy; RUPTA keeps
  more of it than AF at the same SR but far less than the original.
- **Trade-off over rounds (Table 8, Figure 3).** SR and accuracy fall together across rounds;
  "beyond a certain point, further anonymization yields diminishing returns".
- **Distillation (Table 10).** Llama-3-8B after DPO: SR 51.03, accuracy 93.28. The authors note
  DPO "could harm the downstream task performance".
- The limitations assume "a static adversarial model"; no attacker other than the evaluator
  family is tested.

## Look-ahead and memorisation
Not addressed. The relevant feature is structural: both evaluators are given the ground truth
(the person and the label), and the optimiser rewrites with that feedback. The paper does not
discuss whether label information leaks into the rewritten text. Verified fact about the text
read.

## What it settles for us
- **A utility-aware rewriter keeps more task signal than an identity-only rewriter at the same
  re-identification rate: supported on two classification tasks.** On biographies, accuracy
  96.02 against 92.02 at SR near 53. On the harder Reddit task, both lose most of the signal.
- **Where the label is cheap to infer from content (occupation from a biography), blinding is
  cheap; where the signal is subtle, it is not.** Our forecast signal is subtle (our reading).
- **The design hazard for us.** A rewriter or template that is tuned while looking at the
  outcome learns to carry the outcome. RUPTA's utility evaluator sees the label; the analogue in
  S2 is choosing template fields, or judging extraction quality, by forecast accuracy on
  pre-cutoff episodes whose outcomes the extractor already knows. Any such tuning belongs on
  clean episodes or a development set, and the classifier that scores utility must not be the
  rewriter (our reading).
- **Reusable:** scoring utility with the actual downstream model rather than text similarity;
  reporting the frontier of privacy against utility across rounds instead of one point.

## Limits
- Classification of short texts; the downstream label is a property of the text, not a future
  outcome.
- Re-identification by choosing among candidates, with the candidate set size not given in the
  text read.
- One adversary family; no test against an attacker the optimiser never saw.
- On PersonalReddit, SR and accuracy for RUPTA with GPT-4 are both reported as 35.75; this was
  checked twice in the extraction and is as printed.
