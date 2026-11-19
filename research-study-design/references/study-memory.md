# Study Memory

**Load when:** you write or read `question.yml`, `design.yml` or `runs.yml`, or you need to know which later step reads them.

**Contents:** Goal · Where the Files Live · question.yml · design.yml · runs.yml · Who Reads Each File Later · Consistency Rules · Checklist

## Goal

Keep the decisions of a study on disk, with their dates, from the first idea to the last run.
The paper is written months later, often in another session. What was planned, what was
changed, and which run produced which number must not depend on anyone's memory.

## Where the Files Live

In `.paper/`, in the project's top folder. At the idea stage no manuscript exists, so this
skill creates the folder there. It is never moved. `research-paper-writing` looks beside the
manuscript first and then in each folder above it, and uses the first `.paper/` it finds. Its
`references/paper-memory.md` owns the folder as a whole and lists every file in it.

```
<project>/
  .paper/
    question.yml    the research question, its possible answers, the go or stop decision
    design.yml      the study design, frozen with a date, and every later amendment
    runs.yml        one row per run: code, inputs, tool versions, outputs, status
```

Rules:

1. The files are working records. They are never submitted.
2. A decision is written when it is made, with its date. Never rewrite an earlier entry to match
   a later decision; add an amendment. The one allowed change to an existing run row is marking
   the run `superseded`, with `record_run.py --supersede`; it changes only `status`,
   `superseded_by` and `reason`.
3. A slot with no source stays a bracket that starts with `insert`. An empty or bracketed slot
   is an open item, and the files show how many remain.
4. The examples below use one invented study, the journal study that runs through the
   `research-paper-writing` guides. They add invented planning details that those guides do
   not hold: its origin, its dates, its runs. Angle brackets mark a value left open. They are
   not a format to copy.

## question.yml

```yaml
version: 1
updated: "2026-02-20"

question:
  text: "In side-lit offices, does the occupant's view direction change melanopic daylight compliance more than the climate does?"
  outcome: "compliant plan depth"
  comparison: "best-case against worst-case view direction, beside the spread across climates"
  conditions: "side-lit offices, European climates, seated eye height"

origin: "While a design was checked against a melanopic target, the result changed when the view direction of the sensor was changed."

answers:
  - if: "view direction changes compliant plan depth more than climate does"
    paper: "horizontal-workplane metrics may overstate the daylight occupants receive"
    reader_acts: "a designer who assesses a melanopic target states and checks the view direction"
  - if: "climate changes it more"
    paper: "one fixed view direction is an adequate simplification for these rooms"
    reader_acts: "a designer keeps the simpler assessment"
  - if: "the two effects are of similar size"
    paper: "neither can be held fixed; both are reported"
    reader_acts: "a designer reports both"

expected_answer: "view direction changes it more"
expected_answer_on: "2026-02-20"
contribution: "A simulation study of whether the view direction of the sensor or the climate changes the compliant plan depth of side-lit offices more, in 24 geometries and four European climates."
contribution_type: finding   # finding | method | dataset | validation | replication | negative result | review

closest_work:
  - cite: "Author 2021"
    did: "annual melanopic compliance with one fixed view direction"
    difference: "this study varies the view direction on the same buildings"
    read: true
  - cite: "Author 2022"
    did: "compliance across climates and geometries on a horizontal workplane"
    difference: "this study assesses at the eye and compares view direction with climate"
    read: true
gap: "G1"                    # the id in gap.yml; `unverified` there until the recorded search has run

feasibility:
  data: "weather files for four climates"
  tools: "Radiance"
  time: "[insert the run time of one geometry and climate, from the pilot]"
  ethics: "not applicable: no participants"
  smallest_version: "one geometry, two climates, two view directions"

decision:
  status: go                 # exploring | go | narrowed | stopped
  date: "2026-02-20"
  reason: "Each of the three answers gives a paper."
```

Field rules:

