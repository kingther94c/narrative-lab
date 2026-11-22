# Stream 09: blinding by extraction and re-rendering (draft)

Sources checked 2026-11-22, for sub-study S2 (`../../design/substudy_s2_blind_replay.md`), after
EXP-0031. Notes are in `../papers/`; all 24 rows are in `09_rewrite_blinding.csv`: 9 deep notes,
one covered paper re-read for a section its note leaves out (`lopez-lira-2025`, sections 5.6, 5.7
and appendix A.7), and 14 triaged rows. Streams 03 and 08 already cover `engelberg-2025`,
`wu-2025`, `levy-2026`, `glasserman-2023`, `jeon-2026`, `li-2025`, `lopez-lira-2025`, `gao-2025`,
`roy-2026`, `li-2026`, `jia-2026`, `ye-2026`, `benhenda-2026`, `wu-2026`, `jiang-2026` and
`merchant-2025`; nothing below repeats what they say. This draft is not merged into
`../matrix.csv`.

The question the stream has to settle: EXP-0031 reduced each release to a fixed form of
forecast-relevant facts, checked each value against a verbatim quote and rendered one template
for every company. Recognition fell to about 40% and the old-minus-clean leak to about zero, and
forecast accuracy fell too. How can the template stop recognition while keeping the signal, and
how can we know that the extractor, which knows the company and, for old episodes, the outcome,
did not carry that knowledge into the form?

## What the stream establishes

**1. Extract, then re-render: recognition and task utility**

- **Empirical finding.** The closest finance test of the design is a one-sentence "economic
  logic" that GPT-4o writes for a headline without specifics, which is then masked. Before the
  cutoff the firm is still named for 46.3% of Apple, 27.5% of Tesla and 21.6% of Microsoft
  headlines, but 3.3% of Alphabet and 0.6% of Nvidia (`lopez-lira-2025`, Table 10 Panel B). The
  industry is named 62.4% of the time for FF5 Consumer against 20% by chance (Table 12).
  Directional accuracy is 50.74% to 58.19% excluding "unknown", with no raw-text arm and 16 to 36
  post-cutoff headlines per stock. The authors conclude that text specific enough to forecast
  tends to reveal identity, and that the procedure fails their future-invariance test.
- **Gap (this pass).** No paper found tests the EXP-0031 design itself: a fixed schema of numbers
  and menu choices, each checked against a quote, rendered by code, with recognition and forecast
  utility both measured. The searches are listed under Limits.
- **Empirical finding.** Outside finance, a rewriter that is scored on task utility as well as on
  re-identification keeps more of the task at the same re-identification rate. On biographies,
  occupation accuracy 96.02 against 92.02 at a re-identification rate near 53%. On a subtle task
  both lose most of it: 58.45 falls to 35.75 (utility-aware) and 21.26 (privacy only) at about
  35% (`yang-2025`, Tables 1 and 2).
- **Empirical finding.** Iterated adversarial rewriting removes specific cues and stalls on
  coarse ones. Against GPT-4, city falls from 24.6% to 1.3% and country from 59.2% only to 46.1%
  over three rounds, while judged meaning falls from 0.79 to 0.67 (`staab-2025`, Tables 1 and 2).
  The loop works when it is told exactly what to protect: residual risk 2% with the exact list of
  attributes and 44% with a generic list (`krco-2026`, Table 2). Our reading: EXP-0030's fall-back
  to segment structure and reporting style is the generic-list case, and the coarse cue that
  stays is the sector.
- **Empirical finding.** The least a prompt must disclose to keep a task working depends on the
  model and is smaller for stronger ones: at the minimum, 85.7% of sensitive spans can be
  redacted for gpt-5 and 19.3% for qwen2.5-0.5b. Redacting protects better than abstracting (an attacker
  recovers 2.7% to 7.7% of redactions and 5.6% to 14.9% of abstractions). Asked which spans they
  need, models overshare (`zhou-2025`, Table 2 and the appendix tables).
- **Triaged.** LLM paraphrase keeps sentiment F1 on reviews and cuts authorship F1 by 46% against
  a static and 26% against an adaptive attacker (Utpala et al. 2023). A rewrite whose scope adds
  each transcript's own quasi-identifiers leaves 0 to 7 of 53 transcripts re-identified by
  web-search agents, at a unit-recovery utility of 72.0% to 76.1%, against 26 to 40 of 53 and
  95.6% for entity removal (Li, Wen and Li 2026). The one finance paper that scored a rewriter's output
  after the model's cutoff (Kim, Muhn and Nikolaev, Bloated Disclosures) has been withdrawn and
  carries no weight.

