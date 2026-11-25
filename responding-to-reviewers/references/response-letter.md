# The Response Letter

**Load when:** drafting or auditing the point-by-point response.

**Contents:** Goal · Structure · The Opening · Point-by-Point Format · Marking Changed Text · Wording Patterns · Second-Round Responses · Conference Rebuttals · Tone · Auditing a Draft Response · Pre-Send Checklist

## Goal

Produce a point-by-point document a reviewer can check without reopening the manuscript.

## Structure

1. **Header** — manuscript title, ID, journal, decision type, date.
2. **Opening** — two or three sentences. Thanks, and a one-line summary of what changed.
3. **Summary of changes** — 4–8 lines, the substantive changes only. Optional for minor
   revision, valuable for major.
4. **Point-by-point** — every comment, grouped by reviewer, in the reviewer's own order.
5. **Editor's comments** — separately, usually first or last, never buried inside a
   reviewer's block. Each requirement has its `E.n` id, as in `change-ledger-file.md`.

## The Opening

Short. Reviewers skip it. The examples in this guide are invented.

> We thank the reviewers for their careful reading. The main changes are a convergence test
> for the calculation grid (new §2.4 and Table 3), a bounded scope for the headline claim,
> and a new sensitivity analysis in §4.3. All comments are addressed point by point below.

Do not: praise the reviewers at length, restate the paper's contribution, or apologise.

## Point-by-Point Format

Three elements per comment, visually distinct. Quote the reviewer verbatim.

> **Comment R1.1.** *"The choice of a 1.0 m calculation grid is not justified, and may be too
> coarse to resolve the compliant plan depth."*
>
> **Response.** We agree. A grid convergence test was not included in the original
> submission. We have run the study at 1.0 m, 0.5 m, and 0.25 m spacing. Under the worst-case
> view direction, the mean compliant plan depth rose by 6.9% between 1.0 m and 0.5 m, and by
> 0.4% between 0.5 m and 0.25 m. We have therefore rerun all results at 0.5 m spacing. The
> direction of the headline finding is unchanged. Its size changed: under the worst-case view
> direction the mean compliant plan depth is now 3.1 m, where the original submission reported
> 2.9 m.
>
> **Change.** New §2.4 "Grid convergence" and Table 3, `[insert the page]`. Fig. 4 and Table 2 rerun at
> 0.5 m. Methods §2.2 updated to state the spacing and the convergence evidence.

Rules:

1. **Quote the reviewer exactly**, in italics or a block quote. Paraphrase invites a reply
   saying you answered a different question.
2. **Response and Change are separate.** The response argues; the change locates. Merging
   them hides whether anything actually happened.
3. **Give the location** — section, page, table, figure, line. A reviewer who cannot find the
   change assumes it was not made.
4. **Quote new text** where it is short. Saves the reviewer a lookup.
5. **Give numbers.** "Improved substantially" is not an answer; "changed by 6.9%" is.

## Marking Changed Text

Read the journal's revision instructions first and supply every file they require. Many
journals ask for a clean manuscript and a marked-up one as separate files. Then pick one
convention for the response and state it in the opening:

1. New or changed manuscript text quoted in the response in a distinct style.
2. A separately supplied marked-up manuscript, where the journal's instructions ask for one.
3. Page and line numbers keyed to the revised manuscript, not the original.

Say which numbering you are using. Line numbers shift between versions, and a reviewer
checking against the wrong version will report your change as missing.

## Wording Patterns

A "we have" sentence about a change is used only for a change that exists in the manuscript at
a checked location: a row whose status is `done` or `partial`. Each slot is an
`[insert ...]` bracket until the fact is known.

### Conceding

> We agree, and have [insert the change] in [insert the location].

> This was an omission. We have added [insert the content] to [insert the location].

> The reviewer is right that [insert the point, restated]. We have [insert the change].

Never hedge a concession. "While we believe the original approach had merit, we have
nonetheless..." reads as resentful compliance.

### Fixing a misreading

The text was ambiguous. That is your problem, not the reviewer's.

> Our original wording did not make this clear. The value is a documented default rather than
> a measurement, and we have relabelled it as such in [insert the table] and stated its
> source in [insert the section].

Never: "the reviewer appears to have misunderstood", "as stated in the paper", "as we already
noted". These are all readable as "you did not read it properly".

### Adding evidence

> We have run the requested comparison. [insert the method] gives [insert the value] under
> [insert the conditions], against [insert the value] for the proposed method. This is now
> [insert the table] and is discussed in [insert the section].

### Declining, out of scope

> The paper examines [insert the scope]. This question falls outside that scope. Answering it
> would require [insert what it needs]. [insert whether a future-work sentence was added, and
> where; or nothing].

State what the paper *is*. A refusal without a scope statement reads as evasion.

### Declining, infeasible

Be concrete about the obstacle.

> [insert what is not available, and why it cannot be obtained]. We have instead [insert the
> alternative], and [insert where the manuscript now states this limitation and its direction].

### Refusing to over-claim

Rare, and worth doing well.

