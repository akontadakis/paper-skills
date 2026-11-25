# Submission Package

**Load when:** choosing a journal, also after a rejection, or preparing the title, keywords, highlights, declarations, cover letter, supplementary material, proofs and other portal metadata.

**Contents:** Goal · Scope · Title · Keywords · Highlights (Elsevier) · Graphical Abstract · Declarations · Extending a Conference Paper · Cover Letter (Initial Submission) · Journal Selection · After a Rejection · Supplementary Material · Proofs · Checklist

## Goal

Prepare everything the submission portal asks for beyond the manuscript PDF: title,
keywords, highlights, declarations, and the cover letter to the editor.

## Scope

This is the **initial** submission. The cover letter for a *revision* belongs to
`responding-to-reviewers/references/cover-letter.md` in that skill — do not mix the two:
an initial letter sells fit and novelty; a revision letter accounts for changes.

Everything here is read by editors and reviewers **before** the manuscript, so it is
screened against the same claim discipline as the Abstract: nothing stated here that the
paper does not support.

## Title

1. **State the finding or the subject, not the activity.** "View direction and climate in
   melanopic daylight compliance of side-lit offices: a four-climate simulation study" beats
   "A study on the evaluation of melanopic compliance". A title that states a finding carries
   no verb stronger than the claim's ledger status allows.
2. **No `novel`, no `new`, no rhetorical questions** in a title for engineering journals. In the
   text, replace `novel` by saying what is different. Reviewers
   discount them, and `ai-tells.md` register rules apply to titles too.
3. **Front-load the searchable terms.** Search results cut a long title to fit the screen, so
   the topic words go first, not "An investigation into".
4. **Match the scope of the results.** A title broader than the outcome fires the
   negative-space check in `paper-review.md` ("A title broader than the outcome"). Four simulated sites do not carry a title about "buildings".
5. Length: roughly 10–16 words, as a rule of thumb; the journal's guide overrides it. Cut
   articles and filler first.
6. Subtitles after a colon are acceptable for scope bounds: "…: a four-climate simulation
   study". Use the colon for scope, not for drama.
7. Abbreviations in titles only when the abbreviation is the searched term (CFD, LED) —
   not sDA or mel-EDI, which reviewers know but databases index inconsistently.

## Keywords

1. **Complement the title, do not repeat it.** Indexing combines both; a keyword duplicating
   a title word is a wasted slot.
2. 4–6, per most venue rules — check the guide for authors for the exact count.
3. Use the field's controlled vocabulary where one exists (Ei/Scopus terms for engineering).
   Prefer the term the field searches: `circadian lighting` over `non-visual effects of
   light` if both fit.
4. Include one method keyword (`climate-based daylight modelling`, `annual simulation`) and
   one application keyword (`office buildings`) alongside the topic keywords.
5. Spell out what the title abbreviated, and vice versa.

## Highlights (Elsevier)

The journal's guide decides whether it asks for highlights. Record the answer in `highlights_spec`
in `.paper/venue.yml`. Elsevier's highlights page says they are not required until the final
files stage.

1. **3 to 5 bullets (3 to 4 at Cell Press), at most 85 characters each including spaces**, per
   Elsevier's highlights page. Count them.
2. **Results, not topics.** "Simulated worst-case view direction cut mean compliant plan depth from 5.8 m to 3.1 m"
   — not "Melanopic compliance was investigated".
3. Each bullet a complete finding a reader can cite without the paper.
4. No abbreviations that the title has not already earned, no citations, no vague claims.
5. Every highlight must be `supported` in the claim ledger. Highlights are the most-skimmed
   claims in the package; an over-claim here is the first thing a reviewer holds against you.
6. This is the one place the bullets ban does not apply — highlights are bullets by
   specification. They are portal metadata, not manuscript prose.

## Graphical Abstract

Optional at most of your target journals.

1. One pane, one message — usually the pipeline or the headline result, not both.
2. Readable at thumbnail size; the portal's pixel spec changes, so take dimensions from the
   current guide for authors rather than from memory.