**2. Keeping the extractor's knowledge out of the content**

- **Gap (this pass).** No paper found tests whether an informed extractor or rewriter tilts its
  output towards what happened later. The designs closest to ours leave the channel open without
  discussing it: the neutering rewriter is told the firm (`engelberg-2025`, stream 08); RUPTA's
  evaluators see the true person and the true label while the rewriter optimises against them
  (`yang-2025`); the minimisation oracle uses the correct answer (`zhou-2025`); TimeSPEC's claim
  auditors are informed models whose labels are not validated against humans in the text read
  (Zhang, Chen and Stadie 2026, v2).
- **Empirical finding.** An informed model asked to extract does add later knowledge: risk
  factors generated from 2019 earnings calls named COVID-19 in 6.8% of cases (Sarkar and Vafa,
  stream 03 row).
- **Empirical finding.** Instructions do not separate knowledge from content. Told the as-of
  date, GPT-5 stops claiming knowledge (0.39 to 0.01) and answers as well as before (0.76 to
  0.75); it is right on 0.61 of the facts it says it does not know (`qian-2026`, Table 4). Models
  ignore instructed cutoffs across prompting strategies (Liu et al. 2025, triaged), and prompting
  a current model does not reproduce a past perspective (Underwood et al. 2025, triaged).
  `ludwig-2025` (stream 07) found date-restriction prompts still reproduced training text.
- **Empirical finding.** When the document is right and the model's memory is wrong, strong
  models follow the document: Claude Opus keeps a wrong prior in 2.1% of cases. When the document
  has been altered, Opus resists it more than the other five models (adopts the wrong document in
  15.7%), and the more confident the prior, the less the document is adopted (slopes -0.1 to
  -0.45) (`wu-2024`, v3 Table 4 and section 4.4). Our reading: in EXP-0031 the quote-checked
  numbers are the low-risk channel; the risk sits where no quote pins the answer (menu
  judgements, which facts get reported, values marked as computed).
- **Triaged.** LLM summaries changed the sentiment of their source in 26.42% of cases (Alessa et
  al. 2025). A tone or outlook judgement by the extractor is not neutral even without hindsight.
- **Verified fact (designs seen).** Four ways of separating a model's knowledge from the content
  appear in the sources: answer only from audited claims (TimeSPEC's closed-world aggregator,
  which blocks only what is put into words); use a model whose knowledge ends earlier
  (point-in-time models stay near chance on dated facts, `qian-2026` Table 8, and stream 03 found
  them too weak to extract); check a random validation subset against an independent measurement
  and correct (`ludwig-2025`); judge utility with a model of another family than the rewriter
  (Li, Wen and Li 2026). None was tested for hindsight.
- **Open question.** Whether a quote check constrains selection. An extractor that chooses which
  true facts to report can tilt the brief while every value passes (our reading).

**3. Attack and defence protocols to borrow**

- **Empirical finding.** LLMs infer from context, not from named entities. GPT-4 infers personal
  attributes at 85.5% top-1 and 95.2% top-3. Entity removal cuts the easiest items from 85.0% to
  43.9% and the hardest only from 69.2% to 61.5% (`staab-2024`, Table 3).
- **Empirical finding.** Protection is bounded by the attacker used to build and test it. Weaker
  attackers "clearly underestimate" leakage (`staab-2025`, appendix A.5). A reasoning attacker
  that aggregates guesses over several orderings raises re-identification from 44.7% to 57.2%
  with worst-case background knowledge (Charpentier and Lison 2025, triaged). An adaptive attacker recovers about half of the
  protection a paraphrase gave (Utpala et al. 2023, triaged).
- **Method.** Turn the attacker's inferences into a population probability that the best match is
  correct, and count a record as re-identified when fewer than about five people match
  (`krco-2026`, using `rocher-2019`). Most residual risk came from indirect identifiers, which all
  twelve tools often missed.
- **Method.** Ask the attacker whether a guess rests on direct evidence or on base rates
  (`staab-2025`); steer it to a decoy value as a defence (Frikha et al. 2024, triaged), which for
  S2 is the published form of the wrong-identity positive control, not a usable defence on fields
  the forecast needs (our reading).
- **Method.** Score utility with the downstream model rather than text similarity, and report the
  frontier across rounds (`yang-2025`, `staab-2025`).

**4. Numeric fingerprints and coarsening**

