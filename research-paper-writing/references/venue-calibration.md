# Venue Calibration

**Load when:** a venue is chosen: to record its rules, and to learn its conventions from a corpus of its papers.

**Contents:** Goal · Why This Exists · Two Hard Limits · Corpus · Per-Paper Style Card · Aggregate to a Venue Profile · Using the Profile · What This Is Not · Checklist

## Goal

Learn a target journal's actual writing conventions from a small corpus of its recent papers,
then write to those conventions instead of to a generic template.

## Why This Exists

Journal instructions to authors describe format, not writing. They do not say whether this
journal states contributions as a numbered list or embeds them in prose, whether the
Introduction carries the literature or a separate section does, or whether Discussion is two
pages or six. Reviewers for that journal know these conventions without being able to state
them, and a paper that violates them reads as out of place before anyone assesses the science.

`submission-package.md` Journal Selection decides *which* venue. This file decides *how that
venue writes*.

## Two Hard Limits

Read these before building anything.

1. **Convention only, never content.** A style card records how a paper is organised and what
   rhetorical moves it makes. It never records, quotes, or paraphrases a finding, a sentence,
   a statistic, or a phrasing. You are extracting structure, not text. A card containing a
   quoted or paraphrased sentence is discarded and re-made.
2. **The venue does not override the rules that protect the science.** Where a corpus habit
   conflicts with this skill, the skill wins, and the conflict is recorded rather than
   silently resolved. Specifically: claim-evidence alignment, the verb-to-evidence ladder, the
   statistics triad, units, provenance, ethics reporting, and gap verification are not
   negotiable because the corpus is loose about them. Journals publish papers with bare
   p-values and unverified gap claims; calibrating to that is calibrating to a defect.

Everything else — structure, ordering, length, hedging register, contribution placement,
figure conventions, section naming — is fair to calibrate.

## Corpus

1. **Six to ten papers from the target journal**, published in the last three to five years.
   Fewer than five and you are calibrating to individual authors rather than to the journal.
2. **Match the method type.** A simulation paper calibrated against the journal's field-study
   papers learns the wrong conventions. Where the journal publishes both, split the corpus and
   note which subgroup each pattern came from.
3. **Optional second corpus**: highly-cited papers from the field at large, or two or three of
   your own or your group's published papers. Keep these labelled separately. The target
   journal carries the most weight; the others are tie-breakers.
4. Get them legitimately — your library, the publisher, or an open-access copy. See
   `scripts/fetch_oa_pdf.py`.

## Per-Paper Style Card

One card per corpus paper. Every field is a category or a description of a move. No prose from
the paper appears anywhere.

```yaml
paper_id: v01
journal: "Journal A"
role: target            # target | field | own
year: 2024
method_type: simulation # simulation | field | lab | mixed | review
doi: "10.1016/..."

abstract:
  moves: [context, gap, objective, method, headline_finding, implication]
  sentences: 8
  words: 210
  numbers_in_abstract: 3          # how many quantitative results appear
  first_person: false

introduction:
  paragraphs: 6
  hook: policy               # phenomenon | policy | puzzle | debate | empirical_gap
  literature_location: integrated   # integrated | separate_section | both
  gap_stated_in_paragraph: 4
  contribution_placement: late      # early (p2-3) | late (p5+) | embedded
  contribution_format: prose        # numbered | prose | bulleted
  roadmap: absent                   # explicit | narrative | absent

methods:
  subsections: [design, case, model_setup, metrics, validation]
  named: "Methodology"              # what the journal calls this section
  parameter_tables: 2
  provenance_stated: partial        # full | partial | absent
  validation_present: true

results:
  interpretation_present: false     # does Results stay clean of meaning?
  figures: 7
  tables: 3
  primary_vehicle: figures          # prose | figures | tables | mixed

discussion:
  paragraphs: 9
  compares_to_literature: true
  limitations: own_subsection       # own_subsection | one_paragraph | scattered | absent
  practical_implications: true

conclusion:
  words: 260
  restates_numbers: true
  future_work: specific             # specific | generic | absent

style:
  voice: first_person_plural        # first_person_plural | impersonal | mixed
  tense_results: past
  hedging: medium                   # low | medium | high
  mean_sentence_words: 24
  equations_in_body: 6
  nomenclature_block: true
  reference_count: 62
  reference_style: numbered

does_not_do:
  - "no numbered contribution list anywhere"
  - "no teaser figure; Figure 1 is the case geometry"
  - "Discussion never restates Results — it only compares and extends"
  - "no 'to the best of our knowledge' framing"

distinctive:
  - "each Methods subsection ends with a table of the parameters it introduced"
  - "the case description carries a plan drawing and a photograph as one two-panel figure"
```

The `does_not_do` block is the most useful part and the one people skip. A convention the
journal avoids is as binding as one it follows, and it is invisible unless you look for it.

## Aggregate to a Venue Profile

Write `.paper/venue.yml`. It aggregates the cards and is the file the drafting passes read.

