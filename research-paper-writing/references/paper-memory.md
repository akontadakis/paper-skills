# Paper Memory

**Load when:** the manuscript has a `.paper/` folder, or the task needs a claim ledger, a figure inventory or a term lock.

**Contents:** Goal · Why This Exists · Directory · claims.yml · figures.yml · terms.yml · gap.yml · reviews/ · Workflow Integration · Consistency Rules · What This File Deliberately Omits · Checklist

## Goal

Keep the claim ledger, the figure inventory, the terminology lock, and the verified gap in
files on disk, so they survive between sessions instead of dying with the conversation.

## Why This Exists

The claim ledger in `paper-review.md` is the mechanism that stops an unsupported claim from
reaching the Abstract. It only works if it persists. A ledger rebuilt from scratch each session
loses exactly the rows that matter: the `needs evidence` row nobody chased, the `gap` whose
reason was agreed three weeks ago, the claim that was weakened and then silently restored by a
later edit.

The same is true of terminology. "Keep terminology stable across the full paper" is a rule
nobody can apply from memory across a six-month revision cycle.

Paper memory is one directory of small YAML files next to the manuscript. It is the source of
truth for everything the Output Contract asks for.

## Directory

```
<manuscript-dir>/
  .paper/
    question.yml      the research question and the go or stop decision — research-study-design
    design.yml        the frozen study design and its amendments        — research-study-design
    runs.yml          one row per run: code, inputs, versions, outputs  — research-study-design
    claims.yml        the claim ledger                        — this file
    figures.yml       figure and table inventory, with the numbers each carries
    terms.yml         terminology and symbol lock
    gap.yml           the verified gap evidence package
    venue.yml         the journal's observed conventions and its required rules — venue-calibration.md
    verified-refs.yml the works a draft may cite, each checked against a record or by the author — latex-mechanics.md
    changes.yml       reviewer comments and what each one changed — responding-to-reviewers
    checklist-<name>.md   reporting-guideline disposition table — reporting-checklists.md
    reviews/          dated review findings, one file per round
      2026-08-21-results.md
    corpus/           literature-crawler output, one set per search
      <slug>-corpus.yml       every included record
      <slug>-excluded.yml     every excluded record, with its reason
      <slug>-protocol.md      verbatim queries, databases, search date, hit counts
```

This file owns `claims.yml`, `figures.yml`, `terms.yml`, `gap.yml`, and `reviews/`, and it
owns the directory as a whole. Eight entries are defined elsewhere and are listed here so the
directory has one complete description: `question.yml`, `design.yml` and `runs.yml` in the
`study-memory.md` reference of `research-study-design`, `venue.yml` in `venue-calibration.md`,
`verified-refs.yml` in `latex-mechanics.md`, Reference Identity and Notices,
`changes.yml` in the `change-ledger-file.md` reference of `responding-to-reviewers`,
`checklist-<name>.md` in `reporting-checklists.md`, and `corpus/` in the `literature-crawler`
agent. **Anything that adds a file to `.paper/` adds a line here.**

Rules:

1. `.paper/` sits beside the manuscript, in the same repository or folder. It is versioned with
   the manuscript, not hidden in a scratch directory. A study that began with
   `research-study-design` already has a `.paper/` in the project's top folder: look beside the
   manuscript first, then in each folder above it, and use the first one found. Never create a
   second.
2. These files are working artifacts. They are never submitted, and nothing in them is copied
   into the manuscript verbatim.
3. If `.paper/` does not exist and the task needs a ledger, create it. Do not silently keep the
   ledger in the conversation only.
4. Read `.paper/` **before** starting any drafting, revision, or review task on a manuscript
   that has one. It is faster than re-deriving the state and it is the only way to catch a
   regression.

## claims.yml

One row per claim, matching the ledger table and the four statuses in `paper-review.md`. The
example shows the ledger after one round of peer review; `paper-review.md` shows the same
ledger before submission.

