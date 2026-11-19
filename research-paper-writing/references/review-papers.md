# Review Papers

**Load when:** the paper is a review: systematic, scoping, meta-analysis, bibliometric or narrative.

**Contents:** Goal · Scope · Pick the Review Type First · Structure · The Review Question · Methods: What the Protocol Must Report · Results: The Corpus, Then the Synthesis · Discussion · Cross-Cutting Guides That Still Apply · Common Faults · Checklist

## Goal

Write a review whose search is reproducible, whose synthesis says something the individual
papers do not, and whose conclusions a reader can trace back to the evidence.

## Scope

Load this instead of `methods-journal.md` and `results.md` when the paper's contribution is a
synthesis of existing literature rather than new data. It is a third paper shape, and it does
not mix with the other two.

`literature-and-gap.md` is a different job: it verifies a gap so a **primary** study can claim
one. A review's search is the study. Both files are loaded for a review — that one for
technique, this one for protocol and reporting.

## Pick the Review Type First

The type sets the protocol, the reporting standard, and what the paper is allowed to claim.
Declare it in the Abstract and the Introduction, and do not drift.

| Type | Question | Search | Reporting standard | Claim it earns |
|---|---|---|---|---|
| **Systematic review** | Narrow, pre-specified | Exhaustive, protocol-driven, screened by explicit criteria | PRISMA 2020 | What the evidence base as a whole shows |
| **Meta-analysis** | Systematic review plus a pooled estimate | As above | PRISMA 2020 | A quantitative effect across studies |
| **Scoping review** | Broad — what exists, and how it has been studied | Systematic and documented; critical appraisal optional, and no synthesis of effect | PRISMA-ScR | The extent, range, and nature of the literature |
| **Bibliometric review** | How the field's output is structured | Database query, whole corpus | Query and database stated in full | Publication and citation patterns, not findings |
| **Narrative or critical review** | Interpretive, framed by an argument | Purposive, and declared as such | No formal standard; declare the strategy anyway | An argued position, explicitly the authors' |

Two rules follow from this table.

1. **Never call a narrative review systematic.** A reviewer will check for the protocol and
   the flow diagram, and their absence turns a legitimate paper into an overclaim.
2. **A bibliometric analysis is not a synthesis of findings.** Counting papers, keywords, and
   citations describes a literature. It cannot support a claim about what the literature
   found. Papers that blur these two are rejected for it.

## Structure

Introduction, Methods, Results, Discussion, Conclusion — the journal shape, with different
content in the middle two.

1. **Introduction.** Why the synthesis is needed now. Name the review type and the question.
   State what changed since the last review on the topic and cite it; if one exists and is
   not cited, that is a rejection.
2. **Methods — the review protocol.** The search, the screening, the extraction, the appraisal,
   the synthesis method. See below.
3. **Results — the corpus and the synthesis.** What the search returned, then what the studies
   say when read together.
4. **Discussion.** What the synthesis means, where the evidence is weak, and what the field
   should do next.
5. **Conclusion.** Governed by `conclusion.md`, Journal Shape.

## The Review Question

Frame it before searching, and write it down.

1. Use a structured frame if the field has one. PICO — population, intervention, comparator,
   outcome — transfers to building physics as population/setting, intervention or system,
   comparator or baseline, and outcome metric.
2. State the question at a width the search can actually cover. "Daylighting in buildings" is
   not a review question.
3. Fix the inclusion and exclusion criteria at the same time as the question, not after
   seeing the hits.

## Methods: What the Protocol Must Report

This section is the reproducibility floor. Everything here is checkable, and a reviewer will
check it.

1. **Registration.** If the protocol was registered — PROSPERO, OSF, or an equivalent — give
   the identifier and the date. If it was not, say so. Registration is expected for
   health-related systematic reviews and is increasingly requested elsewhere.
2. **Databases.** Every database searched, by name, with the platform and the coverage dates.
   Scopus, Web of Science Core Collection, Compendex, and Google Scholar are not interchangeable, and for some
   databases the platform or interface matters, so name it, and Google Scholar alone is not a defensible
   systematic search.
