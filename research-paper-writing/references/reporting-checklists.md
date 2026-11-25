# Reporting Checklists

**Load when:** the journal asks for a reporting guideline, or the paper claims to follow one.

**Contents:** Goal · Scope · Pick the Guideline · Fetch the Official Checklist · The Disposition Table · Items That Fail Silently · Submitting It · Common Faults · Checklist

## Goal

Show, item by item, that the manuscript reports what the reporting guideline for its study
type asks for — and say plainly where it does not.

## Scope

Load this when the journal's guide asks for a completed reporting checklist, or when the
paper says it follows a reporting guideline. Those are also the two conditions under which
the Submission Gate checks for one. An author may choose to run it for a study type that
has a guideline — a systematic review, a survey or field study of occupants, a prediction
model — but nothing requires it then, and its absence is not a fault.

A reporting guideline is a list of what a paper of one study type must state. It is not a
quality score and it is not a method. Following one does not make a study sound; it makes the
study checkable.

This file owns the checklist pass and its output file. `simulation-reporting.md` owns the
reporting block for a physics or simulation engine, which no general guideline covers, and
`review-papers.md` owns the review protocol. They are not replaced by a checklist; a checklist
item is usually satisfied by pointing at the text those files produced.

## Pick the Guideline

| Study type | Guideline |
|---|---|
| Systematic review, meta-analysis, scoping review | PRISMA, and its extensions for protocols and scoping reviews |
| Observational study of people: field study, cross-sectional, cohort or case-control design | STROBE |
| Questionnaire survey of occupants, such as a post-occupancy survey | CROSS; STROBE where the design is cohort, case-control or cross-sectional |
| Diagnostic or prognostic prediction model for a health outcome, including machine learning | TRIPOD+AI |
| Randomised trial that allocates participants to groups | CONSORT, and its extensions for other trial designs |
| Any other type | search the EQUATOR Network library |
| ML conference or journal with its own reproducibility checklist | the venue's own checklist, from its call for papers or guide for authors |

The EQUATOR Network (`equator-network.org`) lists each guideline and links to its own site,
where the current checklist is published. These guideline names were confirmed there on
2026-11-15, CROSS on 2026-11-25. Follow the link from EQUATOR instead of trusting an address from memory.

Rules:

1. **The journal's guide decides first.** If it names a guideline or supplies its own
   checklist, use that one. Record which in `.paper/venue.yml`, `rules`, as
   `reporting_guideline`.
2. **Most building-physics and lighting studies have no guideline of their own.** A
   parametric simulation study, a daylight measurement campaign, and a validation study are
   covered by `simulation-reporting.md`, not by a health-research guideline. Do not force one
   onto them, and do not claim adherence to one that does not fit.
3. **A guideline applies only when the design is the one it was written for.** A
   post-occupancy questionnaire survey fits CROSS, the survey checklist; where its design is
   cross-sectional or cohort, STROBE fits too. Mark the items that concern clinical care as
   not applicable, with the reason. A laboratory glare experiment
   in which every participant sees every condition, in a randomised order, is not a
   randomised trial that allocates participants to groups, so the main CONSORT checklist does not fit
   it as it stands. A CONSORT 2010 extension for randomised crossover trials exists (Dwan and
   others, BMJ 2019); it covers the simple two-period, two-sequence design, so check that your
   design matches it before you claim it. Report its design with `ethics-and-participants.md`, Describing the Protocol,
   and claim no guideline unless the journal names one.
4. **A study can need two.** A prognostic model of a health outcome built from a field
   survey may need both the prediction-model checklist and the observational one. A
   machine-learning daylight predictor is not a health prediction model: TRIPOD+AI does not
   apply to it. The venue's own checklist applies, if it has one.

## Fetch the Official Checklist

1. **Download the current checklist from the guideline's own site.** Record its name, its
   version or year, the address, and the date you fetched it.
2. **Never rebuild a checklist from memory**, from a blog post, or from another paper's
   supplementary file. Guidelines are revised, items are renumbered, and a remembered list is
   a list of the items that were easy to remember.
