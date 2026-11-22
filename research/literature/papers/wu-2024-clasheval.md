# ClashEval: Quantifying the Tug-of-War between an LLM's Internal Prior and External Evidence

- **Citation:** Kevin Wu, Eric Wu and James Zou (2024). NeurIPS 2024 Datasets and Benchmarks
  track (per the proceedings listing in a search result; the arXiv page states no venue). arXiv
  2404.10198; v1 16 April 2024, v2 10 June 2024, v3 7 February 2025. Versions read: v2 HTML for
  the method and figures' descriptions, v3 HTML for Table 4.
- **Link:** https://arxiv.org/abs/2404.10198 (HTML read: https://arxiv.org/html/2404.10198v2 and
  https://arxiv.org/html/2404.10198v3)
- **Stream:** 09, rewrite blinding (question 2: does the extractor's own knowledge override the
  document?)
- **Verified against source:** yes, 2026-11-22 (abstract, sections 3 and 4, Table 4 of v3 and
  the text describing Figures 3, 4 and 6, through a machine extraction of the HTML; figures not
  read)

## Question
When a document placed in the prompt contradicts what a model already knows, does the model
follow the document or its prior, and what decides which?

## Data
1,294 questions in six domains: drug dosages (249), news (238), Wikipedia dates (200), sports
records (191), names (200) and locations (200). For each, the correct reference document and
perturbed versions: numeric answers multiplied by 0.1, 0.2, 0.4, 0.8, 1.2, 1.5, 2, 3, 5 or 10;
dates shifted in steps of 20 years; names and locations changed slightly, significantly or
absurdly. Six models: GPT-4o, GPT-3.5, Llama-3, Claude Opus, Claude Sonnet, Gemini 1.5 Flash.

## Method
Each model answers each question without the document (its prior, with token probabilities
where available) and with the document (correct or perturbed). Definitions (Table 4 caption):
context bias, the model adopts the document's wrong answer when its prior was correct; prior
bias, the model keeps its wrong prior when the document is correct. Context preference rate is
the share of answers that match the document.

## Outcome variable and horizon
Accuracy, context bias, prior bias, context preference. No horizon.

## Result
Empirical findings.

- **Per model (v3, Table 4, with 95% intervals):**

  | Model | Accuracy | Context bias | Prior bias |
  |---|---|---|---|
  | Claude Opus | 0.743 | 0.157 | 0.021 |
  | Claude Sonnet | 0.658 | 0.201 | 0.025 |
  | Gemini 1.5 | 0.624 | 0.245 | 0.037 |
  | GPT-4o | 0.615 | 0.304 | 0.021 |
  | GPT-3.5 | 0.539 | 0.313 | 0.028 |
  | Llama-3 | 0.500 | 0.264 | 0.021 |

  v2 has a Table 2 with other values for adoption of wrong context (Claude Opus 0.313, GPT-4o
  0.608) on a denominator the extraction did not make clear; the abstract's "over 60%" refers to
  the wrong-document case.
- **The further the document is from the truth, the less it is adopted** (Figure 3); Claude Opus
  follows a wrong document about 30% less than GPT-4o at the same deviation.
- **The more confident the prior, the less the document is adopted:** slopes of context
  preference on prior token probability from -0.1 to -0.45 across datasets (section 4.4); -0.45
  means 4.5 points less preference per 10 points more prior probability.
- **Prompt wording moves the balance** (strict against loose instruction, Figure 6).

## Look-ahead and memorisation
Not the paper's frame, but it measures the mechanism: how often parametric knowledge wins over
the text in the prompt.

## What it settles for us
- **When the document is right, a strong model rarely substitutes its memory for it.** Prior bias
  is 0.021 for Claude Opus. For the S2 extractor, which reads the true release, the numeric fields
  are therefore the low-risk part, and the quote check guards them further (our reading).
- **When the document has been altered, a strong model resists it more than a weak one.**
  Claude Opus has the lowest context bias. An extractor that knows the company should never be
  given noised or altered numbers to transcribe; it may "correct" them towards what it
  remembers. Apply noise in code after extraction, as EXP-0031 does (our reading).
- **The channel to watch is where no document value pins the answer:** menu judgements, the
  choice of which facts to report, and values marked as computed. That is where a confident prior
  meets no contradiction (our reading; the paper tests factual questions only).

## Limits
- Short factual questions with one answer, not extraction from a long document or judgement.
- Models of 2024; neither Claude Opus 5.5 nor Sonnet 5.5.
- Two tables in two versions disagree on the headline rates; the v3 table is used here.