- **Empirical finding.** Coarsening has weak returns. In mobility traces, halving spatial or
  temporal resolution makes identification 9.3% less likely given four points and 6.2% given
  ten; "even coarse datasets provide little anonymity" (`demontjoye-2013`). In card records, four
  points identify 90% and knowing the amount raises risk by 22% (de Montjoye et al. 2015,
  triaged). A counterpoint: a formal privacy model applied to the whole record brought
  unequivocal re-identifications to zero with more utility than ad hoc coarsening (Sánchez et
  al. 2016, triaged).
- **Empirical finding.** A few ordinary attributes suffice. Fifteen demographic attributes make
  99.98% of Massachusetts residents unique, releasing a sample does not protect, and the chance
  that a match is correct has a closed form per record (`rocher-2019`).
- **Empirical finding.** Repeated observations raise risk: 17% to 94% of panelists in purchase
  panels are at high risk, and the usual unicity measure understates it (Li, Schneider, Yu and
  Gupta 2023, triaged).
- **Gap.** No study measures how identifiable a company is from ratios, growth rates or segment
  mixes. Stream 08 has the nearest: `levy-2026` (no identification test), Kim, Muhn and Nikolaev
  2024 (0.07% of firms named from statements; withdrawn) and the size gradient of
  `engelberg-2025`. The statistical-disclosure literature on business microdata says the largest
  firms are identifiable by size within their industry; that is an unverified lead here.

**5. Alternatives that keep a commercial model (brief)**

- **Empirical finding.** Knowledge boundaries must be measured: GPT-4o's ends about seven months
  before its stated cutoff, GPT-5's matches it, and self-reports and declared dates certify
  nothing (`qian-2026`). This supports stream 08's strategy C (select periods instead of
  blinding) and leaves only months of history for a frontier model (our reading).
- **Triaged.** Steering a model's internal time-awareness features cuts look-ahead but needs
  model internals (Merchant and Levy 2026). A point-in-time retrieval corpus closes retrieval
  leakage only (Ye et al. 2026, Hindcast).

## What it means for template v2/v3

Suggestions, our reading, untested. Each names the finding it rests on.

1. **Count the anonymity set in code before calling the attacker.** For each brief, count the
   S&P 500 companies in the same quarter whose as-filed figures fit every field (sector, size
   band, growth bands, margin bands, number of segments, guidance sign), or compute κ from
   `rocher-2019`. Report the share of briefs that fit fewer than five companies. If the attacker
   hits more often than one over the set size, it is using something outside the fields (wording,
   order, recall of exact figures). [`krco-2026`, `rocher-2019`]
2. **Remove fields rather than round them.** Segment revenue shares and a dozen growth rates make
   a long record; halving their precision buys little [`demontjoye-2013`], and redaction
   protects better than abstraction [`zhou-2025`]. Candidates: replace segment shares by the
   number of segments and each segment's growth band; give growth as a band relative to the
   sector median of that quarter; coarsen or drop the sector label and measure what the forecast
   loses.
3. **Choose fields by a minimisation search on episodes the PM cannot remember.** Start from the
   most protective brief, add one field at a time, keep the smallest brief at which forecast
   accuracy on clean or development episodes stops improving, and log every version scored (the
   ledger rule of `gencay-2026`, stream 08). Using old episodes' outcomes for this would select
   fields that help recall. [`zhou-2025`, `yang-2025`]
4. **Restore guidance in a form that is not a fingerprint.** EXP-0031 lost the guidance signal.
   Its direction and size relative to the company's own previous guidance and to the reported
   quarter, in bands, carries the forecast-relevant part without the levels (our reading; check
   with suggestion 1).
5. **Noise after extraction, never before.** An informed extractor given altered numbers may
   restore the true ones [`wu-2024`]. EXP-0031 already noises in code; keep it that way.
6. **Take the judgements away from the informed reader.** Numbers checked against quotes are the
   low-risk channel [`wu-2024`]; menu judgements are where knowledge of the outcome can enter
   without a quote [Sarkar and Vafa; Alessa et al.]. Either drop them or have them made by a model
   that sees only the FACTS brief, not the raw release. EXP-0031's FULL-minus-FACTS contrast
   measures this channel; the change would close it.
7. **Test the extractor for hindsight on a validation subset.** On a random subset of old and
   clean episodes, extract the same fields independently: by rule from the release's tables where
   possible, or with a local open-weight model whose knowledge boundary has been measured to fall
   before the episode dates. Regress the difference (Opus minus independent) for each field on
   the realised outcome, separately for old and clean episodes. A slope on old episodes only is
   hindsight. [`ludwig-2025`, `qian-2026`]
