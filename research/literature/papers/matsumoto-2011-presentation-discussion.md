# What Makes Conference Calls Useful? The Information Content of Managers' Presentations and Analysts' Discussion Sessions

- **Citation:** Dawn Matsumoto, Maarten Pronk and Erik Roelofsen (2011). The Accounting Review
  86(4), 1383-1414. Version read: chapter 2 ("What makes conference calls useful?", joint work
  with Matsumoto and Pronk) of Erik Roelofsen's doctoral thesis, The Role of Analyst Conference
  Calls in Capital Markets, Erasmus University Rotterdam, ERIM PhD Series EPS-2010-190-F&A
  (2010). The published abstract was checked on the Erasmus repository; the published full text
  was not opened.
- **Link:** https://repub.eur.nl/pub/18013/EPS2010190FA9789058922281Roelofsen.pdf (published
  record: https://pure.eur.nl/en/publications/what-makes-conference-calls-useful-the-information-content-of-man/)
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against chapter 2 of the thesis (text extracted
  from the PDF by script). The thesis chapter is an earlier draft: it uses call length as the
  information proxy, while the published abstract speaks of the information content of each
  segment. Numbers below are the thesis's.

## Question
Why are earnings calls informative beyond the press release: because managers can say more, or
because analysts extract more in the Q&A?

## Data
- Over 10,000 earnings calls held in trading hours, January 2003 to December 2005, transcripts from
  Voxant via Factiva; NYSE and NASDAQ firms; final n = 10,062.
- Requires Compustat, I/B/E/S, CRSP and TAQ data. Delisted firms: not discussed.

## Method
- **Stage 1.** Regress presentation length (words) on firm performance, earnings surprise, special
  items, M&A, restructuring, size, analyst following, growth and firm fixed effects. The model
  explains 76% of the variation. The residual is "abnormal presentation length".
- **Stage 2.** Regress discussion length on the residual, split into positive and negative parts,
  with firm fixed effects and an interaction with high analyst following.
- **Content.** The same two stages for the share of financial words and the share of
  forward-looking words in the presentation (forward-looking words from safe-harbour language
  and LIWC; finance words from a list in their Exhibit 2).
- **Is length information?** Regress changes in analysts' forecasts of quarter q+1 (absolute
  revision, change in absolute error against actual q+1 earnings, change in dispersion) on call
  length, with the stage-1 determinants as controls and firm fixed effects.

## Outcome variable and horizon
Discussion length; and, for the information test, analysts' forecasts of next-quarter (q+1)
earnings in the 90 days before and after the call, scored against actual q+1 earnings.

## Result
All empirical findings, from the thesis version.
- **Analysts probe short presentations.** Abnormal presentation length and discussion length are
  negatively related (coefficient -0.0614, t = -2.53). The relation comes from abnormally short
  presentations; long presentations do not shorten the Q&A. It is stronger with above-median
  analyst following (interaction -0.2200, t = -2.64).
- **Content.** Fewer financial words than expected in the presentation lead to a longer Q&A.
  More forward-looking words than expected also lead to a longer Q&A (against the authors'
  prediction); they suggest forward-looking claims are harder to verify and draw questions.
- **Length carries information for next-quarter forecasts.** Longer calls go with larger
  absolute revisions of the q+1 forecast (t = 2.98) and larger gains in accuracy against actual
  q+1 earnings (t = -2.73), not with changes in dispersion. A within-firm interquartile change in
  length (1,840 words) moves the revision by 6.9% and the accuracy gain by 7.6% of their
  interquartile ranges. Split by segment, discussion length is significant for both and
  presentation length for neither.
- **Published abstract (verified fact, abstract only).** Both segments add information beyond the
  press release; the discussion is relatively more informative, more so with more analyst
  following; when performance is poor, managers disclose more in the presentation, but the
  discussion still releases relatively more.
- **Same thesis, chapter 4 summary (verified fact, introduction only).** Analysts moderate their
  tone on the call when news is bad, and more so when institutional holdings are high.

## Look-ahead and memorisation
Not addressed. The stage-1 model is estimated on the full sample with firm fixed effects, so the
abnormal-length residual uses the firm's whole 2003-2005 history. No LLM.

## What it settles for us
- **Text source (supports adding the Q&A).** The best evidence in this pass that what a call adds
  over the release comes mainly through the analysts' questions and the answers, and that it
  improves next-quarter earnings forecasts.
- **Prepared remarks alone (weak).** Presentation length did not move analysts' q+1 forecasts. A
  prepared-remarks-only arm would capture the less informative half.
- **A cheap reader cue (hypothesis).** "Thin prepared remarks followed by a long, probing Q&A"
  and "forward-looking claims that draw follow-ups" are visible to a reader model, but no paper
  here tests them against future sales.

## Limits
- Read the thesis draft, not the published article; the published tests of information content
  may differ.
- Length is a crude proxy; the outcome is analysts' forecasts, not fundamentals themselves.
- 2003 to 2005 only; a broad NYSE and NASDAQ sample, not S&P 500.
