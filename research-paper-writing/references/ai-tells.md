# AI-Tell Audit

**Load when:** a draft sounds machine-written, or as the last sentence-level pass, after `sentence-craft.md`.

**Contents:** Goal · Freeze Before You Edit · Mechanical Pass First · When To Run This · Why This Matters · Confidence Tiers · 0. Near-Conclusive Artefacts · 1. Overused Register — Tier 1 · 2. Superficial Participial Tails — Tier 1 · 3. Copula Avoidance — Tier 2 · 4. Synonym Cycling — Tier 1 · 5. Negation-Contrast Framing — Tier 1 · 6. False Ranges — Tier 2 · 7. Non-Exhaustive Lists — Tier 2 · 8. Rhythm and Punctuation — Tier 3 · 9. Structural Symmetry — Tier 2 · 10. Section-Specific Openers — Tier 1 · 11. Manufactured Emphasis — Tier 1 · 12. Vague Sources — Tier 1 · 13. Unraised Objections and Fake Alternatives — Tier 2 · 14. Announced and Echoed Openers — Tier 2 · Protected Terms — Do Not Substitute · What NOT To Flag · Voice Calibration · Rejected Advice · Checklist

## Goal

Remove the prose patterns that mark a draft as machine-generated and unconsidered, without
over-editing correct academic writing.

## Freeze Before You Edit

List the frozen set before the first edit, as `SKILL.md` `Revision Contract` defines it:
every number, unit, range with the dash inside it, symbol, citation key, cross-reference,
defined term with its abbreviation, proper name, and hedging verb in the passage. Set those
aside. Everything below operates on what is left.

That ordering is what makes `What NOT To Flag` bind. Read as a list of exceptions at the end
of an editing pass, it loses to the momentum of the pass. Three faults are typical. A range
such as `400–700 nm` is returned as `400 and 700 nm`. A defined term such as
`state-of-the-art baseline` loses half its name. A hedge such as `is consistent with` is
quietly strengthened. Every one of them is already listed as exempt below. Frozen first, none
of those tokens is a candidate at all.

## Mechanical Pass First

Run `scripts/ai_tell_audit.py` before reading for tells. It greps every category below that
can be grepped, computes the section 8 rhythm metrics, and prints the raw hits with file and
line. Its rule ids are the section numbers in this file.

```bash
python3 scripts/ai_tell_audit.py sections/*.tex --context
```

Two rules govern what you do with its output.

1. **The output is evidence, not a verdict.** A hit is a candidate. This file decides it, and
   `What NOT To Flag` overrides the script in every case. The script cannot see a protected
   technical term it does not know, cannot tell a real range from a false one, and cannot tell
   `enhance` used technically from `enhance` used as filler.
2. **Report the counts, with the lines.** "Audited, clean" without the pasted output is not an
   audit. The same rule governs the auditor agents — see `paper-review.md`,
   `Independent Review`.

## When To Run This

Run **after** `sentence-craft.md`, and only once paragraph structure is settled. This pass
edits diction and rhythm; restructuring invalidates it.

## Why This Matters

The honest reason is not detector evasion. It is that these patterns read to a reviewer as
prose nobody thought about: filler adjectives that assert importance instead of showing it,
participial tails that assert a consequence the data never tested, and four names for one
object. Fix them because they are bad writing. A lower detector score is a side effect, not
the target.

**This file never trades clarity for unpredictability.** Any advice to loosen transitions,
break the one-paragraph-one-message rule, or add colour to sound human is rejected — see
`Rejected Advice` at the end.

## Confidence Tiers

A tell is not a verdict. Every numbered section below carries a tier that says what a
single hit is worth, and the tier decides whether you may act on one instance.

| Tier | What one hit means | Act on |
|---|---|---|
| **Tier 0** | Conclusive. The text was pasted from a chat interface or a generator and never read. | A single hit. No corroboration needed. Section 0 only. |
| **Tier 1** | Distinctive. Rare in careful technical prose, frequent in generated prose. | Two or more in the same passage. |
| **Tier 2** | Common but overused, and often correct in its technical sense. | A cluster, and only after checking the term against `Protected Terms`. Never on sight. |
| **Tier 3** | Ordinary English whose elevated rate is visible only across a corpus. | Nothing on a single hit. Report the measures as a diagnostic; change a passage only when it is flat and another tell clusters there. |

