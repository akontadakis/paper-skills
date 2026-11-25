# Comment Triage

**Load when:** the comment inventory exists and each comment needs a type, a severity and a decision, or a situation arises after a decision: an error in the results, a data request, a co-author's dissent, a deadline.

**Contents:** Goal · Step 1 — Extract Every Comment · Step 2 — Classify by Type · Step 3 — Rate Impact · Step 4 — Decide Concede or Contest · Step 5 — Check for Conflicts · Step 6 — Sequence the Work · Situations · Triage Checklist

## Goal

Turn a decision letter into a complete, classified inventory, and decide concede or contest
for each item before writing any prose.

## Step 1 — Extract Every Comment

Read the whole letter first. Then extract.

1. **Number everything.** `R1.1`, `R1.2`, `R2.1`. Use the reviewer's own numbering where they
   provided it, and add sub-numbers where one numbered point contains several asks.
2. **Split compound comments.** A single paragraph often carries three requests. Each gets its
   own ID, because each needs its own change and its own answer.
3. **Extract the implicit ones.** "It is unclear how the grid was chosen" is a request for a
   justification, not an observation.
4. **Include the positive remarks.** They do not need a response, but they tell you what not
   to break in revision.
5. **Read the editor's text separately.** It may overrule a reviewer, add a requirement, or
   tell you which comments are binding. Editor requirements outrank reviewer preferences.
   Give each one an `E.n` id and `reviewer: editor` in the ledger.

Count them at the end. A 3-page letter usually holds 20–40 comments, not the 12 the reviewer
numbered.

### On a Second Round

Extract three things, kept separate:

1. The new letter's comments, as above.
2. **Your previous response letter**, as its own layer — what you claimed you had done.
3. **The current manuscript**, verified — what is actually there now.

Re-verify every round-one row before drafting. A claim in your own previous letter is not
evidence the change survived later editing. Mark anything that did not survive as
`regressed`; it is worse than never having done it, because the reviewer was told it was
done. Mark a change that is present but created a new problem — a convergence table that
contradicts the grid used for the main results, a bounded claim that the Discussion now
overruns — as `made worse`. Check each row against its `done_when`, not against whether
something was added.

## Step 2 — Classify by Type

Type determines what kind of answer is even possible.

| Type | The reviewer is saying | What closes it |
|---|---|---|
| **Misreading** | They read it wrong | A clarification in the manuscript. The text was ambiguous. |
| **Missing information** | It is not in the paper | Add it. Almost always concede. |
| **Method** | The method is wrong or unjustified | Justification with evidence, a new analysis, or a bounded claim. |
| **Evidence** | More is needed — experiment, baseline, case, condition | Run it, or defend why it is not required. |
| **Claim** | The claim exceeds the data | Weaken the claim. Rarely worth contesting. |
| **Framing** | The gap, novelty, or positioning is wrong | Reframe, or defend with literature. |
| **Presentation** | Figures, tables, structure, length | Fix it. Cheap. |
| **Language** | Grammar, style, clarity | Fix it. Never argue. |
| **Out of scope** | A different paper | Decline politely, with a reason. |
| **Wrong** | The reviewer is factually mistaken | Contest, with evidence. Handle carefully — see `disagreement.md`. |

## Step 3 — Rate Impact

Not all comments carry equal weight in the decision.

| Level | Meaning |
|---|---|
| **Blocking** | The paper is rejected if this is not resolved. Method validity, an unsupported headline claim, a missing control. |
| **Substantive** | Affects the assessment but not fatal. A missing comparison, an under-justified parameter. |
| **Minor** | Improves the paper. Presentation, wording, an extra citation. |

Effort follows impact. A blocking comment gets a full paragraph, new analysis, and a quoted
change. A minor one gets a sentence.

Record both in the change ledger: the type in `type`, the level in `severity`, each in lower
case. The ledger accepts the ten types above and `blocking`, `substantive` or `minor`, and
nothing else.

## Step 4 — Decide Concede or Contest

Decide for every comment before drafting. Recording the decision first stops the response
drifting into defensiveness mid-paragraph.

**Write `done_when` with the decision.** For every comment you concede or partially concede,
write one sentence stating the manuscript evidence that would settle it, before you change
anything: `Methods 2.4 reports a convergence test on the 0.5 m grid used for the main
results, with the change in mean compliant plan depth between successive refinements`. It names what a reader will
find and where. It is not "the reviewer is satisfied" and not "added as requested".

This sentence is what the row is checked against later. Without it, "we added a table" is
recorded as `done` when the table answers a different question, and nobody notices until the
reviewer does. Written first, it also stops the criterion sliding toward whatever was easy
to do.

### Concede when

1. The reviewer is right. This is most of the time.
2. The fix is cheap, even if you think the point is marginal. Arguing over a figure label
   costs more credibility than the change costs effort.
3. The claim genuinely exceeds the evidence. Bound it.
4. It is a matter of taste and the reviewer has a preference. Their preference wins.
5. You could contest it but the point is not load-bearing for your contribution.

**Concede fully, not grudgingly.** "We agree" then the change. No "although we believe the
original was defensible".

### Partially concede when

The reviewer identified a real problem but proposed the wrong fix. Accept the problem, do
something better, and explain why. The examples in this guide are invented.

