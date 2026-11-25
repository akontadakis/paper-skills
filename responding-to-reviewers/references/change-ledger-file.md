# Change Ledger File

**Load when:** building or checking `.paper/changes.yml`, and at the start of a second round.

**Contents:** Goal · Why This Exists · Where It Lives · Three Layers of Evidence · The Ledger as Shown to the Author · Statuses · Schema · Field Rules · Round Two · Cross-Checks · Handing Back to the Manuscript · Checklist

## Goal

Keep the change ledger on disk, so a round-two response can audit round one instead of trusting
it.

## Why This Exists

The change ledger in this skill's `SKILL.md` is the mechanism that keeps the response letter
and the revised manuscript in agreement. It has one weakness: it lives in the conversation. By
the time round two arrives — often months later, often in a new session, sometimes with a
different co-author driving — the ledger is gone, and the only surviving record of what was
promised is the response letter itself.

That is exactly the record you must not trust. A response letter is layer 2 evidence: what you
said you did. See Three Layers of Evidence below.

`.paper/changes.yml` keeps layer 3 — the verified change, with its location — so round two
starts from what the manuscript actually contains.

## Where It Lives

`.paper/changes.yml`, beside the manuscript, in the same directory as the paper memory files
described in `research-paper-writing/references/paper-memory.md`. Same directory, same
versioning, same rule: it is a working artifact and is never submitted.

`changes.yml` reads `claims.yml`. It does not duplicate it. When a reviewer forces a claim to
be weakened, the claim's own row is edited in `claims.yml` and the change row here points to it.

## Three Layers of Evidence

Keep these separate. They are not the same thing, and collapsing them is how a second-round
review goes wrong.

1. **The reviewer's instruction** — what was asked.
2. **The author's claim** — what the response letter said would happen or had happened.
3. **The verified change** — what the current manuscript actually contains, at a located
   position.

A response reading "revised", "fixed", or "addressed" is evidence of layer 2 only. Never mark
a row `done` from the response text. Open the manuscript, find the change, record where.

This matters most in round two, where you are auditing your own round-one promises. Before
drafting anything, re-verify every row marked `done` in round one against its `done_when` —
an edit made later in the revision can silently undo an earlier one, which is what
`regressed` is for, or leave a change in place that now contradicts the paper, which is what
`made worse` is for.

## The Ledger as Shown to the Author

The file is the record. This table is how its rows are shown in the conversation; it holds more
rows than the YAML excerpt under Schema. The examples in this guide are invented.

| ID | Reviewer | Comment (short) | Type | Decision | Manuscript change | Location | Status |
|---|---|---|---|---|---|---|---|
| R1.1 | 1 | Grid resolution unjustified | method | concede | Added convergence test, new Table 3; all results rerun at 0.5 m | §2.2, §2.4, Table 2, Table 3, Fig. 4 | done |
| R1.2 | 1 | Claim too strong for four climates | claim | concede | Bounded claim to sampled climates | §4.1 L12, Abstract L6, Conclusion L3 | done |
| R1.5 | 1 | Add two more climates | evidence | partially concede | Added sensitivity analysis instead; reasoning in response | §4.3 | partial |
| R2.3 | 2 | Add comparison to Method X | evidence | contest | Reason for the omission added, with two citations | §2.5 | done |
| R2.8 | 2 | Report solver wall-clock time | method | contest | None — run times were not recorded for the runs behind the results, and recovering them would mean repeating the runs; explained in response | response only | waived |
| R2.9 | 2 | Confirm Fig. 3 uses the corrected dataset | evidence | concede | [insert what was regenerated, from which run, and why its provenance cannot be confirmed] | Fig. 3 | not verifiable |
| R3.1 | 3 | Restructure Discussion around themes | presentation | contest | None — would undo the R1.2 scope bounding; flagged to editor in cover letter | response only | waived |

## Statuses

| Status | Meaning |
|---|---|
| `done` | The change exists in the manuscript and its location has been checked |
| `partial` | Some of the comment is addressed; the rest is still open |
| `open` | Not yet addressed |
| `regressed` | Was addressed, then undone by a later edit |
| `made worse` | Was addressed, and the change created a new problem — a contradiction, a number that no longer agrees, a claim now overrun |
| `not verifiable` | Cannot be confirmed from the artifacts to hand — say why. The response says plainly that it could not be verified, and why; it never says "we have" for it |
| `waived` | Deliberately not doing it. Record who decided, why, and the remaining risk. This is also the status of a contested comment that leads to no manuscript change |
| `promised` | Conference rebuttal only, where no revised file can be uploaded: the change will be made in the camera-ready version, and `done_when` says what it will be |

