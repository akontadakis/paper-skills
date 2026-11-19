#!/usr/bin/env python3
"""Mechanical AI-tell and rhythm audit for a manuscript.

Runs the greppable half of references/ai-tells.md and computes the rhythm metrics that
cannot be grepped. It prints the raw hits with file and line, because a report that says
"audited, clean" without the evidence is not an audit.

It reports. It never edits, and it is not a pass/fail gate. references/ai-tells.md governs
what to do with a hit, and its "What NOT To Flag" section overrides anything here.

Reads .tex, .md, .txt, and .docx. Standard library only — no pip install.

Rule ids carry the confidence tier from ai-tells.md. Tier 0 (leaked chat markup,
tracking parameters, unfilled template fields, assistant scaffolding) is conclusive on a
single hit and is deleted; every other tier needs a cluster. Group P0 reports the package's two
bracket forms for a missing fact, `[insert ...]` and `[CITE: ...]`, wherever they stand,
including inside a table, an equation or a figure body. They are filled before submission and
never deleted.

A `.tex` file is audited together with the files it pulls in (`\\input`, `\\include`,
`\\subfile`, `\\import`, `\\subimport`, `\\includefrom`, `\\subincludefrom`); each hit carries
the name and line of the file it is in. An include target that cannot be found is listed as not
checked. Exit code: 0 nothing not checked, 2 wrong arguments, 3 something was not checked.

Usage:
    python3 ai_tell_audit.py sections/*.tex
    python3 ai_tell_audit.py manuscript.docx --context
    python3 ai_tell_audit.py paper.tex --only T1 T2 T5
    python3 ai_tell_audit.py sections/ --json audit.json

What it does NOT do, on purpose:
  - No dash ban. En dashes in ranges, minus signs, and compound names are correct.
  - No hedge flagging. `suggests` on modelled data is right; see the evidence ladder.
  - No flagging of repeated technical terms, three-part enumerations, or passive voice
    where the actor is irrelevant.
  - No detector score. Uncalibrated, and the wrong objective.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# --------------------------------------------------------------------------- rules
# Category ids match the section numbers in references/ai-tells.md.

RULES: list[tuple[str, str, str, str]] = [
    # (id, name, regex, note)
    # Tier 0. Conclusive on a single hit, and the only rule here that is not a
    # candidate for judgement: a leaked marker or an unfilled placeholder in a
    # manuscript is deleted, not weighed. See ai-tells.md section 0.
    ("T0", "Near-conclusive artefact",
     r"(?i)(oaicite|oai_citation|contentReference|attributableIndex|turn\d+search\d+|"
     r"ppl-ai-file-upload|utm_source=(?:chatgpt|claude|perplexity|copilot|gemini)|"
     r"\[cite:\s*\d+\]|\[span_\d+\]\(start_span\)|"
     # Fixed template fields only. A gap marker that names the missing fact
     # ("[figure needed from the Q1 run]") is correct authoring — see section 0.
     r"\[(?:your name|author name|institution|company|affiliation|date|todo|"
     r"insert x here|insert citation|insert name)\]|"
     r"let me know if you (?:need|would|have)|here is the (?:revised|updated|rewritten)|"
     r"i hope this helps|would you like me to|"
     r"as an? (?:ai|large) language model|"
     r"i (?:do not|don't) have access to real-time)",
     "TIER 0 — pasted, not written. Delete it. Do not weigh it against a cluster."),

    # The package's own bracket forms for a missing fact. They are authoring notes that
    # must be filled before submission; deleting one loses the record of what is missing.
    ("P0", "Unresolved placeholder",
     r"\[insert\b[^\]]{0,200}\]|\[CITE:[^\]]{0,200}\]",
     "Fill it before submission. Do not delete it."),

    ("T1", "Overused register",
     r"\b(crucial|vital|pivotal|paramount|profound|delve\s+into|elucidat\w+|"
     r"underscor\w+|showcas\w+|leverag(?:e|es|ed|ing)|interplay|tapestry|"
     r"testament\s+to|multifaceted|nuanced|paradigm\s+shift|foster(?:s|ed|ing)?|"
     r"garner\w*|spearhead\w*|seamless\w*|holistic|meticulous\w*|"
     r"cutting-edge|unprecedented|groundbreaking|revolutionary|"
     r"streamlin\w+|harness(?:es|ed|ing)?|bolster\w*|empower\w*)\b",
     "state the consequence, or cut"),

    ("T1b", "Register — check in context",
     r"\b(essential|key\s+(?:factor|role|insight|challenge|advantage)|"
     r"enhance(?:s|d|ment)?|boost(?:s|ed|ing)?|align(?:s|ed)?\s+with|"
     r"valuable|meaningful|comprehensive|landscape|ecosystem|realm|"
     r"innovative|transformative|sophisticated|synerg(?:y|ies|istic)|"
     r"(?<!\{)(?<!#\s)methodolog(?:y|ies))\b",
     "filler unless it is the field's technical use — check each; `methodology` is a tell "
     "only where `method` is meant"),

    ("T1c", "Stacked near-synonym adjectives",
     r"\b(?:{V})\s*,\s*(?:{V})\s*,?\s*(?:and\s+)?(?:{V})\b".replace("{V}", (
         r"comprehensive|sophisticated|robust|innovative|powerful|novel|flexible|efficient|"
         r"effective|scalable|advanced|versatile|rigorous|thorough|systematic|holistic|"
         r"elegant|seamless|intuitive|cutting-edge|state-of-the-art")),
     "three praise adjectives in a row say less than one measured property — keep the one "
     "the results support"),

    ("T2", "Participial tail",
     r",\s*(highlight|underscor|emphasis|demonstrat|ensur|reflect|showcas|"
     r"contribut|pav|indicat|suggest|reveal|illustrat|underlin)\w*ing\b",
     "smuggles an untested claim; delete in Results, promote in Discussion"),

    ("T3", "Copula avoidance",
     r"\b(serves?\s+as|stands?\s+as|functions?\s+as|represents?|boasts?|"
     r"possess(?:es|ed)?|constitutes?)\b",
     "use is or has — but `the matrix represents the operator` is correct maths; check each"),

    ("T5", "Negation-contrast framing",
     r"(is\s+not\s+\w[^.]{0,60}?\bbut\b|not\s+merely|not\s+just\b|"
     r"rather\s+than\s+simply|not\s+only\s+[^.]{0,60}?\bbut\b)",
     "state the positive claim directly"),

    # Genuine ranges are excluded up front: numbers, months, weekdays, and numbered
    # document objects are all endpoints of a real scale, which is what the rule allows.
    ("T6", "Possible false range",
     r"\bfrom\s+(?!(?:[\d.]|\$|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
     r"Mon|Tue|Wed|Thu|Fri|Sat|Sun|Table|Fig|Figure|Section|Sec|Eq|Equation|Chapter|"
     r"Appendix|page|p\.|year|day|week|month|hour|case|level|stage|step|"
     r"the\s+(?:first|start|beginning|top|left|lowest|highest)))"
     r"\w[\w\s-]{0,30}?\s+to\s+"
     r"(?!(?:[\d.]|\$|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
     r"Mon|Tue|Wed|Thu|Fri|Sat|Sun|Table|Fig|Figure|Section|Sec|Eq|Equation|Chapter|"
     r"Appendix|page|p\.|the\s+(?:last|end|bottom|right|highest|lowest)))\w",
     "keep from/to for real ranges only — check each"),

    ("T10", "Banned section opener",
     r"(?im)^\s*(?:\\\w+\{)?\s*(In\s+recent\s+years|With\s+the\s+rapid\s+"
     r"(?:development|growth|advance)|Since\s+the\s+dawn\s+of|"
     r"It\s+is\s+widely\s+(?:acknowledged|recognis\w+|recogniz\w+)\s+that|"
     r"As\s+can\s+be\s+seen\s+(?:from|in)|In\s+conclusion|"
     r"This\s+paper\s+has\s+presented|Despite\s+these\s+limitations)",
     "open on the finding or the problem"),

    ("T10b", "Throat-clearing opener",
     r"(?m)^\s*(?:\\\w+\{)?\s*(Moreover|Furthermore|Additionally|Notably|"
     r"Importantly|Indeed|Ultimately|Crucially|That\s+said)\b",
     "fine once; three in a row is structural symmetry (T9)"),

    ("T10c", "Empty transition",
     r"\b(With\s+that\s+in\s+mind|Building\s+on\s+this\s+foundation|"
     r"Taking\s+this\s+(?:a\s+step|one\s+step)\s+further|With\s+this\s+in\s+place)\b",
     "names no relation — state the cause, contrast, or consequence, or cut"),

    ("T11", "Fake-insight marker",
     r"\b(essentially|fundamentally|at\s+(?:its|the)\s+(?:core|heart)|"
     r"in\s+essence|the\s+key\s+insight\s+is|the\s+real\s+question\s+is|"
     r"what\s+really\s+matters|in\s+reality|the\s+deeper\s+\w+|"
     r"the\s+(?:reality|truth)\s+is)\b",
     "state the insight without the label"),

    ("T11b", "Aphorism formula",
     r"\b(is\s+the\s+\w+\s+of\s+\w+\s+(?:for|in)\b|the\s+(?:architecture|language|"
     r"currency|grammar)\s+of\s+\w+|becomes?\s+a\s+trap)\b",
     "replace the saying with the specific claim"),

    ("T12", "Vague source",
     r"\b(studies\s+(?:have\s+)?(?:show|shown|suggest|indicate)|research\s+(?:has\s+)?"
     r"(?:shows?|shown|suggests?|indicates?)|it\s+is\s+(?:well\s+)?known\s+that|"
     r"many\s+(?:authors|researchers|studies)|some\s+studies|"
     r"experts?\s+(?:agree|believe)|little\s+attention\s+has\s+been\s+paid|"
     r"it\s+is\s+(?:widely\s+)?(?:acknowledged|accepted|recognis\w+|recogniz\w+)\s+that)\b",
     "name the study and cite it — an uncited claim about the literature is a gap claim"),

    ("T13", "Unraised objection / fake alternative",
     r"\b(this\s+is\s?n[o']t\s+(?:mainly|really|about)|to\s+be\s+clear|"
     r"do\s?n[o']t\s+get\s+me\s+wrong|this\s+is\s+not\s+to\s+say|"
     r"one\s+might\s+be\s+tempted|a\s+tempting\s+(?:option|approach)|"
     r"an\s+obvious\s+approach\s+would\s+be|you\s+might\s+think)\b",
     "usually leftover drafting; state the real constraint"),

    ("T14", "Content-free opener",
     r"(?i)\bIn\s+this\s+(?:paper|section|study|work),?\s+we\s+(?:will\s+)?"
     r"(?:discuss|present|describe|introduce)\b",
     "acceptable once in the Introduction roadmap; a habit elsewhere"),

    ("T14b", "Generic positive ending",
     r"\b(opens?\s+(?:up\s+)?(?:promising|exciting|new)\s+(?:avenues|possibilities|"
     r"opportunities)|the\s+future\s+of\s+\w+\s+is\s+bright|exciting\s+times|"
     r"represents?\s+an?\s+important\s+step|a\s+step\s+in\s+the\s+right\s+direction|"
     r"paves?\s+the\s+way\s+for)\b",
     "end on the last concrete finding, not on optimism"),

    ("T8b", "Exclamation mark", r"(?<![\\!])!(?!=)", "zero in body text"),
]

# Tier per rule id, from ai-tells.md `Confidence Tiers`. Only Tier 0 acts on one hit.
TIER = {
    "T0": 0, "P0": 0,
    "T1": 1, "T1b": 2, "T1c": 2, "T2": 1, "T3": 2, "T5": 1, "T6": 2,
    "T10": 1, "T10b": 2, "T10c": 2, "T11": 1, "T11b": 1, "T12": 1, "T13": 2,
    "T14": 2, "T14b": 1, "T8b": 3,
}

RHYTHM_ONLY = {"R1"}

# Protected: never flagged, per ai-tells.md Protected Terms.
PROTECTED = [
    r"\b(robust\s+optimisation|robust\s+optimization|robust\s+standard\s+error)\b",
    r"\bstate-of-the-art\b(?=\s+(?:comparison|method|baseline|result))",
    r"\bkey\s+(?:frame|point|value|word)s?\b",
    r"\bcontrast\s+enhancement\b|\bimage\s+enhancement\b|\benhanced\s+sky\b",
    r"\bhighlight(?:ed|ing|s)?\s+(?:cell|row|column|in\s+bold|the\s+best)\b",
]
PROTECTED_RE = re.compile("|".join(PROTECTED), re.I)

SENT_END = re.compile(r"(?<=[.!?])[\s\n]+(?=[A-Z(\\])")


# --------------------------------------------------------------------------- input

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _w(tag: str) -> str:
    return f"{{{_W}}}{tag}"


def _para_text(p, found: set) -> tuple:
    """Text of one paragraph in run order, and the footnote ids it references."""
    out: list = []
    notes: list = []

    def walk(el) -> None:
        for ch in el:
            tag = ch.tag
            if tag == _w("t"):
                out.append(ch.text or "")
            elif tag == _w("tab"):
                out.append(" ")
            elif tag == _w("noBreakHyphen"):
                out.append("-")
            elif tag in (_w("br"), _w("cr")):
                out.append(" ")
            elif tag == _w("footnoteReference") or tag == _w("endnoteReference"):
                notes.append((tag.rsplit("}", 1)[1], ch.get(_w("id"))))
            elif tag == f"{{{_M}}}oMath" or tag == f"{{{_M}}}oMathPara":
                found.add("equations")
            elif tag == _w("txbxContent"):
                found.add("text boxes")
            elif tag == _w("delText"):
                continue
            else:
                walk(ch)

    walk(p)
    return "".join(out), notes


def _textbox_paragraphs(root) -> set:
    """The ids of every paragraph inside a text box. Word stores a text box once under
    `mc:Choice` and again under `mc:Fallback`, so reading them would count the text twice.
    They are skipped, and `read_docx_checked` reports "text boxes" as not checked."""
    return {id(p) for box in root.iter(_w("txbxContent")) for p in box.iter(_w("p"))}


def _note_texts(z: zipfile.ZipFile, name: str, kind: str, found: set) -> dict:
    if name not in z.namelist():
        return {}
    root = ET.fromstring(z.read(name))
    boxed = _textbox_paragraphs(root)
    texts = {}
    for note in root.iter(_w(kind)):
        if note.get(_w("type")) in ("separator", "continuationSeparator",
                                    "continuationNotice"):
            continue
        texts[note.get(_w("id"))] = "\n".join(
            _para_text(p, found)[0] for p in note.iter(_w("p")) if id(p) not in boxed)
    return texts


def read_docx_checked(path: Path) -> tuple:
    """Return (text, not_checked). The body is read in document order; a tab becomes a
    space, a no-break hyphen stays a hyphen, and footnote and endnote text follows the
    paragraph that cites it. Parts that are not read are named in `not_checked`, so a
    caller never presents the result as complete."""
    found: set = set()
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        foot = _note_texts(z, "word/footnotes.xml", "footnote", found)
        end = _note_texts(z, "word/endnotes.xml", "endnote", found)
        extra = [n for n in z.namelist()
                 if re.match(r"word/(header|footer)\d*\.xml$", n)]
    body = root.find(_w("body"))
    lines: list = []
    boxed = _textbox_paragraphs(root)
    for p in (body if body is not None else root).iter(_w("p")):
        # Paragraphs inside a text box are not read, and "text boxes" is reported below.
        if id(p) in boxed:
            continue
        text, notes = _para_text(p, found)
        lines.append(text)
        for kind, nid in notes:
            note = (foot if kind == "footnoteReference" else end).get(nid)
            if note:
                lines.append(note)
    not_checked = []
    if "equations" in found:
        not_checked.append("equations (Word math is not read)")
    if "text boxes" in found:
        not_checked.append("text boxes")
    if extra:
        not_checked.append("headers and footers")
    return "\n".join(lines), not_checked


def read_docx(path: Path) -> str:
    return read_docx_checked(path)[0]


SUPPORTED = (".tex", ".md", ".txt", ".docx")


def load_checked(path: Path) -> tuple:
    """Return (lines, not_checked). Bytes that are not valid UTF-8 are replaced so the rest
    can be read, and the file is reported as partly not checked."""
    if path.suffix.lower() == ".docx":
        return read_docx(path).splitlines(), []
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8").splitlines(), []
    except UnicodeDecodeError as e:
        return (raw.decode("utf-8", errors="replace").splitlines(),
                [f"not valid UTF-8 (first bad byte at offset {e.start}); undecodable bytes "
                 f"were replaced and not read"])


def load(path: Path) -> list[str]:
    return load_checked(path)[0]


_ENV_MASK = re.compile(
    r"\\begin\{(verbatim\*?|lstlisting|minted|algorithm\w*|equation\*?|align\*?|gather\*?|"
    r"multline\*?|tabular\*?|tabu)\}.*?\\end\{\1\}", re.S)
_ENV_OPEN = re.compile(
    r"\\begin\{(verbatim\*?|lstlisting|minted|algorithm\w*|equation\*?|align\*?|gather\*?|"
    r"multline\*?|tabular\*?|tabu)\}")
_FLOAT = re.compile(r"\\begin\{(figure|table)(\*?)\}(.*?)\\end\{\1\2\}", re.S)
_CAPTION = re.compile(r"\\(?:sub)?caption\*?\s*(?:\[[^\]]*\])?\s*\{")


def _blank(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def _float_keep_captions(body: str) -> str:
    """Blank a float's body except the text of its \\caption{...} arguments."""
    out = list(_blank(body))
    for m in _CAPTION.finditer(body):
        depth, i = 1, m.end()
        while i < len(body) and depth:
            c = body[i]
            if c == "\\":
                i += 2
                continue
            depth += (c == "{") - (c == "}")
            i += 1
        end = i - 1 if depth == 0 else i
        out[m.end():end] = body[m.end():end]
    return "".join(out)


