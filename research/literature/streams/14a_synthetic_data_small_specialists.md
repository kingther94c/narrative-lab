# Stream 14a: teacher-generated synthetic data for small domain specialists

Sources checked 2026-11-25, for sub-study S1 (`../../design/substudy_s1_distill_prune.md`,
`../../design/s1_reasoning_exam.md`). 23 rows in `14a_synthetic_data_small_specialists.csv`: 5 deep
notes and 18 triaged rows. That is above the 12-18 target because each of the twelve seed papers
was checked rather than cited from memory. Deep notes:
`../papers/harsha-2025-synthetic-financial-qa.md`,
`../papers/yang-2024-synthetic-continued-pretraining.md`,
`../papers/cheng-2024-instruction-pretraining.md`,
`../papers/liu-2023-tinygsm.md`,
`../papers/guha-2025-openthoughts-data-recipes.md`.
Already covered elsewhere and cited, not repeated: `li-2025-small-models-learnability-gap`,
`liu-2025-fin-r1-financial-reasoning-rl`, `qian-2025-fino1-reasoning-transfer-finance`,
`xie-2025-finchain` (stream 13a); `phogat-2024-finetuning-small-models-financial-qa` (stream 05);
Yue et al. 2025 and Hayrapetyan et al. 2026 (13a triaged rows). Stream 14b (distillation methods
for small students) was written in parallel and has its own notes on the Qwen3 report and on
on-policy distillation; this stream's triaged rows on the same papers should be reconciled with
them at merge (14b's notes were not read for this synthesis). Not merged into `../matrix.csv`.

The question (owner, after EXP-0050): can a larger model's financial reasoning, meaning reading a
disclosure and forming a coherent analytical framework (体系), be distilled so that it shows up in
a small model that is better than its size in one domain, in particular by having a larger model
generate a lot of data for the small model to learn from? What S1 has so far, as reported to this
review: SFT on a few thousand 4B answers brought the 0.8B level with the 4B on lookups and
calculations but taught one answer template ("Row; Column; Calculation; \boxed{number}"); on
section R's label items the distilled 0.8B boxes a number on 300/300 items and scores about 0,
against 56 for the untrained 0.8B and 82 for the 4B; FinQA fell after training. Constraints: one
Apple-silicon MLX machine, 12 GiB, until 2026-12-15; local teachers Qwen3.5-4B, Qwen3.5-9B (4-bit),
gpt-oss-20b (11.3 GiB); student 0.8B, maybe 2B.

## What the stream establishes

**1. Volume buys depth in one task family, with early diminishing returns; it does not buy breadth**

- **Empirical finding.** With enough generated data a sub-1B model gets good at one narrow,
  checkable task: TinyGSM's 12.3M GPT-3.5 problems take Phi-style students to 63.1 (125M), 65.9
  (350M) and 68.2 (1.3B) on GSM8K, and 81.5 with a 1.3B verifier, above the 77.4 of the teacher
  (`liu-2023`). Going from a third to two thirds of the data gave a "10% increase", the last third
  "only marginal gain".
- **Empirical finding.** On one financial task family the curve flattens at thousands, not
  millions: Phi-3-mini on synthetic FinQA 63.99 / 64.95 / 68.61 / 68.43 at 750 / 1,500 / 3,000 /
  6,251 examples (`harsha-2025`); a 1,500-example FinQA subset came within 3-8 points of full data
  (`phogat-2024`); FlanT5-3B's math plateaued at about 90K of 130K teacher solutions (Fu et al.
  2023).
- **Empirical finding.** Broad recipes keep gaining at 10^5-10^6 examples, mostly at 7B and with
  32B-and-larger teachers (OpenThoughts to 1.2M, `guha-2025`); DeepSeek-R1's 800K distillation set
  also trained a 1.5B, from a math-specialised base (AIME24 28.9).
- **Empirical finding.** Small curated sets work only when the base already knows the domain: LIMO's
  800 problems give AIME24 63.3 on Qwen2.5-32B and 2.5 on Qwen2.5-3B, and 9.2 on Qwen1.5-32B; s1K
  gets most of the full 59K pool's gain at 32B (50.0 against 53.3, about 7 against 394 H100-hours).
  No paper read shows the small-set effect below 3B.
- **Hypothesis (synthesis).** For a 0.8B, neither "a few hundred perfect examples" nor "millions of
  one kind" is supported. Volume along one task family saturates early; what is left to buy is
  more kinds of task.

**2. Diversity of task and answer type decides transfer to unseen tasks**