`done` is only for a row whose change exists in the manuscript. A contested comment with no
manuscript change is `waived`, never `done`. A waiver is never quietly converted to `done`. It
stays visible in the ledger and, if it affects the science, it is flagged to the editor in the
cover letter.

## Schema

```yaml
version: 1
updated: "2026-08-21"
manuscript: "manuscript.tex"
decision: major_revision   # minor_revision | major_revision | reject_resubmit | rebuttal | round_2
round: 1
submitted: "2026-06-02"
decision_received: "2026-08-04"
deadline: null             # the date the revision is due, when the letter gives one
response_sent: null

comments:
  - id: R1.1
    reviewer: 1             # 1, 2, 3 ... or editor
    comment: "Grid resolution is unjustified."
    type: method            # the ten types of triage.md, Step 2, in lower case
    severity: blocking      # blocking | substantive | minor
    decision: concede       # concede | partially concede | contest
    decision_confirmed: true   # true only after the author confirmed; absent or false means proposed
    reason: null
    done_when: "Sec. 2.4 reports a convergence test on the grid used for the main results, with the change in mean compliant plan depth between refinements."
    manuscript_change: "Added grid-convergence test, new Table 3; all results rerun at 0.5 m, and Sec. 2.2 states the spacing."
    location: ["Sec. 2.2", "Sec. 2.4", "Table 2", "Table 3", "Fig. 4"]
    affects_claims: ["C1", "C2"]
    affects_figures: ["Fig4", "Tab2", "Tab3"]
    affects_runs: ["R1", "R2", "R3"]    # ids in runs.yml; optional
    amendment: "A1"         # an id in design.yml; optional, null when none
    status: done            # done | partial | open | regressed | made worse | not verifiable | waived | promised
    verified_on: "2026-08-18"
    response_paragraph: "R1.1"

  - id: R1.2
    reviewer: 1
    comment: "Claim is too strong for four climates."
    type: claim
    severity: substantive
    decision: concede
    decision_confirmed: true
    reason: null
    done_when: "The Abstract, Sec. 4.1 and the Conclusion each state the claim for the four sampled climates only."
    manuscript_change: "Bounded the claim to the four sampled climates."
    location: ["Sec. 4.1 L12", "Abstract L6", "Conclusion L3"]
    affects_claims: ["C1"]
    affects_figures: []
    claim_verb_change:
      - claim: C1
        before: "shows"
        after: "suggests"
        decision: keep        # restore | keep | pause
        reason: "Conceded to R1.2: a simulation study in four climates does not support 'shows'."
    status: done
    verified_on: "2026-08-18"
    response_paragraph: "R1.2"

  - id: R2.3
    reviewer: 2
    comment: "Add a comparison to Method X."
    type: evidence
    severity: substantive
    decision: contest
    decision_confirmed: true
    reason: "Method X needs bidirectional transmission data that do not exist for the shading assemblies studied. A generic substitute would test an assumed optical model, not Method X."
    manuscript_change: "Added the reason for omitting Method X, with two citations."
    location: ["Sec. 2.5"]
    affects_claims: []
    affects_figures: []
    status: done
    verified_on: "2026-08-18"
    response_paragraph: "R2.3"

  - id: R3.1
    reviewer: 3
    comment: "Restructure the Discussion around themes."
    type: presentation
    severity: minor
    decision: contest
    decision_confirmed: true
    reason: "Would undo the scope bounding made for R1.2."
    manuscript_change: null
    location: []
    affects_claims: ["C1"]
    affects_figures: []
    status: waived
    waived_by: "corresponding author, 2026-08-19"
    waived_risk: "Reviewer 3 may repeat the request in round two."
    flagged_to_editor: true
    response_paragraph: "R3.1"

  - id: E.1                 # an editor's own requirement is a comment
    reviewer: editor
    comment: "[insert the editor's requirement]"
    type: "[insert one of the ten types, after reading the requirement]"
    severity: "[insert blocking, substantive or minor]"
    decision: concede
    decision_confirmed: false
    reason: null
    done_when: "[insert what will show that the requirement is met]"
    manuscript_change: null
    location: []
    affects_claims: []
    affects_figures: []
    status: open
    response_paragraph: "E.1"

conflicts:
  - between: ["R1.2", "R3.1"]
    type: direction         # view | severity | existence | direction
    description: "R1.2 requires narrowing scope; R3.1's restructure would widen it again."
    resolution: "Kept the R1.2 bounding. Explained in the response and flagged to the editor."
  - between: ["R1.4", "R2.5"]
    type: direction
    description: "R1.4 asks for aggregation by orientation; R2.5 asks for disaggregation by hour. Both do not fit the length limit."
    resolution: "Kept the orientation aggregation, moved the hourly data to Appendix B, and asked the editor."
```