Two rules govern the tiers.

1. **Only Tier 0 acts on one hit.** For every other tier the cluster rule in
   `What NOT To Flag` holds: one `crucial`, one em dash, one 22-word sentence means nothing.
2. **The tier never overrides `What NOT To Flag`.** A Tier 1 hit inside a protected term,
   a real range, or correct hedging is not a hit at all. The tier raises how seriously you
   read a hit; it never converts an exempt construction into a fault.

`scripts/ai_tell_audit.py` prints the tier beside every rule id, so its output can be read
in tier order: clear Tier 0, then read the Tier 1 clusters, then leave Tier 3 alone.

## 0. Near-Conclusive Artefacts

**Tier 0.** These need no corroboration and no cluster. One instance is evidence that the
text was pasted from a chat interface or produced by a generator and never read. In a
manuscript the cost is not stylistic. A leaked citation marker in a submitted PDF, or an
`[Insert citation]` left in a Methods paragraph, reaches an editor as evidence of
undisclosed generation, and no later pass repairs that. Clear these before anything else.

| Artefact | Examples |
|---|---|
| Leaked tool and citation markup | `oaicite`, `oai_citation`, `contentReference`, `attributableIndex`, `turn0search0`, `【...】` citation brackets, `[cite: 1]`, `[span_1](start_span)` |
| Chatbot tracking parameters on a pasted link | `?utm_source=chatgpt.com`, `utm_source=perplexity` |
| Unfilled template placeholders | `[Your Name]`, `[Insert citation]`, `[Institution]`, `[Company]`, `[Date]` |
| Assistant scaffolding | `Let me know if you need any changes`, `Here is the revised version`, `I hope this helps`, `Would you like me to` |
| Model disclaimers | `As an AI language model`, `I do not have access to real-time information` |
| Raw markdown where nothing renders it | literal `**bold**` or `##` inside a `.tex` body or a Word paragraph |
| Humaniser residue | a standard term swapped for a dictionary synonym (`counterfeit consciousness` for `artificial intelligence`), Unicode look-alike characters, an abrupt drop in register |

Two constructions look like artefacts and are not.

1. **A deliberate gap marker.** `[insert the source for the 12% shortfall]`, `[CITE: ...]`,
   `[figure needed from the Q1 run]` are notes for the author: the Revision Contract's
   bracket, or the author's own. A missing source is written `[CITE: ...]`, never as a
   made-up key. They are not machine residue. Keep them until the fact arrives, and list
   them as unresolved placeholders instead of deleting them. `ai_tell_audit.py` reports
   `[insert` and `[CITE:` under `P0`, "Unresolved placeholder: fill it before submission, do
   not delete it". None may reach the submitted paper, and the Submission Gate needs that
   count to be zero.
2. **A citation that resolves to the wrong paper.** That is a bibliography fault, and
   `bibliography-auditor` owns it. This section owns the markup, not the reference.

Absence proves nothing. Current models rarely emit model disclaimers, so a clean Tier 0
pass is not evidence that a human wrote the text. It means only that nothing was pasted.

`scripts/ai_tell_audit.py` reports these as `T0`. Unlike every other rule in this file, a
`T0` hit is not a candidate for judgement. Delete it. "Delete it" applies to `T0` only; a
`P0` placeholder is filled, never deleted.

## 1. Overused Register — Tier 1

These words carry near-zero information in a technical manuscript. Most assert significance
that the sentence should demonstrate instead.

