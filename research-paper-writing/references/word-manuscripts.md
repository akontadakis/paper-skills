# Word Manuscript Mechanics

**Load when:** the manuscript is a `.docx` file.

**Contents:** Goal · Scope · Use a Field-Based Citation Manager · Before Sending the File · Required Fields Per Entry Type · Automatic, Not Typed · Integrity Checks · Definition Order · Placement and Format · Legibility · Captions · Pre-Submission Checks · Checklist

## Goal

Fix the faults that live in a `.docx` manuscript rather than in the prose: reference
management, cross-references, figures, equations, tracked changes, and what the journal
template requires.

## Scope

This is the `.docx` counterpart of `latex-mechanics.md`. Load exactly one of the two: whichever
the manuscript is actually written in. Most Elsevier, Springer, and Taylor & Francis journals
in building physics, lighting, and energy accept or prefer Word; most CVPR/NeurIPS/ACL-style
venues require LaTeX.

`figures-tables.md` owns figure and table **design**. This file owns how they survive the round
trip through Word, PDF export, and the publisher's typesetter. Where they overlap, that file
wins on design and this one wins on mechanics.

Word manuscripts fail differently from LaTeX ones. LaTeX faults are loud — the build breaks or
prints `??`. Word faults are silent: a field that never updates, a pasted figure that
downsamples, an equation that becomes an image. Every check here exists because the failure is
invisible on screen.

---

# Part 1 — References

## Use a Field-Based Citation Manager

1. Insert every citation through a reference manager — Zotero, Mendeley, EndNote — so citations
   are live fields, not typed text.
2. Typed citations do not renumber. One inserted reference silently breaks every number after
   it, and the fault is invisible until the proof.
3. Fix the citation style once, from the journal's own style file where one exists, and do not
   hand-edit an individual citation afterwards. A hand-edit is overwritten on the next refresh.
4. To check the references themselves — that each DOI points to the paper the entry
   describes, and that none is retracted — export the library to a `.bib` file with the same
   citation keys as the manager, and run this on it:
   `python3 scripts/bib_check.py refs.bib --online --record .paper/verified-refs.yml`.
   The script reads `.bib` only; it cannot read a reference-manager library or the citation
   fields of a `.docx`. See `latex-mechanics.md`,
   Reference Identity and Notices, for the list, for how to read the output, and for the rule
   that a key is cited only when it is on the list and the manuscript, the brief or `.paper/`
   shows that the work supports the sentence.
5. Then compare the cited items of the `.docx` with the list by hand. No script reads the
   citation fields, so gate item 13 reports this part as a manual check, never as a script
   pass. A cited work that is not on the list gets a `[CITE: ...]` bracket or a `manual` row
   that the author writes after reading it.

## Before Sending the File