## Field Rules

1. **Every comment gets a row**, including trivial and typographical ones. A missing row is a
   missing answer, and silence on a point is what a reviewer looks for in round two.
2. `decision` is set before any prose is drafted. `contest` requires a non-null `reason`
   recorded here first.
3. `status: done` requires a non-null `verified_on`. The date is when someone opened the
   manuscript and found the change at `location`. Never set it from the response text.
4. `decision: concede` with a null `manuscript_change` is unfinished work. It is not a valid
   `done`. A `done` row, whatever its decision, has a non-empty `manuscript_change` and a
   non-empty `location`. A contested comment with no manuscript change is `waived`.
5. `status: waived` requires `waived_by`, `waived_risk` and `flagged_to_editor`. A waiver is
   never quietly converted to `done`, and if it affects the science, `flagged_to_editor` is
   true and the cover letter says so.
6. `affects_claims` and `affects_figures` point into `claims.yml` and `figures.yml`. They are
   what makes the cross-check below possible.
7. `response_paragraph` links the row to where the response letter answers it, so the letter can
   be checked for completeness against the ledger.
8. `conflicts` records contradictory reviewer requests. Each one is stated explicitly in the
   response and flagged to the editor. See `SKILL.md`, Execution Rule 4. Each carries a
   `type`: `direction` when the reviewers ask for opposite changes, `severity` when they
   agree a weakness exists and disagree on its weight, `existence` when one faults what the
   other accepts, and `view` when no fact is at stake. `triage.md`, Step 5, says how each
   type is settled.
9. `done_when` is the manuscript evidence that would settle the comment, written at triage,
   before any change and before any reply. It names what a reader will find and where. Every
   `concede` and `partially concede` row carries it, whatever its status.
10. `status: done` means the manuscript meets `done_when`, and someone checked. A change that
    exists but answers a different question, or only part of the question, is `partial`.
11. `status: made worse` marks a change that was made and created a new problem: a
    contradiction with another section, a number that no longer agrees, a claim the
    Discussion now overruns. It differs from `regressed`, which marks a change that was made
    and later undone. Both are fixed before anything else.
12. `status: partial` requires `partial_reason`: what part of the comment was not done, and
    why. The reason is what the response letter then says, in the same words.
13. `claim_verb_change` records every claim whose hedging verb a response changed, with the
    verb before, the verb after, and one `decision`: `restore` the earlier verb, `keep` the
    new one with a `reason`, or `pause` for the author. A reviewer asking for a stronger
    claim than the data support is refused, and the row records `restore`. The rule is in
    the `paper-review.md` reference of `research-paper-writing`, Claim-Strength Drift.
14. `type` and `severity` take the values of `triage.md`, Steps 2 and 3, written in lower
    case: ten types, and `blocking`, `substantive` or `minor`. Nothing else is valid.
15. `status: promised` is for a conference rebuttal only, where the top-level `decision` is
    `rebuttal` and the venue's current rules allow no revised file to be uploaded. Where a
    revised file can be uploaded, make the change and record it as `done`. A `promised` row
    carries `done_when`. When the
    camera-ready version is prepared, each promised row becomes `done` with a `verified_on`
    date, or the chairs are told it was not done. In a journal revision the change is done or
    it is open; `promised` is not valid there.
16. Each comment's `decision` takes exactly `concede`, `partially concede` or `contest`. A
    missing or other value is invalid, and it switches off the checks that depend on the
    decision. The top-level `decision` is a different field: the editor's decision on the
    manuscript, such as `major_revision`.
17. `decision_confirmed` is `true` only when the author has confirmed that decision. The
    assistant writes `true` only after the author confirmed it in the conversation;
    `/paper-respond` writes `false` for every proposal. Absent means not confirmed. A row with
    `false`, or with no `decision_confirmed`, means the response is not ready to send.
18. An editor's own requirement is a comment. It gets an id `E.n` and `reviewer: editor`, and
    it is answered in the editor's block of the response (`response-letter.md`, Structure). A
    requirement that is met in the response or in the cover letter, and not in the manuscript,
    records in `manuscript_change` what was written there, with `location: ["cover letter"]`
    or `["response"]`.
19. `affects_runs` lists the ids in `runs.yml` of runs that the comment led to or replaced.
    `amendment` is the id in `design.yml` of an amendment the comment led to. Both are optional.
    Each id exists in its file.
20. `updated` is the date the file was last changed. Change it with every edit. `deadline` is
    the date the revision is due, when the decision letter gives one; `null` otherwise.

