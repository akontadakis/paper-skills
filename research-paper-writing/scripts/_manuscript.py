"""Shared manuscript reader for the check scripts.

Not a command. `check_revision_tokens.py` and `check_ledger.py` import it so that both read a
manuscript, fold its characters, find its sections, and extract its numbers in one way.

Four functions:
    read_manuscript(path)  -> (text, missing_includes)
    fold(text)             -> text with Unicode and dash forms normalised
    split_sections(text, suffix) -> {"abstract": ..., "results": ..., ...}
    numbers(text)          -> canonical number tokens, with a unit where one is attached

Standard library only. It never writes a file.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

from ai_tell_audit import read_docx_checked

MAX_INCLUDE_DEPTH = 10

# --------------------------------------------------------------------------- --json output

def json_target_problem(name: str) -> str | None:
    """Why `--json name` cannot be written, or None. Checked before a run starts, so that a
    long check is not lost to a path that was never going to work."""
    path = Path(name)
    if path.is_dir():
        return f"--json {name}: that is a folder, not a file"
    parent = path.parent
    if not parent.is_dir():
        return f"--json {name}: the folder {parent} does not exist"
    if not os.access(parent, os.W_OK | os.X_OK):
        return f"--json {name}: the folder {parent} is not writable"
    if path.exists() and not os.access(path, os.W_OK):
        return f"--json {name}: the file is not writable"
    return None


def write_json_file(name: str, payload: str) -> str | None:
    """Write `payload` to `name`. Returns an error message, or None when it was written."""
    try:
        Path(name).write_text(payload, encoding="utf-8")
    except OSError as e:
        return f"--json {name}: could not write the file ({e.strerror or e})"
    return None


# --------------------------------------------------------------------------- reading

_INCLUDE = re.compile(
    r"\\(?P<cmd2>(?:sub)?import|(?:sub)?includefrom)\*?\s*\{(?P<dir>[^}]*)\}\s*\{(?P<file>[^}]+)\}"
    r"|\\(?P<cmd1>input|include|subfile)\s*(?:\{(?P<b1>[^}]+)\}|[ \t]+(?P<b2>[^\s{}%\\]+))")
_TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.M)


def resolve_include(m: re.Match, root_dir: Path, cur_dir: Path) -> tuple:
    """(target or None, name as written) for one `_INCLUDE` match.

    TeX resolves `\\input` and `\\include` against the folder of the root file, so that is tried
    first, with the folder of the including file as a fall-back. `\\subfile`, `\\subimport` and
    `\\subincludefrom` are resolved against the including file's folder. `\\import` and
    `\\includefrom` take their directory from the root folder. The two arguments of the import
    family are joined as a path, so `\\subimport{sec}{b}` finds `sec/b.tex`.
    """
    if m.group("cmd2"):
        name = str(Path(m.group("dir").strip()) / m.group("file").strip())
        bases = [cur_dir if m.group("cmd2").startswith("sub") else root_dir]
    else:
        name = (m.group("b1") or m.group("b2")).strip()
        bases = [cur_dir] if m.group("cmd1") == "subfile" else [root_dir, cur_dir]
    for base in bases:
        target = base / name
        for cand in ((target.with_suffix(".tex"),) if not target.suffix
                     else (target, target.with_name(target.name + ".tex"))):
            if cand.is_file():
                return cand, name
    return None, name


def _read_tex(path: Path, depth: int, missing: list[str], root_dir: Path | None = None) -> str:
    root_dir = path.parent if root_dir is None else root_dir
    text = _TEX_COMMENT.sub("", path.read_text(encoding="utf-8", errors="replace"))
    if depth >= MAX_INCLUDE_DEPTH:
        # A file that includes itself, or a chain deeper than any real project. What lies
        # below this point was not read, and the caller must be told.
        if _INCLUDE.search(text):
            missing.append(f"{path.name} (include depth limit reached; deeper files not read)")
        return _INCLUDE.sub("", text)

    def expand(m: re.Match) -> str:
        target, name = resolve_include(m, root_dir, path.parent)
        if target is None:
            missing.append(name)
            return ""
        return _read_tex(target, depth + 1, missing, root_dir)

    return _INCLUDE.sub(expand, text)


def read_manuscript_checked(path: Path) -> tuple[str, list[str], list[str]]:
    """Like `read_manuscript`, plus what the reader did not read. For a `.docx` that is the
    parts `ai_tell_audit.read_docx_checked` names (equations, text boxes, headers and
    footers); the third item is empty for other formats."""
    path = Path(path)
    if path.suffix.lower() == ".docx":
        text, skipped = read_docx_checked(path)
        return text, [], list(skipped)
    text, missing = read_manuscript(path)
    return text, missing, []


def read_manuscript(path: Path) -> tuple[str, list[str]]:
    """Return the manuscript text and the include targets that were not found.

    `.docx` paragraphs include table cells. `.tex` comments are removed and `\\input`,
    `\\include`, `\\subfile`, and the two-argument `\\import`, `\\subimport`,
    `\\includefrom`, and `\\subincludefrom` are followed from the root file, with or without braces.
    A missing include is reported by the name written in the source, and a chain that hits
    the depth limit is reported too; the caller must treat that part of the manuscript as
    not checked.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx_checked(path)[0], []
    if suffix == ".tex":
        missing: list[str] = []
        return _read_tex(path, 0, missing), missing
    return path.read_text(encoding="utf-8", errors="replace"), []