3. **The query string, verbatim.** Give at least one database's full Boolean string,
   reproduced exactly, with wildcards and field tags. Put the remaining strings in
   Supplementary. A paraphrased search is not reproducible.
4. **The search date.** The date the search was last run, not the date of writing.
4b. **Queries frozen before screening.** State that the query strings were fixed before
    screening began, and report any query added afterwards as a separate, dated search.
    Tuning a query after reading its results selects the corpus by its conclusions.
4c. **Reported against retrieved.** For each database, the number of records it reported as
    matching and the number retrieved. These are the first numbers in the flow diagram, and
    they are only correct if the two agree or the difference is explained.
4d. **Search validation.** How the search was tested: the known papers it was checked
    against and how many it returned. See `literature-and-gap.md`, Can the Search Find What
    Exists?
5. **Limits applied.** Years, language, document type, subject area. Every limit is a
   potential bias and is named in Limitations.
6. **Supplementary retrieval.** Backward and forward citation tracking, hand-searching of
   specific journals, contact with authors, grey literature, standards, and theses — state
   which were done and which were not. For citation tracking, give the number of rounds and
   the new included records per round, so the reader can see where it ran dry.
7. **Screening.** How many screeners, whether screening was independent and blinded, how
   disagreements were resolved, and the agreement statistic if one was computed. A
   single-screener review is acceptable if declared; an undeclared one is not.
8. **Extraction.** The fields extracted, the form used, and whether extraction was duplicated.
   For building-physics and lighting literature, extract at least: the climate or location;
   the tool and its version; whether each result is measured or simulated; whether the model
   was validated, and against what; the exact metric definition with its threshold, grid, and
   schedule; and the dataset, weather file, or reference building the study used. The last
   field is what reveals that ten studies are one dataset.
9. **Quality or risk-of-bias appraisal.** The instrument used, by name and version, who applied
   it, and how the result feeds the synthesis. For engineering and simulation literature where
   no standard instrument fits, define your own criteria explicitly and apply them uniformly.
10. **Synthesis method.** Narrative synthesis, vote counting, thematic synthesis, or
    meta-analysis. If meta-analytic: the effect measure, the model — fixed or random effects —
    the heterogeneity statistic, and the sensitivity and publication-bias analyses.

Vote counting — tallying how many studies found an effect — ignores study size and quality. If
you use it, say so, and do not let the tally carry a claim about effect magnitude.

## Results: The Corpus, Then the Synthesis

### The corpus

1. **The flow diagram.** Records identified, duplicates removed, records screened, reports sought for
   retrieval, reports not retrieved, reports assessed for eligibility, studies included, with exclusion reasons and counts at the full-text stage. This
   is the PRISMA flow diagram and it is the first thing a reviewer looks at.
2. **The characteristics table.** One row per included study, with the fields a reader needs
   to judge comparability: setting, climate or population, method, sample or model size,
   metrics reported, and the key finding. This table is the review's primary evidence and it
   is worth the page.
3. **The appraisal summary.** How the included studies distribute across your quality
   criteria.

### The synthesis

1. **Organise by concept, never by paper.** A paragraph that begins "Author (2021) found..."
   and ends "Author (2023) found..." is an annotated bibliography, not a synthesis. Each
   paragraph states a finding about the *literature* in its first sentence, then cites the
   studies that establish it.
2. **Report agreement and disagreement with equal weight.** Where studies conflict, say so,
   and where you can, say what differs between them — method, metric definition, climate,
   sample. Explained disagreement is the most valuable output a review produces.
3. **Do not harmonise incomparable numbers.** Two studies reporting "daylight autonomy" under
   different thresholds, grids, or schedules are not reporting the same quantity. Report the
   definitions alongside the values, or do not pool them.
