# Sub-study S2: replaying history without look-ahead

**Status: APPROVED v2, frozen 2026-11-20 (the owner: "同意").** The approved text is kept
verbatim in `docs/plans/2026-11-20_substudy_s2_plan.md`. From here on, changes go through
`research/registry/changelog.md`. The experiments below get `PRE-REGISTRATION` entries in
`research/registry/experiment_registry.md` before any outcome data is touched. The owner
approved the direction and three rule changes on 2026-11-19. v1 was written before the
literature pass. v2 takes in the pass (`research/literature/streams/08_blind_replay.md`) and the
first feasibility run (EXP-0020), and changes how leakage is measured (§5, §9) and which
strategies stand (§4). At the freeze no hypothesis was pre-registered, no data had been pulled,
no model had been called, and decisions 4 to 6 (§15) were open.

The owner's requests (2026-11-18, verbatim):

> 一个新的课题呀，这个新的课题呢，我想要研究怎么样去设计好一个，就是就是如果我必须要用一个我没有办法控制的，呃，AI model，比如说是一个 frontier 的 commercial model 啊，嗯，但是我想去做一些 experience replay，就比如说我有一个 PM agent，我要让他看过去一段时间的这些 news 啊，还有这些呃各种各样的 information 去 make 一个 call。但现在的问题是，如果直接把这些东西给他的话，因为有可能这个 model 已经见过那之前的 data 了，它是这是它 training data 一部分，所以它非常容易预测出来之后的走向。嗯，这有一些这有 look look ahead bias 在里面，我想要避免这样的情况，所以呢，我现在想的是要多加几个 sub agent，这个 sub agent 有一个有一个 sub agent 可能是用来 sourcing 这些啊。啊，historically 在这个时间点上 available 的这些 data，啊和 available 这些 information 这些 text，然后对它进行一一第一层的 filter，在 filter 完了之后呢，嗯，再去加一些 noise。啊，我看到有一个 paper 讲，比如说，呃，英伟达的 earning 是一点二三，当你加一点点 noise 在小数点后面变一点的时候，呃，其实 AI 可能就比较难以辨认出来这是它的 training data。所以它就可以从这个角度去加一些 noise，然后加完 noise 之后，再有一个再先给一个 sub agent，这个这个新的 sub agent 就当做自己是这个 PM agent 啊、呃，然后拿这个去就你给他的 context 就是他要把自己当做一个 PM agent 去做，然后你就把这些呃把这些数据给他，然后让他去 make 一个 call，但同时也要去问他他能不能猜出来我们给我们这些加了 noise 去掉一些关键信息。啊、呃，匿名的这些，比如说呃，英伟达，我把它变成一个公司 A，然后这样的一个东西，它嗯，还有还有一些去掉一些 context，它它能不能够很好的 strike 一个 balance between，它不能够辨别出来这是具体哪个公司，但它又能够有足够的 context，足够的 information，嗯、呃，去 make 一个 reasonable 的 call，呃，对，然后这就涉及到它要把这个它的这些。呃呃，理解啊，还有它的 call 要给到第三个这种辨识的 agent，这个一个 detector 去看它有没有啊、呃、发现这个公司就是英伟达，它有没有？但它哦另一个方面，它也要去看啊、呃、它的这个呃 context 是不是足够的完整去 make 一个 decision。呃，如果没有什么问题了，我们再把这个 input 给一个真正的 agent 去 make a call，这样去做一个 experience replay 的这样一个 framework。啊，所以，嗯，我们就是要看这个过程中，要从，嗯，呃，怎么样去做好这个 prompt engineering，怎么去做这些，呃，trade off 取舍，去能够达到一个比较好的一个效果。

> 要发散性思维，核心目标是让过去的数据有更大的利用率来帮助学习和迭代但不是直接lookahead。也可以考虑可以给出多种不同的noise注入后的信息，分别给agent判断，然后看核心思路等等

The owner's choices on 2026-11-18 and 2026-11-19, in the owner's words where they went beyond
the option offered:

- The call: "优先做下一季基本面方向，之后再拓展到财报后股价反应".
- The model: "按你推荐的Claude subagent，但是用什么model可以先小样本测试一下sonnet是否足够，不行就都opus".
- What lets an episode through: the model cannot use the future, with identifiability as a
  supporting measure; "同时也看看文献有没有更好的思路".
- The paper on numeric noise: Levy (2026), which the owner had merged in memory with Lopez-Lira,
  Tang and Zhu (2025).

