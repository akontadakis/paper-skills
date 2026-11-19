#!/usr/bin/env python3
"""Append one run row to `.paper/runs.yml`, or mark an earlier run as replaced.

The row format is in references/study-memory.md (runs.yml); how to use this script is in
references/run-record.md. The script runs nothing, computes the SHA-256 hash of every input,
code and output file, reads the version-control commit when there is one, and writes only
`.paper/runs.yml`. It edits no manuscript and no other file.

Record a run:

    python3 record_run.py --paper .paper --id R3 --kind production \\
        --purpose "production run, 0.5 m grid" \\
        --command "python code/run_all.py --config configs/main_500mm.yml" \\
        --inputs configs/main_500mm.yml inputs/weather --code code --outputs results/annual.csv \\
        --tool "<name>=<the version string the tool prints>" [--seed 7] [--status valid] \\
        [--hardware TEXT] [--wall-time TEXT] [--reason TEXT] [--superseded-by R9] \\
        [--date 2026-08-12]

One row holds one `seed`: record one row per seed. A `production` run recorded with no `--tool`
prints a warning.

Mark a run as replaced, once the replacing run is recorded:

    python3 record_run.py --paper .paper --supersede R1 --by R3 --reason "grid changed"

This is the only change the script makes to an existing row. It sets `status: superseded`,
`superseded_by` and `reason` on the row, and the `updated:` line; every other byte of the file
is kept. It refuses when either id is not in the file, when the row is already superseded or is
not `valid`, when the row already has a `reason` (edit that row by hand), when `--by` names
the same run, and when the `--by` run is not `valid`. The row must be written as `- id: ...`.

The project root is the folder that holds `.paper`. Paths are stored relative to it, with
forward slashes. A folder stands for every file under it, sorted; `.git`, `.paper`, `.venv`,
`venv`, `__pycache__`, `node_modules` and `.DS_Store` are skipped. A folder that cannot be read
is a refusal, never a silent gap.

`code.commit` is the HEAD commit. `code.dirty` is true when `git status` reports a change
(untracked files included) in a `--code` path, or when a git-ignored file is among the code
files that were hashed. It is null when no `--code` path is given, without git, outside a work
tree, and in a repository with no commit: the script did not look, and writes `null`, not
`false`.

A new file gets `version: 1`, an `updated:` date and a `runs:` list. In an existing file the
text is kept byte for byte, except the value of the top-level `updated:` line; the row is added
at the end of the `runs:` list, which must be the last top-level key, at the indent the existing
list items already use (mixed indents are refused). Any other top-level block, such as
`release:`, stays as it is, and belongs above `runs:`.

The write is safe. The whole new text is built and encoded first, written to a temporary file
beside the record, flushed, synced and moved over `runs.yml`, so a failure leaves the old file
as it was. A lock file `runs.yml.lock` beside the record is held for the whole read, modify and
write, and removed afterwards, so parallel runs do not lose a row. When PyYAML is installed, the
new text is parsed before it replaces the file and the script refuses unless every earlier row
reads back unchanged; without PyYAML that check is skipped (the script needs only the standard
library). `--paper` must be a folder named `.paper`. A symlinked folder, whether found inside a
folder or named directly, is not followed (a warning names it); a symlinked file is hashed
through its target (a warning names the link).

Exit code 0 the row was written, or the run was marked as replaced. 2 the request was refused
(bad argument, unknown or unreadable path, duplicate id, unknown run to supersede, `runs:` not
last, tool version empty, text that cannot be written as UTF-8, the lock could not be taken);
the file is left unchanged. The script never exits 1 and never ends in a traceback.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

try:                                        # POSIX only; a lock file is the fallback
    import fcntl
except ImportError:
    fcntl = None

LOCK_WAIT = 30.0                            # seconds to wait for the lock
KINDS = ("pilot", "check", "production")
STATUSES = ("valid", "superseded", "failed", "excluded")
SKIP_DIRS = {".git", ".paper", ".venv", "venv", "__pycache__", "node_modules"}
SKIP_FILES = {".DS_Store"}
_TOP_KEY = re.compile(r"^([A-Za-z_][\w-]*)\s*:(.*)$")
_ID_LINE = re.compile(r"""^\s*-\s+id\s*:\s*(?:"([^"]*)"|'([^']*)'|([^\s#]+))""")


