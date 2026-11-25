#!/usr/bin/env python3
"""Check a BibTeX file: its fields, its duplicates, and what each DOI really points to.

    python3 bib_check.py refs.bib
    python3 bib_check.py refs.bib --tex main.tex
    python3 bib_check.py refs.bib --tex main.tex --online
    python3 bib_check.py refs.bib --online --email you@example.org --json report.json
    python3 bib_check.py refs.bib --online --record .paper/verified-refs.yml
    python3 bib_check.py refs.bib --tex main.tex --verified .paper/verified-refs.yml

Offline, it checks the required fields per entry type (the table in
references/latex-mechanics.md), duplicate keys, DOIs and titles, the page-range form, and,
with --tex, cited keys that have no entry and entries that are never cited.

With --online it also asks, for each DOI: does it resolve, and do the title, the year, and
the first author of the record match the entry? A DOI that resolves to a different paper is
the signature of a mistyped or invented reference. It then looks for a retraction, a
correction, or an expression of concern.

Three answers, never two. For notices the summary counts "notice found", "no notice found
in the sources checked", and "not checked". A failed request is "not checked". It is never
read as "no notice found", and "no notice found" is never proof that none exists.

Sources and fields, confirmed against live responses on 2026-11-15:
  https://doi.org/<doi> with Accept: application/vnd.citationstyles.csl+json
      title, issued.date-parts, author[0].family. Works for Crossref and DataCite DOIs,
      so arXiv DOIs resolve. An unknown DOI answers 404.
  https://api.crossref.org/works/<doi>
      message["updated-by"]: a list of notices, each with a "type" such as "retraction"
      or "correction" and the DOI of the notice.
  https://api.openalex.org/works/doi:<doi>
      "is_retracted": true or false.
All three are free and a single-work lookup needs no key. Nothing but the DOI is sent. Your
email is sent only if you pass --email, and only to Crossref, whose polite pool is reached by
an email. OpenAlex no longer has a polite pool reached by `mailto`; it uses an optional API
key instead (OpenAlex help page, read 2026-11-17), so it is never sent your email.

Reads `.bib` and LaTeX sources only: --tex takes a `.tex` file. For a Word manuscript,
export the reference-manager library to a `.bib` with the same citation keys.
Standard library only, except PyYAML for --verified and for --record onto an existing list.
It writes at most two files, each only when you ask: the verified list with --record (usually
.paper/verified-refs.yml) and the findings report with --json. It edits no other file. Its
output is evidence for references/latex-mechanics.md and the bibliography-auditor agent to
judge.

--record PATH (with --online) writes a `doi` row for each entry whose title and first author
or year matched the DOI record. It writes none for a work with too little metadata to compare
or with a retraction, withdrawal, removal or expression-of-concern notice, and it says why.
It keeps every `manual` row the author wrote and reports a manual row whose key is not in the
.bib. --verified PATH (with --tex) reports each cited key the list does not cover, each row
that is incomplete, and each entry that differs from its row. With `\\nocite{*}` it checks
every entry.

--record rewrites the whole verified list, so comments in that file are lost. It refuses to
rewrite a list it cannot read in full (no `references` key, `references` not a list, a row
that is not a mapping, a row with no `key`): it says why, exits 2 and leaves the file as it
was. A row whose method is not `doi` is kept as written; a method that is neither `doi` nor
`manual` is reported as VERIFIED_ROW_INCOMPLETE. Fields you add to a row keep their type.
--record writes no row when no notice source answered for the DOI.
A manual row keeps every field the author wrote; only absent fields are added. RECORD_NOT_WRITTEN
is printed only with --record.

Exit code 0 no findings, 1 findings, 2 cannot start (wrong arguments, a file that cannot be
read, no entries, a --tex file that is not `.tex`), 3 no findings but part of the check did
not run: an online request failed, an \\input file was not found, an entry type has no field
rules, an entry had too little metadata or no DOI to compare, an entry could not be parsed
(BIB_ENTRY_NOT_PARSED), a file was not valid UTF-8, or --tex found no cited key.
--json equal to any file it reads (the .bib, the --tex file, an included file, the --verified
list), or --record equal to the .bib, the --tex file or an included file, is refused (exit 2).
--record may name the --verified list: the list is rebuilt, then the draft is checked against it.
"""

from __future__ import annotations

import argparse
import os
import datetime
import difflib
import http.client
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

from fetch_oa_pdf import _ssl_context

# Mirrors the Required Fields table in references/latex-mechanics.md. A tuple inside the
# list means any one of its names satisfies the requirement.
REQUIRED = {
    "article": ["author", "title", ("journal", "journaltitle"), ("year", "date"), "volume",
                "pages"],
    "inproceedings": ["author", "title", "booktitle", ("year", "date")],
    "book": [("author", "editor"), "title", "publisher", ("year", "date")],
    "incollection": ["author", "title", "booktitle", "publisher", ("year", "date")],
    "phdthesis": ["author", "title", ("school", "institution"), ("year", "date")],
    "mastersthesis": ["author", "title", ("school", "institution"), ("year", "date")],
    "techreport": ["author", "title", "institution", ("year", "date")],
    "standard": ["title", ("organization", "institution"), ("year", "date")],
    "manual": ["title", ("organization", "institution"), ("year", "date")],
    "misc": ["author", "title", ("year", "date")],
    # Ordinary non-article types, BibTeX and biblatex names. A source a reader cannot locate
    # is the fault these rules catch, so each asks for the field that locates it.
    "conference": ["author", "title", "booktitle", ("year", "date")],
    "proceedings": ["title", ("year", "date")],
    "inbook": [("author", "editor"), "title", ("chapter", "pages", "booktitle"), "publisher",
               ("year", "date")],
    "thesis": ["author", "title", ("school", "institution"), ("year", "date")],
    "report": [("author", "editor"), "title", "institution", ("year", "date")],
    "unpublished": ["author", "title", ("year", "date"), "note"],
    "online": [("author", "editor", "organization"), "title", ("year", "date", "urldate"), "url"],
    "electronic": [("author", "editor", "organization"), "title", ("year", "date", "urldate"),
                   "url"],
    "dataset": [("author", "editor", "organization"), "title", ("year", "date"), ("doi", "url")],
    "software": [("author", "editor", "organization"), "title", ("year", "date"),
                 ("version", "doi", "url")],
}
INFO_CODES = {"BIB_DEFINED_NOT_CITED", "BIB_ENTRY_NOT_PARSED", "BIB_NOT_UTF8", "ONLINE_NOT_CHECKED", "BIB_TYPE_NOT_CHECKED",
              "VERIFIED_LIST_NOT_CHECKED", "NOTICE_NEW_VERSION", "RECORD_NOT_WRITTEN",
              "VERIFIED_ROW_ORPHAN", "VERIFIED_ROW_KEPT_MISMATCH",
              "CITE_COVERAGE_NOT_CHECKED"}
