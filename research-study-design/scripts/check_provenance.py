#!/usr/bin/env python3
"""Check the provenance rules of `.paper/runs.yml`, `design.yml` and `figures.yml`.

The rules are Consistency Rules 1 to 6 in references/study-memory.md. Rules 7 and 8 need a
reader and are not checked here. An agent that checks by reading drifts over a long project;
this script gives the same answer every time. It is read-only: it edits no manuscript and no
`.paper` file, and runs nothing. The only file it ever writes is the one named by `--json`,
which is refused (exit 2, nothing written) when it is inside a `.paper` folder or already exists.

    python3 check_provenance.py <project folder, or its .paper folder> [--json findings.json]

Rules: 1 every `final` figure names runs, and each exists; 2 each such run has status valid;
3 each recorded file of a valid run still has its recorded hash; 4 failed, excluded and
superseded runs carry a reason, a superseded run names an existing run, and status, kind and
id are well formed (`status` and `kind` are compared after strip and lower-casing, and a
figure `status` must be draft, final or regenerate); 5 `frozen_on` is not later than the first production run; 6 every
amendment dated after the first production run is `post hoc`, or carries `results_seen: false`
with its reason. An amendment's `kind`, when given, is `choice` or `correction`, and a
correction names the check that forced it.

Needs PyYAML. Without it the script prints "not checked: install pyyaml" and exits 3.
`runs.yml` is required. `figures.yml` and `design.yml` are optional: when one is absent, the
rules that need it (1, 2 and 5, 6) did not run. The output and `--json` (`rules_not_run`) say
so, and that alone does not change the exit code. A top-level `release:` block in `runs.yml` is
tolerated and ignored.

A `valid` run that a `final` figure rests on must close the chain. A recorded file that is
missing or cannot be read (FILE_NOT_FOUND) and a row whose hash is not 64 hexadecimal
characters (HASH_MISSING) are findings. A run with no inputs (RUN_NO_INPUTS) and a run with
neither code files nor a commit (RUN_NO_CODE) are "not checked". For a valid run that no final
figure rests on, a missing file and a missing hash are "not checked", not findings. In every
case a recorded path that is absolute or leaves the project with `..` is not read and is "not
checked", and so is a valid run that records no files at all (RUN_NO_FILES). A YAML file that
cannot be parsed, is empty, or lacks its top-level list is reported as unparseable and nothing
in it counts as checked. Any unexpected error prints one line "not checked: internal error:
..." and exits 3, never 1.

An amendment with `results_seen: false` needs its reason in a `reason` field; the ordinary
`why` field does not count.

Each finding has a code, the file, the row id and a message that says what to do. This is
evidence, not a verdict: the reference file decides what to do about a finding.

Exit code 0 no findings and nothing not checked (the rules that ran). 1 at least one finding.
2 could not start: `--json` refused (inside a `.paper` folder, or the path exists, or it cannot
be written). 3 no findings, but something was not checked, or runs.yml is absent or cannot be
parsed: not a clean result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:                      # reported in main(); never a silent pass
    yaml = None

STATUSES = ("valid", "superseded", "failed", "excluded")
KINDS = ("pilot", "check", "production")
TIMINGS = ("changed before analysis", "post hoc")
NEEDS_REASON = ("failed", "excluded", "superseded")
FIGURE_STATUSES = ("draft", "final", "regenerate")
RULES_NEEDING = {"figures.yml": (1, 2), "design.yml": (5, 6)}
_HASH = re.compile(r"^[0-9a-fA-F]{64}$")


def _finding(code, file, row_id, message):
    return {"code": code, "file": file, "id": None if row_id is None else str(row_id),
            "message": message}


def _rules_text(rules):
    return ("rules " if len(rules) > 1 else "rule ") + ", ".join(str(r) for r in rules)


def _day(value):
    """A date from a YAML date, datetime or YYYY-MM-DD string; None when unreadable."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}", value.strip()):
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            return None
    return None


def _norm(value):
    """A string compared after strip and lower; anything else as it is."""
    return value.strip().lower() if isinstance(value, str) else value


def _outside_project(rel):
    """True for an absolute path, or one that leaves the project folder with `..`."""
    text = str(rel).replace("\\", "/")
    if text.startswith("/") or re.match(r"^[A-Za-z]:", text) or text.startswith("~"):
        return True
    depth = 0
    for part in text.split("/"):
        if part in ("", "."):
            continue
        depth += -1 if part == ".." else 1
        if depth < 0:
            return True
    return False


