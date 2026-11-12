# Method graveyard

Rejected approaches and why. An entry is added only after a REJECT verdict in
`experiment_registry.md`.

## Entry format

```
### GY-NNNN — <method name> (date)
- **Claim it made:**
- **How tested:** experiment id, data, the baseline it lost to.
- **Why rejected:** the specific failure, with numbers.
- **Scope of the rejection:** where it fails. If it may survive on a narrow slice, say so.
- **Do not resurrect unless:** the condition that would change the verdict.
```

## Entries

None from this repo yet.

One approach was ruled out before the programme started, on evidence from the sibling project
ResearchOS. It is recorded here so it is not tried again without a reason:

### GY-0000 — Masking the company to remove look-ahead (carried in, 2026-11-12)
- **Claim it made:** redacting or abstracting identifying details lets a model be evaluated on
  documents from inside its training window.
- **How tested:** not in this repo. ResearchOS run notes
  (`../Foundry/ResearchOS/runs/2026-10-first-real-run/README.md`,
  `../Foundry/ResearchOS/runs/2026-10-smallbank-run/`) and the published work listed in
  `01_roadmap.md`.
- **Why rejected:** "Every one of the 15 masks ended identifiable" after four masker rounds, and
  abstraction left eight of eight identifiable (first real run). Only a few small banks could be
  hidden (`masking_results.json` in the small-bank run). Published work reports the same for a
  fully masked earnings call transcript.
- **Scope of the rejection:** as a guarantee. Masking remains usable as a sensitivity analysis.
- **Do not resurrect unless:** a masking method is shown to defeat a fresh guesser on large caps
  without removing the information the task needs.