class Refused(Exception):
    """The request cannot be recorded. The message says what to change."""


# json.dumps writes these raw, and YAML either rejects them (DEL, C1 controls) or reads them
# back as something else (NEL and the line separators become line breaks or spaces).
_NEEDS_ESCAPE = re.compile("[\x7f-\x9f\u2028\u2029\ufeff\ufffe\uffff]")


def q(value) -> str:
    """A double-quoted YAML scalar that reads back as the same text. JSON strings are YAML
    double-quoted scalars, except for the characters escaped here. A lone surrogate cannot be
    written in UTF-8 and is refused."""
    text = str(value)
    if re.search("[\ud800-\udfff]", text):
        raise Refused(f"text cannot be written as UTF-8 (a byte that is not valid text): "
                      f"{text!r}")
    return _NEEDS_ESCAPE.sub(lambda m: "\\u%04X" % ord(m.group()),
                             json.dumps(text, ensure_ascii=False))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError as e:
        raise Refused(f"cannot read {path} to hash it ({e.strerror or e}); nothing was written")
    return h.hexdigest()


def expand(args: list[str], root: Path, label: str, warnings: list) -> list[str]:
    """Project-relative, forward-slash paths of every file the arguments name."""
    found: list[str] = []
    for arg in args:
        p = Path(os.path.abspath(arg))
        try:
            gone = not p.exists() and not p.is_symlink()
            is_dir = p.is_dir()
        except OSError as e:
            raise Refused(f"{label}: cannot read {arg} ({e.strerror or e}); nothing was written")
        if gone:
            raise Refused(f"{label}: path not found: {arg}")
        rel = _under(p, root, arg)
        if is_dir and p.is_symlink():
            warnings.append(f"{label}: {rel} is a symlink to a folder; it was not followed, so "
                            "its files are not recorded")
        elif is_dir:
            before = len(found)

            def unreadable(e, label=label):
                raise Refused(f"{label}: cannot read the folder {e.filename} "
                              f"({e.strerror or e}); nothing was written")

            for dirpath, dirnames, filenames in os.walk(p, onerror=unreadable):
                keep = []
                for d in sorted(dirnames):
                    if d in SKIP_DIRS:
                        continue
                    full = Path(dirpath) / d
                    if full.is_symlink():
                        warnings.append(f"{label}: {_under(full, root, arg)} is a symlink to a "
                                        "folder; it was not followed, so its files are not "
                                        "recorded")
                    else:
                        keep.append(d)
                dirnames[:] = keep
                for name in sorted(filenames):
                    if name in SKIP_FILES:
                        continue
                    full = Path(dirpath) / name
                    shown = _under(full, root, arg)
                    if full.is_symlink():
                        warnings.append(f"{label}: {shown} is a symlink to "
                                        f"{os.path.realpath(full)}; the hash is that of the "
                                        "target file")
                    found.append(shown)
            if len(found) == before:
                warnings.append(f"{label}: the folder {arg} holds no files, so it adds none")
        else:
            if p.is_symlink():
                warnings.append(f"{label}: {rel} is a symlink to {os.path.realpath(p)}; the "
                                "hash is that of the target file")
            found.append(rel)
    return sorted(set(found))


def _under(p: Path, root: Path, shown: str) -> str:
    try:
        rel = p.relative_to(root)
    except ValueError:
        raise Refused(f"path is outside the project folder {root}: {shown}")
    return rel.as_posix()


