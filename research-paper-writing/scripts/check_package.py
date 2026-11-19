#!/usr/bin/env python3
"""Self-check for the paper-skills package.

Runs the structural checks that a human review would otherwise have to repeat by hand:
every cross-reference resolves, no reference file is orphaned, frontmatter is well formed and
within the description limit, the plugin manifests point at files that exist, the YAML
examples in the documentation parse, and every script compiles.

Run it from anywhere:
    python3 research-paper-writing/scripts/check_package.py
    python3 check_package.py --root /path/to/paper-skills

Exit code 0 = clean, 1 = at least one failure, 2 = wrong --root, 3 = no failure but a check
could not run (PyYAML is not installed, so the YAML examples were not parsed). Standard library
only, except that check.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Iterator

FAIL: list[str] = []
WARN: list[str] = []
PASS: list[str] = []
SKIPPED: list[str] = []

DESC_LIMIT = 1024
SKILLS = ("research-study-design", "research-paper-writing", "responding-to-reviewers")


def ok(msg: str) -> None:
    PASS.append(msg)


def bad(msg: str) -> None:
    FAIL.append(msg)


def warn(msg: str) -> None:
    WARN.append(msg)


# Folders that sit inside a working copy and are not part of the package.
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}


def walk(root: Path, pattern: str) -> Iterator[Path]:
    """`root.rglob(pattern)`, limited to the files the package ships."""
    for path in root.rglob(pattern):
        parts = path.relative_to(root).parts
        if SKIP_DIRS.intersection(parts):
            continue
        yield path


def strip_fenced(text: str) -> str:
    """Blank out fenced code blocks. Paths inside a YAML or shell example are illustrative,
    not references to files this package must ship."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out, key = {}, None
    for line in m.group(1).split("\n"):
        fm = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if fm:
            key = fm.group(1)
            out[key] = fm.group(2)
        elif key and line.startswith((" ", "\t")):
            out[key] += " " + line.strip()
    return out


# --------------------------------------------------------------------------- checks

def check_skills(root: Path) -> None:
    for name in SKILLS:
        d = root / name
        if not d.is_dir():
            bad(f"missing skill directory: {name}")
            continue
        sk = d / "SKILL.md"
        if not sk.is_file():
            bad(f"{name}: no SKILL.md")
            continue
        fm = frontmatter(sk)
        if fm.get("name") != name:
            bad(f"{name}/SKILL.md: frontmatter name is {fm.get('name')!r}, "
                f"must match the directory name")
        desc = fm.get("description", "")
        if not desc:
            bad(f"{name}/SKILL.md: no description")
        elif len(desc) > DESC_LIMIT:
            bad(f"{name}/SKILL.md: description {len(desc)} chars, limit {DESC_LIMIT}")
        else:
            ok(f"{name}/SKILL.md frontmatter valid, description {len(desc)}/{DESC_LIMIT}")


# Words in the body of each SKILL.md. The body loads in full every time the skill fires.
# The skill-writing standard asks for far less. These two files each carry a contract and a
# routing table that every task needs, so the budget is a ceiling against regrowth: version
# 1.2.0 had 3,875 and 2,447 words.
WORD_BUDGET = {"research-study-design": 900, "research-paper-writing": 2600,
               "responding-to-reviewers": 2000}


