#!/usr/bin/env python3
"""Check the `.paper/` ledger files against their own rules.

The rules live in references/paper-memory.md (claims.yml, figures.yml, terms.yml, gap.yml)
and in the change-ledger-file.md reference of responding-to-reviewers (changes.yml). An agent
that checks them by reading drifts over a long revision. This script gives the same answer
every time.

    python3 check_ledger.py path/to/.paper
    python3 check_ledger.py path/to/.paper --manuscript manuscript.tex
    python3 check_ledger.py path/to/.paper --manuscript paper.docx --json findings.json

Give it the `.paper` directory, or the folder that contains it. Without --manuscript it
checks the files against each other. With it, it also traces the numbers the manuscript
quotes against `key_numbers`, and looks for `never_use` terms.

Needs PyYAML. Without it the script prints "not checked: install pyyaml" and exits 3. It
never reports a pass it did not compute.

A file that a consistency rule needs and that is absent (claims.yml for rules 1, 2, 5, 6 and
9, figures.yml for rules 1 to 4, terms.yml for 7 and 8, gap.yml for 9 and 10) is "not
checked", names those rules, and gives exit code 3 when nothing wrong was found. When
claims.yml is absent and changes.yml exists, the change-ledger findings are still printed.
`changes.yml` is optional by design (it exists only after peer review) and `venue.yml` is not
read here; an absent `changes.yml` is listed but does not change the exit code. When
`design.yml` exists beside the ledger, the script also lists each planned claim that no
claims.yml row names (a note, not a failure) and reports a claim whose planned claim a post
hoc choice amended (`CLAIM_POST_HOC_NOT_MARKED`) when its analysis_status is not post hoc. When
`design.yml` is absent that part is silent. `--manuscript` reports each part of a Word file it
could not read (equations, text boxes, headers and footers) as not checked. Every run ends with a line saying which rules and field
rules this script does not check, so a clean result never implies more than was checked.

What it is: evidence. Each finding has a code, the file, the row id, and a message. The
reference file decides what to do about a finding. What it is not: a check of whether a
claim is true, or whether its evidence supports it.

Exit code 0 no findings, 1 findings, 3 not checked — either nothing could be checked, or
nothing wrong was found but a section, an included file or a part of a Word file could not be
read, or a rule's file is absent.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from _manuscript import (fold, json_target_problem, numbers, read_manuscript_checked,
                         split_sections, write_json_file)

try:
    if os.environ.get("PAPER_LEDGER_NO_YAML"):          # lets a test take the no-PyYAML path
        raise ImportError
    import yaml
except ImportError:
    yaml = None

FILES = ("claims.yml", "figures.yml", "terms.yml", "gap.yml", "changes.yml")
CLAIM_STATUSES = {"supported", "needs evidence", "gap", "rejected"}
FIGURE_STATUSES = {"draft", "final", "regenerate"}
CHANGE_DECISIONS = {"concede", "partially concede", "contest"}
CHANGE_STATUSES = {"done", "partial", "open", "regressed", "made worse", "not verifiable",
                   "waived", "promised"}
# One list each for the comment type and its severity, shared with triage.md.
COMMENT_TYPES = {"misreading", "missing information", "method", "evidence", "claim", "framing",
                 "presentation", "language", "out of scope", "wrong"}
SEVERITIES = {"blocking", "substantive", "minor"}
UNFINISHED = {"open", "regressed", "made worse"}
SETTLED = {"done", "waived", "not verifiable"}
VERB_DECISIONS = {"restore", "keep", "pause"}
CONFLICT_TYPES = {"view", "severity", "existence", "direction"}
ANALYSIS_STATUSES = {"planned", "changed before analysis", "post hoc", "not applicable"}
# The verbs a `needs evidence` claim may not carry: paper-review.md, Status gates the verb. Keep
# the two lists identical. A `gap` or `rejected` row carries no verb at all, except that a `gap`
# row may state an assumption with the verbs that paper-memory.md shows.
ASSUMPTION_VERBS = {"assume", "assumes"}
STRONG_VERBS = {"shows", "demonstrates", "proves", "establishes", "confirms", "indicates"}
_STRONG = re.compile(r"^(?:shows?|showed|shown|demonstrat(?:e|es|ed)|prov(?:e|es|ed|en)"
                     r"|establish(?:es|ed)?|confirm(?:s|ed)?|indicat(?:e|es|ed))\b")
_EVIDENCE_FLOAT = re.compile(r"^\s*(Fig|Tab)[a-z]*\.?\s*(\d+)", re.I)
# Sections whose numbers must trace to a figure, a table, or the Results.
TRACED = ("abstract", "introduction", "discussion", "conclusion")
# Reported so that nothing unread passes as clean. Alone they give exit code 3, not 1.
INFO_CODES = {"SECTION_NOT_CHECKED", "INPUT_NOT_FOUND", "RULE_NOT_CHECKED", "PART_NOT_CHECKED"}
# A note is printed and never changes the exit code.
NOTE_CODES = {"PLANNED_CLAIM_NOT_YET_CLAIMED"}
# The consistency rules (paper-memory.md) that each file is needed for. An absent file in this
# table means those rules did not run. `changes.yml` and `venue.yml` are optional by design.
RULES_NEEDING = {"claims.yml": (1, 2, 5, 6, 9), "figures.yml": (1, 2, 3, 4),
                 "terms.yml": (7, 8), "gap.yml": (9, 10)}
OPTIONAL_FILES = {"changes.yml": "it exists only after peer review"}
_NOT_COVERED = (
    "not checked by this script: whether evidence supports a claim; field rules claims 4 (that "
    "each location is accurate), 6 (bounded_to) and 7; figures 2 (source), 3 (an empty "
    "supports_claims), 4 (an empty cited_in) and 6 (transformation); terms 3 (defined_at "
    "order); gap 2 (rounds_run) and 5 (search). Rule 2 reads only evidence that starts with "
    "Fig or Tab. Rule 6 checks each claim's verb against its status: a needs evidence row may "
    "not carry shows, demonstrates, proves, establishes, confirms or indicates; a gap row may "
    "carry no verb except the assumption verbs assume and assumes; a rejected row carries none "
    "and is itself reported. Rule 8 compares the written meanings, not their sense. Rule 10 "
    "looks for the study's name or cite key, not for a discussion of it. "
    "Change-ledger cross-checks not run: cross-check 1 (the count of rows against the decision "
    "letter); 7 (a claim weakened in response to a comment has had its claims.yml row "
    "updated); 8 (a regenerated figure has status final and re-verified key_numbers); 9 (every "
    "paragraph of the response letter maps to a row; the script checks only that each row "
    "has a response_paragraph); cross-check 10 (every number quoted in the response is the "
    "number in the manuscript); whether a manuscript meets a done_when; whether an "
    "affects_runs or amendment id exists.")
_DATE = re.compile(
    r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?(?:\s+\d{4})?"
    r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,?\s+\d{4})?")
# Integers that are not quantities: numeric citations, list numbering, page numbers, labels
# such as "Phase 2", and 3D or 2nd.
_INT_NOISE = re.compile(
    r"\[\s*\d+(?:\s*[-,;]\s*\d+)*\s*\]|(?m:^[ \t]*\(?\d+[.)][ \t])|\bpp?\.\s*\d+(?:-\d+)?"
    r"|\b(?:Phase|Group|Scenario|Experiment|Study|Model|Run|Part|Stage|Version|Method|Option|"
    r"Variant|Level|Task|Set|Layer|Case|Cluster|Batch)s?\s+\d+\b|\b\d+(?:st|nd|rd|th|D)\b")
_QUOTED = re.compile(r"``.{0,600}?''|\u201c.{0,600}?\u201d|\"[^\"\n]{0,600}\"", re.S)
_TABLE_ENV = re.compile(r"\\begin\{(table\*?|tabular\w*|longtable)\}.*?\\end\{\1\}", re.S)


class NotChecked(Exception):
    """The audit could not run at all. The message says why."""


def _finding(code: str, file: str, row_id, message: str) -> dict:
    return {"code": code, "file": file, "id": None if row_id is None else str(row_id),
            "message": message}


def _load(paper_dir: Path, name: str, key: str, out: list[dict],
          required: bool = True) -> list[dict] | None:
    """The rows under `key` in one ledger file, or None when the file is absent or broken.

    A file that parses but lacks its `key` is broken, not empty: a misspelled `claim:` must
    never read as a ledger with zero claims. Pass `required=False` for an optional block."""
    path = paper_dir / name
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        out.append(_finding("FILE_UNPARSEABLE", name, None,
                            f"cannot be parsed as YAML: {str(e).splitlines()[0]}"))
        return None
    if not isinstance(data, dict):
        out.append(_finding("FILE_UNPARSEABLE", name, None,
                            "is empty or is not a mapping; nothing in it was checked"))
        return None
    if key not in data:
        if required:
            out.append(_finding("FILE_UNPARSEABLE", name, None,
                                f"has no `{key}` key; nothing in it was checked"))
            return None
        return []
    rows = data.get(key)
    if rows is None:
        rows = []
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        out.append(_finding("FILE_UNPARSEABLE", name, None,
                            f"`{key}` is not a list of rows; nothing in it was checked"))
        return None
    return rows


def _duplicates(rows: list[dict], name: str, code: str, out: list[dict]) -> set[str]:
    seen: set[str] = set()
    for r in rows:
        rid = r.get("id")
        if rid is None:
            out.append(_finding(code.replace("_DUPLICATE", "_MISSING"), name, None,
                                "a row has no id"))
        elif str(rid) in seen:
            out.append(_finding(code, name, rid, f"id {rid} is used by more than one row"))
        else:
            seen.add(str(rid))
    return seen


def _list_field(row: dict, field: str, name: str, out: list[dict]) -> list:
    """The items of a list field. The guide writes these as lists; a bare string is a schema
    fault, reported once and still read as a single item, never character by character."""
    value = row.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    out.append(_finding("FIELD_NOT_LIST", name, row.get("id"),
                        f"{field} is written as a single {type(value).__name__}, not a list; "
                        f"the guide writes a list. It was read as one item."))
    return [value]


def _is_strong(verb) -> bool:
    return bool(_STRONG.match(str(verb or "").casefold().strip()))


def _check_claims(rows: list[dict], figure_ids: set[str] | None, out: list[dict]) -> None:
    name = "claims.yml"
    _duplicates(rows, name, "CLAIM_ID_DUPLICATE", out)
    for r in rows:
        rid, status = r.get("id"), r.get("status")
        evidence = _list_field(r, "evidence", name, out)
        if status not in CLAIM_STATUSES:
            out.append(_finding("CLAIM_STATUS_INVALID", name, rid,
                                f"status is {status!r}; allowed: supported, needs evidence, "
                                f"gap, rejected. Blank is never allowed."))
        if not evidence and status not in ("gap", "needs evidence"):
            out.append(_finding("CLAIM_EVIDENCE_EMPTY", name, rid,
                                f"evidence is empty but status is {status!r}; an empty "
                                f"evidence list needs status gap or needs evidence"))
        if status == "gap" and not r.get("gap_reason"):
            out.append(_finding("CLAIM_GAP_NO_REASON", name, rid,
                                "status is gap and gap_reason is missing"))
        verb = str(r.get("verb") or "").strip()
        if status == "rejected":
            out.append(_finding("CLAIM_REJECTED", name, rid,
                                "status is rejected: the data contradict the claim, and the "
                                "sentence must be rewritten to match them. This blocks the "
                                "Submission Gate (item 1)"))
        if status == "needs evidence" and _is_strong(verb):
            out.append(_finding("CLAIM_VERB_EXCEEDS_STATUS", name, rid,
                                f"verb {r.get('verb')!r} is stronger than status {status!r} "
                                f"permits"))
        elif status == "rejected" and verb:
            out.append(_finding("CLAIM_VERB_EXCEEDS_STATUS", name, rid,
                                f"verb {r.get('verb')!r} on a rejected claim; status rejected "
                                f"permits no verb"))
        elif status == "gap" and verb and verb.casefold() not in ASSUMPTION_VERBS:
            out.append(_finding("CLAIM_VERB_EXCEEDS_STATUS", name, rid,
                                f"verb {r.get('verb')!r} on a gap claim; status gap permits no "
                                f"verb except an assumption ({', '.join(sorted(ASSUMPTION_VERBS))})"))
        if "analysis_status" in r and r.get("analysis_status") not in ANALYSIS_STATUSES:
            out.append(_finding("CLAIM_ANALYSIS_STATUS_INVALID", name, rid,
                                f"analysis_status is {r.get('analysis_status')!r}; allowed: "
                                f"planned, changed before analysis, post hoc, not applicable"))
        vc = r.get("verb_change")
        if vc is not None:
            verdict = vc.get("decision") if isinstance(vc, dict) else None
            if verdict not in VERB_DECISIONS or (verdict == "keep" and not vc.get("reason")):
                out.append(_finding("CLAIM_VERB_NO_DECISION", name, rid,
                                    "verb_change has no decision; choose restore, keep with a "
                                    "reason, or pause"))
        if not r.get("location"):
            out.append(_finding("CLAIM_LOCATION_EMPTY", name, rid,
                                "location is empty; record where the claim is asserted"))
        if status == "gap" and r.get("load_bearing") is True:
            out.append(_finding("CLAIM_LOAD_BEARING_GAP", name, rid,
                                "a load-bearing claim has status gap; this fails the "
                                "Submission Gate"))
        if figure_ids is not None:
            for ev in evidence:
                m = _EVIDENCE_FLOAT.match(str(ev))
                if m:
                    fid = f"{m.group(1).capitalize()}{m.group(2)}"
                    if fid not in figure_ids:
                        out.append(_finding("CLAIM_EVIDENCE_UNKNOWN_FIGURE", name, rid,
                                            f"evidence {ev!r} has no figures.yml row {fid}"))


def _check_figures(rows: list[dict], claim_ids: set[str] | None, out: list[dict]) -> None:
    name = "figures.yml"
    _duplicates(rows, name, "FIG_ID_DUPLICATE", out)
    for r in rows:
        rid, status = r.get("id"), r.get("status")
        if status not in FIGURE_STATUSES:
            out.append(_finding("FIG_STATUS_INVALID", name, rid,
                                f"status is {status!r}; allowed: draft, final, regenerate"))
        if status == "regenerate":
            out.append(_finding("FIG_REGENERATE", name, rid,
                                "status is regenerate; this blocks the Submission Gate until "
                                "the figure is final and its key_numbers are re-verified"))
        supports = _list_field(r, "supports_claims", name, out)
        if claim_ids is not None:
            for cid in supports:
                if str(cid) not in claim_ids:
                    out.append(_finding("FIG_SUPPORTS_UNKNOWN_CLAIM", name, rid,
                                        f"supports_claims names {cid}, which is not in "
                                        f"claims.yml"))


def _check_design(paper_dir: Path, claims: list[dict], out: list[dict]) -> None:
    """When design.yml sits beside the ledger: a planned claim that no claims.yml row names
    (a note), and a claim that a post hoc choice amended but that is not marked post hoc."""
    if not (paper_dir / "design.yml").is_file():
        return
    planned = _load(paper_dir, "design.yml", "planned_claims", out, required=False)
    amendments = _load(paper_dir, "design.yml", "amendments", out, required=False)
    named = {str(c.get("planned_claim")) for c in claims if c.get("planned_claim")}
    for p in planned or []:
        if p.get("id") is not None and str(p["id"]) not in named:
            out.append(_finding("PLANNED_CLAIM_NOT_YET_CLAIMED", "design.yml", p["id"],
                                f"planned claim {p['id']} is named by no claims.yml row "
                                f"(planned_claim); not yet claimed"))
    amended: dict[str, str] = {}
    for a in amendments or []:
        if a.get("timing") == "post hoc" and a.get("kind") == "choice":
            affects = a.get("affects") or []
            for pid in affects if isinstance(affects, list) else [affects]:
                amended.setdefault(str(pid), str(a.get("id")))
    for c in claims:
        pid = c.get("planned_claim")
        if pid is not None and str(pid) in amended and c.get("analysis_status") != "post hoc":
            out.append(_finding("CLAIM_POST_HOC_NOT_MARKED", "claims.yml", c.get("id"),
                                f"planned claim {pid} was changed by amendment {amended[str(pid)]} "
                                f"(post hoc, a choice), so analysis_status must be post hoc; it "
                                f"is {c.get('analysis_status')!r}"))


def _check_gaps(rows: list[dict], claims: list[dict] | None, out: list[dict]) -> None:
    status_of = {str(c.get("id")): c.get("status") for c in claims or []}
    for r in rows:
        linked = _list_field(r, "linked_claims", "gap.yml", out)
        if r.get("status") == "verified":
            continue
        for cid in linked:
            if claims is not None and status_of.get(str(cid)) != "needs evidence":
                out.append(_finding("GAP_UNVERIFIED_LINKED", "gap.yml", r.get("id"),
                                    f"gap status is {r.get('status')!r} but linked claim {cid} "
                                    f"has status {status_of.get(str(cid))!r}; it must be needs "
                                    f"evidence until the gap is verified"))


def _check_changes(rows: list[dict], claim_ids: set[str] | None,
                   figure_ids: set[str] | None, out: list[dict],
                   editorial_decision: str | None = None) -> None:
    name = "changes.yml"
    _duplicates(rows, name, "CHANGE_ID_DUPLICATE", out)
    for r in rows:
        rid, status, decision = r.get("id"), r.get("status"), r.get("decision")
        if decision not in CHANGE_DECISIONS:
            out.append(_finding("CHANGE_DECISION_INVALID", name, rid,
                                f"decision is {decision!r}; allowed: concede, partially "
                                f"concede, contest. A missing or other value is invalid"))
        if r.get("decision_confirmed") is False or \
                str(r.get("decision_confirmed")).strip().casefold() == "false":
            out.append(_finding("CHANGE_DECISION_PROPOSED", name, rid,
                                "decision_confirmed is false: the decision is proposed and the "
                                "author has not confirmed it. The response is not ready to send"))
        if r.get("type") not in COMMENT_TYPES:
            out.append(_finding("CHANGE_TYPE_INVALID", name, rid,
                                f"type is {r.get('type')!r}; allowed: "
                                f"{', '.join(sorted(COMMENT_TYPES))}"))
        if r.get("severity") not in SEVERITIES:
            out.append(_finding("CHANGE_SEVERITY_INVALID", name, rid,
                                f"severity is {r.get('severity')!r}; allowed: "
                                f"{', '.join(sorted(SEVERITIES))}"))
        if status == "promised" and editorial_decision != "rebuttal":
            out.append(_finding("CHANGE_PROMISED_OUTSIDE_REBUTTAL", name, rid,
                                "status is promised, which is for a conference rebuttal only; "
                                "a journal revision is the deliverable, so the change is done "
                                "or it is open"))
        if status not in CHANGE_STATUSES:
            out.append(_finding("CHANGE_STATUS_INVALID", name, rid,
                                f"status is {status!r}; allowed: "
                                f"{', '.join(sorted(CHANGE_STATUSES))}"))
        if status == "done" and not r.get("verified_on"):
            out.append(_finding("CHANGE_DONE_NOT_VERIFIED", name, rid,
                                "status is done but verified_on is empty; open the manuscript, "
                                "find the change, and record the date"))
        if status == "done" and not r.get("manuscript_change"):
            if decision == "concede":
                out.append(_finding("CHANGE_CONCEDE_NO_CHANGE", name, rid,
                                    "decision is concede and manuscript_change is empty; that is "
                                    "unfinished work, not a valid done"))
            else:
                out.append(_finding("CHANGE_DONE_NO_CHANGE", name, rid,
                                    "status is done and manuscript_change is empty; done is "
                                    "only for a change that exists in the manuscript. A contested "
                                    "comment with no change is waived"))
        if (status == "done" or (decision == "concede" and status == "partial")) \
                and not r.get("location"):
            out.append(_finding("CHANGE_LOCATION_EMPTY", name, rid,
                                f"status is {status} and location is empty; record where the "
                                f"change is in the manuscript"))
        if decision == "contest" and not r.get("reason"):
            out.append(_finding("CHANGE_CONTEST_NO_REASON", name, rid,
                                "decision is contest and reason is empty"))
        if status == "waived" and not (r.get("waived_by") and r.get("waived_risk")
                                       and isinstance(r.get("flagged_to_editor"), bool)):
            out.append(_finding("CHANGE_WAIVED_INCOMPLETE", name, rid,
                                "status is waived; waived_by, waived_risk and a decision on "
                                "flagged_to_editor (true or false) are all required"))
        if status in UNFINISHED:
            out.append(_finding("CHANGE_OPEN", name, rid,
                                f"status is {status}; the comment is not yet settled"))
        if status == "partial" and not r.get("partial_reason"):
            out.append(_finding("CHANGE_PARTIAL_NO_REASON", name, rid,
                                "status is partial and partial_reason is empty; say what was "
                                "not done and why"))
        if decision in ("concede", "partially concede") and not r.get("done_when"):
            out.append(_finding("CHANGE_NO_DONE_WHEN", name, rid,
                                "the decision is a concession and there is no done_when; write "
                                "the manuscript evidence that settles it, whatever the status"))
        if not r.get("response_paragraph"):
            out.append(_finding("CHANGE_NO_RESPONSE_PARAGRAPH", name, rid,
                                "response_paragraph is empty; record where the response letter "
                                "answers this comment"))
        for vc in r.get("claim_verb_change") or []:
            if not isinstance(vc, dict):
                continue
            verdict, claim = vc.get("decision"), vc.get("claim")
            if verdict not in VERB_DECISIONS or (verdict == "keep" and not vc.get("reason")):
                out.append(_finding("CHANGE_VERB_NO_DECISION", name, rid,
                                    f"the verb of claim {claim} changed from "
                                    f"{vc.get('before')!r} to {vc.get('after')!r} with no "
                                    f"decision; choose restore, keep with a reason, or pause"))
            elif verdict == "pause":
                out.append(_finding("CHANGE_OPEN", name, rid,
                                    f"the verb change on claim {claim} is paused for the "
                                    f"author to decide"))
        for field, known, where in (("affects_claims", claim_ids, "claims.yml"),
                                    ("affects_figures", figure_ids, "figures.yml")):
            refs = _list_field(r, field, name, out)
            if known is None:
                continue
            for ref in refs:
                if str(ref) not in known:
                    out.append(_finding("CHANGE_AFFECTS_UNKNOWN", name, rid,
                                        f"{field} names {ref}, which is not in {where}"))


def _split(token: str) -> tuple[str, str]:
    number, _, unit = token.partition(" ")
    return number, unit


def _covered(token: str, pool: list[tuple[str, str]]) -> bool:
    """Same digits, and the same unit where both sides state one."""
    number, unit = _split(token)
    return any(number == n and (not unit or not u or unit == u) for n, u in pool)


def _metric_like(token: str) -> bool:
    """A unit or a decimal."""
    return " " in token or "." in token


def _checkable(token: str) -> bool:
    """Traced to the ledger: a quantity with a unit, a decimal, or a bare integer that is not
    a year. A range of bare integers (a year span, a page range) is not traced."""
    if _metric_like(token):
        return True
    return token.isdigit() and not (len(token) == 4 and 1900 <= int(token) <= 2100)


def _trace_text(text: str) -> str:
    """The section text without dates, numeric citations, list numbers and labels."""
    return _INT_NOISE.sub(" ", _DATE.sub(" ", text))


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold().strip()


def _dissent_found(entry, discussion: str) -> bool:
    """True when the study is named in the Discussion text: its citation text as written, or
    its surname followed within 60 characters by its year, or a \\cite key that contains both."""
    if isinstance(entry, dict):
        entry = entry.get("cite") or entry.get("key") or ""
    cite = re.split(r"\s+-+\s+|\s*[;:]\s", fold(str(entry)), maxsplit=1)[0].strip()
    text = _norm(discussion)
    if cite and _norm(cite) in text:
        return True
    year = re.search(r"\b((?:19|20)\d{2})[a-z]?\b", cite)
    names = re.findall(r"[^\W\d_]+", cite[:year.start()]) if year else []
    if not year or not names:
        return False
    surname, yr = names[0].casefold(), year.group(1)
    if re.search(rf"\b{re.escape(surname)}\b.{{0,60}}?\b{yr}", text):
        return True
    for m in re.finditer(r"\\[A-Za-z]*cite[A-Za-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", discussion):
        if any(surname in k.casefold() and yr in k for k in m.group(1).split(",")):
            return True
    return False


def _check_dissent(gaps: list[dict], sections: dict[str, str], manuscript_name: str,
                   out: list[dict]) -> None:
    """Rule 10: each dissenting study is named in the Discussion."""
    rows = [(g, _list_field(g, "dissenting_studies", "gap.yml", out)) for g in gaps]
    if not any(entries for _, entries in rows):
        return
    if "discussion" not in sections:
        out.append(_finding("RULE_NOT_CHECKED", manuscript_name, "rule10",
                            "rule 10 (dissenting_studies addressed in the Discussion) was not "
                            "checked: no Discussion section was found"))
        return
    for g, entries in rows:
        for entry in entries:
            if not _dissent_found(entry, sections["discussion"]):
                out.append(_finding("DISSENT_NOT_IN_DISCUSSION", "gap.yml", g.get("id"),
                                    f"dissenting study {str(entry)!r} is not named in the "
                                    f"Discussion of {manuscript_name} (neither its citation "
                                    f"text nor a cite key with its name and year)"))


def _check_symbols(terms: list[dict], symbols: list[dict], out: list[dict]) -> None:
    """Rule 8: one symbol, one meaning; one quantity, one symbol. Meanings are compared as
    written (case and spacing ignored), so a paraphrase reads as a different meaning."""
    pairs: list[tuple[str, str, str]] = []              # (symbol, meaning, as written)
    for t in terms:
        if t.get("symbol") and t.get("canonical"):
            pairs.append((str(t["symbol"]), str(t["canonical"]), "terms"))
    for s_ in symbols:
        if s_.get("symbol") and s_.get("means"):
            pairs.append((str(s_["symbol"]), str(s_["means"]), "symbols"))
    by_symbol: dict[str, dict[str, str]] = {}
    by_meaning: dict[str, dict[str, str]] = {}
    for sym, meaning, _ in pairs:
        sk, mk = re.sub(r"[\s{}$\\]", "", sym), _norm(meaning).rstrip(".")
        by_symbol.setdefault(sk, {}).setdefault(mk, meaning)
        by_meaning.setdefault(mk, {}).setdefault(sk, sym)
    for sk, meanings in by_symbol.items():
        if len(meanings) > 1:
            out.append(_finding("SYMBOL_TWO_MEANINGS", "terms.yml", sk,
                                f"symbol {sk} carries {len(meanings)} meanings: "
                                f"{'; '.join(repr(m) for m in meanings.values())}"))
    for mk, syms in by_meaning.items():
        if len(syms) > 1:
            out.append(_finding("QUANTITY_TWO_SYMBOLS", "terms.yml", mk,
                                f"the quantity {mk!r} has {len(syms)} symbols: "
                                f"{', '.join(syms.values())}"))


def _check_manuscript(figures: list[dict] | None, terms: list[dict] | None,
                      gaps: list[dict] | None, manuscript: Path, out: list[dict]) -> None:
    name = manuscript.name
    try:
        text, missing, skipped = read_manuscript_checked(manuscript)
    except Exception as e:                                       # noqa: BLE001
        raise NotChecked(f"not checked: manuscript {manuscript} could not be read: {e}") from e
    for part in skipped:
        out.append(_finding("PART_NOT_CHECKED", name, part,
                            f"{name}: {part} were not read, so anything in them was not "
                            f"checked"))
    for target in missing:
        out.append(_finding("INPUT_NOT_FOUND", name, target,
                            f"include target {target} was not found; that part of the "
                            f"manuscript was not checked"))
    folded = fold(text)

    unquoted = _QUOTED.sub(" ", folded)
    for row in terms or []:
        banned = row.get("never_use") or []
        if isinstance(banned, str):
            banned = [banned]
        for term in banned:
            if not str(term).strip():
                continue
            rx = re.compile(rf"(?<![A-Za-z0-9]){re.escape(str(term))}(?![A-Za-z0-9])", re.I)
            n = len(rx.findall(unquoted))
            if n:
                out.append(_finding("TERM_NEVER_USE_PRESENT", "terms.yml", row.get("canonical"),
                                    f"never_use term {term!r} appears {n} time(s) in {name} "
                                    f"outside a quotation"))

    sections = split_sections(folded, manuscript.suffix)
    if gaps is not None:
        _check_dissent(gaps, sections, name, out)

    if figures is None:
        return
    everywhere = [_split(t) for t in numbers(folded)]
    key_pool: list[tuple[str, str]] = []
    for row in figures:
        for entry in _list_field(row, "key_numbers", "figures.yml", out):
            for token in numbers(fold(str(entry))):
                key_pool.append(_split(token))
                if not _covered(token, everywhere):
                    out.append(_finding("KEY_NUMBER_NOT_IN_PROSE", "figures.yml", row.get("id"),
                                        f"key number {token} from {str(entry)!r} does not "
                                        f"appear in {name}"))

    if "results" not in sections:
        out.append(_finding("SECTION_NOT_CHECKED", name, "results",
                            "no Results section was found, so the number trace did not run"))
        return
    tables = " ".join(m.group(0) for m in _TABLE_ENV.finditer(folded))
    cover = key_pool + [_split(t) for t in numbers(sections["results"])] \
        + [_split(t) for t in numbers(tables)] \
        + [_split(t) for t in numbers(sections.get("methods", ""))]
    for section in TRACED:
        if section not in sections:
            out.append(_finding("SECTION_NOT_CHECKED", name, section,
                                f"no {section} section was found; its numbers were not traced"))
            continue
        seen: set[str] = set()
        for token in numbers(_trace_text(sections[section])):
            if token in seen or not _checkable(token):
                continue
            seen.add(token)
            if not _covered(token, cover):
                out.append(_finding("NUMBER_NOT_IN_LEDGER", name, section,
                                    f"{token} is quoted in the {section} but appears in no "
                                    f"key_numbers entry, in no table, and not in the Methods "
                                    f"or the Results"))


def _check_conflicts(rows: list[dict], out: list[dict]) -> None:
    for r in rows:
        if r.get("type") not in CONFLICT_TYPES:
            between = ", ".join(str(x) for x in r.get("between") or [])
            out.append(_finding("CONFLICT_TYPE_INVALID", "changes.yml", between or None,
                                f"conflict type is {r.get('type')!r}; allowed: view, severity, "
                                f"existence, direction"))


def not_checked(paper_dir: Path) -> list[str]:
    """The ledger files that are absent, so nothing in them was checked."""
    return [n for n in FILES if not (Path(paper_dir) / n).is_file()]


def rules_not_run(paper_dir: Path) -> list[tuple[str, tuple[int, ...]]]:
    """(absent file, consistency rules that could not run without it), for the files the
    rules need. An absent optional file (changes.yml) is not here."""
    return [(n, r) for n, r in RULES_NEEDING.items() if not (Path(paper_dir) / n).is_file()]


def _rules_text(rules: tuple[int, ...]) -> str:
    return "rules " + ", ".join(str(r) for r in rules)


def audit(paper_dir: Path, manuscript: Path | None) -> list[dict]:
    """Return every rule fault found in the ledger files of `paper_dir`.

    Each finding is {"code", "file", "id", "message"}. An empty list means no fault was found
    in the files that exist; call `not_checked()` for the files that do not.
    """
    if yaml is None:
        raise NotChecked("not checked: install pyyaml")
    paper_dir = Path(paper_dir)
    if not paper_dir.is_dir():
        raise NotChecked(f"not checked: {paper_dir} is not a directory")

    out: list[dict] = []
    claims = _load(paper_dir, "claims.yml", "claims", out)
    figures = _load(paper_dir, "figures.yml", "figures", out)
    terms = _load(paper_dir, "terms.yml", "terms", out)
    gaps = _load(paper_dir, "gap.yml", "gaps", out)
    changes = _load(paper_dir, "changes.yml", "comments", out)

    claim_ids = None if claims is None else {str(c.get("id")) for c in claims}
    figure_ids = None if figures is None else {str(f.get("id")) for f in figures}

    if claims is not None:
        _check_claims(claims, figure_ids, out)
        _check_design(paper_dir, claims, out)
    if terms is not None:
        symbols = _load(paper_dir, "terms.yml", "symbols", out, required=False)
        _check_symbols(terms, symbols or [], out)
    if figures is not None:
        _check_figures(figures, claim_ids, out)
    if gaps is not None:
        _check_gaps(gaps, claims, out)
    if changes is not None:
        try:
            top = yaml.safe_load((paper_dir / "changes.yml").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            top = None
        _check_changes(changes, claim_ids, figure_ids, out,
                       top.get("decision") if isinstance(top, dict) else None)
        conflicts = _load(paper_dir, "changes.yml", "conflicts", out, required=False)
        if conflicts:
            _check_conflicts(conflicts, out)
    if manuscript is not None:
        manuscript = Path(manuscript)
        if not manuscript.is_file():
            raise NotChecked(f"not checked: manuscript {manuscript} was not found")
        _check_manuscript(figures, terms, gaps, manuscript, out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper_dir", help="the .paper directory")
    ap.add_argument("--manuscript", help="the manuscript root file (.tex, .md, .txt, .docx)")
    ap.add_argument("--json", help="write the findings to this file")
    args = ap.parse_args()

    if args.json:
        problem = json_target_problem(args.json)
        if problem:
            print(problem, file=sys.stderr)
            return 2

    paper_dir = Path(args.paper_dir)
    if not (paper_dir / "claims.yml").is_file() and (paper_dir / ".paper").is_dir():
        paper_dir = paper_dir / ".paper"         # given the manuscript folder; use its ledger
    manuscript = Path(args.manuscript) if args.manuscript else None
    try:
        findings = audit(paper_dir, manuscript)
    except NotChecked as e:
        print(e)
        return 3
    absent = not_checked(paper_dir)
    unrun = rules_not_run(paper_dir)
    if "claims.yml" in absent and "changes.yml" in absent:
        print("not checked: claims.yml is absent, so there is no claim ledger to check "
              f"({_rules_text(RULES_NEEDING['claims.yml'])} did not run)")
        return 3

    print(f"checked {paper_dir}" + (f" against {manuscript}" if manuscript else "") + "\n")
    faults = [f for f in findings if f["code"] not in INFO_CODES | NOTE_CODES]
    by_code: dict[str, int] = {}
    for f in faults:
        by_code[f["code"]] = by_code.get(f["code"], 0) + 1
        where = f["file"] + (f" {f['id']}" if f["id"] else "")
        print(f"  {f['code']:<30} {where}: {f['message']}")
    if faults:
        print()
        for code in sorted(by_code):
            print(f"  {by_code[code]:>3}  {code}")
    for name in absent:
        if name in RULES_NEEDING:
            print(f"  not checked: {name} is absent; {_rules_text(RULES_NEEDING[name])} "
                  f"did not run")
        else:
            print(f"  not checked: {name} is absent (optional: {OPTIONAL_FILES.get(name, '')})")
    for f in findings:
        if f["code"] in INFO_CODES:
            print(f"  not checked: {f['message']}")
        elif f["code"] in NOTE_CODES:
            print(f"  note: {f['message']}")
    if manuscript is None:
        print("  not checked: numbers and never_use terms in the manuscript (rules 3 and 7) "
              "and dissenting studies in the Discussion (rule 10); no --manuscript")
    print("  " + _NOT_COVERED)
    print(f"\n{len(faults)} finding(s). This is evidence, not a verdict: the reference file "
          f"decides each one.")

    if args.json:
        err = write_json_file(args.json, json.dumps(
            {"findings": findings, "not_checked": absent,
             "rules_not_run": {n: list(r) for n, r in unrun}}, indent=2))
        if err:
            print(err, file=sys.stderr)
            return 2
    if faults:
        return 1
    if unrun:                       # a rule's file is missing: those rules did not run
        return 3
    # Nothing wrong was found, but a section or an included file was not read. That is not
    # a clean result, so it does not get the clean exit code.
    return 3 if any(f["code"] in INFO_CODES for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