| Tell | Fix |
|---|---|
| crucial, vital, essential, key (adj.) | state the consequence from the source, or write an `[insert ...]` bracket for it; or cut |
| delve into | examine, analyse |
| underscore, highlight (v.), emphasise (v.) | cut, or flag the claim verb for calibration (Hedging) |
| enhance, boost | increase, improve — and give the magnitude |
| leverage (v.) | use |
| interplay | interaction — only if you actually resolved one |
| landscape, ecosystem, realm, space (abstract) | name the actual thing: `the literature on X`, `current practice` |
| showcase, demonstrate the potential of | show, or cut |
| pivotal, paramount, profound | cut |
| tapestry, testament to, symphony | cut entirely |
| align with | match, agree with, follow |
| valuable, meaningful, robust (as praise) | cut, or say for whom and how much |
| multifaceted, nuanced, complex (unquantified) | say which facets |
| paradigm shift | cut unless you mean Kuhn |
| foster, garner, spearhead | cause, gather, lead |
| seamless(ly), holistic | cut, or state what actually joins up |
| comprehensive (unquantified) | give the coverage: how many cases, which conditions |
| meticulously, rigorously (as self-praise) | cut — the Methods show it or they do not |
| elucidate | explain, show |
| cutting-edge, state-of-the-art (as decoration) | cut; keep `state-of-the-art` only as the technical SOTA-comparison term |
| unprecedented, groundbreaking, revolutionary | cut, or give the prior art it exceeds |
| streamline, harness, bolster, empower | simplify, use, support, enable — or cut |
| innovative, transformative, sophisticated, synergy | cut, or name the property and its measure |
| methodology (meaning *method*) | method — keep `methodology` for the study of methods, and as a section heading where the venue uses it |

`robust optimisation` is a technical term. `a robust framework` is filler. See
`Protected Terms` below.

Two carve-outs from the table above, both literal rather than filler:

1. **`highlight` as a typographic operation** — shading a table cell, marking the best value
   in a column. `figures-tables.md` and `experiments.md` both use it this way. The tell is
   `highlight` meaning *show* (`this highlights the importance of`), not `highlight` meaning
   *apply emphasis to a cell*.
2. **`enhance` where the field uses it technically** — contrast enhancement, image
   enhancement, enhanced sky models. The tell is `enhance` as a vague synonym for improve.

**Stacked praise adjectives** (script rule `T1c`, Tier 2). Three near-synonym adjectives in a
row — `a comprehensive, sophisticated, and innovative framework` — say less than one measured
property. Keep the one the results support and give its measure, or cut all three. This is
not the three-part enumeration that `What NOT To Flag` protects: that rule covers three
*items* with distinct content, such as three reasons or three measured quantities. Three
adjectives that could be swapped for each other are padding.

## 2. Superficial Participial Tails — Tier 1

The most damaging tell in a scientific paper, because it smuggles an untested claim into a
sentence that looked descriptive.

Watch for a comma followed by `-ing`: `highlighting`, `underscoring`, `emphasising`,
`demonstrating`, `ensuring`, `reflecting`, `showcasing`, `contributing to`, `paving the way for`.

- ✗ `Compliant plan depth fell to 3.1 m under the worst-case view direction, highlighting the dominance of view direction.`
- ✓ `Compliant plan depth fell to 3.1 m under the worst-case view direction.` — then, if the dominance claim is
  earned and this is Discussion, argue it in its own sentence with its evidence.

Rules:

1. In Results, delete the tail. It is interpretation, banned there by `results.md`.
2. In Discussion, promote the tail to a full sentence and attach its evidence.
3. Keep participial phrases that state a mechanism you actually tested, or a plain fact
   (`falling below the 250 lx threshold at 14:00`).

## 3. Copula Avoidance — Tier 2

Inflated linking verbs. Use `is` or `has`.

| Tell | Fix |
|---|---|
| serves as, stands as, functions as | is |
| represents | is |
| boasts, features, possesses | has |
| constitutes | is |

`X represents an increase of 12%` → `X is 12% higher`.

## 4. Synonym Cycling — Tier 1

Language models substitute synonyms to avoid repetition. Academic writing requires the
opposite: one term per concept, repeated.

- ✗ `the model ... the framework ... the system ... our architecture` — all the same object.
- ✓ Pick the canonical noun, repeat it, use pronouns between.

This is the diagnostic form of the terminology rule in `sentence-craft.md` checklist item 9
and SKILL.md Execution Rule 1. Repetition of a defined term is correct, not lazy.

## 5. Negation-Contrast Framing — Tier 1

`not X, but Y` and its variants state the positive claim indirectly.