## 1. Question and why it belongs here

The north star asks where capability for a specialised task should live. One answer the main
design does not cover is **experience**: a playbook an agent builds by working through past
cases. A commercial model cannot be retrained, so experience is the one thing its user can add.
But the model has read about the past. Shown a 2022 earnings release, it may recall what happened
next, be right for that reason, and learn nothing true from the episode.

Clean experience is scarce. Only the releases of one season after the roster's cutoff
(2026-06-30) have a next-quarter label today: 995 episodes on the training and development side,
against 29,606 from 2019 to the cutoff (§10). The older thirty-fold is useless as it stands.

**The question: how can pre-cutoff history be made usable for a commercial-model agent's
learning, without the model using what it remembers of the outcomes, and at what cost in
information?**

The owner's first design is a pipeline: source the point-in-time documents, filter and anonymise
them, add noise to the numbers, let a probe agent make the call and say whether it recognises the
company, let a detector judge both leakage and sufficiency, and only then pass the input to the
real agent. S2 keeps that pipeline, treats it as one strategy among several (§4), and measures
all of them the same way.

## 2. What is already known

| Finding | Kind | Source |
|---|---|---|
| A masker and guesser loop with renaming, one scaling factor and a year shift left all 15 large caps identifiable; after rewriting each document as a generic brief, a fresh guesser still named 8 of 8 at 0.80 to 0.93 confidence. Three small regional banks were hidden. "What gives a megacap away is not a name but its structure" | Empirical finding, ResearchOS, one model, 15 to 21 cases | `../Foundry/ResearchOS/runs/2026-10-first-real-run/README.md`, `2026-10-smallbank-run/README.md`; GY-0000 |
| That loop scaled levels by one factor and left every ratio exact | Verified in the code | `../Foundry/ResearchOS/researchos/masking.py`, `pre_mask` |
| Entity masking leaves 31 to 70% of transcripts re-identifiable; iterative rewriting by an LLM lowers the firm rate to 9% with industry at 44%, and the anonymised score loses to the raw one in a horse race after the cutoff, where look-ahead cannot operate | Empirical finding | `wu-2025`, `lopez-lira-2025` notes |
| A failed guess is a lower bound on memorisation; keeping only unrecognised items skews to obscure firms | Argument of the authors | `lopez-lira-2025`, Remark 1; methodology §10 |
| Recall fades one to two years before the stated cutoff; the positive control must come from at least three years before it | Empirical finding, one open-weight model | `gao-2025` |
| Randomising the last digit of every item of an unnamed, undated financial statement takes GPT-4's accuracy on the direction of next year's earnings from 0.60 to 0.51 (base rate 0.58); moving every decimal point three places, with no digit changed, does the same. Boosted trees on the same items go from 0.627 to 0.623. With a code interpreter the model's arithmetic is 100% right; without one it sums all balance-sheet items correctly 4% of the time. No test asks the model to name the firm, and the model was never handed computed ratios | Empirical finding, OpenAI models to gpt-4o, numeric tables only | `levy-2026` |
| On news, masking the name leaves 69% of firms and 92.5% of dates identifiable; nine rounds of masking and paraphrase bring both to chance (0.11%, 0.03%), by replacing every number with a placeholder. Earnings calls need up to 93 rounds. Large firms stay above chance | Empirical finding | `engelberg-2025` |
| What a model can be made to recall, whether it can date a masked input, and whether its calls shift are three different properties. A model that dated 9% of masked snapshots still moved its calls by 19 points when the date was shown. Arms assigned by design (date shown, date only, masked, wrong date) separate them; sorting by what an attacker recognised does not | Empirical finding, 15 models, macro snapshots | `jia-2026` |
| Measured knowledge cutoffs run earlier than the vendor's date for five of seven models, by three to eight months. The recall-by-forecast interaction has both signs across models and is undefined on frontier models, whose recall is saturated | Empirical finding | `jia-2026` |
| Telling a model to ignore later knowledge does not work, and can make things worse | Empirical finding | `lopez-lira-2025`, `li-2026` |
| Subtracting a remembered prior from the output is shown only on logits of open models; no black-box version has been tested | Verified fact about the methods | `li-2026`, `merchant-2025` |
| An LLM that writes trading rules for code to apply: one weak positive result on six assets; with look-ahead closed off and every trial counted, no LLM-written strategy beat luck, and a planted leaky feature passed the overfitting statistics | Empirical findings, prices only | `li-2025`, `gencay-2026` |
| Agents that learn from replayed outcomes credit a lesson with the market's move, not its own effect; none beat a rule baseline on real data | Empirical finding | `wu-2026` |
| A gap between calls on raw and on blinded text mixes recall, lost context and a prior attached to the name; on headlines it had the opposite sign to the one look-ahead predicts | Empirical finding | `glasserman-2023` |

