# Scripts

Seven helpers. Five need nothing installed; one needs PyMuPDF and one needs PyYAML. None of
them edits your manuscript, and none of them is a gate — they produce evidence that a human
or an agent then judges against the reference files.

| Script | Needs | What it does |
| --- | --- | --- |
| `fetch_oa_pdf.py` | nothing | Resolves a DOI, arXiv id, or PubMed id to an open-access PDF and a BibTeX record |
| `extract_figures.py` | `pip install PyMuPDF` | Pulls figures out of a PDF, and audits raster resolution at printed size |
| `ai_tell_audit.py` | nothing | Runs the greppable half of `references/ai-tells.md` and computes the rhythm metrics |
| `check_revision_tokens.py` | nothing (`pyyaml` for `--terms`) | Lists the frozen tokens a revision removed or added |
| `check_ledger.py` | `pip install pyyaml` | Checks `.paper/` against its own rules and traces quoted numbers |
| `bib_check.py` | nothing (`pyyaml` for `--verified`) | Checks a `.bib` file offline, and each DOI's identity and notices online |
| `check_package.py` | `pip install pyyaml` for a complete result | Checks this package's own integrity |

`_manuscript.py` is not a command. It is the shared reader the check scripts import.

Two more scripts, `record_run.py` and `check_provenance.py`, keep the run record. They are in the
`scripts/` folder of the `research-study-design` skill, and its `run-record.md` reference
describes them.

Run a script from your project folder and give it its full path: the skill's base directory,
then `scripts/`, then the file name.

Every script has `--help` and runs on Python 3.9 or newer.

## fetch_oa_pdf.py

```bash
python3 fetch_oa_pdf.py 10.1016/j.buildenv.2023.110000 --email you@example.org
python3 fetch_oa_pdf.py 2301.07041 --out papers/
python3 fetch_oa_pdf.py --batch dois.txt --out papers/ --email you@example.org
python3 fetch_oa_pdf.py 10.1038/s41586-023-06600-9 --bibtex-only
```

Sources: Unpaywall, OpenAlex, arXiv, Europe PMC, and `doi.org` for the BibTeX record. All
free. Unpaywall requires a real contact email on every call: pass `--email`, or set
`UNPAYWALL_EMAIL`. The email is sent to Unpaywall only. Without it, Unpaywall is skipped and
the rest still run. The DOI is sent to `doi.org`, and the identifier to the other sources. A
bare number is a PubMed id only with 7 or 8 digits; a shorter one needs the `PMID:` prefix
(`PMID:12345`), so a stray year in a batch file is skipped as unrecognised. For Europe PMC it
takes a PDF link marked open (`OA` or `F`), else a PDF link on `europepmc.org`, and skips any
other link.

**Open access only.** It does not bypass paywalls, use institutional proxies or VPN
credentials, or pretend to be a browser. When no open copy exists it says so and prints the
publisher landing page for your library. When a host refuses an automated request — several
publishers return 403 to anything that is not a browser — it prints the URLs so you can open
them yourself. That is the correct behaviour, not a bug.

It distinguishes three answers that are easy to confuse: **downloaded**, **no open access
found**, and **not checked** (the network or TLS failed). Never read the third as the second.
A lookup that failed is never worded as a statement about the paper.

Exit code 0 when every identifier got an answer. 2 when none was given, the `--batch` file
cannot be read, or every identifier was unrecognised. 3 when at least one lookup was not
checked, or an identifier was not recognised.

## extract_figures.py

```bash
python3 extract_figures.py extract paper.pdf --out figs/
python3 extract_figures.py extract paper.pdf --only 3 5 --dpi 400
python3 extract_figures.py extract paper.pdf --native
python3 extract_figures.py audit manuscript.pdf --min-dpi 300
```

`extract` finds captions, works out the region each one belongs to, and renders it to PNG. It
writes `figure_index.json` with each caption and its file, which is a ready-made start for
`.paper/figures.yml`. `--native` saves the embedded raster at its own resolution instead of
rendering the page region.

