# Discussion Writing Guide

**Load when:** writing or revising a Discussion or a limitations paragraph, in the journal and review shapes.

**Contents:** Goal · Hard Rules · Structure · Opening Paragraph · Comparing With Literature · Mechanism · Limitations · Implications · Common Mistakes · Checklist

## Goal

Turn results into meaning: answer the question asked, place it against the literature, bound it honestly.

Use this guide for journal-shape papers (IMRAD). Conference-shape papers fold this into
`experiments.md` and `conclusion.md`. Do not load both. When the journal combines Results and
Discussion in one section, see `results.md`, When the Journal Combines Results and Discussion.

## Hard Rules

1. No new results. Every number here was already reported in Results.
2. No claim stronger than the evidence. If the data cannot carry it, weaken or cut it.
3. Correlation is not mechanism. A proposed mechanism is labelled as proposed.
4. Limitations are stated by you, not left for the reviewer.
5. Present tense for what is now known; past tense for what this study did.

## Structure

Five moves, in this order. Each is one or more paragraphs.

1. **Answer** — the question from the Introduction, answered in one or two sentences. No preamble, no summary of what you did.
2. **Compare** — how this sits against prior work: agreement, disagreement, extension. Explain disagreements, do not just note them.
3. **Explain** — the mechanism or reason behind the main finding, flagged as interpretation.
4. **Bound** — limitations, and what each one does to the conclusions.
5. **Apply** — what follows for practice, design, standards, or the next study.

## Opening Paragraph

1. First sentence answers the research question directly.
2. Second sentence gives the single strongest piece of supporting evidence.
3. Do not open with "In this study, we..." or a recap of the method.

Example shape. The study is invented; it is the journal study used in `abstract.md` Version 4.

> These simulations suggest that view direction, more than climate, decided whether a desk
> met the melanopic target in the side-lit offices we simulated. The worst-case view direction cut the mean
> compliant plan depth from 5.8 m to 3.1 m, a loss larger than the 0.9 m spread across the
> four climates.

## Comparing With Literature

1. Name the study and what it found before saying how you differ.
2. When you disagree, give a candidate reason: different population, different boundary condition, different metric, different model.
3. Distinguish "we measured something different" from "we measured the same thing and got another answer".
4. Do not cite agreement selectively. If a study contradicts you, address it.
5. State the prior position in a form its own authors would recognise before criticising it.
   A position rebutted in a weakened form is not rebutted.
6. Label which kind of criticism you are making:
   - **Internal** — it fails by its own standards or assumptions.
   - **External** — its standards or assumptions do not hold in your conditions.
   Internal criticism is stronger and needs no shared premise. External criticism obliges you
   to defend your own assumptions in the same paragraph.

## Mechanism

1. Mark it as interpretation: "a likely explanation is", "this is consistent with", not "this shows".
2. Prefer a mechanism your own data can partly test, and say which part it tested.
3. If two mechanisms fit equally, say so, and say what would separate them.
4. Do not build the paper's main argument on a finding from an analysis chosen after the
   results were seen. Discuss it as exploratory, say that the choice came after the data,
   and say what a planned test of it would need. `paper-memory.md`, `analysis_status`.

## Limitations

Write these as a paragraph, not a defensive list. For each one, state the limit **and** its consequence.

1. **Scope** — what setting, climate, population, or geometry the result is bounded to.
2. **Method** — assumptions in the model or measurement that could move the answer, and in which direction.
3. **Data** — sample size, coverage, censoring, resolution. For a study with participants,
   `ethics-and-participants.md` decides which sample limits must be named here, and every
   bound recorded in `.paper/claims.yml` as `bounded_to` appears in this paragraph.
4. **Known bias** — anything you found and did not fully remove. Disclose it with its magnitude and sign.

When `.paper/design.yml` exists, every threat it records with `decision: accept` or `decision: reduce`
appears in this paragraph, with the consequence the record gives; for `reduce`, with the bias
that remains. A threat accepted at design time and
absent here is an omission.

Rules:

1. Give direction and rough size, not just existence: "compliant plan depth was read at the last passing point of a 0.5 m grid, so each reported depth may understate the true depth by up to 0.5 m".
2. Do not list a limitation you already fixed.
3. Do not use limitations to smuggle in a defence of a weak result.
4. Do not end the limitations paragraph on an apology. End on what remains valid despite them.

## Implications

1. Say what someone should do differently, and who.
2. Keep the leap short. Do not go from a simulated room to national policy.
3. If the implication depends on a limitation, name it in the same sentence.

## Common Mistakes

1. Restating Results paragraph by paragraph.
2. Over-claiming generality from one site, one geometry, or one dataset.
3. Introducing a supplementary number that was never in Results.
4. Burying the answer in paragraph four.
5. Treating a limitation section as a ritual, with no consequence attached to any item.
6. Future work that is a wish list rather than the next necessary experiment.

## Checklist

1. Is the research question answered in the first two sentences?
2. Does every number here already appear in Results?
3. Is every mechanism explicitly labelled as interpretation?
4. Is each limitation paired with its consequence and direction?
5. Are contradicting studies addressed, not just the agreeing ones?
6. Would each claim survive a reviewer asking "which figure shows that?"
7. Is any claim in Abstract or Introduction left unsupported by this section? If so, fix the claim, not the Discussion.