```yaml
version: 1
manuscript: "manuscript.tex"
updated: "2026-08-21"

claims:
  - id: C1
    text: "View direction affects melanopic compliance more than climate in side-lit offices."
    location: ["Abstract L6", "Sec. 4.1 L12", "Conclusion L3"]
    status: supported          # supported | needs evidence | gap | rejected
    evidence:
      - "Fig. 4"
      - "Table 2"
      - "Sec. 4.2, mean compliant plan depth 5.8 m against 3.1 m"
    verb: "suggests"
    risk: "Holds only for the four sampled climates. Bound the sentence."
    bounded_to: "four European climates, 24 side-lit office geometries"
    analysis_status: planned   # planned | changed before analysis | post hoc | not applicable
    planned_claim: "P1"        # the planned_claims row of design.yml this claim came from
    verb_change:               # present only when a revision changed the verb
      before: "shows"
      after: "suggests"
      decision: keep           # restore | keep | pause
      reason: "Conceded to reviewer comment R1.2: a simulation study in four climates does not support 'shows'."

  - id: C2
    text: "The 0.5 m analysis grid does not bias the reported compliant plan depth."
    location: ["Methods L88"]
    status: supported
    evidence:
      - "Table 3"
      - "Sec. 2.4, grid-convergence test at 1.0 m, 0.5 m and 0.25 m"
    verb: "indicates"
    risk: "Was `needs evidence` before review. The convergence test answered reviewer comment R1.1."
    load_bearing: false

  - id: C3
    text: "Melanopic shortfall is driven by climate."
    location: ["Intro L21"]
    status: rejected
    evidence: ["Fig. 4"]
    verb: null
    risk: "Fig. 4 shows the opposite relationship. Rewrite the claim to match the data."

  - id: C4
    text: "The simulated compliant plan depth matches what occupants receive in real rooms."
    location: ["Discussion L40"]
    status: gap
    evidence: []
    verb: "assume"
    gap_reason: "The model was not validated against measurement, and no measured rooms are available to this study."
    load_bearing: false
```

Field rules:

1. `status` takes exactly one of the four values. Blank is never allowed — that is the
   no-silent-gaps rule in `paper-review.md`.
2. `evidence` empty requires `status: gap` or `status: needs evidence`, and a stated
   `gap_reason` in the `gap` case.
3. `verb` records the verb the sentence carries. The status caps it: see `paper-review.md`,
   Two Rules That Make It Work, rule 2, Status gates the verb. That table is the one statement
   of the ceiling.
4. `location` is where the claim is asserted in the manuscript, not where its evidence lives.
   A claim asserted in three places has three entries, because weakening it means editing all
   three.
5. `load_bearing` marks a claim the contribution depends on. A `gap` on a load-bearing claim
   fails the Submission Gate.
6. `bounded_to` records the conditions the claim is limited to. This is what the Limitations
   paragraph and the sample-bounding rule in `ethics-and-participants.md` both draw on. When
   `design.yml` exists, `bounded_to` starts from the `bounded_to` of every case set in
   `design.yml` that the claim rests on; narrow it from there, and do not retype it.
7. For a review paper, `evidence` cites included studies by their corpus identifier rather than
   a figure of your own. See `review-papers.md`.
8. `analysis_status` records when the analysis behind the claim was decided. `planned` means
   it was fixed before any result was seen. `changed before analysis` means the plan was
   revised before the data were analysed, and the change is stated in Methods. `post hoc`
   means the threshold, the climate set, the grid size, the subgroup, or the metric was
   chosen after results were seen. `not applicable` is for a claim that rests on no analysis
   choice, such as a statement of what was built. The field is optional; when it is present
   it takes one of those four values. A `post hoc` claim is labelled exploratory in Results,
   is never worded as planned or as the hypothesis the study set out to test, and does not
   carry the paper's headline. Presenting a choice made after the fact as one made before is
   an easy overclaim to make in a simulation study, where the first runs often suggest a
   better threshold. When `.paper/design.yml` exists, the status follows from the amendments
   that affect the claim's planned claim, and is never set from memory. `planned_claim` names
   the row of its `planned_claims` that this claim came from; seed it before drafting (see
   Workflow Integration). A claim whose planned claim is affected by a `post hoc` amendment of `kind: choice` is
   `post hoc`. A `kind: correction` amendment, which repaired a fault a check exposed, leaves
   the status as it was. A claim is `planned` only if the design was frozen on or before the
   date of the first production run.
9. A verb changed by a revision records its decision here as `verb_change`: `before`, `after`,
   and a `decision` of `restore`, `keep` with a `reason`, or `pause`. See `paper-review.md`,
   Claim-Strength Drift. This is the claim's own record. When the change answers a reviewer,
   the comment's row in `changes.yml` records the same decision under `claim_verb_change`,
   which names the claim by id; that field is defined in the `change-ledger-file.md`
   reference of `responding-to-reviewers`. The two must agree, and `scripts/check_ledger.py`
   checks that each carries a decision.

