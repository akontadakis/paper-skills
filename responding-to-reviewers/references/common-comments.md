# Common Reviewer Comments

**Load when:** a comment matches a stock complaint: grid or mesh, sample size, novelty, validation, limitations, language.

**Contents:** Goal · Simulation and Modelling · Claims and Scope · Method and Evidence · Framing · Presentation · Structural · Answering Any of These

## Goal

Recognised patterns and how to answer them. Adapt the wording; do not paste it.

Each entry gives what the reviewer is really asking, the default move, and the trap.

Bare filenames below — `results.md`, `sentence-craft.md`, `ai-tells.md`, and the rest — refer
to the `references/` directory of the `research-paper-writing` skill. Load that skill for any
manuscript text you write.

**Which file owns the fix.** Most of these comments have one reference file behind them.
Loading it is the difference between answering the comment and answering the whole class of
comment the reviewer sampled from.

| Comment is about | Load |
|---|---|
| Simulation setup, provenance, convergence, validation | `simulation-reporting.md` |
| Statistics, effect size, uncertainty, multiplicity, model agreement, predictive scores | `statistics-reporting.md` |
| Sample size, participants, ethics approval, consent, generalisation from the sample | `ethics-and-participants.md` |
| Claim strength, hedging, verb-to-evidence | `sentence-craft.md` Hedging, plus `paper-review.md` claim ledger |
| The gap, or "this has already been shown" | `literature-and-gap.md` |
| Search protocol, screening, flow diagram (review papers) | `review-papers.md` |
| Figures, tables, captions, legibility | `figures-tables.md`; `extract_figures.py audit`, in the `scripts/` folder of `research-paper-writing`, for print resolution |
| Bibliography, cross-references, float placement (LaTeX) | `latex-mechanics.md` |
| Fields, cross-references, tracked changes (Word) | `word-manuscripts.md` |
| English, register, repetition | `sentence-craft.md`, then `ai-tells.md` with `ai_tell_audit.py`, in the same `scripts/` folder |
| Results carrying interpretation, or Discussion introducing numbers | `results.md` and `discussion.md` |
| Journal-convention mismatch the reviewer cannot name precisely | `venue-calibration.md` |

Every fix you make updates `.paper/` as part of the same pass: a weakened claim in
`claims.yml`, a regenerated figure's `key_numbers` in `figures.yml`, a new term in `terms.yml`.
See `change-ledger-file.md`.

---

## Simulation and Modelling

### "The simulation parameters are not reported"

**Really asking:** I cannot reproduce this, so I cannot assess it.

**Default:** Concede completely. Add the full reporting block from
`research-paper-writing/references/simulation-reporting.md` — engine and version, ambient
parameters, sky model, weather file and type, timestep, analysis period, material properties
with provenance.

**Trap:** Adding only the parameters the reviewer named. They named examples, not a
checklist. Report the whole block or the same comment returns in round two.

### "The grid resolution / mesh / timestep is not justified"

**Really asking:** Show me it converged.

**Default:** Run the convergence test. Report the quantity at two or three resolutions with
the percentage change, and state the resolution used for headline results. If the finest
resolution changes the answer materially, rerun everything at it.

**Trap:** Justifying by citation or convention ("1.0 m is standard practice"). Convention is
not convergence evidence for your geometry.

### "The model has not been validated for this application"

**Really asking:** Does this engine work in this regime?

**Default:** Cite the validation studies covering your regime. Where none covers it, say so
explicitly and state the consequence — this is a limitation with a direction, not a hole to
paper over.

**Trap:** Citing a validation study in a different regime as if it transfers. A reviewer who
checks will find it, and the paper's credibility drops further than the original gap cost.

### "Where do the input values come from?"

**Really asking:** Which of these are measured and which are defaults?

**Default:** Add the provenance rank to every input — override, measured or file, documented
default. Disclose substituted defaults as substituted, with their values.

**Trap:** Wording a default as a measurement to make the table look complete. This is
provenance laundering and it is the most serious Methods fault in the field.

---

## Claims and Scope

### "The conclusions are too strong / not supported"

**Really asking:** The Abstract promises more than the Results deliver.

**Default:** Concede and bound the claim. Fix it in the Abstract, Introduction, Discussion,
and Conclusion together — a bounded claim in one place and the original wording in another is
worse than not fixing it.

**Trap:** Adding hedge words while leaving the claim's scope unchanged. "May potentially
suggest" over an unsupported claim is still unsupported.

### "The results are specific to this case and do not generalise"

**Really asking:** What do I take away from this?

**Default:** Two moves. Bound the claim to the sampled conditions, and state the transferable
finding — the mechanism, the ranking, the sensitivity — that does survive beyond the case.

**Trap:** Only doing the first. A bounded claim with no transferable finding invites "thin
contribution" instead.

### "This has already been shown by [citation]"

**Really asking:** What is new here?

**Default:** Read the paper carefully before replying. Then either state the specific
difference — different conditions, metric, scale, or a contradiction you can now explain — or
concede and reframe the contribution around what remains new. Cite the work either way.

**Trap:** Dismissing it on a superficial difference. If the reviewer knows the field well
enough to name it, they know whether your distinction is real.

---

## Method and Evidence

### "Comparison with [method] is missing"

**Really asking:** I cannot tell whether yours is better.

**Default:** Run it if you can, and report it whichever way it comes out. If you cannot, give
the concrete obstacle — data that does not exist, code unavailable, an incompatible boundary
condition — and cite results for that method under conditions where they exist.

**Trap:** "Out of scope." A missing comparison is almost never out of scope; that answer
reads as avoidance.

### "Why these cases?" / "Was this analysis planned?"

*Answered from the study record: `.paper/design.yml` and `.paper/runs.yml`, defined in the
`study-memory.md` reference of `research-study-design`.*

