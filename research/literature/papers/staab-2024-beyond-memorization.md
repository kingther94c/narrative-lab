# Beyond Memorization: Violating Privacy via Inference with Large Language Models

- **Citation:** Robin Staab, Mark Vero, Mislav Balunović and Martin Vechev (2024). ICLR 2024
  (spotlight poster). arXiv 2310.07298. v1 11 October 2023; v2 6 May 2024. Version read: v2,
  HTML.
- **Link:** https://arxiv.org/abs/2310.07298 (HTML read: https://arxiv.org/html/2310.07298v2;
  venue checked at https://iclr.cc/virtual/2024/poster/17964)
- **Stream:** 09, rewrite blinding (question 3: LLM re-identification attacks)
- **Verified against source:** yes, 2026-11-22 (abstract, sections 4 to 6, Tables 1 to 3 and
  Figure 7 caption, read through a machine extraction of the arXiv HTML; figures not read)

## Question
Can an LLM infer personal attributes of an author (location, age, income and so on) from text
the author wrote, with no named identifier present, and do standard text anonymisers stop it?

## Data
- PersonalReddit: 520 public Reddit profiles, comments from 2012 to early 2016, from subreddits
  likely to carry personal information. Eight attributes (age, education, sex, occupation,
  relationship status, location, place of birth, income). 1,184 labels, 1,066 kept at labeller
  certainty of at least 3; labelled by the authors in about 112 hours. Each label has a
  hardness score from 1 to 5 (4 and 5 needed a web search by the human labeller).
- The real data set is not released; 525 human-checked synthetic examples are.
- Models: nine LLMs including GPT-4, Claude 2 and Llama-2 7B and 70B (the extracted text says
  "99" in one place and "9" in the Figure 4 caption; a rendering artefact).

## Method
The model reads all of a profile's comments and gives, with reasoning, up to three guesses per
attribute. Guesses are scored against the labels. A defence test runs the comments through the
Azure Language Service first, which replaced locations, addresses, persons, organisations,
events, dates, ages, numbers and currencies detected with confidence above 0.4. Only the
attributes the tool covers (location, age, occupation, place of birth, income) are scored after
anonymisation.

## Outcome variable and horizon
Top-1 and top-3 accuracy of attribute inference. No horizon.

## Result
Empirical findings.

- GPT-4: 85.5% top-1 and 95.2% top-3 over all attributes (section 5, Figure 4 caption). The
  abstract gives 95.8% top-3. Per attribute, top-1 (Table 2): sex 97.8, place of birth 92.7,
  relationship 91.5, location 86.2, age 78.3, occupation 71.6, education 67.8, income 62.5.
- Smaller models do worse: Llama-2 7B 51% and Llama-2 70B 66% overall.
- Cost: about 100 times cheaper and 240 times faster than the human labellers.
- After Azure anonymisation (Table 3, GPT-4 accuracy by hardness, before and after): level 1
  85.0 to 43.9; level 2 78.2 to 59.2; level 3 77.9 to 64.2; level 4 84.2 to 52.6; level 5
  69.2 to 61.5. The fall is smallest for the hardest items.
- Why the defence fails, in the authors' words: models "pick up on more subtle language clues
  and context (e.g., region-specific slang or phrases)" that an entity tagger leaves in place
  (section 6, Figure 7).
- A simulated chatbot that steers the conversation to extract attributes reached 59.2% top-1
  over 224 interactions (simulation, not real users).

## Look-ahead and memorisation
Not applicable: the attack is inference from content, not recall of the text. The paper's title
makes the point that the risk does not need memorisation.

## What it settles for us
- **Removing named entities does not stop an LLM that reasons from context: supported in a
  second domain.** This is the pattern of EXP-0028 and EXP-0030, where Claude Opus named every
  company after names, places, people and brands were removed and fell back on segment
  structure, reporting style and business description (our reading).
- **The hard items barely move.** Anonymisation removes the easy cues and leaves the inferences
  that rest on context. A recognition rate that falls little after redaction says the remaining
  cues are diffuse, which a list of terms to remove cannot fix (our reading).
- **Reusable:** top-3 scoring, a hardness label per item, and asking the attacker for its
  reasoning so that the cue it used can be classified.

## Limits
- Personal attributes, not the identity of a known entity; the label space is small (sex has two
  values), so top-1 rates are not comparable with naming one company of 500.
- One commercial anonymiser as the defence; no LLM rewriting defence (see
  `staab-2025-advanced-anonymizers`).
- Labels come from the authors; no inter-annotator agreement is reported in the parts read.