3. No caption to lean on: every label must survive alone.
4. Follow `figures-tables.md` for colour, fonts, and accessibility — it is still a figure.

## Declarations

Most portals collect these as separate fields. Draft them with the manuscript, not at the
portal at midnight.

### CRediT authorship

The 14 roles: Conceptualization, Data curation, Formal analysis, Funding acquisition,
Investigation, Methodology, Project administration, Resources, Software, Supervision,
Validation, Visualization, Writing – original draft, Writing – review & editing.

1. Every author gets at least one role; every role listed is real.
2. Writing – original draft and Writing – review & editing are different roles — assign
   them separately.
3. Authorship itself follows ICMJE-style criteria: substantial contribution, drafting or
   revision, approval, accountability. A contributor who fails them goes to Acknowledgements.

### Ethics approval and consent

Collected as its own portal field by most journals, and a common cause of a desk hold. The
manuscript-body version is governed by `ethics-and-participants.md`; this is the portal block,
and the two must say the same thing.

1. **Human participants.** Name the approving committee or board in full, give the protocol
   identifier, give the approval date, and name the framework the study actually followed and
   the approving body applied — for medical research the Declaration of Helsinki, cited by
   version (currently October 2024); for other human-subject research, the institutional or
   national code the committee used. The Declaration requires registration in a public
   database before the first participant is recruited, so do not claim it for an unregistered
   study.
2. **Consent to participate.** State that informed consent was obtained and whether it was
   written. Where minors or others needing additional protection took part, say who consented
   and who assented.
3. **Consent to publish.** A separate statement, needed whenever identifiable images, audio,
   video, or case details appear. Journals treat this as distinct from consent to participate
   and will ask for it separately.
4. **Exemption or waiver.** Name the body that granted it and the ground. Never submit "no
   approval was required" without saying who determined that.
5. **Not applicable.** For a purely computational, simulation, or secondary-data study with no
   personal data, state "not applicable" rather than leaving the field blank. A blank field
   stalls the submission; an explicit "not applicable" does not.
6. **Secondary data.** Name the source dataset, its licence, and the consent under which it was
   originally collected.

The trap is a lighting or building-physics paper that reads as a physical measurement study but
collected glare ratings, preference votes, alertness measures, or post-occupancy surveys. That
is human-subject work and it needs every block above.

### Protocol registration

For a systematic review or meta-analysis, give the registration — PROSPERO (reviews with a
health outcome only; no scoping reviews), OSF Registries, or the journal's accepted
equivalent — with its identifier and date, and state whether it preceded the
search. If the protocol was not registered, say so. See `review-papers.md`.

For a primary study that was preregistered, cite the registration and state whether it preceded
data collection. Every deviation from the registered plan is disclosed in the manuscript, not
only in the portal field.

### Competing interests

State them or state "none". Funding from a party with a stake in the outcome is declared
even when it feels routine — an undeclared interest discovered later is far more damaging
than a declared one.

### Funding

Grant numbers and funder names exactly as the funder requires them. Check the funder's
own acknowledgement wording.

### Data availability

Pick the true statement, not the most convenient one:

1. Data in the article or supplementary material.
2. Data in a repository — name it, give the DOI or accession, state the licence.
3. Data available on request — say from whom and under what conditions.
4. Data not available — give the reason (proprietary, privacy, licence).

For a simulation study, "data" includes the model inputs, weather files (or their source if
licence-restricted), and the settings needed to regenerate results — this is the
availability half of the `simulation-reporting.md` gate (its §11). Scripts and model files
in a repository with a DOI turn a reproducibility claim into a checkable one. When
`.paper/runs.yml` has a `release:` block, take the repository, the identifier, the licence and
what is withheld from it.

### AI use disclosure

Most publishers (Elsevier included) now require a statement when generative AI was used in
writing, and forbid listing an AI as an author.