def _blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def _load(paper: Path, name: str, key, notes):
    """(data, status): status is 'ok', 'absent' or 'broken' (a note says why)."""
    path = paper / name
    if not path.is_file():
        return None, "absent"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:             # YAMLError, ValueError (2026-02-30), OSError, ...
        why = (str(e).splitlines() or [type(e).__name__])[0]
        notes.append(_finding("FILE_UNPARSEABLE", name, None,
                              f"{name} cannot be parsed as YAML ({why}); "
                              "nothing in it was checked. Fix the file and run again."))
        return None, "broken"
    if not isinstance(data, dict):
        notes.append(_finding("FILE_UNPARSEABLE", name, None,
                              f"{name} is empty or is not a mapping; nothing in it was "
                              "checked."))
        return None, "broken"
    if key and not isinstance(data.get(key), list):
        notes.append(_finding("FILE_UNPARSEABLE", name, None,
                              f"{name} has no `{key}` list; nothing in it was checked."))
        return None, "broken"
    return data, "ok"


def _rows(rows, name, out):
    """The rows that are mappings, with a finding for each that is not."""
    good = []
    for i, row in enumerate(rows, 1):
        if isinstance(row, dict):
            good.append(row)
        else:
            out.append(_finding("ROW_NOT_MAPPING", name, f"row {i}",
                                f"row {i} is not a mapping (`key: value` lines); it was not "
                                "checked. Rewrite it as a row."))
    return good


def _file_entries(run, field, rid, out):
    """(path, hash) pairs of `inputs`, `outputs` or `code.files`, reporting malformed ones."""
    if field == "files":
        code = run.get("code")
        if code is None:
            return []
        if not isinstance(code, dict):
            out.append(_finding("FIELD_NOT_MAPPING", "runs.yml", rid,
                                "`code` is not a mapping (commit, dirty, files); its files "
                                "were not checked."))
            return []
        value, label = code.get("files"), "code.files"
    else:
        value, label = run.get(field), field
    if value is None:
        return []
    if not isinstance(value, list):
        out.append(_finding("FIELD_NOT_LIST", "runs.yml", rid,
                            f"`{label}` is not a list; write one `- path:` and `sha256:` per "
                            "file. It was not checked."))
        return []
    pairs = []
    for entry in value:
        if isinstance(entry, dict) and isinstance(entry.get("path"), str) and entry["path"].strip():
            pairs.append((entry["path"], entry.get("sha256")))
        else:
            out.append(_finding("ENTRY_MALFORMED", "runs.yml", rid,
                                f"an entry of `{label}` has no `path`; write `- path:` and "
                                "`sha256:`. It was not checked."))
    return pairs


def _final_run_ids(figs):
    """The ids of the runs that the `final` rows of figures.yml name (as plain ids)."""
    out = set()
    for fig in figs.get("figures", []):
        if not isinstance(fig, dict) or _norm(fig.get("status")) != "final":
            continue
        value = fig.get("runs")
        names = [value] if isinstance(value, str) else (value if isinstance(value, list) else [])
        out.update(str(v).strip() for v in names if isinstance(v, (str, int)) and str(v).strip())
    return out


