# LaTeX Project Mechanics

**Load when:** the manuscript is in LaTeX and the task touches the bibliography, cross-references, float layout, or the final checks on the file.

**Contents:** Goal · Scope · Required Fields · Reference Identity and Notices · Brace Protection · Preprint to Published · Consistency · Mechanical Checks · Citation Coverage · Never Invent a Citation · Integrity Checks · Definition Order · Document Skeleton · Elsevier Class · Anonymization (Double-Blind Venues) · Promise and Delivery · Checks · Placement Specifiers · Pre-Submission Grep List · Checklist

## Goal

Fix the faults that live in the LaTeX project rather than in the prose: the bibliography,
cross-references, and how floats land on the compiled page.

## Scope

This file covers the manuscript as a **compiled artifact**. For figure design (colour, error
bars, legibility, caption anatomy) use `figures-tables.md`. For table styling and `booktabs`
use `experiments.md` — its `Figure/Table Writing Rules` section is shape-neutral and applies
to journal papers as well, even though the rest of that file is conference-only. Those own
content; this owns mechanics. Where they overlap, they win on design and this wins on
compilation.

Most checks here are mechanical and can be run against the `.tex`, `.bib`, `.blg`, and the
compiled PDF.

---

# Part 1 — Bibliography

## Required Fields

A missing field prints as a malformed entry or a silent omission. Check per entry type.

| Type | Required | Also expected in most journals |
|---|---|---|
| `@article` | author, title, journal, year, volume, pages | number/issue, **doi** |
| `@inproceedings` | author, title, booktitle, year | pages, publisher, **doi** |
| `@book` | author/editor, title, publisher, year | edition, isbn |
| `@incollection` | author, title, booktitle, publisher, year | editor, pages |
| `@phdthesis` | author, title, school, year | type, url |
| `@techreport` | author, title, institution, year | number, url |
| `@standard` / `@manual` | title, organization, year | number, edition — see rule 4 |
| `@misc` | author, title, year | howpublished, url, **urldate** |

Rules:

1. **DOIs are effectively mandatory** for journal targets in your fields — *Energy &
   Buildings*, *Building and Environment*, *Solar Energy*, *LR&T*, *Buildings* all expect
   them. Add the DOI to every entry that has one.
2. A `url` needs an access date. A DOI does not.
3. Standards need edition and year: `EN 12464-1:2021`, not `EN 12464-1`. The edition changes
   the thresholds.
4. Use `@standard` only where the biblatex style supports it. A BibTeX `.bst` may not define
   `@standard`; it can then fall back to `@misc` and drop the organisation and the number. With
   a `.bst`, use `@techreport`, with `institution` the standards body and `number` the
   designation. Either way, check the printed reference in the compiled PDF.

## Reference Identity and Notices

A complete entry can still be the wrong paper. Three faults pass every field check.

1. **The DOI points somewhere else.** A mistyped DOI, or a reference produced by a language
   model, resolves to a real but different work. Compare the title, the year, and the first
   author of the DOI's record with the entry.
2. **The work was retracted, corrected, or carries an expression of concern.** Citing a
   retracted paper as support is an error an editor can find in seconds.
3. **The DOI is not registered at all.**

Run `python3 scripts/bib_check.py refs.bib --tex main.tex --online`. Offline it checks the required
fields above, duplicates, and cited keys with no entry. Online it resolves each DOI and looks
for notices. Read its three notice counts as three: `notice found`, `no notice found in the
sources checked`, and `not checked`. The second is not proof that none exists, and the third
is never read as the second. The `bibliography-auditor` agent runs it and judges each hit.

A retracted work may be cited to discuss its retraction; the sentence then says it was
retracted. Otherwise replace it or remove the claim it carried.

**Cite only what was verified.** A citation is a fact, and the Revision Contract treats it as
one. `.paper/verified-refs.yml` lists the works a draft may cite. This section is the one
definition of the file.