# Finding reasons that mean part of the check did not run, so the result is not clean.
NOT_CHECKED_REASONS = {"request_failed", "no_field_rules", "verified_list_unread",
                       "too_little_metadata", "no_cited_keys", "entry_not_parsed",
                       "not_utf8", "no_doi"}
TITLE_RATIO = 0.85
CSL = "application/vnd.citationstyles.csl+json"
AGENT = "paper-skills-bib-check/1.0"


def _finding(code: str, key: str | None, message: str, reason: str | None = None) -> dict:
    out = {"code": code, "key": key, "message": message}
    if reason:
        out["reason"] = reason
    return out


# --------------------------------------------------------------------------- parsing

def _read_value(text: str, i: int) -> tuple[str, int, bool]:
    """Read one field value starting at text[i]; return it, the index after it, and whether
    every brace or quote it opened was closed."""
    parts: list[str] = []
    n = len(text)
    closed = True
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        c = text[i]
        if c == "{":
            depth, j = 1, i + 1
            while j < n and depth:
                depth += (text[j] == "{") - (text[j] == "}")
                j += 1
            closed = closed and depth == 0
            parts.append(text[i + 1:j - 1] if depth == 0 else text[i + 1:j])
            i = j
        elif c == '"':
            j, depth = i + 1, 0
            while j < n and not (text[j] == '"' and depth == 0):
                depth += (text[j] == "{") - (text[j] == "}")
                j += 1
            closed = closed and j < n
            parts.append(text[i + 1:j])
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in ",}#\n":
                j += 1
            parts.append(text[i:j].strip())
            i = j
        while i < n and text[i] in " \t":
            i += 1
        if i < n and text[i] == "#":
            i += 1
            continue
        break
    return "".join(parts), i, closed


def parse_bib_checked(text: str) -> tuple[list[dict], list[str]]:
    """The entries of a BibTeX file and a list of problems: each `@type{` header that gave no
    entry, an entry written with parentheses, and a value whose brace or quote never closes
    (every later entry may then have been swallowed). Nothing is dropped without a word."""
    text = re.sub(r"(?m)^\s*%.*$", "", text)
    entries: list[dict] = []
    problems: list[str] = []
    pos, header = 0, re.compile(r"@\s*([A-Za-z]+)\s*([{(])")
    keyre = re.compile(r"\s*([^,\s{}]*)\s*(,?)")
    while True:
        m = header.search(text, pos)
        if not m:
            break
        kind = m.group(1).lower()
        if kind in ("comment", "string", "preamble"):
            # Skip the whole block, so an entry written inside it is not read as real.
            open_c, close_c = ("{", "}") if m.group(2) == "{" else ("(", ")")
            depth, j = 0, m.end() - 1
            while j < len(text):
                depth += (text[j] == open_c) - (text[j] == close_c)
                j += 1
                if depth == 0:
                    break
            if depth:
                problems.append(f"@{kind} block is never closed; the rest of the file was "
                                f"not read")
            pos = j
            continue
        km = keyre.match(text, m.end())
        label = f"@{kind}{m.group(2)}{km.group(1)}"
        if m.group(2) == "(":
            problems.append(f"{label}: an entry written with parentheses is not read")
            pos = km.end()
            continue
        if not km.group(1) or not km.group(2):
            problems.append(f"{label}: the key is missing or has no comma after it, so the "
                            f"entry was not read")
            pos = km.end()
            continue
        fields: dict[str, str] = {}
        i, n = km.end(), len(text)
        clean = True
        while i < n:
            fm = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(text, i)
            if not fm:
                break
            value, i, closed = _read_value(text, fm.end())
            clean = clean and closed
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", value).strip()
            while i < n and text[i] in " \t\r\n":
                i += 1
            if i < n and text[i] == ",":
                i += 1
                continue
            break
        while i < n and text[i] in " \t\r\n":
            i += 1
        if not clean or i >= n:
            problems.append(f"@{kind}{{{km.group(1)}: a brace or quote is never closed; this "
                            f"entry and every later one may not have been read")
        elif text[i] != "}":
            problems.append(f"@{kind}{{{km.group(1)}: text that is not a field follows near "
                            f"{text[i:i + 30]!r}; the fields after it were not read")
        else:
            i += 1
        entries.append({"key": km.group(1), "type": kind, "fields": fields})
        pos = i
    return entries, problems


def parse_bib(text: str) -> list[dict]:
    """Return the entries of a BibTeX file as {"key", "type", "fields"}.

    Field names and the entry type are lower-cased. Values keep their inner braces. The
    `@comment`, `@string`, and `@preamble` blocks, and `%` comment lines, are skipped.
    `parse_bib_checked` also returns what could not be read.
    """
    return parse_bib_checked(text)[0]


_CITE_COMMAND = re.compile(r"\\([A-Za-z]*cite[A-Za-z]*)\*?", re.I)
# Set-up, declaration and aux-file commands that hold no citation key.
_NOT_CITING = {"setcitestyle", "citestyle", "citetext", "citeindextrue", "citeindexfalse",
               "declarecitecommand", "bibcite", "citation"}
_OPTIONAL = re.compile(r"\s*(?:\[[^\]]*\]|\([^)]*\))")
_GROUP = re.compile(r"\s*\{([^}]*)\}")