1. Disclose language editing as the publisher's policy defines it: some exempt basic grammar
   and spelling checks, others ask for all AI copy editing to be declared. The authors remain
   responsible for all content.
2. AI-generated text that produced claims, analysis, or citations is not a language edit —
   if that happened, the content needs the same verification as any other source, and the
   disclosure must say what was done.
3. AI-generated or AI-manipulated figures are restricted at most journals — check before
   including any.
4. Do not rely on the absence of tells to skip the disclosure. `ai-tells.md` exists to make
   prose read as considered, not to make use deniable.
5. Build the disclosure from what was actually done, not from what was logged. Use outside
   this session — a co-author's tool, a translation service, an earlier draft — counts, and a
   missing record of it does not make it not have happened. Ask each author.

**Elsevier journals.** The publisher's policy for authors, as read on 2026-11-15 (the page
gives its own date as June 2026):

1. Basic checks of grammar, spelling, and punctuation need no declaration. A tool that makes
   substantive changes to sentence structure or to the organisation of the text does.
2. The declaration is its own section at the end of the manuscript, immediately before the
   references. It names the tool and the purpose, and states that the authors reviewed the
   output and take responsibility for the content. It is published with the article.
3. An AI tool is not listed or cited as an author.
4. AI tools must not create or alter an image that represents primary observed or
   experimental data. A measured luminance map, a photograph of a test room, and an HDR
   capture are all such images.
5. A data visualisation may be made with an AI tool only when the output derives directly
   from the underlying data, and the method is then described in Methods. An explanatory
   image made with AI is disclosed in its caption and in the declaration.
6. A general-purpose generative image tool is not used for a graphical abstract.
7. AI used as part of the research design or method is not restricted by this policy. It is
   described in Methods in enough detail to be reproduced — `simulation-reporting.md`,
   section 12.

Policies change. Read the current page (`https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals`)
and the journal's own guide before submission, and record the required wording and the date
in `.paper/venue.yml`, `rules`. For any other publisher, read that publisher's policy; do not
carry these seven points across.

### Confidentiality

An unpublished manuscript, a reviewer letter, and data held under a consortium or client
agreement are confidential until the author says otherwise. Do not send their text to an
outside service — a search engine, a hosted checker, an API — without the author's say. The
literature and bibliography tools in this skill send search terms and DOIs only, never
manuscript text.

### Manuscript files

The portal wants specific files in a specific order, and desk screening checks it.

1. Use the journal's own template from the start. Moving a finished manuscript into a template
   late breaks numbering, captions, and styles. For an Elsevier journal in LaTeX, see
   `latex-mechanics.md`, Elsevier Class.
2. Run the format's pre-submission gate before uploading: `latex-mechanics.md` for a LaTeX
   manuscript, `word-manuscripts.md` for a `.docx`. Load exactly one.
3. Check the front and back matter order against the journal's instructions. Journals differ
   and the order is checked at desk screening.
4. Figures: in the text or as separate files, at the resolution the journal states, per its
   guide. `python3 scripts/extract_figures.py audit` reports the effective resolution at printed size.
5. For a double-blind venue, anonymise the manuscript **and** its file properties.
6. Where the portal asks for alt text per figure, write it from `figures-tables.md`, Colour
   and Accessibility, rule 9.
7. Check every limit in `.paper/venue.yml`, `rules`, against the manuscript itself: word
   count, abstract length, highlight length, reference style, figure resolution. A `null`
   there means the guide was never read for that item; `"none stated"` means it was read and
   sets no such rule.

## Extending a Conference Paper

A journal paper that grows out of a conference paper — Building Simulation, Lux Europa, a
CIE session — is legitimate and common. It is also the easiest way to be desk-rejected for
duplicate publication if the relation is not stated.

1. **Read the journal's policy on prior publication first**, and the conference's copyright
   terms. Some journals welcome extended versions, some want a stated share of new material,
   some refuse. The journal's page governs; this file states no percentage.
2. **Cite the conference paper** in the Introduction, and say in one or two sentences what
   the journal paper adds: new cases, new measurements, a validation, a longer period, a
   corrected method.