```yaml
version: 1
updated: "2026-08-21"
references:
  - key: "author2021"
    method: doi            # doi | manual
    doi: "10.xxxx/xxxxx"
    title: "The title in the .bib entry"
    first_author: "Author"
    year: 2021
    checked_on: "2026-08-19"
  - key: "en17037"
    method: manual
    title: "The title in the .bib entry"
    checked_on: "2026-08-19"
    note: "Read sections 5 and 6 of the printed standard; title and edition match the entry."
```

```bash
python3 scripts/bib_check.py refs.bib --online --record .paper/verified-refs.yml
python3 scripts/bib_check.py refs.bib --tex main.tex --verified .paper/verified-refs.yml
```

1. **A `doi` row certifies identity only.** The DOI points to a record whose title, and first
   author or year, match the entry. It does not say that the work supports any sentence.
   `--record` writes a `doi` row only when the title and at least one of first author or year
   were compared and matched. With too little to compare, it reports "not checked" and writes
   no row. It writes no row for a work that carries a retraction, withdrawal, removal or
   expression-of-concern notice.
2. **Only the author writes a `manual` row.** Claude may draft one for the author to confirm,
   and never writes it to the file. A row needs `key`, `title`, `checked_on` (an ISO date) and
   a `note` that says how the work was checked. A `manual` row is allowed for a work with no
   DOI, such as a standard, a report or a book, and for a work with a DOI that the author read
   and could not or did not check online. Never write one for a work nobody has read.
3. `--record` always keeps the manual rows. It reports a manual row whose key is not in the
   `.bib` as an orphan row, and keeps it. It never replaces a manual row with a `doi` row, and
   never changes a field the author wrote in it: it adds only the fields that are absent. It
   drops a `doi` row whose entry no longer matches its record, and writes no row when no notice
   source answered for the DOI. It rewrites the whole file, so YAML comments are lost: keep
   notes in `note`. It keeps unknown top-level keys of the list.
4. `--verified` reports every cited key the list does not cover, and every row whose stored
   `doi`, `title`, `first_author` or `year` differs from its entry, `doi` rows and `manual`
   rows alike. It needs PyYAML. A `--tex` file that is not `.tex` is refused, with exit 2. A
   `.tex` file that holds no cited key is reported as "citation coverage: not checked", with
   exit 3. Neither is a pass.
5. **The rule for the writer.** Cite a key only when it is on the list **and** the manuscript,
   the brief or `.paper/` shows that the work supports the sentence. Otherwise write
   `[CITE: what the source must show]`, never a key recalled from memory.
6. A manuscript that cites works and has no list does not pass gate item 13: the item is
   reported as "fail: no verified list", or the author records a waiver. For a Word manuscript
   see `word-manuscripts.md`, Part 1.

## Brace Protection

BibTeX lowercases titles under most styles. Protect anything that must keep its capitals.

- ✗ `title = {Radiance validation for EnergyPlus and TMY data}`
- ✓ `title = {{Radiance} validation for {EnergyPlus} and {TMY} data}`

Protect: proper nouns, software names, acronyms, standard designations, place names,
chemical symbols, and the first letter after a colon if the style demands it.

Do **not** brace the whole title (`title = {{...}}`) — it defeats the style's own casing and
looks inconsistent against correctly-cased neighbours.

## Preprint to Published

The most common bibliography fault in ML-adjacent papers, and an easy reviewer complaint.

1. Search every `arXiv` / `@misc` entry for a published version.
2. If published, replace the entry — do not keep both.
3. Keep the arXiv entry only where genuinely unpublished, and mark it: `howpublished = {arXiv preprint arXiv:XXXX.XXXXX}`.
4. Check the year: the preprint year and the publication year usually differ, and citing the
   wrong one misplaces the work in your own timeline argument.

## Consistency

1. **Author names**: one format throughout. `Ward, G.` or `Ward, Greg`, not both. Watch for
   the same author appearing under two spellings, which splits them in the reference list.
2. **Venue names**: one form per venue. `Energy and Buildings` or `Energy Build.`, following
   the target's style, never mixed.
3. **Duplicate keys or duplicate works** under different keys. Two entries for one paper
   produce two reference-list lines.
4. **Page ranges**: en dash, consistent form. `112--119`, not `112-119` mixed with `112–9`.

