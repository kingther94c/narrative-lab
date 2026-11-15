# narrative-lab

Research on **financial narrative intelligence**: whether LLMs can extract investment-relevant
information from company disclosures, and how prompting, retrieval, fine-tuning and tools compare
as ways of adapting a model to that job, on small open-weight models and on commercial ones.

Equity failure detection (fundamentals deteriorating under an optimistic narrative) is the
application the work is tested on. It is not a hypothesis the project needs to come out true: a
rigorous comparison of the adaptation methods is a result even if the narrative signals carry no
alpha.

## Status

**Phase 0: literature review and research design**, started 2026-11-12. No benchmark exists yet
and no model has been trained. A sub-study on compressing small models for an earnings exam
(S1) is being set up.

The repository runs a series of studies. Each finished study is reported under
[`reports/`](reports/README.md), with instructions to reproduce it.

Start at [`research/registry/01_roadmap.md`](research/registry/01_roadmap.md).

## Layout

| Path | What it holds |
|---|---|
| `docs/proposal/` | The owner's proposal, one file per version, never edited in place |
| `docs/plans/` | Plans as the owner approved them, kept verbatim |
| `research/registry/` | Roadmap, methodology, experiment registry, graveyard, feature evidence, changelog |
| `research/literature/` | Paper notes, evidence matrix, gap analysis |
| `research/design/` | Data audit, feasibility measurements, labelling codebook, research design |
| `research/ledger/` | Hash manifests of sealed forecasts |
| `research/experiments/` | Numbered experiment scripts, frozen once run |
| `reports/` | One folder per finished study: findings and how to reproduce them |

Data, model checkpoints, run outputs, licensed text and gold test labels live outside the repo.
[`AGENTS.md`](AGENTS.md) has the house rules.