`audit` runs on **your** compiled PDF and reports every embedded raster's pixel size, printed
size, and effective dpi, flagging anything under the threshold. This is the mechanical half of
the legibility rules in `references/figures-tables.md` and `references/word-manuscripts.md`.
A manuscript whose figures are all vector correctly reports nothing to audit.

Exit code 0 when the run finished, 1 for `audit --strict` with a raster below the threshold, 2
when it could not start (a missing, unreadable, encrypted or empty PDF, or PyMuPDF not
installed; the reason goes to stderr), 3 when `extract` found no matching caption or could not
extract a figure.

Extracting a figure from a paper you have lawful access to, for reading or a properly
attributed comparison, is normal scholarly use. Republishing one needs the rightsholder's
permission unless the licence grants it. The script does not check licences.

## ai_tell_audit.py

```bash
python3 ai_tell_audit.py sections/*.tex --context
python3 ai_tell_audit.py manuscript.docx
python3 ai_tell_audit.py paper.tex --only T1 T2 T5 --json audit.json
python3 ai_tell_audit.py sections/methods.tex --section methods   # procedure text: no length targets
```

Reads `.tex`, `.md`, `.txt`, and `.docx`. Rule ids match the section numbers in
`references/ai-tells.md`.

It masks what must never be edited before matching: LaTeX comments, inline and displayed math,
`\cite`/`\ref`/`\label`/`\url`, verbatim and algorithm blocks, tabular environments, the body of
float environments, and the protected technical terms listed in `ai-tells.md`. Caption text
inside a float is audited, because a caption is prose. It scans by paragraph rather than by
line, so a tell that wraps across a line break is still found.

A bracket that marks a missing fact, `[insert ...]` or `[CITE: ...]`, is reported in its own
group, `P0`, "Unresolved placeholder", with its line: fill it before submission, do not delete it.
It is reported wherever it stands, including a table cell, an equation and a figure body, but
not in a LaTeX comment. `T0` is for true pasted artefacts, and those are deleted.

A `.tex` file is audited together with the files it includes (`\input`, `\include`, `\subfile`,
`\import`, `\subimport`, `\includefrom`, `\subincludefrom`). Each hit carries the name and line of the
file it is in, and a file given twice is audited once. An include target that cannot be found is
listed as not checked.

What it could not read, it names as not checked: a missing or unreadable file, a LaTeX
environment that is opened and never closed, and, in a `.docx`, equations, text boxes, headers
and footers. Exit code 0 when every file was read in full, 2 for a usage error such as an
unknown rule id, 3 when something was not checked. Hits alone do not change the exit code.

**Its output is evidence, not a verdict.** It cannot tell a real range from a false one, or a
field's technical `enhance` from filler. `references/ai-tells.md` decides every hit, and its
`What NOT To Flag` section overrides the script. Act on clusters, not on isolated hits.

It deliberately does not ban dashes, flag correct hedging, flag repeated technical terms, or
produce a detector score.

## check_package.py

```bash
python3 check_package.py
python3 check_package.py --root /path/to/paper-skills
```

Fourteen checks. Exit 0 clean, 1 on any failure, 2 for a wrong `--root`, 3 when nothing failed
but a check could not run. It needs PyYAML for a complete result: without it the YAML examples are
not parsed and it exits 3. Run it after editing the skill.

1. Each `SKILL.md` has valid frontmatter, with the name matching the directory and the
   description within the 1024-character limit.
2. Every path under references, agents, or scripts mentioned anywhere exists.
3. Every bare file name written in backticks resolves to a real file. The skills refer to
   siblings by bare name, so a typo there is otherwise silent.
4. Every `Execution Rule N` and `Global Principle N` reference points at a rule that exists.
   Inserting a rule renumbers every reference after it, and nothing else catches that.
5. Every `.paper/` file written anywhere appears in `paper-memory.md`'s Directory block, which
   is the one complete description of that directory.
6. No reference or agent file is orphaned.
7. Agent frontmatter is complete, the name matches the filename, and any agent with write
   access states its write scope.
8. Both plugin manifests parse and point at real files. `plugin.json` has no `agents` field:
   Claude Code loads agents from the top-level `agents/` folder, and an agent file inside a
   skill folder is reported.
9. Every fenced YAML example block parses.
10. Every Python script compiles and every shell script parses; both are executable and have
   a shebang.