Notes for every source are in `research/literature/papers/`; the synthesis is
`research/literature/streams/08_blind_replay.md`.

Consequences for the design. Each is our inference.

1. **Very small numeric noise may be enough to break recall of numbers**, at almost no cost in
   information: a statistical model barely notices it.
2. **When the recall went, so did the skill.** In Levy's setting the model had nothing left once
   it could not recognise the figures. A blind agent must be compared with a statistical
   baseline on the same inputs, and arithmetic belongs in code. Whether a model that is handed
   correct ratios keeps any skill under noise has not been tested by anyone; S2 tests it.
3. **Levy's inputs were statements of numbers. Ours are text with structure**, and ResearchOS
   found that structure identifies a large company. Noise on digits is unlikely to be sufficient
   here; whether it is, is hypothesis H3.
4. **The known way to hide a text removes its numbers.** Entity neutering reaches chance by
   turning every figure into a placeholder. Our call is made of figures. Blinding that keeps the
   numbers usable is the open problem, and nobody has measured it.
5. **Leakage is measured by arms, not by an attacker's verdict.** An attacker's failure to name
   a view is weak evidence that the view is inert (§9).

## 3. Two harms, and the quantity to maximise

Look-ahead damages two different things.

- **Evaluation.** A backtest score on pre-cutoff episodes is inflated. Only post-cutoff
  documents give a clean score. Nothing in S2 changes that (methodology §3 and §10).
- **Learning.** An agent that is right by recall gets no honest error signal, and its
  reflections on the episode are rationalisations. Judgement.

The second harm has a property the first lacks: **the test of what was learned is always run on
clean post-cutoff episodes.** A replay strategy does not have to be perfectly blind to be
compared with another; both are judged by what their playbooks do on clean data.

S2 maximises **usable history**: the share of pre-cutoff company-quarters that give an honest
error signal, with measured outcome leakage no higher than the post-cutoff reference. The end
measure is the gain on clean post-cutoff calls per unit of Claude usage.

## 4. Strategies

Grouped by what they change. All are hypotheses.