## Round Two

This is the file's main payoff.

1. **Do not start round two by reading your round-one response letter.** Read `changes.yml`,
   then verify against the manuscript.
2. **Re-verify every row marked `done` in round one against its `done_when`**, by opening the
   manuscript, before you read what the response letter said about it. An edit made later in
   the revision can silently undo an earlier one. A row that no longer holds becomes
   `regressed`. A row whose change is present but created a new problem — it contradicts
   another part of the paper, or a number no longer agrees — becomes `made worse`. Both are
   fixed before anything else. A change that is present, harms nothing, and does not meet
   `done_when` is `partial`, with the missing part in `partial_reason`.
2b. **Then read the response letter, and compare.** Where the letter claims more than the
   manuscript shows, the manuscript is right and the letter was wrong. Say so in round two
   instead of defending the earlier wording.
3. Bump `round` and add the new comments with new ids. Keep the round-one rows. They are the
   record you reference by number when a reviewer asks whether you did what you said.
4. A round-one row that was `waived` and is raised again needs a real answer, not the same
   waiver.
5. Keep every round-one row, raise `round`, and set `updated`.

## Cross-Checks

Run checks 1 to 8, 11, 12 and 13 before drafting the response letter, and all thirteen before sending. Checks 9 and 10 need the letter.

1. Every comment in the decision letter has a row. Count them independently — reviewers rarely
   number every point, and one paragraph often contains three.
2. No row has `status: open`. In a rebuttal, a change that will be made later is `promised`,
   never left `open`.
3. Every `concede` row has a non-null `manuscript_change`, unless its status is `open`, `promised` or `regressed`, and every `concede` row that is `done` or `partial` has a non-empty `location`.
4. Every `done` row has a `verified_on` date, a non-empty `manuscript_change` and a non-empty `location`.
5. Every `contest` row has a `reason`.
6. Every `waived` row has `waived_by`, `waived_risk`, and a decision on `flagged_to_editor`.
7. Every id in `affects_claims` exists in `claims.yml`, and any claim weakened in response to a
   comment has had its `claims.yml` row updated — status, verb, and `bounded_to`.
8. Every id in `affects_figures` exists in `figures.yml`, and any regenerated figure has
   `status: final` with re-verified `key_numbers`.
9. Every row has a `response_paragraph`, and every paragraph of the response letter maps to at
   least one row.
10. Every number quoted in the response is the number now in the manuscript.
11. No row has `status: regressed` or `made worse`, and every `partial` row has a
    `partial_reason`.
12. Every `claim_verb_change` has a decision, and none is `pause`.
13. Every `decision` is one of the three values, and every row has `decision_confirmed: true`.

Failing any of checks 1 to 6 or 9 to 13 means the response is not ready to send. A failure of 7
or 8 is fixed before the next Submission Gate.

`check_ledger.py`, in the `scripts/` folder of the `research-paper-writing` skill, runs the mechanical part of these
checks on `.paper/changes.yml`: row ids that are missing or used twice, statuses, types, severities,
decisions, proposed decisions, `verified_on`, missing reasons, `done_when`, a `done` row with no
`manuscript_change` or no `location`, `response_paragraph`, the fields of a `waived` row,
`partial_reason`, verb decisions, conflict types, and ids that point at no claim or figure.
Paste its output. It cannot tell whether the manuscript meets a `done_when`; that needs the
manuscript open.

## Handing Back to the Manuscript

A revision is still manuscript writing. When `changes.yml` says a section must be rewritten,
`research-paper-writing` does the rewriting and its paper-memory files are updated as part of
that work. Three rules bind the two skills together.

1. A claim weakened for a reviewer is weakened in `claims.yml` too, or the next Submission
   Gate will pass a claim that no longer matches the text.
2. A figure regenerated for a reviewer has its `key_numbers` re-checked against the prose, or
   the response will quote a number the manuscript no longer contains.
3. A rerun or an amendment made for a reviewer is recorded in `runs.yml` and `design.yml`, and
   the row names it in `affects_runs` and `amendment`.

## Checklist

1. Does `.paper/changes.yml` exist, with a row per comment, including the trivial ones?
2. Was every `decision` set before any response prose was drafted?
3. Does every `done` row carry a `verified_on` date from opening the manuscript?
4. Are all waivers documented with who decided, the risk, and whether the editor was told?
5. Do all thirteen cross-checks pass, with the script's output pasted?
5b. Was each `done_when` written at triage, and was each `done` row checked against it?
6. For round two: was every round-one `done` row re-verified before drafting?
7. Are `claims.yml` and `figures.yml` updated to match what the revision actually did?