def check_skill_quality(root: Path) -> None:
    """The description says when to use the skill and nothing else; the body stays small;
    the reader is told when the skill applies; a script is run through its interpreter."""
    for name in SKILLS:
        sk = root / name / "SKILL.md"
        if not sk.is_file():
            continue
        text = sk.read_text(encoding="utf-8")
        desc = frontmatter(sk).get("description", "")
        if not desc.startswith("Use when"):
            bad(f"{name}/SKILL.md: description must start with 'Use when' and give triggers "
                f"only, not a summary of what the skill does")
        body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
        words = len(body.split())
        budget = WORD_BUDGET.get(name, 1500)
        if words > budget:
            bad(f"{name}/SKILL.md: {words} words, over its word budget of {budget} — move "
                f"detail into a reference file")
        if not re.search(r"^## When to Use\b", body, re.M):
            bad(f"{name}/SKILL.md: no '## When to Use' section")
    # A guide is chosen from its first lines. A long one says when to load it and what it holds.
    for name in SKILLS:
        for guide in sorted((root / name / "references").glob("*.md")):
            text = guide.read_text(encoding="utf-8")
            if len(text.splitlines()) <= 100:
                continue
            head = "\n".join(text.splitlines()[:12])
            for marker in ("**Load when:**", "**Contents:**"):
                if marker not in head:
                    bad(f"{guide.relative_to(root)}: over 100 lines with no {marker} line in "
                        f"its first 12 lines")
    for agent in sorted((root / "agents").glob("*.md")):
        if not re.search(r"\bUse (?:when|before|after)\b", frontmatter(agent).get("description", "")):
            bad(f"{agent.relative_to(root)}: description says what the agent does but not "
                f"when to dispatch it — add a 'Use when ...' sentence")
    runs = re.compile(r"`((?:\S*/)?scripts/[a-z_]+\.py [^`]+)`")
    for doc in walk(root, "*.md"):
        for hit in runs.findall(strip_fenced(doc.read_text(encoding="utf-8", errors="replace"))):
            bad(f"{doc.relative_to(root)}: `{hit[:50]}` runs a script by its bare path — write "
                f"`python3 {hit.split()[0]} ...`")
    ok("skill descriptions, word budgets and script invocations checked")


def check_refs(root: Path) -> None:
    """Every `references/x.md` and `agents/x.md` mentioned anywhere must exist."""
    pattern = re.compile(r"(?:references|agents|scripts)/[A-Za-z0-9._/-]+"
                         r"\.(?:md|yaml|py|sh)")
    # THIRD_PARTY.md names files in other repositories, by design.
    docs = [p for p in walk(root, "*.md") if p.name != "THIRD_PARTY.md"]
    missing: set[tuple[str, str]] = set()
    for doc in docs:
        body = strip_fenced(doc.read_text(encoding="utf-8", errors="replace"))
        for ref in pattern.findall(body):
            if any((root / s / ref).is_file() for s in SKILLS) or (root / ref).is_file():
                continue
            missing.add((str(doc.relative_to(root)), ref))
    if missing:
        for doc, ref in sorted(missing):
            bad(f"broken reference in {doc}: {ref}")
    else:
        ok(f"all cross-references resolve ({len(docs)} documents scanned)")


def check_bare_names(root: Path) -> None:
    """Both skills refer to sibling files by bare name in backticks — `results.md`,
    `sentence-craft.md`. A typo there is silent, so check every one resolves."""
    known = {p.name for s in SKILLS for p in (root / s / "references").rglob("*.md")}
    known |= {p.name for p in (root / "agents").glob("*.md")}
    known |= {p.name for s in SKILLS for p in (root / s / "scripts").glob("*")}
    known |= {p.name for p in root.iterdir() if p.is_file()}      # repo-root files
    known |= {p.name for p in (root / ".github").rglob("*") if p.is_file()}
    for extra in ("tests", "commands"):                       # additive root folders
        known |= {p.name for p in (root / extra).rglob("*") if p.is_file()}
    known |= {"SKILL.md", "README.md", "CLAUDE.md", "AGENTS.md", "THIRD_PARTY.md",
              "plugin.json", "marketplace.json"}
    bare = re.compile(r"`([a-z0-9][a-z0-9._-]*\.(?:md|py|sh|yml|yaml))`")
    bad_refs: set[tuple[str, str]] = set()
    n = 0
    for doc in walk(root, "*.md"):
        body = strip_fenced(doc.read_text(encoding="utf-8", errors="replace"))
        for name in bare.findall(body):
            n += 1
            if name in known:
                continue
            # .paper/ working files are created at run time, not shipped.
            if name in {"claims.yml", "figures.yml", "terms.yml", "gap.yml",
                        "changes.yml", "venue.yml", "question.yml", "design.yml",
                        "runs.yml", "verified-refs.yml"}:
                continue
            bad_refs.add((str(doc.relative_to(root)), name))
    if bad_refs:
        for doc, name in sorted(bad_refs):
            bad(f"bare filename in {doc} matches no file in the package: `{name}`")
    else:
        ok(f"all {n} bare `filename.md` references resolve")


