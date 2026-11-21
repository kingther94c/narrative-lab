# Entity Neutering

- **Citation:** Joseph Engelberg, Asaf Manela, William Mullins and Luka Vulicevic (2025). Working
  paper (UC San Diego; Washington University in St. Louis). SSRN 5182756. First draft 1 February
  2025. Version read: the draft dated 26 June 2026, marked "Method updated & improved".
- **Link:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5182756 (the record Manela's page
  redirects to; it sits behind a bot check and was not opened). The draft read is the PDF linked
  from https://willmullins.net/ :
  https://drive.google.com/file/d/1HnKEu6KKug8HqHhOUqJ0_tdPbwg3JA4U/view
- **Stream:** 08, blind replay (also bears on 03, look-ahead bias and memorisation)
- **Verified against source:** yes, 2026-11-19 (all 66 pages of the June 2026 draft read as page
  text in the in-app browser: sections 1 to 6, Tables 1 to 5, the internet appendix with Tables
  A1 to A7 and the prompts in Appendix B. Figures were read by caption only, so numbers that
  appear only in a chart were taken from the text that describes them. Earlier drafts, the
  slides and the code repository were not opened.)

## Question
Can an LLM strip a financial text of everything that identifies the firm and the date, so that a
frontier model can be used on historical text without look-ahead bias, and how much of the
text's predictive content survives?

## Data
- **News:** Dow Jones archive (Newswire, Wall Street Journal and press releases on the wire),
  2000 to 2022. From 40,954,779 items the filters (first article in a chain, one stock tagged,
  body over 500 characters, unique CRSP match) leave 2,554,091, of which a 20% random sample of
  509,719 is used. Mean length 377 words.
- **MD&A:** 102,070 Management Discussion and Analysis sections from 10-K and 10-Q filings, 2002
  to 2023, from the Notre Dame repository. Mean length 7,334 words.
- **Earnings calls:** 11,411 transcripts for about 869 NASDAQ and S&P 500 firms, 2017 to 2024.
  Mean length 8,426 words.
- **Delisted firms:** not addressed. The news sample requires a CRSP match and controls.
- **Models:** gpt-5-nano-2025-08-07 through the API, without internet, does the masking, the
  paraphrasing, the identification test and the sentiment scoring. Llama 3.2 (3 billion
  parameters) and Gemma 3 (4 billion) repeat the identification test on 255,328 articles.
- **Cutoff:** the paper gives September 2024 as GPT-5's training cutoff. Every sample lies before
  or on it. There is no sample after the cutoff.

## Method
The procedure, step by step. Each step is a fresh model instance with no memory of other steps.

1. **Mask.** The model is told the firm's name, ticker and industry and is asked to replace the
   firm, its products and industry terms, the names of people, locations, sectors, product
   lines, services, times, years, dates, links, and "all numbers and percentages in the text,
   including units". Each is replaced by a placeholder (`name_x`, `product_type_x`, `number a`),
   never deleted.
2. **Identification test.** A new instance is told "You are omniscient" and must give one best
   guess of the ticker, the firm name, the industry (from a fixed list) and the date. A text
   counts as identified if the firm is right or the date is within seven days.
3. **Paraphrase.** If the text is identified, a new instance, again told the firm, ticker and
   industry, rewrites it so that "someone who has memorized the text could not recognize it",
   changing wording, sentence structure and quotations while keeping about the same length.
4. **Test again.** Same prompt as step 2.
5. **Iterate.** If still identified, mask and paraphrase again with prompts that say the last
   attempt failed and ask for more aggression. News stops at 9 iterations, MD&As at 20.
6. **Drop.** Texts still identified at the end are removed from the sample.
7. **Compare.** Sentiment is extracted from the raw and the neutered text of every surviving
   item, and the two are compared as predictors of returns.

The paper adds a framework after Ludwig, Mullainathan and Rambachan (2024). If neutering removes
all leakage and does not improve prediction, the loss in predictive fit from neutering is an
upper bound on look-ahead bias in the raw text (Proposition 1). Removing all leakage follows if
leakage runs only through a chosen channel, here firm and date, and the model cannot recover
that channel (Proposition 2). The authors call the choice of channel "an assumption".

