# Install the paper-skills package

There are two install routes. **Use one route, never both.** Both together give you every
skill and agent twice.

## Route A: copy into your personal folders

Run these commands from this folder.

1. Copy the three skills into your personal skills folder. Install all three: they refer to
   each other's files.

   ```sh
   mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/commands
   cp -R research-study-design research-paper-writing responding-to-reviewers ~/.claude/skills/
   ```

2. Copy the six helper agents into your agents folder:

   ```sh
   cp agents/*.md ~/.claude/agents/
   ```

   The agents are bibliography-auditor, claim-auditor, consistency-checker,
   design-reviewer, latex-layout-auditor and literature-crawler.

3. Copy the slash commands:

   ```sh
   cp commands/*.md ~/.claude/commands/
   ```

4. Restart Claude Code. Open a new chat.

5. Check: type `/research-study-design`. The skill should load.
   Then type `/research-paper-writing` and `/responding-to-reviewers`. Each should load too.

## Route B: install as a plugin

This folder is also a plugin. Its manifest is `.claude-plugin/plugin.json`.

From GitHub, in one line:

```sh
claude plugin marketplace add akontadakis/paper-skills && claude plugin install paper-skills@paper-skills-marketplace
```

From a local copy of this folder:

```sh
claude plugin validate .
claude plugin marketplace add .
claude plugin install paper-skills@paper-skills-marketplace
```

With this route the skills, agents and commands carry the plugin prefix, for example
`/paper-skills:research-paper-writing`.

## Update and remove

Route A, copy. To update, remove the old copy first, so that a deleted guide does not stay
behind, then copy again from the new version of this folder:

```sh
rm -rf ~/.claude/skills/research-study-design ~/.claude/skills/research-paper-writing ~/.claude/skills/responding-to-reviewers
rm ~/.claude/agents/{bibliography-auditor,claim-auditor,consistency-checker,design-reviewer,latex-layout-auditor,literature-crawler}.md
rm ~/.claude/commands/{paper-gate,paper-independent-review,paper-ledger,paper-plan,paper-respond,paper-trace}.md
```

Then repeat steps 1 to 4 of Route A. To remove the package, run the three `rm` lines and restart
Claude Code.

Route B, plugin. Update, then restart Claude Code:

```sh
claude plugin marketplace update paper-skills-marketplace
claude plugin update paper-skills@paper-skills-marketplace
```

To remove it:

```sh
claude plugin uninstall paper-skills@paper-skills-marketplace
```

## Scripts

The helper scripts live in `research-paper-writing/scripts/` and `research-study-design/scripts/`.
They come with the skill folders in both routes. None of them edits a manuscript. They need
Python 3.9 or newer.

- `fetch_oa_pdf.py` finds an open-access PDF and a BibTeX record for a DOI.
- `extract_figures.py` pulls figures out of a PDF and audits their resolution. It needs PyMuPDF.
- `ai_tell_audit.py` counts the machine-writing patterns listed in the AI-tell reference.
- `check_revision_tokens.py` lists the numbers, citations, and hedging verbs a revision changed.
- `check_ledger.py` checks the `.paper/` ledger files against their rules. It needs PyYAML.
- `bib_check.py` checks a `.bib` file, and with `--online` checks each DOI and looks for retractions.
- `check_package.py` checks this package's own integrity.
- `record_run.py` appends one run to `.paper/runs.yml`: code version, input and output hashes, tool versions.
- `check_provenance.py` checks that each final figure rests on a valid run whose files have not changed. It needs PyYAML.

See `research-paper-writing/scripts/README.md` for how to run each one.

## Tests

The package has unit tests in `tests/`. In a virtual environment, run
`pip install pytest pyyaml pymupdf`, then `python3 -m pytest tests`. They need no network.

## Which skill to use

Use research-study-design before the results exist: to sharpen the question, design the study and record the runs.
Use research-paper-writing to write the paper.
Use responding-to-reviewers after you get reviewer comments.