## Mechanical Checks

Run these; do not eyeball them.

1. Every `\cite{key}` resolves to a `.bib` entry. Unresolved keys print `[?]` in a numeric style; an author-year style prints a bold key or `(?)`.
2. Grep the compiled PDF text for `?` markers and for `[?]`.
3. Read the `.blg` file. Warnings there name missing fields and empty entries directly.
4. `biber --validate-datamodel` if using biblatex and `biber` is installed. A machine with a
   PDF toolchain often has no LaTeX toolchain, so check before relying on it. Where the
   binaries are missing, do the field and consistency checks by reading the `.bib` directly,
   and say which automated checks could not be run rather than reporting them as passed.
5. Every `.bib` entry is actually cited, or the style will silently drop it and you will not
   notice the ones you meant to cite.

## Citation Coverage

Readers enter a long paper in the middle. Cite at **first mention within each major
section**, not only at the paper's first mention.

Cite on first mention per section:

1. Named software and versions: Radiance, EnergyPlus, DIVA, ClimateStudio, Honeybee.
2. Named models: Perez all-weather sky, Reindl decomposition, Klems basis.
3. Named standards, with edition: EN 12464-1:2021, EN 17037:2018+A1:2021, LM-83-23, WELL v2 with its release (`[insert release]`).
4. Named datasets and weather sources: TMYx, IWEC, Meteonorm, ImageNet, COCO.
5. Named metrics with a defined origin: sDA, ASE, DGP, mel-EDI, CS.

A reader jumping to Methods needs the standard's edition cited *there*, even if the
Introduction already cited it.

## Never Invent a Citation

When drafting and the reference is not to hand, insert a visible placeholder — never a
plausible-looking fake:

```latex
\textcolor{red}{[CITE: field study showing view-direction dependence in open-plan offices]}
```

Grep for `[CITE:` before submission. A red marker left in a draft is embarrassing; a
fabricated citation is misconduct.

---

# Part 2 — Cross-References

## Integrity Checks

1. Every `\ref`, `\cref`, `\Cref`, `\eqref`, `\autoref`, `\pageref`, `\vref` and `\cpageref`
   resolves, each key of a list such as `\cref{a,b}` included. Unresolved prints `??`.
2. Grep the compiled PDF for `??`.
3. No orphan floats: every figure, table, and equation that carries a `\label` is referenced
   at least once in the text.
4. No orphan labels: a `\label` on nothing, usually left after a deleted float.
5. Backward references point at the right target. `As shown in Section 3` after renumbering
   is the classic silent error — use `\cref`, never a hardcoded number.
6. Appendix references resolve after the `\appendix` switch.

## Definition Order

1. Number floats in order of first mention — already required by `figures-tables.md`.
2. **Also check source order.** A figure `\input` early but first referenced late will float
   to the wrong place in the compiled output even though the numbering is correct.
3. A term must be defined before it is used, in *reading* order, not source order. Watch
   `\input`-ed section files reordered in the main document.
4. Define each acronym at first use in the body **and** again at first use in the Abstract —
   they are read separately. See `sentence-craft.md`, Abbreviations.

## Document Skeleton

Faults that make the compiled paper structurally incomplete, easy to miss in the source:

1. `\title` and `\author` defined but **no `\maketitle`** — the compiled paper has no title
   block. Check the class: some venue classes emit it automatically, `article` does not.
2. An `abstract` environment missing, or placed where the class ignores it.
3. `\begin{document}` without the venue's required preamble options (review/camera-ready
   mode, line numbers for submission).
4. Sections out of the shape's canonical order, or a required section absent — conference
   shape expects Related Work; check against the shape definition in `SKILL.md`.

## Elsevier Class

Energy and Buildings, Building and Environment, Solar Energy, and Applied Energy are Elsevier
journals, and Elsevier's `elsarticle` class has its own front matter. A manuscript moved into
it from `article` compiles and looks plausible while breaking in these places.

1. **Front matter sits inside the `frontmatter` environment**: title, authors, affiliations,
   abstract, and keywords. With this class `\maketitle` is not what emits the title block —
   rule 1 of Document Skeleton is the `article` case.
