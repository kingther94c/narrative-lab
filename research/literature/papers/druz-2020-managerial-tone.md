# When Managers Change Their Tone, Analysts and Investors Change Their Tune

- **Citation:** Marina Druz, Ivan Petzev, Alexander F. Wagner and Richard J. Zeckhauser (2020).
  Financial Analysts Journal 76(2), 47-69. Version read: the earlier working paper, Druz, Wagner
  and Zeckhauser, "Reading Managerial Tone: How Analysts and the Market Respond to Conference
  Calls", Harvard Kennedy School Faculty Research Working Paper RWP16-004, 16 January 2016
  (67 pages). The published article was not opened (publisher page only); an SFI Swiss Finance
  Institute listing of the 2015 version (paper 15-02) gave a partial abstract.
- **Link:** https://appext.hks.harvard.edu/publications/getFile.aspx?Id=1301 (published record:
  https://www.hks.harvard.edu/publications/when-managers-change-their-tone-analysts-and-investors-change-their-tune)
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against the full 2016 working-paper text
  (extracted from the PDF by script). The published FAJ version adds a co-author and is framed
  as "tone change"; its numbers may differ from the ones below.

## Question
Does managers' unexpected tone on the call predict future earnings and uncertainty, beyond the
press release, analysts' tone and analysts' forecasts, and do analysts and the market react
correctly?

## Data
- S&P 500 companies, 2004 to 2012, about 450 firms per panel regression (unbalanced); 13,743
  firm-quarters in the earnings regressions.
- Transcripts split into management presentation, analysts' questions and management answers.
  The transcript vendor was not found in the text read. Press releases from EDGAR.
- I/B/E/S earnings and forecasts, CRSP returns. Delisted firms: not discussed (S&P 500 membership
  over the period, not a survivor list, is implied but not stated).

## Method
- **Tone.** Loughran-McDonald (2011) word lists (August 2013 version), negativity = negative words
  relative to positive and negative words, with a negation rule for positive words. Computed
  separately for presentation, answers, analysts' questions and the press release. A short
  self-compiled list is a robustness check.
- **Tone surprise.** Residual negativity (RNP for the presentation, RNA for answers) from a
  regression of call negativity on recent performance, earnings surprise, the pre-call consensus
  for t+1, uncertainty, the press release's negativity and CEO fixed effects; standardised to mean
  0 and SD 1. Split into "tone disappointment" (positive residual, too negative) and "tone delight"
  (negative residual).
- **Other speech features.** Share of uncertain, strong modal and weak modal words; words per
  sentence; "atypical tense" (presentation not in past tense, answers not in present or future);
  share of financial words; inconsistency in tone between presentation and answers.
- **Outcomes.** Panel regressions with industry and CEO fixed effects, standard errors clustered
  by CEO.

## Outcome variable and horizon
- EPS in quarter t+1 (I/B/E/S, in dollars; mean 0.73, SD 0.63).
- Uncertainty: SD of analysts' t+1 forecasts three days after the call; revision frequency; change
  in bid-ask spread.
- Analysts' forecast change and forecast error for t+1; CAR over [0,1] and drift over [2,50]
  trading days (DGTW characteristic-adjusted).

## Result
All empirical findings, from the 2016 working paper.
- **Next-quarter earnings (Table 4).** One SD of residual negativity lowers t+1 EPS by $0.044 in
  the presentation (t = -8.33) and $0.026 in the answers (t = -5.28). That is about 7% and 4% of
  the SD of t+1 EPS. Controls include the pre-call consensus for t+1 (coefficient 0.68), the press
  release's negativity and the analysts' questions' negativity.
- **Asymmetry.** Tone disappointment: -0.057 (presentation, t = -6.55), -0.024 (answers,
  t = -3.19). Tone delight: +0.028 (presentation, t = 3.45), +0.029 (answers, t = 3.38). Excess
  negativity in the prepared presentation is the strongest signal.
- **Incremental to analysts after the call.** With the consensus three days after the call in
  place of the pre-call one, presentation disappointment is still -0.042 (t = -5.06) and answers
  disappointment -0.018 (t = -2.56). The authors say the predictive power is about halved but
  remains strong.
- **Other speech features predict lower t+1 EPS** (columns 5 and 6): uncertain words -0.072
  (t = -3.30), strong modal words -0.056 (t = -2.85), words per sentence -0.003 (t = -2.25),
  atypical tense -0.018 (t = -2.03), financial words -0.002 (t = -2.30); log words in the answers
  -0.031 (t = -2.60). Weak modal words and tone inconsistency are not significant.
- **Press release and analysts.** In the same regressions the press release's negativity
  (-0.046, t = -4.54) and the analysts' questions' negativity (-0.074, t = -6.44) also predict
  lower t+1 EPS. The text does not state whether these two are standardised, so their size cannot
  be compared with RNP.
- **Horizon.** Unreported results say tone predicts "up to earnings in the same quarter in the
  following year". Also unreported: presentation negativity above the press release's predicts
  lower earnings and lower returns.
- **Uncertainty.** Residual negativity predicts a wider post-call forecast SD, more revisions and
  wider spreads; disappointment more than delight.
- **Analysts.** One SD of presentation residual negativity cuts the t+1 forecast by 2.09%.
  Analysts react more to delight than to disappointment and under-react to disappointment;
  generalist analysts under-react more.
- **Market.** One SD of presentation delight: +1.08% CAR[0,1]; disappointment: -0.57%. After
  disappointment the drift over the next 50 days is about twice the initial reaction; after
  delight there is no drift.

## Look-ahead and memorisation
Not addressed as such. The tone residual is estimated in sample with CEO fixed effects, so it uses
the CEO's whole 2004-2012 history. The predictive regressions are in sample; there is no
out-of-sample forecast. No LLM.

## What it settles for us
- **The release-relative tone check is the strongest tested reader cue for next-quarter
  fundamentals (supports).** "Is management more negative than its own press release and the
  numbers justify?" predicts t+1 EPS beyond the release and beyond analysts. It works on the
  prepared presentation alone, which is the half a transcript-free design could approximate.
- **Asymmetry (supports a rule for prepared remarks).** In the presentation, unusual gloom predicts
  about twice as much as unusual cheer; in the answers the two are similar. Analysts and prices
  under-react to gloom, not to cheer.
- **Analysts' questions carry signal (supports adding the Q&A).** The negativity of the questions
  predicts earnings on its own.
- **Not about revenue.** The outcome is EPS level; revenue growth acceleration is untested.

## Limits
- Read the 2016 working paper, not the FAJ article.
- Dictionary tone, not an LLM measure; no human validation of the tone scores.
- Effects are a few percent of an SD of next-quarter EPS. The adjusted R-squared (0.84, or 0.86
  with the post-call consensus) is carried mainly by the consensus; no column without tone is
  shown, so the gain from tone is not reported.
- Several key results are "available on request".