# --------------------------------------------------------------------------- folding

_DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2212"), "-")
# With keep_dashes the en dash and the em dash stay distinct from the hyphen, because the dash
# inside a range is part of the frozen set. Figure dash and minus sign fold to the usual forms.
_KEEP = {ord("\u2010"): "-", ord("\u2011"): "-", ord("\u2212"): "-",
         ord("\u2012"): "\u2013"}
_TEX_SPACES = re.compile(r"\\[,;:!]|\\ |~")
_TEX_RANGE = re.compile(r"(?<=\d)\s?-{2,3}\s?(?=\d)")


def fold(text: str, keep_dashes: bool = False, tex: bool = False) -> str:
    """Normalise before any splitting, so a respelled character cannot hide a change.

    NFKC maps full-width digits to ASCII and no-break and thin spaces to a plain space.
    Hyphen, en dash, em dash, and the minus sign all become `-`, and so does the LaTeX
    `--` between two numbers. LaTeX spacing commands and `~` become one space.

    With `keep_dashes=True` the en dash and the em dash stay as they are, so a changed dash
    can be reported. With `tex=True` as well, LaTeX `--` becomes the en dash and `---` the em
    dash, so a `.tex` source and a typeset revision compare equal.
    """
    text = unicodedata.normalize("NFKC", text)
    if not keep_dashes:
        return _TEX_SPACES.sub(" ", _TEX_RANGE.sub("-", text.translate(_DASHES)))
    text = text.translate(_KEEP)
    if tex:
        text = text.replace("---", "\u2014").replace("--", "\u2013")
    return _TEX_SPACES.sub(" ", text)


# --------------------------------------------------------------------------- sections

SECTION_KEYS = ("abstract", "introduction", "methods", "results", "discussion", "conclusion",
                "other")


def _section_key(title: str) -> str:
    t = re.sub(r"^\s*\d+(?:\.\d+)*\.?\s+", "", title).strip().casefold()
    if t.startswith("abstract") or t == "summary":
        return "abstract"
    if "introduction" in t:
        return "introduction"
    if "method" in t or "material" in t or "setup" in t:
        return "methods"
    if "result" in t or "experiment" in t or "evaluation" in t or "finding" in t:
        return "results"
    if "discussion" in t or "limitation" in t:
        return "discussion"
    if "conclusion" in t or "concluding" in t:
        return "conclusion"
    return "other"


_PLAIN_NAMES = ("abstract", "summary", "introduction", "background", "related work",
                "method", "methods", "methodology", "materials and methods",
                "experimental setup", "experiments", "results", "results and discussion",
                "evaluation", "discussion", "limitations", "conclusion", "conclusions",
                "concluding remarks", "references", "acknowledgements", "acknowledgments",
                "appendix")