**Really asking:** Did you choose the cases, the threshold or the analysis after seeing the
result?

**Default:** Answer from the dated record. Give the reason recorded for each case set, the
date the design was frozen, and each amendment with its date and timing. A choice recorded as
`post hoc` is stated as made after the results, with the analysis under the original choice
beside it. A new analysis run for the reviewer is a new row in `runs.yml`, and the design
change behind it is a `post hoc` amendment.

**Trap:** Writing a justification the record does not hold. If the cases were chosen because
the data were at hand, say so and bound the claim. If there is no dated record, say that the
choices were not pre-specified; do not claim that they were.

### "The sample size is too small"

*Owned by `ethics-and-participants.md` (sample description) and `statistics-reporting.md`
(power, and what a null result can be said to mean).*

**Really asking:** Is this noise?

**Default:** Report the effect size with its uncertainty. Give the a priori power analysis if
one was run; otherwise report the smallest effect the achieved n could detect. Never compute
power from the observed effect. Bound the claim to what n supports. Where the design is a case study by intent, say
so in Methods rather than defending it in the response.

**Trap:** Arguing that the effect is large so n does not matter. Uncertainty scales with n
regardless of effect size.

### "The statistical treatment is inappropriate"

*Owned by `statistics-reporting.md`.*

**Really asking:** The test does not match the data structure.

**Default:** Take this seriously — it is often correct, especially with repeated measures,
nested data, or non-independence across timesteps. Redo the analysis properly. If the result
changes, report the new one.

**Trap:** Defending the original test because the conclusion is unchanged. If it is
unchanged, the redone analysis costs you nothing.

### "The assumptions are too strong"

**Really asking:** Does this hold in real conditions?

**Default:** State where each assumption holds and where it breaks. Where you can, show the
result under a partial violation. Give the direction of the bias.

**Trap:** Listing assumptions without consequences. Every limitation needs its direction and
size.

---

## Framing

### "The contribution is incremental"

**Really asking:** Why is this a paper?

**Default:** Sharpen the contribution statement to what is actually new — often a finding
rather than a method. Give the quantitative gain and its practical consequence. For a journal
paper, the transferable finding usually carries more weight than novelty of technique.

**Trap:** Restating the contributions louder. Add context the reviewer did not have; do not
repeat what they already read and rejected.

### "The gap is not clearly identified"

**Really asking:** I do not know what problem this solves.

**Default:** Rewrite the gap statement as a specific missing piece, with the citations
showing it is missing. Use `research-paper-writing/references/literature-and-gap.md` to
verify the gap, then `introduction.md` to word it.

**Trap:** "Little attention has been paid to..." That is the phrasing that produced the
comment.

### "The literature review is incomplete"

**Really asking:** Usually — you missed my field, or my paper.

**Default:** Read what they name. Cite a named work only if it bears on a claim in the paper,
and engage with its content rather than adding it to a list. Decline the rest, with a reason
in the response. A citation you add is listed in `.paper/verified-refs.yml`, and the manuscript, the brief or
`.paper/` shows that the work supports the sentence. If the
reviewer's requests are mostly for their own work and bear on no claim, flag the pattern to
the editor. Run the adjacent-field round in `literature-and-gap.md`, since a gap in one
direction usually means gaps in others.

**Trap:** Adding the citations to the reference list without integrating them. Visible, and
irritating. The opposite trap is adding every named work to satisfy the reviewer.

---

## Presentation

### "The figures are unreadable"

**Really asking:** I could not extract the finding.

**Default:** Fix them against `research-paper-writing/references/figures-tables.md` — type
size at final print scale, defined error bars, unitted axes, colour-safe palette. Then check
the compiled PDF with `latex-mechanics.md`.

**Trap:** Enlarging the figure without enlarging the type. The complaint is legibility at
print size, not dimensions.

### "The paper is too long / repetitive"

**Really asking:** The same content appears in several places.

**Default:** Find the duplication — usually Results restating Methods, or Discussion
restating Results — and cut it. Report the new length.

**Trap:** Cutting the Discussion because it is easiest. It is usually the section carrying
the contribution.

### "The English needs improvement"

**Really asking:** Sometimes exactly that; sometimes the argument is unclear and this is the
polite version.

**Default:** Concede, never argue. Run `sentence-craft.md` and then `ai-tells.md`. If no
specific errors were named, check the argument structure too — reverse-outline each section.

**Trap:** Getting only a language edit when the problem is structural. If a reviewer says
"unclear" about a specific passage, the passage's logic is the suspect, not its grammar.

---

## Structural

### "Results and Discussion are mixed"

**Really asking:** You interpreted in Results, or introduced numbers in Discussion.

**Default:** Separate them. Every interpretation, comparison, and mechanism moves to
Discussion; every number in Discussion must already appear in Results. See `results.md` and
`discussion.md`.

**Trap:** Leaving the participial tails — "…, suggesting that…", "…, confirming…" — in
Results. Those are interpretation. See `ai-tells.md` §2.

### "The limitations are not adequately discussed"

**Really asking:** You listed limitations without consequences.

**Default:** For each limitation, give the direction and rough size of its effect on the
conclusion. "Compliant plan depth was read on a 0.5 m grid, so each reported depth may differ
from the depth on a finer grid by up to [insert the bound and its direction]."

**Trap:** Adding more limitations. The complaint is depth, not count.

---

## Answering Any of These

1. Verify the comment against the manuscript before responding. Reviewers are sometimes
   wrong, and occasionally reviewing a different version.
2. Fix the general fault, not only the named instance. One unreported parameter usually means
   several.
3. State the change and its location.
4. Re-run the relevant gate afterwards — `simulation-reporting.md` if the method changed,
   `paper-review.md` before resubmitting.
