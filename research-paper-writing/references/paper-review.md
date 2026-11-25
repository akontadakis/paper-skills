# Paper Review

**Load when:** self-review, the claim ledger, an independent review, a full pass before submission, or the Submission Gate.

**Contents:** Goal · Core Principle · Critical Rule (Do Not Violate) · What Conference Reviewers Reward · Conference Rejection Dimensions · End-of-Paper Self-Review Question List · Journal Shape: Different Rejection Dimensions · Claim Ledger · Independent Review · Pre-Submission Pass Order · Submission Gate · Claim-Strength Drift · Negative-Space Review · Adversarial Writing Workflow

## Goal

Read the draft as a hostile but fair reviewer would. Find what would get it rejected, and fix
it before submission.

## Core Principle

Assume every weak point will be found. Fixing it now costs less than defending it in a
rebuttal.

## Critical Rule (Do Not Violate)

Every major claim, above all in the Abstract and Introduction, must be:

1. technically correct, and
2. backed by evidence reported in the paper.

A claim without evidence gets the evidence, or is weakened, or is removed.

## What Conference Reviewers Reward

1. A contribution that is clearly new: a task, a pipeline, a module, a design choice, an
   experimental finding, or an insight.
2. Better results than prior methods, under a fair comparison.
3. Comparisons and ablations complete enough to trust both of the above.

## Conference Rejection Dimensions

| Rejection Dimension | Warning Signs |
| --- | --- |
| 1. Weak contribution | 1.1 The failure the paper targets is trivial, or already widely known and addressed.<br />1.2 The technique is well known, and its gain was predictable. |
| 2. Unclear writing | 2.1 Technical details are missing, so the method cannot be reproduced.<br />2.2 A module has no stated reason to exist. |
| 3. Weak experimental results | 3.1 The gain over prior methods is marginal.<br />3.2 The method beats prior methods, but its absolute performance is still poor. |
| 4. Incomplete evaluation | 4.1 Ablations are missing.<br />4.2 Strong baselines or standard metrics are missing.<br />4.3 The test cases are too easy to show that the method works. |
| 5. Unsound method design | 5.1 The setting is unrealistic.<br />5.2 The method has a technical flaw, or a step with no justification.<br />5.3 The method needs retuning for each case.<br />5.4 The limitations it adds outweigh its gain. |

## End-of-Paper Self-Review Question List

Keep these questions at the end of the draft while revising. Each "no" or "not sure" becomes a
concrete edit before submission.

### 1. Contribution

1. What does a reader know after this paper that they did not know before?
2. Does the paper remove a failure that matters, and that others have not already addressed?
3. Is the idea non-obvious to someone who knows the field's standard practice?
4. Is the gain informative, or was it predictable before the experiment?
5. Can the novelty be named as one type: task, pipeline, module, design choice, experimental
   finding, or insight?

### 2. Writing Clarity

1. Could a competent reader reimplement the method from the paper alone?
2. Does every key module have enough technical detail?
3. Does every module have a stated reason, tied to a failure in the Introduction?
4. Are terms and notation the same in every section?
5. Does every paragraph carry one message, linked to its neighbours? See `paragraph-flow.md`.

### 3. Experimental Strength

1. Is the gain over strong baselines large enough to matter, not just measurable?
2. Is the absolute performance competitive for the target venue?
3. Does the gain hold across datasets, settings and metrics?
4. Are failure cases reported as openly as successes?

### 4. Evaluation Completeness

1. Does every key design choice have an ablation?
2. Are all strong and recent baselines included, under the same protocol?
3. Are the metrics standard for the task, and sufficient?
4. Are the test cases hard enough to show that the method works?
5. Are the comparison and ablation protocols documented?

### 5. Method Design Soundness

1. Is the setting realistic for practical use?
2. Does the method hide a technical defect or an unreasonable assumption?
3. Does it work without retuning for each case?
4. Does its gain outweigh the complexity and the new limitations it adds?
5. Could a reviewer reasonably argue that its net value is negative?

## Journal Shape: Different Rejection Dimensions

Everything above is written for a conference paper, where rejection turns on contribution,
baselines, and ablations. Journal reviewers reject on different grounds. For a journal/IMRAD
paper, run **this** set instead of the five above — or both, if the paper genuinely has both
a technical contribution and an empirical study.