def _numbered_items(text: str, heading: str) -> set[int]:
    """Collect the top-level list numbers under a `## heading` block."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return set()
    return {int(x) for x in re.findall(r"^(\d+)\.\s", m.group(1), re.M)}


def check_numbered_crossrefs(root: Path) -> None:
    """`SKILL.md Execution Rule 9` must point at a rule that exists. Inserting a rule
    silently renumbers every reference to the ones after it, and nothing else catches it."""
    sk = (root / "research-paper-writing" / "SKILL.md").read_text(encoding="utf-8")
    rtr = (root / "responding-to-reviewers" / "SKILL.md").read_text(encoding="utf-8")
    sets = {
        ("rpw", "Execution Rule"): _numbered_items(sk, "Execution Rules"),
        ("rpw", "Global Principle"): _numbered_items(sk, "Global Principles"),
        ("rtr", "Execution Rule"): _numbered_items(rtr, "Execution Rules"),
        ("rtr", "Global Principle"): _numbered_items(rtr, "Global Principles"),
    }
    for key, nums in sets.items():
        if not nums:
            bad(f"could not read the numbered list for {key[1]}s in {key[0]}/SKILL.md")

    pat = re.compile(r"(Execution Rules?|Global Principles?)\s+(\d+)(?:\s+and\s+(\d+))?")
    n = 0
    for doc in walk(root, "*.md"):
        skill = "rtr" if "responding-to-reviewers" in doc.parts else "rpw"
        body = strip_fenced(doc.read_text(encoding="utf-8", errors="replace"))
        for m in pat.finditer(body):
            kind = "Execution Rule" if m.group(1).startswith("Execution") else "Global Principle"
            # A reference inside one skill to "SKILL.md" means its own SKILL.md unless the
            # other skill is named on the same line.
            target = skill
            line = body[body.rfind("\n", 0, m.start()) + 1:body.find("\n", m.end())]
            if "responding-to-reviewers" in line:
                target = "rtr"
            elif "research-paper-writing" in line:
                target = "rpw"
            valid = sets.get((target, kind), set())
            for g in (m.group(2), m.group(3)):
                if g is None:
                    continue
                n += 1
                if int(g) not in valid:
                    bad(f"{doc.relative_to(root)}: '{kind} {g}' does not exist in "
                        f"{target}/SKILL.md (it has 1-{max(valid) if valid else 0})")
    ok(f"all {n} numbered rule reference(s) point at an existing item")


def check_paper_memory_dir(root: Path) -> None:
    """paper-memory.md's Directory block is the one complete description of `.paper/`.
    Anything that writes a file there must appear in it."""
    pm = root / "research-paper-writing" / "references" / "paper-memory.md"
    text = pm.read_text(encoding="utf-8")
    m = re.search(r"^## Directory\s*\n+```(.*?)```", text, re.M | re.S)
    if not m:
        bad("paper-memory.md has no Directory code block")
        return
    listed = m.group(1)
    used: set[str] = set()
    for doc in walk(root, "*.md"):
        for ref in re.findall(r"`\.paper/([A-Za-z0-9_<>-]+(?:\.(?:yml|md))?)/?[^`]*`",
                              doc.read_text(encoding="utf-8", errors="replace")):
            used.add(ref)
    missing = sorted(x for x in used if x and x not in listed)
    if missing:
        for x in missing:
            bad(f"`.paper/{x}` is written somewhere but is not in paper-memory.md's "
                f"Directory block")
    else:
        ok(f"paper-memory.md's Directory block lists all {len(used)} `.paper/` entries in use")


def check_orphans(root: Path) -> None:
    """A reference or agent file nothing points at is dead weight."""
    targets = []
    for s in SKILLS:
        targets += sorted((root / s / "references").rglob("*.md"))
    targets += sorted((root / "agents").glob("*.md"))
    corpus = {p: p.read_text(encoding="utf-8", errors="replace")
              for p in walk(root, "*.md")}
    corpus.update({p: p.read_text(encoding="utf-8", errors="replace")
                   for p in walk(root, "*.json")})
    orphans = []
    for t in targets:
        # An agent is dispatched by its name, so the name in backticks is its reference.
        needle = f"`{t.stem}`" if t.parent == root / "agents" else t.name
        if not any(needle in text for p, text in corpus.items() if p != t):
            orphans.append(str(t.relative_to(root)))
    if orphans:
        for o in orphans:
            bad(f"orphan file, nothing references it: {o}")
    else:
        ok(f"no orphan files ({len(targets)} reference and agent files all reachable)")


def check_agents(root: Path) -> None:
    """Claude Code loads a plugin's agents from the top-level agents/ folder. An agent file
    anywhere else is not loaded, and the plugin validator does not say so."""
    required = ("name", "description", "tools", "model")
    found = 0
    for s in SKILLS:
        for a in sorted((root / s / "agents").glob("*.md")):
            bad(f"{a.relative_to(root)}: agent file inside a skill folder is not loaded by the "
                f"plugin — move it to agents/")
    for a in sorted((root / "agents").glob("*.md")):
        found += 1
        fm = frontmatter(a)
        missing = [f for f in required if f not in fm]
        if missing:
            bad(f"{a.relative_to(root)}: frontmatter missing {', '.join(missing)}")
        if fm.get("name") and fm["name"] != a.stem:
            bad(f"{a.relative_to(root)}: frontmatter name {fm['name']!r} != filename")
        if "Write" in fm.get("tools", "") or "Edit" in fm.get("tools", ""):
            body = a.read_text(encoding="utf-8")
            if not re.search(r"write only (?:inside|to)|may write only", body, re.I):
                bad(f"{a.relative_to(root)}: has write access but never states its write "
                    f"scope — say 'You may write only inside <path>'")
    if not found:
        bad("no agent files in agents/")
    ok(f"{found} agent file(s) checked")


def check_plugin(root: Path) -> None:
    d = root / ".claude-plugin"
    for name in ("plugin.json", "marketplace.json"):
        p = d / name
        if not p.is_file():
            bad(f"missing {name}")
            continue
        try:
            js = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad(f"{name} does not parse: {e}")
            continue
        ok(f"{name} parses")
        for rel in js.get("skills", []):
            if not (root / rel).exists():
                bad(f"plugin.json skills: path does not exist: {rel}")
        if name == "plugin.json":
            for s in SKILLS:
                if not any(s in str(x) for x in js.get("skills", [])):
                    bad(f"plugin.json does not list the {s} skill")
            if "agents" in js:
                bad("plugin.json has an `agents` field. Claude Code loads agents from the "
                    "top-level agents/ folder; a file listed here is not loaded. Remove the field.")


def check_yaml_blocks(root: Path) -> None:
    try:
        import yaml
    except ImportError:
        SKIPPED.append("YAML example blocks not parsed: pyyaml is not installed")
        return
    n = errs = 0
    for doc in walk(root, "*.md"):
        text = doc.read_text(encoding="utf-8", errors="replace")
        for block in re.findall(r"```yaml\n(.*?)```", text, re.S):
            n += 1
            try:
                yaml.safe_load(block)
            except Exception as e:                            # noqa: BLE001
                errs += 1
                bad(f"YAML example does not parse in {doc.relative_to(root)}: "
                    f"{str(e).splitlines()[0]}")
    if not errs:
        ok(f"{n} YAML example block(s) parse")


def check_scripts(root: Path) -> None:
    import shutil
    import subprocess

    executables = [p for s in SKILLS for p in sorted((root / s / "scripts").glob("*.py"))]
    executables += sorted(root.glob("*.sh"))

    for p in executables:
        text = p.read_text(encoding="utf-8")
        if p.suffix == ".py":
            try:
                ast.parse(text)
            except SyntaxError as e:
                bad(f"{p.relative_to(root)}: syntax error line {e.lineno}")
        elif p.suffix == ".sh" and shutil.which("bash"):
            r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
            if r.returncode:
                bad(f"{p.relative_to(root)}: shell syntax error: "
                    f"{r.stderr.strip().splitlines()[-1] if r.stderr else '?'}")
        if p.name.startswith("_"):          # an imported helper module, not a command
            continue
        if not (p.stat().st_mode & 0o111):
            warn(f"{p.relative_to(root)}: not executable (chmod +x)")
        if not text.startswith("#!"):
            warn(f"{p.relative_to(root)}: no shebang")
    ok(f"{len(executables)} script(s) parse")


def check_install(root: Path) -> None:
    p = root / "INSTALL.md"
    if not p.is_file():
        bad("no INSTALL.md")
        return
    text = p.read_text(encoding="utf-8")
    for s in SKILLS:
        if s not in text:
            bad(f"INSTALL.md does not mention the {s} skill")
    for a in sorted((root / "agents").glob("*.md")):
        if a.stem not in text:
            bad(f"INSTALL.md does not mention agent {a.stem}")
    for skill in SKILLS:
        for sc in sorted((root / skill / "scripts").glob("*.py")):
            if sc.name.startswith("_"):
                continue
            if sc.name not in text:
                warn(f"INSTALL.md does not mention script {sc.name}")
    ok("INSTALL.md covers the skills and agents")


def check_shape_exclusivity(root: Path) -> None:
    """method.md and methods-journal.md must never be loaded together; review-papers.md
    replaces methods-journal.md and results.md. The SKILL.md must say so."""
    sk = (root / "research-paper-writing" / "SKILL.md").read_text(encoding="utf-8")
    for phrase, why in [
        ("Never load both", "the method.md / methods-journal.md exclusivity rule"),
        ("review-papers.md", "the review paper shape"),
        ("word-manuscripts.md", "the Word manuscript path"),
        ("paper-memory.md", "the on-disk claim ledger"),
    ]:
        if phrase not in sk:
            bad(f"research-paper-writing/SKILL.md no longer states {why} ({phrase!r})")
    ok("SKILL.md still states the shape-exclusivity and cross-cutting rules")


# --------------------------------------------------------------------------- main

def check_commands(root: Path) -> None:
    """A slash command is a thin pointer to a skill. One that names a skill this package does
    not ship, or that may fire without the user typing it, is a silent fault."""
    d = root / "commands"
    if not d.is_dir():
        return
    files = sorted(d.glob("*.md"))
    for f in files:
        fm = frontmatter(f)
        rel = f.relative_to(root)
        if not fm.get("description"):
            bad(f"{rel}: frontmatter has no description")
        if fm.get("disable-model-invocation", "").strip().lower() != "true":
            bad(f"{rel}: frontmatter must set disable-model-invocation: true")
        body = f.read_text(encoding="utf-8")
        named = re.findall(r"with skill `([a-z0-9-]+)`", body)
        if not named:
            bad(f"{rel}: does not say which skill to invoke")
        for s in named:
            if s not in SKILLS:
                bad(f"{rel}: names skill {s!r}, which this package does not ship")
        if "failed to load" not in body:
            bad(f"{rel}: must say to stop if the skill fails to load")
        if (root / "agents" / f.name).exists() or any(
                (root / s / "references" / f.name).exists() for s in SKILLS):
            bad(f"{rel}: has the same file name as a reference or agent file")
    ok(f"{len(files)} command file(s) checked")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="package root (default: two levels above this script)")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]

    if not (root / "INSTALL.md").is_file():
        return int(bool(print(f"does not look like the package root: {root}", file=sys.stderr))) or 2

    print(f"checking {root}\n")
    for fn in (check_skills, check_skill_quality, check_refs, check_bare_names, check_numbered_crossrefs,
               check_paper_memory_dir, check_orphans, check_agents, check_plugin,
               check_yaml_blocks, check_scripts, check_install, check_shape_exclusivity,
               check_commands):
        try:
            fn(root)
        except Exception as e:                                # noqa: BLE001
            bad(f"{fn.__name__} crashed: {e}")

    for m in PASS:
        print(f"  PASS  {m}")
    for m in WARN:
        print(f"  WARN  {m}")
    for m in SKIPPED:
        print(f"  NOT CHECKED  {m}")
    for m in FAIL:
        print(f"  FAIL  {m}")
    print(f"\n{len(PASS)} passed, {len(WARN)} warning(s), {len(FAIL)} failure(s), "
          f"{len(SKIPPED)} not checked")
    return 1 if FAIL else 3 if SKIPPED else 0


if __name__ == "__main__":
    sys.exit(main())