- ✗ `The limiting factor is not the climate, but the view direction.`
- ✓ `View direction, rather than climate, is the limiting factor.`

The rewrite carries the same claim and no more. A shorter version that says climate has no
effect reads better and is wrong: the source never said that. That is the sharpening the
Revision Contract forbids.

Also in this family: `it is not merely X, it is Y`, `rather than simply X, this Y`.

Final-pass grep: `is not.*but`, `not merely`, `not just`, `rather than simply`.

Keep a genuine contrast where the negated item is a real, named alternative the reader
expects. The fault is the rhetorical flourish, not contrast itself.

## 6. False Ranges — Tier 2

`from X to Y` where X and Y are not endpoints of any scale.

- ✗ `from glare control to occupant satisfaction`
- ✓ `including glare control and occupant satisfaction`

Keep `from` and `to` for real ranges: `from 400 to 700 nm`.

## 7. Non-Exhaustive Lists — Tier 2

`benchmarks for X, Y, Z` implies the list is complete. Write `benchmarks such as X, Y, Z`
when it is not.

## 8. Rhythm and Punctuation — Tier 3

Uniform sentence length is a strong tell and is also genuinely harder to read. In a single
manuscript this section is a diagnostic: report the measures, and change a passage only when
it reads flat and another tell clusters there.

| Check | Target |
|---|---|
| Mean sentence length | 15–25 words (from `sentence-craft.md`) |
| Spread | in any passage over ~150 words, longest minus shortest ≥ 20 words |
| Uniform runs | no three consecutive sentences within ±5 words of each other |
| Short sentences | at least one sentence ≤ 10 words per ~150 words |
| Em dash | at most one per 300 words |
| Exclamation mark | zero in body text |

**Procedure text is exempt from the length targets.** A written procedure in Methods — a
measurement sequence, a simulation setup, a calibration — is short, even sentences by design,
and varying their length to sound less uniform makes the procedure harder to follow. The
mean, spread, uniform-run, and short-sentence rows do not apply to it; the em dash and
exclamation rows still do. Run the script on such text with `--section methods`. Everything
else in Methods, including the rationale for a design choice, is ordinary prose and is
measured as usual.

Mean and spread are separate targets. Hitting a 15–25 word average while every sentence sits
at 19 words fails this section.

Both spread rules use the same ~150-word window. Measured over a shorter passage they
over-constrain each other: an 80-word window at a 15-word mean holds about five sentences,
and forcing one ≤ 10 and one ≥ 30 leaves the remaining three sharing ~40 words, which then
trips the uniform-run rule.

**Where the targets conflict, the mean yields to the spread.** A passage averaging 26 words
with real variation reads better than one pinned at 19. Do not lengthen sentences to raise
the mean, and never pad a sentence to hit a number here — these are diagnostics for a draft
that feels flat, not a specification to write against.

## 9. Structural Symmetry — Tier 2

1. Paragraphs of near-identical length throughout a section.
2. Every paragraph built `topic sentence → three evidence sentences → restatement`. The
   closing restatement is usually deletable.
3. Three consecutive paragraphs opening `Moreover` / `Furthermore` / `Additionally`.
4. Over-balanced hedging: giving both sides equal weight when your data favours one.

## 10. Section-Specific Openers — Tier 1

| Section | Banned opener | Instead |
|---|---|---|
| Abstract | `In recent years,` `With the rapid development of` | the problem, in one sentence |
| Introduction | `Since the dawn of` `It is widely acknowledged that` | a specific cited fact |
| Results | `As can be seen from Figure 3,` | `Figure 3 shows` — or state the finding and cite the figure in parentheses |
| Discussion | `Despite these limitations,` as a transition formula | name the limitation and its consequence |
| Conclusion | `In conclusion,` `This paper has presented` | the finding |

**Empty transitions** (script rule `T10c`, Tier 2). `With that in mind,` `Building on this
foundation,` `Taking this a step further,` `With this in place,` name no relation between two
sentences. `Building on this result, we refined the grid` is different: it names what is
built on, and it is left alone. Replace each with the relation it hides — cause, contrast, consequence, or
refinement, per `SKILL.md` Global Principle 4 — or cut it and let the sentence stand.