3. **Say it again in the cover letter**, with the full reference, so the editor learns it
   from you and not from the similarity report.
4. **Rewrite, do not paste.** Reused method description is acceptable where it is cited as
   such. Reused results text, figures, and discussion are what a similarity check flags.
   Redraw any figure that reappears and say that it does.
5. **Bring it up to journal standard**: the full reporting block of
   `simulation-reporting.md`, a Limitations paragraph, and the validation a conference paper
   usually omits.
6. **Carry the claims forward honestly.** A claim the conference paper made and the longer
   study no longer supports is corrected in the journal paper, and the correction is stated.
   Start the ledger from the conference paper's claims — `paper-memory.md`.
7. **Record it** in `.paper/venue.yml`, `rules`, as `prior_publication_policy`, with the date
   read.

## Cover Letter (Initial Submission)

Half a page. The editor reads it to decide which associate editor and reviewers get the
paper — write for that decision.

1. **Address and identifiers** — editor-in-chief by name if listed, journal, manuscript
   title.
2. **Fit** — one or two sentences: what the paper shows and why it belongs in *this*
   journal. Name the journal's scope area it fits; citing one or two recent papers from the
   journal that it builds on is the strongest fit argument available.
3. **The contribution** — two or three sentences, the same claims as the Abstract, no
   stronger. Do not restate the Abstract; state why the finding matters to this readership.
4. **Statements the editor needs**: the work is original, not published, not under review
   elsewhere; all authors approved the submission. Add any journal-required ethics line.
5. **Suggested reviewers**, if the portal asks: 3–5, no recent co-authors, no same
   institution, more than one country. Exclusions are legitimate — name a conflict, not a
   fear of criticism.
6. **Close** in one sentence.

Do not: summarise the paper section by section, praise the journal, or claim significance
the Abstract does not claim. The letter is screened against the manuscript.

## Journal Selection

Run this before writing the package, ideally before drafting — the venue sets the shape.

1. **Scope fit first**: find three recent papers in the candidate journal that your paper
   would cite or be cited by. None findable means wrong journal, whatever the impact factor.
2. Match the paper type: a methods contribution, a case study, and a review have different
   natural venues even inside one field.
3. Check turnaround and open-access terms against your constraints; check any funder OA
   mandate before choosing a subscription-only venue.
4. Legitimacy check for unfamiliar venues: listed in Scopus/DOAJ, a real editorial board,
   a checkable ISSN. Unsolicited invitations from unknown journals fail this by default.
5. Record the choice, and the three scope-fit papers as `scope_fit_papers` in
   `.paper/venue.yml` — they seed the cover letter's fit
   paragraph and the Introduction's positioning.
6. **Read the guide for authors now and record its rules** in the `rules` block of
   `.paper/venue.yml`, with the link and the date: article type, limits, reference style,
   template, figure resolution, data statement, AI-disclosure wording, supplementary
   specification (`supplementary_spec`) and the number of keywords (`keyword_count`). The schema is in
   `venue-calibration.md`. Writing to a limit from the start costs nothing; discovering it
   at upload costs a restructure.
7. Check the journal's policy on preprints and on sharing the accepted manuscript before
   posting a preprint, and check any embargo. Record it in `.paper/venue.yml`, `rules`, as
   `preprint_policy`, with the date read. Where code or data are released, deposit them
   in a repository that issues a DOI, and cite that DOI in the Data availability statement.

## After a Rejection

A rejection is a set of reviews that the next journal will not see. Its reviewers may be the
same people.

1. Read the decision as data. Sort each reason into one of three: scope or fit; a fault that
   any reviewer would raise; one reviewer's preference. Keep the comments in
   `.paper/reviews/<date>-rejection.md`.
2. Fix every fault that any reviewer would raise before sending the paper anywhere. A
   manuscript resubmitted unchanged meets the same objection.
3. Run Journal Selection again with the reasons in hand. A rejection for scope changes the
   journal. A rejection for method changes the paper first.
