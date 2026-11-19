---
description: Run the Submission Gate on the manuscript in this folder and report pass or fail per item, with the evidence.
disable-model-invocation: true
argument-hint: "[manuscript root file]"
---

First invoke the Skill tool with skill `research-paper-writing` (listed as `paper-skills:research-paper-writing` when the package is installed as a plugin). If the skill cannot be loaded, report that it failed to load and stop. Do not continue from this summary.

Then run the Submission Gate in the skill's `references/paper-review.md` on the manuscript in the current folder, or on `$ARGUMENTS` if a file was given.

1. Read `.paper/` first. If there is none, say so: gate item 9 is then "not run". Read `design.yml` for gate item 15, and `gap.yml` for gate item 16, when they exist.
2. Run the mechanical checks from the skill's `scripts/` folder and paste their output: `check_ledger.py` with `--manuscript`; for a LaTeX manuscript, `bib_check.py refs.bib --tex main.tex --online`, which gate item 13 needs, and `bib_check.py refs.bib --tex main.tex --verified .paper/verified-refs.yml` when that list exists; and the pre-submission greps of the format's guide. For gate item 14, when `.paper/runs.yml` exists, run `check_provenance.py`, which is in the `scripts/` folder of the `research-study-design` skill. `--online` sends each DOI to doi.org, Crossref, and OpenAlex, and nothing else. If the author does not want that, run it without `--online` and report the notice and identity parts of gate item 13 as not run; still run `--verified`, which works offline. A manuscript that cites works and has no list fails gate item 13 as "fail: no verified list", unless the author records a waiver. For a Word manuscript, report the comparison of cited items with the list as a manual check.
3. Report every gate item by number as pass, fail, or not run, each with the output or the location that shows it. An item with no evidence is not a pass. An item that does not apply to the study is a pass, with the reason. The by-hand part of item 13 for a Word manuscript is reported as a manual check.
4. Do not edit the manuscript. If `.paper/` exists, write the run to `.paper/reviews/<date>-gate.md`. If it does not, report in the conversation only and create nothing.
