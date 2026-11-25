# Agents and Scripts

**Load when:** you are about to dispatch one of this skill's agents or run one of its check scripts, or the author asks what they do.

**Contents:** Agents · Scripts

## Agents

Five of the six agents in the package's top-level `agents/` folder serve this skill. They are ordinary
subagents: install them to `~/.claude/agents/` (see `INSTALL.md`) or install the plugin, then
dispatch them with the Agent tool, using the `name` in their frontmatter as `subagent_type`,
with the prefix `paper-skills:` when the package is installed as a plugin
(`paper-skills:claim-auditor`).

| Agent | Runs against | Answers |
| --- | --- | --- |
| `claim-auditor` | manuscript + `.paper/` | Does every claim have a row, a matching verb, and evidence that resolves? Does the Submission Gate pass? |
| `consistency-checker` | source files | Terminology drift, acronyms, cross-references, definition order, undefined metrics, promise versus delivery, numeric consistency |
| `bibliography-auditor` | `.bib`, `.tex`, `.blg`, PDF | Field completeness, DOIs, whether each DOI points to the work cited, retraction and correction notices, brace protection, preprint upgrades, unresolved citations, citation coverage, and whether the cited version supports the sentence |
| `latex-layout-auditor` | the compiled PDF | Float placement, isolated float pages, subfigure alignment, caption overflow, overfull boxes, legibility at print size |
| `literature-crawler` | OpenAlex, Crossref, Semantic Scholar, arXiv, DBLP, Europe PMC | What the literature contains, where it is thin, and whether a candidate gap survives the false-gap and echo-chamber checks |

Rules:

1. **They report; you decide.** Four of the five write nothing. `literature-crawler` writes only
   inside `.paper/`. None of them edits the manuscript, and none spawns further agents.
2. **Dispatch them in parallel** where they are independent. `claim-auditor`,
   `consistency-checker`, and `bibliography-auditor` have no dependency on each other.
3. **`latex-layout-auditor` needs a compiled PDF.** Without one it reports the log findings only,
   says the layout was not audited, and does not call the result a layout audit.
4. **`claim-auditor` needs `.paper/claims.yml`.** Without one it stops rather than reconstructing
   a ledger and auditing its own reconstruction.
5. **Merge their findings yourself**, deduplicated and prioritised, into one
   `.paper/reviews/<date>-<scope>.md`. Then fix against that file in a single pass, and review
   the fixed text again, up to three rounds in all, as `paper-review.md`, The loop, says. Do
   not run one fix pass per finding.
6. **Never let an agent's report stand as the claim.** A finding is verified against the
   manuscript before it is acted on, and a disagreement between two agents is reported to the
   user, not silently resolved.
7. **Put in the dispatch prompt everything the agent needs.** An agent cannot ask the user
   anything. Give every agent the absolute path of the skill folder; it reads `references/`
   and `scripts/` under it. Give `bibliography-auditor` and `literature-crawler` whether the
   author allows the network, and `literature-crawler` the contact email, the OpenAlex API
   key and the sentinel papers, when the author supplied them. An agent proceeds without what
   is absent and reports it as not supplied.

Running an agent is optional. For a single-paragraph edit it is overkill; for a pre-submission
pass on a full manuscript it is the cheapest way to catch mechanical faults that reading misses.

## Scripts

Seven helpers in this skill's `scripts/` folder, documented in `scripts/README.md`. They
produce evidence; they never edit the manuscript and none of them is a gate. Run each one
through the interpreter, from the project folder, and give the script its full path. In every
command line in these guides, `scripts/` stands for this skill's `scripts/` folder, under the
base directory shown when the skill loads: `python3 <skill folder>/scripts/check_ledger.py .paper`.
Every script has `--help` and needs Python 3.9 or newer.

| Script | Needs | Use it for |
| --- | --- | --- |
| `fetch_oa_pdf.py` | nothing | Resolving a DOI, arXiv id, or PubMed id to an open-access PDF and a BibTeX record. Open access only — it does not bypass paywalls. |
| `extract_figures.py` | PyMuPDF | Pulling a figure out of a paper, and auditing raster resolution at printed size in your own compiled PDF |
| `ai_tell_audit.py` | nothing | The greppable half of `references/ai-tells.md`, plus the section 8 rhythm metrics. Reads `.tex`, `.md`, `.txt`, `.docx`. |
| `check_revision_tokens.py` | nothing; PyYAML for `--terms` | Comparing a revision with its source: the numbers, ranges, citations, cross-references, locked terms, and hedging verbs it removed or added. The mechanical check of Revision Contract point 1. |
| `check_ledger.py` | PyYAML | Checking `.paper/` against its own rules, and tracing the numbers the manuscript quotes against `key_numbers` |
| `bib_check.py` | nothing; PyYAML for `--verified` | Checking a `.bib` file: required fields, duplicates, cited keys with no entry and, with `--online`, whether each DOI points to the work its entry describes and whether that work carries a retraction or correction notice. `--record` writes the verified list `.paper/verified-refs.yml` (it needs `--online`); `--verified` checks the cited keys against that list, offline. |
| `check_package.py` | PyYAML for a complete result | Checking this skill's own integrity after editing it |

Rules:

1. **Script output is evidence, not a verdict.** The reference file decides every hit.
   `ai-tells.md` `What NOT To Flag` overrides `ai_tell_audit.py` in every case.
2. **Paste the counts.** A pass reported as "clean" without the output is not a pass. See
   `references/paper-review.md`, `Independent Review`.
3. `fetch_oa_pdf.py` reports three different answers — downloaded, no open access found, and
   not checked. Never read the third as the second. Every script holds to the same rule: a
   failed request, a missing file, or a part that could not be read is printed as not
   checked, and is never part of a clean result. The exit codes of each script are in
   `scripts/README.md`.
4. `check_revision_tokens.py` sees tokens, not meaning. A clean result does not show a
   revision is faithful; a difference is not a fault when the revision was asked to make it.