| Rejection Dimension | Typical Failure Signals |
| --- | --- |
| 1. Not reproducible | 1.1 Software version, parameters, or input data unstated.<br />1.2 A default silently substituted for a missing input.<br />1.3 The headline number cannot be rebuilt from the paper alone. |
| 2. Unsound method | 2.1 Model or instrument not validated for the regime used.<br />2.2 An assumption that breaks in the studied conditions, unexamined.<br />2.3 A convention with several accepted forms, never declared. |
| 3. Over-claimed (see `ethics-and-participants.md`, Bounding the Claim to the Sample) | 3.1 Conclusions exceed the sampled conditions, geometry, or population.<br />3.2 Correlation described as mechanism.<br />3.3 Abstract stronger than Results. |
| 4. Weak statistical or numerical treatment (see `statistics-reporting.md`) | 4.1 Significance without effect size, or effect without uncertainty.<br />4.2 Precision beyond what the measurement supports.<br />4.3 Aggregates whose population and denominator are unstated.<br />4.4 No convergence or sensitivity evidence for a parameter that moves the answer.<br />4.5 Separate significance results presented as a significant difference — A significant, B not, the difference itself never tested. |
| 5. Thin contribution to the field | 5.1 A parameter study with no transferable finding.<br />5.2 A case study framed as general.<br />5.3 Result already established in the literature the paper does not cite. |
| 6. Presentation (see `figures-tables.md`; `python3 scripts/extract_figures.py audit` for print legibility) | 6.1 Undefined error bars, unlabelled units, unreadable figures.<br />6.2 Results section carrying interpretation, or Discussion introducing new numbers.<br />6.3 Terminology drifting between sections. |

### Journal Self-Review Question List

**1. Reproducibility**

1. Could a competent stranger rebuild the headline number from the paper alone?
2. Are all software versions, parameters, datasets, and material properties stated?
3. Does every input value carry its provenance, and is no default worded as a measurement?
4. Have we run the full gate in `simulation-reporting.md`?

**2. Validity**

1. Is the model or instrument validated for the regime we used it in?
2. Which assumptions could break here, and did we test or bound them?
3. Is every multi-form convention declared, with the form used?
4. Is there a sensitivity or convergence check for each parameter that moves the answer?

**3. Claim Discipline**

1. Does every claim in the Abstract have a figure, table, or stated number behind it?
2. Is any conclusion drawn beyond the conditions actually sampled?
3. Is every proposed mechanism labelled as interpretation?
4. Is each limitation stated with its direction and its consequence?
4b. Is any choice made after the first results — a threshold, a climate set, a grid size, a
    metric — worded as if it were planned? See `paper-memory.md`, `analysis_status`.
5. Does every citation group actually support the specific clause it sits behind? A
   sentence carrying two claims and one citation usually supports only one of them —
   split the sentence, narrow the claim, or move the citations. Never certify support
   from a title or from memory.

**4. Numerical Treatment**

1. Does every result carry uncertainty, n, and a denominator?
2. Is precision consistent with what the measurement supports?
3. Are negative and null results reported?
4. Is the summary statistic named, along with the population it summarises?
5. Is the independent unit named behind every interval and p-value? Hours of one room, points
   of one grid, and repeated votes from one participant are not independent samples.
6. Is the meaning of every `±` stated, and is each agreement judged against a margin fixed
   before the comparison?

**5. Contribution and Framing**

1. What transferable finding does a reader take away, beyond this case?
2. Does the literature already contain this result?
3. Is the gap stated in the Introduction the gap the paper actually fills?

**6. Presentation**

1. Is every error bar defined and every axis unitted?
2. Does Results contain interpretation, or Discussion contain new numbers?
3. Is terminology identical across Methods, Results, and Discussion?

## Claim Ledger

Maintain this while reviewing. It is the structured form of the claim-evidence map in the
Output Contract, and it is what makes an unsupported claim impossible to lose track of. The rows
below show a ledger before submission; `paper-memory.md` shows the same ledger on disk after one
round of peer review.

| ID | Claim, as worded | Location | Evidence artifact | Status | Risk |
|---|---|---|---|---|---|
| C1 | View direction affects compliance more than climate | Abstract L6 | Fig. 4, Table 2 | supported | holds only for the four sampled climates |
| C2 | The 1.0 m grid does not bias results | Methods L88 | — | needs evidence | no convergence test has been run; run it or cut the claim |
| C3 | Melanopic shortfall is climate-driven | Intro L21 | Fig. 4 | rejected | Fig. 4 shows the opposite; rewrite the claim |
| C4 | Simulated depth matches real rooms | Discussion L40 | — | gap | no measurement exists for this study; state it as a limitation |