## Outcome variable and horizon
Characteristic-adjusted (DGTW) stock returns on day t+1 and over days t+2 to t+5, predicted by
the sign and strength of sentiment. The sentiment prompt mentions future returns on purpose.

## Result
Empirical findings.

- **Identification of news articles, by method (section 4.2).**

  | Method | Firm named | Date within 7 days |
  |---|---|---|
  | Mask the firm name only (after Sarkar and Vafa) | 69.1% | 92.5% |
  | Name, ticker and up to 20 related terms (after Glasserman and Lin) | 47.3% | not given in the text |
  | First masking pass of entity neutering | 11.3% | 1.21% |
  | Entity neutering, 9 iterations | 0.11% (539 articles) | 0.03% |

- **Chance benchmarks.** Always guessing Apple would be right 0.18% of the time; a random draw
  from the sample's firms 0.11%. For dates the benchmark is 0.45% within seven days; the right
  year is guessed 5.45% of the time against a benchmark of 6.01%.
- **By firm size (Table A5).** Top size quartile 0.24%, bottom quartile 0.02%; growth 0.18%,
  value 0.04%. Large firms stay above the benchmark.
- **Other attackers (Table 1).** Llama 3.2 names the firm in 0.07% of neutered articles and
  Gemma 3 in 0.08%.
- **Dropped.** 693 of 509,719 articles (0.14%) are identified by firm or date and removed.
- **Longer texts.** MD&As: 0.29% of firms and 0.01% of dates identified after 20 iterations;
  0.85% for the top size quartile (Table A6); 301 dropped. Earnings calls: 66% identified after
  the first masking, 52% after the first paraphrase, 3.41% at iteration 20 and the benchmark of
  0.26% only at iteration 93; Table A4 drops 372 of 11,148.
- **Industry.** The test prompt asks for an industry guess, but this draft reports no industry
  identification rate. Verified fact about the text read.
- **Sentiment kept.** Where both versions have a sentiment, the direction agrees 96% of the time
  for positive and 97% for negative articles; the rank correlation of magnitudes is 81%.
- **Sentiment lost.** 16.3% of raw articles with a sentiment have none after neutering. Table A1
  shows 65,654 of 409,548 lost this way, leaving 343,894 for the regressions.
- **Return predictability, news (Table 2, basis points, day t+1).** Negative against positive
  sentiment: -12.43 (t = -9.97) raw, -11.66 (t = -9.29) neutered. Strong negative: -11.10
  (t = -6.66) raw, -6.33 (t = -4.08) neutered. Over t+2 to t+5, strong positive is 12.13
  (t = 3.76) raw and 3.55 (t = 1.22) neutered.
- **Trading strategy (Table 3).** Six-factor alpha 13.12 bps a day (t = 8.56) raw and 11.70
  (t = 7.30) neutered, difference 1.42 (t = 1.35). With strong sentiment only: 19.70 against
  10.64, difference 9.06 (t = 1.91).
- **Bound on look-ahead bias (section 4.4.1).** At most 12% of the gain in fit for t+1 returns
  with binary sentiment and 36% with strong and weak sentiment; 24% and 76% for t+2 to t+5.
  With strong sentiment the bound is 28% on low-VIX days and 43% on high-VIX days.
- **MD&As (Table 5, Table A7).** Negative sentiment -18.62 (t = -6.19) raw and -13.92
  (t = -4.63) neutered; bounds of 41% to 73%. The strategy alpha is 14.02 (t = 2.92) raw and
  7.51 (t = 1.49) neutered.
- **Earnings calls.** 95.1% share the same sentiment direction. Neither version predicts
  returns, so the analysis stops there.
- **Against dictionaries.** Neutered LLM sentiment earns 10 bps long-short on day t+1, against
  1.8 for Loughran and McDonald and 2.4 for Garcia et al.