## figures.yml

The figure and table inventory. It answers two questions that are otherwise re-derived every
session: what number does this figure actually carry, and which claim rests on it.

```yaml
version: 1
updated: "2026-08-21"

figures:
  - id: "Fig4"
    kind: figure          # figure | table
    file: "figs/depth_by_view_direction.pdf"
    source: "scripts/plot_depth.py"
    runs: ["R3"]
    transformation: "results/annual.csv -> filter occupied hours -> compliant plan depth per geometry -> mean by view direction and climate"
    caption_gist: "Mean compliant plan depth by view direction, four climates."
    key_numbers:
      - "mean compliant plan depth 5.8 m best case, 3.1 m worst case"
      - "spread across climates 0.9 m"
    supports_claims: ["C1"]
    cited_in: ["Sec. 4.2"]
    status: final         # draft | final | regenerate

  - id: "Tab2"
    kind: table
    file: "tables/depth.tex"
    source: "scripts/make_table2.py"
    runs: ["R3"]
    transformation: "results/annual.csv -> filter occupied hours -> compliant plan depth per geometry -> one row per geometry, best-case and worst-case view direction"
    caption_gist: "Compliant plan depth per office geometry, best-case and worst-case view direction."
    key_numbers:
      - "mean over the 24 geometries 5.8 m best case, 3.1 m worst case"
    supports_claims: ["C1"]
    cited_in: ["Sec. 4.2"]
    status: final

  - id: "Tab3"
    kind: table
    file: "tables/grid.tex"
    source: "scripts/make_table3.py"
    runs: ["R2"]
    transformation: "results/grid_test.csv -> mean compliant plan depth at each grid spacing"
    caption_gist: "Grid-convergence test at 1.0 m, 0.5 m and 0.25 m."
    key_numbers:
      - "6.9% between 1.0 m and 0.5 m, 0.4% between 0.5 m and 0.25 m"
    supports_claims: ["C2"]
    cited_in: ["Sec. 2.4"]
    status: final
```

Field rules:

1. `key_numbers` holds the values the prose quotes from this figure. When a figure is
   regenerated, every number here is re-checked against the text. This is the single most
   common silent inconsistency in a revised manuscript.
2. `source` records what produces the figure — a script, a notebook, an engine run, or
   `manual`. A figure with no reproducible source is a `simulation-reporting.md` provenance
   problem, not only a bookkeeping one.
3. `supports_claims` cross-references `claims.yml` ids. A figure supporting no claim is either
   decorative or the claim is missing; both need a decision.
4. `cited_in` is where the text refers to it. A figure with an empty `cited_in` is an uncited
   float — the same fault `latex-mechanics.md` and `word-manuscripts.md` check for.
5. `status: regenerate` marks a figure whose underlying data or style has changed. It blocks
   the Submission Gate until it is `final` and its `key_numbers` are re-verified.
6. `transformation` records what was done between the source data and the plotted values:
   the filter, the aggregation, the normalisation, the units conversion — as the script
   path and its steps, or as the manual steps. `source` says what draws the figure;
   `transformation` says what the figure's numbers are numbers *of*. It is what lets a reader
   of the ledger check that the caption's claim follows from the data, which is a different
   question from whether the figure was drawn correctly. `null` is allowed for a schematic.
7. `runs` names the rows of `.paper/runs.yml` that produced the figure's numbers. It is what
   ties a claim to the code, the inputs and the tool versions behind it. A `final` figure
   with no run cannot be traced. `runs.yml` is defined in the `study-memory.md` reference of
   `research-study-design`; a project that has none leaves the field out, and the paper then
   claims no more reproducibility than `source` supports.

## terms.yml

The terminology lock. It enforces "keep terminology stable" and "define before reuse" across
sessions and across co-authors.

```yaml
version: 1
updated: "2026-08-21"

terms:
  - canonical: "melanopic equivalent daylight illuminance"
    abbrev: "mel-EDI"
    defined_at: "Sec. 2.1"
    unit: "lx"
    symbol: "E_v,mel,D65"
    never_use: ["equivalent melanopic lux", "EML", "melanopic lux", "circadian illuminance"]
    note: "EML is a different quantity with a different normalisation. Do not treat as a synonym."

  - canonical: "view direction"
    abbrev: null
    defined_at: "Sec. 2.3"
    unit: null
    symbol: null
    never_use: ["gaze direction", "observer orientation", "field of view"]
    note: "Synonyms appear in the cited literature. Quote them when quoting; do not adopt them."

symbols:
  - symbol: "E_v,mel,D65"
    means: "melanopic equivalent daylight illuminance"
    unit: "lx"
    defined_at: "Eq. 1"
  - symbol: "rho"
    means: "surface reflectance"
    unit: "dimensionless"
    defined_at: "Sec. 3.2"
```