- **Empirical finding (controlled).** With about 10^6 examples, models trained on fewer than about
  300 distinct instructions do not generalise to unseen ones; from about 1,000 they always do,
  even with few examples each. Models trained on few instructions fall back on a default output
  (the no-op). Training on one semantic class of rules does not generalise; a mix does (Zhang,
  Wang and Charton 2024; string rewriting, small GPT-2 and Llama-2-7B).
- **Empirical finding (finance).** GPT-4o's synthetic FinQA questions were under 5% Boolean or
  text-only, and the small students trained on them were weakest on exactly those test questions
  (`harsha-2025`). The generator's choice of what to ask became the student's blind spot.
- **Empirical finding (format).** Specialising FlanT5 on math chain of thought drove BigBench Hard
  CoT accuracy to 0 at the first checkpoint; zero-shot-format training data removed in-context
  ability while in-context-format data kept both (Fu et al. 2023, ICML). Orca 2 trains 7B-13B
  students on several answer strategies chosen per task, with the strategy prompt erased from the
  student's input, and reports parity with 70B chat models on reasoning benchmarks.
- **Empirical finding (counterweight).** "Diversity" as more data *sources* did not help at 7B:
  the top 2 code sources beat the top 16 (41.3 against 36.4, `guha-2025`); s1's diversity-only 1K
  selection was its worst on AIME24 (26.7). Neither varied task or answer type.
- **Empirical finding (synthetic generalises better than real).** Phi-3-mini trained on synthetic
  FinQA scored 84.26 on TATQA against 81.19 from real FinQA, and the reverse transfer also favoured
  synthetic (67.82 against 63.81); the authors attribute it to broader question variety
  (`harsha-2025`).
- **Hypothesis (for S1).** The 0.8B's boxed number on 300/300 label items is the default-output
  failure described by Zhang et al.: one instruction type and one answer type in training. The
  literature predicts that more examples of the same template will not fix it and that many task
  and answer types will.

**3. Document-grounded synthesis puts domain knowledge into the weights; raw text does not**

- **Empirical finding (mechanism).** Knowledge seen in one phrasing is memorised but not
  extractable (0% extraction without augmentation, Allen-Zhu and Li 2024).
- **Empirical finding.** EntiGraph turns 1.3M tokens of articles into 455M tokens of text about
  relations among their entities; continued pretraining lifts Llama 3 8B closed-book QA from 39.49
  to 56.22 (GPT-4 51.30), log-linear in synthetic tokens with no plateau reached; raw-text training
  fell below the base (`yang-2024`).
- **Empirical finding (finance).** Turning financial news into tasks about each text: by rules,
  LLaMA-7B 58.6 to 63.4 (raw text 57.6; BloombergGPT-50B 62.5; AdaptLLM, Cheng et al. ICLR 2024);
  by a fine-tuned 7B task writer, Llama3-8B 70.1 to 74.7 (raw text 72.0; Llama3-70B 71.9), with
  model-written tasks 1.6 points above rule-mined ones and 26-30% of finance pairs wrong
  (`cheng-2024`). Llama-Fin (8B) beats its base on 13 of 17 novel finance tasks; raw-text continued
  pretraining alone took MT-Bench to about 1, joint training kept 7.36 (Ke et al. 2025).
- **Limit.** All of this is knowledge of a corpus and short-answer tasks at 7-8B. No paper shows
  that document-grounded synthesis teaches judgement items, or works by continued training of a
  released sub-1B model (`cheng-2024`'s 500M and 1.3B results are from scratch, on general tasks).

**4. Teacher: close and compatible beats strongest; logits beat text where available**

- **Empirical finding.** Below about 1.5B, students learn better from a small teacher and short
  traces (`li-2025`). Across five 1.5B-4B students and 20 teachers, a larger teacher was not
  reliably better (Gemma-2-9b-it 14.90 against 27b-it 13.17 for a 4B student), same-family
  teachers helped, and GPT-4 was the worst teacher for that 4B student (5.72); compatibility with the student predicted
  usefulness (Xu et al. 2025, NAACL). At 7B, QwQ-32B beat DeepSeek-R1 as a teacher (`guha-2025`).
  Teacher-student accuracy correlations were 0.25-0.64 for 1B-3B students (Chen et al. 2025).
- **Empirical finding (pre-training-style distillation).** A stronger teacher eventually gives a
  worse student (Busbridge et al. 2025, ICML); the optimal teacher was about 2.5 times the student
  (Zhang et al. 2025, ACL, fit on students below 3B).
- **Empirical finding (on-policy).** Training the student on its own samples, scored by the
  teacher's token distributions, gave 1.7-2.1 times the gain of standard distillation for T5
  students of 77M-800M (GKD, Agarwal et al. ICLR 2024). Qwen3 built its 0.6B-14B models this way;
  on Qwen3-8B, on-policy distillation reached AIME24 74.4 against 67.6 for RL from the same
  checkpoint, at 1,800 against 17,920 GPU-hours (Qwen3 report, Table 21).
- **Empirical finding (generalist teacher, finance).** R1-distilled Qwen-7B scores 58.0 against
  65.6 for the plain instruct model on Fin-R1's finance suite (`liu-2025`), while R1 distillation
  is strong in math (R1-Distill-Qwen-1.5B AIME24 28.9, from a math-specialised base).
- **Hypothesis (for S1).** Qwen3.5-4B is 5 times the 0.8B, same family and tokenizer: the
  literature's default. The 9B (about 11 times) is worth one arm; gpt-oss-20b (25 times, another
  family and tokenizer) is a poor trace teacher for a 0.8B by every result above, and is better
  used to write and check questions.