def mask_tex_blocks(lines: list) -> tuple:
    """Blank multi-line TeX regions without changing line numbers: comments, verbatim,
    math and algorithm environments, tabulars, and every float except its caption text.
    Returns (masked_lines, not_checked)."""
    text = "\n".join(lines)
    text = re.sub(r"(?<!\\)%[^\n]*", lambda m: "", text)
    text = _FLOAT.sub(lambda m: _blank(text[m.start():m.start(3)])
                      + _float_keep_captions(m.group(3))
                      + _blank(text[m.end(3):m.end()]), text)
    text = _ENV_MASK.sub(lambda m: _blank(m.group(0)), text)
    not_checked = []
    m = _ENV_OPEN.search(text)
    if m:
        ln = text.count("\n", 0, m.start()) + 1
        not_checked.append(f"\\begin{{{m.group(1)}}} on line {ln} is never closed; "
                           f"the rest of the file from there is masked")
        text = text[:m.start()] + _blank(text[m.start():])
    return text.split("\n"), not_checked


def mask_protected_markup(line: str, suffix: str) -> str:
    """Blank out regions that must never be edited, so they are never flagged."""
    if suffix == ".tex":
        line = re.sub(r"(?<!\\)%.*$", "", line)                       # comments
        line = re.sub(r"\$[^$]*\$", " ", line)                        # inline math
        line = re.sub(r"\\(?:cite|ref|cref|eqref|label|url|texttt|verb)\w*"
                      r"\s*(\[[^\]]*\])?\{[^}]*\}", " ", line)
        line = re.sub(r"\\[A-Za-z@]+", " ", line)                     # other macros
    elif suffix in (".md", ".txt"):
        line = re.sub(r"`[^`]*`", " ", line)
        line = re.sub(r"\$[^$]*\$", " ", line)
    return line


