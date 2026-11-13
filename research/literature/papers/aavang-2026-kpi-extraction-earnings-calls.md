# Effective Performance Measurement: Challenges and Opportunities in KPI Extraction from Earnings Calls

- **Citation:** Aavang, R. T., Tjalk-Bøggild, R., Iolov, A., Rizzi, G., Zhang, M., and Bjerva, J. (2026). Proceedings of the 64th Annual Meeting of the ACL, Volume 6: Industry Track, pp. 1434–1460. Version read: the ACL Anthology camera-ready PDF (full text, including appendices A to G), cross-checked against arXiv 2605.03147v1.
- **Link:** https://aclanthology.org/2026.acl-industry.100/ (arXiv: https://arxiv.org/abs/2605.03147; data: https://huggingface.co/datasets/AAU-NLP/effective-performance-measurement; code: https://github.com/aaunlp/effective-performance-measurement)
- **Stream:** 04 Financial NLP benchmarks and data sets
- **Verified against source:** yes, 2026-11-12

## Question

Two questions. Do encoders fine-tuned on XBRL-tagged SEC filings carry over to earnings call
transcripts? How well do current LLMs extract KPIs from calls when no fixed label schema is given?

## Data

- Universe: 20 S&P 500 companies (AAPL, JNJ, JPM, AMZN, BA, PG, XOM, NEE, GOOGL, DOW, PLD, MSFT,
  PFE, BAC, HD, CAT, KO, CVX, DUK, SHW), 2023 to 2024. Large caps only; delisted firms are not
  included.
- Text source: 10-K and 10-Q filings from the SEC; call transcripts from Financial Modeling Prep.
- SECB: 41K entries and 78K entities from filings. Gold is the filers' XBRL tags plus two regex
  pseudo-tags (dollar, percentage) for untagged numbers.
- ECB: 10,477 speaker-turn chunks from the calls. Unlabelled.
- ECB-A: 587 chunks (147 words on average) from 10 randomly chosen full transcripts, with 2,460
  entities and 934 relational groups.
- Licence: the Hugging Face card is tagged MIT. The paper states no licence and does not discuss
  the redistribution terms of the vendor transcripts.

## Method

- Gold for ECB-A: **one** domain expert, two passes about three months apart. Pass one tags KPI
  descriptors and values (traditional, non-traditional, value). Pass two confirms the entities and
  links them into groups. No agreement statistic between the passes is reported.
- A gold group links a KPI to its value, scope (division, product or geography), temporal context
  and modality. Modality covers words such as "guidance", "projected", "expected" and "target", so
  forward-looking figures are in scope. The guidelines give a worked guidance example. No count of
  guidance items is reported.
- Systems: SEC-trained BERT taggers (SEC-BERT-BASE, BERT-SL1000 and variants) against few-shot
  LLMs with a structured-output prompt that mirrors the annotator guidelines (Gemma-3-27B,
  Qwen3-30B-A3B, Llama-3.3-70B, Gemini 3 Pro).
- Metrics: Exact F1 (string match on label and value); Semantic F1 (cross-encoder similarity,
  many-to-one); Match F1 (pairs aligned one-to-one by value, then label similarity); LLM judge
  (DeepSeek-V3.2), the share of gold groups found. In the aggregation pipeline numeric values must
  agree within 1%, and labels are clustered at similarity 0.85.
- Human check of the pipeline output: three non-expert evaluators, 200 extractions each, 100 shared.

## Outcome variable and horizon

Extraction quality against ECB-A, and the precision of aggregated extractions as judged by humans.
No market outcome and no horizon.

## Result

No intervals are reported for any figure.

- Empirical finding: SEC-trained encoders do not transfer. Exact F1 is 0.0 for all five on ECB-A;
  Semantic F1 is at most 7.1 and the judge score at most 0.9.
- Empirical finding: LLMs on ECB-A, in the order Exact / Semantic / Match / Judge (%): Gemini 3 Pro
  11.5 / 61.6 / 39.2 / 45.5; Llama-3.3-70B 3.4 / 51.5 / 25.8 / 26.6; Qwen3-30B-A3B 3.5 / 38.1 /
  26.2 / 33.9; Gemma-3-27B 3.2 / 40.0 / 11.6 / 8.8. The running text swaps the Qwen and Llama judge
  figures relative to Table 3.
- Empirical finding: human check of the pipeline. Precision 79.67% (478 of 600). Krippendorff's
  alpha 0.429; mean Cohen's kappa 0.39 (pairwise 0.53, 0.36, 0.27); raw agreement 69%. The authors
  attribute the low alpha to the high share of positive labels.
- Empirical finding: the gold is incomplete. Of 100 unmatched predictions sampled per model, 18%
  to 32% were valid KPIs the annotator had missed. The authors describe ECB-A as a partial gold
  standard.
- Empirical finding: across two years of calls the pipeline tracks 1,323 KPIs over at least four
  periods; the three open models agree on 4.16% of them.
- Verified fact: on the paper's Boeing example (a free cash flow target next to a reference to a
  guidance range) the models disagree. Two relate the target to the KPI under different labels, one
  extracts both but does not relate them, and one groups them wrongly, so the consensus pipeline
  outputs nothing for that guidance item.

## Look-ahead and memorisation

Not handled. The limitations section says the 2023 to 2024 data is most likely in the training data
of some of the evaluated LLMs. No cutoff analysis and no memorisation test.

## What it settles for us

- **Gold labels checked by one human (supports, with a warning).** A peer-reviewed benchmark was
  built with a single expert who revisited the work after three months. That is a precedent for the
  one-annotator default. The warning: the authors list the single annotator as a limitation, report
  no test-retest statistic, and find that up to a third of sampled "errors" were valid items the
  annotator missed. A recall-style score against single-annotator gold understates precision.
- **Sub-task 1, guidance tuples (supports the schema, leaves the benchmark open).** The tuple
  (KPI, value, scope, period, modality) is close to a guidance tuple. Guidance is tagged but is not
  separated, counted or scored on its own, and nothing is compared across quarters as a label.
- **Hypothesis that no benchmark labels guidance revisions (not refuted).**
- **Scoring convention we can reuse.** Value-first alignment with a 1% tolerance, scale
  equivalence (thousands, millions) and separate handling of ranges, reported next to an exact
  match score. Exact F1 is 3% to 12% for the individual models, while humans judge the aggregated
  output 79.67% precise. The two are not the same quantity, but the gap shows exact match is too
  strict to be the only score.
- **Agreement statistic.** Chance-corrected agreement drops when one label dominates (alpha 0.43
  at 69% raw agreement). Our change class will be dominated by "maintained", so report raw
  agreement and a prevalence-robust statistic alongside kappa.
- Reuse: the annotation guidelines (Appendix D and Listing 2), the matching logic (Appendix B),
  and ECB-A as an out-of-domain extraction probe.

## Limits

- 20 large US companies; 10 transcripts annotated. Nothing on small caps or press releases.
- Transcripts, not EDGAR documents: the text source our default avoids.
- One annotator; partial gold; no retest statistic.
- LLM judge not validated against humans; human evaluators were not experts.
- Abstract and body differ on what the 2,460 figure counts (annotation groups or entities).
