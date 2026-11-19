#!/usr/bin/env python3
"""Extract figures from a PDF, and audit figure resolution in your own compiled manuscript.

Two jobs, one caption index.

  extract   Pull figures out of a paper as PNG files, one per caption, so you can read them
            at size or drop a comparison figure into a slide.
  audit     Report the effective resolution and physical size of every embedded raster in
            YOUR compiled PDF, and flag anything that will print soft. This is the
            mechanical half of the legibility rules in references/figures-tables.md and
            references/word-manuscripts.md.

Requires PyMuPDF:  pip install PyMuPDF

Usage:
    python3 extract_figures.py extract paper.pdf --out figs/
    python3 extract_figures.py extract paper.pdf --only 3 5 --dpi 400
    python3 extract_figures.py extract paper.pdf --native      # embedded rasters, not renders
    python3 extract_figures.py audit  manuscript.pdf
    python3 extract_figures.py audit  manuscript.pdf --min-dpi 300 --json audit.json

Exit codes: 0 done; 1 `audit --strict` found a raster below --min-dpi; 2 could not start
(missing, unreadable, encrypted or empty PDF, or PyMuPDF not installed; the reason goes to
stderr); 3 `extract` found no matching caption, or a caption it could not extract.

Copyright: extracting a figure from a paper you have lawful access to, for reading, teaching,
or a properly attributed comparison, is normal scholarly use. Reusing a figure in your own
publication needs the rightsholder's permission unless the licence already grants it. This
script does not check licences. That is your call, not its.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import pymupdf as fitz                                   # PyMuPDF, current module name
except ImportError:
    try:
        import fitz                                          # PyMuPDF before the rename
    except ImportError:
        print("PyMuPDF is required:  pip install PyMuPDF", file=sys.stderr)
        sys.exit(2)

# Anchored at line start so an in-text "see Figure 3" is not mistaken for a caption. After the
# number comes a full stop, colon, bar or dash ("Figure 2 |", "FIG. 2.", "Figure 2 - Text"),
# or nothing but a space and a capital letter ("Fig. 2 Text"). A lower-case word or a comma
# there ("Fig. 2, the", "Figure 2 shows") is a sentence, not a caption.
_SEP = r"(?:\s*[.:|\u2013\u2014\u2212]|\s+-\s+|\s+(?-i:[A-Z]))"
CAPTION_PATTERNS = [
    (re.compile(r"^\s*(Fig(?:ure)?\.?\s*(\d+)[a-z]?)" + _SEP, re.I), "figure"),
    (re.compile(r"^\s*(Table\s*(\d+)[a-z]?)" + _SEP, re.I), "table"),
    (re.compile(r"^\s*(Scheme\.?\s*(\d+))" + _SEP, re.I), "scheme"),
    (re.compile(r"^\s*(Chart\.?\s*(\d+))" + _SEP, re.I), "chart"),
    (re.compile(r"^\s*(Supplementary\s+Fig(?:ure)?\.?\s*(\d+))" + _SEP, re.I), "supplementary"),
    (re.compile(r"^\s*(Extended\s+Data\s+Fig(?:ure)?\.?\s*(\d+))" + _SEP, re.I), "extended_data"),
    (re.compile(r"^\s*(Appendix\s+Fig(?:ure)?\.?\s*(\d+))" + _SEP, re.I), "appendix"),
]

PT_PER_INCH = 72.0


# --------------------------------------------------------------------------- captions

def find_captions(doc) -> list[dict]:
    """Locate caption blocks. Returns page, rect, label, kind, and the caption's first line."""
    found = []
    for pno, page in enumerate(doc):
        blocks = page.get_text("blocks")                      # (x0,y0,x1,y1,text,bno,type)
        for b in blocks:
            if len(b) < 5 or b[4] is None:
                continue
            text = b[4].strip()
            if not text:
                continue
            first = text.split("\n", 1)[0]
            for pat, kind in CAPTION_PATTERNS:
                m = pat.match(text)
                if not m:
                    continue
                found.append({
                    "page": pno,
                    "label": re.sub(r"\s+", " ", m.group(1)).strip(),
                    "number": int(m.group(2)),
                    "kind": kind,
                    "rect": fitz.Rect(b[:4]),
                    "caption": re.sub(r"\s+", " ", text)[:400],
                    "first_line": first[:160],
                })
                break
    # A figure number can legitimately appear twice (a continued caption). Keep the first.
    seen, out = set(), []
    for f in sorted(found, key=lambda x: (x["page"], x["rect"].y0)):
        key = (f["kind"], f["number"])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def region_for(page, cap: dict, doc) -> fitz.Rect:
    """The area belonging to a caption: above it for a figure, below it for a table."""
    pr = page.rect
    cr = cap["rect"]
    others = [c["rect"] for c in doc._caps
              if c["page"] == cap["page"] and c["rect"] != cr]
    if cap["kind"] == "table":
        top = cr.y1
        bottom = min([o.y0 for o in others if o.y0 > cr.y1] + [pr.y1 - 36])
    else:
        bottom = cr.y0
        above = [o.y1 for o in others if o.y1 < cr.y0]
        top = max(above + [pr.y0 + 36])
    # Widen to the drawn and imaged content actually inside the band, so a single-column
    # figure is not cropped to the full page width.
    band = fitz.Rect(pr.x0, top, pr.x1, bottom)
    content = fitz.Rect(band.x1, band.y1, band.x0, band.y0)   # empty, inverted
    for item in page.get_drawings():
        r = item["rect"]
        if r.y0 >= band.y0 - 2 and r.y1 <= band.y1 + 2 and r.get_area() > 4:
            content |= r
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if r.y0 >= band.y0 - 2 and r.y1 <= band.y1 + 2:
            content |= r
    if content.is_empty or content.get_area() < 400:
        return band
    pad = 6
    return fitz.Rect(max(pr.x0, content.x0 - pad), max(band.y0, content.y0 - pad),
                     min(pr.x1, content.x1 + pad), min(band.y1, content.y1 + pad))