def _headings(text: str, suffix: str) -> list[tuple[int, int, str]]:
    """(heading start, body start, title) for each top-level heading, in order."""
    found: list[tuple[int, int, str]] = []
    if suffix == ".tex":
        for m in re.finditer(r"\\begin\{abstract\}", text):
            found.append((m.start(), m.end(), "abstract"))
        for m in re.finditer(r"\\end\{abstract\}", text):
            found.append((m.start(), m.end(), "__after_abstract__"))
        for m in re.finditer(r"\\section\*?\s*(?:\[[^\]]*\])?\{([^}]*)\}", text):
            found.append((m.start(), m.end(), m.group(1)))
    elif suffix == ".md":
        for m in re.finditer(r"^#{1,2}[ \t]+(.+?)[ \t]*#*[ \t]*$", text, re.M):
            found.append((m.start(), m.end(), m.group(1)))
    else:
        for m in re.finditer(r"^[ \t]*((?:\d+(?:\.\d+)*\.?[ \t]+)?[A-Za-z][A-Za-z &-]*)[ \t]*$",
                             text, re.M):
            bare = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", m.group(1)).strip().casefold()
            if bare in _PLAIN_NAMES:
                found.append((m.start(), m.end(), m.group(1)))
    return sorted(found)


def split_sections(text: str, suffix: str) -> dict[str, str]:
    """Map canonical section names to their text. A section that is absent has no key.

    Recognised: `\\begin{abstract}` and `\\section{}` in LaTeX, level one and two `#`
    headings in Markdown, and a short plain heading line, optionally numbered, elsewhere.
    Subsections stay with their parent. `Experiments` counts as results and `Materials and
    Methods` as methods. Any other heading, and text before the first heading, is `other`.
    """
    heads = _headings(text, suffix.lower())
    out: dict[str, list[str]] = {}

    def add(key: str, body: str) -> None:
        if body.strip():
            out.setdefault(key, []).append(body)

    if not heads:
        add("other", text)
    else:
        add("other", text[:heads[0][0]])
        for i, (_, body_start, title) in enumerate(heads):
            end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
            key = "other" if title == "__after_abstract__" else _section_key(title)
            add(key, text[body_start:end])
    return {k: "\n".join(v) for k, v in out.items()}


# --------------------------------------------------------------------------- numbers

_SI_UNITS = {
    "lux": "lx", "candela": "cd", "lumen": "lm", "metre": "m", "meter": "m", "second": "s",
    "minute": "min", "hour": "h", "day": "d", "kelvin": "K", "watt": "W", "joule": "J",
    "pascal": "Pa", "hertz": "Hz", "percent": "%", "degreeCelsius": "\u00b0C",
    "celsius": "\u00b0C", "degree": "\u00b0", "kilo": "k", "mega": "M", "giga": "G",
    "milli": "m", "centi": "c", "micro": "\u00b5", "nano": "n", "per": "/",
    "squared": "2", "cubed": "3", "square": "", "gram": "g", "litre": "L", "liter": "L",
    "volt": "V", "ampere": "A", "decibel": "dB",
}

# A unit is an SI prefix plus a base unit, with an optional exponent, optionally joined to
# another by `/` or a middle dot: `mV`, `kg`, `kWh/m2`, `mol/L`. A word unit such as `years` is
# listed by hand. Longest first, so `kWh/m2` wins over `kWh`, `k`, and `m`.
_PREFIXES = ("", "k", "M", "G", "T", "m", "\u03bc", "\u00b5", "n", "p", "c", "d", "h")
_BASES = ("m", "g", "s", "A", "V", "W", "J", "N", "Pa", "Hz", "K", "L", "lx", "lm", "cd", "mol",
          "Wh", "\u03a9", "\u2126", "eV", "bar", "Bq", "Gy", "Sv")
_WORD_UNITS = ("lux", "ppm", "ppb", "dB", "min", "h", "\u00b0C", "\u00b0", "%", "years", "year",
               "days", "day", "hours", "hour", "ach", "ACH", "dBA", "dBC", "deg", "sr")
_ATOMS = sorted({p + b for p in _PREFIXES for b in _BASES} | set(_WORD_UNITS),
                key=len, reverse=True)