3. If the site cannot be reached, say so, and do not produce a checklist. A checklist
   reconstructed from memory and presented as the official one is a fabricated record.

## The Disposition Table

Write `.paper/checklist-<name>.md`, where `<name>` is the guideline's short name in lower
case, such as prisma or strobe. One row per item of the official checklist, in its order and with its
numbering.

```
# PRISMA 2020 checklist
Source: <address of the official checklist>   Fetched: 2026-11-15
Manuscript: manuscript.tex, version of 2026-11-14

| Item | What it asks | Disposition | Where, or why |
|---|---|---|---|
| 7 | Full search strategy for all databases | reported | Methods 2.2; Supplementary S1 |
| 12 | Effect measures used in synthesis | not applicable | Narrative synthesis; no effect measure was pooled |
| 15 | Certainty of the body of evidence | absent, disclosed | Not assessed. Stated in Limitations, para 3 |
```

Each row takes exactly one of three dispositions.

| Disposition | Meaning | The last column holds |
|---|---|---|
| **reported** | The manuscript states it | the section, and the line or paragraph |
| **not applicable** | The item cannot apply to this study | the reason, in one sentence |
| **absent, disclosed** | The item applies and the study does not have it | where the Limitations paragraph says so |

Rules:

1. **No empty cell.** A row with no disposition, or a disposition with nothing in the last
   column, is a fault. Blank is how an omission hides.
2. **`reported` points to a place.** "See Methods" is not a location. Give the subsection and
   the paragraph or line, and check the text is actually there.
3. **`not applicable` needs a reason the item's own wording supports.** "Not relevant" is not
   a reason. An item that is inconvenient is not inapplicable.
4. **There is no fourth disposition.** An item that applies, is not reported, and is not
   disclosed is a gap in the manuscript. Fix the manuscript, or disclose it and move the row
   to `absent, disclosed`. Do not leave it in the table as "partially".
5. **Write the manuscript first, the table second.** The table records what the text says.
   An item marked `reported` for text that is still to be written is a promise, not a record.
6. **Re-check the locations after every revision.** A section that moved turns a correct row
   into a wrong one without changing a word of the table.

## Items That Fail Silently

A manuscript can pass a quick read of a checklist while missing these. Look for them by name.

1. **Data provenance.** Where every dataset, weather file, and measurement came from, with
   its version and date.
2. **Split discipline, for a predictive model.** How training, tuning, and test data were
   separated, and whether the split respects time and place —
   `statistics-reporting.md`, Predictive Performance.
3. **The reference the result was judged against.** For a validation, what counted as truth
   and how good that reference is.
4. **Who was left out.** Exclusions with counts and reasons, and how the analysed sample
   differs from the recruited one — `ethics-and-participants.md`.
5. **Failures and subgroups.** Cases where the method did worse, not only the average.
6. **What was planned and what was not.** Which analyses were fixed in advance —
   `paper-memory.md`, `analysis_status`.

## Submitting It

1. If the portal asks for the checklist, export the table to the form the journal wants. Some
   supply their own template; fill that, from this table.
2. State in Methods which guideline was followed, with its citation. State it only if the
   table has no empty cell.
3. Do not write "reported in accordance with" a guideline for a manuscript that has `absent,
   disclosed` rows without saying so. "Reported following X, with the exceptions stated in
   Limitations" is the honest form.

## Common Faults

1. A checklist rebuilt from memory, with items missing or misnumbered.
2. `reported` with a section name and no check that the text is there.
3. `not applicable` used for an item that applies and was not done.
4. A checklist completed once and never re-checked after the revision moved the sections.
5. Adherence to a guideline claimed in Methods with no checklist behind the claim.
6. A health-research guideline applied to a simulation study it does not fit.

## Checklist

1. Was the guideline chosen from the journal's guide first, then from the study design?
2. Was the official checklist fetched from its own site, with its version and date recorded?
3. Does every row carry one of the three dispositions, with a location or a reason?
4. Does every `reported` location hold the text it claims?
5. Is every `absent, disclosed` item actually stated in the Limitations paragraph?
6. Were the locations re-checked after the last revision?
7. Does the Methods statement of adherence match what the table shows?