### Statuses

| Status | Meaning | Action |
|---|---|---|
| `supported` | A named figure, table, or reported number backs it | none |
| `needs evidence` | Plausible, evidence not yet produced or not yet located | produce it, or propose the weaker wording to the author |
| `gap` | No evidence exists, and a reason is stated | run the experiment, or cut the claim |
| `rejected` | The evidence contradicts the claim | rewrite the claim to match the data |

### Two Rules That Make It Work

1. **No silent gaps.** A claim with an empty evidence cell must carry `needs evidence` or
   `gap`, and a `gap` row carries its stated reason. Blank is not an allowed value. An unsupported claim must be
   typed as unsupported, never left ambiguous.

   The two are not interchangeable, and the discriminator is whether the evidence *could*
   exist:

   - **`needs evidence`** — the evidence is producible or findable, and nobody has done it
     yet. An unrun analysis, an unread literature, a number that exists in the logs but is
     not yet in the paper. The action is to produce it.
   - **`gap`** — no evidence can exist for this study as run. The data were not collected,
     the runs cannot be repeated, the instrument was not present. The action is to cut the
     claim or bound it into Limitations.

   Typing a producible claim as `gap` is the more damaging error of the two: `gap` is the
   status the Submission Gate blocks on when the claim is load-bearing, so it converts an
   unfinished task into a blocker. See `literature-and-gap.md`,
   `When the Draft Is Already Written`, for the worked case, and `paper-memory.md` for how
   the distinction is recorded on disk.
2. **Status gates the verb.** This is the one statement of the ceiling; `paper-memory.md`, the
   `claim-auditor` agent and `check_ledger.py` all follow it.

   | Status | Strongest verb the sentence may carry |
   |---|---|
   | `supported` | what the evidence ladder in `sentence-craft.md` allows for that kind of evidence |
   | `needs evidence` | `suggests`, `may`, `is consistent with` |
   | `gap` | none: state it as an assumption or a limitation |
   | `rejected` | none: rewrite the sentence to match the data |

   A `needs evidence` or `gap` claim may not use `shows`, `demonstrates`, `proves`,
   `establishes`, `confirms` or `indicates`. If the status cannot be raised, the verb must
   come down: propose the lower verb to the author (`SKILL.md`, Execution Rule 2).

   `check_ledger.py` reads the recorded `verb` field only, and flags those six barred verbs.
   Whether the sentence in the manuscript carries that verb, and any verb outside the list
   that still exceeds the ceiling, is read by `claim-auditor`, Check 2, or by the person
   running the gate.

### The Risk Column

Records why a claim is fragile even when technically supported. This is where the following
get pinned to a specific sentence rather than left as general advice:

1. Modelled, not measured — see the provenance-language table in `simulation-reporting.md`.
2. Interpretation presented as observation.
3. An alternative explanation the study did not test.
4. Scope overreach beyond the sampled geometries, climates, or population.

A supported claim with a populated risk cell usually needs a qualifier in the sentence, not
a new experiment.

### Report the Near-Misses

When reporting a language or claim audit, also list what was checked and **deliberately not
flagged**, with the reason. For example: `"tended to increase" — correct hedging for modelled
data, left as written.`

This prevents the over-editing failure mode, where every hedge gets "fixed" and correct
prose is damaged. It matters most when running the word lists in `ai-tells.md`.

## Independent Review

The checklists in this file have one structural weakness: the agent that wrote the prose is
usually the agent that then reports it clean. Self-audit rationalises its own phrasing, skips
the mechanical pass, or reports "audited" without ever running it. The result reaches the user
looking reviewed.

Four rules fix it. They apply to every non-trivial section draft and every rewrite, before
the text is shown to the user.

### 1. The evidence rule

**A report of "clean" without the raw output is not a review.** Every mechanical check pastes
its counts and its lines:

- `scripts/ai_tell_audit.py` for the AI-tell and rhythm pass, per category.
- The Pre-Submission Grep List in `latex-mechanics.md`, or the Pre-Submission Checks in
  `word-manuscripts.md`, with the hit counts shown.
- `python3 scripts/extract_figures.py audit` for figure resolution at printed size.

