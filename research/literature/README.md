# Literature review

Work package 1 of Phase 0. Organised by the design decision each stream has to settle, not by
topic. The streams, their questions and their seed papers are in
[`../registry/01_roadmap.md`](../registry/01_roadmap.md) under WP1.

## Method

- Per stream: search, triage 10 to 15 candidates, deep-read 3 to 5.
- Cap: about 50 triaged papers and about 20 deep notes. Stop when two consecutive batches change
  no design decision.
- Where to look: SSRN, arXiv, NBER, ACL Anthology, journal pages. Prefer the published version and
  record which version was read.

## Inclusion

Include a paper if it does at least one of these:

- measures the predictive or explanatory value of a text-derived feature of company disclosures;
- evaluates an LLM on a financial text task with a stated protocol;
- studies look-ahead, memorisation or contamination in LLM evaluation;
- introduces a financial NLP benchmark or labelling protocol;
- compares adaptation methods (prompting, retrieval, fine-tuning, tools) under some control;
- operationalises corporate distress, failure or misreporting;
- gives a statistical method the design needs.

Exclude vendor blog posts, papers with no stated evaluation protocol, and papers that could not be
opened and read.

## Rules

- Every citation has a working link and is checked against the abstract or the text. Nothing is
  cited from memory.
- Each claim taken from a paper is labelled: verified fact, empirical finding, convention,
  hypothesis or open question.
- Record how each paper handled look-ahead or memorisation, even when the answer is "not
  addressed".

## Note template

One file per deep-read paper: `papers/<firstauthor>-<year>-<slug>.md`.

```
# <Title>

- **Citation:** authors, year, venue or working-paper series, version read
- **Link:**
- **Stream:**
- **Verified against source:** yes / no, and on what date

## Question
## Data
Text source, sample, period, universe; whether delisted firms are included.
## Method
## Outcome variable and horizon
## Result
Effect size with its interval or t-statistic, and what it was incremental to.
## Look-ahead and memorisation
How the paper handled them, or "not addressed".
## What it settles for us
Which design default it supports, contradicts or leaves open, and what we can reuse (data, labels,
code, baselines).
## Limits
```

## `matrix.csv`

One row per paper, triaged or deep-read. Columns:

`stream, citation, year, text_source, feature, method, outcome, horizon, incremental_to,
pit_handling, informs_decision, depth, url, verified`

`depth` is `triaged` or `deep`. `verified` is `yes` only when the row was checked against the
source.

## `gaps.md`

Three lists: gaps mapped to candidate experiments; questions already answered that this project
should not redo; and each design default marked supported, contradicted or not addressed.