**5. Trace form: short, several per question, rationale as a second target**

- **Empirical finding.** Short chain of thought beats long up to 3B (`li-2025`); weak students peak
  at intermediate granularity and padding length does not help (Chen et al. 2025); long traces help
  at 7B (cutting traces over 2,048 tokens cost 33.3%, `guha-2025`).
- **Empirical finding.** Several teacher answers per question are a cheap multiplier: a 0.3B student
  went from 6.11 to 23.89 on MultiArith with diverse rationales (Ho et al. 2023); 16 answers per
  question matched more unique questions (`guha-2025`); Fu et al. used 40 per question.
- **Empirical finding.** Rationales as an auxiliary training target let a 220M T5 beat standard
  fine-tuning with 12.5% of e-SNLI, and a 770M T5 beat 540B PaLM few-shot on ANLI (Hsieh et al.
  2023); the answer format at inference can stay short.
- **Empirical finding (answer verification).** At 7B on math, no answer filter beat keeping all
  answers (`guha-2025`); TinyGSM did not check answers and the student still passed the teacher.
  Neither tested label or judgement items.

**6. Specialisation costs generality unless general data is mixed in**

- **Empirical finding.** Fu et al. (BBH CoT to 0), AdaptLLM (raw domain text lowers prompted
  ability), Ke et al. (MT-Bench about 1 after raw continued pretraining), Hayrapetyan et al. 2026
  (plain finance SFT -3.2 to -4.0, 13a). Mixing general instructions or training jointly limits the
  loss (AdaptLLM, `cheng-2024`, Ke et al.).
- **Consequence (hypothesis).** S1's FinQA drop is the expected price of single-format
  specialisation, and a design aimed at "better than its size in one domain" should state how much
  general loss it accepts and measure it.

**7. Finance evidence for small students is thin**

- **Verified by search, not refuted.** The smallest finance student trained on teacher-generated data
  found is 3.8B (Phi-3-mini, `harsha-2025`, `phogat-2024`). Everything else is 7-8B (Fin-R1, Fin-o1,
  Llama-Fin, AdaptLLM, Instruction Pre-Training). Huang and Simpson (LREC 2026) distil GPT-4o into
  compact encoder classifiers for sentiment, not generative reasoning (abstract only).
- **Open question.** No paper measures a "coherent analytical framework" in a student. The nearest
  measurable proxies are transfer to unseen task families and consistency of answers about the same
  document; neither has been reported for synthetic-data students.

## Look-ahead and memorisation across the stream

Document-grounded synthesis memorises the source corpus on purpose (`yang-2024`). For S1 that makes
the split decisive: generate only from releases in the training window, and test on later releases
and on firms not used for generation; otherwise the student can recall the test release's numbers.
TinyGSM and OpenThoughts decontaminate benchmarks by n-gram and similarity checks; `harsha-2025`
does not say whether test-split pages fed generation; `cheng-2024` and AdaptLLM do not date their
finance news against the evaluation sets.

## Consequences for S1 (all hypotheses)

1. **Generate from the releases, many task types per release.** For each training-window EX-99.1
   release, have the teacher write many short tasks of different kinds, in the manner of
   `cheng-2024` and AdaptLLM: lookups and computations (as now), direction and driver labels,
   which-segment and which-period choices, true/false claims about the release, "cannot be
   determined from this release", short explanations of a change, relation text between line items
   in the manner of EntiGraph (revenue against operating income, EPS against net income and share
   count). Fix a quota per answer type before generation and audit the result (`harsha-2025`).