def in_verbatim(line: str, state: dict, suffix: str) -> bool:
    """Track fenced code blocks in .md and .txt. TeX regions are masked beforehand by
    mask_tex_blocks, so a one-line environment or a commented \\begin cannot leak state."""
    if suffix in (".md", ".txt"):
        if line.strip().startswith("```"):
            state["fence"] = not state.get("fence", False)
            return True
        return bool(state.get("fence"))
    return False


# --------------------------------------------------------------------------- audit

_EM_DASH = re.compile(r"(?<!-)---(?!-)|\u2014")
_EM_DASH_TEXT = re.compile(r"(?<=\w) -- (?=\w)")


def count_em_dashes(text: str, suffix: str) -> int:
    """Em dashes: `---` and the character `\u2014`, but not one between two digits (`5\u20147`, a
    range). In `.md` and `.txt` a spaced ` -- ` between words counts too; in `.tex` `--` is an
    en dash and is never counted."""
    n = sum(1 for m in _EM_DASH.finditer(text)
            if not (m.start() and m.end() < len(text)
                    and text[m.start() - 1].isdigit() and text[m.end()].isdigit()))
    if suffix in (".md", ".txt"):
        n += len(_EM_DASH_TEXT.findall(text))
    return n


def audit_file(path: Path, only: set[str] | None) -> dict:
    not_checked: list = []
    if path.suffix.lower() == ".docx":
        text_, not_checked = read_docx_checked(path)
        lines = text_.splitlines()
    else:
        lines, not_checked = load_checked(path)
    suffix = path.suffix.lower()
    scan = lines
    if suffix == ".tex":
        scan, nc = mask_tex_blocks(lines)
        not_checked = not_checked + nc
    state: dict = {}
    hits: list[dict] = []
    prose: list[str] = []

    # Scan by paragraph, not by line: a tell such as "from X to Y" or a ", -ing" tail
    # routinely wraps across a line break in a .tex source, and a line-based grep misses it.
    # `offsets` maps a character position in the buffer back to its source line number.
    blocks: list[tuple[str, list[tuple[int, int]]]] = []
    buf, offsets = "", []

    def flush() -> None:
        nonlocal buf, offsets
        if buf.strip():
            blocks.append((buf, offsets))
        buf, offsets = "", []

    for n, raw in enumerate(scan, 1):
        if in_verbatim(raw, state, suffix):
            flush()
            continue
        line = mask_protected_markup(raw, suffix)
        if not line.strip():
            flush()
            continue
        prose.append(line)
        offsets.append((len(buf), n))
        buf += line.rstrip() + " "
    flush()

    def line_of(block_offsets: list[tuple[int, int]], pos: int) -> int:
        ln = block_offsets[0][1] if block_offsets else 0
        for start, n in block_offsets:
            if start <= pos:
                ln = n
            else:
                break
        return ln

    for block, block_offsets in blocks:
        for rid, name, pattern, note in RULES:
            if only and rid not in only and rid.rstrip("b") not in only:
                continue
            # Line-anchored rules must see real line starts, so run those per line.
            if "(?m)" in pattern or "(?im)" in pattern:
                for start, n in block_offsets:
                    seg = mask_protected_markup(scan[n - 1], suffix)
                    pspans = [q.span() for q in PROTECTED_RE.finditer(seg)]
                    for m in re.finditer(pattern, seg):
                        if any(m.start() < e and s0 < m.end() for s0, e in pspans):
                            continue
                        hits.append({"rule": rid, "name": name, "note": note,
                                     "file": str(path), "line": n,
                                     "match": m.group(0).strip()[:60],
                                     "text": lines[n - 1].strip()[:200]})
                continue
            pspans = [q.span() for q in PROTECTED_RE.finditer(block)]
            for m in re.finditer(pattern, block, re.I):
                if any(m.start() < e and s0 < m.end() for s0, e in pspans):
                    continue
                n = line_of(block_offsets, m.start())
                hits.append({"rule": rid, "name": name, "note": note,
                             "file": str(path), "line": n,
                             "match": re.sub(r"\s+", " ", m.group(0)).strip()[:60],
                             "text": lines[n - 1].strip()[:200]})

    # A placeholder inside a masked region (table cell, math, figure body, code) is still
    # unresolved: scan the whole text for group P0, apart from TeX comments.
    if not only or "P0" in only:
        _, _, p0_pattern, p0_note = next(r for r in RULES if r[0] == "P0")
        for n, raw in enumerate(lines, 1):
            body = re.sub(r"(?<!\\)%.*$", "", raw) if suffix == ".tex" else raw
            for m in re.finditer(p0_pattern, body, re.I):
                hits.append({"rule": "P0", "name": "Unresolved placeholder", "note": p0_note,
                             "file": str(path), "line": n,
                             "match": re.sub(r"\s+", " ", m.group(0)).strip()[:60],
                             "text": raw.strip()[:200]})

    # A wrapped match can be found once per block only; dedupe identical (rule, line, match).
    seen, deduped = set(), []
    for h in hits:
        k = (h["rule"], h["line"], h["match"].lower())
        if k in seen:
            continue
        seen.add(k)
        deduped.append(h)
    hits = sorted(deduped, key=lambda h: (h["line"], h["rule"]))

    text = " ".join(prose)
    words = len(re.findall(r"\b[\w'-]+\b", text))
    sents = [s for s in SENT_END.split(text) if len(re.findall(r"\b\w+\b", s)) >= 3]
    lens = [len(re.findall(r"\b[\w'-]+\b", s)) for s in sents]

    rhythm: dict = {"words": words, "sentences": len(sents)}
    if lens:
        rhythm.update(mean=round(statistics.fmean(lens), 1),
                      shortest=min(lens), longest=max(lens),
                      spread=max(lens) - min(lens),
                      short_sentences=sum(1 for x in lens if x <= 10))
        runs, i, worst = 0, 0, 0
        while i < len(lens) - 2:
            win = lens[i:i + 3]
            if max(win) - min(win) <= 5:
                runs += 1
                worst = max(worst, 3)
            i += 1
        rhythm["uniform_runs_of_3"] = runs
    rhythm["em_dashes"] = count_em_dashes(text, suffix)
    rhythm["em_dash_per_1000w"] = round(rhythm["em_dashes"] / words * 1000, 1) if words else 0
    return {"file": str(path), "hits": hits, "rhythm": rhythm,
            "not_checked": not_checked}