1. `question.text` names an outcome, a comparison and the conditions. A topic ("melanopic
   daylight in offices") is not a question.
2. `answers` lists every answer the study could give. Each has the paper it would make and what
   a named reader would do differently. If every answer leads to the same action, the question
   is not sharp yet. If only one answer gives a paper, record that as a risk in
   `decision.reason`.
3. `expected_answer` is the researcher's own, written before any run, with the date in
   `expected_answer_on`. It lets a result be called expected or surprising.
4. `closest_work` holds the nearest three to five papers, each with what it did and how this
   study differs. `read: false` marks a paper known only from a title, an abstract or memory.
   Such an entry is a lead. It supports no claim. An entry with `read: true` is one of the
   first sentinel papers of the literature search and a candidate for evidence in `gap.yml`.
5. `gap` points into `gap.yml`. A gap stays `unverified` until the search in
   `literature-and-gap.md` has run and is recorded.
6. `contribution` is one sentence in the form the Abstract needs. `contribution_type` is named
   honestly. A replication is `replication`.
7. `decision.status` is the researcher's decision. `stopped` and `narrowed` are good outcomes
   of this stage, and each needs its `reason`.

## design.yml

```yaml
version: 1
updated: "2026-08-08"
design_type: "comparative simulation study"
frozen_on: "2026-03-02"
frozen_commit: "<commit id of the frozen file, when the project is under version control>"

planned_claims:
  - id: P1
    text: "View direction changes compliant plan depth more than climate does."
    evidence_needed: "mean compliant plan depth for the best- and worst-case view direction, and the range of the four climate means"
    would_change_conclusion: "the reduction from best to worst view direction is smaller than the spread across climates"
    no_difference_margin: "one grid spacing: the depth is read on the grid and cannot resolve less"

factors:
  - name: "view direction"
    levels: "8 directions at each desk; the best and the worst case are kept"
  - name: "climate"
    levels: 4
  - name: "room geometry"
    levels: 24
held_constant:
  - "seated eye height, 1.2 m"
  - "[insert the glazing and the surface properties, with their sources]"

cases:
  - set: "climates"
    members: "[insert the four climate names and their weather files]"
    reason: "[insert what the four span, and what each contrasts with]"
    bounded_to: "four European climates"
    contrast_case: "[insert the climate most likely to reverse the result, or state that none is included]"
  - set: "geometries"
    members: "24 side-lit office geometries"
    reason: "[insert how the 24 were generated]"
    bounded_to: "side-lit offices"

unit:
  analysed: "one geometry in one climate"
  independent: "room geometry"
sample_size:
  basis: "full enumeration"  # power | precision | feasibility | full enumeration
  note: "With fixed inputs and settings the runs repeat, and the 24 geometries are not a sample of a population. The researcher chose to plan no test."

ethics: {board: "not applicable: no participants"}

pre_run_checks:        # status: done | not done | not planned | not possible
  - check: "ambient-parameter convergence, on the deepest room"
    status: not done
    note: "to be run on the deepest room before the first production run"
  - check: "run-to-run spread: one case repeated"
    status: not done
    note: "to be run on one case, repeated with nothing changed"
  - check: "grid convergence at 1.0 m, 0.5 m and 0.25 m"
    status: not planned
    note: "not planned at the freeze"
  - check: "validation against measurement"
    status: not possible
    note: "no measured rooms are available to this study"

analysis:
  outcome: "compliant plan depth: the distance from the window to the deepest desk with melanopic EDI of at least 250 lx for at least 50% of occupied hours (08:00-18:00)"
  summary: "mean over 24 geometries and four climates, for the best- and the worst-case view direction"
  comparison: "difference of the two means, beside the range of the four climate means"
  test: "none"
  failed_or_excluded_runs: "counted and reported with the reason; never dropped silently"
  # optional, for studies with participants or measurements: primary_outcome,
  # secondary_outcomes, exclusion_rules, stopping_rule

threats:
  - threat: "no validation against measurement"
    decision: accept          # remove | reduce | accept
    consequence: "every result is a model output; stated in Limitations"
  - threat: "four climates"
    decision: accept
    consequence: "the claim is bounded to the four"
  - threat: "grid convergence not tested before the production run"
    decision: accept
    consequence: "the depth is read on the grid, so it cannot resolve less than one grid spacing; stated in Limitations"
  - threat: "the best and the worst view direction are kept per desk from the same simulations that are then compared"
    decision: reduce
    consequence: "the selection overstates the difference between directions, in the direction of the expected answer; [insert how the selection is reported]"

amendments:
  - id: A1
    date: "2026-08-08"
    what: "analysis grid changed from 1.0 m to 0.5 m; all results rerun"
    why: "reviewer comment R1.1; the convergence test showed a 6.9% change between 1.0 m and 0.5 m"
    timing: post hoc          # changed before analysis | post hoc
    kind: correction          # correction | choice
    forced_by: "grid-convergence test of 2026-08-07: the 1.0 m grid had not converged"
    old_result: "worst-case mean compliant plan depth 2.9 m at 1.0 m; 3.1 m at 0.5 m"
    affects: ["P1"]
```

Field rules:

1. `frozen_on` is the date the design stopped changing freely. `frozen_commit` is the commit id
   of the frozen file, where the project is under version control: a typed date alone cannot be
   checked. It is on or before the date of
   the first production run in `runs.yml`. Without it, nothing in the file may later be called
   planned.
2. Each `planned_claims` row is a sentence the researcher hopes to write, with the evidence it
   needs, the result that would refute it, and the margin below which a difference counts as
   no difference. A row with no `would_change_conclusion` describes a study that cannot fail.
3. Each `cases` row gives the reason for the set, the limit it puts on the claim, and a contrast
   case or the statement that there is none. "The files were at hand" is an honest reason. It
   is written as the reason, and it limits the claim.
4. `unit.independent` decides what any n counts. Hours of one room and points of one grid are
   not independent.
5. `sample_size.basis` is `power` with the smallest effect of interest and its source,
   `precision` with the widest interval that still answers the question and its source,
   `feasibility` with the smallest effect that n can detect, or `full enumeration`. An effect
   size with no source is a bracket.
6. `pre_run_checks` lists each check with its `status`: `done`, `not done`, `not planned` or
   `not possible`. The detail goes in `note`. `status` is the state at the freeze; a check run
   later is a run of `kind: check` in `runs.yml`. `not possible` and `not planned` are allowed
   and are stated; each then appears under `threats`.
7. `threats` records each threat with one decision. An accepted threat goes into the
   Limitations paragraph later, in the same words.
8. `amendments` is append-only. `timing` is `changed before analysis` when no result had been
   seen, and `post hoc` when one had. These are the words `claims.yml` uses for
   `analysis_status`. An amendment dated after the first production run is `post hoc`, unless
   it carries `results_seen: false` and the reason.
9. `kind` says what a `post hoc` amendment did to the claims in `affects`. A `choice` picked
   among alternatives after results were seen: a threshold, a case set, a metric, a subgroup.
   Each claim it affects becomes `analysis_status: post hoc` and is reported as exploratory.
   A `correction` repaired a fault that a check exposed: a setting that had not converged, a
   wrong input file, a bug. It names the check in `forced_by` and gives the result under the
   old setting in `old_result`. The claims keep their status; Methods still report the change
   and its date. A change that could have gone either way is a `choice`. Every `post hoc`
   amendment, of either kind, gives the result under the original choice in `old_result`.
10. `affects` lists `planned_claims` ids. Before drafting, each planned claim gets one row in
    `claims.yml` with `planned_claim` set, so an amendment can be followed to the sentences it
    touches.
11. A claim's `bounded_to` in `claims.yml` starts from the `bounded_to` of every case set the
    claim rests on.
12. `ethics` holds `board`, `reference` and `date` when people take part. A study with no
    participants says so in one line, as in the example. The four optional `analysis` fields
    are fixed before the first session or measurement.

## runs.yml

```yaml
version: 1
updated: "2026-08-12"

release:                  # above `runs:`, which stays the last key
  repository: "[insert the repository]"
  identifier: "[insert the DOI of the deposit]"
  licence: "[insert the licence]"
  withheld: "[insert what is not released, and why]"

runs:
  - id: R1
    date: "2026-04-14"
    kind: production          # pilot | check | production
    purpose: "production run, 1.0 m grid"
    command: "<the command that started the run>"
    code:
      commit: "<commit id>"
      dirty: false
      files:
        - path: "code/run_all.py"
          sha256: "<hash>"
    inputs:
      - path: "configs/main.yml"
        sha256: "<hash>"
    tools:
      - name: "Radiance"
        version: "<the version string the tool prints>"
    seed: null                # one seed per row
    # optional: hardware, wall_time
    outputs:
      - path: "results/annual_1000mm.csv"
        sha256: "<hash>"
    status: superseded        # valid | superseded | failed | excluded
    superseded_by: "R3"
    reason: "Replaced after the grid-convergence test, amendment A1."

  - id: R2
    date: "2026-08-07"
    kind: check
    purpose: "grid-convergence test at 1.0 m, 0.5 m and 0.25 m"
    status: valid             # the other fields as in R1

  - id: R3
    date: "2026-08-12"
    kind: production
    purpose: "production run, 0.5 m grid"
    command: "<the command that started the run>"
    code:
      commit: "<commit id>"
      dirty: false
    inputs:
      - path: "configs/main_500mm.yml"
        sha256: "<hash>"
    tools:
      - name: "Radiance"
        version: "<the version string the tool prints>"
    seed: null
    outputs:
      - path: "results/annual.csv"
        sha256: "<hash>"
    status: valid
```

Field rules:

1. One row per run, or per batch that shares one command, one code version and one set of
   inputs. A row holds one `seed`: record one row per seed. `record_run.py` writes the row and
   computes the hashes; `hardware` and `wall_time` are optional text fields.
2. `code.files` lists each code file with its hash. `code.commit` is the version-control
   commit, when the project has version control; `dirty: true` means files had changed since
   that commit, so the commit alone does not identify the code. `dirty: null` means the script
   did not look, as when no `--code` path was given. `kind` separates a `pilot` and
   a `check`, such as a convergence test, from a `production` run. The design freeze must
   come on or before the date of the first production run.
3. `tools` holds the version string each tool prints, copied and not remembered. A version
   nobody checked is a bracket.
4. `status: valid` is the only status a figure may rest on. `superseded` names the run that
   replaced it: `record_run.py --supersede R1 --by R3 --reason "..."` sets `status`,
   `superseded_by` and `reason` of the old row, once the replacing run is recorded. It is the
   one allowed change to an existing row. `failed` and `excluded` carry a `reason`. No run is
   ever deleted: a run that vanished from the record is a result nobody can account for.
5. `release` is a top-level block above `runs:`: where the code and data are deposited, the
   identifier, the licence, and what is withheld and why. The scripts keep it as it is.
6. A figure names its runs in `figures.yml`, in a `runs` list. That closes the chain: claim,
   figure, run, code and inputs.

## Who Reads Each File Later

| File | Read by | For |
|---|---|---|
| `question.yml` | `research-paper-writing` | the `contribution` sentence, the Introduction's gap and aim, `closest_work` as the first sentinel papers of the search and rule 8 below |
| `design.yml` | `research-paper-writing` | Methods (design, cases, analysis), Limitations (accepted threats), the first `claims.yml` rows (one per planned claim), `analysis_status` and `bounded_to` in `claims.yml` |
| `design.yml` | `responding-to-reviewers` | "why these cases?" and "was this planned?" are answered from the record |
| `runs.yml` | `research-paper-writing` | the simulation reporting block, the data and code availability statement, the Submission Gate |
| `runs.yml` | `responding-to-reviewers` | an analysis run for a reviewer is a new row, and its design change is a `post hoc` amendment |

## Consistency Rules

`python3 <skill folder>/scripts/check_provenance.py <project folder>` checks rules 1 to 6. Rules 7 and 8 need
a reader. `figures.yml`, its `final` status, `claims.yml` and `gap.yml` are defined in the
`paper-memory.md` reference of `research-paper-writing`.

1. Every `final` row in `figures.yml` names at least one run, and each named run exists.
2. Every run a `final` figure rests on has `status: valid`.
3. Each recorded input, code and output file of a `valid` run still has its recorded hash. A
   file that changed after the run makes the run stale: rerun it, or record a new run. For a
   run a `final` figure rests on, a recorded file that is missing and a row with no hash are
   findings, and a run with no inputs, or with neither code files nor a commit, is reported as
   not checked. For another run, a missing file or hash is reported as not checked.
4. A `failed`, `excluded` or `superseded` run has its `reason`, and a `superseded` run names an
   existing run in `superseded_by`.
5. `frozen_on` in `design.yml` is on or before the date of the first production run.
6. Every amendment dated after the first production run has `timing: post hoc`, or carries
   `results_seen: false` with the reason in a `reason` field.
7. A claim whose `planned_claim` is affected by a `post hoc` amendment of `kind: choice` has
   `analysis_status: post hoc` in `claims.yml`, and is worded as exploratory.
8. A `closest_work` entry with `read: false` is cited nowhere as support.

## Checklist

1. Does `question.yml` hold a question with an outcome, a comparison and conditions?
2. Does each possible answer have its paper and its reader?
3. Is `design.yml` frozen with a date that precedes the first production run?
4. Does each planned claim say what result would change the conclusion?
5. Does each case set give its reason, its limit on the claim and its contrast case?
6. Is every change after the freeze an amendment with a date and a timing?
7. Does each `final` figure name a `valid` run whose files still match their hashes?
8. Are the brackets that remain listed for the researcher?