```yaml
version: 1
venue: "Journal A"          # a placeholder; the counts and habits below are invented
shape: journal                     # journal | conference | review
papers: 8
method_subgroup: simulation
built: "2026-08-21"

conventions:
  - pattern: "Literature is integrated into the Introduction; no Related Work section"
    support: [v01, v02, v03, v05, v07, v08]
    strength: dominant             # dominant | common | mixed | rare
  - pattern: "Contribution stated as prose in the final Introduction paragraph"
    support: [v01, v03, v04, v06]
    strength: common
  - pattern: "Explicit Limitations subsection inside Discussion"
    support: [v02, v04, v05, v06, v08]
    strength: dominant
  - pattern: "Nomenclature block after the abstract"
    support: [v01, v02, v03, v04, v05, v06, v07, v08]
    strength: dominant

typical:
  abstract_words: [190, 250]
  introduction_paragraphs: [5, 7]
  figures: [6, 10]
  references: [50, 80]
  mean_sentence_words: [22, 26]

avoids:
  - "numbered contribution lists"
  - "teaser figures"
  - "'to the best of our knowledge' novelty framing"

conflicts_with_skill:
  - habit: "three of eight papers report a bare p-value with no interval"
    ruling: "skill wins — statistics-reporting.md triad applies regardless"
  - habit: "two papers claim a gap with no supporting citation"
    ruling: "skill wins — literature-and-gap.md gap evidence package applies"

scope_fit_papers: []               # the three papers that show the journal's scope; keys from the .bib — submission-package.md

rules:                             # what the journal REQUIRES, read from its own guide
  guide_url: "<address of the guide for authors>"
  checked_on: "<date you read it>"
  article_type: "<as the guide names it>"
  word_limit: null                 # null = not yet checked
  abstract_limit: "<number of words, from the guide>"
  highlights_spec: "none stated"   # the guide was read and sets no such rule
  reference_style: "<numbered | author-year, from the guide>"
  template: "<class or template the guide names>"
  figure_resolution: "<from the guide's artwork instructions>"
  data_statement_required: "<true | false, from the guide>"
  ai_disclosure_wording: "<the heading and wording the guide asks for>"
  reporting_guideline: null        # the guideline or checklist the guide names — reporting-checklists.md
  supplementary_spec: null         # limits and formats for supplementary files — submission-package.md
  keyword_count: null              # how many keywords the guide asks for, or "none stated"
  prior_publication_policy: null   # for a paper extended from a conference paper — submission-package.md
  preprint_policy: null            # preprints, and sharing the accepted manuscript — submission-package.md
```

The `rules` block above is deliberately all placeholders. Write what the guide says on the
day you read it; never fill a value from this file, from memory, or from another journal.

Rules for the profile:

1. **`strength` is a count, not a score.** `dominant` means most of the corpus; `mixed` means
   the journal accepts both, which is a licence to choose rather than a rule to follow. Do not
   invent percentages from eight papers.
2. **`typical` ranges are observed ranges, not targets.** They tell you when your draft is an
   outlier, which is a prompt to check, not to trim.
3. **`conflicts_with_skill` is mandatory when a conflict exists.** An unrecorded conflict
   becomes a silent decision to follow the corpus, which is exactly the failure limit 2
   prevents.
4. A pattern supported by one or two papers is an author's habit. Do not record it as a
   convention.
5. **`conventions` and `rules` are different kinds of fact.** `conventions` is what published
   papers do, observed from the corpus. `rules` is what the guide for authors requires, read
   from the journal's own page. A corpus cannot tell you a word limit, and a guide cannot tell
   you whether Limitations is usually its own subsection.
6. **Every `rules` value comes from the guide, with `guide_url` and `checked_on` filled in.**
   Never write a limit, a resolution, or a reference style from memory or from another
   journal of the same publisher. Each value is in one of three states: the rule as the
   guide states it; `"none stated"`, when the guide was read and sets no such rule — a
   journal with no highlights, no word limit; or `null`, when the guide has not been checked
   for it. Only `null` blocks the Submission Gate item that depends on it. `"none stated"` is
   an answer, and it carries the same `checked_on` date. Re-read the guide before submission if
   `checked_on` is more than a few months old; guides change without notice.
7. The `rules` block does not need a corpus. Fill it as soon as the venue is chosen, even when
   no venue profile is built.

## Using the Profile

| Stage | What the profile decides |
|---|---|
| Before drafting | Section set and section names, whether Related Work exists, whether a Nomenclature block is needed |
| Drafting each section | Contribution placement and format, where the gap goes, whether Limitations is its own subsection, roadmap or no roadmap |
| Figures and tables | How many, what Figure 1 usually is, whether tables or figures carry the primary result |
| Sentence craft | Voice, hedging register, and the sentence-length band the corpus actually uses — this is the `Voice Calibration` input in `ai-tells.md` |
| Before submission | Whether the draft sits inside the `typical` ranges, and whether it does anything in `avoids`. Whether it meets every value in `rules`, each of which is checked against the manuscript, not assumed |

The profile informs the section guides; it does not replace them. `introduction.md` still says
what an Introduction must accomplish. The profile says how this journal usually arranges it.

## What This Is Not

1. **Not a template to fill in.** A paper written to match a profile exactly reads as
   imitation. The profile removes the wrong choices; it does not make the right one.
2. **Not a substitute for reading the papers.** Building the cards means reading them. The
   reading is most of the value.
3. **Not transferable.** A profile is for one venue and one method type. Do not reuse a
   *Building and Environment* profile for *Lighting Research and Technology*.
4. **Not a source of text.** See limit 1. Nothing from the corpus reaches your manuscript.
5. **Not a ranking.** No journal-quality score, no fit percentage. `submission-package.md`
   Journal Selection owns the choice of venue and it does not use numbers either.

## Checklist

1. Six or more papers, from the target journal, within the last five years?
2. Method type matched, or subgroups labelled?
3. Does every card contain categories and moves only, with no quoted or paraphrased text?
4. Does every card have a filled `does_not_do` block?
5. Is `.paper/venue.yml` written, with `strength` set by support count rather than by feel?
6. Is every conflict between a corpus habit and this skill recorded with a ruling?
7. Does the draft avoid everything in `avoids`?
8. Where the draft falls outside a `typical` range, is there a reason, rather than an accident?
