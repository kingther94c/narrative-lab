# RAT-Bench: A Comprehensive Benchmark for Text Anonymization

- **Citation:** Nataša Krčo, Zexi Yao, Matthieu Meeus and Yves-Alexandre de Montjoye (2026).
  arXiv 2602.12806 v1, 13 February 2026. Version read: v1, HTML.
- **Link:** https://arxiv.org/abs/2602.12806 (HTML read: https://arxiv.org/html/2602.12806)
- **Stream:** 09, rewrite blinding (questions 3 and 4)
- **Verified against source:** yes, 2026-11-22 (abstract, benchmark design, Tables 1 to 3,
  Figure 4 description and discussion, read through a machine extraction of the first 100,000
  of 256,196 characters of the HTML; the later appendices were not read)

## Question
How well do text anonymisation tools prevent re-identification, measured as the share of people
an attacker could single out in a population, rather than as the share of identifiers removed?

## Data
Synthetic texts written by GPT-4.1 in three settings (medical appointment transcripts, chatbot
conversations, meeting transcripts): 100 records in English, 50 each in Spanish and Simplified
Chinese. Each record embeds five indirect identifiers drawn from nine census attributes (state,
gender, date of birth, race, marital status, education, employment, occupation, citizenship),
sampled from US census microdata (PUMS), and one direct identifier (name, SSN, card number,
phone, address or email). Identifiers are written in standard form (easy), non-standard form
(hard) or only implied (implicit).

## Method
- An LLM attacker (GPT-4.1, prompt after Staab et al.) infers the attributes from the anonymised
  text.
- If any direct identifier is recovered, risk R = 1. Otherwise R is the probability that a match
  on the inferred attributes is correct in the US population, from the generative model of
  `rocher-2019-reidentification-incomplete-datasets`. A person counts as re-identified when
  R > 0.2, which is fewer than about five matching people.
- Utility: BLEU against the original (explicit-identifier texts only).
- Twelve tools: six entity taggers (Azure, Presidio, Scrubadub, GliNER, UniNER, TextWash), one
  word-level differential-privacy method (TEM), five LLM prompts (Anthropic's PII Purifier prompt
  on GPT-4.1, Gemini 2.5 Flash and Llama 3.1-8B; the Rescriber prompt on GPT-4.1 and Llama), plus
  the iterative anonymiser of `staab-2025-advanced-anonymizers` with GPT-4.1.

## Outcome variable and horizon
Share of records re-identified (R > 0.2); BLEU. No horizon.

## Result
Empirical findings.

- **No tool removes the risk (Table 1, easy / hard / implicit):** no anonymisation 100% / 98% /
  32%; Azure 22% / 33% / 21%; Presidio 41% / 77% / 30%; PII Purifier on GPT-4.1 26% / 58% /
  19%; Rescriber on GPT-4.1 45% / 76% / 30%; TEM 90% / 85% / 31%. Azure "often over-redacts",
  lowering BLEU; GPT-4.1 with the PII Purifier prompt removes more precisely at higher cost.
- **Indirect identifiers drive the residual risk.** "A significant proportion of the
  re-identification risk in our benchmark comes from indirect identifiers", which all tools
  often miss; implicit identifiers are "barely reduced" by any tool. With no direct identifier,
  risk rises with the number of indirect identifiers (3, 5, 9), reaching 60% for Presidio
  (Figure 4b).
- **Iterative LLM anonymisation (Table 2, easy / hard / implicit):** given the exact attribute
  list, 2% / 18% / 18%; with a generic list ("generalization"), 44% / 64% / 22%, no better than
  some one-shot LLM tools at much higher cost. Knowing which attributes to protect matters more
  than iterating.
- **Attacker.** GPT-5 "often refuses to guess", so GPT-4.1 is the attacker; the threshold
  R > 0.2 is called "comparatively lenient". No stronger attacker is tested, so rates are lower
  bounds.
- Entity taggers degrade outside English (Presidio easy risk 48% in English, 88% in Spanish, 86%
  in Chinese, Table 3).

## Look-ahead and memorisation
Not applicable (synthetic texts about synthetic people).

## What it settles for us
- **Measure recognition as an anonymity-set size, not only as an attacker's hit rate.** The
  benchmark turns what the attacker can infer (attributes) into how many members of the
  population share them. For S2 the population is known and small: the S&P 500 companies in a
  given quarter. Code can count how many of them are consistent with a rendered brief (sector,
  size band, growth band, margin band, number of segments, guidance sign) without any model
  call. A brief that fits fewer than about five companies is the analogue of R > 0.2 (our
  reading).
- **The iterative loop works only when it is told what to protect.** Our EXP-0030 loop was told
  what the attacker said gave the company away; the cues it then fell back on (segment structure,
  reporting style) were exactly the attributes it was not told to protect. This matches the
  "generalization" row (our reading).
- **Combinations of ordinary attributes identify.** No single field in our template identifies a
  company; the combination may. Risk should be computed on the joint record (our reading).

## Limits
- Synthetic people and synthetic texts; real texts carry more diffuse cues.
- One attacker model; refusals by stronger models limited the choice.
- Utility is BLEU, not task performance.
- The risk model needs a known population distribution, which exists for census attributes and,
  for us, for listed companies.
