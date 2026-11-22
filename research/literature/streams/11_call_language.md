# Stream 11: earnings-call language and Q&A behaviour (draft)

Sources checked 2026-11-22, for sub-study S2 (`../../design/substudy_s2_blind_replay.md`). Notes
are in `../papers/`; all 21 rows are in `11_call_language.csv`: 6 deep notes and 15 triaged rows.
Stream 02 already covers Jha et al. (`jha-2024-chatgpt-corporate-policies`), Siano (2025) and
Choi et al. (2025); streams 03, 08 and 09 cover re-identification of masked call transcripts
(`lopez-lira-2025`, `engelberg-2025`, Wu et al. 2025, Sarkar and Vafa). Nothing below repeats
them except where a number is needed. de Kok (2025) and Kim, Muhn and Nikolaev (2023) have rows in
stream 02 too; the rows here record only what this question needs. This draft is not merged into
`../matrix.csv`.

The question the stream has to settle: S2's PM agent reads only the 8-K earnings release. What
would the earnings call add, especially managers' word choice and their behaviour in the Q&A,
for predicting next quarter's or next year's fundamentals (not only short-window returns)? Which
features are incremental to the release and to analysts? How have recent papers measured them
with LLMs, and how did they validate the measures? Which features work on the prepared remarks
alone, given that the data audit (`../../design/data_audit.md` section 2) found no licensed free
transcript source?

## What the stream establishes

**1. What a call adds beyond the release and analysts**

- **Empirical finding.** Both parts of the call add information beyond the press release, and the
  analysts' discussion adds more than the presentation, more so with more analyst following
  (`matsumoto-2011`, published abstract). In the thesis draft, longer calls lead analysts to
  revise next-quarter forecasts more and to become more accurate against actual q+1 earnings; a
  within-firm interquartile change in length moves revisions by 6.9% and accuracy by 7.6% of
  their interquartile ranges, and the effect comes from the discussion, not the presentation.
- **Empirical finding.** The one study that controls for the release's own tone, the analysts'
  tone and analysts' forecasts both before and after the call still finds that unexpected
  negativity in the call predicts next-quarter EPS (`druz-2020`, 2016 working paper, S&P 500
  2004-2012). One SD of residual negativity lowers t+1 EPS by $0.044 in the presentation
  (t = -8.33) and $0.026 in the answers (t = -5.28), against a mean of 0.73 and an SD of 0.63. With
  the consensus three days after the call as control, the presentation effect is still -0.042
  for tone disappointment (t = -5.06). The release's negativity also predicts t+1 EPS (-0.046,
  t = -4.54), so release language is not empty either.
- **Empirical finding.** The analysts' side carries signal. The negativity of analysts' questions
  predicts lower t+1 EPS (-0.074, t = -6.44) in the same regressions (`druz-2020`). Investors react
  more to analysts' tone than to managers' (Brockman, Li and Price 2015, triaged). Market reactions
  to extreme language in the Q&A come from both managers and analysts (`bochkay-2020`, online
  appendix as described in the text).
- **Empirical finding.** Vocal affect in the Q&A predicts the firm's financial future beyond the
  numbers and the words, and analysts ignore it in near-term forecasts (Mayew and Venkatachalam
  2012, triaged). A transcript loses this channel.
- **Open question.** `druz-2020` describes Mayew and Venkatachalam as finding no significant
  association between unexpected future earnings and linguistic tone "(or vocal cues)" in their
  smaller sample, which conflicts with the abstract on vocal cues. The full text was not read.

**2. Language features with evidence for future fundamentals**

- **Empirical finding.** Extreme words predict sales. One SD of signed extremity (share of
  extreme positive minus extreme negative words, rated by humans) raises the four-quarter change
  in sales by 0.0038 of assets (t = 6.31) and in earnings by 0.0020 (t = 6.77); the median sales
  change is 0.0075 and its SD 0.0591 (`bochkay-2020`, 2006-2015, broad US sample). Extreme negative
  words have the largest coefficients; moderate positive words carry nothing once controls are
  in. This is the only study in the pass with a sales outcome.