- **Cost.** About $1,500 per 100,000 news articles with GPT-5 nano.

## Look-ahead and memorisation
The whole paper is a remedy for look-ahead bias by changing the text, not the model.

- Its test of success is that a model cannot name the firm or the date. The bound then rests on
  two assumptions that are stated and not tested: leakage runs only through firm and date, and
  neutering never improves prediction.
- All samples predate the model's cutoff, so the fall in predictability after neutering cannot
  be split into bias removed and information lost. The bound treats all of it as possible bias.
  Wu et al. (2025) warn against reading such a fall as bias removed; see our note on that paper.
- The paper reports that Lopez-Lira et al. (2025) applied an older, masking-only version of the
  method to transcripts and found 47% identified on average.

## What it settles for us
- **Cheap blinding fails on text: supported.** Masking the name leaves 69% of firms and 92.5% of
  dates identifiable; adding 20 related terms still leaves 47%. For S2 strategy A this means
  level L1 (rename, scale, relative dates) cannot be expected to hide a press release.
- **Time leaks more than identity under light masking.** The date is recovered more often than
  the firm (92.5% against 69.1%). This is direct support for hypothesis H2 (hiding time matters
  more than hiding the name), on news text.
- **The method removes the numbers.** Every number, percentage and unit becomes a placeholder.
  Our call is the direction of next quarter's fundamentals, which is made of numbers. So levels
  L3 and L4 of strategy A, if built this way, would not be the same task. Rule 2's objection to
  masking stands for our label. The second and third sentences are our inference.
- **The evidence on information loss is for sentiment only.** Agreement of 96% on direction says
  little about a task that needs magnitudes. Even for sentiment, one article in six loses its
  signal, and the strong-sentiment and multi-day results weaken most.
- **Length is the cost driver.** A news item needs up to 9 rounds, an MD&A 20, a transcript up
  to 93, each round being up to four model calls (mask, test, paraphrase, test). Where an
  earnings release with tables falls on this scale is not tested.
- **Large firms remain the weak point.** Identification is about twelve times higher for the top
  size quartile than the bottom in news, and nearly thirty times in MD&As. This matches the
  ResearchOS finding and the megacap bottleneck in the plan.
- **Drop, do not force.** The paper removes what stays identifiable instead of rewriting until
  it passes. That is close to strategy C (select, do not blind). In the plan's terms the usable
  share of history is then a measured output, 99.86% for news here.
- **Reusable.** The identification prompt (forced best guess of name, ticker, industry and date)
  and the two chance benchmarks (most frequent firm; random draw from the sample) fit our
  attacker and its base rates. The date-within-seven-days rule needs a quarterly equivalent.
- **Open question: hindsight in the rewriter.** The masker and paraphraser are the contaminated
  model and are told the firm's name. Nothing tests whether the rewrite tilts the text towards
  what later happened. If it did, the assumption that neutering never improves prediction would
  fail without any sign in the identification test. Our inference; the plan lists this risk for
  strategy A.
- **Open question: stronger attackers.** See Limits.

## Limits
- The attackers are small: GPT-5 nano and two open models of 3 and 4 billion parameters. No
  flagship model is tried as attacker, so the 0.11% is a lower bound for a frontier PM.
- One open-ended guess per text. No top-3, no line-up, and no test of whether the model's
  sentiment call leans towards the realised outcome when it fails to name the firm.
- Failing to name the firm is taken as the absence of leakage. Our note on Lopez-Lira et al.
  (2025) records their point that a negative memorisation test is only a lower bound, and that
  restricting a sample to unidentified items does not fix this.
- The text read does not say how a correct firm guess was scored (exact match, ticker or fuzzy).
- No post-cutoff sample, so information loss and bias removal are confounded.
- Numbers shown only in Figures 2, 3, 8 and A1 to A3 were not read from the charts.
- The method has changed across drafts. Levy (2026) cites the paper for guess rates of 25% or
  more on SEC filings, which this draft does not report; rates quoted elsewhere may come from
  earlier versions that we did not open.