8. **Audit selection, not only values.** Record which of the available segments, indicators and
   effects the extractor reported; test whether what it left out is related to the outcome on old
   episodes and not on clean ones. (Open question 2 above.)
9. **Strengthen the attacker and the readout.** Several samples per brief with aggregated top-k
   guesses [Charpentier and Lison]; a field for "direct evidence or base rate" [`staab-2025`];
   chance benchmarks per quarter [`engelberg-2025`]; sector and date recognition reported
   separately [`lopez-lira-2025`]; and, if the PM's memory holds several episodes of one company,
   an attack on the sequence, not only on single briefs [Li et al. 2023].
10. **Keep a wrong-identity arm** as the positive control [Frikha et al.; stream 08].

## Gaps

- No study of schema extraction plus code rendering as a blinding method, in finance or
  elsewhere, with recognition and task utility both measured.
- No test of hindsight carried by an informed extractor, rewriter or lesson writer (the stream
  08 gap stands after this pass).
- No measurement of how identifiable a company is from its figures.
- No evaluation of any of these protocols on Claude Opus 5.5 or Sonnet 5.5.

## Limits of this pass

- Every arXiv source was read through a machine extraction of its HTML, in several cases only the
  first 100,000 characters; numbers that appear only in figures were not read; no number was
  checked against a PDF. This machine has no PDF text tool, so the NBER copy of Sarkar and Vafa
  and the CASC deliverable on business microdata could not be read; the Sarkar and Vafa figure is
  stream 03's.
- Searches (web, 2026-11-22): LLM extract-then-predict for look-ahead; anonymised structured
  summaries of earnings calls; hindsight in rewriters and summarisers; LLM anonymisation with
  utility; re-identification attacks; firm re-identification from financial numbers; statistical
  disclosure control for business data; uniqueness and coarsening; knowledge conflicts;
  knowledge-boundary probing; synthetic firms.
- `lopez-lira-2025` section 5.7: the appendix prompt asks for three sentences, the body and
  Figure 8 describe one; the post-cutoff year-guess rates (21.0% to 34.0%) are higher than before
  the cutoff and are not discussed by the authors.
- ClashEval's two versions report different headline rates; the v3 table is used.
- Stream 08's TimeSPEC row reflects v1; this pass read v2, whose numbers differ.
- The triaged rows rest on abstracts or partial reads.

## Unverified leads

Seen only in search results or titles; nothing is claimed from them.

- AgentDoxx (arXiv 2610.05586): after entity masking, at least one web-search attacker
  re-identified 85.3% of a sample of transcripts (search snippet).
- Statistical disclosure control for business microdata (CASC deliverables at research.cbs.nl;
  an Istat working paper of 2006; an OECD document STD/DOC(2011)2): turnover identifies very
  large firms within an industry class, additive noise barely moves outliers, and public-use
  business files are rare (search snippets; PDFs not readable here). Ruiz (arXiv 1712.02549,
  abstract read) proposes multiplicative masking that keeps skewness.
- Dou et al. (ACL 2024, arXiv 2311.09538): abstraction of self-disclosures ("16F" to "a teenage
  girl") gives a moderate privacy gain at high utility (search snippet).
- GRASP (arXiv 2608.06526): anonymisers trained by reinforcement learning (title only).
- "Can Prompt Anonymity Protect Your Identity From LLM Providers?" (arXiv 2609.33903): 50% to
  75% of users re-identifiable after rewriting defences (search snippet).
- Self-Blinding and Counterfactual Self-Simulation (arXiv 2601.14553): a model simulating not
  knowing; may bear on question 2 (title only).
- Frame In, Frame Out (arXiv 2505.05406): LLM news summaries frame more than human references
  (search snippet).
- Synthetic-firm benchmarks: FinMaster (arXiv 2505.13533), V-FiLLM (arXiv 2608.11047), FinForge
  (arXiv 2601.06747). Synthetic companies avoid recall but carry no real outcome, so they cannot
  supply S2's learning signal (our reading; search snippets only).
- CROSS-MAP (Mao and Zhao, arXiv 2609.23193, abstract read): maps inputs into another semantic
  domain before inference and back; no structured schema.
- Look-ahead freedom as temporal non-interference (Fonseca, arXiv 2607.04958, abstract read): a
  checkable property of data pipelines; does not address what a model knows.
- NoLBERT (arXiv 2509.01110) and "Evaluating LLMs in Finance Requires Explicit Bias
  Consideration" (arXiv 2602.14233): titles only.