def rhythm_findings(r: dict, section: str | None = None) -> list[str]:
    """Section 8 findings. `section="methods"` marks procedure text: a written procedure is
    short, even sentences by design, so the length targets are not applied to it. The em dash
    count still is."""
    out = []
    if r.get("words", 0) < 150:
        return ["passage under 150 words — rhythm targets do not apply"]
    if section == "methods":
        out.append("procedure text — rhythm targets do not apply")
    elif "mean" in r:
        if not 15 <= r["mean"] <= 25:
            out.append(f"mean sentence length {r['mean']} w (target 15-25; the mean yields "
                       f"to the spread — do not pad to hit it)")
        if r["spread"] < 20:
            out.append(f"spread only {r['spread']} w (target >= 20 in any 150-word passage)")
        if r["uniform_runs_of_3"]:
            out.append(f"{r['uniform_runs_of_3']} run(s) of 3 consecutive sentences within "
                       f"+/-5 words")
        per150 = r["short_sentences"] / (r["words"] / 150)
        if per150 < 1:
            out.append(f"{r['short_sentences']} sentence(s) <= 10 words "
                       f"(target at least 1 per 150 words)")
    if r["em_dash_per_1000w"] > 3.3:
        out.append(f"{r['em_dashes']} em dashes = {r['em_dash_per_1000w']}/1000 w "
                   f"(target at most 1 per 300 w). En dashes in ranges are NOT counted.")
    return out


