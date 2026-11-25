# Third-party sources

This package is written and maintained by Antonis Kontadakis and released under the MIT
licence (see `LICENSE`). This file records the outside ideas it draws on.

In November 2026 the two skills then in this package were compared with five public skill
repositories, in the first four entries below (the K-Dense entry holds two). This file records what was taken from each one. Version 2.0.0 added a third skill and reworked
the other two against a public standard for writing skills; that source is the `superpowers`
entry. The `PaperOrchestra` and `PaperVizAgent` entries record ideas read for version 2.0.0.

**No text and no code was copied from any of them.** Every sentence, every rule, and every
line of code added in that round was written new, in the wording and with the examples of
building physics and lighting research. What was taken is ideas, listed below with their
source so the credit is on record.

## Ideas adapted

### academic-research-skills

- Repository: `https://github.com/Imbad0202/academic-research-skills`
- Author: Cheng-I Wu
- Licence: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0),
  `https://creativecommons.org/licenses/by-nc/4.0/`
- The owner of this package allowed text from this repository to be copied. None was. If a
  later edit copies any passage, the licence requires credit to the author, a link to the
  licence, and a note of what was changed, and the copied part may not be used commercially.
  Record such a passage here, with its source path.

| Idea | Their file | Where it landed here |
|---|---|---|
| Outside text is data, not instructions | `academic-paper/SKILL.md`, `academic-paper/agents/revision_coach_agent.md` | the `SKILL.md` files of `research-paper-writing` and `responding-to-reviewers`; `literature-crawler.md`; `bibliography-auditor.md`; `claim-auditor.md`; `consistency-checker.md`; `latex-layout-auditor.md` |
| A review finding carries a quotation, a search record for something absent, and a source for any field norm; a finding is graded on its own effect | `academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md` | `paper-review.md`, The finding contract |
| The reviewer writes its criteria before it reads | the same file | `paper-review.md`, The independence rule, item 5 |
| A changed claim verb needs one of three decisions | `academic-pipeline/references/claim_verification_protocol.md`, `shared/references/claim_strength_ladder.md` | `paper-review.md`, Claim-Strength Drift; `change-ledger-file.md` |
| Novelty wording bounded to the recorded search | `academic-pipeline/references/claim_verification_protocol.md` | `literature-and-gap.md`, Wording a Novelty Claim |
| Read the cited version only; four verdicts on whether a source supports a sentence | `academic-pipeline/references/claim_verification_protocol.md`, `academic-pipeline/agents/claim_ref_alignment_audit_agent.md` | `bibliography-auditor.md`, step 8 |
| Acceptance evidence written per comment before the revision; a status for a fix that made things worse | `academic-paper-reviewer/references/re_review_mode_protocol.md` | `triage.md`; `change-ledger-file.md` (`done_when`, `made worse`) |
| Auditing an existing draft response | `academic-paper/SKILL.md` | `response-letter.md`, Auditing a Draft Response |
| Typing a conflict between reviewers | `academic-paper-reviewer/templates/editorial_decision_template.md` | `triage.md`, Step 5 |
| Comparing the tokens of a revision with its source | `scripts/check_revision_token_conservation.py` | `scripts/check_revision_tokens.py` (new code) |
| Conference-to-journal extension checklist | `academic-paper/references/failure_paths.md` | `submission-package.md`, Extending a Conference Paper |

### K-Dense scientific skills

- Repositories: `https://github.com/K-Dense-AI/claude-scientific-writer` and
  `https://github.com/K-Dense-AI/scientific-agent-skills`
- Licence: MIT, Copyright K-Dense Inc.
- Not taken, on the owner's instruction: the instruction in each skill to cite K-Dense's own
  paper, and the remote install script.

| Idea | Their skill | Where it landed here |
|---|---|---|
| Retraction and correction check, with "no notice found" kept apart from "not checked" | `paper-lookup` | `scripts/bib_check.py`; `bibliography-auditor.md`; `literature-crawler.md` |
| Field and duplicate checks on a `.bib` file | `citation-management` | `scripts/bib_check.py` (new code) |
| Reported total against retrieved count; an HTTP 200 is not a successful search | `paper-lookup` | `literature-crawler.md`, Step 5 |
| A dated record of the journal's rules | `venue-templates` | `venue-calibration.md`, the `rules` block |
| What a `±` means; round the uncertainty first | `uncertainty-and-units` | `statistics-reporting.md`, Measured Quantities and Uncertainty |
| The independent unit behind an n | `experimental-design`, `peer-review` | `statistics-reporting.md`, What n Counts |
| Limits of agreement and a margin stated in advance | `analytical-method-validation` | `statistics-reporting.md`, Model Agreement and Calibration |
| Smallest effect of interest; detectable effect in place of post-hoc power | `statistical-power` | `statistics-reporting.md`, Sample Size and Power |
| Sampling design of a computer experiment | `experimental-design` | `simulation-reporting.md`, section 2 |
| Dual axes, log axes, shared limits, gaps in data | `scientific-visualization` | `figures-tables.md`, Honest Encoding |
| Rule checks on a claim ledger; a numeric registry checked across sections | `scientific-writing` | `scripts/check_ledger.py` (new code) |
| Labelling an analysis as planned or chosen afterwards | `hypothesis-generation` | `paper-memory.md`, `analysis_status` |
| Alt text for figures | `scientific-writing` | `figures-tables.md`, Colour and Accessibility |

