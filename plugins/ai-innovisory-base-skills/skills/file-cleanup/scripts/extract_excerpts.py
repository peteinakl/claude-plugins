#!/usr/bin/env python3
"""
Pull a short text excerpt from files that are cheap and meaningful to read,
so Claude can write a one-line topic for each in the file-cleanup skill's
index, without reading every file end-to-end and without ever opening
anything that isn't text-bearing. images, video, audio, spreadsheets, and
other binaries are always skipped here, by design, not by omission.

Usage:
    python3 extract_excerpts.py <path1> [<path2> ...]

Prints JSON: a list of {path, name, extractable, excerpt, reason}. When
extractable is false, excerpt is null and reason explains why: not a
text-bearing type, a missing extraction tool, or too large to parse
efficiently.

Excerpts are deliberately short, capped at ~1500 characters, and for PDFs
limited to the first two pages. This is meant to give Claude enough to
name a topic in a few words, not to hand over the whole document; if
something needs a fuller read for another reason, that's a separate task
from indexing an archive run.

Supported types:
  - Plain text: .txt, .md, .rtf, .csv, .json, .yaml, .yml, .log, read directly.
  - .pdf, via the `pdftotext` command-line tool (poppler-utils) if present.
  - .docx, via the python-docx package if installed.
Everything else (including .xlsx, since it's a binary container rather than
plain text) is reported as not extractable rather than guessed at.
"""
import argparse
import json
import os
import shutil
import subprocess

TEXT_EXTENSIONS = {".txt", ".md", ".rtf", ".csv", ".json", ".yaml", ".yml", ".log"}
EXCERPT_CHAR_LIMIT = 1500
DOCX_SIZE_CAP_BYTES = 20 * 1024 * 1024
PDF_PAGE_LIMIT = 2
PDF_TIMEOUT_SECONDS = 20


def extract_plain_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read(EXCERPT_CHAR_LIMIT), None
    except OSError as e:
        return None, f"could not read file: {e}"


def extract_pdf(path):
    if not shutil.which("pdftotext"):
        return None, ("pdftotext not installed (part of poppler-utils); "
                       "install it to enable PDF topics")
    try:
        result = subprocess.run(
            ["pdftotext", "-l", str(PDF_PAGE_LIMIT), path, "-"],
            capture_output=True, text=True, timeout=PDF_TIMEOUT_SECONDS,
        )
        text = result.stdout.strip()
        if not text:
            return None, "no extractable text (likely a scanned or image-only PDF)"
        return text[:EXCERPT_CHAR_LIMIT], None
    except subprocess.TimeoutExpired:
        return None, "pdftotext timed out"
    except OSError as e:
        return None, f"pdftotext failed: {e}"


def extract_docx(path):
    if os.path.getsize(path) > DOCX_SIZE_CAP_BYTES:
        return None, "docx file too large to parse efficiently"
    try:
        import docx
    except ImportError:
        return None, ("python-docx not installed; run "
                       "'pip install python-docx --break-system-packages' to enable docx topics")
    try:
        doc = docx.Document(path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        if not text:
            return None, "no extractable paragraph text found"
        return text[:EXCERPT_CHAR_LIMIT], None
    except Exception as e:
        return None, f"docx parsing failed: {e}"


def excerpt_for(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTENSIONS:
        return extract_plain_text(path)
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".docx":
        return extract_docx(path)
    return None, "not a text-bearing type, skipped by design (e.g. image, video, audio, spreadsheet, archive)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    results = []
    for path in args.paths:
        name = os.path.basename(path)
        if not os.path.isfile(path):
            results.append({
                "path": path, "name": name, "extractable": False,
                "excerpt": None, "reason": "file not found",
            })
            continue

        excerpt, reason = excerpt_for(path)
        results.append({
            "path": path,
            "name": name,
            "extractable": excerpt is not None,
            "excerpt": excerpt,
            "reason": reason,
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
