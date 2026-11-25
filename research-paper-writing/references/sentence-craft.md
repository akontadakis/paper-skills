# Sentence Craft Guide

**Load when:** sentence-level polish, after the paragraph structure is settled.

**Contents:** Goal · Tense by Section · Verbs · Old Before New · Hedging · Anthropomorphism · Numbers and Units · Abbreviations · Word Choice · Sentence-Level Faults · Prose, Not Bullets · Editing Around Protected Markup · Revision Checklist

## Goal

Fix the layer below the paragraph: tense, verbs, hedging, numbers, and word choice.

Use this after paragraph structure is settled. Restructuring a paragraph invalidates
sentence-level edits, so do not run this first.

## Tense by Section

| Content | Tense | Example |
|---|---|---|
| Established knowledge, accepted fact | present | Melanopic response peaks near 490 nm. |
| What a cited study found | past | Author (2019) reported a 12% shortfall. |
| What a cited study's method does, still true | present | The three-phase method chains a daylight matrix, a BSDF transmission matrix and a view matrix. |
| What you did | past | We ran the simulation for every occupied hour. |
| What you found | past | Mean compliant plan depth fell to 3.1 m under the worst-case view direction. |
| What a figure or table shows | present | Figure 4 shows the seasonal spread. |
| What the finding means, now | present | These simulations suggest that view direction matters more than climate in side-lit offices. |
| Limitations, scope | present | The grid resolution bounds the deep-plan cases. |
| Future work | future / conditional | Field measurement would resolve the discrepancy. |

Rules:

1. Do not switch tense inside a sentence without a reason the reader can see.
2. Methods and Results are past. Discussion mixes past (what you did) and present (what is now known) — that mixture is correct, not an error.

## Verbs

1. **De-nominalize.** Move the action out of the noun and into the verb.
   - `performed an analysis of` → `analysed`
   - `the utilisation of X resulted in a reduction of Y` → `X reduced Y`
   - `made a comparison between` → `compared`
2. **Cut empty verbs.** `conduct`, `perform`, `carry out`, `utilise`, `achieve`.
   - `utilise` is almost never right. Use `use`.
3. **Active voice by default.** `We measured` beats `measurements were made`. Passive is correct only when the actor is irrelevant or unknown.
4. **Put the actor in the subject slot.** If the sentence's grammatical subject is not the thing doing the acting, rewrite it.
5. **Keep subject and verb close.** Long noun phrases between them force the reader to hold state.

## Old Before New

The standard flow mechanism below the paragraph level. Each sentence opens with information
the reader already holds and places the new information at the end, where the stress falls.

1. **Given first.** Start from what the previous sentence established; the new point goes
   last.
   - ✗ `A 14% shortfall in the north zone was revealed by the annual simulation.`
   - ✓ `The annual simulation revealed a 14% shortfall in the north zone.` — "the annual
     simulation" is given (it was just described); the shortfall is the news.
2. **Keep the subject stable.** While a paragraph is about one entity, keep that entity in
   the subject slot; switching subjects sentence-to-sentence forces the reader to reorient.
3. When a sentence reads as disconnected, check its opening: it is usually introducing
   brand-new material in the given position.
4. This is the sentence-level mechanism behind SKILL.md Global Principle 4; the paragraph-
   level relations (cause, contrast, consequence, refinement) still govern which sentence
   comes next.

## Hedging

Calibrate. Both directions are errors.

**A hedge is part of the claim.** The Revision Contract in `SKILL.md` freezes the hedging verb
of every claim, so a style pass never adds, removes or swaps one. Calibration is a separate job.
It runs only when the author asks for it, or when a review finding names the claim. Each verb
that moves is then recorded in `.paper/claims.yml` as a `verb_change` with its decision; see
`paper-review.md`, Claim-Strength Drift. Outside that job, keep the hedge and flag the problem
to the author.

**Over-hedged** — stacked qualifiers dilute a real result:

- `it could possibly be suggested that there may be a potential tendency` stacks four hedges
  on one claim. Flag it. When the author asks for calibration, the claim keeps one hedge,
  chosen from the ladder below to match the evidence.
- Stacks to flag: `may possibly`, `might potentially`, `appears to suggest`.

**Under-hedged** — a claim the data cannot carry:

- `proves` → `shows`, `indicates`
- `demonstrates that A causes B` from correlational data → `is consistent with A causing B`
- `always`, `never`, `all` → check the data actually covers every case.

**Scale the verb to the evidence:**

