#!/usr/bin/env python3
"""Fetch open-access PDFs and citation metadata for papers you want to read or cite.

Legitimate open access only. This resolves a DOI, arXiv id, or PubMed id to a copy the
publisher or the author has made openly available, using Unpaywall, OpenAlex, arXiv, and
Europe PMC. It does not bypass a paywall, does not use institutional proxies or VPN
credentials, and does not spoof a browser. When no open copy exists it says so and prints the
publisher landing page so you can reach it through your library.

Standard library only. No pip install required.

Usage:
    python3 fetch_oa_pdf.py 10.1016/j.buildenv.2023.110000 --email you@example.org
    python3 fetch_oa_pdf.py 2301.07041
    python3 fetch_oa_pdf.py PMC7906746
    python3 fetch_oa_pdf.py 10.1038/s41586-023-06600-9 --bibtex-only
    python3 fetch_oa_pdf.py --batch dois.txt --out papers/ --email you@example.org

Unpaywall requires a real contact email on every call. Pass --email, or set UNPAYWALL_EMAIL.
The email is sent to Unpaywall only. Without one, Unpaywall is skipped and only OpenAlex,
arXiv, and Europe PMC are tried. The DOI is also sent to doi.org, for the BibTeX record.
A PubMed id is a bare number of 7 or 8 digits, or any 1 to 8 digits after a `PMID:` prefix
(`PMID:12345`); a shorter bare number is not read as a PubMed id.

A DOI that holds brackets or `<`, `>`, `;` goes in single quotes on the command line.
--bibtex-only on an arXiv id asks doi.org for 10.48550/arXiv.<id>; on a PMC or PubMed id it
reports "not checked". Only http and https addresses are downloaded. At least three seconds
pass between two requests to arXiv; for many arXiv papers use arXiv's bulk data access.

Exit code 0 when every lookup answered (also a lookup in which Unpaywall was skipped for want of
an email and nothing open was found elsewhere: the output and the JSON `sources_not_asked` say so), 2 when no identifier was given, the --batch file
cannot be read, --out is a file, --json cannot be written, or every identifier was
unrecognised, 3 when something was not checked (a lookup or a download failed on the network,
or an identifier was not recognised).
"not checked" is never an answer about the paper.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "research-paper-writing-skill/1.0 (open-access fetcher; +https://unpaywall.org/products/api)"

# Resolver errors are counted so a network or TLS failure is never reported as
# "no open-access copy found". The two are different answers.
ERRORS: list[str] = []
# Downloads that failed because the network did (not because a host refused). Cleared per
# identifier. A host that answers 403 has answered; a network that fails has not.
DOWNLOAD_ERRORS: list[str] = []

TLS_HINT = (
    "TLS certificate verification failed. This is a local Python install problem, not a "
    "missing paper.\n"
    "  macOS python.org build:  /Applications/Python\\ 3.x/Install\\ Certificates.command\n"
    "  or:                      python3 -m pip install --upgrade certifi"
)


# Where an operating system keeps its CA bundle when Python itself ships without one.
SYSTEM_CA_BUNDLES = ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt",
                     "/etc/pki/tls/certs/ca-bundle.crt")


def _ssl_context():
    """A verifying TLS context. Verification is never switched off.

    Order: certifi if installed, else Python's default store, else the operating system's
    CA bundle. The last step matters on a python.org macOS build, whose default store is
    empty until `Install Certificates.command` is run, so every request fails.
    """
    import ssl
    try:
        import certifi                                        # optional
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats()["x509_ca"] == 0:
        paths = ssl.get_default_verify_paths()
        configured = [p for p in (paths.cafile, paths.capath) if p and os.path.exists(p)]
        if not configured:
            for bundle in SYSTEM_CA_BUNDLES:
                if os.path.isfile(bundle):
                    ctx.load_verify_locations(bundle)
                    break
    return ctx

MIN_PDF_BYTES = 10_000
TIMEOUT = 45
# arXiv asks for one request every three seconds. The time of the last one is kept here.
ARXIV_DELAY = 3.0
_LAST_ARXIV: list = [None]

ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5})(v\d+)?$", re.I)
OLD_ARXIV_RE = re.compile(r"^(?:arxiv:)?([a-z-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?$", re.I)
PMC_RE = re.compile(r"^PMC\d+$", re.I)
# A bare number is a PubMed id only with 7 or 8 digits; a shorter one needs the PMID: prefix,
# so a stray year or count in a batch file is not looked up as a paper.
PMID_RE = re.compile(r"^(?:pmid:\s*(\d{1,8})|(\d{7,8}))$", re.I)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


# --------------------------------------------------------------------------- helpers

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _on_arxiv(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host == "arxiv.org" or host.endswith(".arxiv.org")


def _arxiv_wait(url: str) -> None:
    """Keep at least ARXIV_DELAY seconds between two requests to arXiv."""
    if not _on_arxiv(url):
        return
    now = time.monotonic()
    last = _LAST_ARXIV[0]
    if last is not None and now - last < ARXIV_DELAY:
        time.sleep(ARXIV_DELAY - (now - last))
    _LAST_ARXIV[0] = time.monotonic()


class RedirectRefused(urllib.error.URLError):
    """A server sent the request on to an address that is not http or https."""


class _HttpOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        # Look at the address before urllib does: it allows ftp and reports file as a bare
        # "HTTP 302", which is not what happened.
        target = headers.get("location") or headers.get("uri") or ""
        scheme = urllib.parse.urlparse(urllib.parse.urljoin(req.full_url, target)).scheme.lower()
        if scheme not in ("http", "https"):
            raise RedirectRefused(f"redirected to a {scheme or 'relative'} address")
        return super().http_error_302(req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _open(req):
    """Open a request with verified TLS. A redirect to anything but http or https is refused."""
    opener = urllib.request.build_opener(_HttpOnlyRedirect,
                                         urllib.request.HTTPSHandler(context=_ssl_context()))
    return opener.open(req, timeout=TIMEOUT)


def get(url: str, accept: str = "application/json", raw: bool = False):
    _arxiv_wait(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with _open(req) as r:
        data = r.read()
        final = r.geturl()
        ctype = r.headers.get("Content-Type", "")
    if raw:
        return data, final, ctype
    return json.loads(data.decode("utf-8", "replace"))


def normalise(identifier: str) -> tuple[str, str]:
    """Return (kind, cleaned_id). kind is doi | arxiv | pmc | pmid | unknown."""
    s = identifier.strip()
    for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if s.lower().startswith(p):
            s = s[len(p):]
            break
    m = re.match(r"^https?://arxiv\.org/(?:abs|pdf)/(.+?)(?:\.pdf)?$", s, re.I)
    if m:
        s = m.group(1)
    if ARXIV_RE.match(s) or OLD_ARXIV_RE.match(s):
        return "arxiv", re.sub(r"^arxiv:", "", s, flags=re.I)
    if PMC_RE.match(s):
        return "pmc", s.upper()
    if DOI_RE.match(s):
        return "doi", s
    m = PMID_RE.match(s)
    if m:
        return "pmid", m.group(1) or m.group(2)
    return "unknown", s


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:120] or "paper"


def download(url: str, dest: Path) -> tuple[bool, str]:
    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme not in ("http", "https"):
        return False, (f"not downloaded: the address uses {scheme or 'no'} scheme; only http "
                       f"and https addresses are fetched. Open it by hand if you trust it.")
    try:
        data, final, ctype = get(url, accept="application/pdf,*/*", raw=True)
    except RedirectRefused:
        return False, ("not downloaded: redirected to an address that is not http or https. "
                       "Open the address of the paper by hand if you trust it.")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return False, (f"HTTP {e.code} — the host refuses automated requests. "
                           "The paper is open access; open the URL in a browser.")
        DOWNLOAD_ERRORS.append(f"{url}: HTTP {e.code}")
        return False, f"download failed: HTTP {e.code}"
    except Exception as e:                                   # noqa: BLE001
        DOWNLOAD_ERRORS.append(f"{url}: {e}")
        return False, f"download failed: {e}"
    if not data.startswith(b"%PDF"):
        head = data[:200].decode("utf-8", "replace").replace("\n", " ")
        return False, f"not a PDF (server returned {ctype or 'unknown type'}): {head[:120]}"
    if len(data) < MIN_PDF_BYTES:
        return False, f"PDF too small ({len(data)} bytes) — probably a stub or error page"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    except OSError as e:
        return False, f"could not save the PDF to {dest}: {e.strerror or e}"
    return True, f"{len(data):,} bytes from {final}"


# --------------------------------------------------------------------------- resolvers

def _safe(name: str):
    """A resolver reads a reply from outside. A reply of a shape this script does not know is
    an error of that source (not checked), never a traceback and never "no open copy"."""
    def wrap(fn):
        def run(*a, **k):
            try:
                return fn(*a, **k)
            except (AttributeError, TypeError, KeyError, ValueError, IndexError) as e:
                ERRORS.append(f"{name}: the reply had an unexpected shape ({type(e).__name__})")
                log(f"  {name}: the reply had an unexpected shape")
                return []
        run.__name__ = fn.__name__
        return run
    return wrap


def via_arxiv(arxiv_id: str) -> list[dict]:
    base = re.sub(r"v\d+$", "", arxiv_id)
    return [{"source": "arXiv", "url": f"https://arxiv.org/pdf/{base}", "licence": "arXiv (see paper)"}]


def _on_europepmc(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host == "europepmc.org" or host.endswith(".europepmc.org")


@_safe("Europe PMC")
def via_europepmc(ident: str, kind: str) -> list[dict]:
    q = f"EXT_ID:{ident}" if kind == "pmid" else f"PMCID:{ident}"
    if kind == "doi":
        q = f'DOI:"{ident}"'
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
           f"?query={urllib.parse.quote(q)}&format=json&pageSize=5&resultType=core")
    try:
        js = get(url)
    except Exception as e:                                   # noqa: BLE001
        ERRORS.append(f"Europe PMC: {e}")
        log(f"  Europe PMC: {e}")
        return []
    out = []
    for res in js.get("resultList", {}).get("result", []):
        pmcid = res.get("pmcid")
        if pmcid and res.get("isOpenAccess") == "Y":
            # The search result lists the full-text links. Take a pdf link that is marked open
            # (availabilityCode OA or F), else a pdf link on a europepmc.org host. Any other
            # link may sit behind a paywall and is skipped; a result with none gives no
            # candidate, because no PDF address is known for it.
            links = [u for u in (res.get("fullTextUrlList") or {}).get("fullTextUrl") or []
                     if str(u.get("documentStyle", "")).lower() == "pdf" and u.get("url")]
            pdf = (next((u["url"] for u in links
                         if str(u.get("availabilityCode", "")).upper() in ("OA", "F")), None)
                   or next((u["url"] for u in links if _on_europepmc(u["url"])), None))
            if pdf:
                out.append({
                    "source": "Europe PMC (OA subset)",
                    "url": pdf,
                    "licence": res.get("license") or "open access",
                })
    return out


@_safe("Unpaywall")
def via_unpaywall(doi: str, email: str) -> list[dict]:
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={urllib.parse.quote(email)}"
    try:
        js = get(url)
    except urllib.error.HTTPError as e:
        if e.code != 404:                        # 404 = DOI unknown to Unpaywall, a real answer
            ERRORS.append(f"Unpaywall: HTTP {e.code}")
        log(f"  Unpaywall: HTTP {e.code}")
        return []
    except Exception as e:                                   # noqa: BLE001
        ERRORS.append(f"Unpaywall: {e}")
        log(f"  Unpaywall: {e}")
        return []
    if not js.get("is_oa"):
        return []
    locs = [js.get("best_oa_location")] + (js.get("oa_locations") or [])
    out, seen = [], set()
    for loc in locs:
        if not loc:
            continue
        u = loc.get("url_for_pdf") or loc.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        out.append({
            "source": f"Unpaywall / {loc.get('host_type', '?')} "
                      f"({loc.get('repository_institution') or js.get('publisher') or '?'})",
            "url": u,
            "licence": loc.get("license") or "unstated",
        })
    return out


@_safe("OpenAlex")
def via_openalex(doi: str, mailto: str | None = None) -> list[dict]:
    # `mailto` is accepted for older callers and ignored: OpenAlex has no polite pool reached
    # by email any more, so the email is not sent there. A single-work lookup needs no key.
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    try:
        js = get(url)
    except Exception as e:                                   # noqa: BLE001
        ERRORS.append(f"OpenAlex: {e}")
        log(f"  OpenAlex: {e}")
        return []
    out, seen = [], set()
    for loc in [js.get("best_oa_location")] + (js.get("locations") or []):
        if not loc or not loc.get("is_oa"):
            continue
        u = loc.get("pdf_url") or loc.get("landing_page_url")
        if not u or u in seen:
            continue
        seen.add(u)
        src = (loc.get("source") or {}).get("display_name") or "?"
        out.append({"source": f"OpenAlex / {src}", "url": u,
                    "licence": loc.get("license") or "unstated"})
    return out


def crossref_bibtex(doi: str) -> str | None:
    try:
        data, _, _ = get(f"https://doi.org/{urllib.parse.quote(doi)}",
                         accept="application/x-bibtex", raw=True)
        text = data.decode("utf-8", "replace").strip()
        if not text.startswith("@"):
            # An HTTP 200 that is a landing page or an error page, not the record asked for.
            ERRORS.append("BibTeX: the reply was not BibTeX")
            log("  BibTeX: the reply was not BibTeX — not saved")
            return None
        return text
    except Exception as e:                                   # noqa: BLE001
        ERRORS.append(f"BibTeX: {e}")
        log(f"  BibTeX: {e}")
        return None


def landing_page(kind: str, ident: str) -> str:
    return {"doi": f"https://doi.org/{ident}",
            "arxiv": f"https://arxiv.org/abs/{ident}",
            "pmc": f"https://europepmc.org/article/PMC/{ident}",
            "pmid": f"https://pubmed.ncbi.nlm.nih.gov/{ident}/"}.get(kind, ident)


# --------------------------------------------------------------------------- main

def handle(ident: str, args) -> dict:
    ERRORS.clear()
    DOWNLOAD_ERRORS.clear()
    kind, clean = normalise(ident)
    log(f"\n== {ident}  [{kind}]")
    if kind == "unknown":
        log("  not a DOI, arXiv id, PMID, or PMCID — skipped")
        return {"input": ident, "status": "unrecognised"}

    result: dict = {"input": ident, "kind": kind, "id": clean,
                    "landing_page": landing_page(kind, clean)}

    if args.bibtex_only and kind in ("pmc", "pmid"):
        msg = "no BibTeX source for this kind of identifier"
        log(f"  not checked: {msg}")
        result.update(status="not checked", errors=[msg])
        return result
    if kind in ("doi", "arxiv") and (kind == "doi" or args.bibtex_only):
        # An arXiv paper has a DOI of its own, 10.48550/arXiv.<id>, which doi.org answers.
        doi = clean if kind == "doi" else "10.48550/arXiv." + re.sub(r"v\d+$", "", clean)
        bib = crossref_bibtex(doi)
        if bib:
            result["bibtex"] = bib
            if args.out and not args.list_only:
                p = Path(args.out) / f"{safe_name(doi)}.bib"
                try:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(bib + "\n", encoding="utf-8")
                    log(f"  bibtex -> {p}")
                except OSError as e:
                    msg = f"the BibTeX file {p} could not be written ({e.strerror or e})"
                    log(f"  not checked: {msg}")
                    result["bibtex_not_checked"] = [msg]
        else:
            result["bibtex_not_checked"] = list(ERRORS)
        ERRORS.clear()                    # the BibTeX lookup is reported on its own
    if args.bibtex_only:
        if result.get("bibtex_not_checked"):
            log("  not checked: the BibTeX lookup failed: "
                + "; ".join(result["bibtex_not_checked"]))
            result["status"] = "not checked"
            result["errors"] = result["bibtex_not_checked"]
        else:
            result["status"] = "metadata only"
        return result

    candidates: list[dict] = []
    unpaywall_skipped = False
    if kind == "arxiv":
        candidates += via_arxiv(clean)
    if kind in ("pmc", "pmid"):
        candidates += via_europepmc(clean, kind)
    if kind == "doi":
        if args.email:
            candidates += via_unpaywall(clean, args.email)
        else:
            log("  Unpaywall skipped (no --email / UNPAYWALL_EMAIL)")
            unpaywall_skipped = True
        candidates += via_openalex(clean)
        candidates += via_europepmc(clean, "doi")

    if not candidates:
        if ERRORS:
            log("  not checked: every resolver errored, so no answer about open access:")
            for e in ERRORS:
                log(f"    {e}")
            if any("CERTIFICATE_VERIFY_FAILED" in e for e in ERRORS):
                log("  " + TLS_HINT.replace("\n", "\n  "))
            result["status"] = "not checked"
            result["errors"] = list(ERRORS)
        elif unpaywall_skipped:
            log("  No open-access copy found in OpenAlex or Europe PMC. Unpaywall was not asked "
                "(no --email / UNPAYWALL_EMAIL), so an open copy may still exist there.")
            log(f"  Reach it through your library: {result['landing_page']}")
            result["status"] = "no open access found"
            result["sources_not_asked"] = ["Unpaywall"]
        else:
            log("  NO open-access copy found. The paper may be paywalled.")
            log(f"  Reach it through your library: {result['landing_page']}")
            result["status"] = "no open access found"
        return result

    result["candidates"] = candidates
    log(f"  {len(candidates)} open-access candidate(s)")
    if args.list_only:
        for c in candidates:
            log(f"    - [{c['licence']}] {c['source']}: {c['url']}")
        result["status"] = "listed"
        return result

    dest = Path(args.out or ".") / f"{safe_name(clean)}.pdf"
    for c in candidates:
        log(f"  trying {c['source']} ...")
        ok, msg = download(c["url"], dest)
        if ok:
            log(f"  SAVED {dest}  ({msg})")
            result.update(status="downloaded", path=str(dest),
                          used=c["source"], licence=c["licence"])
            return result
        log(f"    {msg}")
        time.sleep(1)

    if DOWNLOAD_ERRORS:
        # A network or server failure is not a host's refusal. Nothing is said about the paper.
        log("  not checked: a download failed on the network or the server, so it is not "
            "known whether a PDF is available:")
        for e in DOWNLOAD_ERRORS:
            log(f"    {e}")
        log("  Locations the resolvers listed, to try by hand:")
        for c in candidates:
            log(f"    [{c['licence']}] {c['url']}")
        result["status"] = "not checked"
        result["errors"] = list(DOWNLOAD_ERRORS)
        return result
    log("  Every candidate failed to yield a PDF. The resolvers list these as open access;")
    log("  the hosts refused an automated request. Open one of these in a browser:")
    for c in candidates:
        log(f"    [{c['licence']}] {c['url']}")
    result["status"] = "open access, manual download needed"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("identifiers", nargs="*", help="DOI, arXiv id, PMID (7 or 8 digits, or PMID:n), or PMCID")
    ap.add_argument("--batch", help="file with one identifier per line ('#' comments allowed)")
    ap.add_argument("--out", default=".", help="output directory (default: current)")
    ap.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL"),
                    help="contact email, sent to Unpaywall only (its requirement); or set UNPAYWALL_EMAIL")
    ap.add_argument("--bibtex-only", action="store_true", help="fetch metadata, no PDF")
    ap.add_argument("--list-only", action="store_true",
                    help="show OA locations; download nothing and write no file")
    ap.add_argument("--json", help="write a JSON report to this path")
    args = ap.parse_args()

    from _manuscript import json_target_problem, output_is_input
    if args.json:
        problem = json_target_problem(args.json) or (
            f"--json {args.json}: this is the --batch file, and the script would overwrite it"
            if output_is_input(args.json, {"batch": args.batch}) else None)
        if problem:
            log(problem)
            return 2
    if args.out and Path(args.out).exists() and not Path(args.out).is_dir():
        log(f"--out {args.out}: this is a file, not a folder")
        return 2
    idents = list(args.identifiers)
    if args.batch:
        try:
            batch_text = Path(args.batch).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as e:
            log(f"cannot read the --batch file {args.batch}: {e}")
            return 2
        for line in batch_text.splitlines():
            line = re.sub(r"(^|\s)#.*$", "", line).strip()      # a `#` inside a DOI is kept
            if line:
                idents.append(line)
    if not idents:
        ap.print_help()
        return 2
    if not args.list_only:
        # Probe the output folder before the first request, so no lookup is lost to it.
        try:
            Path(args.out).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            log(f"--out {args.out}: the folder cannot be created ({e.strerror or e})")
            return 2
        if not os.access(args.out, os.W_OK | os.X_OK):
            log(f"--out {args.out}: the folder is not writable")
            return 2

    results = []
    for i, ident in enumerate(idents):
        results.append(handle(ident, args))
        if i < len(idents) - 1:
            time.sleep(1)                                    # be polite

    tally: dict[str, int] = {}
    for r in results:
        tally[r.get("status", "?")] = tally.get(r.get("status", "?"), 0) + 1
    log("\n=== " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())))
    for r in results:
        if r.get("bibtex_not_checked") and r.get("status") != "not checked":
            log(f"    not checked: BibTeX for {r['input']}: " + "; ".join(r["bibtex_not_checked"]))
    if tally.get("not checked"):
        log("    'not checked' is NOT 'no open access'. Fix the errors above and re-run.")
    if args.json:
        try:
            Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        except OSError as e:
            log(f"--json {args.json}: could not write the report ({e.strerror or e})")
            return 2
        log(f"report -> {args.json}")
    # An identifier the script did not recognise was not checked. Exit 2 when every
    # identifier was unrecognised, so nothing could start; exit 3 when something was not
    # checked, as in the other scripts of this folder.
    if tally.get("unrecognised") == len(results):
        return 2
    if (tally.get("not checked") or tally.get("unrecognised")
            or any(r.get("bibtex_not_checked") for r in results)):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