def _sha256(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(paper: Path) -> dict:
    """Run rules 1 to 6. Returns findings, not_checked (strings), not_checked_items (dicts),
    rules_not_run ({file: [rule, ...]}) and fatal (a message when nothing could run)."""
    paper = Path(paper)
    root = paper.parent
    findings: list = []
    notes: list = []                      # things that were not checked, as finding dicts
    unrun: dict = {}

    def result(fatal=None):
        return {"findings": findings, "not_checked": [n["message"] for n in notes],
                "not_checked_items": notes, "rules_not_run": unrun, "fatal": fatal}

    runs_data, st = _load(paper, "runs.yml", "runs", notes)
    if st == "absent":
        return result("not checked: no runs.yml in " + str(paper))
    if st == "broken":
        unrun["runs.yml"] = [1, 2, 3, 4, 5, 6]
        return result(f"not checked: runs.yml is unparseable; rules 1 to 6 did not run "
                      f"({notes[-1]['message']})")

    runs = _rows(runs_data["runs"], "runs.yml", findings)
    by_id: dict = {}
    for run in runs:
        rid = run.get("id")
        if _blank(rid):
            findings.append(_finding("RUN_NO_ID", "runs.yml", None,
                                     "a run has no `id`; give each run a unique id."))
            continue
        rid = str(rid)
        if rid in by_id:
            findings.append(_finding("RUN_DUPLICATE_ID", "runs.yml", rid,
                                     f"id {rid} is used by more than one run; ids are used "
                                     "once. Rename the later row; never reuse an id."))
        else:
            by_id[rid] = run

    # Rule 4 (and the shape of status and kind).
    for rid, run in by_id.items():
        raw_status = run.get("status")
        status = _norm(raw_status)
        if status not in STATUSES:
            findings.append(_finding("RUN_STATUS_INVALID", "runs.yml", rid,
                                     f"status is {raw_status!r}; use one of valid, superseded, "
                                     "failed, excluded."))
        if _norm(run.get("kind")) not in KINDS:
            findings.append(_finding("RUN_KIND_INVALID", "runs.yml", rid,
                                     f"kind is {run.get('kind')!r}; use one of pilot, check, "
                                     "production."))
        if status in NEEDS_REASON and (not isinstance(run.get("reason"), str)
                                       or not run["reason"].strip()):
            findings.append(_finding("RUN_NO_REASON", "runs.yml", rid,
                                     f"a {status} run needs a non-empty `reason`; write why "
                                     "it is not valid. Never delete the row."))
        if status == "superseded":
            by = run.get("superseded_by")
            if _blank(by) or str(by) not in by_id:
                findings.append(_finding("RUN_SUPERSEDED_BY_UNKNOWN", "runs.yml", rid,
                                         f"superseded_by is {by!r}, which is not a run in "
                                         "runs.yml; name the run that replaced this one "
                                         "(record it first)."))

    figs, fst = _load(paper, "figures.yml", "figures", notes)
    behind_final = _final_run_ids(figs) if fst == "ok" else set()

    # Rule 3. For a run that a final figure rests on, a recorded file that is gone, a row with
    # no hash, a run with no inputs, and a run with neither code files nor a commit are the
    # chain failing to close: the first two are findings, the last two are not checked.
    for rid, run in by_id.items():
        if _norm(run.get("status")) != "valid":
            continue
        final = rid in behind_final
        gap = findings if final else notes
        recorded_any = False
        seen = {"inputs": 0, "files": 0}
        for field in ("inputs", "outputs", "files"):
            for rel, recorded in _file_entries(run, field, rid, findings):
                recorded_any = True
                seen[field] = seen.get(field, 0) + 1
                if _outside_project(rel):
                    notes.append(_finding("PATH_OUTSIDE_PROJECT", "runs.yml", rid,
                                          f"run {rid}, {rel} is an absolute path or leaves the "
                                          "project folder; it was not read. Record the run "
                                          "again with paths inside the project."))
                    continue
                if not isinstance(recorded, str) or not _HASH.match(recorded.strip()):
                    gap.append(_finding("HASH_MISSING", "runs.yml", rid,
                                          f"no hash recorded: run {rid}, {rel} (the recorded "
                                          "value is not 64 hexadecimal characters); record the "
                                          "run again with record_run.py"))
                    continue
                target = root / rel
                if not target.is_file():
                    gap.append(_finding("FILE_NOT_FOUND", "runs.yml", rid,
                                          f"file not found: run {rid}, {rel}; restore it or "
                                          "record a new run"))
                    continue
                try:
                    now = _sha256(target)
                except OSError as e:
                    gap.append(_finding("FILE_NOT_FOUND", "runs.yml", rid,
                                          f"file not found: run {rid}, {rel} cannot be read "
                                          f"({e.strerror})"))
                    continue
                if now != recorded.strip().lower():
                    findings.append(_finding("FILE_CHANGED", "runs.yml", rid,
                                             f"{rel} changed after run {rid} (field {field}); "
                                             "the run is stale. Rerun it, or record a new run "
                                             "and point the figure at it."))

        if not recorded_any:
            notes.append(_finding("RUN_NO_FILES", "runs.yml", rid,
                                  f"run {rid} records no files, so nothing about it could be "
                                  "verified; record it with record_run.py, with its inputs, "
                                  "code and outputs"))
        elif final:
            if not seen["inputs"]:
                notes.append(_finding("RUN_NO_INPUTS", "runs.yml", rid,
                                      f"run {rid} records no inputs, so a final figure rests on a "
                                      "run whose inputs cannot be verified; record the run again "
                                      "with --inputs"))
            code = run.get("code")
            commit = code.get("commit") if isinstance(code, dict) else None
            if not seen["files"] and _blank(commit):
                notes.append(_finding("RUN_NO_CODE", "runs.yml", rid,
                                      f"run {rid} records neither code files nor a commit, so "
                                      "the code behind a final figure cannot be identified; "
                                      "record the run again with --code"))

    # Rules 1 and 2.
    if fst != "ok":
        unrun["figures.yml"] = list(RULES_NEEDING["figures.yml"])
    else:
        for fig in _rows(figs["figures"], "figures.yml", findings):
            fid = fig.get("id")
            fstatus = _norm(fig.get("status"))
            if fstatus not in FIGURE_STATUSES:
                findings.append(_finding("FIGURE_STATUS_INVALID", "figures.yml", fid,
                                         f"status is {fig.get('status')!r}; use one of draft, "
                                         "final, regenerate. The figure was not checked."))
                continue
            if fstatus != "final":
                continue
            value = fig.get("runs")
            if isinstance(value, str) and value.strip():
                findings.append(_finding("FIELD_NOT_LIST", "figures.yml", fid,
                                         "`runs` is a plain string; write a list, for "
                                         f"example runs: [\"{value.strip()}\"]. It was read as "
                                         "one id."))
                names = [value.strip()]
            elif isinstance(value, list):
                names = []
                for v in value:
                    if isinstance(v, (dict, list)):
                        findings.append(_finding("ENTRY_MALFORMED", "figures.yml", fid,
                                                 "an entry of `runs` is not a run id; write "
                                                 "ids such as \"R3\"."))
                    elif not _blank(v):
                        names.append(str(v))
            else:
                if value is not None:
                    findings.append(_finding("FIELD_NOT_LIST", "figures.yml", fid,
                                             "`runs` is not a list; write a list of run ids."))
                names = []
            if not names:
                findings.append(_finding("FIGURE_NO_RUN", "figures.yml", fid,
                                         "a final figure names no run; add `runs: [\"R3\"]` "
                                         "with the run that made it, or set status to draft."))
            for n in names:
                if n not in by_id:
                    findings.append(_finding("FIGURE_RUN_UNKNOWN", "figures.yml", fid,
                                             f"run {n} is not in runs.yml; correct the id or "
                                             "record the run."))
                elif _norm(by_id[n].get("status")) != "valid":
                    findings.append(_finding("FIGURE_RUN_NOT_VALID", "figures.yml", fid,
                                             f"rests on run {n}, whose status is "
                                             f"{by_id[n].get('status')!r}; point the figure at "
                                             "a valid run, or rerun and record a new one."))

    # Rules 5 and 6.
    design, dst = _load(paper, "design.yml", None, notes)
    if dst != "ok":
        unrun["design.yml"] = list(RULES_NEEDING["design.yml"])
    else:
        prod = [str(r.get("id")) for r in by_id.values() if _norm(r.get("kind")) == "production"]
        days = []
        for rid in prod:
            d = _day(by_id[rid].get("date"))
            if d is None:
                notes.append(_finding("DATE_UNREADABLE", "runs.yml", rid,
                                      f"date of production run {rid} is not YYYY-MM-DD; the "
                                      "first production run may be wrong. Correct the date."))
            else:
                days.append(d)
        first = min(days) if days else None
        frozen = design.get("frozen_on")
        if _blank(frozen):
            if prod:
                findings.append(_finding("DESIGN_NOT_FROZEN", "design.yml", None,
                                         "a production run exists but design.yml has no "
                                         "`frozen_on`; nothing in it may be called planned. "
                                         "Record the freeze date, or say it was never frozen."))
        elif first is not None:
            fd = _day(frozen)
            if fd is None:
                notes.append(_finding("DATE_UNREADABLE", "design.yml", None,
                                      "frozen_on is not YYYY-MM-DD; rule 5 not checked."))
            elif fd > first:
                findings.append(_finding("FREEZE_AFTER_FIRST_RUN", "design.yml", None,
                                         f"frozen_on {fd} is after the first production run "
                                         f"({first}); the design was not frozen before the "
                                         "runs. Do not move the date: say so in Methods."))
        ams = design.get("amendments")
        if ams is not None and not isinstance(ams, list):
            findings.append(_finding("FIELD_NOT_LIST", "design.yml", None,
                                     "`amendments` is not a list; write one row per "
                                     "amendment."))
            ams = []
        for am in _rows(ams or [], "design.yml", findings):
            aid = am.get("id")
            timing = am.get("timing")
            if timing not in TIMINGS:
                findings.append(_finding("AMENDMENT_TIMING_INVALID", "design.yml", aid,
                                         f"timing is {timing!r}; use `changed before "
                                         "analysis` or `post hoc`."))
            if am.get("results_seen") is False and _blank(am.get("reason")):
                findings.append(_finding("AMENDMENT_NO_REASON", "design.yml", aid,
                                         "`results_seen: false` needs the reason, in a "
                                         "`reason` field: say why no result had been opened."))
            ad = _day(am.get("date"))
            if ad is None:
                findings.append(_finding("AMENDMENT_NO_DATE", "design.yml", aid,
                                         "the amendment has no readable date (YYYY-MM-DD); "
                                         "add the date it was made."))
            kind = am.get("kind")
            if kind is not None and str(kind).strip().lower() not in ("choice", "correction"):
                findings.append(_finding("AMENDMENT_KIND_INVALID", "design.yml", aid,
                                         f"kind is {kind!r}; use `choice` for a pick among "
                                         "alternatives, or `correction` for a fault a check "
                                         "exposed."))
            elif (kind is not None and str(kind).strip().lower() == "correction"
                  and not str(am.get("forced_by") or "").strip()):
                findings.append(_finding("AMENDMENT_CORRECTION_NO_CHECK", "design.yml", aid,
                                         "kind is `correction` but `forced_by` is empty; name "
                                         "the check that exposed the fault, or record the "
                                         "amendment as a `choice`."))
            if ad is None:
                pass
            elif (first is not None and ad > first and timing != "post hoc"
                  and am.get("results_seen") is not False):
                # Data can be collected and not yet opened. The record must then say so.
                findings.append(_finding("AMENDMENT_NOT_POST_HOC", "design.yml", aid,
                                         f"dated {ad}, after the first production run "
                                         f"({first}), but timing is {timing!r}; set timing to "
                                         "`post hoc`, or record `results_seen: false` with "
                                         "the reason if no result had been opened."))
    return result()


def _paper_dir(target: Path) -> Path:
    if (target / ".paper").is_dir():
        return target / ".paper"
    return target


def _json_refusal(path):
    """Why `--json PATH` may not be written, or None."""
    p = Path(os.path.abspath(path))
    if any(part == ".paper" for part in p.parts):
        return f"--json {path}: refused, the path is inside a .paper folder, which holds the record"
    if os.path.lexists(p):
        return f"--json {path}: refused, the path already exists and is never overwritten"
    return None


def _write_json(path, res):
    text = json.dumps({"findings": res["findings"], "not_checked": res["not_checked_items"],
                       "rules_not_run": res["rules_not_run"]}, indent=2)
    with open(path, "x", encoding="utf-8") as fh:     # "x": never over an existing file
        fh.write(text)


def main(argv=None) -> int:
    try:
        return _main(argv)
    except SystemExit:
        raise
    except BaseException as e:                        # never exit 1 (findings) by accident
        print(f"not checked: internal error: {type(e).__name__}: {e}")
        return 3


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="the project folder, or its .paper folder")
    ap.add_argument("--json", help="write the findings to this new file; refused (exit 2) when "
                    "the path is inside a .paper folder or already exists. It is the only file "
                    "this script writes")
    args = ap.parse_args(argv)

    if args.json:
        why = _json_refusal(args.json)
        if why:
            print(why, file=sys.stderr)
            return 2
    if yaml is None:
        print("not checked: install pyyaml")
        return 3
    paper = _paper_dir(Path(args.target))
    res = audit(paper)
    if args.json:
        try:
            _write_json(args.json, res)
        except OSError as e:
            print(f"--json {args.json}: refused, cannot write it ({e.strerror or e})",
                  file=sys.stderr)
            return 2
    if res["fatal"]:
        print(res["fatal"])
        print("result: not checked (exit 3): not a clean result")
        return 3

    print(f"checked {paper}\n")
    for f in res["findings"]:
        where = f["file"] + (f" {f['id']}" if f["id"] else "")
        print(f"  {f['code']:<26} {where}: {f['message']}")
    if res["findings"]:
        print()
    for name, rules in res["rules_not_run"].items():
        print(f"  not checked: {name} is absent or unreadable; {_rules_text(rules)} did "
              "not run")
    for n in res["not_checked_items"]:
        print(f"  not checked: {n['message']}")
    print("  not checked by this script: rules 7 and 8 of study-memory.md (they need a reader).")
    nf, nn = len(res["findings"]), len(res["not_checked_items"])
    if nf:
        print(f"\nresult: {nf} finding(s) (exit 1). This is evidence, not a verdict.")
        return 1
    if nn:
        print("\nresult: no findings, but something was not checked (exit 3): not a clean "
              "result.")
        return 3
    print("\nresult: no findings, nothing not checked in the rules that ran (exit 0).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