> The reviewer is right that four climates limit generality. [insert why two further climates
> were not added]. We have bounded the claim to the four sampled climates and added the
> sensitivity analysis in §4.3.

### Contest only when

1. The reviewer is factually wrong, and you can show it.
2. The request is outside the paper's scope, and you can say what the paper is instead.
3. Complying would make the paper worse — usually by forcing a claim past the evidence.
4. The request is infeasible, and you can say why concretely.

Contesting more than about a fifth of the substantive comments reads as defensiveness even
when each individual argument is sound. If your contest rate is high, re-examine the
concessions you are refusing to make.

**Never contest**: language, presentation, or anything cosmetic. Just fix it. There is one
exception: a presentation request that would undo a change another reviewer required. That is a
conflict between reviewers. Handle it under Step 5 and flag it to the editor in the cover letter.

## Step 5 — Check for Conflicts

1. **Reviewers contradicting each other.** Common. Pick one, explain the choice in the
   response, and flag it to the editor in the cover letter. Do not silently satisfy one and
   ignore the other. Label the conflict by its type, because the type decides the answer:

   | Type | The reviewers | What settles it |
   |---|---|---|
   | `direction` | ask for opposite changes: shorten and expand, aggregate and disaggregate | A choice, stated, with the other served in an appendix or supplementary where possible. The editor arbitrates. |
   | `severity` | see the same weakness, and disagree on how serious it is | Answer at the level of the more serious reading. It costs little and it closes both. |
   | `existence` | disagree on whether there is a problem: one praises what the other faults | Evidence. Show the text or the data, and treat the faulting reviewer's reading as a sign the text was unclear. |
   | `view` | differ in preference or school, with no fact at stake | A choice, with the reason. Do not pretend it is settled by evidence. |

   Split a bundled comment into its separate requests before deciding that two reviewers
   conflict. They often agree on two of three points.
2. **A reviewer contradicting the editor.** The editor wins.
3. **A request that breaks another part of the paper.** Say so, and propose the alternative.
4. **A request that would over-claim.** Refuse it, on evidence grounds. A reviewer asking you
   to state a mechanism your data cannot support is asking for a defect.

## Step 6 — Sequence the Work

1. Blocking comments first, because they may change the paper's structure and invalidate
   smaller edits.
2. Group comments touching the same section and do them together.
3. Presentation and language last — they are invalidated by restructuring.
4. Update the change ledger as each is finished, with its location. Use the ledger's own
   status values from `change-ledger-file.md`, Statuses — `done`, `partial`, `open`, `regressed`,
   `made worse`, `not verifiable`, `waived`, and `promised` in a rebuttal — not free text. The Decision column takes `concede`,
   `partially concede`, or `contest`; a `partially concede` row almost always ends at
   `partial`, not `done`. A `partial` row records what was not done and why, in
   `partial_reason`.
5. Set a row to `done` only when the manuscript shows what its `done_when` says. A change
   that exists and does not meet it is `partial`. A change that created a new problem is
   `made worse`.
6. A contested comment that leads to no manuscript change is `waived`, with `waived_by`,
   `waived_risk` and `flagged_to_editor`. It is never `done`.

## Situations

1. **A comment reveals a real error in the results.** Tell the author before anything else.
   The author corrects the error and reruns what depends on it. Record the new runs, mark the
   old ones with `record_run.py --supersede`, add a `post hoc` amendment of `kind: correction`
   with `old_result` to `design.yml`, name both in the row's `affects_runs` and `amendment`,
   and update `claims.yml` and `figures.yml`. Say in the response and in the cover letter that the result changed, and
   why. Never fix it without saying so.
2. **A request for raw data or code.** Whether to share is the author's decision, and the
   journal's data policy and any ethics or licence limit apply: check the journal's
   instructions. If the files cannot be shared, say what is withheld and why, and treat it
   as an infeasible request. Never send files on your own.
3. **A co-author disagrees with a concession.** Do not draft around it. Keep the row with
   `decision_confirmed: false` until the corresponding author has the co-authors' view and
   confirms. A disagreement that stays open goes to the author who decides, and is recorded
   in `reason` or `waived_by`.
4. **A review that looks machine-written.** Answer each comment on its merits, as for any
   other. Do not say in the response that the review looks machine-written. If the author
   wants to raise it, that goes to the editor in a separate message: check the journal's
   instructions.
5. **The deadline and an extension.** Put the deadline from the decision letter in the
   inventory. If the work will not fit, ask the editor for more time before the date passes,
   in writing, with the date you need. Rules on extensions vary: check the journal's
   instructions. Do not cut the manuscript work to fit the date.
6. **Do not contact a reviewer directly.** Everything goes through the editor, in the
   response and the cover letter.

After a rejection, the repair of the paper and the choice of the next journal are in
`submission-package.md`, After a Rejection, of `research-paper-writing`.

## Triage Checklist

1. Is every comment extracted, including implicit and compound ones?
2. Is the editor's own text extracted separately?
3. Does every comment have an ID, a type, and an impact level?
4. Does every comment have a concede / partially concede / contest decision, recorded before
   drafting?
4b. Does every conceded or partially conceded comment have a `done_when`, written before the
    manuscript was changed?
5. Is the contest rate below roughly a fifth of substantive comments?
6. Are reviewer conflicts identified, typed, and a choice made?
7. Does any request, if followed, push a claim past its evidence?
8. Is the work sequenced blocking-first?