# --------------------------------------------------------------------------- includes

def tex_includes(path: Path, root_dir: Path | None = None) -> tuple:
    """(found, missing): the files a `.tex` file pulls in, as paths, and the names written in
    the source for targets that do not exist. Commented lines are ignored. `root_dir` is the
    folder of the root file, against which `\\input` and `\\include` are resolved first."""
    from _manuscript import _INCLUDE, _TEX_COMMENT, resolve_include   # late: _manuscript imports this module
    try:
        text = _TEX_COMMENT.sub("", path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return [], []
    found, missing = [], []
    for m in _INCLUDE.finditer(text):
        target, name = resolve_include(m, root_dir or path.parent, path.parent)
        (found if target else missing).append(target or name)
    return found, missing


def with_includes(files: list, unchecked: list) -> list:
    """The files to audit: each `.tex` file followed by the files it includes, once each.
    Includes are resolved against the folder of the root file the chain started from."""
    out, seen = [], set()
    queue = [(f, f.parent) for f in files]
    seen.update(f.resolve() for f in files)
    while queue:
        f, root = queue.pop(0)
        out.append(f)
        if f.suffix.lower() != ".tex":
            continue
        found, missing = tex_includes(f, root)
        for name in missing:
            unchecked.append(f"{f}: included file not found: {name}")
        for t in found:
            if t.resolve() not in seen:
                seen.add(t.resolve())
                queue.append((t, root))
    return out


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="files or directories")
    ap.add_argument("--only", nargs="+", help="restrict to rule ids, e.g. T1 T2 T5")
    ap.add_argument("--context", action="store_true", help="print the whole line for each hit")
    ap.add_argument("--json", help="write a machine-readable report")
    ap.add_argument("--section", choices=["methods"],
                    help="the kind of text being audited. `methods` marks procedure text, "
                         "where the sentence-length targets of section 8 do not apply")
    args = ap.parse_args()

    only = None
    if args.only:
        valid = [r[0] for r in RULES]
        known = set(valid) | {v.rstrip("b") for v in valid}
        bad = [o for o in args.only if o not in known]
        if bad:
            print(f"error: unknown rule id(s): {', '.join(bad)}. "
                  f"Valid ids: {', '.join(valid)}", file=sys.stderr)
            return 2
        only = set(args.only)

    unchecked: list[str] = []
    files: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            for ext in ("*.tex", "*.md", "*.txt", "*.docx"):
                files.extend(sorted(path.rglob(ext)))
        elif path.is_file():
            files.append(path)
        else:
            unchecked.append(f"{p}: not found")
    files = [f for f in files if not f.name.startswith("~$")]
    for f in [f for f in files if f.suffix.lower() not in SUPPORTED]:
        files.remove(f)
        unchecked.append(f"{f}: unsupported file type")
    if not files and not unchecked:
        print("error: no .tex, .md, .txt or .docx files given", file=sys.stderr)
        return 2

    files = with_includes(files, unchecked)
    reports = []
    for f in list(files):
        try:
            reports.append(audit_file(f, only))
        except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError) as e:
            files.remove(f)
            unchecked.append(f"{f}: could not be read ({type(e).__name__}: {e})")
    for rep in reports:
        for item in rep["not_checked"]:
            unchecked.append(f"{rep['file']}: {item}")

    by_rule: dict[str, list] = {}
    for rep in reports:
        for h in rep["hits"]:
            by_rule.setdefault(h["rule"], []).append(h)

    print("=" * 78)
    print("AI-TELL AUDIT — raw hits. This is the evidence, not a verdict.")
    print("Act on CLUSTERS, not isolated hits. references/ai-tells.md decides each one,")
    print("and its 'What NOT To Flag' section overrides everything below.")
    print("Tier 0 is the one exception: one hit is conclusive, and it is deleted.")
    print("P0 (an [insert ...] or [CITE: ...] bracket) is filled, not deleted.")
    print("=" * 78)

    p0 = by_rule.get("P0", [])
    if p0:
        print(f"\n!! PLACEHOLDERS: {len(p0)} unresolved placeholder(s). Fill them before "
              f"submission. Do not delete them.")
        for h in p0:
            print(f"   {h['file']}:{h['line']}: {h['match']}")

    t0 = by_rule.get("T0", [])
    if t0:
        print(f"\n!! TIER 0: {len(t0)} near-conclusive artefact(s). Clear these first.")
        for h in t0:
            print(f"   {h['file']}:{h['line']}: {h['match']}")

    for rid, name, _, note in RULES:
        hs = by_rule.get(rid, [])
        print(f"\n[{rid}] Tier {TIER.get(rid, 2)} — {name} — {len(hs)} hit(s)")
        if hs:
            print(f"      {note}")
        for h in hs[:40]:
            print(f"  {h['file']}:{h['line']}: {h['match']}")
            if args.context:
                print(f"      | {h['text']}")
        if len(hs) > 40:
            print(f"  ... and {len(hs) - 40} more (see --json)")

    print("\n" + "=" * 78)
    print("RHYTHM (section 8) — computed, not grepped")
    print("=" * 78)
    for rep in reports:
        r = rep["rhythm"]
        print(f"\n{rep['file']}")
        print(f"  {r['words']} words, {r['sentences']} sentences", end="")
        if "mean" in r:
            print(f", mean {r['mean']} w, range {r['shortest']}-{r['longest']} "
                  f"(spread {r['spread']})")
        else:
            print()
        fs = rhythm_findings(r, args.section)
        for f in fs:
            print(f"  - {f}")
        if not fs:
            print("  - within targets")

    total = sum(len(v) for v in by_rule.values())
    print("\n" + "=" * 78)
    print(f"{total} lexical hit(s) across {len(files)} file(s) in "
          f"{len([k for k in by_rule if by_rule[k]])} categories.")
    print("A hit is a candidate, not a fault. Check each against Protected Terms and")
    print("What NOT To Flag before changing a single word.")
    if by_rule.get("T0"):
        print(f"EXCEPT Tier 0: {len(by_rule['T0'])} artefact(s) above are not candidates.")
    for item in unchecked:
        print(f"not checked: {item}")
    if unchecked:
        print("The result above is NOT a clean result: the parts listed as not checked "
              "were not audited.")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"reports": reports, "not_checked": unchecked}, indent=2), encoding="utf-8")
        print(f"report -> {args.json}")
    return 3 if unchecked else 0


if __name__ == "__main__":
    sys.exit(main())