def cited_keys(tex: str) -> set[str]:
    """Every key cited in a LaTeX source. `\\nocite{*}` gives {"*"}: everything is cited.

    Optional arguments, with or without white space between them, are skipped. A biblatex
    multicite (`\\cites{a}{b}`, `\\autocites`, `\\parencites`, ...) gives the key of every
    group. Any other cite command gives the keys of its first group only, so `\\defcitealias{k}{text}`
    gives `k`. Set-up commands (`\\setcitestyle`, `\\citestyle`, `\\citetext`, `\\citeindextrue`,
    `\\DeclareCiteCommand`, `\\bibcite`, `\\citation`) give no key.
    """
    tex = re.sub(r"(?<!\\)((?:\\\\)*)%.*$", r"\1", tex, flags=re.M)
    keys: set[str] = set()
    for m in _CITE_COMMAND.finditer(tex):
        if m.group(1).lower() in _NOT_CITING:
            continue
        multi = m.group(1).lower().endswith("cites")
        volume = m.group(1).lower().endswith("volcite")   # \volcite{vol}{key}: first group is not a key
        i = m.end()
        while True:
            while True:
                o = _OPTIONAL.match(tex, i)
                if not o:
                    break
                i = o.end()
            g = _GROUP.match(tex, i)
            if not g:
                break
            i = g.end()
            if volume:
                volume = False
                continue
            keys |= {k.strip() for k in g.group(1).split(",")
                     if k.strip() and not k.strip().startswith("#")}
            if not multi:
                break
    return keys


# --------------------------------------------------------------------------- normalising

def normalise_doi(raw: str) -> str:
    doi = re.sub(r"\\([_%&#])", r"\1", str(raw)).replace("{", "").replace("}", "")
    doi = doi.strip().lower()
    return re.sub(r"^(?:https?://(?:dx\.|www\.)?doi\.org/|doi:\s*)", "", doi)


def _plain(text: str) -> str:
    """Strip LaTeX accents, commands and braces, then fold to lower-case ASCII."""
    text = re.sub(r"\\[`'\"^~=.]|\\[A-Za-z]+\s*", "", str(text))
    text = unicodedata.normalize("NFKD", text.replace("{", "").replace("}", ""))
    return "".join(c for c in text if not unicodedata.combining(c)).casefold()


def _title_key(title: str) -> str:
    t = re.sub(r"^\s*retracted\s*:\s*", "", _plain(title))
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _first_family(author: str) -> str:
    first = re.split(r"\s+and\s+", author.strip(), maxsplit=1, flags=re.I)[0].strip()
    if first.startswith("{") and first.endswith("}"):
        return _plain(first)
    family = first.split(",")[0] if "," in first else first.split()[-1] if first.split() else ""
    return _plain(family).strip()