def native_xrefs(page, cap: dict, all_caps: list[dict]) -> list[int]:
    """The xrefs of the images that belong to one caption, in page order.

    An image belongs to a caption only when it lies in that caption's region: between it and
    the previous caption (or the page top), for the usual layout with the caption under the
    figure. If the page's first caption has no image above it but has one below, the document
    puts captions above figures, and the region is between the caption and the next caption
    (or the page bottom). A table caption always owns what lies below it.
    """
    caps = sorted((c for c in all_caps if c["page"] == cap["page"]),
                  key=lambda c: c["rect"].y0)
    imgs = [(fitz.Rect(i["bbox"]), i["xref"]) for i in page.get_image_info(xrefs=True)
            if i.get("xref")]
    slack = 2

    def inside(r, top, bottom):
        return r.y0 >= top - slack and r.y1 <= bottom + slack

    first = caps[0]["rect"]
    caption_above = (not any(inside(r, 0, first.y0) for r, _ in imgs)
                     and any(inside(r, first.y1, page.rect.y1) for r, _ in imgs))
    idx = next(n for n, c in enumerate(caps) if c["rect"] == cap["rect"])
    if cap["kind"] == "table" or caption_above:
        top = cap["rect"].y1
        bottom = caps[idx + 1]["rect"].y0 if idx + 1 < len(caps) else page.rect.y1
    else:
        top = caps[idx - 1]["rect"].y1 if idx else 0
        bottom = cap["rect"].y0
    out: list[int] = []
    for r, xref in sorted(imgs, key=lambda t: (t[0].y0, t[0].x0)):
        if inside(r, top, bottom) and xref not in out:
            out.append(xref)
    return out


# --------------------------------------------------------------------------- extract

class StartupError(Exception):
    """The run cannot start: `main` prints the message to stderr and exits 2."""


def open_pdf(path: str):
    try:
        doc = fitz.open(path)
    except Exception as e:                                    # noqa: BLE001
        raise StartupError(f"cannot open {path}: {e}\n"
                           "If it is a real PDF, it may be encrypted or truncated. "
                           "Try opening it in a viewer first.") from e
    if doc.is_encrypted and not doc.authenticate(""):
        raise StartupError(f"{path} is password protected. Remove the password and retry.")
    if doc.page_count == 0:
        raise StartupError(f"{path} has no pages.")
    return doc


def cmd_extract(args) -> int:
    doc = open_pdf(args.pdf)
    doc._caps = find_captions(doc)
    caps = doc._caps
    if args.kind:
        caps = [c for c in caps if c["kind"] == args.kind]
    not_checked = 0
    if args.only:
        found = {c["number"] for c in caps}
        for n in dict.fromkeys(args.only):
            if n not in found:
                print(f"not checked: no caption found for figure {n}")
                not_checked += 1
        caps = [c for c in caps if c["number"] in set(args.only)]
    if not caps:
        print("No captions matched. Try --kind figure, or check the PDF has a text layer "
              "(a scanned PDF has none).", file=sys.stderr)
        return 3

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    index, zoom = [], args.dpi / PT_PER_INCH

    for cap in caps:
        page = doc[cap["page"]]
        name = re.sub(r"[^A-Za-z0-9]+", "_", cap["label"]).strip("_").lower()
        rec = {"label": cap["label"], "kind": cap["kind"], "page": cap["page"] + 1,
               "caption": cap["caption"], "files": []}

        if args.native:
            for i, xref in enumerate(native_xrefs(page, cap, doc._caps)):
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    p = out / f"{name}_img{i + 1}.png"
                    pix.save(p)
                    rec["files"].append({"path": str(p), "px": [pix.width, pix.height]})
                except Exception as e:                        # noqa: BLE001
                    print(f"  {cap['label']} image {i + 1}: {e}", file=sys.stderr)
        else:
            rect = region_for(page, cap, doc)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
            p = out / f"{name}.png"
            pix.save(p)
            rec["files"].append({"path": str(p), "px": [pix.width, pix.height],
                                 "dpi": args.dpi,
                                 "pt": [round(rect.width, 1), round(rect.height, 1)]})

        index.append(rec)
        if args.native and not rec["files"]:
            print(f"{cap['label']:<28} p.{cap['page'] + 1:<4} "
                  f"not checked: no embedded raster for {cap['label']}")
            not_checked += 1
        else:
            files = ", ".join(f["path"] for f in rec["files"]) or "(none)"
            print(f"{cap['label']:<28} p.{cap['page'] + 1:<4} {files}")

    ip = out / "figure_index.json"
    ip.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"\n{len(index)} item(s). Index -> {ip}", file=sys.stderr)
    if not args.native:
        print("Rendered from the page. Use --native for the embedded raster at its own "
              "resolution.", file=sys.stderr)
    if not_checked:
        print(f"{not_checked} item(s) not checked: this is not a complete extraction.",
              file=sys.stderr)
        return 3
    return 0