11. `INSTALL.md` names every skill, agent, and script.
12. `SKILL.md` still states the shape-exclusivity and cross-cutting rules.
13. Every slash command names a skill this package ships and says to stop if the skill fails
    to load.
14. Each skill description starts with `Use when`, each `SKILL.md` is inside its word budget
    and has a `When to Use` section, each long guide says when to load it, each agent says
    when to dispatch it, and each script is run through `python3`.

It checks the files the package ships. A virtual environment and a cache folder inside the
working copy are left out.

Checks 3, 4, and 5 exist because each one caught a real fault that a read-through missed.

## check_revision_tokens.py

```bash
python3 check_revision_tokens.py --source old.tex --revised new.tex
python3 check_revision_tokens.py --source old.docx --revised new.docx --terms .paper/terms.yml
python3 check_revision_tokens.py --source a.md --revised b.md --strict --json out.json
```

The Revision Contract in `SKILL.md` says a style revision returns its frozen set unchanged.
This script lists what a revision removed and what it added, in eight groups: numbers with
their units, ranges and comparison signs; citations (every key of a `\cites{a}{b}` multicite
too); cross-references; hedges; locked terms; symbols, which covers Greek letters and metric
names such as `sDA300/50`; abbreviations and standard names such as `DGP` and
`CIE S 026:2018`; and proper names. The hedges group holds the claim verbs with their tense,
the modals `may might could can would`, the approximators `approximately about around roughly
nearly almost`, and the bounds `up to`, `at least`, `at most`, `more than`, `less than`,
`no more than` and `no less than`. `about` and `around` count only before a number. The
proper-name group holds a word that is written capitalised in mid-sentence position in either
text, counted wherever it stands in both texts, and any CamelCase or mixed-case name such as
`EnergyPlus`. A single line break is not a sentence start, so a re-wrapped paragraph gives no
difference, and moving a name to the start of a sentence is not one either.
`400–700 nm` rewritten as `400 and 700 nm`, `p < 0.05` rewritten as `p > 0.05`, a dropped
`may`, `at least` changed to `more than`, `Radiance` changed to `EnergyPlus`, and a `\cite` key
that went missing all show up as one line each.

