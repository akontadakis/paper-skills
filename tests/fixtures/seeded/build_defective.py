#!/usr/bin/env python3
"""Rebuild `defective/` from `clean/` by planting the faults listed in `manifest.json`.

Run it after any edit to `clean/`, so the two copies differ only by the planted faults:
    python3 tests/fixtures/seeded/build_defective.py
Each planted string must be found exactly once in its clean file, and each anchor quote must
appear exactly once in its defective file. The script stops if either is not true.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLEAN, BAD = HERE / "clean", HERE / "defective"

# (file, text in the clean copy, text in the defective copy)
PLANTS = {
    "D1": ("manuscript.tex", r"\SI{2000}{\candela\per\metre\squared}", r"\SI{2000}{\lux}"),
    "D2": ("manuscript.tex",
           r"work-plane illuminance at the core was \SI{215}{\lux}",
           r"work-plane illuminance at the core was \SI{212}{\lux}"),
    "D3": ("manuscript.tex",
           "The result holds for the\nfour climates, the south orientation, and the one room depth that were "
           "simulated.",
           "The result holds for all climates and orientations."),
    "D4": ("manuscript.tex",
           "Core workstations receive what daylight is\nleft.",
           "DGP is the usual glare criterion at the perimeter. Core workstations receive what "
           "daylight is\nleft."),
    "D5": ("manuscript.tex",
           r"fixed blinds (Fig.~\ref{fig:core}).",
           r"fixed blinds (Fig.~\ref{fig:core}; see also Fig.~\ref{fig:missing})."),
    "D6": ("refs.bib",
           "Tuning automated shading against daylight glare probability",
           "Automated shading and visual comfort in deep-plan schools"),
    "D7": (".paper/claims.yml", '    status: gap\n    evidence: []\n    verb: "assume"',
           '    status: needs evidence\n    evidence: []\n    verb: "shows"'),
    "D8": (".paper/changes.yml",
           '    status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
           '    status: done\n    verified_on: null\n    response_paragraph: "R1.1"'),
    "D9": ("manuscript.tex", r"\cite{okafor2020}", r"\cite{okafor2020,nowak2019}"),
    "D10": (".paper/figures.yml", "0.31 with the controller", "0.29 with the controller"),
    "D11": (".paper/claims.yml",
            '    bounded_to: "four climates, south orientation, one room depth"\n', ""),
}


def main() -> int:
    if BAD.exists():
        shutil.rmtree(BAD)
    shutil.copytree(CLEAN, BAD)
    for did, (rel, old, new) in PLANTS.items():
        p = BAD / rel
        text = p.read_text(encoding="utf-8")
        if text.count(old) != 1:
            print(f"{did}: expected exactly one match in clean/{rel}, found {text.count(old)}")
            return 1
        p.write_text(text.replace(old, new), encoding="utf-8")
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for row in manifest:
        text = (BAD / row["file"]).read_text(encoding="utf-8")
        if text.count(row["anchor_quote"]) != 1:
            print(f"{row['defect_id']}: anchor quote appears {text.count(row['anchor_quote'])} "
                  f"times in defective/{row['file']}")
            return 1
    print(f"defective/ rebuilt with {len(PLANTS)} planted faults")
    return 0


if __name__ == "__main__":
    sys.exit(main())