## 11. Manufactured Emphasis — Tier 1

1. **Aphorism formulas**: `X is the Y of Z`, `the architecture of X`, `the language of X`.
2. **Staccato drama**: a one-clause sentence dropped for effect after a long one. One per
   paper at most; zero is safer.
3. **Fake-insight markers**: `essentially`, `fundamentally`, `at its core`, `the key insight is`,
   `the reality is`, `the truth is`. If the insight is real, state it without the label.

## 12. Vague Sources — Tier 1

The most consequential tell in an academic manuscript, because it is simultaneously a style
fault and an unverified claim about the literature.

| Tell | Why it fails |
|---|---|
| `studies show`, `research indicates`, `many researchers` | a claim about the literature with nothing behind it |
| `it is widely acknowledged that`, `it is well known that` | asserts consensus without evidence of one |
| `some studies suggest`, `experts agree` | names nobody, so nobody can check it |
| `little attention has been paid to` | the classic unverified gap claim |

The fix is not a synonym. Name the studies and cite them, or drop the claim to what you can
defend from your own reading: `we are not aware of a study that reports X`.

This is the same fault `literature-and-gap.md` exists to prevent, arriving through the prose
rather than through the framing. A hit here is a claim-ledger row, not only an edit: it
carries `needs evidence` until the citations exist. See `paper-memory.md`.

## 13. Unraised Objections and Fake Alternatives — Tier 2

Two forms of drafting residue. Both put an argument in the paper that nobody made, then
answer it.

**Answering an objection no one raised.** `This is not really about X`, `to be clear`,
`this is not to say`, `one could frame it differently, but`. If the objection is real and
attributable, name whose it is and answer it properly — that is what `discussion.md`
`Comparing With Literature` is for. If it is not, delete the defence and state the claim.

**Rejecting an alternative no reader proposed.** `A tempting approach would be Y, but that
would fail because Z.` One of these can be a genuine design-rationale sentence. Several
short, unrelated rejections are a sign that earlier drafting decisions were left in the text.
Ask what each one adds. If it only records a decision you already made, rewrite the paragraph
around the constraint itself.

A methods paper that genuinely rejected an alternative should say so in Methods, with the
reason and the evidence, not in a subordinate clause elsewhere.

## 14. Announced and Echoed Openers — Tier 2

Three related faults, all of which spend a sentence saying nothing.

1. **Announcing instead of stating.** `In this section, we discuss the results of the
   parametric sweep.` Acceptable once, in the Introduction roadmap. Anywhere else, delete it
   and state the result.
2. **Echoing the heading.** A heading followed by a sentence that restates the heading.
   `2.4 Grid convergence` / `We now consider grid convergence.` Delete the sentence; the
   heading already did that work.
3. **Generic positive endings.** A Conclusion or Discussion paragraph closing on vague
   optimism — `this opens promising avenues`, `the future of the field is bright`, `this
   represents an important step`. End on the last concrete finding instead. Where real
   further work exists, `conclusion.md` says how to state it specifically.

## Protected Terms — Do Not Substitute

Never apply the tables above inside a technical term, a standard name, a quoted passage, a
title, or a defined variable. Check the term against the field before editing.

**Daylighting and building physics**: sDA, ASE, UDI, DGP, DGI, UGR, GR, mel-EDI, melanopic
ratio, EML, CS, daylight factor, daylight autonomy, illuminance, luminance, luminous efficacy,
Radiance, `rtrace`, `rpict`, `gendaymtx`, `rfluxmtx`, `dctimestep`, ambient bounces, BSDF,
Klems basis, tensor tree, EPW, TMY, TMYx, AMY, Perez all-weather sky, CIE overcast,
EnergyPlus, view factor, maintenance factor, reference plane, calculation grid.

**ML / CV / NLP**: robust optimisation, attention, embedding, transformer, ablation, baseline,
ground truth, feature map, latent space, fine-tuning, zero-shot, benchmark, checkpoint,
learning rate, batch normalisation.

**Statistics**: significant (statistical sense), power, effect size, confidence interval,
robust standard error, mixed model, random effect, censoring.