1. **Update all fields** so numbering and the reference list are current.
2. **Check the reference list count** against the number of distinct citations in the text.
3. **Look for the manager's error markers** — `{Author, Year #123}`, `ERROR!`, `Citation not
   found`. These print in the PDF.
4. Decide whether to **unlink the field codes**, and keep an unlinked copy separate from your
   working copy. Some publishers require unlinked fields; unlinking is one-way, so never unlink
   the file you will revise.
5. **Never send the file with the manager's library unavailable** to a co-author who will
   refresh fields. Refreshing against an empty library destroys the citations.

## Required Fields Per Entry Type

Identical to `latex-mechanics.md`, Part 1 — the required-field table, DOI rules,
preprint-to-published upgrades, capitalisation consistency, and the rule against inventing a
citation all apply unchanged. Load that section for the rules; apply them inside the reference
manager rather than in a `.bib` file.

The one Word-specific addition: check for **duplicate library entries**. Two records for the
same paper produce two reference-list rows and inconsistent in-text numbers. Deduplicate by DOI
in the manager before the final refresh.

---

# Part 2 — Cross-References and Numbering

## Automatic, Not Typed

1. Insert every reference to a figure, table, equation, or section as a Word cross-reference
   field, never as typed text.
2. Use caption numbering for figures and tables so insertion and deletion renumber the whole
   document.
3. Number sections with a multilevel list bound to the heading styles, not by typing numbers
   into the heading text.

A typed "Figure 3" that should now be Figure 4 is the single most common Word manuscript fault
and it is invisible until someone checks every one by hand.

## Integrity Checks

1. Update all fields, then search the document for `Error! Reference source not found`. Any hit
   is a broken cross-reference.
2. Confirm every figure and table is cited in the text at least once, in ascending order.
3. Confirm the numbers in the text match the numbers in the captions after the update.
4. Confirm no figure or table is cited before it is introduced.

## Definition Order

Every symbol, abbreviation, and metric is defined before first use, and the definition order
rules in `sentence-craft.md` and `notation-and-equations.md` apply unchanged. Word gives no
mechanical check for this, so it is read manually, once, in a single pass through the file.

---

# Part 3 — Figures

## Placement and Format

Table design follows `experiments.md`, `Figure/Table Writing Rules`, in any paper shape. Its
design rules hold in Word: minimal ink, no vertical rules, decimal alignment, metric-direction
arrows, restrained highlighting. Its LaTeX commands do not; produce the same look with Word
table styles.

1. Follow the journal's instruction on whether figures sit in the text or in a separate file.
   Many Elsevier and Springer journals want figures in the text for review and as separate
   files at revision or acceptance.
2. Insert figures as vector — EPS, PDF, or EMF — for anything drawn: plots, diagrams, schematics.
   Use raster only for photographs, renderings, and false-colour maps.
3. For raster, meet the publisher's resolution requirement at the **final printed width**, not
   the on-screen size. Follow the journal's artwork instructions, recorded in `.paper/venue.yml`. Where the guide
   gives none, use 300 dpi for photographs and 500 dpi for combination figures, with line art
   as vector, or at 1000 dpi where it must be raster. These are common publisher defaults: check
   the journal's guide.
4. **Never paste from a plotting tool or a spreadsheet through the clipboard.** Word re-encodes
   the paste and the result is a downsampled bitmap. Export the figure to a file, then insert
   the file.
5. **Never resize a figure by dragging it.** Scaling changes the effective resolution and the
   font size inside the figure. Export it at the intended width instead.
6. Set text wrapping to in-line with text. Floating images move unpredictably between Word
   versions and during the publisher's conversion.

## Legibility

The final-print legibility rules in `figures-tables.md` apply. Two of them fail more often in
Word:

1. Font size inside the figure, once the figure is placed at column or page width, must match
   the caption size within a point or two. A figure exported at 8 inches and placed at 3.5
   inches has 8 pt labels that print at 3.5 pt.
2. Line weights scale down with the figure and disappear. Check hairlines at print size.

## Captions

1. Use the caption style so numbering is automatic.
2. Figure captions go below the figure, table captions above the table. This is near-universal.
3. Caption content and self-sufficiency are governed by `figures-tables.md`.

---

# Part 4 — Equations

1. Use the built-in equation editor, or the publisher's stated alternative — usually MathType.
   Do not use a discontinued legacy equation object; publishers cannot process it, and it may
   render as an empty box on another machine.
2. Never paste an equation as an image. It cannot be edited, it does not scale, and most
   publishers reject it.
3. Number displayed equations with a right-aligned field number and cross-reference them.
   Manually typed equation numbers do not renumber.
4. Set inline symbols in the equation editor or in an italic serif face consistent with the
   displayed equations. A symbol typed as body text in one place and set as an equation in
   another is a visible inconsistency.
5. Notation budget, symbol hygiene, and how much of an equation to explain are governed by
   `notation-and-equations.md`.

---

# Part 5 — Journal Template and Submission Form

1. Download the journal's own template and start in it, or move the text into it early. Moving
   a finished manuscript into a template late breaks numbering, captions, and styles.
2. Use styles for headings, captions, and body text. Direct formatting does not survive the
   publisher's conversion.
3. Check line numbering and double spacing if the journal requires them for review.
4. Check the order of the front and back matter against the journal's instructions:
   title page, abstract, keywords, main text, declarations, acknowledgements, references,
   figure captions, tables, appendices. Journals differ, and the order is checked at desk
   screening.
5. A nomenclature table, where the journal uses one, goes where the template puts it — usually
   after the abstract. Its content rules are in `notation-and-equations.md`.
6. Anonymise for double-blind review: remove author names, affiliations, acknowledgements, and
   funding, and **check the file's document properties**, which carry the author name
   independently of the text. This is the Word equivalent of the anonymisation check in
   `latex-mechanics.md` and it is the one people forget.

---

# Part 6 — Tracked Changes and Version Hygiene

Relevant mainly at revision. `responding-to-reviewers` owns what the revision must say; this
owns the file.

1. Produce the two files the journal asks for — usually a marked copy showing changes and a
   clean copy with all changes accepted.
2. Generate the clean copy by accepting all changes in a copy of the file, not by hand.
3. **Delete all comments** from both files. A reviewer-facing comment left in the file is
   read as intended text.
4. Check that no tracked change is still pending in the clean copy. Search the document for
   remaining revision marks after accepting.
5. Check document properties and any hidden text before sending either file.
6. Keep one authoritative copy. Two co-authors editing two copies is not a merge problem in
   Word; it is a lost-edits problem.

---

## Pre-Submission Checks

Run these on the final file, in order. Several need the exported PDF as well.

1. Update all fields, then search for `Error! Reference source not found`.
2. Search for the reference manager's error markers.
3. Search for authored placeholders: `[insert`, `[CITE:`, `TODO`, `TBD`, `XXX`, `??`, `[ref]`,
   `FIXME`. `[insert` is the bracket the Revision Contract leaves for a missing fact.
4. Search for assistant residue pasted in during drafting: `As an AI`, `Certainly!`,
   `Here is the revised`, `I hope this helps`, `Let me know if`.
5. Search for revision scars if this is a revised manuscript: `as suggested by the reviewer`,
   `as requested`, `we now`, `has been revised to`. See `responding-to-reviewers`, Execution
   Rule 7.
6. Confirm every figure and table is cited, in order.
7. Export to PDF and check it: figures legible at print size, equations rendered, no text
   reflowed off a page, no figure split across a page break.
8. Confirm the file opens correctly on a machine without your fonts, reference manager, or
   equation add-in.
9. Confirm word count, abstract length, and figure and table counts against the journal limits.
10. Confirm the anonymisation, including document properties, for a double-blind venue.

## Checklist

1. Are all citations live fields from a reference manager, with no typed citations?
2. Have all fields been updated, with no error markers anywhere in the document?
3. Are all figure, table, equation, and section references automatic cross-references?
4. Are figures inserted from files, unscaled, vector where they are drawings?
5. Do in-figure fonts and line weights survive at final print width?
6. Are equations editable objects, numbered by field, never images?
7. Is the manuscript in the journal's template, using styles rather than direct formatting?
8. Is the front and back matter in the order the journal specifies?
9. For a revision: are the marked and clean copies both produced correctly, with all comments
   deleted?
10. For a double-blind venue: is the document, including its properties, anonymised?