def _family_words(name: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", _plain(name)).split()


def _same_family(mine: str, theirs: str) -> bool:
    """Whole family names, after case, accents and hyphens are folded: equal; or, when one is
    several words, sharing the last word ("van der Berg" and "Berg"), or one name being the
    first or last whole words of the other ("Able-Jones" and "Able"). Never a bare
    substring: "Li" is not inside "Williams"."""
    a, b = _family_words(mine), _family_words(theirs)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = sorted((a, b), key=len)
    return len(long) > 1 and (a[-1] == b[-1] or long[:len(short)] == short)


def _year(fields: dict) -> int | None:
    m = re.search(r"\d{4}", fields.get("year") or fields.get("date") or "")
    return int(m.group(0)) if m else None


def _family_display(author: str) -> str:
    """The first author's family name as the entry writes it, without braces."""
    first = re.split(r"\s+and\s+", author.strip(), maxsplit=1, flags=re.I)[0].strip()
    if first.startswith("{") and first.endswith("}"):
        return first[1:-1].strip()
    family = first.split(",")[0] if "," in first else first.split()[-1] if first.split() else ""
    return family.replace("{", "").replace("}", "").strip()


def _title_marked(title: str) -> str:
    """The normalised title with `|` where a subtitle starts: after a colon, a question mark,
    or a dash. Used to tell a subtitle boundary from a title that merely opens the same way."""
    t = re.sub(r"^\s*retracted\s*:\s*", "", _plain(title))
    t = re.sub(r"\s*(?::|\?|-{2,}|[\u2013\u2014]|\s-\s)\s*", " | ", t)
    t = re.sub(r"[^a-z0-9|]+", " ", t)
    return re.sub(r"\s+", " ", t).strip(" |")


# --------------------------------------------------------------------------- offline

def offline_checks(entries: list[dict], cited: set[str] | None) -> list[dict]:
    """Field, duplicate, page-range and citation-coverage findings. No network."""
    out: list[dict] = []
    seen_key: set[str] = set()
    seen_doi: dict[str, str] = {}
    seen_title: dict[str, str] = {}
    unruled: dict[str, int] = {}
    for e in entries:
        key, f = e["key"], e["fields"]
        if e["type"] not in REQUIRED:
            unruled[e["type"]] = unruled.get(e["type"], 0) + 1
        for need in REQUIRED.get(e["type"], []):
            names = need if isinstance(need, tuple) else (need,)
            if not any(f.get(n) for n in names):
                out.append(_finding("BIB_MISSING_FIELD", key,
                                    f"@{e['type']} is missing {' or '.join(names)}"))
        if key in seen_key:
            out.append(_finding("BIB_DUPLICATE_KEY", key, "this key is defined more than once"))
        seen_key.add(key)
        if f.get("doi"):
            doi = normalise_doi(f["doi"])
            if doi in seen_doi and seen_doi[doi] != key:
                out.append(_finding("BIB_DUPLICATE_DOI", key,
                                    f"same DOI as entry {seen_doi[doi]}: {doi}"))
            seen_doi.setdefault(doi, key)
        title = _title_key(f.get("title", ""))
        if title:
            if title in seen_title and seen_title[title] != key:
                out.append(_finding("BIB_DUPLICATE_TITLE", key,
                                    f"same title as entry {seen_title[title]}"))
            seen_title.setdefault(title, key)
        if re.fullmatch(r"\s*\d+\s*-\s*\d+\s*", f.get("pages", "")):
            out.append(_finding("BIB_PAGE_RANGE_FORM", key,
                                f"pages = {f['pages']!r} uses one hyphen; write the range with "
                                f"`--`"))
    for kind in sorted(unruled):
        out.append(_finding("BIB_TYPE_NOT_CHECKED", None,
                            f"not checked: no field rules for @{kind} ({unruled[kind]} entries)",
                            reason="no_field_rules"))
    if cited is not None:
        for key in sorted(cited - {"*"} - seen_key):
            out.append(_finding("BIB_CITED_NOT_DEFINED", key,
                                "cited in the manuscript but has no entry in the .bib file"))
    if cited is not None and "*" not in cited:
        for key in sorted(seen_key - cited):
            out.append(_finding("BIB_DEFINED_NOT_CITED", key,
                                "has an entry but is never cited"))
    return out


# --------------------------------------------------------------------------- online

def _notice_code(kind: str) -> str:
    k = kind.casefold()
    if "retract" in k or "withdraw" in k:
        return "NOTICE_RETRACTION"
    if "remov" in k:
        return "NOTICE_RETRACTION"          # Crossref's `removal`: the article was taken down
    if "concern" in k:
        return "NOTICE_CONCERN"
    if k in ("new_version", "new_edition"):
        return "NOTICE_NEW_VERSION"
    return "NOTICE_CORRECTION"


BLOCKING_NOTICES = {"NOTICE_RETRACTION", "NOTICE_CONCERN"}


def _int(value) -> int | None:
    """A whole number from a value an outside record gave, or None."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _same_title(mine: str, theirs: str) -> bool:
    """Close enough to be the same work, for the online identity test only. A record often
    holds the title without the subtitle the entry carries, or the reverse, so one title
    opening the other counts when the longer one goes on after a subtitle boundary (a colon,
    a dash or a question mark). Takes titles as written; the stored-row test is exact."""
    a, b = _title_key(mine), _title_key(theirs)
    if difflib.SequenceMatcher(None, a, b).ratio() >= TITLE_RATIO:
        return True
    short, long = sorted((_title_marked(mine), _title_marked(theirs)), key=len)
    return len(short.split()) >= 3 and long.startswith(short + " |")


def online_checks(entries: list[dict], fetch: Callable[[str], dict | None],
                  verified: set[str] | None = None,
                  evidence: dict[str, dict] | None = None,
                  record: bool = True) -> list[dict]:
    """Identity and notice findings for each entry that has a DOI.

    `fetch(doi)` returns None when the request failed, {"resolved": False} when the DOI is
    unknown, or {"title", "year", "first_author_family", "notices"} with an optional
    "notices_checked": False when the record was read but no notice source answered, and an
    optional "sources_failed" naming a notice source that did not answer.

    `verified`, when given, receives the key of each entry whose DOI resolved to the work the
    entry describes: the title was compared and matched, at least one of the first author and
    the year was compared and matched, and the work carries no retraction, withdrawal, removal
    or concern notice. An entry that fails this gets a RECORD_NOT_WRITTEN note that says why.
    `evidence`, when given, receives for each such key which of "first_author" and "year" were
    compared and matched. That is what a verified list is built from.

    `record` says whether a verified list is being written. Only then is a condition that
    stops a row reported as RECORD_NOT_WRITTEN with the words "No row was written"; without
    it the same condition is reported as not checked, or by its notice, and says nothing of a row.
    """
    out: list[dict] = []
    for e in entries:
        key, f = e["key"], e["fields"]
        if not f.get("doi"):
            out.append(_finding("ONLINE_NOT_CHECKED", key,
                                "not checked: the entry has no DOI, so identity and notices "
                                "were not checked", reason="no_doi"))
            continue
        doi = normalise_doi(f["doi"])
        rec = fetch(doi)
        if rec is None:
            out.append(_finding("ONLINE_NOT_CHECKED", key,
                                f"the request for {doi} failed; identity and notices were not "
                                f"checked", reason="request_failed"))
            continue
        if rec.get("resolved") is False:
            out.append(_finding("DOI_NOT_RESOLVED", key,
                                f"{doi} did not resolve at doi.org. It may be mistyped or "
                                f"invented; check it by hand before deciding"))
            continue

        diffs: list[str] = []
        mine, theirs = _title_key(f.get("title", "")), _title_key(rec.get("title") or "")
        if mine and theirs and not _same_title(f.get("title", ""), rec.get("title") or ""):
            diffs.append(f"title: the DOI record says {str(rec.get('title'))!r}")
        year, their_year = _year(f), _int(rec.get("year"))
        if year and their_year and abs(year - their_year) > 1:
            diffs.append(f"year: entry {year}, DOI record {their_year}")
        family = _first_family(f.get("author", ""))
        their_family = _plain(rec.get("first_author_family") or "").strip()
        if family and their_family and not _same_family(family, their_family):
            diffs.append(f"first author: entry {family!r}, DOI record {their_family!r}")
        if diffs:
            out.append(_finding("DOI_IDENTITY_MISMATCH", key,
                                f"{doi} points to a different work or the entry is wrong. "
                                + "; ".join(diffs)))
        codes_here = {_notice_code(str(k)) for k in rec.get("notices") or []}
        if not diffs and verified is not None:
            title_ok = bool(mine and theirs)
            author_ok = bool(family and their_family)
            year_ok = bool(year and their_year)
            if not (title_ok and (author_ok or year_ok)):
                have = [n for n, ok in (("title", title_ok), ("first author", author_ok),
                                        ("year", year_ok)) if not ok]
                out.append(_finding("RECORD_NOT_WRITTEN" if record else "ONLINE_NOT_CHECKED", key,
                                    "not checked: too little metadata to compare. The title "
                                    "and one of first author or year must be present in the "
                                    f"entry and in the DOI record; missing on one side: "
                                    f"{', '.join(have)}." + (" No row was written" if record
                                                             else ""),
                                    reason="too_little_metadata"))
            elif rec.get("notices_checked") is False:
                if record:
                    out.append(_finding("RECORD_NOT_WRITTEN", key,
                                        "not checked: the notices could not be read. No row "
                                        "was written", reason="request_failed"))
            elif codes_here & BLOCKING_NOTICES:
                if record:
                    out.append(_finding("RECORD_NOT_WRITTEN", key,
                                        "not recorded: carries a notice (retraction, "
                                        "withdrawal, removal or expression of concern). No "
                                        "row was written"))
            else:
                verified.add(key)
                if evidence is not None:
                    evidence[key] = {"first_author": author_ok, "year": year_ok}

        for kind in rec.get("notices") or []:
            code = _notice_code(str(kind))
            if code == "NOTICE_NEW_VERSION":
                out.append(_finding(code, key,
                                    f"{doi} has a notice of type {kind!r}: a newer version or "
                                    f"edition exists. Check that this is the one you mean to "
                                    f"cite"))
                continue
            out.append(_finding(code, key,
                                f"{doi} carries a notice of type {kind!r}; read the notice "
                                f"before citing this work as support"))
        if rec.get("notices_checked") is False:
            out.append(_finding("ONLINE_NOT_CHECKED", key,
                                f"no notice source answered for {doi}; notices were not checked",
                                reason="request_failed"))
        elif rec.get("sources_failed"):
            out.append(_finding("ONLINE_NOT_CHECKED", key,
                                f"{' and '.join(rec['sources_failed'])} did not answer for "
                                f"{doi}; notices were checked at the other source only",
                                reason="request_failed"))
    return out


# --------------------------------------------------------------------------- verified list
# A citation is a fact. `.paper/verified-refs.yml` lists the keys whose entry was checked
# against a real record: by DOI with --online --record, or by hand as a `manual` row that says
# how. A draft may cite only those keys; --tex --verified checks that.

class VerifiedListError(Exception):
    """The verified list exists but cannot be read."""


def _yaml_str(value) -> str:
    """A YAML double-quoted scalar that reads back as `value`. JSON escapes are valid YAML
    escapes; with ensure_ascii every character outside ASCII becomes a \\u escape, so no line
    separator, C1 control or BOM reaches the file raw."""
    if value is None:
        return "null"
    text = str(value)
    if any(0xD800 <= ord(c) <= 0xDFFF for c in text):
        text = text.encode("utf-8", "replace").decode("utf-8")
    # JSON leaves DEL (U+007F) raw, and YAML does not accept it raw; \\x7f reads back as DEL.
    return json.dumps(text, ensure_ascii=True).replace("\x7f", "\\x7f")


def read_verified(path: Path) -> list[dict]:
    """The rows of a verified list. Raises VerifiedListError if the file cannot be read."""
    return read_verified_full(path)[0]


def read_verified_full(path: Path) -> tuple[list[dict], dict]:
    """(rows, other top-level keys, `version` included). They are the author's and are written
    back as they were."""
    try:
        import yaml
    except ImportError as e:
        raise VerifiedListError("reading a verified list needs PyYAML (pip install pyyaml)") from e
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:                                     # noqa: BLE001
        raise VerifiedListError(f"{path} cannot be read: {str(e).splitlines()[0]}") from e
    if data is None:
        return [], {}
    if not isinstance(data, dict) or "references" not in data:
        raise VerifiedListError(f"{path} has no `references` key (is it misspelt?)")
    extra = {k: v for k, v in data.items() if k not in ("updated", "references")}
    refs = data["references"]
    if refs is None:
        return [], extra
    if not isinstance(refs, list):
        raise VerifiedListError(f"{path}: `references` is not a list")
    for n, r in enumerate(refs, 1):
        if not isinstance(r, dict):
            raise VerifiedListError(f"{path}: row {n} of `references` is not a mapping")
        if r.get("key") in (None, ""):
            raise VerifiedListError(f"{path}: row {n} of `references` has no `key`")
    rows = [dict(r) for r in refs]
    for r in rows:
        r["key"] = str(r["key"])
    return rows, extra


def _evidence_fields(entry: dict, evidence: dict | None) -> dict:
    """The fields a row stores for an entry that was verified now: the DOI, the title, and the
    first author and year as far as they were compared and matched."""
    f = entry["fields"]
    seen = (evidence or {}).get(entry["key"], {"first_author": True, "year": True})
    out = {"doi": normalise_doi(f["doi"]), "title": f.get("title", "")}
    if seen.get("first_author") and f.get("author"):
        out["first_author"] = _family_display(f["author"])
    if seen.get("year") and _year(f):
        out["year"] = _year(f)
    return out


def verified_rows(entries: list[dict], online: list[dict], verified: set[str],
                  previous: list[dict], today: str,
                  evidence: dict[str, dict] | None = None) -> list[dict]:
    """The new verified list.

    A row whose method is not `doi` is always kept as it is. A manual row keeps its note. When this run verified its entry by DOI, the
    DOI evidence is added to it and its method stays `manual`. A DOI row is written for each
    entry verified now, and replaces the earlier DOI row. An earlier DOI row is kept only when
    this run could not reach the record for that entry. A manual row keeps every field the
    author wrote; only fields it lacks are added.
    """
    by_key = {e["key"]: e for e in entries}
    failed = {f["key"] for f in online
              if f.get("reason") == "request_failed" and f["key"] not in verified}
    rows: list[dict] = []
    manual: set[str] = set()
    for r in previous:
        key = r["key"]
        if r.get("method") == "manual":
            manual.add(key)
            row = dict(r)
            if key in verified:
                for name, value in _evidence_fields(by_key[key], evidence).items():
                    row.setdefault(name, value)
            rows.append(row)
        elif r.get("method") != "doi":
            manual.add(key)                 # a row the script does not own is never dropped
            rows.append(dict(r))
        elif key in by_key and key not in verified and key in failed:
            rows.append(r)
    for key in sorted(verified - manual):
        rows.append({"key": key, "method": "doi",
                     **_evidence_fields(by_key[key], evidence), "checked_on": today})
    return sorted(rows, key=lambda r: r["key"])


def record_notes(entries: list[dict], online: list[dict], previous: list[dict]) -> list[dict]:
    """Findings about the manual rows of a list that --record kept: a row whose key is not in
    the .bib (an orphan), and a row whose entry got DOI_IDENTITY_MISMATCH in the same run."""
    keys = {e["key"] for e in entries}
    mismatched = {f["key"] for f in online if f["code"] == "DOI_IDENTITY_MISMATCH"}
    out: list[dict] = []
    for r in previous:
        if r.get("method") not in ("doi", "manual"):
            out.append(_finding("VERIFIED_ROW_INCOMPLETE", r["key"],
                                f"method is {r.get('method')!r}; use `doi` or `manual`. The "
                                f"row was kept as written"))
            continue
        if r.get("method") != "manual":
            continue
        if r["key"] not in keys:
            out.append(_finding("VERIFIED_ROW_ORPHAN", r["key"],
                                "orphan row: this manual row's key is not in the .bib file. "
                                "The row was kept"))
        elif r["key"] in mismatched:
            out.append(_finding("VERIFIED_ROW_KEPT_MISMATCH", r["key"],
                                "the DOI of this entry did not match its record in this run. "
                                "The manual row was kept as written; check that it still "
                                "describes this entry"))
    return out


def _yaml_name(name) -> str:
    return str(name) if re.fullmatch(r"[A-Za-z_][\w-]*", str(name)) else _yaml_str(name)


def _yaml_value(value) -> str:
    """A YAML value that reads back with its type: a date stays a date, a number a number."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, (str, type(None))):
        return _yaml_str(value)
    try:
        import yaml
    except ImportError:                       # a new list has no nested value to keep
        return json.dumps(value, ensure_ascii=True, default=str).replace("\x7f", "\\x7f")
    if isinstance(value, (dict, list)):
        # Flow style on one line; PyYAML writes dates, floats and non-string keys so that a
        # load of the new file equals a load of the old one.
        return yaml.safe_dump(value, default_flow_style=True, width=10 ** 9).strip()
    return json.dumps(value, ensure_ascii=True, default=str).replace("\x7f", "\\x7f")


def write_verified(path: Path, rows: list[dict], today: str, extra: dict | None = None) -> None:
    """Write the list in one step: a temporary file beside it, then an atomic replace. `extra`
    holds the other top-level keys the author had in the file; they are written back."""
    order = ("key", "method", "doi", "title", "first_author", "year", "checked_on", "note")
    extra = dict(extra or {})
    version = extra.pop("version", 1)
    lines = [f"version: {_yaml_value(version)}", f"updated: {_yaml_str(today)}"]
    if extra:
        try:
            import yaml
            lines += yaml.safe_dump(extra, sort_keys=False, default_flow_style=False,
                                    allow_unicode=False).rstrip("\n").splitlines()
        except ImportError:                   # no PyYAML: only reachable with no extra keys
            pass
    lines += ["", "references:" if rows else "references: []"]
    for r in rows:
        first = True
        for field in order + tuple(k for k in r if k not in order):
            if field not in r:
                continue
            value = r[field]
            if field == "method" and value in ("doi", "manual"):
                text = value
            elif field == "year" and isinstance(value, int) and not isinstance(value, bool):
                text = str(value)
            elif isinstance(value, (datetime.date, datetime.datetime)) or (
                    field not in order and not isinstance(value, (str, type(None)))):
                # A field the author wrote keeps its YAML type: a date, a number, a flag, a list.
                text = _yaml_value(value)
            else:
                text = _yaml_str(value)
            lines.append(f"  {'- ' if first else '  '}{_yaml_name(field)}: {text}")
            first = False
    data = ("\n".join(lines) + "\n").encode("utf-8")
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _iso_date(value) -> bool:
    if isinstance(value, datetime.datetime):
        return True
    if isinstance(value, datetime.date):
        return True
    try:
        datetime.date.fromisoformat(str(value))
    except ValueError:
        return False
    return len(str(value)) == 10


def _row_gaps(row: dict) -> list[str]:
    """What a row lacks to count as evidence."""
    gaps: list[str] = []
    method = row.get("method")
    if not str(row.get("title") or "").strip():
        gaps.append("`title`")
    if not _iso_date(row.get("checked_on")):
        gaps.append("`checked_on` as an ISO date (YYYY-MM-DD)")
    if method == "manual":
        if len(str(row.get("note") or "").split()) < 3:
            gaps.append("a `note` of at least three words that says how the work was checked")
    elif not str(row.get("doi") or "").strip():
        gaps.append("`doi`")
    elif not (str(row.get("first_author") or "").strip() or row.get("year")):
        gaps.append("`first_author` or `year` (build the row again with --online --record)")
    return gaps


def _row_differences(row: dict, fields: dict) -> list[str]:
    """Each stored field of a row that differs from the entry now. The title is compared
    exactly, after case, accents, braces and punctuation are folded."""
    diffs: list[str] = []
    if str(row.get("doi") or "").strip():
        now = normalise_doi(fields.get("doi", "")) if fields.get("doi") else ""
        if now != normalise_doi(str(row["doi"])):
            diffs.append("doi")
    if str(row.get("title") or "").strip():
        if _title_key(fields.get("title", "")) != _title_key(str(row["title"])):
            diffs.append("title")
    if str(row.get("first_author") or "").strip():
        if _first_family(fields.get("author", "")) != _plain(str(row["first_author"])).strip():
            diffs.append("first author")
    if row.get("year") not in (None, ""):
        try:
            same = _year(fields) == int(str(row["year"]).strip())
        except ValueError:
            same = False
        if not same:
            diffs.append("year")
    return diffs


def verify_citations(entries: list[dict], cited: set[str], rows: list[dict]) -> list[dict]:
    """Findings for each cited key that the verified list does not cover, each incomplete row,
    and each row that differs from its entry. With `*` in `cited` (`\\nocite{*}`), every entry
    of the .bib file counts as cited."""
    out: list[dict] = []
    by_key = {e["key"]: e for e in entries}
    row_of = {r["key"]: r for r in rows}
    keys = (cited - {"*"}) | (set(by_key) if "*" in cited else set())
    for key in sorted(keys):
        if key not in by_key:
            continue                     # BIB_CITED_NOT_DEFINED reports it already
        row = row_of.get(key)
        if row is None:
            out.append(_finding("CITE_NOT_VERIFIED", key,
                                "cited, but not in the verified list. Check the entry against "
                                "the work (--online --record), or add a manual row that says how "
                                "you checked it"))
            continue
        method = row.get("method")
        if method not in ("doi", "manual"):
            out.append(_finding("VERIFIED_ROW_INCOMPLETE", key,
                                f"method is {method!r}; use `doi` or `manual`"))
            continue
        gaps = _row_gaps(row)
        if gaps:
            out.append(_finding("VERIFIED_ROW_INCOMPLETE", key,
                                f"a {method} row needs " + "; ".join(gaps)))
            continue
        diffs = _row_differences(row, by_key[key]["fields"])
        if diffs:
            out.append(_finding("CITE_VERIFICATION_STALE", key,
                                f"the entry changed after it was verified on "
                                f"{row.get('checked_on')} ({', '.join(diffs)}); verify it again"))
    return out


def summarise(entries: list[dict], findings: list[dict]) -> dict[str, int]:
    """Count entries by notice state. The three states are never merged."""
    by_key: dict[str, set[str]] = {}
    for f in findings:
        if f["code"] == "ONLINE_NOT_CHECKED" and f.get("reason") == "too_little_metadata":
            continue          # the notices were read; only the identity test had too little
        by_key.setdefault(f["key"], set()).add(f["code"])
    counts = {"notice found": 0, "no notice found in the sources checked": 0, "not checked": 0}
    for e in entries:
        codes = by_key.get(e["key"], set())
        if any(c.startswith("NOTICE_") and c != "NOTICE_NEW_VERSION" for c in codes):
            counts["notice found"] += 1
        elif codes & {"ONLINE_NOT_CHECKED", "DOI_NOT_RESOLVED"}:
            counts["not checked"] += 1
        else:
            counts["no notice found in the sources checked"] += 1
    return counts


_NETWORK_ERRORS = (OSError, http.client.HTTPException)


def _get_json(url: str, accept: str, agent: str) -> tuple[int, dict | None]:
    """(status, body). Raises OSError when the network itself fails."""
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": agent})
    try:
        with urllib.request.urlopen(req, timeout=25, context=_ssl_context()) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
            return r.status, body if isinstance(body, dict) else None
    except urllib.error.HTTPError as e:
        return e.code, None
    except json.JSONDecodeError:
        return 200, None                      # an HTTP 200 that is not the JSON asked for


def make_fetch(email: str | None = None, pause: float = 1.0) -> Callable[[str], dict | None]:
    """The real `fetch`: doi.org for identity, Crossref and OpenAlex for notices."""
    # Crossref's polite pool is reached by an email. OpenAlex has no such pool now (it uses
    # an optional API key, and a single-work lookup needs none), so it never gets the email.
    agent = AGENT + (f" (mailto:{email})" if email else "")
    mailto = f"mailto={urllib.parse.quote(email)}" if email else ""

    def fetch(doi: str) -> dict | None:
        quoted = urllib.parse.quote(doi, safe="/()")
        time.sleep(pause)
        try:
            status, csl = _get_json(f"https://doi.org/{quoted}", CSL, AGENT)
        except _NETWORK_ERRORS:
            return None
        if status == 404:
            return {"resolved": False}
        if status != 200 or csl is None:
            return None
        try:
            title = csl.get("title")
            parts = (csl.get("issued") or {}).get("date-parts") or [[None]]
            authors = csl.get("author") or [{}]
            rec = {"title": title[0] if isinstance(title, list) and title else title,
                   "year": parts[0][0] if parts and parts[0] else None,
                   "first_author_family": authors[0].get("family") or authors[0].get("literal"),
                   "notices": [], "notices_checked": False, "sources_failed": []}
        except (AttributeError, TypeError, IndexError, KeyError):
            return None                       # a record of a shape this script does not know
        # A 404 here means the source holds no record of this DOI, which is normal for a
        # DataCite DOI at Crossref. Any other failure means the source did not answer.
        try:
            status, cr = _get_json(f"https://api.crossref.org/works/{quoted}"
                                   + (f"?{mailto}" if mailto else ""), "application/json", agent)
            if status == 200 and cr:
                rec["notices_checked"] = True
                for u in (cr.get("message") or {}).get("updated-by") or []:
                    rec["notices"].append(str(u.get("type") or "update")
                                          if isinstance(u, dict) else "update")
            elif status != 404:
                rec["sources_failed"].append("Crossref")
        except _NETWORK_ERRORS + (AttributeError, TypeError):
            rec["sources_failed"].append("Crossref")
        try:
            status, oa = _get_json(f"https://api.openalex.org/works/doi:{quoted}"
                                   f"?select=doi,is_retracted", "application/json", AGENT)
            if status == 200 and oa:
                rec["notices_checked"] = True
                if oa.get("is_retracted") and "retraction" not in rec["notices"]:
                    rec["notices"].append("retraction")
            elif status != 404:
                rec["sources_failed"].append("OpenAlex")
        except _NETWORK_ERRORS + (AttributeError, TypeError):
            rec["sources_failed"].append("OpenAlex")
        return rec

    return fetch


# --------------------------------------------------------------------------- main

def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _manuscript import output_is_input
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib", help="the .bib file")
    ap.add_argument("--tex", help="the LaTeX root file, to compare cited keys with entries")
    ap.add_argument("--online", action="store_true",
                    help="also check each DOI's identity and notices (sends DOIs only)")
    ap.add_argument("--email", help="sent to Crossref only, for its polite pool; never sent to doi.org or OpenAlex")
    ap.add_argument("--json", help="write the findings to this file")
    ap.add_argument("--record", metavar="PATH",
                    help="with --online: write the entries whose DOI resolved to the work they "
                         "describe to this verified list (usually .paper/verified-refs.yml). "
                         "Always keeps the manual rows already in it")
    ap.add_argument("--verified", metavar="PATH",
                    help="with --tex: report every cited key that the verified list does not "
                         "cover. Needs PyYAML")
    args = ap.parse_args()
    if args.record and not args.online:
        print("--record needs --online: only an online check can verify an entry",
              file=sys.stderr)
        return 2
    if args.verified and not args.tex:
        print("--verified needs --tex: it checks the keys a manuscript cites", file=sys.stderr)
        return 2
    if args.online and args.email and not re.fullmatch(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+", args.email):
        print(f"--email {args.email!r}: this is not an email address that can be sent in a "
              f"request header. Nothing was checked.", file=sys.stderr)
        return 2
    inputs = {"the .bib file": args.bib, "the --tex file": args.tex}
    if args.tex and Path(args.tex).suffix.lower() == ".tex":
        try:                                   # every file the manuscript reader opens
            from _manuscript import read_manuscript_opened
            for f in read_manuscript_opened(Path(args.tex))[2][1:]:
                inputs[f"the included file {f}"] = f
        except OSError:
            pass                               # reported when the file is read below
    for flag, target in (("--json", args.json), ("--record", args.record)):
        # --record may name the --verified list: rebuild the list, then check against it.
        clash = output_is_input(target, dict(inputs, **(
            {"the --verified file": args.verified} if flag == "--json" else {})))
        if clash:
            print(f"{flag} {target}: this is {clash}, and the script would overwrite it. "
                  f"Nothing was checked.", file=sys.stderr)
            return 2
    if args.json and args.record and Path(args.json).resolve() == Path(args.record).resolve():
        print("--json and --record name the same file. Nothing was checked.", file=sys.stderr)
        return 2
    if args.json:
        jp = Path(args.json)
        parent = jp.resolve().parent
        if jp.is_dir() or not parent.is_dir() or not os.access(parent, os.W_OK) or (
                jp.exists() and not os.access(jp, os.W_OK)):
            print(f"--json {args.json}: this path cannot be written (the folder must exist and "
                  f"be writable, and the path must not be a folder). Nothing was checked.",
                  file=sys.stderr)
            return 2
    if args.tex and Path(args.tex).suffix.lower() != ".tex":
        print(f"--tex {args.tex}: bib_check.py reads LaTeX sources only, so it cannot read this "
              f"file. For a Word manuscript, export the reference-manager library to a .bib "
              f"file with the same citation keys, build the list with --online --record, and "
              f"compare the items cited in the document with the list by hand "
              f"(references/word-manuscripts.md).", file=sys.stderr)
        return 2
    previous: list[dict] = []
    extra: dict = {}
    if args.record and Path(args.record).exists():
        try:
            previous, extra = read_verified_full(Path(args.record))
        except VerifiedListError as e:
            print(f"--record refused, the file was not changed: {e}", file=sys.stderr)
            return 2

    unread: list[str] = []
    notes: list[dict] = []
    try:
        raw = Path(args.bib).read_bytes()
        try:
            bib_text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            bib_text = raw.decode("utf-8", errors="replace")
            notes.append(_finding("BIB_NOT_UTF8", None,
                                  f"not checked: {args.bib} is not valid UTF-8 (first bad byte "
                                  f"at offset {e.start}); undecodable bytes were replaced and "
                                  f"not read", reason="not_utf8"))
        entries, problems = parse_bib_checked(bib_text)
        cited = None
        if args.tex:
            from _manuscript import read_manuscript, read_manuscript_opened
            if Path(args.tex).suffix.lower() == ".tex":
                tex, unread, opened = read_manuscript_opened(Path(args.tex))
            else:
                (tex, unread), opened = read_manuscript(Path(args.tex)), [Path(args.tex)]
            for f in opened:
                try:
                    f.read_bytes().decode("utf-8")
                except UnicodeDecodeError as e:
                    notes.append(_finding("BIB_NOT_UTF8", None,
                                          f"not checked: {f} is not valid UTF-8 (first bad "
                                          f"byte at offset {e.start}); undecodable bytes were "
                                          f"replaced and not read", reason="not_utf8"))
            cited = cited_keys(tex)
    except OSError as e:
        print(f"cannot read: {e}", file=sys.stderr)
        return 2
    notes += [_finding("BIB_ENTRY_NOT_PARSED", None, f"not checked: {pr}",
                       reason="entry_not_parsed") for pr in problems]
    if not entries:
        for f in notes:
            print(f"  {f['code']:<24} {f['message']}")
        print(f"{args.bib}: no entries could be parsed. Nothing was checked.")
        return 2

    findings = notes + offline_checks(entries, cited)
    summary = None
    verified_note = None
    if args.online:
        ok_keys: set[str] = set()
        evidence: dict[str, dict] = {}
        online = online_checks(entries, make_fetch(args.email), ok_keys, evidence,
                               record=bool(args.record))
        findings += online
        summary = summarise(entries, online)
        if args.record:
            today = datetime.date.today().isoformat()
            rows = verified_rows(entries, online, ok_keys, previous, today, evidence)
            findings += record_notes(entries, online, previous)
            try:
                write_verified(Path(args.record), rows, today, extra)
            except OSError as e:
                print(f"--record failed, the file was not changed: {e}", file=sys.stderr)
                return 2
            verified_note = f"verified list: {len(rows)} row(s) written to {args.record}"
    if args.tex and not cited:
        findings.append(_finding("CITE_COVERAGE_NOT_CHECKED", None,
                                 f"citation coverage: not checked: no citation command was "
                                 f"found in {args.tex}", reason="no_cited_keys"))
    elif args.verified:
        try:
            rows = read_verified(Path(args.verified))
        except VerifiedListError as e:
            findings.append(_finding("VERIFIED_LIST_NOT_CHECKED", None,
                                     f"not checked: {e}", reason="verified_list_unread"))
        except OSError as e:
            findings.append(_finding("VERIFIED_LIST_NOT_CHECKED", None,
                                     f"not checked: {e}", reason="verified_list_unread"))
        else:
            findings += verify_citations(entries, cited, rows)

    print(f"{args.bib}: {len(entries)} entries"
          + (f", {len(cited - {'*'})} cited keys in {args.tex}" if cited is not None else "") + "\n")
    by_code: dict[str, int] = {}
    for f in findings:
        by_code[f["code"]] = by_code.get(f["code"], 0) + 1
        who = f"{f['key']}: " if f["key"] else ""
        print(f"  {f['code']:<24} {who}{f['message']}")
    if findings:
        print()
        for code in sorted(by_code):
            print(f"  {by_code[code]:>3}  {code}")
    if cited is None:
        print("  citation coverage: not checked (no --tex)")
    for name in unread:
        print(f"  citation coverage: partly not checked — \\input target not found: {name}")
    if summary is None:
        print("  online checks: not run (pass --online). DOI identity and notices were not "
              "checked.")
    else:
        print("\n  notices, per entry:")
        for label, n in summary.items():
            print(f"  {n:>3}  {label}")
        print("  'No notice found' covers Crossref and OpenAlex only. It is not proof that no "
              "notice exists.")
        print(f"  {len(ok_keys):>3}  entries whose DOI resolved to the work the entry describes")
    if verified_note:
        print(f"  {verified_note}")

    faults = [f for f in findings if f["code"] not in INFO_CODES]
    not_checked = bool(unread) or any(f.get("reason") in NOT_CHECKED_REASONS for f in findings)
    print(f"\n{len(faults)} finding(s) to act on, {len(findings) - len(faults)} note(s). "
          f"This is evidence, not a verdict.")
    if not_checked and not faults:
        print("This is NOT a clean result: part of the check was not run (see 'not checked' "
              "above).")
    if args.json:
        try:
            Path(args.json).write_text(json.dumps({"findings": findings, "summary": summary},
                                                  indent=2), encoding="utf-8")
        except OSError as e:
            print(f"--json failed, the report was not written: {e}", file=sys.stderr)
            return 2
    if faults:
        return 1
    if not_checked:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