_ATOM_BASE = "(?:" + "|".join(re.escape(u) for u in _ATOMS) + ")"
# An explicit exponent: `m^2`, `m^-2`, `m^{-2}`, `m\u00b2`, `m\u207b\u00b2`.
_EXPLICIT_EXP = r"(?:\^\{?-?\d\}?|\u207b?[\u00b2\u00b3\u00b9])"
_ATOM = _ATOM_BASE + r"(?:" + _EXPLICIT_EXP + r"|\d(?!\d))?"
_ATOM_X = _ATOM_BASE + _EXPLICIT_EXP
_GROUP = r"\(" + _ATOM + r"(?:[\u00b7* ]+" + _ATOM + r")*\)"
# Atoms are joined by `/` or a middle dot, or by a space when the second one carries an explicit
# exponent (`cd m^-2`, `m s^-1`); a bare `m s` stays a unit and a word.
UNIT_RE = _UNIT_RE = (r"W/m2K|W/mK|W/m\u00b2K|" + _ATOM + r"(?:[/\u00b7*](?:" + _ATOM + "|" + _GROUP
                      + ")| " + _ATOM_X + ")*")
_EXP = r"(?:[eE][+-]?\d+)?"
# Five written forms: `10 000` (space-grouped thousands), `612,418` (comma-grouped), `1,5` (a
# decimal comma: one or two digits, or four or more, after the comma), a plain integer or
# decimal, and a decimal with no leading zero (`.05`). Each may carry an exponent.
_NUM = (rf"\d{{1,3}}(?: \d{{3}})+(?!\d)(?:\.\d+)?|\d+(?:,\d{{3}})+(?!\d)(?:\.\d+)?{_EXP}"
        rf"|\d+,(?:\d{{1,2}}|\d{{4,}})(?!\d){_EXP}"
        rf"|\d+(?:\.\d+)?{_EXP}|\.\d+{_EXP}")
# A unit that came from siunitx is carried between these marks so a compound unit such as
# `W/m2` survives whole; a unit typed in the text is matched against the list above.
_SI_OPEN, _SI_CLOSE = "\u27e6", "\u27e7"
_UNIT_TAIL = (rf"(?:\s?(?:{_SI_OPEN}(?P<siunit>[^{_SI_CLOSE}]*){_SI_CLOSE}"
              rf"|\\?(?P<unit>{_UNIT_RE})(?![A-Za-z])))?")
_TOKEN = re.compile(
    rf"(?P<sign>(?<![A-Za-z0-9)\]])-)?(?<![A-Za-z0-9_.,])(?P<a>{_NUM})"
    rf"(?:\s?(?P<dash>[-\u2013])\s?(?P<b>{_NUM}))?{_UNIT_TAIL}")

_SKIP_MACROS = re.compile(
    r"\\(?:cite\w*|ref|eqref|cref|Cref|autoref|pageref|nameref|label|bibitem|url|href"
    r"|includegraphics|vspace|hspace|setlength|usepackage|documentclass|bibliographystyle"
    r"|bibliography)\*?\s*(?:\[[^\]]*\])*\s*\{[^}]*\}")
_TARGET = r"\(?\d+(?:\.\d+)*[a-z]?\)?"
# A list of targets is read only after a plural pointer word (`Figs. 3 and 4`). After a singular
# one only a range written without spaces (`Fig. 3-5`) follows, so `Fig. 2, and 5 sensors` and
# `Eq. (3) and 4` keep the count that follows the pointer.
_FLOAT_REF = re.compile(
    r"\b(?:Figs|Figures|Tabs|Tables|Secs|Sections|Eqs|Equations|Chapters|Appendices|Refs|Steps|"
    r"Cases|Rules)\.?\s*" + _TARGET + r"(?:\s*(?:and|to|-|\u2013)\s*" + _TARGET + r")*"
    r"|\b(?:Fig|Figure|Tab|Table|Sec|Section|Eq|Equation|Chapter|Appendix|Ref|Step|Case|Rule)"
    r"\.?\s*" + _TARGET + r"(?:[-\u2013]" + _TARGET + r")?")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SCI = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:\u00d7|x|\\times|\\cdot)\s*10\s*\^\s*\{?\s*(-?\d+)\s*\}?")


def _si_unit(arg: str) -> str:
    parts = re.findall(r"\\([A-Za-z]+)|([^\\\s{}]+)", arg)
    return "".join(_SI_UNITS.get(m, m) if m else lit for m, lit in parts)


