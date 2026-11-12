# Feature evidence

Per narrative feature: why it should matter, what the evidence is, and how far it reaches.

## Entry format

```
### <feature>
- **Mechanism:** why it should carry information.
- **Evidence:** experiment id and finding, or "professional convention, untested".
- **Functional form:** level / change / direction / discontinuity.
- **Estimate and scope:** value and the slice it applies to, or "unresolved".
- **Confidence:** high / medium / low.
- **Interactions:** features it depends on or co-moves with.
```

## Entries

Nothing has been tested in this repo yet. The entries below carry in what the sibling project
ResearchOS observed. They are weak priors: small samples (15 to 21 cases), a different task
(predicting the first-session stock reaction), and one model.

### Guidance
- **Mechanism:** a change in what management commits to for coming periods is information about
  expected fundamentals that the current period's numbers do not contain.
- **Evidence:** ResearchOS first real run, 15 large caps: "expectations_gap and guidance ended on
  top" of seven perspectives. Small-bank run, 21 cases: "Guidance was the best single perspective
  (0.227 ...)". Neither run could show an effect at its sample size: the trained-versus-untrained
  Brier intervals were -0.008 [-0.021, +0.006] and -0.004 [-0.023, +0.011]. Sources:
  `../Foundry/ResearchOS/runs/2026-10-first-real-run/README.md`,
  `../Foundry/ResearchOS/runs/2026-10-smallbank-run/README.md`.
- **Functional form:** unresolved.
- **Estimate and scope:** unresolved.
- **Confidence:** low.
- **Interactions:** co-moves with expectations gap, tone and risks when all are read from the same
  outlook passages (see the last entry).

### Management tone
- **Mechanism:** hypothesis: a shift in tone leads the disclosed numbers.
- **Evidence:** ResearchOS first real run: "management tone added least". Untested here. No ground
  truth a single annotator can supply has been shown to exist for it; the labelling pilot (WP4)
  tests that.
- **Functional form:** unresolved.
- **Estimate and scope:** unresolved.
- **Confidence:** low.
- **Interactions:** see the last entry.

### Reading features together inflates their agreement
- **Mechanism:** when one model reads the whole document through several lenses in one pass, each
  lens is coloured by the same overall impression.
- **Evidence:** ResearchOS perspectives run, 21 cases: mean pairwise correlation of the seven
  perspectives 0.855 read together, 0.387 read in isolation. Source:
  `../Foundry/ResearchOS/runs/2026-10-perspectives-run/README.md`.
- **Consequence for this repo:** each feature is extracted on its own, with its own evidence
  quote.
- **Confidence:** medium for the direction, low for the size.