4. Refill the `rules` block of `.paper/venue.yml` from the new journal's guide, with the link
   and the date: article type, limits, reference style, template, data statement. Reformat to
   it. Rebuild `conventions` if a corpus of the new journal is available.
5. Re-run the literature search and update its date. Months have passed, and a paper
   published in between is the next reviewer's first comment.
6. Run the Submission Gate in `paper-review.md` from the start. A limit, a style and a required
   statement have all changed.
7. Write a new cover letter for an initial submission. Do not mention the earlier decision
   unless the new journal asks about prior submissions or the reviews are transferred. Where
   it asks, answer truthfully.
8. Send the manuscript to one journal at a time.

## Supplementary Material

Supplementary files are reviewed. Every rule for the main text holds there too.

1. Each supplementary item is cited in the main text, in order. An item nothing cites is cut.
2. The main text stands without the supplement. A result the conclusion depends on is in the
   main text.
3. A number that appears in both places is the same number. Give supplementary figures and
   tables their own rows in `.paper/figures.yml`, with ids such as `FigS1`, so the ledger check
   covers them.
4. A check that failed, a run that was excluded, and an analysis chosen after the results are
   named in the main text, even when their detail is in the supplement. The supplement is not
   a place to put what a reviewer should not notice.
5. Captions in the supplement are self-contained, and its numbering is separate: Figure S1,
   Table S1.
6. Follow the journal's rules on format and size, and record them in `venue.yml`, `rules`, as `supplementary_spec`.

## Proofs

The proof is the last look, and it is for correcting errors. It is not a revision.

1. Check the proof against the accepted manuscript, not from memory: every number, unit,
   symbol and sign; every equation, because equations are often re-keyed; decimal points and
   alignment in tables; the order and quality of figures; captions; cross-references.
2. Check the front and back matter: author names and their order, affiliations, the
   corresponding author, funding, and each declaration.
3. Check the reference list. Copy-editing changes it more than any other part.
4. Where the proof can be saved as text, compare it with the accepted text:
   `python3 scripts/check_revision_tokens.py --source accepted.txt --revised proof.txt` lists
   the numbers, units, citations and hedging verbs that changed in typesetting.
5. Answer every query from the copy editor. A copy-edit that changes a hedge, a number or a
   defined term has changed the frozen set of the Revision Contract. Ask for it to be restored.
6. An error in the science found at this stage goes to the editor, stated plainly. Do not
   change a result quietly in a proof.
7. Keep the list of corrections in `.paper/reviews/<date>-proofs.md`.

## Checklist

1. Does the title state the finding, at the scope the results support, with searchable
   terms first?
2. Do the keywords complement rather than repeat the title?
2b. For a human-subject study: is the ethics block complete — body, identifier, date, framework,
   consent to participate, and consent to publish where identifiable material appears?
2c. For a computational or secondary-data study: does the ethics field say "not applicable"
   rather than sitting blank?
2d. For a systematic review or a preregistered study: is the registration given with its
   identifier and date, or its absence stated?
3. Is every highlight ≤ 85 characters, results-stated, and `supported` in the claim ledger?
4. Is every declaration drafted — CRediT per author, competing interests, funding with
   grant numbers, data availability that is actually true, AI use?
5. Does the data-availability statement cover the simulation inputs and settings
   (`simulation-reporting.md` §11)?
6. Does the cover letter argue fit to this journal, and claim nothing beyond the Abstract?
7. Are suggested reviewers conflict-free and geographically mixed?
8. Are the three scope-fit papers recorded in `scope_fit_papers`, and does the Introduction actually engage them?
9. Is every `rules` value in `.paper/venue.yml` filled from the guide, with its date, and
   checked against the manuscript?
10. If the paper extends a conference paper: is that paper cited in the Introduction and
    named in the cover letter, and is the journal's prior-publication policy recorded?
11. Does the AI-use declaration follow the publisher's current policy, including its rules
    for figures?