def _expand_siunitx(text: str) -> str:
    text = re.sub(r"\\(?:SIrange|qtyrange)\s*(?:\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}",
                  lambda m: f"{m.group(1)}-{m.group(2)} {_SI_OPEN}{_si_unit(m.group(3))}"
                            f"{_SI_CLOSE}", text)
    text = re.sub(r"\\(?:SI|qty)\s*(?:\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}",
                  lambda m: f"{m.group(1)} {_SI_OPEN}{_si_unit(m.group(2))}{_SI_CLOSE}", text)
    return re.sub(r"\\num\s*(?:\[[^\]]*\])?\{([^}]*)\}", r"\1", text)


def _canon(number: str) -> str:
    """One spelling per value: lower-case `e`, no `+` in the exponent, a leading zero, and a
    decimal point for a decimal comma. A thousands separator (`1,200`) is kept as written."""
    number = number.replace("E", "e").replace("e+", "e")
    if "," in number and not re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:e-?\d+)?", number):
        number = number.replace(",", ".")
    return "0" + number if number.startswith(".") else number


_U_PART = re.compile(r"([A-Za-z\u00b0%\u00b5\u03bc\u03a9\u2126]+)"
                     r"(?:\^\{?(-?\d)\}?|(\u207b?)([\u00b2\u00b3\u00b9])|(\d))?|(/)|[()\u00b7*\s]")
_SUPER = {"\u00b2": 2, "\u00b3": 3, "\u00b9": 1}


def _canon_unit(unit: str) -> str:
    """One spelling per unit: `cd m^-2`, `cd/m\u00b2` and `cd/m2` all give `cd/m2`.

    Everything after a `/` is a denominator, so `W/m2K` and `W/(m2 K)` agree. A unit with no
    exponent, slash, or space comes back as written.
    """
    if unit == "lux":
        return "lx"
    if not re.search(r"[/\s\u00b7*(^\u00b2\u00b3\d]", unit):
        return unit
    unit = re.sub(r"^W/m([2\u00b2]?)K$", lambda m: f"W/(m{m.group(1)} K)", unit)
    unit = re.sub(r"^W/mK$", "W/(m K)", unit)
    parts = list(_U_PART.finditer(unit))
    if "".join(m.group(0) for m in parts) != unit:
        return unit                                 # something unparsed: keep what was written
    pos: list[tuple[str, int]] = []
    neg: list[tuple[str, int]] = []
    slash = False
    for m in parts:
        if m.group(6):
            slash = True
        elif m.group(1):
            if m.group(2):
                e = int(m.group(2))
            elif m.group(4):
                e = -_SUPER[m.group(4)] if m.group(3) else _SUPER[m.group(4)]
            else:
                e = int(m.group(5)) if m.group(5) else 1
            e = -e if slash else e
            (pos if e > 0 else neg).append((m.group(1), abs(e)))

    def show(items: list[tuple[str, int]]) -> str:
        return "\u00b7".join(a + (str(e) if e != 1 else "") for a, e in sorted(items))

    out = show(pos) or ("1" if neg else "")
    if len(neg) == 1:
        out += "/" + show(neg)
    elif neg:
        out += "/(" + show(neg) + ")"
    return out


_PM = re.compile(r"\\pm(?![A-Za-z])")
_DIGIT_COMMAS = re.compile(r"(?<!\d)\d+(?:,\d+)+")
_COMMA_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+|\d+,(?:\d{1,2}|\d{4,})")


def _split_digit_commas(text: str) -> str:
    """Put a space after the commas of an unspaced list of numbers (`1,2,3`), so each member is
    read. A thousands separator (`1,200`) and a decimal comma (`1,5`) are left alone."""
    return _DIGIT_COMMAS.sub(
        lambda m: m.group(0) if _COMMA_NUMBER.fullmatch(m.group(0)) else m.group(0).replace(",", ", "),
        text)