| Evidence | Verb |
|---|---|
| Direct, controlled, replicated | shows, demonstrates |
| Strong but single-study | indicates, provides evidence that |
| Correlational | is associated with, is consistent with |
| Modelled or inferred | suggests, implies |
| Speculative | may, could |

**Scale the task verb to the design.** The verb naming what the study *did* is itself a
claim, and it over-claims as easily as a finding verb:

| Verb | Claims | Requires |
|---|---|---|
| compared | descriptive difference | the comparison itself — safe default |
| evaluated | judged against a criterion | the criterion, stated |
| validated | agreement with independent reference data | the reference data, and the error metric |
| replicated | same result on new data | the new data and the original protocol |
| predicts | out-of-sample performance | a held-out test, not a fit |
| characterised | systematic coverage of the behaviour | the sweep or sample that covers it |

Never promote a descriptive comparison into "validated" or two model fits into "replicated".
What a Validation subsection must report is in `methods-journal.md`; this rule governs only
what the verb may claim.

## Anthropomorphism

1. Studies, data, models, and figures do not think, believe, want, or claim.
   - `the model believes` → `the model predicts`
   - `the data want to tell us` → cut it
2. `The results suggest` is acceptable and standard. `The results argue` is not.

## Numbers and Units

On a revision these rules are flagged to the author and not applied, because the frozen set comes back unchanged.

1. Spell out numbers below ten in prose, use numerals for ten and above — **except** always use numerals with units, in comparisons, and in any measured value: `3 m`, `5 of 12 sites`; otherwise `two hypotheses`. Follow the journal for the thousands separator. SI style groups digits in threes with a thin space and leaves a four-digit number ungrouped (`4380`, `12 380`); many journals use a comma (`4,380`). Pick one and hold it.
2. Never start a sentence with a numeral. Recast the sentence.
3. Space between value and unit: `10 lx`, `2.5 m`, `450 nm`, and `25 °C` — degrees Celsius takes the space.
   Closed up: plane angles (`45°`), and `%` by near-universal journal practice (`34%`), though strict SI would space it. Pick one for `%` and hold it.
4. Use SI, and the unit the field uses. Do not invent abbreviations.
5. Decimal places: consistent within a metric, and no more than the measurement supports. Do not report `51.243%` from a 188-sample set.
6. Report uncertainty in the same units and to the same decimal place as the value: `4.2 ± 0.3 m` or `4.20 ± 0.27 m`, not `4.2 ± 0.27 m`. Say what the `±` is — a standard deviation, a standard error, an interval, an expanded uncertainty — once in Methods, and again in each table or figure caption that shows a `±` value, because captions are read alone. Round the uncertainty first; `statistics-reporting.md`, Measured Quantities and Uncertainty, has the rules.
7. Ranges use `to` in prose when a dash is ambiguous with a minus sign: `−5 to 12 °C`.
8. Define every symbol at first use and never redefine it.

## Abbreviations

On a revision these rules are flagged to the author and not applied, because the frozen set comes back unchanged.

1. Define at first use in the main text, and again at first use in the Abstract — they are read separately.
2. Do not introduce an abbreviation you will use fewer than three times; write the term out.
3. Do not abbreviate a term the target readership already knows.
4. One expansion per abbreviation, one abbreviation per concept. No aliasing.

## Word Choice

| Wrong | Right | Why |
|---|---|---|
| affect / effect | affect = verb, effect = noun | except "to effect a change" |
| comprise / compose | the whole comprises the parts | never "is comprised of" |
| significant | statistically significant, or large / substantial | reserve "significant" for the statistical sense |
| correlated | associated | unless you computed a correlation |
| amount of / less | number of / fewer | for countable things |
| data is / data are | pick one, hold it | `data are` in formal scientific prose; singular is now widely accepted, but mixing within a paper is not |
| while | whereas / although | reserve "while" for simultaneity in time |
| since | because | reserve "since" for time |
| respectively | — | only when two ordered lists genuinely map onto each other |
| novel | say what is different | reviewers discount "novel"; neither `novel` nor `new` in a title |
| very, quite, rather, extremely | cut | intensifiers weaken technical prose |
| in order to | to | |
| due to the fact that | because | |
| it should be noted that / it is worth noting that | cut | |
| a number of | cut, or give the number | |
| prior to / subsequent to | before / after | |
| in close proximity to | near | |
| a total of N | N | |
| whether or not | whether | except "regardless of whether or not" |
| the reason is because | because | |
| it is well known that | cite it, or state the fact plainly | unattributed consensus is not evidence |
| it has been shown that | name who showed it, with the citation | |