| | Strategy | Mechanism | Main risk | Wave |
|---|---|---|---|---|
| A | **Blind the input** (the owner's pipeline) | Four switches, each on or off: pseudonyms for the company and its named things; relative periods for dates; two-factor scaling of levels; noise on numbers (last-digit randomisation after Levy, or bounded noise on ratios). Later, with an LLM: span replacement and coarser structure | Renaming alone leaves 69% of firms and 92.5% of dates identifiable on news (`engelberg-2025`). The method that does reach chance deletes the numbers. A rewriting model brings its hindsight into the text | 1 (code only) |
| B | **Several views of one episode** (the owner's second request) | Eight views that switch A's four elements on and off by design, each judged by a fresh call (§5) | Eight times the calls | 1 |
| C | **Select instead of blind** | A closed-book probe per company-quarter (company and period only, repeated samples, "unknown" allowed). Where the model recalls nothing, use the raw text; blind only where it recalls. Measured cutoffs run months earlier than vendors' dates (`jia-2026`), so the last quarters before the cutoff may already be usable, and those releases are on the drive | A null probe is a lower bound. The usable set skews to obscure firms. A propensity can be high at chance accuracy, so the probe is gated on its hit rate | 1 |
| D | **Change the question** | Compare two companies in the same quarter, so that hindsight about the period cancels; labels relative to a baseline, with a base rate near 50% | Recall still works when both are recognised: a within-sector ranking task still leaked in one study (triaged, `08_blind_replay.csv`) | 1, as the label only |
| E | **Change the role** | The model writes rules; code applies them to all of history; the model sees aggregate feedback only. Three controls from `gencay-2026`: a closed vocabulary of as-filed features, a ledger of every version scored, and a stopping rule | Low prior: with those controls no LLM-written strategy beat luck. Statistics do not detect hindsight in the choice of rule; only the clean set does | 2 |
| F | **Change the learning signal** | Open-book case study (outcome shown, lessons drawn) against blind forecast, reveal and reflection. From `wu-2026`: score a lesson on the same episode with and without it, accept it only after it predicts episodes it was not built from, and keep a rule baseline as fallback. A placebo with shuffled outcomes | A lesson writer with hindsight contaminates the playbook; the one who writes lessons must be as blind as the one who forecasts | 2 |
| G | **Debias the output** | Subtract the call made from company and period alone | Not available: the published methods need logits. It survives as a control (the no-document prior, §9) and as C's gate | Dropped as a strategy |
| H | **Split the task** | The model reads and extracts; code does the arithmetic; only the forecast step needs blind data | Good sub-skills do not make a good call | Built into the pipeline (§6) |
| I | **Synthetic worlds** | Invented companies with a known generating process | The agent learns the simulator. No evidence found | Control only, if needed |
| J | **Audit the rationale** | Split the PM's rationale into claims, date each, and re-answer from the admissible ones (triaged) | Catches only leakage the model puts into words. In the one test, leakage fell from 0.171 to 0.001 and rank skill from 0.54 to 0.17 | 2, as the auditor's tool |
| K | **Checks that need no outcome** | Logical consistency across related forecasts tracks forecast quality (triaged). A training-free diagnostic on any amount of history | Forcing consistency did not improve forecasts | Diagnostic |

Wave 1 shares one generator and one set of measures. Wave 2 runs the learning loop on whatever
survives.

## 5. Several views of one episode

One episode, eight views, eight fresh calls. The views are a half-fraction of a two-level design
over A's four elements (name, period, scaling, noise), after the layout `wu-2026` uses for
memories. Every element is on in four views and off in four, so its effect on the call is
estimated inside the episode and the episode's own difficulty cancels. One view is the raw text
and one has everything switched on.

Five uses.

1. **Which element leaks.** The main effect of each element on how far the call leans towards
   the realised outcome, on pre-cutoff episodes. The same contrasts on post-cutoff episodes are
   the placebo: there, a name can add only what the model legitimately knows about the company.
   This replaces the first draft's split by what an attacker recognised, which `jia-2026` shows
   to be a poor proxy for whether a view is inert.
2. **Two kinds of change, kept apart.** Under the four elements the call should not move, apart
   from what a name legitimately adds. Under decision-relevant changes (number edits made by
   code, §9) it should. A count of unchanged calls means nothing without both (`li-2025`).
3. **A blind consensus call.** The mean over the blinded views averages out what depends on
   surface detail.
4. **Dose and response.** As the noise bound grows, identifiability falls and the call
   eventually destabilises. The gap between the two curves is the usable window.
5. **The core of the reasoning.** Only reasoning steps that appear in at least m of the views
   count as the episode's thesis, and only the thesis may feed a playbook. A reason found only
   where the name was shown is filtered out.

A per-episode estimate is mostly noise. Everything is pooled across episodes before it is read.

## 6. The pipeline and its roles

| Role | Runs as | Notes |
|---|---|---|
| Sourcer | Code | Assembles what existed at the event date by EDGAR acceptance timestamp: the 8-K earnings release (Exhibit 99.1), the previous release, fundamentals as first filed. News waits for a licensed source (rule 12) |
| Sanitiser | Code; an LLM only for span replacement and coarser structure, in wave 2 | Typed numbers; growth rates and margins computed by code and printed for the agent; one key per view (§7) |
| Probe PM | Fresh no-tool roster subagent | Makes the call only: direction, probability, a short rationale, what was missing. The same prompt as the real PM |
| Attacker | A cascade: rule fingerprint, then Sonnet, then Opus on what Sonnet missed. Any hit counts | Open top-three guess; ten-way line-up (chance 10%); year and quarter; closed-book recall of the outcome. Runs from the `s2-recall` definitions |
| Auditor (the owner's detector) | Rules. If a model reads rationales, it is first validated on 20 synthetic rationales with planted signs of recognition | Combines attacker results, signs of recognition in the rationale (claim by claim, strategy J), and a sufficiency checklist |
| Real PM | The agent under study | In production, elements are switched on until an episode passes. **In measurement every episode gets all eight views**, or the arms would hold different episodes (rule 5) |

One departure from the owner's sketch: the probe is not asked whether it recognises the company
in the same call that makes the decision. Asking invites recall and changes the call. ResearchOS
gives a prior for the size of such coupling: seven perspectives read together correlated 0.855,
read apart 0.387 (`feature_evidence.md`). The combined form is kept as one prompt factor in
S2-c.

Episodes are never dropped for staying identifiable. Each gets a status, and results
are reported for all of them, by status.

## 7. The sanitiser

`../Foundry/tools/tools/textmask.py` is reused for whole-word replacement only (`redact`,
`find_terms`). Its scaling is not, for two reasons found on this corpus (provisional: an ad hoc
read-only query on 2026-11-19, to be re-run by script in S2-a):

- Its table branch needs ` | ` separators. 56 of 60 sampled training releases have none, and
  more than half of the numbers on their table lines stay unscaled.
- One factor on net income, share count and EPS breaks EPS = net income ÷ shares, and the factor
  can be read back from the three printed numbers.

To write here:

1. **Typed cells**: level, share count, per-share, percentage, year. Built on
   `exp0005_earnings_exam.py` (`table_rows`, `parse_number`, `scale_for`).
2. **Two-factor scaling**: levels × f, share counts × f/g, per-share figures × g. The factors
   are not round: a power of ten keeps every digit string, which the rule attacker of step 5
   matches at once.
3. **A linker** from each printed percentage, ratio and subtotal to a formula over level cells,
   by value match (`exp0005.matches`).
4. **Noise** drawn on growth rates and margins; levels re-derived; linked numbers reprinted.
   Redrawn until signs, orderings and the position against guidance all hold.
5. **A rule attacker** (`fingerprint`): nearest neighbour on company facts. It sets the floor
   for the noise bound before any Claude call: the bound is raised until the rule attacker
   fails on the fully blinded view. No view is withheld from measurement on its account.
6. **A rounding-aware `check`** that also lists every percentage it could not link.

Decision-relevant edits (beat to miss, raise to cut) are number edits made by code before
sanitising, never written by a roster model (`labeling_codebook.md` §8). In wave 2 a Sonnet
sanitiser writes text that an Opus PM reads; the two are one family and may suit each other.
Wave 1 is code only and is not exposed to this.

## 8. The call, the label and the baselines

**The call**: the direction of a fundamental in the next quarter, labelled by rule from values
as first filed (`exp0005.period_for`, `value_for`). Stock reaction comes later and needs price
data the repo does not hold.

Candidate labels on the 1,309 training and development companies with at least one episode,
quarters ending from 2019 (empirical finding, EXP-0020; 31,065 episodes):

| Next-quarter label | Episodes | Base rate | Best simple rule |
|---|---|---|---|
| Year-on-year revenue growth is positive | 31,065 | 68% | Persistence, 80% |
| Year-on-year revenue growth accelerates (2-point dead band) | 24,144 | 49% | Reversal, 52% |
| Operating margin is up year on year | 26,468 | 53% | Persistence, 66% |
| Net income is up year on year | 28,648 | 55% | Persistence, 64% |

Each quarter comes from the first 10-Q or 10-K that reports it, and its growth rate uses the
prior-year figure printed in that same filing, so it is the rate a reader saw at the time. A
fiscal fourth quarter is the year less nine months (6,481 of 36,929 quarters).

**Primary label: acceleration**, with a dead band wider than the noise bound on the growth
rate shown, so that noise cannot put the label on the wrong side of the printed figure. A
2-point band removes a fifth of the episodes. Operating margin is secondary. In the one clean
quarter the picture is less tidy: persistence, not reversal, is the better rule (53% against 47%
on 709 episodes), and only 28% of the 25 largest-company episodes accelerate. One quarter is one
draw of the economy; the baselines are refitted on each window and reported beside every model
result.

**Baselines first** (rule 8): persistence, reversal, and a logistic model on as-filed
fundamentals, for the PM; the rule fingerprint for the attacker.

## 9. Measures

**The readout.** How far a call leans towards the realised outcome: the probability it gives to
the direction that happened.

**Outcome leakage, primary.**

1. **Element effects with a placebo** (§5, use 1). The effect of showing the name, or the
   period, on the readout, on pre-cutoff episodes, less the same effect on post-cutoff episodes.
   With one clean quarter the subtraction confounds period with cutoff; the pre-cutoff effect is
   reported on its own as well.
2. **The transplant, a positive control.** True data with a wrong company or a wrong period
   asserted, after `jia-2026`. If the call moves towards what happened to the asserted company,
   memory reaches the call when it is available, and the readout can see it. A measure that
   shows nothing here is blind, and a low reading elsewhere means nothing. The extension from
   dates to identities is ours.
3. **Number edits, with two controls.** How often the call follows a rule-made edit, by the size
   of the edit: the follow rate must rise with it, or the edit is broken. And the model's call
   with no document at all is recorded for every company, because a standing prior that happens
   to point the way the outcome went would look like recall (`ye-2026`). An edited episode has
   no true label; this measures sensitivity.

**Checks on any leakage measure** (`roy-2026`, restated for S2). It is never validated against a
label that one of its own inputs defines. It is computed within one model. It is tried on
episodes within a few months of the cutoff, where items differ in exposure and little else: a
measure that separates 2019 from 2025 and fails there is measuring drift. The smallest effect it
could detect is computed before any difference is read.

**The closed-book probe.** Company and period only, with "unknown" allowed in any wording.
Repeated samples; `jia-2026` used 20 at a fixed temperature, and a subagent's temperature cannot
be set, so the number of samples and the harness settings are recorded as they are. Two scores:
how often the model answers at all, and how often it is right, after removing the company's and
the quarter's own means so that knowing a firm usually grows does not count (`wu-2026`). The
propensity is used only where the hit rate beats chance. Recall is described, and is not used to
validate the measures above: on frontier models it is saturated, and its interaction with the
forecast has both signs across models.

**Supporting.** Identifiability: top-three hit, ten-way line-up, year within one, by company
size, against two chance benchmarks (the most frequent company, a random draw). Accuracy in old
periods against the clean window, shown beside rule baselines that cannot remember; descriptive
only.

**Information kept**, measured on post-cutoff episodes only, where a loss cannot be a removed
bias: accuracy against the realised outcome and the increment over the statistical baselines
first; agreement with the call on raw text second, since a name can distort a call as well as
inform it (`glasserman-2023`).

**Usable history** and **calls per episode**, by strategy, company size and period.

**Contamination labels.** Post-cutoff episodes: clean (vendor-stated cutoff). Pre-cutoff
episodes, however treated: contaminated, with the strategy and the elements switched on stated. S2 does not call a
treated result clean.

## 10. Samples and splits

All counts are for training and development companies (EXP-0020).

- **Clean window.** 995 labelled episodes released after the cutoff, one per company, all from
  July to September 2026; 734 lie outside the dead band. The October and November releases
  (1,256) have no next quarter yet. That is one labelled transition. Among the 50 largest
  companies by revenue there are 37 clean episodes, 25 outside the dead band, which binds any
  claim about megacaps on clean data. The test side would add about one and a half times as
  many.
- **Old periods.** 29,606 labelled episodes released by the cutoff, 1,401 of them from the 50
  largest companies. Their releases are not on the drive: of 33,378 releases since 2019 that map
  to a labelled quarter, 4,404 are there, nearly all from 2026, because `exp0003.targets` keeps
  only the last pre-cutoff release of each company. Releases from 2019 to 2025 are a new pull
  and need the owner's say-so (rule 17). `s2/exp0020/releases.jsonl` lists every candidate.
- **Companies.** S2-a and S2-b use training and development companies of split v1 only. The
  session that dispatches subagent calls reads what it dispatches, and Claude does not read
  post-cutoff test items (changelog, 2026-11-14). A test-side run needs an exception or a
  scripted path (decision 5).
- **A second clean quarter.** Calls on the October and November releases could be sealed now
  and scored in February 2027 (decision 6).

## 11. Experiments

Numbers are provisional. Each experiment gets its pre-registration, with thresholds and seeds,
once S2-b has supplied the rates.

### S2-0 Literature pass

Done 2026-11-19: `research/literature/streams/08_blind_replay.md`, 13 deep notes and 6 triaged
rows. It was also asked for approaches that do better than anonymising; §4 and §9 are revised
from it. A spot check re-opened three of the papers for eight claims: all supported in
substance, with one pair of figures in the `wu-2026` note not found in the part re-read and not
used here.

### S2-a Feasibility (engineering, no hypothesis)

Scripts take the next free numbers when written; a block is reserved in the registry.

| Script (subcommands) | Purpose |
|---|---|
| `exp0020_s2a_episodes.py` (series, label, targets, audit) | **Run 2026-11-19 (EXP-0020).** Quarterly series as first filed; candidate labels and rule baselines (§8); every earnings release since 2019 with what is on the drive (§10). Local archives only. The pull and the logistic baseline are later scripts |
| `s2a_sanitiser` (build, check, fingerprint, show) | The eight views with their keys; the rule attacker sets the noise floor |
| `s2a_dispatch` (emit, ingest, check, usage) | Transport. `emit` writes one JSON per call (id, agent, prompt, canaries) and never opens labels or keys. The session passes the prompt verbatim to the named agent and writes the raw reply and usage back, three in flight at most. `ingest` checks canaries and schema and appends the run record. A failed call is re-emitted under a new id and both are kept. Also confirms that the agent definitions load and report no tools |
| `s2a_roles` (prepare, score, check) | PM and attacker prompts, line-ups, rule scoring (`masking.normalize_name`, `identifying_guess`) |
| `s2a_counterfactual` (build, check) | Rule number edits made before sanitising, with unedited controls, tagged as agreeing with or contradicting the outcome |
| `s2a_role_models` (prepare, score) | The Sonnet question (§12), then a smoke run of 5 episodes by 3 views |

### S2-b Screening (descriptive, thresholds pre-registered)

Three steps, each on training and development companies.

1. **Is there leakage to remove, for this call?** The closed-book probe and the transplant on
   old episodes of the largest companies. If the model recalls nothing and the transplant moves
   nothing, replay on raw text with a contamination label is the answer for this task, and that
   is the finding.
2. **Where does recall end?** The probe on the last quarters before the cutoff, whose releases
   are on the drive already (about 1,500 from 2026). This is strategy C's test and needs no
   pull.
3. **The eight views** (strategies A and B) on the same episodes, old and clean, with the
   transplant and the number edits. Each element is reported as leakage, information kept,
   usable history and cost.

The size is set from S2-a's usage figures and the smallest detectable effect, and put to the
owner.

### S2-c The best two or three, in depth (confirmatory)

A small factorial of prompt factors on development episodes, with the same number of
evaluations per arm (methodology §7): numeric treatment first, then structure, period, and the
style of the sanitiser's instruction.

### S2-d The learning loop (confirmatory; power computed first)

Playbooks built with no replay, raw replay, the best strategy from S2-c, E and F, compared on
clean post-cutoff episodes. Every run records the playbook's update rule and the latest outcome
date behind each entry (`ye-2026`). A lesson is scored on the same episode with and without it,
and kept only after it predicts episodes it was not built from (`wu-2026`). Strategy E runs with
its closed vocabulary, ledger and stopping rule (`gencay-2026`).

### Hypotheses to be pre-registered

- **H1 (the re-test of GY-0000).** Some combination of elements defeats the Opus line-up on
  large caps while accuracy on clean episodes stays within a stated bound of the raw text's.
  Prior from ResearchOS: false for megacaps.
- **H2 (the period matters more than the name).** Hiding the period lowers the readout more
  than hiding the name. `engelberg-2025` supports it on news (dates are recovered more often
  than firms); `wu-2026` found that hiding dates left the pre-cutoff advantage in place.
- **H3.** Randomising the last digit does not suffice on text with structure; ratio noise adds
  to it.
- **H4.** The consensus of the blinded views leaks less than one view and keeps as much
  information.
- **H5.** Selecting episodes by the closed-book probe gives more usable history than blinding
  them, with no more leakage.
- **H6 (skill without recall).** Handed ratios computed by code, the blinded PM beats the
  logistic baseline on clean episodes. Levy's result makes the prior low.

## 12. Models, and whether Sonnet is enough

Decided by role, by which error is dangerous, not by one bake-off.

| Role | Rule | Extra calls |
|---|---|---|
| Attacker | No test: the cascade ends in Opus, and any hit counts. The attacker is never weaker than the PM | None |
| PM and probe | The model the owner would deploy. Both models answer about 20 closed-book recall queries and about 30 clean development episodes on raw text. Sonnet is used only if its clean accuracy cannot be told from Opus's; otherwise everything runs on Opus | About 100 |
| Sanitiser | Code in wave 1. In wave 2, Sonnet by default; the attacker catches its failures | None in wave 1 |
| Auditor | Rules; a model only after the 20-rationale validation | About 20, short |

## 13. Rules this sub-study touches

- **Rule 2 and GY-0000.** S2 studies masking as its subject. The rule is unchanged elsewhere.
- **Rule 7 and methodology §2.** The commercial part is reopened for S2 only. The attacker and
  the recall probe run from `.claude/agents/s2-recall-claude-*.md`, because the roster prompt
  says "Answer only from the text in the message".
- **Rule 5.** One confirmatory run per frozen configuration; the views are crossed by design, not
  chosen by outcome.
- **Rule 8.** Baselines for the PM and for the attacker run before any model result is read.
- **Rule 12.** Sanitised texts and keys stay on the external drive. Prompts live in the scripts.
- **Rule 17.** Old releases and a second company-facts snapshot are pulls (decision 4).
- **Methodology §10.** Unchanged. S2 does not claim that masking removes look-ahead.

## 14. Compute, order and cost

S2 uses no MLX time and does not compete with S1. Its scarce resource is the owner's Claude
allowance: at most three agents in parallel (rule 19), and every view of every episode is
several calls. Usage per call is unknown until `s2a_dispatch usage` measures it; S2-b's size is
proposed only after that. For scale, a full audit row in `jia-2026` cost about 10 million tokens
on a small commercial model. A subagent's temperature cannot be set and its effort is pinned at
`high`; both are recorded with every call, since `jia-2026` found that sampling settings and the
reply parser move such measures. WP5's sealing (2027-01-10) has priority over S2.

## 15. Decisions for the owner

1. ~~**S2 as the re-test of GY-0000.**~~ Approved 2026-11-19.
2. ~~**Commercial part reopened for S2 only.**~~ Approved 2026-11-19.
3. ~~**Separate no-tool definitions for the attacker and the recall probe.**~~ Approved
   2026-11-19; created in S2-a.
4. **EDGAR pulls.** EXP-0020 lists 31,165 releases since 2019 that map to a labelled quarter and
   are not on the drive. Proposed: about 1,500 of them, drawn by seed from
   `s2/exp0020/releases.jsonl`: four per company for the 250 largest by revenue, spread over
   2019 to 2024, and 500 from the rest. At the 5 requests a second used so far that is under
   half an hour and under 100 MB. Step 2 of S2-b needs no pull. Also a second company-facts
   snapshot in December (1.3 GiB).
5. **The test-side run**: an exception to "Claude does not read post-cutoff test items", or a
   scripted path. Needed before S2-c.
6. **A prospective arm**: seal calls on the October and November 2026 releases now.
7. ~~**Freeze this draft.**~~ Approved 2026-11-20.

## 16. What would change this plan

- **No measurable leakage on raw text for this call** (S2-b): the strategies have nothing to
  remove. The study turns to the stock-reaction call, where recall is known to be strong, or
  stops with that finding.
- **The transplant moves nothing although the probe shows recall**: the readout cannot see
  leakage and no strategy can be ranked. The readout is redesigned before anything else runs.
- **Recall is saturated for every old episode of a large company**: strategy C offers those
  companies nothing before the last quarters, and their history depends on A and B alone.
- **The blind PM does not beat the logistic baseline on clean episodes**: there is no skill to
  protect on this call. The call is changed, or text the baseline cannot read (guidance, tone)
  is made the subject.
- **The rule fingerprint already finds every noised view**: noise on ratios cannot hide these
  companies, and wave 1 moves to C, D and E.
- **Usage per call makes eight views unaffordable**: B is run on megacaps only, where it matters
  most.

## Sources

Every source cited above has a note in `research/literature/papers/` that says which version
and which sections were read. Short names used here:

| Short name | Note |
|---|---|
| `levy-2026` | `levy-2026-numerical-reasoning-lookahead.md` |
| `engelberg-2025` | `engelberg-2025-entity-neutering.md` |
| `glasserman-2023` | `glasserman-2023-lookahead-gpt-sentiment.md` |
| `jeon-2026` | `jeon-2026-blindtrade-anonymization-first.md` |
| `jia-2026` | `jia-2026-hindsightbench-black-box-audit.md` |
| `wu-2026` | `wu-2026-memtrial-trust-memory.md` |
| `roy-2026` | `roy-2026-memguard-alpha.md` |
| `ye-2026` | `ye-2026-alpha-illusion.md` |
| `benhenda-2026` | `benhenda-2026-look-ahead-bench.md` |
| `li-2025` | `li-2025-profit-mirage-factfin.md` |
| `li-2026` | `li-2026-fincad-contrastive-decoding.md` |
| `merchant-2025` | `merchant-2025-divergence-decoding.md` |
| `gencay-2026` | `gencay-2026-honest-evaluation-strategy-discovery.md` |
| `wu-2025`, `lopez-lira-2025`, `gao-2025` | Stream 03 notes of the same names |

Triaged only, with a row in `research/literature/streams/08_blind_replay.csv` and no note: Kim,
Muhn and Nikolaev (2024); Zhang, Chen and Stadie (2026); Paleka et al. (2024); Ghosh (2026); Yu
et al. (2023); Zhang et al. (2026).