def numbers(text: str) -> list[str]:
    """Canonical number tokens in reading order, each with its unit where one is attached.

    `400-700 nm` is one token, so a range broken into two values shows as a change.
    `\\SI{4.2}{\\lux}` and `4.2 lux` both give `4.2 lx`; a percentage gives `62 %`;
    `1.2 x 10^{-3}`, `1.2E-3`, and `1.2e-3` all give `1.2e-3`, and `.05` gives `0.05`. A
    thousands separator is kept as written, so `612,418`, `612 418`, and `612418` differ. A
    decimal comma is read as a decimal point: `1,5 m` gives `1.5 m` (one or two digits after the
    comma, or four or more; exactly three is a thousands separator). `\\pm` and `\u00b1` agree and
    are never a unit, and `cd m^-2`, `cd/m\u00b2`, and `cd/m2` all give `cd/m2`.
    Numbers inside `\\cite`, `\\ref`, and `\\label`, numbers that name a figure, table,
    section, or equation, and ISO dates are skipped. A list of targets is skipped only after a
    plural pointer word (`Figs. 3 and 4`).
    Call `fold()` first on text that may carry Unicode dashes or spaces.
    """
    text = _PM.sub("\u00b1", text)
    text = _SKIP_MACROS.sub(" ", text)
    text = _expand_siunitx(text)
    text = _FLOAT_REF.sub(" ", text)
    text = _ISO_DATE.sub(" ", text)
    text = _split_digit_commas(text)
    text = _SCI.sub(lambda m: f"{m.group(1)}e{int(m.group(2))}", text)
    out: list[str] = []
    for m in _TOKEN.finditer(text):
        token = (m.group("sign") or "") + _canon(m.group("a"))
        if m.group("b"):
            token += m.group("dash") + _canon(m.group("b"))
        unit = m.group("siunit") or m.group("unit")
        if unit:
            token += " " + _canon_unit(unit)
        out.append(token)
    return out


# --------------------------------------------------------------------------- other frozen tokens

def _prep(text: str) -> str:
    """The text the token finders read: no citation or reference macros, no figure pointers."""
    text = _SKIP_MACROS.sub(" ", text)
    text = _expand_siunitx(text)
    text = _FLOAT_REF.sub(" ", text)
    return _ISO_DATE.sub(" ", text)


_RANGE_WORDS = re.compile(
    rf"(?<![\w.])(?P<between>between\s+)?(?P<a>{_NUM})\s+(?:(?P<to>to|through|thru)"
    rf"|(?P<and>and))\s+(?P<b>{_NUM})(?![\w])", re.I)


def ranges_in_words(text: str) -> list[str]:
    """Ranges written as words: `400 to 700` and `between 400 and 700` both give `400 to 700`.

    A bare `400 and 700` is a pair, not a range, and gives nothing; so rewriting a range as
    a pair removes a token.
    """
    out = []
    for m in _RANGE_WORDS.finditer(_prep(text)):
        if m.group("and") and not m.group("between"):
            continue
        out.append(f"{_canon(m.group('a'))} to {_canon(m.group('b'))}")
    return out


_LATEX_OPS = (
    (re.compile(r"\\(?:leqslant|leq|le)(?![A-Za-z])"), "≤"),
    (re.compile(r"\\(?:geqslant|geq|ge)(?![A-Za-z])"), "≥"),
    (re.compile(r"\\(?:neq|ne)(?![A-Za-z])"), "≠"),
    (re.compile(r"\\approx(?![A-Za-z])"), "≈"),
    (re.compile(r"\\pm(?![A-Za-z])"), "±"),
    (re.compile(r"\\ll(?![A-Za-z])"), "≪"),
    (re.compile(r"\\gg(?![A-Za-z])"), "≫"),
    (re.compile(r"<="), "≤"), (re.compile(r">="), "≥"), (re.compile(r"!="), "≠"),
)
_GREEK_NAMES = ("alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi "
                "omicron pi rho sigma tau upsilon phi chi psi omega").split()
_GREEK_LOWER = "αβγδεζηθικλμν" \
               "ξοπρστυφχψω"
_GREEK_TEX = {}
for _name, _ch in zip(_GREEK_NAMES, _GREEK_LOWER):
    _GREEK_TEX[_name] = _ch
    _GREEK_TEX[_name.capitalize()] = _ch.upper()
_GREEK_CMD = re.compile(r"\\(?:var)?(" + "|".join(sorted(_GREEK_TEX, key=len, reverse=True))
                        + r")(?![A-Za-z])")