Field rules:

1. `never_use` is the working list. Every entry is a term that means the same thing, or is
   close enough to be confused, and has been ruled out. Grep the manuscript for these.
2. `symbols` is the one-meaning-one-symbol register from `notation-and-equations.md`, Symbol
   Hygiene. A symbol appearing twice with two meanings is caught here, not by reading.
3. `defined_at` supports the definition-before-use check. A term first *used* before its
   `defined_at` location is a fault.
4. `terms.yml` is also the source for the Nomenclature block where the journal wants one.
5. This file is the reason a `never_use` term is not silently reintroduced by a later edit or a
   co-author.

## gap.yml

The verified gap from `literature-and-gap.md`, in its Gap Evidence Package form. It is written
before drafting, its `search` block is updated at each re-run, and it is what answers the reviewer who asks whether the gap is real.

```yaml
version: 1
updated: "2026-08-21"

gaps:
  - id: G1
    statement: "The effect of view direction on annual mel-EDI compliance has not been compared with the effect of climate on the same buildings."
    type: partial              # complete | partial | controversy
    status: verified           # verified | unverified | false
    rounds_run: [1, 2, 3]
    adjacent_fields_searched: ["chronobiology", "occupational health"]
    evidence:
      - cite: "Author 2021"
        page: "4"
        quote: "all evaluations assume a fixed north-facing view"
      - cite: "Author 2022"
        page: "9"
        quote: "the effect of observer orientation was not modelled"
      - cite: "Author 2023"
        page: "12"
        quote: "future work should address view-dependent exposure"
    dissenting_studies: ["Author 2020 — reports no orientation effect; address in Discussion"]
    linked_claims: ["C1"]
    search:
      databases: ["OpenAlex", "Crossref", "Semantic Scholar"]
      date_range: "2010 to 2026"
      searched_on: "2026-08-19"
      sentinels_found: "6 of 7; missed Author 2019, added by citation tracking"
      tracking_rounds: "3 rounds; new included records per round: 9, 2, 0"
```

Field rules:

1. `status: unverified` means the three-round search has not been run. The Introduction wording
   is then limited to what you can defend, and the linked claim carries `needs evidence` in
   `claims.yml`. See `literature-and-gap.md`, When the Draft Is Already Written.
2. `rounds_run` records which of the three search rounds were actually done. A gap claimed on
   round one alone is not verified.
3. `dissenting_studies` comes from the echo-chamber check and feeds `discussion.md`,
   Comparing With Literature. A dissenting study recorded here and absent from the Discussion
   is an omission a reviewer will find.
4. For a review paper, this file records the review protocol's search instead: databases and
   search date. The verbatim query strings are in `corpus/<slug>-protocol.md`. See
   `review-papers.md`.
5. `search` records the search the gap rests on. A sentence that states the gap as an
   absolute — `first`, `no prior study`, `the only` — may be written only when `databases`,
   `date_range`, and `searched_on` are all filled, and it names all three. See
   `literature-and-gap.md`, Wording a Novelty Claim. `sentinels_found` and `tracking_rounds`
   are the evidence that the search could find what exists and that it ran dry.

## reviews/

One file per review round, named by date and scope: `.paper/reviews/2026-08-21-results.md`. A
second round on the same day adds its number: `.paper/reviews/2026-08-21-results-r2.md`.

Each file holds the findings from that round, critical, important and minor, as defined in
`paper-review.md`, The finding contract, with a file and line for each, a quotation of at
most 25 words or the places searched, and the source of any field norm the finding rests on.
A fix pass adds a "Fixes applied" heading to the file of the round it answers: for each fix,
the finding it answers and the passage it changed. The purpose is threefold.

1. **Round comparison.** The reviewer of a round never reads an earlier file: it sees the
   text, not the earlier findings or the fixes. The writer reads the earlier file, after the
   new round returns, to compare the two rounds as `paper-review.md`, The loop, says.