- **Empirical finding.** In the prepared presentation, gloom predicts more than cheer: tone
  disappointment -0.057 (t = -6.55), tone delight +0.028 (t = 3.45). In the answers the two are
  similar (-0.024 and +0.029) (`druz-2020`). Analysts under-react to disappointment and prices
  drift for 50 days after it, but not after delight.
- **Empirical finding.** Hedging and stilted speech predict lower t+1 EPS conditional on tone:
  uncertain words -0.072 (t = -3.30), strong modal words -0.056 (t = -2.85), words per sentence
  -0.003 (t = -2.25), "atypical tense" (presentation not in the past tense, answers not in the
  present or future) -0.018 (t = -2.03) (`druz-2020`, Table 4 columns 5-6). These are single
  specifications; no other paper here replicates them.
- **Hypothesis (from the authors, unreported).** Tone predicts out to the same quarter of the next
  year, and a presentation more negative than its own press release predicts lower earnings and
  returns (`druz-2020`, "available on request").
- **Empirical finding.** Complexity is ambiguous: it mixes informative technical content and
  obfuscation, which move information asymmetry in opposite directions (Bushee, Gow and Taylor
  2018, triaged).

**3. Q&A behaviour: scripting, non-answers, evasion, casting**

- **Empirical finding.** Scripted answers predict negative earnings surprises. When the
  spokesman's function-word style in the Q&A matches the prepared remarks, unexpected earnings
  (actual minus the analysts' median forecast) are lower by 0.082 for t+1 and 0.099 for t+2, top
  against bottom decile, 29.8% and 28.3% of the median absolute surprise (`lee-2016`, 2002-2011).
  The result holds for scripting measured against the manager's own previous four quarters.
  Analysts revise t+1 forecasts down; spreads widen.
- **Empirical finding.** Non-answers are common and only weakly tied to fundamentals. About 11%
  of responses contain an explicit non-answer, stable over 2002-2015 (`gow-2021`). One SD more
  future ROA (average of t+1 to t+3) goes with 0.215 to 0.393 percentage points fewer non-answers,
  a small effect against the 11% mean. Product questions draw refusals more under competition,
  so some refusals protect proprietary information rather than hide bad news.
- **Empirical finding.** Non-answers move prices and uncertainty more than they predict a
  direction. They go with lower post-call returns and higher implied volatility (Barth, Mansouri
  and Woebbeking 2023, S&P 500 2002-2019, triaged); investors read silence as bad news (Hollander,
  Pronk and Roelofsen 2010, triaged). LLM-flagged non-responses in S&P 500 calls 2019-2024 raise
  analysts' forecast errors (one SD: +11.24% of the mean error), dispersion and drift; only direct
  refusals matter (`liang-2025`). The authors read this as confusion, not a bad-news signal.
- **Empirical finding (weak, unpublished).** Answers that stay on the topic of the question go
  with better next-quarter earnings surprises: a 4-SD move in question-answer topic similarity
  shifts next-quarter SUE by about 0.145 SD (Chen, Rui and Whinston 2017, S&P 500 2011-2015,
  triaged; table inconsistencies, low weight).
- **Empirical finding.** Who gets called on predicts surprises: firms that favour bullish analysts
  have more negative future earnings surprises and restatements (Cohen, Lou and Malloy 2020,
  triaged). This needs analyst identities and their recommendations.
- **Empirical finding.** Deception-related word categories in CEO and CFO answers predict later
  restatements at 6-16% above random out of sample (Larcker and Zakolyukina 2012, triaged). The
  outcome is misreporting, not growth.
- **Empirical finding.** These channels are separate. Scripting is uncorrelated with refusals
  (-0.002), with favourable-analyst casting (0.008) and with vocal affect (`lee-2016`).

**4. How LLM papers measure these, and how they validated**

- **Empirical finding.** An LLM non-answer label can beat rules: 96% accuracy and 70% fewer
  errors than the Gow et al. regexes (de Kok 2025, abstract only). The companion data use a
  typology a checklist can borrow: justification (cannot give, do not know), type (complete
  refusal, qualitative only, range or percentage), question type (breakdown, forward-looking,
  related party, R&D or regulation), and spin (optimistic, neutral or pessimistic).
- **Empirical finding.** Validation quality varies widely. Regex baseline: precision 58.95%,
  true-positive rate 78.87% on 500 held-out crowd-coded responses (`gow-2021`). Multi-model
  consensus labels on 22.7 million Q&A pairs agree with humans at kappa 0.835, and a fine-tuned
  4B model reaches 84.9% Macro-F1 on a 1K expert set (EvasionBench, triaged). At the weak end,
  one paper tuned its prompt to "over 70%" overlap with 200 author-coded exchanges, GPT-4 flagged
  23.3% more non-responses than Llama 3.3, and repeat runs agreed with the first run 76.22% and
  69.11% of the time (`liang-2025`).
- **Verified fact (designs seen).** Human validation of non-LLM measures in this pass: crowd
  workers plus research-assistant adjudication (`gow-2021`); five MTurk raters per word, ICC 88%
  to 90.4%, 94.4% agreement with graduate students (`bochkay-2020`); 67 undergraduates rating
  documents (Chen, Rui and Whinston); randomisation and reading of extreme deciles, no human labels
  (`lee-2016`); none for dictionary tone (`druz-2020`).
- **Gap (this pass).** No LLM paper found links an evasiveness, uncertainty or forward-looking
  score from calls to future sales or earnings. The LLM papers that reach real outcomes measure
  other constructs: planned capex predicts capex for nine quarters, with a post-cutoff test
  (Jha et al., stream 02); GPT risk exposures predict volatility, investment and innovation, with a
  check outside the training window (Kim, Muhn and Nikolaev, triaged). Text-only earnings-surprise
  prediction is reported "with reasonable accuracy" (Koval et al. 2023, pre-LLM, triaged), but
  high accuracy on surprise labels is "often an illusion" of class imbalance (FinCall-Surprise,
  triaged).

**5. Look-ahead and point-in-time handling**

- **Verified fact (as read).** None of the deep-read studies runs an out-of-sample forecast of
  fundamentals. Residuals, deciles and topic models are fitted on the full sample
  (`druz-2020`, `lee-2016`, `matsumoto-2011`, Chen, Rui and Whinston). Lee's abnormal scripting
  uses only the previous four quarters and gives the same sign, the closest to point-in-time.
  Dictionaries and regexes are built without outcome data (`bochkay-2020`, `gow-2021`).
- **Verified fact (as read).** The LLM non-answer paper on S&P 500 calls does not address
  memorisation; its sample sits inside the models' training period (`liang-2025`). FinCall-Surprise
  (2019-2021 calls) states nothing about it.

## Prepared remarks, release quotes or Q&A

| Feature | Prepared remarks alone | Release management quotes | Needs Q&A |
|---|---|---|---|
| Excess negativity vs the release (`druz-2020`) | yes, the stronger half | partly: release negativity predicts by itself; the contrast needs both texts | no |
| Extreme vs moderate wording (`bochkay-2020`) | yes (footnote 30; appendix not read) | untested | no |
| Uncertain and strong modal words, sentence length, tense (`druz-2020`) | call-level measures; split not reported | untested | unclear |
| Scripted answers (`lee-2016`) | no | no | needs both parts |
| Analysts' question tone (`druz-2020`, Brockman et al.) | no | no | yes |
| Non-answers, evasion, topic drift (`gow-2021`, `liang-2025`, Barth et al., Chen et al.) | no | no | yes |
| Casting (Cohen et al.) | no | no | yes, plus analyst identities |
| Deception cues (Larcker and Zakolyukina) | no | no | yes (Q&A narratives) |
| Vocal affect (Mayew and Venkatachalam) | no | no | audio |

## What it means for the S2 design

Suggestions, our reading, untested. Each names the finding it rests on.

1. **Add text in steps, and price each step.** Arms: release only (current); release plus
   prepared remarks; release plus full call. The literature predicts most of the gain from the
   Q&A [`matsumoto-2011`], but the two best fundamentals results also work on prepared remarks
   [`druz-2020`, `bochkay-2020`]. Whether any S&P 500 firms file prepared remarks or CFO commentary
   as 8-K exhibits, which would give a licensed prepared-remarks arm, is an open question for the
   data audit (not checked in this pass).
2. **Compute the strongest features in code, not with an informed model.** Release-relative
   negativity (Loughran-McDonald), signed extremity (a rated lexicon), regex non-answers and
   function-word scripting can all be computed by script. That closes the hindsight channel that
   stream 09 found for an informed extractor, and the features can be handed to the PM as numbers
   or bands instead of raw text [`druz-2020`, `bochkay-2020`, `gow-2021`, `lee-2016`; stream 09].
3. **Test the reader against the features.** On clean episodes, regress the outcome on the PM's
   probability and on each code-computed feature. A feature that stays significant is a cue the
   PM missed; one that drops out is one it already used. This is the test the literature cannot
   run for us.
4. **Use within-company baselines.** Tone levels carry the manager's style [Davis et al. 2015];
   the scripting signal survives against the manager's own previous four quarters [`lee-2016`].
   Give the PM the previous quarter's release (and call, if any) and ask for change, not level.
5. **Expect small effects and power for them.** Per-SD effects are about 4-7% of an SD of
   next-quarter EPS [`druz-2020`] and about 6% of an SD of the four-quarter sales change
   [`bochkay-2020`]. No paper targets acceleration of year-over-year revenue growth.
6. **Report a proper score next to accuracy.** Surprise-style labels are imbalanced and accuracy
   on them can be an illusion [FinCall-Surprise]; S2 scores accuracy against the outcome and the
   increment over baselines, so add the Brier score and a calibration check for the probability.
7. **If an LLM labels Q&A behaviour, validate it first.** A fixed typology [de Kok], a human gold
   set with kappa [EvasionBench], repeated runs, and a second model family [`liang-2025`].

## Gaps

- No study of call language against acceleration of revenue growth; the nearest outcome is the
  four-quarter change in sales scaled by assets [`bochkay-2020`].
- No study tests any call-language feature against fundamentals after an LLM's knowledge cutoff.
- No LLM-measured evasiveness, hedging or forward-looking score linked to future sales or earnings.
- No study measures whether an LLM reader uses these cues when it forecasts.
- No study of prepared remarks or management quotes in the 8-K release as a substitute for the
  call.

## Limits of this pass

- PDFs were read through a text extraction by macOS PDFKit (spaces between words are sometimes
  lost; some minus signs in `bochkay-2020` tables were dropped, and signs there follow the text).
  No figure was read.
- Three deep notes rest on earlier versions: `gow-2021` (2019 working paper), `matsumoto-2011`
  (2010 thesis chapter), `druz-2020` (2016 working paper). Published numbers may differ.
- de Kok (2025) could not be opened (INFORMS and SSRN returned HTTP 403); its row rests on the
  abstract and the companion repository's README. All other triaged rows rest on abstracts,
  except Chen, Rui and Whinston (full manuscript read).
- Searches (web, 2026-11-22): non-answers and evasion in calls (regex, ML, LLM); script adherence;
  call tone and tone change; extreme language; manager-analyst tone; vocal cues; casting;
  deception; linguistic complexity; LLM measures from calls linked to future earnings, sales or
  surprises; evasion benchmarks.

## Unverified leads

Seen only in search results, in citations inside papers read, as titles, or as abstracts not
worth a row; nothing is claimed from them.

- Chen, Nagar and Schoenfeld (2018), Manager-analyst conversations in earnings conference calls,
  Review of Accounting Studies 23, 1315-1354: analysts, not managers, are the participants whose
  comments move intraday prices during the discussion (search snippet; abstract page not opened).
  Whether it tests future earnings is unknown.
- Huang, Teoh and Zhang (2014), Tone Management, The Accounting Review 89(3): abnormally positive
  tone in earnings press releases predicts lower future earnings (as cited by `druz-2020`;
  `bochkay-2020` cites it as evidence of strategic tone; not opened). It bears directly on the
  release quotes the PM already reads.
- "The Language of Evasion: How Semantic Similarity Between Questions and Answers Predicts Stock
  Returns", Journal of Behavioral Finance 2026 (doi 10.1080/15427560.2026.2657322): 164,944 calls
  2008-2024, 3.9% annual alpha, gross profit over assets 0.209 z-units higher one year ahead for
  on-topic answerers (search snippet; publisher page returned 403).
- A critique of the vocal-analysis software used by Mayew and Venkatachalam (search snippet).
- Bian, Chen and Wang (2022) and Liu, Cao and Flake (2024) on non-answers (cited in `liang-2025`;
  not opened).
- Zhou and Huang, Unraveling Managerial Tangents (arXiv 2309.05555, abstract read): a FinBERT
  tangent index from Q&A related to later stock prices only.
- DualEvasion (Kim, Jeong and Kwak, arXiv 2608.28040, abstract read): 505 Q&A pairs from 60 calls
  with separate text-evasion and vocal-confidence labels; multimodal models miss unconfident
  delivery.
- Lie to me: detecting managerial evasiveness via conversational audio encoders (arXiv
  2609.13893, title only).
- Koval et al., From Facts to Insights (COLING 2025): LLMs on call-derived content including
  management expectations (search snippet).

## For the S2 analysis checklist

Ranked by the strength of evidence for future fundamentals, then by whether a release-only or
prepared-remarks-only design can use it. For each: (1) evidence for future fundamentals, with
effect size and horizon; (2) what text it needs; (3) how it was measured and validated.

1. **Is management gloomier than its own release and numbers justify?**
   (1) Next-quarter EPS: one SD of unexpected negativity, -$0.044 (presentation, t = -8.33) and
   -$0.026 (answers, t = -5.28), mean 0.73 and SD 0.63; incremental to the release's tone,
   analysts' question tone and the pre- and post-call consensus; said to persist to the same
   quarter next year (unreported) [`druz-2020`]. In the presentation, excess gloom predicts about twice as strongly as
   excess cheer (-0.057 against +0.028); in the answers the two are similar.
   (2) Prepared remarks suffice for the stronger half; the release-relative contrast needs the
   release and the remarks; release quotes alone give only the release's own tone, which also
   predicts.
   (3) Loughran-McDonald word counts, residualised; no LLM, no human validation.
2. **Extreme words, especially extreme negative ones.**
   (1) Four-quarter change in sales: +0.0038 of assets per SD of signed extremity (t = 6.31;
   median 0.0075, SD 0.0591); earnings +0.0020 (t = 6.77); extreme negative words strongest;
   moderate positive words carry nothing [`bochkay-2020`]. Not controlled for release language.
   (2) Reported to hold in prepared remarks and Q&A separately; untested on release quotes.
   (3) Human-rated lexicon (five MTurk raters per entry, ICC 88% to 90.4%); no LLM.
3. **Answers that sound pre-written.** Complete, polished sentences; few starts with "and", "so",
   "but"; few broken sentences or dashes; phrasing reused from the prepared remarks (the last cue
   is our reading, not the paper's).
   (1) Unexpected earnings vs analysts: -0.082 (t+1) and -0.099 (t+2), top vs bottom decile,
   29.8% and 28.3% of median magnitudes; holds against the manager's own recent habit
   [`lee-2016`].
   (2) Needs the Q&A and the prepared remarks together.
   (3) Function-word cosine similarity; validated by randomisation and reading, not by human
   labels; no LLM. A reader model's version of this cue is untested.
4. **What the analysts' questions sound like.** Sceptical, negative or repeated follow-up
   questions.
   (1) Analysts' question negativity predicts lower t+1 EPS (-0.074, t = -6.44) beyond managers'
   tone [`druz-2020`]; investors weight analysts' tone more [Brockman et al.].
   (2) Needs the Q&A.
   (3) Dictionary tone; no LLM.
5. **Hedging and stilted delivery.** Uncertain words, strong modal words, long sentences,
   explaining results in the future tense or answering in the past tense.
   (1) Each predicts lower t+1 EPS conditional on tone (uncertain words t = -3.30; strong modals
   t = -2.85; sentence length t = -2.25; atypical tense t = -2.03) [`druz-2020`]; one paper only.
   (2) Call-level; split by section not reported.
   (3) Word lists and an automatic tense tagger; no LLM. Do not read complexity alone as evasion
   [Bushee et al.].
6. **Direct refusals, especially to forward-looking or performance questions.** Separate them
   from "we don't break that out" (often proprietary), "I don't know" and "we'll get back to you".
   (1) For fundamentals the evidence is weak: more future ROA (t+1 to t+3) goes with slightly fewer
   non-answers (0.2 to 0.4 pp per SD against an 11% base rate) [`gow-2021`]; on-topic answers go
   with better next-quarter SUE (unpublished) [Chen, Rui and Whinston]. Stronger for uncertainty
   and prices: higher analyst errors and dispersion, only for direct refusals [`liang-2025`];
   lower returns and higher implied volatility [Barth et al.; Hollander et al.]. Read a refusal as
   wider uncertainty more than as a lower point forecast.
   (2) Needs the Q&A.
   (3) Regex [`gow-2021`], trigram ML [Barth et al.], LLM labels validated at 96% accuracy
   [de Kok] and kappa 0.835 [EvasionBench], weakly validated in [`liang-2025`].
7. **Who is called on.** Not usable under blinding: it needs analyst names and their
   recommendations [Cohen et al.].
8. **Deception cues.** General-knowledge references, fewer anxiety words, extreme positive
   emotion in CEO answers; predicts restatements, not growth [Larcker and Zakolyukina].
9. **Voice.** Not in a transcript [Mayew and Venkatachalam].

**What does not work or is fragile**

- **Tone levels without a baseline.** Tone has a manager-specific component [Davis et al.]; the
  studies that work remove it with CEO or manager fixed effects or the manager's own history
  [`druz-2020`, `lee-2016`]. Scripting is serially correlated (0.49) [`lee-2016`].
- **Cheerfulness in prepared remarks.** Tone delight in the presentation predicts about half as
  much as gloom and is priced at once [`druz-2020`]; moderate positive words carry nothing
  [`bochkay-2020`].
- **Non-answers as a directional signal.** They mostly raise uncertainty [`liang-2025`]; some
  protect proprietary information [`gow-2021`]; the fundamentals link is small.
- **Complexity or readability as obfuscation.** It mixes two opposite components [Bushee et al.].
- **Label noise.** Regex precision 59% [`gow-2021`]; two LLMs disagree on about a fifth of flags
  and a single LLM repeats its own label about three times in four [`liang-2025`].
- **Market results as evidence of fundamentals.** Barth et al., Hollander et al., Price et al. and
  Brockman et al. test prices only.
- **Accuracy on imbalanced surprise labels** [FinCall-Surprise].
- **Robustness gaps.** Lee's guidance result is not robust to the within-manager measure and his
  90-day return result is significant only at 10%; several Druz results are "available on
  request"; Bochkay's section split is in an appendix not read.
- **Size.** All effects are a few percent of an SD. In `druz-2020` the adjusted R-squared of the
  earnings model is 0.84 and the pre-call consensus (coefficient 0.68) carries most of it; no
  column without tone is reported, so the R-squared gain from tone is unknown.

**Would call language make a blinded text easier to re-identify?**

Yes, plausibly by more than the release does (our reading; not tested on companies). Raw
transcripts carry the operator's introductions with executives' names and titles, analysts' names
and banks, and product names; automatic tagging found product names with 78.67% accuracy, so a
scrub misses some [`gow-2021`]. Style survives name removal: function-word counts alone pick the
speaking manager out of ten in 79.8% (Q&A) and 87.0% (prepared remarks) of calls [`lee-2016`], and
tone has a stable manager-specific component [Davis et al.]. The set of analysts on a call maps to
a coverage list, which points to the company (our reading). Stream 03 records that firms are
re-identified from entity-masked call transcripts in 31% to 70% of cases (`lopez-lira-2025`,
`wu-2025` and an NBER conference paper), against 9% after LLM rewriting (`wu-2025`). If call text
enters S2, pass code-computed features or a fixed-template summary (stream 09's
extract-then-render), replace speakers with roles (CEO, CFO, Analyst 1 to n), and run the stream
09 attacker on each new text arm before scoring forecasts.