_GREEK_CHAR = re.compile("[Α-ΡΣ-Ωα-ω]")
_COMPARE = re.compile(rf"(?<![-=<])(?P<op>[<>≤≥≠≈±=≪≫])\s*"
                      rf"(?P<v>[-+]?(?:{_NUM}))")


def _greek(text: str) -> str:
    """`\\alpha` and `α` are one symbol; `\\varepsilon` is read as `\\epsilon`."""
    return _GREEK_CMD.sub(lambda m: _GREEK_TEX[m.group(1)], text)


def comparisons(text: str) -> list[str]:
    """A comparison sign and the number after it: `p < 0.05` gives `<0.05`.

    Covers `< > ≤ ≥ ≠ ≈ ± = ≪ ≫` and the LaTeX commands `\\leq \\geq \\approx \\pm` and the
    like. The left side is not part of the token, so `p-value < 0.05` and `p < 0.05` agree.
    """
    text = _prep(text)
    for rx, ch in _LATEX_OPS:
        text = rx.sub(ch, text)
    return [m.group("op") + _canon(m.group("v").lstrip("+")) if not m.group("v").startswith("-")
            else m.group("op") + "-" + _canon(m.group("v")[1:])
            for m in _COMPARE.finditer(text)]


_IDENT = re.compile(r"(?<![\w\\@./:-])[A-Za-z][A-Za-z0-9]*\d[A-Za-z0-9]*(?:\.\d+)?"
                    r"(?:/\d+(?:\.\d+)?)*")


def symbols(text: str) -> list[str]:
    """Greek letters (also as LaTeX commands) and names made of letters and digits.

    `sDA300/50`, `UDI300`, `CO2` and `PM2.5` are each one token, so changing a digit inside
    one is a change. `\\alpha` and `α` are the same symbol.
    """
    text = _greek(_prep(text))
    return _GREEK_CHAR.findall(text) + _IDENT.findall(text)


_ABBREV = re.compile(r"(?<![\w\\@./:-])(?P<t>[a-z]{0,2}[A-Z]{2,})s?(?![A-Za-z0-9])")
_STANDARD = re.compile(
    rf"(?<![\w\\@./:-])[A-Z]{{2,}}(?: [A-Z]{{1,3}})? \d[\d-]*(?::\d{{4}})?(?![\w]|\.\d)"
    rf"(?!\s?(?:{_UNIT_RE})(?![A-Za-z]))")


# Words that turn up in capitals in a heading or for emphasis. A two-letter word such as `OR`,
# `IS`, `AS`, `IT`, or `US` is left out on purpose: each can be an abbreviation.
_STOP = frozenset("""the and for with from into that this are was were not but nor yet all any can
    may its our their than then also both each such via per vs of in to on at by an be if so no
    note see here where when which while these those who how what why""".split())
_PLAIN_WORD = re.compile(r"[A-Za-z]+")


def plain_words(text: str) -> set:
    """The words of `text` that are not written in capitals, folded to lower case."""
    return {w.casefold() for w in _PLAIN_WORD.findall(text) if not (len(w) > 1 and w.isupper())}


def abbreviations(text: str, words=None) -> list[str]:
    """Abbreviations of two or more capitals (`DGP`, `sDA`) and standard names.

    A standard name is an abbreviation, an optional part letter, and a number: `ISO 9241`,
    `EN 17037`, `CIE S 026:2018`. A plural `s` is not part of the abbreviation.

    A word in capitals that is also written in ordinary case somewhere in `text`, or in
    `words` (a set of lower-case words, which a caller comparing two texts fills from both),
    is an ordinary word and not an abbreviation: `RESULTS` in a heading beside `Results`.
    """
    text = _prep(text)
    plain = _STOP | plain_words(text) | set(words or ())

    def ordinary(tok: str) -> bool:
        return tok.isupper() and tok.casefold() in plain and (len(tok) > 2 or tok.casefold() in _STOP)

    out = [m.group("t") for m in _ABBREV.finditer(text) if not ordinary(m.group("t"))]
    return out + [t for t in _STANDARD.findall(text) if not ordinary(t.split()[0])]
