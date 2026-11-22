# Estimating the Success of Re-identifications in Incomplete Datasets Using Generative Models

- **Citation:** Luc Rocher, Julien M. Hendrickx and Yves-Alexandre de Montjoye (2019). Nature
  Communications 10, 3069. doi:10.1038/s41467-019-10933-3. Version read: the PubMed Central copy
  (PMC6650473).
- **Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6650473/
- **Stream:** 09, rewrite blinding (question 4)
- **Verified against source:** yes, 2026-11-22 (abstract, Results, Discussion and the Methods
  formulas, through a machine extraction; figures read by caption and text only)

## Question
Does releasing only a sample of a dataset, or only some attributes, protect people from being
re-identified, and can the chance that a given match is correct be estimated for each record?

## Data
Several census and survey corpora, including US census data (Massachusetts) and others; samples
from 0.1% to the full population.

## Method
A latent Gaussian copula fitted to the released sample (marginals chosen by BIC; correlations
from mutual information) estimates the population distribution of attribute combinations. For a
record x with population probability p(x) and population size n:

- probability that x is unique in the population, ξx = 1 − p(x)^(n−1);
- probability that a match on x is correct, κx = (1/(n·p(x)))·(1 − (1 − p(x))^n).

## Outcome variable and horizon
Accuracy of estimated population uniqueness (mean absolute error, AUC); share of people unique
given k attributes. No horizon.

## Result
Empirical findings.

- Uniqueness is estimated well from small samples: on US data at a 1% sample, MAE 0.029 ± 0.015;
  across corpora at 1%, 0.041 ± 0.053; mean AUC 0.89 for US populations trained on 1% samples
  (Figure 1b, Figure 2a). Error rises at 0.1%.
- "15 demographic attributes would render 99.98% of people in Massachusetts unique" (Results);
  the abstract generalises this to Americans.
- Uniqueness rises quickly with the number of attributes (Figure 3b).
- Worked example: ZIP code, date of birth and gender give ξ = 0.58 and κ = 0.77 for one person;
  adding the number of children raises the probability of a correct match to about 99.8%.
- The Discussion rejects the claim that sampling or releasing partial data gives plausible
  deniability.

## Look-ahead and memorisation
Not applicable.

## What it settles for us
- **A closed-form risk per brief.** With the S&P 500 as the population (n about 500 per quarter)
  and the joint distribution of the template's fields across those companies, κ gives the chance
  that the best-matching company is the right one, without asking a model. It is a floor on what
  a perfect attacker who knows every company's figures could do, and a check on whether the LLM
  attacker's hit rate is explained by the fields alone (our reading).
- **Few fields can suffice when the population is small.** With about 500 companies, a handful
  of banded fields can leave most companies unique (our inference from the formula; to be
  computed, not assumed).
- Used by `krco-2026-rat-bench` as its risk model.

## Limits
- Demographic attributes of people; company figures are continuous, correlated and skewed, and
  the copula fit for them is untested.
- The model assumes the attacker knows the population distribution; an LLM knows it only
  partly, for large companies better than small ones.