2. **Keywords** go in the class's `keyword` environment, with the separator the class
   defines, not as a hand-typed line.
3. **Corresponding author and e-mail** use the class's own commands, so the footnote marks
   and the e-mail are set by the class. A hand-made footnote is lost at typesetting.
4. **Highlights and the graphical abstract** follow the journal's guide: some journals take
   them as separate files at the portal, and recent versions of the class also provide
   environments for them. Check which the journal wants before building either.
5. **The reference style file must match the journal's reference style.** The class ships
   with a numbered style, `elsarticle-num`, and with name-based and author-year styles.
   Using the numbered file for an author-year journal, or the reverse, is a desk-screening
   fault. Read the style from the guide and record it in `.paper/venue.yml`, `rules`.
6. **Submission mode.** Use the class option the guide asks for at submission — single
   column, double spacing, line numbers where required — not the final two-column layout.
7. Elsevier also publishes single- and double-column templates built on separate class
   files. Use them only if the journal's guide points to them.

Take the class, its documentation, and the exact command and option names from Elsevier's
LaTeX instructions page (`https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions`,
checked 2026-11-15) or from your TeX distribution, and read the class documentation for the
version you have. This skill ships no template, and the command names are deliberately not
listed here: they change between class versions, and a name typed from memory is the fault
this section exists to prevent.

## Anonymization (Double-Blind Venues)

For CVPR/NeurIPS-style review, before submission:

1. No author names, affiliations, or emails anywhere — including PDF metadata
   (`pdfinfo` shows Author/Creator fields; clear them).
2. Acknowledgements and funding removed or anonymised for the review copy.
3. Self-citations in the third person: "Smith et al. [12] showed", never "our previous
   work [12]" or "we previously showed [12]".
4. No identifying artefact links: repository URLs with usernames, dataset hosts, project
   pages. Use an anonymised repository or "available on publication".
5. Supplementary files checked the same way — they are reviewed too.

Greps: `\\author`, `Acknowledg`, `our (previous|prior|earlier) work`, `github.com/`,
`gitlab.com/`, email patterns.

## Promise and Delivery

Where a section introduction promises topics, the subsections must deliver exactly those, in
that order.

- ✗ Intro says "we consider glare, illuminance, and melanopic exposure", then subsections run
  illuminance → melanopic → glare, and glare is one sentence.
- ✓ Promise matches delivery, in order.

Check this after any restructuring. It is the most common structural drift in a revised
paper.

---

# Part 3 — Float Layout

Audit the **compiled PDF**, not the source. These faults are invisible in the `.tex`.

## Checks

1. **Float distance.** No float more than one page away from its first reference. A reader
   should not page backward to find Figure 4.
2. **Isolated float pages.** A page containing only floats, with no body text, usually means
   an over-constrained placement specifier. Loosen it or resize the float.
3. **Subfigure row alignment.** In a multi-row grid, use `[t]` on every subfigure, not `[b]`.
   Mixed anchoring makes captions and images misalign across the row.
4. **Mixed raster and vector in one row.** A PNG and a PDF at nominally the same width often
   differ in height. Set an explicit `\includegraphics[height=...]` so the row normalises.
5. **Caption overflow.** Caption wider than the float, or running past the column, or a
   caption orphaned from its figure across a page break.
6. **Column overflow.** `Overfull \hbox` warnings in the log for tables and equations. In a
   two-column layout these silently push content into the gutter.
7. **Final print size.** Confirm the figure is legible at the size it actually prints, with a
   7 pt minimum on labels — see `figures-tables.md`.
8. **Table caption placement.** Above the table, figure caption below — unless the venue
   says otherwise. Consistent throughout.

## Placement Specifiers

1. `[htbp]` as the default. `[H]` (from `float`) only where the float genuinely must not
   move, and rarely.
2. `[h]` alone is not honoured as written: LaTeX turns it into `[ht]` and may still defer the
   float to the end, which produces the isolated-float-page fault above.
3. Fix placement problems by resizing the float or moving its source position, not by
   escalating the specifier.

---

