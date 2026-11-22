# Unique in the Crowd: The Privacy Bounds of Human Mobility

- **Citation:** Yves-Alexandre de Montjoye, César A. Hidalgo, Michel Verleysen and Vincent D.
  Blondel (2013). Scientific Reports 3, 1376. doi:10.1038/srep01376. Version read: the PubMed
  Central copy (PMC3607247).
- **Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3607247/ (publisher page
  https://www.nature.com/articles/srep01376 redirected to a login and was not opened)
- **Stream:** 09, rewrite blinding (question 4: how much coarsening is needed?)
- **Verified against source:** yes, 2026-11-22 (abstract, Results including "Scaling
  properties", Discussion and Methods, through a machine extraction; the quoted sentences were
  checked verbatim in a second read; the supplementary Table S1 was not opened)

## Question
How many points of a person's location trace are enough to single them out, and how much does
lowering the spatial or temporal resolution help?

## Data
Mobile-phone records of about 1.5 million users over 15 months (April 2006 to June 2007), about
6,500 antennas, an average of 114 interactions per user per month.

## Method
Unicity: the share of traces uniquely matched by p points drawn at random from them. Resolution
is coarsened by clustering antennas (v antennas per cell) and widening time bins (h hours), and
unicity is fitted as a function of both.

## Outcome variable and horizon
Unicity (share of users uniquely identified). No horizon.

## Result
Empirical findings.

- Four random points identify more than 95% of users at full resolution; two points more than
  50%.
- Unicity follows one formula, ε = α − (νh)^β, with an exponent that falls with the number of
  points: "β = 0.157 − 0.007p".
- "Given four points (p = 4), we find that ε > .5 when using a resolution of h = 5 hours and
  v = 5 antennas."
- "given four points, a two-fold decrease in spatial or temporal resolution makes it 9.3% less
  likely to identify an individual", "while given ten points, the same two-fold decrease results
  in a reduction of only 6.2%".
- Conclusion (abstract): "Hence, even coarse datasets provide little anonymity."
- The authors note that drawing points at random may underestimate unicity.

## Look-ahead and memorisation
Not applicable.

## What it settles for us
- **Coarsening has weak returns when many fields remain.** Each halving of resolution buys
  little, and less the more points are known. Rounding every growth rate to whole percent (as in
  EXP-0031) is a mild coarsening applied to many fields at once, so it should not be expected to
  hide a company whose record has a dozen numeric fields; removing fields buys more than
  coarsening them (our reading, transferring from mobility traces to a record of firm figures).
- **What a brief reveals should be counted in fields, not only in precision.** The number of
  fields known (p) matters more than the resolution of each (our reading).

## Limits
- Location traces of people, not company figures; the population is far larger (1.5 million
  against about 500 companies), which makes our problem worse, not better (our reading).
- Points drawn at random; an attacker that picks the most distinctive points does better.
- Results rest on one operator's data; Sánchez, Martínez and Domingo-Ferrer argue in a comment on
  the 2015 credit-card study that proper anonymisation methods change the picture (triaged in
  `../streams/09_rewrite_blinding.csv`).
