# Instruction Pre-Training: Language Models are Supervised Multitask Learners

- **Citation:** Cheng, D., Gu, Y., Huang, S., Bi, J., Huang, M., Wei, F. (2024). EMNLP 2024 (main
  conference, per the arXiv comments field). arXiv 2406.14491. Version read: v2 (28 November 2024),
  HTML, about 92% of the page (the tail of the appendix not read).
- **Link:** https://arxiv.org/abs/2406.14491 (HTML: https://arxiv.org/html/2406.14491v2)
- **Stream:** 14a
- **Verified against source:** yes, 2026-11-25, against the arXiv abstract page and the v2 HTML
  through an automated page reader. Table 5 (synthesizer quality) was garbled in extraction and is
  not cited by column.

## Question

Does converting raw pre-training text into "text plus instruction-response pairs about that text"
make better models, both from scratch and when continuing pre-training on a domain (biomedicine,
finance)?

## Data

- Synthesizer training: about 34 context-based data sets in 8 domain groups (expert materials,
  encyclopedia, fiction, news, trivia, academic tests, social media, multi-domain), at most 10K
  examples each; formats free-form, multiple choice, and both with chain of thought.
- From scratch: RefinedWeb subset, 100B tokens; 40M raw texts (one fifth) converted in two rounds
  into 200M pairs (about 10B tokens), covering 40+ task categories (abstract).
- Domain: PubMed abstracts; financial news (corpus not released).

## Method

- An "instruction synthesizer" (Mistral-7B-v0.1 fine-tuned on the data above) reads a raw text and
  writes instruction-response pairs about it, about 5 pairs per text, about 52 tokens each;
  multi-round synthesis prepends earlier rounds so later pairs differ.
- From scratch: 500M and 1.3B models on raw text plus synthesized pairs against raw text alone.
- Domain-adaptive continued pre-training of Llama3-8B: domain raw text plus synthesized pairs,
  against raw text alone; general instructions mixed in.
- Ablations: no general corpora; rule-based task mining (as in AdaptLLM, Cheng et al. 2024 ICLR)
  instead of the synthesizer; one-shot instead of multi-round synthesis.

## Outcome variable and horizon

Zero- or few-shot accuracy on general benchmarks; for finance, ConvFinQA, FPB, FiQA SA, Headline and
NER, averaged. No horizon.

## Result

- **Empirical finding, finance (Llama3-8B):** average 70.1 (Llama3-8B) / 72.0 (continued
  pre-training on raw text) / 74.7 (instruction pre-training) against 71.9 for Llama3-70B.
  Biomedicine: 53.6 / 58.4 / 61.3 against 63.9 for Llama3-70B.
- **Empirical finding, ablations (finance averages):** without general corpora 73.3; rule-based
  tasks 73.1; one-shot synthesis 73.1; full method 74.7. Biomedicine 58.6 / 58.8 / 58.5 / 61.3.
  The model-written, multi-round tasks beat rule-mined tasks by 1.6 (finance) and 2.5
  (biomedicine) points.
- **Empirical finding, from scratch:** averages over nine benchmarks (my averaging of the reader's
  table values): 500M 45.1 to 46.6; 1.3B 48.6 to 49.7. The 500M model on 100B tokens is close to
  Pythia-1B on 300B (46.6 against 47.1). Instruction-pre-trained models also improve faster during
  later instruction tuning (figure only).
- **Empirical finding, quality of the synthesized pairs:** judged by GPT-4, response accuracy
  77.5% (general), 86.2% (biomedicine), **69.8% (finance)**, context relevance 92.9 / 99.4 / 85.8%;
  human check 75.5 / 81.0 / **73.5%** accuracy and 87.5 / 97.0 / 88.0% relevance. About three in
  ten finance pairs are wrong and the model still gains.
- No intervals or seeds; the authors flag the finance NER results as unstable.

## Look-ahead and memorisation

Not addressed. The finance news corpus is undated in the text read and not public; evaluation sets
(FPB, FiQA, Headline, ConvFinQA) are older than the corpus may be.

## What it settles for us

- Evidence that **a 7B model can be trained to write varied tasks from raw domain text, and that
  training on text plus those tasks beats training on the text alone** in finance (+2.7 over raw
  continued pre-training at 8B) and outperforms rule-mined tasks. It is the closest published
  design to "a teacher reads each 8-K release and writes many different questions and answers about
  it".
- It shows the gain survives a noisy generator (70-74% correct finance pairs). That is encouraging
  for a local 4B-20B generator, but the outcome tasks here are sentiment and headline
  classification plus ConvFinQA; nothing tests whether wrong pairs teach wrong *reasoning*
  (open question for S1).
- The from-scratch results show the mechanism works at 500M-1.3B, the size of S1's student, but
  only for general benchmarks and from scratch, not for continued training of a released 0.8B.
- Pairs are short (about 52 tokens). The gain comes from many small, varied tasks per text, not
  from long traces. For S1 this argues for a mix of many short tasks per release alongside fewer
  worked analyses (hypothesis).
- Reusable: the released synthesizer and data (LMOps repository, per the abstract), as a
  comparison generator for S1 if a licence and size check allow; the multi-round prompt format.

## Limits

Finance evaluated on five older classification and QA sets, mostly sentiment; no reasoning or
judgement items; single runs; corpus not public; the synthesizer is tuned on general reading data
sets, not on financial tasks.