2. **Diagnose then fix.** A fix pass reads the findings file and addresses those specific
   items, rather than editing on general principle. This is what keeps a polish pass from
   quietly undoing an earlier decision.
3. **Regression detection.** A finding that repeats one marked addressed in the earlier file
   is a regression, as `paper-review.md`, The loop, defines it. It is the manuscript
   equivalent of the `regressed` status in `responding-to-reviewers`.

Findings files are append-only in practice: never edit an old one to reflect a later fix,
except to add the fix notes of the pass that answers it. Write the next round to a new file.

## Workflow Integration

| Point in the workflow | Paper memory action |
|---|---|
| Before any task on an existing manuscript | Read `.paper/`. If absent, decide whether to create it. |
| Settling the story, before drafting | Read `question.yml` if it exists: the question, the expected answer, the closest work. |
| Drafting Methods and Limitations | Read `design.yml` if it exists: the cases with their reasons, the analysis plan, the amendments, the accepted threats. |
| Reporting a simulation setup, or writing an availability statement | Read `runs.yml` if it exists: versions, inputs and hashes come from the record. |
| Gap verification, before drafting | Write `gap.yml`. Update its `search` block at each re-run. |
| Before drafting, when `design.yml` has `planned_claims` | Seed `claims.yml`: one row for each planned claim, with `planned_claim` set and `bounded_to` started from its case sets. |
| Drafting a section | Read `terms.yml`. Add each new term as it is defined. |
| Producing or revising a figure | Update its `figures.yml` row, including `key_numbers`. |
| Any claim asserted in the Abstract, Introduction, Discussion or Conclusion | Add or update its `claims.yml` row before writing the sentence. |
| After a review run | Write `.paper/reviews/<date>-<scope>.md`. |
| Submission Gate | Run the gate against `claims.yml` and `figures.yml`, not against memory. |
| Venue chosen, before drafting | Fill the `rules` block of `venue.yml` from the guide for authors. Add the `conventions` block if a corpus of that journal's papers is available. See `venue-calibration.md`. |
| Bibliography built or changed | Run `bib_check.py refs.bib --online --record .paper/verified-refs.yml`. The author writes any `manual` row after reading the work; draft one for the author to confirm and do not write it. See `latex-mechanics.md`, Reference Identity and Notices. |
| Literature search run | The `literature-crawler` agent writes `corpus/` and merges into `gap.yml`. It never overwrites a verified gap entry. |
| Responding to reviewers | `changes.yml` in that skill reads `claims.yml`. Neither file is rebuilt. |

## Consistency Rules

These are the checks that make the files worth keeping. Run them at the Submission Gate, and
after any figure regeneration.

1. Every `supports_claims` id in `figures.yml` exists in `claims.yml`.
2. Every non-empty `evidence` entry in `claims.yml` naming a figure or table has a matching
   `figures.yml` row.
3. Every `key_numbers` value appears in the manuscript with the same digits, and every number
   the manuscript quotes from a figure appears in that figure's `key_numbers`.
4. No `figures.yml` row is `status: regenerate`.
5. No `claims.yml` row has a blank `status`, and no `gap` row lacks a `gap_reason`.
6. No `claims.yml` row's `verb` exceeds what its `status` permits.
7. No `never_use` term from `terms.yml` appears in the manuscript outside a quotation.
8. No symbol in `terms.yml` carries two meanings, and no quantity two symbols.
9. Every `gap.yml` entry linked to a claim has `status: verified`, or the linked claim is
   `needs evidence`.
10. Every `dissenting_studies` entry is addressed somewhere in the Discussion.

A failure in 1 to 6 is a Submission Gate failure. A failure in 7 to 10 is a defect to fix
before the gate is re-run.

## What This File Deliberately Omits

No progress percentages, no readiness scores, no automatic status transitions. A claim moves
from `needs evidence` to `supported` because someone produced the evidence and recorded it, not
because a pass completed. Any mechanism that can flip a status without evidence defeats the
point of the ledger.

## Checklist

1. Does `.paper/` exist, beside the manuscript, versioned with it?
2. Was it read before this task started?
3. Does every claim asserted in the Abstract, Introduction, Discussion or Conclusion have a row?
4. Does every figure and table have a row, with its `key_numbers` and `supports_claims`?
5. Is every term that has a tempting synonym locked in `terms.yml`?
6. Is the gap recorded with its evidence quotes and its verification status?
7. Do all ten consistency rules pass?
8. Was a findings file written after the last review run?