It folds Unicode first, so a full-width digit is not reported as a change. One quantity in two
spellings compares equal: `cd m^-2` and `cd/m²`, `\pm` and `±`, `1,5` and `1.5`, `[12, 13]` and
`[13, 12]`. A word in capitals that the same text also writes in ordinary case is not treated as
an abbreviation, so a change of heading case is not a difference. The dash inside a
range is part of the frozen set: an en dash replaced by a hyphen is reported. In a `.tex` file
`--` is the en dash. It follows `\input`, `\include`, `\subfile` and the two-argument `\import` family in a LaTeX
project (`\input` and `\include` against the root file's folder first, then the including file's
folder; `\subfile` and `\subimport` against the including file's folder) and reads `.docx` table cells and footnotes.

Two limits, printed with every run. It sees tokens, not meaning: it cannot see a negation or a
changed sense, and it sees a reversed comparison only when the sign sits next to a number. And
a difference is not a fault when the revision was asked to change that number. Exit code is 0
unless `--strict` is given, except 2 when an input file cannot be read or the `--json` path
cannot be written (checked before the run). With `--strict`, 1
means a difference, and 3 means no difference in what was read but something was not checked:
an included file was not found, a Word equation, text box, header or footer was skipped, or
the `--terms` file could not be read or has no `terms:` key.

It needs Python 3.9 or newer, as every script here does.

## check_ledger.py

```bash
python3 check_ledger.py path/to/.paper
python3 check_ledger.py path/to/.paper --manuscript main.tex
python3 check_ledger.py path/to/.paper --manuscript paper.docx --json findings.json
```

Checks `claims.yml`, `figures.yml`, `terms.yml`, `gap.yml`, and `changes.yml` against the
rules in `references/paper-memory.md` and in the change-ledger reference of
`responding-to-reviewers`: a status outside its allowed values, empty evidence under the
wrong status, a verb stronger than the status permits, a `rejected` claim, a `done` reviewer
comment with no `verified_on`, an id that points at nothing, a list field written as a plain string, a symbol
with two meanings, and a quantity with two symbols.

With `--manuscript` it also traces numbers. A number quoted in the Abstract, Introduction,
Discussion, or Conclusion must appear in a `key_numbers` entry, in a table, or in the
Results; and every `key_numbers` value must appear somewhere in the manuscript. That is the
check for a figure that was regenerated while the Abstract kept the old value. Whole
numbers are traced too, apart from years, citation numbers, list numbers and labels. Numbers in
Methods are never flagged. It also looks for `never_use` terms outside quotations, and checks
that each dissenting study recorded in `gap.yml` is named in the Discussion. That last check
shows the study is named there. It cannot show the study is answered.

The verb rule: a `needs evidence` row may not carry `shows`, `demonstrates`, `proves`,
`establishes`, `confirms` or `indicates`; a `gap` row carries no verb, except that it may state an
assumption with `assume` or `assumes`; a `rejected` row carries none and is itself reported
(`CLAIM_REJECTED`, which blocks gate item 1).

For `changes.yml` it checks duplicate and missing ids; a `decision` outside `concede`,
`partially concede` and `contest` (`CHANGE_DECISION_INVALID`); a proposed decision
(`decision_confirmed: false`, `CHANGE_DECISION_PROPOSED`); a `done_when` missing on any conceded
or partly conceded row; a `done` row with an empty `manuscript_change` or `location`; a conceded
row with no `location` once it is `done` or `partial`; a row with no `response_paragraph`; and a
`waived` row with no `waived_by`, `waived_risk` or decision on `flagged_to_editor`. Ids of the
form `E.n` with `reviewer: editor`, `affects_runs`, `amendment` and the top-level `updated` are
accepted. It does not run cross-check 1 (the count against the decision letter), the second
halves of checks 7 and 8, the second half of 9 or check 10; every run says so. When `claims.yml`
is absent and `changes.yml` exists, the change findings are still printed.

When `design.yml` sits beside the ledger, it lists each planned claim that no `claims.yml` row
names in `planned_claim` as a note that does not fail the run, and reports a claim whose planned
claim a `post hoc` amendment of `kind: choice` touched and whose `analysis_status` is not
`post hoc` (`CLAIM_POST_HOC_NOT_MARKED`). Without `design.yml` this part says nothing.

Each finding has a code, the file, the row id, and a message. Exit 2 also means the `--json` path
cannot be written. It needs PyYAML; without it
the script prints `not checked: install pyyaml` and exits 3. An absent file, a section it
could not find, an include target it could not open, and each part of a Word file it could not
read (equations, text boxes, headers and footers) are each printed as not checked,
with the numbers of the consistency rules that did not run, and none of them counts as clean.
`changes.yml` is the one exception: it exists only after peer review, so its absence is not a
fault. Every run also prints which rules of `paper-memory.md` this script does not check at
all. Exit code 0 no findings, 1 findings, 3 not checked: either nothing could be checked, or
nothing wrong was found but a file or a part of the manuscript was not read.

Give it the `.paper` folder, or the manuscript folder that contains it.

It cannot judge whether evidence supports a claim. That is the `claim-auditor` agent's job,
and the agent runs this script first.

## bib_check.py

```bash
python3 bib_check.py refs.bib
python3 bib_check.py refs.bib --tex main.tex
python3 bib_check.py refs.bib --tex main.tex --online
python3 bib_check.py refs.bib --online --email you@example.org --json report.json
```

It writes at most two files, each only when you ask: the verified list with `--record` and
the findings report with `--json`. A `--json` path that cannot be written ends the run before
any check, with exit 2.

Offline: the required fields per entry type from `references/latex-mechanics.md`, duplicate
keys, DOIs, and titles, a page range written with one hyphen, and, with `--tex`, cited keys
that have no entry and entries never cited.

With `--online` it resolves each DOI and compares the record's title, year, and first author
with the entry. A DOI that resolves to a different paper is the signature of a mistyped or
invented reference. It then looks for a retraction, a correction, or an expression of
concern.

Sources: `doi.org` for the record, which covers Crossref and DataCite DOIs, so arXiv DOIs
work; Crossref and OpenAlex for notices. All free, no key. Only the DOI is sent. Your email
is sent only if you pass `--email`, and only to Crossref.

The notice summary counts three states: **notice found**, **no notice found in the sources
checked**, and **not checked**. A failed request is not checked. "No notice found" is not
proof that none exists.

It reads `.bib` and LaTeX sources only. `--tex` refuses a file that is not `.tex` (exit 2).
For a Word manuscript, export the reference-manager library to `.bib` with the same citation
keys, build the list with `--online --record`, and compare the cited items with the list by
hand.

It also keeps the list of works a draft may cite, `.paper/verified-refs.yml`. A `doi` row
says that the DOI points to a record whose title, and first author or year, match the entry.
It does not say that the work supports any sentence. With `--online --record <path>` it
writes a `doi` row (`key`, `doi`, `title`, `first_author`, `year`, `checked_on`) for each entry
that passes that test. It writes no row, and says why (`RECORD_NOT_WRITTEN`), for an entry
with too little metadata to compare, and for a work with a retraction, withdrawal, removal or
expression-of-concern notice. It always keeps the `manual` rows the author wrote. It never
replaces one: when the DOI also matched, it adds the DOI evidence and keeps the note. It
reports a manual row whose key is not in the `.bib` (`VERIFIED_ROW_ORPHAN`), and a manual row
whose entry had a DOI mismatch in the same run (`VERIFIED_ROW_KEPT_MISMATCH`). It drops a
`doi` row whose entry no longer matches. It writes no row, and says so, when no notice source
answered for the DOI (`RECORD_NOT_WRITTEN`, counted as not checked). A row whose `method` is not
`doi` is always kept as written; a method that is neither `doi` nor `manual` is reported as
`VERIFIED_ROW_INCOMPLETE`. Fields the author added to a row keep their type when the list is
rewritten. `--record` rewrites the whole file, so comments in it are lost.

A `manual` row is written by the author. It needs `key`, `title`, `checked_on` (an ISO date)
and a `note` of at least three words that says how the work was checked.

With `--tex <file> --verified <path>` it reports each cited key the list does not cover
(`CITE_NOT_VERIFIED`), each row that lacks a field (`VERIFIED_ROW_INCOMPLETE`), and each row
whose `doi`, `title`, `first_author` or `year` differs from the entry now
(`CITE_VERIFICATION_STALE`). The title is compared exactly after case and punctuation are
folded. With `\nocite{*}` it checks every entry. It reads every key of `\cites{a}{b}` and the
other biblatex multicites, and ignores set-up commands such as `\setcitestyle` and
`\citetext`. When `--tex` is given and the file holds no cited key it prints "citation
coverage: not checked: no citation command was found in <file>" and exits 3, with or without
`--verified`. `--verified` needs PyYAML, and so does `--record` onto an existing
list. A list it cannot read in full (no `references` key, `references` not a list, a row that
is not a mapping, a row with no `key`) is reported as not checked by `--verified`; `--record`
refuses to rewrite it, prints the reason, exits 2 and leaves the file unchanged.

Retraction, withdrawal and removal notices are reported as `NOTICE_RETRACTION`; an expression
of concern as `NOTICE_CONCERN`; a correction or other update as `NOTICE_CORRECTION`; a new
version or edition as `NOTICE_NEW_VERSION`, which is information. The type Crossref gives
stays in the message.

Exit code 0 no findings, 1 findings, 2 it could not start (wrong arguments, a file that
could not be read, no entries, a `--tex` file that is not `.tex`), 3 no findings but part of
the check did not run: an online request failed, a file named by `\input` was missing, an
entry type has no field rules, an entry had too little metadata to compare, or `--tex` found
no cited key.

## A note on certificates

`fetch_oa_pdf.py` and `bib_check.py` verify every TLS connection. On a macOS Python
installed from python.org the certificate store is empty until its `Install
Certificates.command` is run, and every request then fails. Both scripts fall back to the
operating system's own certificate bundle when Python has none. Verification is never
switched off. If requests still fail with a certificate error, run `pip install certifi`.
