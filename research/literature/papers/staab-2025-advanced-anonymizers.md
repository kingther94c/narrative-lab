# Language Models are Advanced Anonymizers

- **Citation:** Robin Staab, Mark Vero, Mislav Balunović and Martin Vechev (2025). ICLR 2025.
  arXiv 2402.13846; v1 21 February 2024 (titled "Large Language Models are Advanced
  Anonymizers"), v2 3 February 2025. Version read: v2, HTML.
- **Link:** https://arxiv.org/abs/2402.13846 (HTML read: https://arxiv.org/html/2402.13846v2;
  venue checked at
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/f478b2e8ad9ff0756bf5b79fb31c330f-Abstract-Conference.html)
- **Stream:** 09, rewrite blinding (questions 1 and 3)
- **Verified against source:** yes, 2026-11-22 (abstract, method, section 5 text, Tables 1 and
  2, appendix prompts E.1 to E.4, read through a machine extraction of the arXiv HTML in two
  parts; numbers shown only in Figures 3 to 5 were not read)

## Question
Can an LLM anonymise text well enough to defeat an LLM that infers personal attributes, and at
what cost in utility, compared with commercial entity-removal tools?

## Data
Real Reddit comments (the PersonalReddit set of `staab-2024-beyond-memorization`) and synthetic
online texts; 13 LLMs as anonymisers. Human study: 50 participants (abstract); 100 texts, five
raters per sample (appendix F.1).

## Method
- **Adversarial anonymisation.** Round i: an inference model reads the current text and
  states what it can infer about the target attributes, with reasoning. An anonymiser model gets
  the current text and those inferences, first explains the changes it will make, then returns a
  rewritten text. Repeat until nothing is inferred or a round limit (five in Figure 3; three in
  the human study). Both models see only the current text, not the history.
- **Privacy:** adversarial accuracy of a GPT-4 attacker on the anonymised text, scored as in
  the 2023 paper. The attacker also gives a certainty: whether it inferred from direct evidence
  or relied only on statistical bias.
- **Utility:** the mean of a GPT-4 judge's readability and meaning scores (1 to 10, rescaled),
  BLEU and ROUGE-1 against the original. The judge prompt (E.3) also scores "hallucinations" as
  0 (new information added) or 1 (none). Baselines: Azure Language Service, a paraphraser
  (Dipper) and a self-disclosure abstraction model (Dou et al.).

## Outcome variable and horizon
Adversarial accuracy and utility score. No horizon.

## Result
Empirical findings.

- Azure lowers adversarial accuracy from 86.7% to 66.3% with utility 0.76. GPT-4 adversarial
  anonymisation reaches 41.6% after five rounds while keeping higher mean utility than Azure
  (section 5). Section 4 reports 66.3% to 45.3% after three rounds against a one-shot LLM
  anonymiser.
- Location by resolution (Table 2, adversarial accuracy, Azure against GPT-4 rounds 1 to 3):
  city 24.6 against 6.8, 4.1, 1.3; state 14.3 against 9.5, 0, 0; country 59.2 against 61.8,
  46.1, 46.1. About 45% of location labels can still be inferred after three rounds. The
  authors: city and state references are "more specific, making them easier to remove".
- Correct inferences survive from topic choice alone once direct cues are gone (the lipstick
  example for sex), which the certainty field labels as statistical bias.
- Human study (Table 1, normalised medians, rounds 1 to 3): meaning 0.79, 0.73, 0.67; usable
  1.00, 0.91, 0.88; readability 0.86, 0.90, 0.90. Azure: readability 0.38, meaning 0.47.
- Model choice: Llama3.1-70B comes close to GPT-4's trade-off; within the Qwen family larger
  models dominate smaller ones; Dipper gives "only minor improvements in privacy while heavily
  impacting utility".
- Attacker strength: the method "is naturally bounded by the strength of the feedback
  adversary". Weaker attackers (GPT-3.5, Llama3.1-8B) "clearly underestimate the potential
  privacy leakage" (appendix A.5), and GPT-4 slightly overestimates how well its own last round
  anonymised the text.

## Look-ahead and memorisation
Not applicable. The anonymiser is a strong model with world knowledge; whether it adds content
from that knowledge is checked only by the judge's 0/1 hallucination flag, whose aggregate is
not reported in the parts read.

## What it settles for us
- **The loop we ran in EXP-0030 is the published method.** Feeding the attacker's stated cues to
  a rewriter is adversarial anonymisation. It works on specific cues (city, state) and stalls on
  coarse ones that the whole content carries (country at 46%). Our analogue of country is the
  sector and the business model, which every sentence of a release carries (our reading).
- **Meaning falls round by round.** The utility loss is smooth, not a cliff, which supports
  measuring forecast accuracy at each blinding level rather than at one end point (our reading).
- **Test with the strongest attacker.** Anonymisation tuned against a weaker attacker
  overstates privacy. Our attacker should be at least as strong as the PM (it is: both are
  Opus), and a reasoning or multi-sample attacker is the stricter test.
- **Residual inference from base rates is not leakage of identity.** A correct guess from
  "statistical bias" (the most likely company for a sector and size) needs its own benchmark;
  the certainty field is a cheap way to separate it (our reading).
- **Open question:** whether the rewriter injects knowledge. The paper's utility metrics reward
  closeness to the original and would not detect an addition that agrees with later events.

## Limits
- Personal attributes with small label spaces, not one entity among hundreds.
- Utility is text similarity and judged meaning, not a downstream prediction task.
- The final attacker is the same model family as the anonymiser in the headline results.
- Per-round utility numbers for the automatic metric are in figures not read.
