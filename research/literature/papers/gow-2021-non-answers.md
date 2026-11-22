# Non-Answers During Conference Calls

- **Citation:** Ian D. Gow, David F. Larcker and Anastasia A. Zakolyukina (2021). Journal of
  Accounting Research 59(4), 1349-1384. Version read: working paper dated 3 January 2019 (NYU
  Stern copy, 59 pages). The published abstract was checked on EconPapers; the published full
  text and the SSRN revision (abstract 3310360) could not be opened (SSRN returned HTTP 403).
- **Link:** https://www.stern.nyu.edu/sites/default/files/assets/documents/Gow%20Larcker%20Zakolyukina-Non-answers%20during%20conference%20calls.pdf
  (journal record: https://econpapers.repec.org/RePEc:bla:joares:v:59:y:2021:i:4:p:1349-1384)
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against the full 2019 working-paper text
  (extracted from the PDF by script; spaces between words are sometimes lost, minus signs kept).
  The published version may differ: its abstract adds results on question tone, uncertainty and
  complexity that the 2019 draft does not have.

## Question
Can a text measure of explicit non-answers in the Q&A be built at scale, and does disclosure by
this measure follow proprietary-cost and capital-market incentives?

## Data
- StreetEvents transcripts, 2002 to 2015; US firms listed on NYSE, Amex or NASDAQ; financials and
  utilities (GICS 40, 55, 60) excluded; at least five Q&A responses per call.
- Two samples: 18,112 firm-years (2,524 firms) and 2,017,404 question-answer pairs.
- Average total assets $4.6 billion, about twice the Compustat average, so larger firms.
- Delisted firms: not discussed. Every observation needs Compustat, CRSP, Capital IQ and Equilar
  data.

## Method
- **Gold standard.** 1,796 random manager responses, each tagged by two CrowdFlower workers
  (non-answer or not, one of three types, shortest justifying phrase). University of Chicago
  research assistants resolved disagreements and checked a random sample of the rest.
- **Classifier.** Hand-written regular expressions, tuned on 1,296 responses until in-sample
  accuracy passed 90%, then frozen and scored on 500 held-out responses. Three types: Refuse
  ("we do not disclose"), Unable ("I don't know"), After-call ("take that off-line"). The full
  expressions are in Appendix A.
- **Question tags.** Product-related questions by named-entity tags checked against hand-coded
  product names (NER accuracy 78.67% on 830 questions). Future-performance-related questions by
  the Bozanic et al. (2018) forward-looking word list plus the Matsumoto et al. (2011) finance
  terms, applied unchanged.
- **Tests.** Firm-year regressions of the non-answer rate on competition, capital raising and
  controls (variables standardised; clustered by firm and year). Question-level linear
  probability models with call fixed effects.

## Outcome variable and horizon
The non-answer rate (share of Q&A responses with a non-answer phrase, averaged per fiscal year)
and the per-response indicator. Future performance enters only as a regressor: "Future
profitability" is return on assets averaged over fiscal years t+1 to t+3.

## Result
- **Measurement (verified fact from the paper).** Out of sample: true-positive rate 78.87%,
  precision 58.95%, accuracy 89.20%. In sample: 81.82%, 68.13%, 90.90%. The regexes miss about a
  fifth of human-coded non-answers ("We are not at liberty to share that right now") and flag some
  hand-offs between executives as non-answers. They cannot detect evasion by changing the subject.
- **Prevalence (empirical finding).** About 11% of responses contain a non-answer, stable over
  2002 to 2015 (interquartile range about 7% to 14%), 3.68 per call on average, 9% (materials,
  energy) to 13% (telecoms, health care) by sector. Refuse 8.2%, Unable 3.6%, After-call 0.2%.
- **Future performance (empirical finding).** One standard deviation more future profitability
  (ROA over t+1 to t+3) goes with a 0.215 to 0.393 percentage-point lower non-answer rate,
  controlling for current ROA and the 12-month return. Against a mean of 11%, this is a small
  effect. One standard deviation more return volatility goes with 0.268 to 0.331 points more.
- **Question content (empirical finding).** Product-related questions are about 6.5 percentage
  points more likely to get a non-answer, more so under competition (amplification 0.213 to 0.538
  points). Future-performance questions are more likely to go unanswered, and the gap widens
  shortly before equity or debt offerings.
- **Published abstract (verified fact, abstract only).** Questions with negative tone, more
  uncertainty, more complexity or requests for more detail are more likely to get non-answers;
  performance-related questions draw non-answers, "less so when the news is good".
- No test in the 2019 draft links non-answers to returns, earnings surprises or analyst
  revisions. Liang and Carrasco Kind (2025) cite the published paper among studies that find a
  negative market reaction; that was not checked here.

## Look-ahead and memorisation
Not addressed. The non-answer measure itself uses no outcome data, and the regexes were tuned on a
random sample of responses, not on outcomes. The future-profitability regressor uses data from up
to three years after the call by design: it is a determinant test, not a forecast. No LLM.

## What it settles for us
- **Q&A non-answers as a checklist item (weak support for fundamentals).** The link to future
  profitability is real but small and runs over three years, not one quarter. The paper does not
  show that non-answers predict sales.
- **Question context matters (supports a conditional reading).** A refusal to a product or
  proprietary question is partly about competition, not bad news. A reader model should ask what
  the question was about before reading a refusal as negative.
- **Reusable.** The three-type taxonomy; the Appendix A regexes as a cheap baseline against which
  an LLM label can be scored (de Kok 2025 reports this comparison); the forward-looking question
  tag; 11% as a base rate to check an LLM labeller against.
- **Needs the Q&A.** Nothing here works on prepared remarks or a press release.

## Limits
- Read the 2019 draft, not the published version.
- Regex precision of 59% means about four in ten flagged responses are not non-answers by the
  human standard; associations are attenuated and may be biased if errors correlate with style.
- Larger firms than average, but not restricted to the S&P 500.
- Future profitability is averaged over three years, so the paper says nothing about next-quarter
  revenue growth.
