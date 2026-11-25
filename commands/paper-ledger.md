---
description: Show the state of the paper memory in .paper/ — claims by status, figures, open reviewer comments — and run the ledger check.
disable-model-invocation: true
argument-hint: "[manuscript root file]"
---

First invoke the Skill tool with skill `research-paper-writing` (listed as `paper-skills:research-paper-writing` when the package is installed as a plugin). If the skill cannot be loaded, report that it failed to load and stop. Do not continue from this summary.

Then report the state of `.paper/` in the current folder. Change nothing.

1. If `.paper/` does not exist, say so and stop. Do not build one.
2. Run `python3 <skill folder>/scripts/check_ledger.py .paper` from the project folder, adding `--manuscript $ARGUMENTS` if a file was given, and paste its output, including every "not checked" line.
3. Give the counts: claims by status, figures by status, gaps by status, and reviewer comments by status, and rows whose `decision_confirmed` is not `true` (false or absent), if `changes.yml` exists.
4. Compare the `updated` dates in the files with the manuscript's modification time. Say plainly if the ledger is older than the manuscript.
5. List what blocks the Submission Gate today, by gate item number.