# --------------------------------------------------------------------------- audit

def cmd_audit(args) -> int:
    doc = open_pdf(args.pdf)
    doc._caps = find_captions(doc)
    caps_by_page: dict[int, list] = {}
    for c in doc._caps:
        caps_by_page.setdefault(c["page"], []).append(c)

    rows, worst = [], []
    for pno, page in enumerate(doc):
        for info in page.get_image_info(xrefs=True):
            bbox = fitz.Rect(info["bbox"])
            w_in = bbox.width / PT_PER_INCH
            h_in = bbox.height / PT_PER_INCH
            if w_in < 0.3 or h_in < 0.3:
                continue                                      # a rule, a logo, an icon
            px_w, px_h = info["width"], info["height"]
            dpi_x = px_w / w_in if w_in else 0
            dpi_y = px_h / h_in if h_in else 0
            dpi = min(dpi_x, dpi_y)
            near = sorted(caps_by_page.get(pno, []),
                          key=lambda c: abs(c["rect"].y0 - bbox.y1))
            label = near[0]["label"] if near else "—"
            row = {"page": pno + 1, "near": label,
                   "px": [px_w, px_h],
                   "size_in": [round(w_in, 2), round(h_in, 2)],
                   "size_mm": [round(w_in * 25.4), round(h_in * 25.4)],
                   "dpi": round(dpi),
                   "colorspace": info.get("cs-name", "?"),
                   "verdict": ""}
            if dpi < args.min_dpi:
                row["verdict"] = f"LOW — under {args.min_dpi} dpi at printed size"
                worst.append(row)
            elif dpi < args.min_dpi * 1.2:
                row["verdict"] = "borderline"
            else:
                row["verdict"] = "ok"
            rows.append(row)

    print(f"{'page':>4}  {'near':<14} {'pixels':<13} {'printed':<13} {'dpi':>5}  verdict")
    print("-" * 78)
    for r in sorted(rows, key=lambda x: x["dpi"]):
        print(f"{r['page']:>4}  {r['near'][:14]:<14} "
              f"{r['px'][0]}x{r['px'][1]:<7} "
              f"{r['size_mm'][0]}x{r['size_mm'][1]} mm  "
              f"{r['dpi']:>5}  {r['verdict']}")

    print()
    if not rows:
        print("No raster images found. If every figure is vector, that is the right answer "
              "for plots and diagrams — nothing to audit here.")
    else:
        print(f"{len(rows)} raster image(s). {len(worst)} below {args.min_dpi} dpi.")
        if worst:
            print("\nFix each by exporting the figure at the width it is placed at, not by "
                  "resizing it on the page.")
            print("Typical publisher floors: 300 dpi photographs, 500 dpi combination "
                  "figures, 1000 dpi line art. Check your journal's own guide.")
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nreport -> {args.json}")
    return 1 if worst and args.strict else 0


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="pull figures out as PNG")
    e.add_argument("pdf")
    e.add_argument("--out", default="figures")
    e.add_argument("--dpi", type=int, default=300)
    e.add_argument("--only", type=int, nargs="+", help="caption numbers to extract; add --kind figure to restrict to figures")
    e.add_argument("--kind", choices=["figure", "table", "scheme", "chart",
                                      "supplementary", "extended_data", "appendix"])
    e.add_argument("--native", action="store_true",
                   help="save embedded rasters at their own resolution instead of rendering")
    e.set_defaults(func=cmd_extract)

    a = sub.add_parser("audit", help="report raster resolution at printed size")
    a.add_argument("pdf")
    a.add_argument("--min-dpi", type=int, default=300)
    a.add_argument("--json")
    a.add_argument("--strict", action="store_true", help="exit 1 if anything is below --min-dpi")
    a.set_defaults(func=cmd_audit)

    args = ap.parse_args()
    if not Path(args.pdf).is_file():
        print(f"not found: {args.pdf}", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except StartupError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