2. **Many instruction types, few examples each, and hold whole families out.** The controlled study
   puts the threshold in the hundreds of distinct instructions; its number does not transfer, its
   direction does. Paraphrase every instruction; vary the answer format (label, sentence, number,
   option letter); never one box template. Train on some section R families and test on others
   (13a point 5).
3. **Volume: tens of thousands, not millions, and grow it by sampling.** Single-family gains in
   finance flatten at about 3K (3.8B); the broad recipes that keep scaling sit at 7B and use API or
   32B+ teachers. A target of roughly 20K-100K examples from a few thousand releases, with 4-8
   teacher answers per task, is within reach of a local teacher; measure accuracy at three sizes
   rather than assume a curve. Local generation throughput has not been measured and should be,
   before any size is pre-registered.
4. **Short traces.** A sentence or two of rationale, then the answer in the asked format; test
   rationale-as-auxiliary (Hsieh) against rationale-in-output. Long thinking traces only in a 2B
   arm, if any.
5. **Teacher.** Qwen3.5-4B as the trace teacher; Qwen3.5-9B as one comparison arm on a small pilot
   (the literature says test, do not assume); gpt-oss-20b only to write questions and check
   answers. Filter by rule gold where it exists (S1 has it), and run keep-all against filtered on
   label items once, since no paper covers it.
6. **Add an on-policy step.** After SFT, sample the 0.8B's own answers on training tasks and train
   it toward the 4B's token distributions on those samples (GKD; Qwen3). Same tokenizer family makes
   this possible; whether a 0.8B trainer and a 4-bit 4B scorer fit together in 12 GiB is an
   engineering check, not a literature question.
7. **Keep general data in the mix** and report the general-ability price (FinQA, one general
   benchmark) next to the domain gain.
8. **Measure the claim the owner cares about.** Beyond accuracy: transfer to held-out R families
   and to new answer formats, and consistency across questions on the same release. No published
   design does this; S1 would be first.

## Reusable

- `harsha-2025`'s generation prompts (appendix C) and execution filter; its nearest-neighbour audit.
- The Instruction Pre-Training synthesizer and data (LMOps repository, per the abstract) as a
  comparison task writer, subject to licence and size checks.
- EntiGraph's two-step prompt (entities, then relations among pairs and triples) and its released
  data and code (arXiv comments).
- TinyGSM's verifier recipe, if S1 adds best-of-n with a scorer.
- Xu et al.'s compatibility-adjusted reward (CAR) to rank candidate teachers on a pilot.

## Gaps that suggest an experiment

- No study of teacher-generated data for a student below 1B on a document-reading task with label
  answers, in any domain.
- No test of whether task- and answer-type diversity in synthetic data undoes single-template lock-in
  in a small student. S1 has the failure, the items and the rule labels to test it directly.
- No finance synthetic-data study below 3.8B, none on judgement items, none measuring transfer to
  unseen task families or within-document consistency.
- Effect of the teacher's wrong labels (4B at 82 on R) on a student trained on label items is
  unknown.

## Limits

- Most evidence is mathematics and code with verifiable answers; finance evidence is numeric QA and
  sentiment at 3.8B and above.
- Teachers in the literature (GPT-3.5/4/4o, gpt-4-turbo, 32B and larger reasoning models) are far
  stronger relative to their students' tasks than a local 4B-20B is to section R; findings on
  unchecked answers may not carry over.
- Seven of the 23 rows are preprints without a venue (TinyGSM, OpenThoughts, Zhang et al., Allen-Zhu
  and Li, Orca 2, phi-1, s1) plus the Qwen3 report.
- Full texts were read through an automated reader or local text extraction; several tables came out
  scrambled (Instruction Pre-Training Table 5; `harsha-2025` Tables 1-6, matched to the text's own
  statements). Values not re-keyed from PDFs.

## Opened but not entered

Chu et al. 2025 (arXiv 2501.17161v2, "SFT memorizes, RL generalizes"; abstract only, belongs with
13a's RL rows) and Huang and Simpson 2026 (LREC 2026, arXiv 2606.18875; abstract only, encoder
students). Not triaged: MetaMath, Evol-Instruct and WizardMath, WRAP (Maini et al. 2024),
TinyStories, SmolLM2, Phi-3 and Phi-4 reports, AgentInstruct, MiniLLM, Self-Instruct, the FLAN
Collection. Nothing is claimed from them.