> We would prefer not to state this as a causal mechanism. Our data show the association but
> do not separate it from [insert the alternative]. We have described it as consistent with
> [insert the mechanism] in [insert the section]. [insert the measurement that would
> distinguish the two, and where it is stated, if the author added it].

This refusal protects the paper. A reviewer who pushed for it will usually accept the
reasoning; an editor certainly will.

### Batching minor points

> **Comments R2.10–R2.12 (typographical and units).** All accepted and corrected: [insert the list].

## Second-Round Responses

1. Reference your first-round IDs so the reviewer can follow the thread.
2. Address only what remains open, plus anything new.
3. Do not re-argue a point you already conceded — check the change landed and move on.
4. If the reviewer repeats a point you contested, they were not persuaded. Either concede
   this time, or make a genuinely different argument. Repeating the first answer verbatim
   ends badly.

## Conference Rebuttals

Different constraints, so a different shape.

1. Read the venue's current rebuttal rules first: the length limit and its unit (words,
   characters or pages), whether new results are allowed, whether links are allowed, whether
   a revised file may be uploaded, and whether the rebuttal must be anonymous. Follow them.
   The rules differ between venues and between years.
2. Triage by decision impact and say so: "We address the three concerns most relevant to
   the decision."
3. Where no revised file can be uploaded, "we will" is correct. Each "we will" is a
   `promised` row in the ledger that the author agreed to. Where a revised file can be
   uploaded, make the change, report it with "we have", and record it as `done`.
4. Answer factual misreadings first — they are the cheapest changes of mind to win.
5. Report only results the author ran and supplied, and only where the venue allows new
   results. Inline, compactly: a single number beats a paragraph.
6. Never leave a blocking concern unanswered to fit a minor one in.
7. One shared opening for all reviewers; do not repeat the thanks three times.

## Tone

1. Professional and plain. No warmth, no coldness.
2. `We` throughout. Refer to the reviewer as "the reviewer", not "you".
3. No exclamation marks, no rhetorical questions.
4. Do not thank the reviewer for each individual comment. Once, at the top.
5. Do not describe a comment as "interesting", "excellent", or "insightful" — it reads as
   managing them.
6. Length matches impact, not annoyance.

## Auditing a Draft Response

Use this when a response already exists — written by a co-author, started before the
revision was finished, or drafted in a hurry — and the question is whether it is fit to send.
The output is advice. It never declares the response ready; the Pre-Send Checklist and the
ledger cross-checks do that, with the manuscript open.

Inputs: the decision letter, the draft response, and the revised manuscript. If the
manuscript is missing, say so, and report every check that needs it as not run.

1. **Rebuild the inventory from the letter, not from the draft.** Extract every comment as
   `triage.md`, Step 1, describes. A draft that skipped a comment will not remind you of it.
2. **Coverage, one line per comment**:

   | Coverage | Meaning |
   |---|---|
   | `addressed` | The draft answers this comment and points to a change or gives a reason |
   | `partly` | The draft answers one part of a compound comment, or answers without a location |
   | `missing` | The draft does not answer it |

3. **Gaps.** List every `missing` and `partly` comment, with what is absent.
4. **Risk flags**, each quoted from the draft:
   - **A claim with no change behind it** — "we have revised", "this has been addressed",
     with no location, or with a location where the manuscript shows no such change.
   - **A different question answered** — the reply is sound and is not a reply to what the
     reviewer asked. Compare each reply with the comment's `done_when`, or with the comment
     itself if none was written.
   - **Combative or dismissive wording** — "the reviewer misunderstood", "as clearly stated",
     "obviously". See Tone.
   - **A promise** — "we will" in a journal revision, where the change should already exist.
   - **A number that differs from the manuscript.**
   - **A claim strengthened under pressure** — a verb moved up the ladder to satisfy a
     reviewer.
5. **Do not rewrite the draft in this pass.** Report first. The author decides what to
   concede; then the response is redrafted from the ledger, in the normal order: manuscript
   first, letter second.
6. **Offer to record the result** in `.paper/changes.yml`, as rows with their true status,
   once the author has read the audit. Written there, the audit becomes the starting point
   of the real work. Do not write the file as part of the audit itself: until the author
   confirms it, the audit is a report.

## Pre-Send Checklist

1. Does every comment in the letter have a numbered response?
2. Is every reviewer quote verbatim?
3. Does every conceded point name a manuscript location?
4. Does every location actually contain the change? Open the manuscript and verify.
5. Is every number in the response the number now in the manuscript?
6. Are line and page numbers keyed to the revised version, and is that stated?
7. Is any change described that was not made?
8. Any "the reviewer misunderstood", "as we already stated", or "as mentioned above"?
9. Any "we will" in a journal revision response? Each is a change now made (write "we have")
   or a promise the author did not make (remove).
10. Are reviewer conflicts flagged to the editor?
11. Has the editor's own text been answered separately?
12. Does the revised manuscript still pass its own gates — `paper-review.md`, and
    `simulation-reporting.md` if the method changed?
13. Does each `done` row's change meet its `done_when`, and is no row `regressed` or `made
    worse`?
14. Has every changed claim verb a recorded decision?