**Post-2023 overused register.** These now read as machine-generated and are increasingly
flagged by reviewers. Full table, with the protected-term carve-outs, in `ai-tells.md`. One
hit is not a fault: act on a cluster, as the tier rules in `ai-tells.md` say, and never inside
a protected term. A field's own `enhance` or `robust` stays.

| Wrong | Right |
|---|---|
| crucial, vital, key (adj.) | state the consequence from the source, or write an `[insert ...]` bracket; or cut |
| delve into | examine, analyse |
| underscore, highlight (v.) | cut, or flag the claim verb for calibration (Hedging) |
| enhance, leverage | improve (with magnitude), use |
| interplay | interaction |
| landscape, realm (abstract) | name the actual thing |
| showcase, pivotal, align with | show, cut, match |

## Sentence-Level Faults

1. **Dangling modifier** — the opening phrase must modify the grammatical subject.
   - ✗ `Using a 0.5 m grid, compliant plan depth was resolved in 0.5 m steps.` (the depth was not using the grid)
   - ✓ `Using a 0.5 m grid, we resolved compliant plan depth in 0.5 m steps.` / `A 0.5 m grid resolved compliant plan depth in 0.5 m steps.`
2. **Ambiguous `this`** — never leave `this` bare. `This effect`, `this shortfall`, `this substitution`.
3. **Subject–verb agreement across a long phrase** — `the set of measurements ... was`, not `were`.
4. **Stacked nouns** — three or more nouns in a row forces the reader to guess the relations. `daylight zone weight convention clash` → `a clash between daylight-zone weighting conventions`.
5. **Sentence length** — target 15–25 words average (a diagnostic; see `ai-tells.md`, section 8). One long sentence is fine; three in a row is not.
6. **Two claims in one sentence** — when `while`, `whereas`, `although`, or a semicolon stitches two independent, separately-checkable claims together, split them. Each claim needs its own evidence pointer, and a reviewer disputing one should not be disputing the sentence. A contrast whose two halves rest on one evidence pointer may stay in one sentence, and so may a contribution with its gain (`abstract.md`, Version 3).

## Prose, Not Bullets

1. The final manuscript is continuous prose. Bullets are a planning tool.
2. Lists are acceptable only in Methods (inclusion criteria, materials, parameter settings) and Supplementary.
3. Never in Abstract, Introduction, Results, Discussion, or Conclusion.
4. Structured abstracts (`Background:` `Methods:`) only where the venue requires them.

## Editing Around Protected Markup

When editing a `.tex` source rather than plain prose, these are not text.

1. **Never modify**: math environments (`$...$`, `equation`, `align`), `\cite{}`, `\ref{}`,
   `\label{}`, `\eqref{}`, algorithm blocks, code listings, and figure/table environments.
   Inside a float, only the caption text is editable, unless the task is table layout under
   `experiments.md`, Figure/Table Writing Rules; no cell value changes even then.
2. **Never substitute a technical term.** A word on a style blacklist may be a defined term
   in the field. `robust optimisation` stays. See the protected-terms list in `ai-tells.md`.
3. **Flag, do not guess.** If a domain term's correctness is unclear, mark it for the author
   rather than replacing it.
4. **Preserve semantic content exactly.** An edit may change how a technical statement reads,
   never what it asserts. A number, unit, condition, or qualifier is not a style choice.
5. Mark any claim you cannot verify with the Revision Contract's bracket, which names what is
   missing: `[insert the source for the 12% shortfall]`. Do not soften the claim silently —
   silent softening hides the problem from the author.

## Revision Checklist

1. Is the tense correct for the section and consistent within each paragraph?
2. Is every action in a verb rather than a noun?
3. Is every hedge earned, and is any claim over-stated?
4. Does every number carry the right units, precision, and uncertainty?
5. Is every abbreviation defined once, in text and in the Abstract?
6. Is every `this` followed by a noun?
7. Does any opening phrase dangle?
8. Are there stacked nouns that need unpacking?
9. Is any term used with two names, or one name for two things?
10. Are there bullets anywhere they should not be?
11. Does any sentence end in an unsupported `-ing` clause (`highlighting...`, `underscoring...`)?
12. Has any protected markup, technical term, or numeric value been altered by an edit?
13. Does each sentence open with given material and end on the new point, with a stable subject?
14. Does any task verb (`validated`, `replicated`, `predicts`) claim more than the design performed?

After this pass, run `ai-tells.md` for register, rhythm, and the over-editing guard.