Also protected: anything inside math environments, `\cite{}`, `\ref{}`, `\label{}`, code and
algorithm blocks. See `sentence-craft.md`, `Editing Around Protected Markup`.

## What NOT To Flag

Over-editing is the failure mode of this pass. These are **correct** and must be left alone.

1. **En dashes in ranges, minus signs, and compound names.** `400–700 nm`, `−5 °C`,
   `Okabe–Ito`, `Perez all-weather`. A blanket dash ban corrupts units and citations.
   Follow `sentence-craft.md` on ranges instead.
2. **A three-part enumeration.** `This problem is challenging for three reasons. First...
   Second... Finally...` is a prescribed structure in `introduction.md`. Groups of three are
   only a tell when the content was padded to reach three.
3. **A repeated technical term.** Repetition of a defined term is required. Do not vary it.
4. **Correct hedging.** `tended to increase`, `is consistent with`, `suggests` on modelled
   data are all right per the evidence ladder in `sentence-craft.md`. Do not "strengthen"
   them.
5. **Heading case.** Title case or sentence case is set by the venue style sheet.
6. **Quote direction.** Curly or straight is set by the typesetter, not the author.
7. **Polish itself.** Clean grammar and consistent style are not evidence of generation.
8. **Passive voice where the actor is irrelevant.** `The samples were stored at 4 °C.`
9. **Formal register.** Plain, neutral, impersonal prose is the correct human voice for a
   manuscript. Do not add personality, asides, humour, or uneven rhythm to sound human.

**Cluster rule**: act on clusters of tells, not isolated ones. A single em dash, a single
`crucial`, or one 22-word sentence means nothing. **Section 0 is the one exception**: a
Tier 0 artefact is conclusive on its own and is deleted without a second hit.

## Voice Calibration

If the author supplies two or three of their own published papers, calibrate to those instead
of to a generic profile:

1. Measure their actual sentence-length mean and spread.
2. Note their habitual connectors (`however` vs `whereas` vs `by contrast`) and match them.
3. Note their punctuation density — semicolons, parentheses, dashes per 1000 words.
4. Note whether they write `we` or impersonal, and hold it.

A draft that matches the author's own published rhythm is both more honest and more
consistent with their record than one edited toward an average.

## Rejected Advice

Recorded so it is not re-imported from the source material:

1. **"Let transitions be imperfect; let a paragraph carry two ideas."** Rejected. It
   deliberately degrades writing and contradicts SKILL.md Global Principles 1 and 4.
2. **"Add observational asides to data description"** (`Interestingly, the loss surface
   resembles...`). Rejected. `results.md` bans interpretation in Results.
3. **"Prefer vivid informal verbs"** (`sift through the activation traces`). Rejected. Less
   precise, wrong register.
4. **Blanket em/en dash ban.** Rejected — breaks ranges, minus signs, compound names.
5. **Detector-score targets.** Rejected. Uncalibrated, and the wrong objective.

## Checklist

1. Any Tier 0 artefact left — leaked markup, a tracking parameter, an unfilled
   placeholder, assistant scaffolding? One is enough. Clear these first.
2. Any word from the overused-register table left, outside a protected term?
3. Any `, -ing` tail asserting an untested consequence?
4. Any `serves as` / `represents` where `is` works?
5. One canonical noun per concept, repeated?
6. Any `not X, but Y` left? (grep `is not.*but`, `not merely`, `not just`)
7. Any `from X to Y` that is not a real range?
8. Diagnostic only: do the rhythm measures show a flat passage, with another tell in it?
   Report it; change it only then. Procedure text in Methods is excepted.
9. Any banned section opener, or a transition that names no relation?
10. Any `studies show` / `it is widely acknowledged` with no citation behind it, and is each
    such claim in the ledger as `needs evidence`?
11. Any objection answered that nobody raised, or alternative rejected that nobody proposed?
12. Any sentence that only announces the next point or restates its own heading?
13. Any paragraph ending on vague optimism instead of the last concrete finding?
14. Everything in `What NOT To Flag` left untouched?
15. Were the mechanical-pass counts reported with their lines, rather than summarised as
    "clean"?