## Pre-Submission Grep List

Run these on the source, and the PDF ones on `pdftotext output.pdf -` output.

Use `grep -F` (fixed string) for the literal patterns — under `grep -E`, `??` is an empty
repetition and errors out, and `\[?\]` matches a bare `]`, giving false positives. (Under
plain BRE grep, `?` is literal; `-F` removes the ambiguity entirely.)

```bash
# Source-side: authored placeholders and notes (reads .tex files in subfolders too)
grep -rn --include='*.tex' -e '\[CITE:' -e '\[[Ii]nsert' -e 'TODO' -e 'FIXME' -e 'XXX' -e '\\todo' .
# Source-side: chat residue pasted from an assistant
grep -rni --include='*.tex' -e 'I hope this helps' -e 'Certainly!' -e 'Here is the revised' \
          -e 'as an AI' -e 'my last training' .
# Source-side: cross-reference integrity WITHOUT a compiled PDF —
#   first command lists refs with no matching label; second lists labels never referenced.
#   R covers \ref \cref \Cref \eqref \autoref \pageref \vref \cpageref; tr splits \cref{a,b}
R='\\(ref|cref|Cref|eqref|autoref|pageref|vref|cpageref)\{[^}]+\}'
comm -23 <(grep -rhoE --include='*.tex' "$R" . | sed 's/.*{//;s/}//' | tr ',' '\n' | sed 's/^ *//;s/ *$//' | sort -u) \
         <(grep -rhoE --include='*.tex' '\\label\{[^}]+\}' . | sed 's/.*{//;s/}//' | sort -u)
comm -13 <(grep -rhoE --include='*.tex' "$R" . | sed 's/.*{//;s/}//' | tr ',' '\n' | sed 's/^ *//;s/ *$//' | sort -u) \
         <(grep -rhoE --include='*.tex' '\\label\{[^}]+\}' . | sed 's/.*{//;s/}//' | sort -u)
grep -roE --include='*.tex' '\\ref\{[^}]*\}' . | wc -l   # count refs (-o, else counts lines)
# Source-side: a manuscript with no bibliography command prints the message
grep -rqE --include='*.tex' '\\(bibliography\{|addbibresource\{|printbibliography)' . || echo 'no bibliography command found'
# Cite keys with no .bib entry: python3 <skill folder>/scripts/bib_check.py refs.bib --tex main.tex
# PDF-side: compiled symptoms (needs pdftotext)
pdftotext paper.pdf - | grep -Fn -e '??' -e '[?]'     # unresolved refs and cites
# Logs: triage these, do not zero them
grep -n 'Overfull\|Underfull' *.log
grep -n 'Warning\|Error'      *.blg
```

If `pdftotext` is unavailable, open the PDF and search for `??` and `[?]` in the viewer.
Escaped-regex equivalents, if you must use `grep -E`: `\?\?` and `\[\?\]`.

## Checklist

1. Does every `.bib` entry have its required fields and a DOI where one exists?
1a. Was `python3 scripts/bib_check.py refs.bib --online` run, and is every identity mismatch and every notice
   resolved?
1b. For an Elsevier journal: is the front matter inside `frontmatter`, and does the reference
   style file match the journal's reference style?
2. Are proper nouns, acronyms, and standard names brace-protected?
3. Has every arXiv entry been checked for a published version?
4. Is every author name and venue name in one consistent form?
5. Does every `\cite` resolve, and has every `.blg` warning been triaged?
6. Is every named software, model, standard, and dataset cited at first mention **per
   section**, with edition and version?
7. Are there any `[CITE:` or `[insert` placeholders left?
8. Does every `\ref` resolve, with no orphan floats or labels?
9. Does each section intro's promised list match its subsections, in order?
10. Is every float within one page of its first reference?
11. Are subfigure rows top-anchored and height-normalised?
12. Any `Overfull \hbox` in the log?
13. Does the compiled document have its title block (`\maketitle` present where the class
    needs it), abstract, and every section the shape requires?
14. Double-blind venue: no names, no metadata identity, no first-person self-citations, no
    identifying links — in the supplementary too?
