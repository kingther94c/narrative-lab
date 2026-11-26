# TinyGSM: achieving >80% on GSM8k with small language models

- **Citation:** Liu, B., Bubeck, S., Eldan, R., Kulkarni, J., Li, Y., Nguyen, A., Ward, R., Zhang, Y.
  (2023). arXiv 2312.09241, preprint (no venue listed). Version read: v1 (14 December 2023), the
  only version; HTML.
- **Link:** https://arxiv.org/abs/2312.09241 (HTML: https://arxiv.org/html/2312.09241v1)
- **Stream:** 14a (comparable domain: grade-school mathematics)
- **Verified against source:** yes, 2026-11-25, against the arXiv abstract page and the v1 HTML
  through an automated page reader.

## Question

Can models of 125M-1.3B parameters pass 80% on GSM8K, which before needed about 34B parameters, if
trained on a very large teacher-generated data set?

## Data

- TinyGSM: 12.3M grade-school problems with Python solutions (about 1.8B tokens), all written by
  GPT-3.5-turbo, cost about $3,600. Seeds: the 7,473 GSM8K training questions; the teacher writes
  variants; about one third are variants with irrelevant information added (GSM-IC style).
- Filter: drop problems that are too short or have no numbers and code that does not run. Answer
  correctness is *not* checked; the authors rejected majority-vote filtering because it keeps only
  easy problems.
- Contamination check: 22 of 11.0M unique questions share a 13-gram with the GSM8K test set; about
  38K (0.35%) share an 8-gram. The authors note that n-gram checks miss paraphrases.

## Method

- Students: Phi-1.5-family models of 125M, 350M and 1.3B (pre-trained on Phi-1.5's data), fully
  fine-tuned on TinyGSM.
- Verifier: a second model of the same family, initialised from a generator, trained to score each
  token of a solution as leading to a correct answer or not, on 48 generations per GSM8K training
  question from several generator checkpoints. At test time 48 candidates are sampled and the
  top-scoring one is submitted. The verifier is the only use of real GSM8K training data.

## Outcome variable and horizon

GSM8K test accuracy; SVAMP (1,000 problems) as a check out of distribution. No horizon.

## Result

- **Empirical finding, generator alone:** 125M 63.1, 350M 65.9, 1.3B 68.2 (from Phi-1.5-style
  pre-training); 53.1 / 55.5 / 57.3 from random initialisation.
- **Empirical finding, with verifier:** 1.3B generator + 1.3B verifier 81.5, above the GPT-3.5
  teacher (77.4, measured by the authors). 125M generator + 1.3B verifier 76.1 beats 1.3B generator
  + 125M verifier 71.7: scaling the verifier pays more than scaling the generator.
- **Empirical finding, data volume:** going from about one third to two thirds of TinyGSM gave a
  "10% increase in performance" (the paper does not say whether points or relative); the final
  third gave "only marginal gain".
- **Empirical finding, transfer:** SVAMP 75.6 for the 1.3B without further tuning.
- Stated limits: some generated problems break common sense; code-only solutions struggle with
  equations; verifier scores look pattern-driven on some samples; paraphrase contamination is
  unsolved.

## Look-ahead and memorisation

Contamination addressed by n-gram matching only (above). No temporal dimension.

## What it settles for us

- **The clearest evidence that "a teacher generates a lot of data" can make a sub-1B model good at
  one narrow, verifiable task family**: 125M at 63% and 1.3B at 68% on GSM8K from 12.3M generated
  problems. For scale, Fu et al. (2023, ICML; stream 14a CSV) report 15.2-23.8 on GSM8K validation
  for FlanT5 250M-3B specialised on 130K teacher solutions (different models, split and data).
  Gains flatten somewhere between about 8M and 12M examples for this task (two thirds and the
  full set).
- It does not show breadth. Every problem is a variant of one task family seeded from one data set;
  the out-of-distribution check (SVAMP) is the same kind of problem. Nothing here speaks to S1's
  problem of carrying a skill across *answer types* (number against label), and the volume used is
  three orders of magnitude above S1's current few thousand examples.
- The verifier result transfers as a design idea: in S1, where labels can be computed by rule from
  the release, a scorer or a rule check over several sampled answers may raise a 0.8B more cheaply
  than a larger generator (hypothesis for S1). It needs the gold rule, which EarningsExam has.
- Unchecked answers did not stop the student exceeding the teacher; at this volume label noise
  appears tolerable for computation problems (empirical finding, not tested for judgement items).
- Cost comparison for us: 1.8B tokens via an API teacher. A local 4B-9B teacher on one Apple-silicon
  machine is far slower; volumes of this order are out of reach before 2026-12-15, so S1 must rely on
  diversity and multiple samples per item rather than raw volume (hypothesis, to be costed).

## Limits

One task family; the students' pre-training data (Phi-1.5 synthetic textbooks) is itself
GPT-generated and close in style to the fine-tuning data; no intervals; preprint.