4. **Tabulate wherever a comparison is being made across more than three studies.**
5. **Interpretation stays out.** Report what the synthesis found. What it means belongs in the Discussion.
6. **Count each study once.** A preprint, its conference paper, and its journal version are
   one study. Merge them, keep the most complete version, and report how many records were
   merged. A corpus that counts all three overstates the evidence threefold.
7. **A paper count is not independent replication.** Twelve studies on the same reference
   office, the same weather file, or the same public dataset are close to one observation of
   that case. Report how many distinct buildings, climates, datasets, and research groups
   stand behind a finding, alongside the number of papers.
8. **Use each source for what it is.** Record the role of every source: a primary result, a
   protocol or method paper, a secondary review, a standard, a manufacturer's documentation.
   A protocol does not report results. A review is not cited for a number when the primary
   study is available. Product documentation is not evidence that the product works.
9. **Keep each number with its context.** A value extracted from a study travels with its
   unit, its metric definition, its comparator, and whether it is measured or simulated. A
   number separated from these and set beside another study's number is the harmonisation
   fault in rule 3, arriving through the extraction sheet.
10. **Do not mix measured and simulated results** in one tally or one mean without saying so.
    They answer different questions, and a simulated result from an unvalidated model is a
    weaker kind of evidence than either.

## Discussion

1. State what the synthesis establishes, at the confidence the evidence base supports.
2. State where the evidence is thin, and separate "studied and inconclusive" from "not
   studied". They lead to different recommendations.
3. Address the review's own biases: language limits, database coverage, publication bias,
   the exclusion of grey literature, and single-screener extraction if that is what happened.
4. Make the research agenda specific. "More research is needed" is not a finding. Name the
   condition, metric, or population that is missing, which is exactly the gap taxonomy in
   `literature-and-gap.md`.

## Cross-Cutting Guides That Still Apply

`introduction.md` Journal Shape, `discussion.md`, `conclusion.md` Journal Shape,
`sentence-craft.md`, `ai-tells.md`, `figures-tables.md`, and `paper-review.md` all apply
unchanged. Do not load `method.md`, `methods-journal.md`, `results.md`, or `experiments.md`
for a review, except the `Figure/Table Writing Rules` section of `experiments.md`, which
applies to every paper. This file replaces the middle two and the other two are for primary studies.

`paper-memory.md` applies with one substitution: the evidence cell of a claim ledger row cites
included studies by their corpus identifier, not a figure or table of your own.

## Common Faults

1. A narrative review described as systematic.
2. A search strategy paraphrased instead of reproduced.
3. No search date, so the coverage cannot be judged.
4. No flow diagram, or one whose numbers do not add up.
5. Synthesis organised paper-by-paper.
6. Metrics pooled across incompatible definitions.
7. Bibliometric counts used to support a claim about findings.
8. Quality appraisal performed and then never used in the synthesis.
9. Conflicting studies averaged instead of explained.
10. A prior review on the same topic not cited.
11. One study counted two or three times through its preprint and conference versions.
12. A tally of papers presented as replication when they share one building or one dataset.
13. A review or a protocol cited for a result it did not produce.
14. Queries adjusted after screening, with no record of the change.

## Checklist

1. Is the review type declared, and does the protocol match it?
2. Is the question fixed, with criteria set before screening?
3. Is at least one full query string reproduced verbatim, with all databases and coverage
   dates named?
4. Is the search date given?
5. Is every limit stated, and does Limitations name its bias?
6. Are the screening and extraction procedures stated, including how many people did them?
7. Is there a flow diagram whose counts reconcile?
8. Is there a characteristics table covering every included study?
9. Was quality appraised with a named instrument, and does the appraisal feed the synthesis?
10. Is the synthesis organised by concept rather than by paper?
11. Is disagreement between studies reported and, where possible, explained?
12. Is the research agenda specific enough to act on?
13. Were the queries frozen before screening, and is the search validated against known
    papers?
14. Is each study counted once, with versions merged?
15. Does the synthesis report distinct buildings, climates, datasets, and groups, as well as
    the number of papers?
16. Is every source used in its own role, and every extracted number kept with its unit,
    definition, and measured-or-simulated label?