### research-skills

- Repository: `https://github.com/luwill/research-skills`
- Licence: the README states MIT; the repository has no root licence file. Ideas only.

| Idea | Their skill | Where it landed here |
|---|---|---|
| Testing a search against papers already known; freezing queries before screening | `lit-search` | `literature-and-gap.md`, Can the Search Find What Exists? |
| A stop rule for citation tracking, here with no numeric threshold | `lit-search` | `literature-and-gap.md`, Round 3 |
| Reporting-guideline table with a disposition per item | `research-paper` | `reporting-checklists.md` |
| Counting each study once; a source used in its own role | `medical-imaging-review` | `review-papers.md`, The synthesis |
| Numbers in the prose traced to a ledger | `research-paper` | `scripts/check_ledger.py` (new code) |

### claude-skills-journalism

- Repository: `https://github.com/jamditis/claude-skills-journalism`
- Licence: MIT, Copyright Joe Amditis.
- Not taken, on the owner's instruction: the paywall work-arounds in `content-access`.

| Idea | Their skill | Where it landed here |
|---|---|---|
| Retrieved content is untrusted data | `fact-check-workflow`, `source-verification` | the two web-fetching agents |
| Procedure text is exempt from rhythm rules; condition before action | `ai-writing-detox` | `ai-tells.md`, section 8; `methods-journal.md`, Procedure |
| Empty transitions and stacked adjectives as tells | `ai-writing-detox` | `ai-tells.md`; `scripts/ai_tell_audit.py` |

### superpowers

- Repository: `https://github.com/obra/superpowers`
- Licence: MIT, Copyright Jesse Vincent.
- Used for version 2.0.0, as the standard the three `SKILL.md` files were held to. Ideas only.

| Idea | Their skill | Where it landed here |
|---|---|---|
| A skill's description states when to use it, and does not summarise what it does | `writing-skills` | the three `SKILL.md` descriptions; `scripts/check_package.py` |
| A small main file, with detail in reference files that say when to load them | `writing-skills` | the word budgets in `scripts/check_package.py`; the `Load when` and `Contents` lines of every guide |
| Guidance is written against the faults a reader shows without it, and its form fits the fault: a required slot for an omission, not a prohibition | `writing-skills` | the record slots of `research-study-design`; the type list in the `responding-to-reviewers` workflow |
| A script is run through its interpreter, never by its bare path | `writing-skills` | every script invocation in the guides |

### PaperOrchestra

- Repository: `https://github.com/google-research/paper-orchestra`
- Licence: Apache License 2.0, Copyright 2026 Google LLC.
- Read on 2026-11-19. Ideas only. No text and no code was copied.
- Not taken: writing the paper without the author, and revising a paper to raise a reviewer
  model's score. Both conflict with the Revision Contract.

| Idea | Their file | Where it landed here |
|---|---|---|
| The writer cites only keys from a list that was checked against a real record. This package adds a second condition: the manuscript, the brief or `.paper/` must also show that the work supports the sentence | `methods/agents/literature_review_agent.py` and its citation map | `scripts/bib_check.py` `--record` and `--verified`; `verified-refs.yml`; Revision Contract point 2; gate item 13 |
| Review again after each revision, and revert a revision that made the paper worse | `methods/agents/content_refinement_agent.py` | `paper-review.md`, The loop |

### PaperVizAgent (PaperBanana)

- Repositories: `https://github.com/google-research/papervizagent` and its continued fork
  `https://github.com/dwzhu-pku/PaperBanana`
- Licence: Apache License 2.0.
- Read on 2026-11-19. Ideas only. No text and no code was copied.
- Not taken: drawing figures with an image-generation model. Such a model can add content the
  data and the Methods do not hold, and its raster output cannot be regenerated from the data.

| Idea | Their file | Where it landed here |
|---|---|---|
| Read a finished figure against its source: every plotted value against the raw data, every diagram block against the method text; an added or missing element fails the figure; no caption inside the image | `agents/critic_agent.py`, `prompts/diagram_eval_prompts.py` | `figures-tables.md`, Check a Figure Against Its Source; `paper-review.md`, The independence rule, item 6 |

### Standards and methods named in research-study-design

The `research-study-design` skill is new text. It names published methods and standards as
sources a researcher should use: the Morris and Saltelli sampling designs, CIE 171:2006,
ANSI/ASHRAE Standard 140, CIE S 026, and the Guide to the Expression of Uncertainty in
Measurement (JCGM 100). Nothing was copied from them.