"Zero hits" is a valid result and is reported as zero hits, with the command that produced it.
A check that was not run is reported as **not run**, never folded into a pass.

### 2. The independence rule

The reviewer must not be the writer, and must not see the writer's self-assessment.

1. Dispatch a **fresh** agent — `claim-auditor`, `consistency-checker`,
   `bibliography-auditor`, `latex-layout-auditor`, or a general-purpose reviewer given this
   file. The figure check of item 6 is done by the general-purpose reviewer and by
   `claim-auditor`; the other three agents do not read a figure against its source.
2. Give it the artifact and the criteria, and the absolute path of this skill's folder
   (`agents-and-scripts.md`, rule 7). For the figure check, also give it
   `.paper/figures.yml` and the paths of the data and the scripts the figures rest on. Do not
   give it the claim that the text is finished, the summary of what was fixed, or the previous
   report. A reviewer told the work is done agrees with it.
3. It **re-runs the mechanical checks itself**. It does not accept the writer's counts.
4. It returns a findings list, not a verdict. "Looks good" is not an output this protocol
   accepts.
5. **It commits its criteria before it reads.** Give the reviewer the study type and the
   dimension list first, and have it write, for each dimension, what would count as a
   failure for a study of this type — a parametric EnergyPlus study, a field measurement
   campaign, a glare experiment with participants. Then give it the manuscript. A reviewer
   that reads first drifts toward whatever the manuscript makes easy to praise or easy to
   attack; criteria written first hold it to the question. If, after reading, the reviewer
   wants to grade against a criterion it did not write down, it says so and gives the reason.
6. **It opens every figure the reviewed text cites**, and reads each against its data and the
   Methods, as `figures-tables.md`, Check a Figure Against Its Source, says. A figure that
   nobody opened was not reviewed, and is reported as not checked. Only the reviewers named
   in item 1 for this check can do it.

### 3. The traceability rule

Every finding cites the rule it violates, by file and item: `sentence-craft.md` Hedging,
`ai-tells.md` T2, `paper-review.md` gate item 3, `statistics-reporting.md` triad. A finding
with no rule behind it is an opinion, and it is treated as one — recorded, not acted on
automatically.

This is what makes a fix traceable back to a decision, and it is what stops a review pass from
quietly introducing a preference as though it were a rule.

### 4. The finding contract

A finding is a record that the next reviewer, and the author, can check without re-reading
the paper. Each one carries five things.

1. **A severity, defined by its effect on the decision.**

   | Severity | Meaning |
   |---|---|
   | **critical** | By itself, it invalidates a load-bearing claim or makes the headline result unreproducible. A reviewer who saw only this would recommend rejection or major revision. |
   | **important** | It weakens a claim, or will certainly draw a reviewer comment that needs a manuscript change. The paper survives it, the claim may need bounding. |
   | **minor** | Everything else: presentation, wording, a typo, a missing unit in one caption. |

2. **Each finding earns its own grade.** A finding is never raised a level because other
   findings sit beside it. Two typos next to a missing validation do not make the validation
   more serious, and five minor findings do not sum to a critical one. If a defect needs its
   neighbours to matter, it is not critical alone.
3. **A quotation of at most 25 words** from the manuscript, with its location, for a finding
   about something that is on the page. The quote is what lets the author find it and the
   next reviewer confirm it. A finding with no quote and no location is an impression.
