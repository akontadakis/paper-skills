---
description: Trace each final figure and table back to its run, code and inputs, and report any recorded file that has changed since the run.
disable-model-invocation: true
argument-hint: "[project folder]"
---

First invoke the Skill tool with skill `research-study-design` (listed as `paper-skills:research-study-design` when the package is installed as a plugin). If the skill cannot be loaded, report that it failed to load and stop. Do not continue from this summary.

Then trace the results of the project in the current folder, or in `$ARGUMENTS` if a folder was given. Change nothing.

1. If `.paper/runs.yml` does not exist, say so and stop. Do not build a run record from memory.
2. Run `python3 <skill folder>/scripts/check_provenance.py <project folder>` from the project folder, and paste its output, including every "not checked" line and its last line. Say what its exit code means: 1 at least one finding, 3 nothing found but something was not checked.
3. For each `final` row of `figures.yml`, give the chain in one line: figure, its runs, the code version of each run, and the number of input files. A figure with no run is listed as untraced.
4. List the runs that are `failed`, `excluded` or `superseded`, each with its reason, and give the count of each.
5. Say plainly which results could be regenerated today from the record, and which could not.
