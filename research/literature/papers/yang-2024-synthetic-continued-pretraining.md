# Synthetic continued pretraining

- **Citation:** Yang, Z., Band, N., Li, S., Candès, E., Hashimoto, T. (2025). ICLR 2025 (listed as
  a poster on the ICLR virtual site; the ICLR slides are marked oral, not checked further).
  arXiv 2409.07431. Version read: v2 (3 October 2024), HTML, main text and appendices C-H; the last
  6% of the page not read.
- **Link:** https://arxiv.org/abs/2409.07431 (HTML: https://arxiv.org/html/2409.07431v2; ICLR page:
  https://iclr.cc/virtual/2025/poster/31270)
- **Stream:** 14a
- **Verified against source:** yes, 2026-11-25, against the arXiv abstract page, the v2 HTML through
  an automated page reader, and the ICLR poster page.

## Question

A small corpus states each fact once or a few times; models need many varied restatements to learn
a fact. Can a prompted model turn a small corpus into a large, varied synthetic corpus, so that
continued pretraining makes a model *know* the corpus (answer and follow instructions about it
without seeing it)?

## Data

QuALITY: 265 articles and short books, about 5,000 tokens each, about 1.3M tokens in all.
Evaluation: QuALITY's four-option reading questions asked closed-book (the article is not given).

## Method

- EntiGraph: (1) the generator extracts a summary and a list of entities from each document;
  (2) for sampled pairs, and some triples, of entities, it writes text analysing how they relate,
  with the document in its prompt. The combinatorics of pairs gives far more distinct text than
  paraphrasing does.
- Generator: gpt-4-turbo. 455M synthetic tokens from 1.3M source tokens (about 350 times).
- Continued pretraining of Llama 3 8B Base: 2 epochs, 10% of batches replayed from RedPajama,
  peak lr 5e-6, about 41 hours on one 8xH100 node. Then instruction tuning on UltraChat (about 250M
  tokens).
- Baselines: continued pretraining on the raw 1.3M tokens (4 epochs, tuned); "Rephrase" in the
  style of WRAP (stopped at 38M tokens); synthetic QA fine-tuning (about 28M tokens, over $5k).
- Evaluation: 5-shot chain of thought, 64 samples per question, one valid answer drawn at random.

## Outcome variable and horizon

Closed-book QuALITY accuracy; open-book accuracy with retrieval; claim-level precision of
closed-book summaries. No horizon.

## Result

- **Empirical finding:** closed-book accuracy 39.49 (base) to 56.22 (EntiGraph, 455M tokens),
  above GPT-4 closed-book 51.30 and GPT-3.5 44.81. Raw continued pretraining fell below the base
  model. Rephrasing scaled poorly (exact value not in the text read).
- **Empirical finding, scaling:** accuracy rises log-linearly with synthetic tokens up to 455M; a
  three-phase fit (linear, log-linear, plateau) is given; no plateau was reached in the data.
- **Empirical finding, with retrieval:** EntiGraph + RAG 62.60 against base + RAG 60.35. Closed-book
  EntiGraph recovers about 80% of RAG's gain (16.73 against 20.86 points).
- **Empirical finding, instructions:** after instruction tuning the model summarises and compares
  the source articles closed-book; false claims rise only slightly with summary length (figures,
  not tabulated in text).
- **Hypothesis (authors):** the gain is not plain distillation of GPT-4's knowledge, since the
  student beats GPT-4 closed-book; a toy model attributes it to the generated text "filling in"
  relations between entities.

## Look-ahead and memorisation

Not relevant to finance. The method is memorisation by design: its purpose is to put the source
corpus into the weights. For our use that is the risk: training on releases from a period means the
model may recall their numbers when tested on the same releases.

## What it settles for us

- The strongest evidence that **document-grounded synthesis teaches a model what is in documents,
  where training on the raw documents does not**, and that the return keeps rising with synthetic
  volume (log-linear to 350 times the source). This is the paper behind "let the teacher generate
  a lot" when the aim is knowledge of a corpus.
- It is about knowledge of a fixed corpus, not about reasoning procedures. For S1 the analogue would
  be making the 0.8B familiar with how earnings releases describe margins, segments, non-GAAP items
  and guidance, by generating many varied analyses of each release (hypothesis for S1). It does not
  show that such familiarity improves label or judgement items.
- Diversity comes from the *structure* of the prompts (entity pairs and triples), not from
  temperature. The finance analogue: line item x line item, period x period, segment x total
  (hypothesis).
- Teacher quality matters: the authors checked a subset by hand and found no factual errors, but
  credit this to gpt-4-turbo and warn that harder text may produce hallucinated relations; they did
  not test a weaker or self-generating generator. With a local 4B-20B generator on S1's machine,
  faithfulness has to be measured, not assumed.
- Scale for us: 455M tokens at 41 H100-hours for an 8B model is far beyond a 12 GiB MLX budget for
  training, though a 0.8B needs roughly a tenth of the compute per token. Generation of hundreds of
  millions of tokens by a local teacher would take weeks to months (hypothesis, to be measured).

## Limits

One corpus (fiction and journalism, not tables); one model size (8B); one generator; reading
questions with four options; generation cost about two orders of magnitude above the source.