4. **For a finding about something absent, the places searched.** "The paper does not report
   the ambient bounce count" is recorded with where the reviewer looked: `searched Methods
   2.3, Table 2, Supplementary S1`. An absence finding with no search record cannot be told
   from a reviewer who did not read far enough. This is the record that the Negative-Space
   Review below must leave.
5. **For a finding that rests on a field norm, the norm and its source.** "The field
   requires X" is a claim about the field. Name the norm, and name where it comes from: a
   rule in this skill's reference files, cited by file and section as the traceability rule
   requires; a standard and its edition; the journal's guide for authors; a reporting
   guideline; or the convention recorded in `.paper/venue.yml`. A norm the reviewer cannot
   source from any of these is recorded as **minor** and marked `norm not verified`, whatever
   its apparent weight.

   A finding that cites a rule of this skill is already sourced and is graded on its effect.
   A missing convergence test, a bare p-value behind an Abstract claim, and a default worded
   as a measurement are faults this skill names, and they keep the severity its rules and
   the Submission Gate give them. This item downgrades only the norm that comes from nowhere.

   This is the commonest fault of a model acting as reviewer: it applies the expectations of
   another field. Random seeds and a held-out test set are norms of machine-learning
   evaluation. A deterministic EnergyPlus parametric study has neither, and their absence is
   not a defect. Trial registration is a norm of clinical research. A reviewer that imports
   them invents rejection risks the journal's own reviewers would never raise. The detection
   is still reported; only its severity waits for a source. Once a source is supplied, the
   finding is graded on its own effect like any other, by the table in item 1.

Confidence is recorded separately from severity and never changes it. `critical, low
confidence — could not open the supplementary file` is a valid and useful finding. Lowering
the severity because the reviewer is unsure hides the finding; raising it to be safe
inflates the list.

### The loop

Terms:

- A **version** is a saved state of the text: v0 is the text before any fix, v1 the text after
  the first fix pass, v2 after the second. Save each as a commit or a dated copy.
- A **round** is one review of one saved version: the mechanical checks with pasted output,
  then a fresh reviewer that sees neither the earlier findings nor the fixes. There are at most
  three rounds, so at most two fix passes. Only a reviewed version can be kept.

Steps:

1. Write the text and save it as v0.
2. Round 1. Run the mechanical checks on v0 and paste the output. Dispatch the independent
   reviewer, without the self-assessment. Write its findings, each in the form of the finding
   contract, to `.paper/reviews/<date>-<scope>.md`.
3. After every round, stop when it returned no critical and no important finding and step 6
   put no earlier finding back on the list: keep that version. Give the minor findings, and
   every line reported as not checked (a figure nobody opened, a check that did not run), to
   the author as open items. After round 3, go to step 8. Otherwise go to step 4.
4. Fix pass. Start from the current text: the version just reviewed, with any passage or pass
   that step 6 or 7 undid restored from the previous version. Fix every finding on the list in
   **one** pass, not one pass per finding. Save the result as the next version. Write a "Fixes applied" heading
   in that round's file, and under it, for each fix, the finding it answers and the passage it
   changed.
5. Next round. Run step 2 on the new version, with a fresh reviewer, and write its findings to
   a new file for the same scope. A second round on the same day adds its number to the file
   name: `<date>-<scope>-r2.md`, then `-r3`. No round overwrites an earlier file.
6. Compare the two rounds. The writer does this, from the two files; the reviewer does not see
   the earlier file. There is no score: a number invites edits made to raise it. Count the
   critical, important and minor findings of each round. Then test each finding of the new
   round against the previous version, in this order:
   - It repeats a finding that was marked addressed. That is a regression. Fix it first.
   - The fault is in the previous version too. The earlier reviewer missed it. It goes on the
     list as a new finding and is not counted against the fix pass.
   - The fault is not in the previous version, and it sits in a passage the fix pass changed.
     The fix introduced it. Undo that fix when that finding is critical or important: restore
     the passage from the previous version, put the earlier finding back on the list as open,
     and fix it again, more narrowly, in the next fix pass. Never patch the patch: a fix
     written on top of a faulty fix carries the fault forward. When the introduced finding is
     minor, the fix stays and the finding goes on the list.
   - Anything else is a new finding, and it goes on the list.
7. Undo the whole fix pass only when it introduced more critical findings than it resolved, or
   as many critical findings and more important ones. Count the introduced findings from the
   third item of step 6, and the resolved ones from the earlier findings that the new round did
   not raise again. A good fix is never undone only because another fix in the same pass was
   bad. Undoing returns the text to the previous version and puts every finding of that pass
   back on the list as open. A restarted fix pass is the next fix pass, not an extra one. Text
   that was undone or restored is reviewed in the next round. Then go back to step 3.
8. After round 3 there is no fix pass. Keep the version, among the reviewed ones, with the fewest critical findings, then the fewest
   important ones, counting for each version every finding from any round that applies to it. Give the
   remaining findings, and every line reported as not checked, to the author as open items.

Do not run this on a single-paragraph edit. It is for a section draft, a substantial rewrite,
and the pre-submission pass.

## Pre-Submission Pass Order

This order is for a full pass on a finished draft. A single task loads only its own guide; see
`SKILL.md`, What to Load.

1. `paper-memory.md`. Read `.paper/` first.
2. `submission-package.md`, Journal Selection, if the venue is not fixed yet. The venue sets the
   paper shape.
3. `literature-and-gap.md`.
4. `venue-calibration.md`, once the venue is chosen. Fill the `rules` block of `.paper/venue.yml`
   from the guide for authors; this needs no corpus. Build the `conventions` block only when a
   corpus of that journal's papers is available. Venue calibration sets convention. It never
   overrides claim discipline, statistics, units, provenance, or ethics.
5. The section guides for the shape. Use `statistics-reporting.md`, `ethics-and-participants.md`,
   `notation-and-equations.md`, `figures-tables.md` and, for a modelling study,
   `simulation-reporting.md` with the sections that carry them.
6. `sentence-craft.md`, then `ai-tells.md`.
7. For a modelling study, the Pre-Submission Gate of `simulation-reporting.md`. This is a
   re-check. A failure found this late forces Methods edits that undo the sentence-level
   passes, which is why step 5 uses that guide while Methods is drafted.
8. `latex-mechanics.md` or `word-manuscripts.md`, whichever the manuscript is written in.
9. `reporting-checklists.md`, when a reporting guideline applies.
10. This file, on the whole manuscript: the claim ledger against the text, Claim-Strength Drift
   (always before a resubmission), Negative-Space Review, and The loop of Independent Review.
11. The Submission Gate below.
12. `submission-package.md` for the portal metadata, once the gate passes.

Each step assumes the one before it is settled.

## Submission Gate

A single verdict on the whole package, drawn from gates owned elsewhere. Run it last.

Blocked from submission while any of these holds:

1. The claim ledger contains a row with status `rejected`.
2. A `gap` row carries a claim that is load-bearing for the contribution. A `gap` on a
   bounded, disclosed limitation is **not** a blocker — it belongs in Limitations, stated
   with its direction and consequence, and the paper ships. A `gap` row with no `load_bearing`
   is treated as load-bearing (`paper-memory.md`, claims.yml field rule 5).
3. Any Abstract claim is not `supported`. When `claims.yml` exists, an Abstract claim with no
   row counts as not supported. When there is no `claims.yml`, this item is not run.
4. The `simulation-reporting.md` gate has not been run, **or has been run and does not pass**,
   for any study whose results come from a physics or simulation engine. Running a failing
   gate does not satisfy this item. ML training alone does not trigger this item (see
   `simulation-reporting.md`, When This Gate Applies); a pipeline embedding a physics engine does.
5. The placeholder and residue greps return any hit. For a Word manuscript use the
   Pre-Submission Checks in `word-manuscripts.md` and read items 5 and 6 here as their `.docx`
   equivalents: the field-update and error-marker searches in place of the source greps, and
   `Error! Reference source not found` in place of `??`. For LaTeX, use `latex-mechanics.md`.
   Source-side:
   `[CITE:`, `[insert` with a small or a capital I (`[Insert citation]` too), `\todo`, `TODO`,
   `FIXME`, `XXX`, and the chat-residue phrases.
   `[insert` is the bracket the Revision Contract leaves for a missing fact. Read every other
   square bracket that is not a citation too: a missing fact marked in another form is the
   same fault. PDF-side, when
   a compiled PDF exists: `??` and `[?]`. All must be zero.
   The `.log` and `.blg` greps are **not** part of this gate — a real run almost always
   produces an `Underfull \vbox` or a benign `.blg` warning. Those are triaged, not zeroed.
6. Reference integrity fails on the **source**, checkable without a compiled PDF:
   - a `\ref`, `\cref`, `\Cref`, `\eqref`, `\autoref`, `\pageref`, `\vref` or `\cpageref` key
     with no matching `\label`: the `comm` commands in the
     `latex-mechanics.md` Pre-Submission Grep List;
   - a `\cite` key with no matching `.bib` entry: `python3 scripts/bib_check.py refs.bib
     --tex main.tex` (`BIB_CITED_NOT_DEFINED`);
   - a referenced float that does not exist;
   - a manuscript with no bibliography at all: the `no bibliography command found` command of the
     same list.
   These are structural failures, not authored placeholders, so item 5 does not catch them.
   See `latex-mechanics.md` Parts 1 (bibliography) and 2 (cross-references). For a Word
   manuscript the equivalent failures are a typed citation that does not renumber, a typed
   cross-reference, a duplicate reference-manager entry, and a reference list whose count does
   not match the distinct citations in the text. See `word-manuscripts.md` Parts 1 and 2.
7. A convergence- or resolution-sensitive parameter has no convergence evidence — or, the
   ML analogue, a hyperparameter tuned per dataset or per scenario has no sensitivity
   evidence and its tuned values are unreported.
8. A default, inferred value, or model output is worded as a measurement anywhere.
8b. Any gate item in this list is claimed as passing without the output that shows it. See
   `Independent Review`, the evidence rule. A check reported as "not run" does not block on
   its own, and it makes the verdict `incomplete`, never `not blocked`; a check reported as
   passing with no evidence blocks.
9. Any of paper-memory consistency rules 1 to 6 fails: a `supports_claims` id with no claim, an
   evidence cell naming a figure with no `figures.yml` row, a `key_numbers` value that does not
   match the prose, a cited figure still marked `status: regenerate` or `status: draft`, a
   blank status or a `gap` with no reason, or a verb stronger than its status permits. See
   `paper-memory.md`. Run this against the files, not against memory. Rule 6 is read against
   the sentence at each claim's `location`: `check_ledger.py` reads the recorded `verb` field
   only. Rule 3 is read against each figure: the script accepts a quoted number found in any
   `key_numbers` entry, a table, the Results or the Methods. If the manuscript has no
   `.paper/`, this item is reported as not run — which is itself a finding, not a pass.
10. A study involving people, personal data, or images of occupants has no ethics statement
   naming the approving body, the protocol identifier, and the date, or has no consent
   statement. This blocks at the editor's desk before a reviewer sees the paper. A declared
   exemption or a stated reason for no approval satisfies the item; silence does not. See
   `ethics-and-participants.md`.
11. The journal requires a reporting checklist, or the manuscript says it follows a reporting
   guideline, and `.paper/checklist-<name>.md` is missing or has a row with no disposition.
   A paper for which no guideline applies and none is claimed does not trigger this item. See
   `reporting-checklists.md`.
12. A value in the `rules` block of `.paper/venue.yml` is `null` — not yet checked — or the
   manuscript breaks one: a word or abstract limit, the reference style, the figure
   resolution. `"none stated"` is a checked answer and does not block. If no venue
   has been chosen, this item is reported as not run. See `venue-calibration.md`.
13. A cited work carries a retraction notice and is cited as support, or a DOI resolves to a
   different work than its entry describes. Both come from `python3 scripts/bib_check.py
   refs.bib --online`. "Not checked" does not block on its own; a notice that was found and
   ignored does. A cited key that `.paper/verified-refs.yml` does not cover blocks too: run
   `python3 scripts/bib_check.py refs.bib --tex main.tex --verified .paper/verified-refs.yml`.
   A manuscript that cites works and has no list fails this item as "fail: no verified list",
   unless the author records a waiver. A `doi` row shows identity, not support: a citation
   also needs the manuscript, the brief or `.paper/` to show that the work supports the
   sentence. For a Word manuscript, the comparison of the cited items with the list is done
   by hand and reported as a manual check, never as a script pass. See `latex-mechanics.md`,
   Reference Identity and Notices, and `word-manuscripts.md`, Part 1.
14. A `final` figure or table rests on no `valid` run, or a recorded input, code or output
   file has changed since its run. When `.paper/runs.yml` exists, run `check_provenance.py`,
   in the `scripts/` folder of the `research-study-design` skill, and paste its output. For a
   run behind a `final` figure, the script reports a recorded file that is missing, or a row
   with no hash, as a finding. It reports a run with no recorded inputs, or with neither code
   files nor a commit, as "not checked". That is not a pass either: report this item as fail and
   name the row. It cannot pass until the row records its inputs and its code. If the study has
   no `runs.yml`, this item is reported as
   not run, and the manuscript claims no more reproducibility than its `figures.yml` `source`
   fields support.
15. A choice made after the results is worded as planned. When `.paper/design.yml` exists,
   every amendment with `timing: post hoc` is stated in Methods as made after the results,
   with the result under the old setting reported beside the new one, whether the amendment is
   of `kind: choice` or of `kind: correction`. For one with `kind: choice`, each claim whose
   `planned_claim` it affects is `analysis_status: post hoc` and labelled exploratory. When no
   dated design exists, the manuscript does not say `planned`, `pre-specified` or `a priori`
   of any choice.
16. A sentence claims a gap or a first, and the search behind it was not re-run for this
   submission: `searched_on` in `.paper/gap.yml` is earlier than the day this pre-submission
   pass began. When no record shows that day, ask the author. Re-run the search and update
   `searched_on`; the sentence then names the new date. See `literature-and-gap.md`, Wording a
   Novelty Claim, rule 5.

**Verdict.** The gate report ends in one of three words. `blocked`: at least one item fails.
`not blocked`: every item passes or carries a recorded waiver. `incomplete`: no item fails,
and at least one item was not run; name those items. A manuscript with no `.paper/claims.yml`
gives `incomplete`, never `not blocked`, because items 1, 2, 3 and 9 cannot be decided.

### Waivers

An author may decide to submit with a known blocker. Record it — never silently clear it.

`Blocker | Who decided | Reason | Remaining risk`

A waiver is never converted into a pass, and it is never dropped from the record because the
draft looks finished. If the waived item touches the science, it belongs in Limitations too.

Do not award the paper a readiness label or a numeric score. The verdict is one of the three
words above, and the reasons are the useful output.

## Claim-Strength Drift

A revision changes verbs. A reviewer asks for a weaker claim and it is weakened; a later
polish pass, reading for flow, turns `suggests` back into `shows`. Or the reverse: an edit
made under deadline hedges a result the data fully support. Both are silent changes to what
the paper claims, and neither shows up as a changed number.

Run this after any revision pass that touched the Abstract, the Introduction, the Discussion,
or the Conclusion, and always before a resubmission.

1. For every claim the revision touched, compare the verb before and after against the
   ladder in `sentence-craft.md`, Hedging. `scripts/check_revision_tokens.py` lists the
   hedging verbs a revision removed and added; it is the mechanical first pass.
2. A move in **either** direction is reported: stronger or weaker.
3. Each move gets exactly one decision, recorded in the claim's ledger row:

   | Decision | When |
   |---|---|
   | **restore** | The move was not intended. Put the earlier verb back. |
   | **keep, with the reason** | The move is intended and the evidence status supports it: new evidence was added, or a reviewer's comment was conceded. Record which. |
   | **pause** | The author must decide. The sentence is flagged and the revision is not reported as finished. |

   There is no fourth option. A changed verb that is simply left in place is a decision made
   without anyone making it.
4. A verb moved up the ladder needs the ledger status to have moved with it. `needs evidence`
   does not become `shows` because the sentence reads better.
5. In a reviewer response, record the decision in the comment's row as well —
   `claim_verb_change` in the `change-ledger-file.md` reference of `responding-to-reviewers`.

## Negative-Space Review

The checklists above test what is on the page. This tests what is missing. Run it on the
near-final draft. Every finding from this section records where it looked — the finding
contract, item 4.

1. **A question with no answer** — raised in the Introduction, never resolved.
2. **A method with no result** — described in Methods, never reported.
3. **A result with no method** — reported in Results, never described in Methods.
4. **An assumption never stated** — required for the analysis to hold, absent from the text.
5. **A title broader than the outcome** — the paper delivers less than the title promises.

### Symmetry of Reported Fields

Where three or more entities should be reported the same way, build a completeness matrix:
entities as rows, reported fields as columns. Any empty cell is either a real omission or
needs a stated reason.

Entities that must be reported symmetrically: climates, sites, view directions, orientations,
luminaires, glazing assemblies, scenarios, models, datasets, baselines, ablation conditions.

- ✗ Three of four climates report their weather-file provenance; the fourth does not.
- ✗ Three luminaires report mel-DER; the fourth reports only photopic output.

### Unknown Is Not Zero

An unreported runtime, failure count, excluded run, or missing measurement stays **unknown**.
It never becomes a zero, a blank cell read as zero, or an omission the reader will interpret
as "none occurred". If a run failed or was excluded, say so and say why — see
`simulation-reporting.md`.

## Adversarial Writing Workflow

1. Read the paper as a skeptical reviewer.
2. Pick the question list that matches the paper shape — the five conference dimensions, or the six journal dimensions.
3. Answer every question with explicit evidence from the paper.
4. Record each failed answer as a finding of the finding contract, with its severity: critical, important or minor.
5. Fix claims, writing and method scope. A finding that needs a new experiment is given to the author as an open item, and the claim it touches is bounded or cut until the experiment exists.
6. Review again as `The loop` says: at most three rounds, then stop.
