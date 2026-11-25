#!/usr/bin/env python3
"""Compare the frozen tokens of a source text and its revision.

The Revision Contract in SKILL.md says the frozen set comes back unchanged: numbers, units,
ranges, citation keys, cross-references, locked terms, and the hedging verb of every claim.
This script lists what a revision removed and what it added in each of eight groups: numbers
(with units and ranges), citations, cross-references, hedges (the claim verbs with their tense,
the modals `may might could can would`, the approximators `approximately about around roughly
nearly almost`, and the bounds `up to`, `at least`, `at most`, `more than`, `less than`, `no more
than`, `no less than`; `about` and `around` count only before a number), locked terms, symbols
(Greek letters, comparison signs, metric names such as `sDA300/50`), abbreviations and standard
names, and proper names (a capitalised word that is not at the start of a sentence or a line, and
any CamelCase or mixed-case name such as `EnergyPlus`). A name first written at the start of a
line is not read unless it is mixed-case.

    python3 check_revision_tokens.py --source old.tex --revised new.tex
    python3 check_revision_tokens.py --source old.docx --revised new.docx --terms .paper/terms.yml
    python3 check_revision_tokens.py --source a.md --revised b.md --strict --json out.json

Reads .tex, .md, .txt, and .docx. Standard library only; --terms needs PyYAML. Both files
should have the same type: a source and a revision of different types are read by the rules of
the source, and the run says so.

Two limits of what it reads. It reads unit symbols, not unit words: `3 mm per hour` rewritten as
`3 mm per day` is not listed. It reads a hyphenated compound only when the term is locked in
`terms.yml` or is one of its built-in protected terms: `state-of-the-art` is read, an ordinary
`open-plan` is not.

What it is: evidence. A difference is not a fault by itself, because a revision may be asked
to change a number. What it is not: a check of meaning. Token conservation cannot see
negation, direction, modality, or meaning. A clean result is not proof the revision is
faithful.

Exit code 0 by default, except 2 when a file cannot be read at all. With --strict, 1 when any
group differs, and 3 when nothing differs but part of a manuscript (an include target, or a
Word equation, text box, header or footer), an empty file, files of two types, or the --terms
file was not read. A --terms file with no `terms:` key counts as not read. `--json` may not name
the source, the revised file or the --terms file (exit 2).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from _manuscript import (abbreviations, comparisons, fold, json_target_problem, numbers,
                         output_is_input, plain_words, ranges_in_words, read_manuscript_checked, read_manuscript_opened,
                         symbols, write_json_file)
from _manuscript import UNIT_RE, _prep
from ai_tell_audit import PROTECTED_RE

GROUPS = ("numbers", "citations", "crossrefs", "hedges", "terms", "symbols", "abbrevs", "names")
LIMIT = ("Token conservation cannot see negation, direction, modality, or meaning. "
         "A clean result is not proof the revision is faithful.")

# The verb ladder in references/sentence-craft.md, plus the modals. Each pattern maps to one
# lemma. The tense is part of the token: `suggest` and `suggests` are one (present), but
# `suggested` and `suggesting` are different tokens, because the tense of a claim verb is part
# of the claim.
HEDGES = [
    (r"\bmay\b", "may"), (r"\bmight\b", "might"), (r"\bcould\b", "could"),
    (r"\bsuggest(?:s|ed|ing)?\b", "suggest"), (r"\bimpl(?:y|ies|ied|ying)\b", "imply"),
    (r"\bindicat(?:e|es|ed|ing)\b", "indicate"), (r"\bshow(?:s|ed|n|ing)?\b", "show"),
    (r"\bdemonstrat(?:e|es|ed|ing)\b", "demonstrate"), (r"\bprov(?:e|es|ed|en|ing)\b", "prove"),
    (r"\bconfirm(?:s|ed|ing)?\b", "confirm"), (r"\bestablish(?:es|ed|ing)?\b", "establish"),
    (r"\bappear(?:s|ed)?\s+to\b", "appear to"), (r"\bseem(?:s|ed)?\s+to\b", "seem to"),
    (r"\btend(?:s|ed)?\s+to\b", "tend to"), (r"\bconsistent\s+with\b", "consistent with"),
    (r"\bassociated\s+with\b", "associated with"),
    (r"\bprovid(?:e|es|ed|ing)\s+evidence\b", "provide evidence"),
    (r"\blikely\b", "likely"), (r"\bpossibly\b", "possibly"), (r"\bpotentially\b", "potentially"),
    (r"\bprobably\b", "probably"), (r"\bperhaps\b", "perhaps"),
    # Modals and approximators. `about` and `around` count only before a number, so the
    # preposition does not flood the output.
    (r"\bcan\b", "can"), (r"\bwould\b", "would"), (r"\bapproximately\b", "approximately"),
    (r"\babout(?=\s+[-+\u00b1]?\.?\d)", "about"), (r"\baround(?=\s+[-+\u00b1]?\.?\d)", "around"),
    (r"\broughly\b", "roughly"), (r"\bnearly\b", "nearly"), (r"\balmost\b", "almost"),
    (r"\bup\s+to\b(?!\s+date\b)", "up to"), (r"\bat\s+least\b", "at least"), (r"\bat\s+most\b", "at most"),
    (r"\b(?:no\s+)?(?:more|less)\s+than\b", None),       # the lemma is the matched words
]
_HEDGES = [(re.compile(p, re.I), lemma) for p, lemma in HEDGES]
_MODALS = {"may", "might", "could", "can", "would", "approximately", "about", "around", "roughly",
           "nearly", "almost", "up to", "at least", "at most", "more than", "less than",
           "no more than", "no less than", "consistent with", "associated with", "likely", "possibly",
           "potentially", "probably", "perhaps"}


def _tense(word: str) -> str:
    word = word.casefold()
    if word.endswith("ing"):
        return "ing"
    if word.endswith("ed"):
        return "past"
    if word.endswith(("wn", "en")):
        return "participle"
    return ""


_OPT = r"(?:\s*(?:\([^)]*\)|\[[^\]]*\]))*"          # biblatex notes: (pre)(post)[pre][post]
_CITE_ARG = _OPT + r"\s*\{([^}]*)\}"
# `\cites{a}{b}` and `\parencites[pre][post]{a}[pre]{b}` carry one braced group per work; other
# commands take one group, and a second group after them is text.
# Commands that carry `cite` in the name and no citation key.
_NOT_CITE = r"(?!(?:setcitestyle|citestyle|citetext|citeindextrue|citeindexfalse|bibcite|citation)\b)"
_TEX_CITE = re.compile(r"\\" + _NOT_CITE + r"[A-Za-z]*cite[A-Za-z]*\*?" + _CITE_ARG)
_TEX_MULTICITE = re.compile(r"\\[A-Za-z]*cites\*?((?:" + _OPT + r"\s*\{[^}]*\})+)")
_BRACED = re.compile(r"\{([^}]*)\}")
_MD_CITE = re.compile(r"\[[^\]]*@[^\]]*\]")
_NUM_CITE = re.compile(r"\[(\d+(?:\s*[-,\u2013]\s*\d+)*)\]")
_PAREN = re.compile(r"\(([^()]*\b(?:19|20)\d{2}[a-z]?[^()]*)\)")
_AUTHOR_YEAR = re.compile(r"[A-Z][^;()]*?,?\s+(?:19|20)\d{2}[a-z]?$")
_NARRATIVE = re.compile(r"\b([A-Z][A-Za-z-]+(?:\s+et\s+al\.|\s+and\s+[A-Z][A-Za-z-]+)?)"
                        r"\s+\(((?:19|20)\d{2}[a-z]?)\)")
_TEX_REF = re.compile(r"\\(?:ref|eqref|cref|Cref|autoref|pageref|nameref|vref)\*?\s*\{([^}]*)\}")
# A target is a number (`3`, `4.2`, `3a`) or a capital letter that may carry a number (`B`, `S1`, `A2`).
_TARGET_CORE = r"(?:\d+(?:\.\d+)*(?:[A-Za-z](?![A-Za-z]))?|[A-Z](?:\.?\d+(?:\.\d+)*)?(?![A-Za-z]))"
_PNUM = r"\(?" + _TARGET_CORE + r"\)?"
# After a comma the next number is a figure number only when it is short and carries no unit:
# `Fig. 2, 412 lx` is a pointer followed by a measurement, not a list.
_PSHORT = (r"\(?\d{1,2}(?:\.\d+)*[a-z]?\)?(?![\d%]|\s?(?:" + UNIT_RE + r")(?![A-Za-z]))")
_SEP = r"(?:,\s*(?:and\s+)?{s}|(?:and|&|to|through|[-\u2013])\s*{n})"
# A list of targets is read only after a plural pointer word (`Figs. 2, 3 and 5`). After a
# singular one a single target follows, with a range written without spaces (`Fig. 3-5`), so
# `Fig. 2, and 5 sensors` is one pointer and a count.
_POINTER = re.compile(
    r"(?:\b|(?=\\S(?![A-Za-z])))(?:(?:Figs|Figures|Tabs|Tables|Secs|Sections|Eqs|Equations)\.?\s*(?P<pl>" + _PNUM
    + r"(?:\s*" + _SEP.format(s=_PSHORT, n=_PNUM) + r")*)"
    r"|(?P<name>Fig|Figure|Tab|Table|Sec|Section|Eq|Equation|Appendix|\\S(?![A-Za-z]))\.?\s*(?P<sg>" + _PNUM
    + r"(?:[-\u2013]" + _PNUM + r")?))")
_POINTER_WORD = re.compile(r"\b(Figs?|Figures?|Tabs?|Tables?|Secs?|Sections?|Eqs?|Equations?|Appendix)")
_PLIST = re.compile(r"(,\s*(?:and\s+)?|and\s+|&\s*|to\s+|through\s+|[-\u2013]\s*)?"
                    r"\(?(" + _TARGET_CORE + r")\)?")
_POINTER_NAME = {"fig": "Fig.", "tab": "Table", "sec": "Section", "eq": "Eq.", "eqs": "Eq.",
                 "equ": "Eq.", "app": "Appendix"}


def _numeric_members(body: str) -> list[str]:
    """The members of a numeric bracket, one token each: `[12, 13]` and `[13,12]` agree, and
    `[12-14]` is `[12]`, `[13]`, `[14]`."""
    out: list[str] = []
    for part in re.split(r"\s*,\s*", body):
        r = re.fullmatch(r"(\d+)\s*[-\u2013]\s*(\d+)", part)
        if r and 0 <= int(r.group(2)) - int(r.group(1)) <= 200:
            out += [f"[{n}]" for n in range(int(r.group(1)), int(r.group(2)) + 1)]
        else:
            out.append("[" + re.sub(r"\s+", "", part) + "]")
    return out


def _citations(text: str, suffix: str) -> list[str]:
    out: list[str] = []
    if suffix == ".tex":
        for m in _TEX_CITE.finditer(text):
            groups = [m.group(1)]
            multi = _TEX_MULTICITE.match(text, m.start())
            if multi:
                groups = _BRACED.findall(multi.group(1))
            for g in groups:
                out += [k.strip() for k in g.split(",") if k.strip()]
        return out
    for m in _MD_CITE.finditer(text):
        out += re.findall(r"@([\w:.-]*\w)", m.group(0))
    for m in _NUM_CITE.finditer(text):
        out += _numeric_members(m.group(1))
    for m in _PAREN.finditer(text):
        for part in m.group(1).split(";"):
            part = re.sub(r"^\s*(?:e\.g\.,?|see|cf\.)\s+", "", part.strip())
            if _AUTHOR_YEAR.match(part):
                out.append(part)
    out += [f"{m.group(1)} ({m.group(2)})" for m in _NARRATIVE.finditer(text)]
    return out


def _crossrefs(text: str) -> list[str]:
    out: list[str] = []
    for m in _TEX_REF.finditer(text):
        out += [k.strip() for k in m.group(1).split(",") if k.strip()]
    for m in _POINTER.finditer(text):
        word = _POINTER_WORD.match(m.group(0))
        name = _POINTER_NAME[word.group(1)[:3].lower()] if word else "Section"      # `\S4.2`
        prev = None
        for item in _PLIST.finditer(m.group("pl") or m.group("sg")):
            sep, num = (item.group(1) or "").strip(), item.group(2)
            if prev is not None and sep and sep[0] in "-\u2013t":     # a range: `3-5`, `3 to 5`
                out.append(f"{name} {prev}{sep[0] if sep[0] != 't' else ' to '}{num}")
            else:
                out.append(f"{name} {num}")
            prev = num
    return out


_FILLER_CAN = re.compile(r"\bas\s+can\s+be\s+(?:\w+ly\s+)?seen\b", re.I)


def _hedges(text: str) -> list[str]:
    out = []
    text = _FILLER_CAN.sub("as seen", text)           # a filler phrase, not a modal
    for rx, lemma in _HEDGES:
        for m in rx.finditer(text):
            if lemma is None:
                out.append(" ".join(m.group(0).lower().split()))
                continue
            tense = "" if lemma in _MODALS else _tense(m.group(0).split()[0])
            out.append(f"{lemma} ({tense})" if tense else lemma)
    return out


_CMD_BREAK = re.compile(r"\\(?:item|section|subsection|subsubsection|paragraph|chapter|caption|"
                        r"title|begin|end|par)\*?")
_CMD = re.compile(r"\\[A-Za-z]+\*?")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_CLOSERS = "'\")]"


def _at_sentence_start(text: str, pos: int) -> bool:
    """True when the word at `pos` opens a sentence, a heading, a braced argument or a
    paragraph. A single newline does not: a hard-wrapped file breaks lines anywhere."""
    j = pos
    while j > 0 and text[j - 1] in " \t\r\n":
        j -= 1
    if j == 0:
        return True
    gap = text[j:pos]
    prev = text[j - 1]
    if gap.count("\n") >= 2 or prev == "{":
        return True
    if not gap:
        return False
    k = j - 1
    while k >= 0 and text[k] in _CLOSERS:
        k -= 1
    if k >= 0 and text[k] in ".!?:":
        return True
    if prev == "#":                                   # a Markdown heading marker
        ls = text.rfind("\n", 0, j) + 1
        return not text[ls:j].strip("# \t")
    return False


def _scan_names(text: str) -> tuple[list[str], list[str], set[str]]:
    """One pass over the text, in linear time: the mixed-case words, every capitalised word
    (a word in capitals is listed in capitalised form, so that a change of letter case is not a
    change of name), and the capitalised words that stand in mid-sentence position."""
    text = _CMD.sub("", _CMD_BREAK.sub(" . ", _prep(text)))
    mixed: list[str] = []
    caps: list[str] = []
    mid: set[str] = set()
    for m in _WORD.finditer(text):
        w = m.group(0)
        if len(w) < 2 or w.isdigit():
            continue
        if w.isupper():
            caps.append(w.capitalize())
        elif re.search(r"[a-z][A-Z]", w) or (w[0].islower() and re.search(r"[A-Z]", w)):
            mixed.append(w)
        elif w[0].isupper() and w[1:].islower():
            caps.append(w)
            if not _at_sentence_start(text, m.start()):
                mid.add(w)
    return mixed, caps, mid


def _names(text: str, known: set[str] | None = None) -> list[str]:
    """Proper names: a capitalised word that is written capitalised in mid-sentence position
    (every occurrence of it counts, wherever it stands, so moving a name to the start of a
    sentence is not a change), and any CamelCase or mixed-case name (`EnergyPlus`, `iPhone`).
    A word in capitals is an abbreviation and belongs to the abbrevs group. `known` is the set
    of such words found in the other text as well."""
    mixed, caps, mid = _scan_names(text)
    known = mid if known is None else known | mid
    return mixed + [w for w in caps if w in known]


def _terms(text: str, terms: list[str]) -> list[str]:
    out = [m.group(0).casefold() for m in PROTECTED_RE.finditer(text)]
    for term in terms:
        body = r"\s+".join(re.escape(w) for w in fold(term).split())
        if not body:
            continue
        rx = re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.I)
        out += [term] * len(rx.findall(text))
    return out


def _tokens(text: str, suffix: str, terms: list[str], words: set,
            name_words: set | None = None) -> dict[str, Counter]:
    text = fold(text, keep_dashes=True, tex=suffix == ".tex")
    return {
        # `[1, 2]` and `[1,2]` are one citation, not numbers; the citations group holds them.
        "numbers": Counter(numbers(_NUM_CITE.sub(" ", text)) + ranges_in_words(text)),
        "citations": Counter(_citations(text, suffix)),
        "crossrefs": Counter(_crossrefs(text)),
        "hedges": Counter(_hedges(text)),
        "terms": Counter(_terms(text, terms)),
        "symbols": Counter(symbols(text) + comparisons(text)),
        "abbrevs": Counter(abbreviations(text, words)),
        "names": Counter(_names(text, name_words)),
    }


def _fold_for_names(text: str, suffix: str) -> str:
    return fold(text, keep_dashes=True, tex=suffix == ".tex")


def compare(source: str, revised: str, suffix: str,
            terms: list[str]) -> dict[str, dict[str, list[str]]]:
    """Return, per group, the tokens the revision removed and the tokens it added.

    Counts matter: a number quoted twice and kept once is one removal. Order does not:
    moving a sentence changes nothing.
    """
    suffix = suffix.lower()
    # A word in capitals that appears in ordinary case in either text (`RESULTS`, `Results`) is a
    # change of letter case, not an abbreviation.
    words = plain_words(source) | plain_words(revised)
    # A capitalised word that stands mid-sentence in either text is a name in both.
    name_words = (_scan_names(_fold_for_names(source, suffix))[2]
                  | _scan_names(_fold_for_names(revised, suffix))[2])
    a = _tokens(source, suffix, terms, words, name_words)
    b = _tokens(revised, suffix, terms, words, name_words)
    return {g: {"removed": sorted((a[g] - b[g]).elements()),
                "added": sorted((b[g] - a[g]).elements())} for g in GROUPS}


def load_terms(path: Path) -> tuple[list[str], str | None]:
    """Locked terms from a `.paper/terms.yml`: each canonical name and each abbreviation."""
    try:
        import yaml
    except ImportError:
        return [], "terms.yml: not checked: install pyyaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        return [], f"terms.yml: not checked: {e}"
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return [], (f"terms.yml: not checked: the top level is a {type(data).__name__}, "
                    "expected a mapping with a `terms:` list")
    if "terms" not in data:
        return [], ("terms.yml: not checked: no `terms:` key (found "
                    f"{', '.join(map(str, data)) or 'an empty file'})")
    rows = data.get("terms")
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        return [], "terms.yml: not checked: `terms:` is not a list"
    out: list[str] = []
    for row in rows:
        if isinstance(row, dict):
            out += [str(row[k]) for k in ("canonical", "abbrev") if row.get(k)]
    return out, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="the text before the revision")
    ap.add_argument("--revised", required=True, help="the text after the revision")
    ap.add_argument("--terms", help="a .paper/terms.yml whose locked terms are also compared")
    ap.add_argument("--json", help="write the full result to this file")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any group differs")
    args = ap.parse_args()

    if args.json:
        problem = json_target_problem(args.json)
        if problem:
            print(problem, file=sys.stderr)
            return 2

    if args.json:
        inputs = {"the source file": args.source, "the revised file": args.revised,
                  "the --terms file": args.terms}
        for label, name in (("source", args.source), ("revised", args.revised)):
            if Path(name).suffix.lower() == ".tex" and Path(name).is_file():
                try:
                    for opened in read_manuscript_opened(Path(name))[2]:
                        inputs[f"the file {opened.name}, which the {label} file includes"] = opened
                except OSError:
                    pass                      # the run reports an unreadable file itself
        clash = output_is_input(args.json, inputs)
        if clash:
            print(f"--json {args.json}: this is {clash}, and the script would overwrite it. "
                  f"Nothing was checked.", file=sys.stderr)
            return 2

    texts, notes, unread = [], [], 0
    for label, name in (("source", args.source), ("revised", args.revised)):
        path = Path(name)
        try:
            text, missing, skipped = read_manuscript_checked(path)
        except Exception as e:                                   # noqa: BLE001
            print(f"cannot read {label} file {path}: {e}", file=sys.stderr)
            return 2
        texts.append(text)
        if not text.strip():
            notes.append(f"{label}: {path} is empty, not checked")
            unread += 1
        notes += [f"{label}: \\input target not found, not checked: {m}" for m in missing]
        notes += [f"{label}: not checked: {item}" for item in skipped]
        unread += len(missing) + len(skipped)

    suffixes = (Path(args.source).suffix.lower(), Path(args.revised).suffix.lower())
    if suffixes[0] != suffixes[1]:
        notes.append(f"source and revised have different file types ({suffixes[0] or 'none'} and "
                     f"{suffixes[1] or 'none'}); both were read as {suffixes[0] or 'plain text'}, "
                     "so citations may not compare, not checked")
        unread += 1

    terms: list[str] = []
    terms_unchecked = False
    if args.terms:
        terms, note = load_terms(Path(args.terms))
        if note:
            notes.append(note)
            terms_unchecked = True

    result = compare(texts[0], texts[1], Path(args.source).suffix, terms)
    differs = any(v["removed"] or v["added"] for v in result.values())

    print(f"source:  {args.source}\nrevised: {args.revised}\n")
    for g in GROUPS:
        r, a = result[g]["removed"], result[g]["added"]
        print(f"{g:<10} removed {len(r):>3}   added {len(a):>3}")
        for t in r:
            print(f"    - {t}")
        for t in a:
            print(f"    + {t}")
    for n in notes:
        print(f"\nNOTE  {n}")
    if unread or terms_unchecked:
        parts = []
        if unread:
            parts.append(f"{unread} part(s) of the manuscripts not checked (see NOTE)")
        if terms_unchecked:
            parts.append("terms file not checked")
        verdict = (("Differences found" if differs else "No token differences")
                   + f" in the parts that were checked; {'; '.join(parts)}.")
    else:
        verdict = "Differences found." if differs else "No token differences."
    print(f"\n{verdict} {LIMIT}")

    if args.json:
        err = write_json_file(args.json, json.dumps({"result": result, "notes": notes}, indent=2))
        if err:
            print(err, file=sys.stderr)
            return 2
    if not args.strict:
        return 0
    return 1 if differs else 3 if unread or terms_unchecked else 0


if __name__ == "__main__":
    sys.exit(main())