def git_state(root: Path, code_args: list[str], code_files: list[str]):
    """(commit, dirty). (None, None) when there is no usable git. `dirty` is None when no code
    path was given: nothing was looked at, so nothing is claimed."""
    if shutil.which("git") is None:
        return None, None

    def git(*a):
        return subprocess.run(["git", *a], cwd=str(root), capture_output=True, text=True)

    try:
        if git("rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
            return None, None
        head = git("rev-parse", "--verify", "-q", "HEAD")
    except OSError:
        return None, None
    if head.returncode != 0:
        return None, None
    commit = head.stdout.strip()
    specs = [_under(Path(os.path.abspath(a)), root, a) or "." for a in code_args]
    if not specs:
        return commit, None
    st = git("status", "--porcelain", "--untracked-files=all", "--", *specs)
    if st.returncode != 0:
        return commit, None
    if st.stdout.strip():
        return commit, True
    # An ignored file is in no commit, so the commit does not identify it. One that is hashed
    # as code makes the run dirty. Ignored folders that are skipped are not code files.
    ign = git("ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", *specs)
    if ign.returncode != 0:
        return commit, None
    return commit, bool(set(ign.stdout.split("\0")) & set(code_files))


def parse_tool(text: str) -> tuple[str, str]:
    name, sep, version = text.partition("=")
    name, version = name.strip(), version.strip()
    if not sep or not name:
        raise Refused(f"--tool {text!r}: write NAME=VERSION")
    if not version:
        raise Refused(f"--tool {text!r}: the version is empty. Run the tool's own version "
                      "command and copy the string it prints.")
    return name, version


def build_row(a, root: Path, warnings: list):
    inputs = expand(a.inputs, root, "--inputs", warnings)
    code = expand(a.code, root, "--code", warnings)
    outputs = expand(a.outputs, root, "--outputs", warnings)
    if not outputs and a.status != "failed":
        raise Refused("--outputs is required unless --status is failed")
    tools = [parse_tool(t) for t in a.tool]
    commit, dirty = git_state(root, a.code, code)
    if a.kind == "production" and not a.tool:
        warnings.append("--tool: a production run is recorded with no tool and no version; add "
                        "--tool NAME=VERSION for each tool, copied from what it prints")

    def files(paths, indent):
        pad = " " * indent
        out = []
        for rel in paths:
            out.append(f"{pad}- path: {q(rel)}")
            out.append(f"{pad}  sha256: {q(sha256_of(root / rel))}")
        return out

    def lst(key, paths, indent=4):
        if not paths:
            return [f"{' ' * indent}{key}: []"]
        return [f"{' ' * indent}{key}:"] + files(paths, indent + 2)

    seed = "null"
    if a.seed is not None:
        # An unquoted integer only when YAML reads it back as the same digits: 007 is not 7.
        ok = (re.fullmatch(r"-?[0-9]{1,18}", a.seed) and str(int(a.seed)) == a.seed)
        seed = a.seed if ok else q(a.seed)
    lines = [f"  - id: {q(a.id)}", f"    date: {q(a.date)}", f"    kind: {a.kind}",
             f"    purpose: {q(a.purpose)}", f"    command: {q(a.command)}", "    code:",
             f"      commit: {'null' if commit is None else q(commit)}",
             f"      dirty: {'null' if dirty is None else str(dirty).lower()}"]
    lines += lst("files", code, 6)
    lines += lst("inputs", inputs)
    if tools:
        lines.append("    tools:")
        for n, v in tools:
            lines += [f"      - name: {q(n)}", f"        version: {q(v)}"]
    else:
        lines.append("    tools: []")
    lines.append(f"    seed: {seed}")
    if a.hardware:
        lines.append(f"    hardware: {q(a.hardware)}")
    if a.wall_time:
        lines.append(f"    wall_time: {q(a.wall_time)}")
    lines += lst("outputs", outputs)
    lines.append(f"    status: {a.status}")
    if a.superseded_by:
        lines.append(f"    superseded_by: {q(a.superseded_by)}")
    if a.reason:
        lines.append(f"    reason: {q(a.reason)}")
    row = "\n".join(lines) + "\n"
    row_info = (len(inputs) + len(code) + len(outputs), commit)
    return row, row_info


_COMMENT_OR_BLANK = re.compile(r"^\s*(#.*)?$")
_ITEM = re.compile(r"^(\s*)-(\s|$)")
_BLOCK_ID = re.compile(r"^\s*-\s+id\s*:")


def _list_indent(items: list[str], path: Path) -> int:
    """The indent of the list items under `runs:`; 2 when there are none. Refuses mixed or
    unrecognised layouts, because a row written at the wrong indent corrupts the file."""
    body = [ln.rstrip("\r\n") for ln in items if not _COMMENT_OR_BLANK.match(ln.rstrip("\r\n"))]
    if not body:
        return 2
    if any("\t" in ln[:len(ln) - len(ln.lstrip())] for ln in body):
        raise Refused(f"the `runs:` list in {path} is indented with tabs; the file was left "
                      "unchanged.")
    m = _ITEM.match(body[0])
    if not m:
        raise Refused(f"the first line under `runs:` in {path} is not a list item (`- id:`); "
                      "the file was left unchanged.")
    indent = len(m.group(1))
    for ln in body:
        lead = len(ln) - len(ln.lstrip())
        if lead < indent or (lead == indent and not _ITEM.match(ln)):
            raise Refused(f"the rows of `runs:` in {path} are not all indented the same way; "
                          "fix the indent by hand. The file was left unchanged.")
    return indent


def _load_yaml(text: str):
    """(True, data) with PyYAML, or (False, None) when it is not installed."""
    try:
        import yaml
    except ImportError:
        return False, None
    try:
        return True, yaml.safe_load(text)
    except Exception as e:                       # YAMLError, ValueError for a bad date, ...
        raise Refused(f"the YAML cannot be parsed ({str(e).splitlines()[0] if str(e) else type(e).__name__})")


def _rows_of(data, what: str, path: Path) -> list:
    runs = data.get("runs") if isinstance(data, dict) else None
    if runs is None and isinstance(data, dict) and "runs" in data:
        return []
    if not isinstance(runs, list):
        raise Refused(f"{what} `runs` of {path} is not a list; the file was left unchanged.")
    return runs


def _verify(old_text, new: str, run_id: str, path: Path) -> None:
    """With PyYAML: the new text parses, `runs` is a list, every earlier row and key is
    unchanged and the last row is the new one. Without PyYAML: nothing."""
    have, new_data = _load_yaml(new)
    if not have:
        return
    if not isinstance(new_data, dict):
        raise Refused(f"the new text would not be a mapping; {path} was left unchanged.")
    new_rows = _rows_of(new_data, "the new", path)
    old_rows, old_data = [], {}
    if old_text is not None:
        _, old_data = _load_yaml(old_text)
        if not isinstance(old_data, dict):
            raise Refused(f"{path} is not a YAML mapping now; it was left unchanged.")
        old_rows = _rows_of(old_data, "the existing", path)
    if new_rows[:len(old_rows)] != old_rows or len(new_rows) != len(old_rows) + 1:
        raise Refused(f"adding the row would change or break the earlier rows of {path}; it "
                      "was left unchanged. Check the file's layout.")
    last = new_rows[-1]
    if not isinstance(last, dict) or str(last.get("id")) != run_id:
        raise Refused(f"the new row would not read back as run {run_id}; {path} was left "
                      "unchanged.")
    for key in old_data:
        if key not in ("runs", "updated") and new_data.get(key) != old_data[key]:
            raise Refused(f"adding the row would change `{key}` in {path}; it was left unchanged.")


def _read_text(runs_path: Path) -> str:
    try:
        raw = runs_path.read_bytes()
    except OSError as e:
        raise Refused(f"cannot read {runs_path} ({e.strerror or e}); nothing was written")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refused(f"{runs_path} is not UTF-8; it was left unchanged")


def _layout(text: str, runs_path: Path):
    """(lines, eol, top, ri, inline, indent, ids): where `runs:` is, the indent of its rows and
    the ids already in it. Refuses a file the script cannot edit safely."""
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    top = [(i, m.group(1), m.group(2)) for i, ln in enumerate(lines)
           if (m := _TOP_KEY.match(ln.rstrip("\r\n")))]
    if not top or top[-1][1] != "runs":
        raise Refused(f"`runs:` must be the last top-level key of {runs_path}, and it is "
                      "not (or is missing). Move it to the end by hand; the file was left "
                      "unchanged.")
    ri, _, rest = top[-1]
    inline = rest.split("#")[0].strip()
    if inline and inline != "[]":
        raise Refused(f"`runs:` in {runs_path} has an inline value; write it as a block list.")
    items = lines[ri + 1:]
    indent = _list_indent(items, runs_path)
    have_yaml, data = _load_yaml(text)
    if have_yaml:
        if not isinstance(data, dict):
            raise Refused(f"{runs_path} is not a YAML mapping; it was left unchanged.")
        ids = {str(r.get("id")) for r in _rows_of(data, "the existing", runs_path)
               if isinstance(r, dict)}
    else:
        ids = set()
        for ln in items:
            if _COMMENT_OR_BLANK.match(ln.rstrip("\r\n")):
                continue
            m = _ITEM.match(ln)
            if m and len(m.group(1)) == indent:
                m = _ID_LINE.match(ln)
                if not m:
                    raise Refused(f"a row of `runs:` in {runs_path} is not written as "
                                  "`- id: ...`, so duplicate ids cannot be checked without "
                                  "PyYAML. Install PyYAML (`pip install pyyaml`) or write the "
                                  "row in block style. The file was left unchanged.")
                ids.add(next(g for g in m.groups() if g is not None))
    return lines, eol, top, ri, inline, indent, ids


def _set_updated(lines: list, top: list, today: str) -> None:
    for i, name, _ in top:
        if name == "updated":
            tail = lines[i][len(lines[i].rstrip("\r\n")):]
            lines[i] = f"updated: {q(today)}" + tail
            break


def new_text(runs_path: Path, row: str, run_id: str, today: str):
    """(old text or None, whole file after the row is added). Raises Refused when it cannot be
    added. `row` is written at two spaces; it is shifted to the indent the file uses."""
    if not runs_path.exists():
        text = f'version: 1\nupdated: {q(today)}\n\nruns:\n{row}'
        _verify(None, text, run_id, runs_path)
        return None, text
    text = _read_text(runs_path)
    lines, eol, top, ri, inline, indent, ids = _layout(text, runs_path)
    if run_id in ids:
        raise Refused(f"run id {run_id} is already in {runs_path}. Use a new id; a run is "
                      "never overwritten.")
    if inline == "[]":                              # `runs: []` becomes an open list
        lines[ri] = "runs:" + eol
    _set_updated(lines, top, today)
    out = "".join(lines)
    if out and not out.endswith("\n"):
        out += eol
    shift = indent - 2
    pad = " " * shift
    rows = [(pad + ln) if shift >= 0 else ln[-shift:] for ln in row.splitlines()]
    out += eol.join(rows) + eol
    _verify(text, out, run_id, runs_path)
    return text, out


def _scalar(rest: str) -> str:
    """The plain text of a one-line YAML scalar: no comment, no quotes."""
    v = re.split(r"\s#", " " + rest, maxsplit=1)[0].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def supersede_text(runs_path: Path, old: str, by: str, reason: str, today: str):
    """The whole file after run `old` is marked as replaced by `by`. Only the `status`,
    `superseded_by` and `reason` lines of that row and the `updated:` line change."""
    if not runs_path.exists():
        raise Refused(f"{runs_path} does not exist, so there is no run to supersede.")
    if old == by:
        raise Refused(f"--by {by}: a run cannot replace itself; name the run that replaced it.")
    text = _read_text(runs_path)
    lines, eol, top, ri, inline, indent, ids = _layout(text, runs_path)
    for name, label in ((old, "--supersede"), (by, "--by")):
        if name not in ids:
            raise Refused(f"{label} {name}: no run with that id in {runs_path}. Record the "
                          "replacing run first; the file was left unchanged.")
    def locate(name: str, label: str):
        start = None
        for k in range(ri + 1, len(lines)):
            m = _ITEM.match(lines[k])
            if m and len(m.group(1)) == indent:
                idm = _ID_LINE.match(lines[k])
                if idm and next(g for g in idm.groups() if g is not None) == name:
                    start = k
                    break
        if start is None:
            raise Refused(f"run {name} is not written as `- id: {name}` in {runs_path}; the "
                          "script edits only a row written that way. Edit it by hand.")
        m = re.match(r"^(\s*)-(\s+)id\b", lines[start])
        fi = len(m.group(1)) + 1 + len(m.group(2))
        end = len(lines)
        for k in range(start + 1, len(lines)):
            m2 = _ITEM.match(lines[k])
            if m2 and len(m2.group(1)) == indent:
                end = k
                break
        last = start
        for k in range(start, end):
            if not _COMMENT_OR_BLANK.match(lines[k].rstrip("\r\n")):
                last = k
        key = re.compile(r"^ {%d}([A-Za-z_][\w-]*)\s*:(.*)$" % fi)
        at: dict = {}
        for k in range(start + 1, last + 1):
            km = key.match(lines[k].rstrip("\r\n"))
            if km and km.group(1) not in at:
                at[km.group(1)] = (k, km.group(2))
        if "status" not in at:
            raise Refused(f"run {name} has no `status` line in {runs_path}; fix the row by hand.")
        return fi, last, at, _scalar(at["status"][1]).lower()

    fi, last, at, status = locate(old, "--supersede")
    _, _, _, by_status = locate(by, "--by")
    if by_status != "valid":
        raise Refused(f"--by {by}: that run has status {by_status!r}, not valid. Only a valid run "
                      f"can replace another; {runs_path} was left unchanged.")
    if status == "superseded":
        raise Refused(f"run {old} is already superseded in {runs_path}; its row was not changed.")
    if status != "valid":
        raise Refused(f"run {old} has status {status!r}, not valid; only a valid run is marked "
                      "as replaced, so that its own reason is not overwritten.")
    if "reason" in at and _scalar(at["reason"][1]).strip():
        raise Refused(f"run {old} already has a reason in {runs_path}. Edit that one row by hand, "
                      "or remove the old reason and run this again; the file was left unchanged.")
    drop = set()
    for name in ("superseded_by", "reason"):
        if name in at:
            k = at[name][0]
            drop.add(k)
            j = k + 1
            while j <= last and (not lines[j].strip() or
                                 len(lines[j]) - len(lines[j].lstrip()) > fi):
                drop.add(j)
                j += 1
    sp = " " * fi
    block = [f"{sp}status: superseded{eol}", f"{sp}superseded_by: {q(by)}{eol}",
             f"{sp}reason: {q(reason)}{eol}"]
    out_lines: list = []
    for k, ln in enumerate(lines):
        if k == at["status"][0]:
            out_lines += block
        elif k not in drop:
            out_lines.append(ln)
    _set_updated(out_lines, [(i, n, r) for i, n, r in top], today)
    out = "".join(out_lines)
    _verify_supersede(text, out, old, by, reason, runs_path)
    return out


def _verify_supersede(old_text: str, new: str, old: str, by: str, reason: str,
                      path: Path) -> None:
    """With PyYAML: the new text parses, only the three fields of the one row changed, and no
    other key but `updated` changed. Without PyYAML: nothing."""
    have, new_data = _load_yaml(new)
    if not have:
        return
    _, old_data = _load_yaml(old_text)
    if not isinstance(new_data, dict) or not isinstance(old_data, dict):
        raise Refused(f"the edit would not leave a YAML mapping; {path} was left unchanged.")
    old_rows = _rows_of(old_data, "the existing", path)
    new_rows = _rows_of(new_data, "the new", path)
    ok = len(old_rows) == len(new_rows)
    for o, n in zip(old_rows, new_rows):
        if not ok:
            break
        if isinstance(o, dict) and str(o.get("id")) == old:
            want = {k: v for k, v in o.items() if k not in ("superseded_by", "reason")}
            want.update(status="superseded", superseded_by=by, reason=reason)
            ok = n == want
        else:
            ok = n == o
    for k in old_data:
        if k not in ("runs", "updated") and new_data.get(k) != old_data[k]:
            ok = False
    if not ok:
        raise Refused(f"marking run {old} as superseded would change more than its status, "
                      f"`superseded_by` and `reason` in {path}; it was left unchanged. Edit the "
                      "row by hand.")


class _Lock:
    """An exclusive lock on `runs.yml.lock` for the whole read, modify and write."""

    def __init__(self, runs_path: Path):
        self.path = runs_path.with_name(runs_path.name + ".lock")
        self.fd = None

    def __enter__(self):
        deadline = time.monotonic() + LOCK_WAIT
        while True:
            try:
                if self._try():
                    return self
            except OSError as e:
                raise Refused(f"cannot take the lock {self.path} ({e.strerror or e}); nothing "
                              "was written")
            if time.monotonic() >= deadline:
                raise Refused(f"the lock {self.path} could not be taken; another run may be "
                              "writing, or a crashed run left it. If no run is active, delete "
                              "that file and try again. Nothing was written.")
            time.sleep(0.05)

    def _try(self) -> bool:
        if fcntl is None:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                return False
            return True
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            return False
        try:                       # the holder removes the file: make sure this one is current
            same = os.fstat(fd).st_ino == os.stat(self.path).st_ino
        except OSError:
            same = False
        if not same:
            os.close(fd)
            return False
        self.fd = fd
        return True

    def __exit__(self, *exc):
        try:
            os.unlink(self.path)                 # while still holding it
        except OSError:
            pass
        if self.fd is not None:
            os.close(self.fd)
        return False


def write_atomic(path: Path, text: str) -> None:
    """Encode first, write a temporary file beside the target, sync, then replace."""
    try:
        data = text.encode("utf-8")
    except UnicodeEncodeError as e:
        raise Refused(f"the text cannot be written as UTF-8 ({e.reason}); {path} was left "
                      "unchanged")
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".runs.", suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        if path.exists():
            shutil.copymode(path, tmp)
        else:
            os.chmod(tmp, 0o644)
        os.replace(tmp, path)
        tmp = None
    except OSError as e:
        raise Refused(f"could not write {path} ({e.strerror or e}); it was left unchanged")
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, allow_abbrev=False,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", required=True, help="the .paper folder")
    ap.add_argument("--id", help="run id, used once, e.g. R3")
    ap.add_argument("--kind", choices=KINDS)
    ap.add_argument("--purpose")
    ap.add_argument("--command", help="the command that started the run")
    ap.add_argument("--inputs", nargs="*", default=[], metavar="PATH")
    ap.add_argument("--code", nargs="*", default=[], metavar="PATH")
    ap.add_argument("--outputs", nargs="*", default=[], metavar="PATH")
    ap.add_argument("--tool", action="append", default=[], metavar="NAME=VERSION",
                    help="a tool and the version string it printed; may repeat")
    ap.add_argument("--seed", help="one seed per row; record one row per seed")
    ap.add_argument("--hardware", help="the machine the run used, as text")
    ap.add_argument("--wall-time", dest="wall_time", help="the elapsed time of the run, as text")
    ap.add_argument("--status", choices=STATUSES)
    ap.add_argument("--reason")
    ap.add_argument("--superseded-by", dest="superseded_by")
    ap.add_argument("--supersede", metavar="ID",
                    help="mark this existing run as replaced (needs --by and --reason)")
    ap.add_argument("--by", metavar="ID", help="with --supersede: the run that replaced it")
    ap.add_argument("--date", help="YYYY-MM-DD, default today")
    a = ap.parse_args(argv)

    try:
        paper = Path(os.path.abspath(a.paper))
        if paper.name != ".paper":
            raise Refused(f"--paper must be a folder named .paper; {a.paper!r} was given")
        root = paper.parent
        if not root.is_dir():
            raise Refused(f"the project folder {root} (the parent of --paper) does not exist")
        runs_path = paper / "runs.yml"
        if a.supersede is not None:
            return _supersede_main(a, runs_path)
        if a.by:
            raise Refused("--by is only for --supersede")
        for flag, value in (("--id", a.id), ("--kind", a.kind), ("--purpose", a.purpose),
                            ("--command", a.command)):
            if not value:
                raise Refused(f"{flag} is required (or use --supersede ID --by ID --reason TEXT)")
        a.status = a.status or "valid"
        a.date = a.date or date.today().isoformat()
        if not re.fullmatch(r"[^\s#:]+", a.id):
            raise Refused(f"--id {a.id!r} must be one word with no spaces, colon or #")
        try:
            date.fromisoformat(a.date)
        except ValueError:
            raise Refused(f"--date {a.date!r}: write it as YYYY-MM-DD")
        if a.status in ("failed", "excluded", "superseded") and not (a.reason or "").strip():
            raise Refused(f"--status {a.status} requires --reason")
        if a.status == "superseded" and not a.superseded_by:
            raise Refused("--status superseded requires --superseded-by (the replacing run)")
        if a.superseded_by and a.status != "superseded":
            raise Refused("--superseded-by is only for --status superseded")
        warnings: list = []
        row, (count, commit) = build_row(a, root, warnings)
        try:
            paper.mkdir(exist_ok=True)
        except OSError as e:
            raise Refused(f"cannot create {paper} ({e.strerror or e})")
        with _Lock(runs_path):
            _, text = new_text(runs_path, row, a.id, date.today().isoformat())
            write_atomic(runs_path, text)
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"refused: {e.strerror or e}{f' ({e.filename})' if e.filename else ''}; nothing "
              "was written", file=sys.stderr)
        return 2
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    where = f"commit {commit[:12]}" if commit else "no version control"
    print(f"wrote run {a.id} to {runs_path}: {count} files hashed, {where}")
    return 0


def _supersede_main(a, runs_path: Path) -> int:
    """The --supersede mode. Raises Refused; main prints it and exits 2."""
    other = [flag for flag, value in (
        ("--id", a.id), ("--kind", a.kind), ("--purpose", a.purpose), ("--command", a.command),
        ("--inputs", a.inputs), ("--code", a.code), ("--outputs", a.outputs), ("--tool", a.tool),
        ("--seed", a.seed), ("--hardware", a.hardware), ("--wall-time", a.wall_time),
        ("--status", a.status), ("--superseded-by", a.superseded_by), ("--date", a.date)) if value]
    if other:
        raise Refused(f"--supersede changes an existing row only; it cannot be combined with "
                      f"{', '.join(other)}")
    if not a.by:
        raise Refused("--supersede needs --by (the run that replaced it)")
    if not (a.reason or "").strip():
        raise Refused("--supersede needs --reason (why the run was replaced)")
    with _Lock(runs_path):
        text = supersede_text(runs_path, a.supersede, a.by, a.reason, date.today().isoformat())
        write_atomic(runs_path, text)
    print(f"marked run {a.supersede} as superseded by {a.by} in {runs_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
