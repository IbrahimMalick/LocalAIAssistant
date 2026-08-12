"""
Document loaders.

Turn a source file on disk into clean plain text. Text formats work with the
standard library alone. Heavier formats (PDF, EPUB) use optional libraries and
degrade gracefully with a clear message if those libraries are not installed —
the same pattern the TTS backends use.

Supported out of the box (stdlib):
    .txt .md .markdown        plain text / Markdown
    .vtt .srt                 subtitle / transcript files (timestamps stripped)

Supported with optional libraries:
    .pdf                      requires `pypdf`   (pip install pypdf)
    .epub                     requires `ebooklib` + `beautifulsoup4`, with a
                              stdlib zip+HTML-strip fallback if they're absent
"""

from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path
from typing import List

# File extensions we know how to read. Used by the ingester to decide what to
# pick up from a source directory.
TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
TRANSCRIPT_EXTENSIONS = {".vtt", ".srt"}
PDF_EXTENSIONS = {".pdf"}
EPUB_EXTENSIONS = {".epub"}
SUPPORTED_EXTENSIONS = (
    TEXT_EXTENSIONS | TRANSCRIPT_EXTENSIONS | PDF_EXTENSIONS | EPUB_EXTENSIONS
)


class LoaderError(RuntimeError):
    """Raised when a file cannot be read into text."""


# ---------------------------------------------------------------------------
# Individual format loaders
# ---------------------------------------------------------------------------
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


_TS_LINE = re.compile(r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->")
_CUE_NUM = re.compile(r"^\d+$")


def load_transcript(path: Path) -> str:
    """
    Read a .vtt/.srt subtitle file into clean prose.

    Drops the ``WEBVTT`` header, cue numbers, and ``00:00:00.000 -->`` timing
    lines, then de-duplicates consecutive repeated caption lines (common in
    auto-generated captions).
    """
    lines: List[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.upper().startswith("WEBVTT"):
            continue
        if _TS_LINE.match(line) or "-->" in line:
            continue
        if _CUE_NUM.match(line):
            continue
        # Strip inline caption tags like <c> or <00:00:00.000>.
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line:
            continue
        if lines and lines[-1] == line:
            continue  # collapse duplicated caption lines
        lines.append(line)
    return " ".join(lines)


def load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise LoaderError(
            f"Reading PDFs requires 'pypdf' (pip install pypdf). "
            f"Cannot load {path.name}. Convert it to text/Markdown, or install "
            "pypdf. See setup/knowledge_setup.md."
        ) from exc
    try:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:  # pragma: no cover - depends on file
        raise LoaderError(f"Failed to read PDF {path.name}: {exc}") from exc


def load_epub(path: Path) -> str:
    """
    Read an EPUB. Prefers ebooklib+BeautifulSoup for clean extraction; falls
    back to a stdlib zip + naive HTML strip so it still works with no extra deps.
    """
    try:
        from ebooklib import epub  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore

        book = epub.read_epub(str(path))
        parts: List[str] = []
        for item in book.get_items():
            if item.get_type() == 9:  # ITEM_DOCUMENT
                soup = BeautifulSoup(item.get_content(), "html.parser")
                parts.append(soup.get_text(" "))
        return "\n".join(parts)
    except ImportError:
        # Stdlib fallback: unzip and strip tags from the XHTML documents.
        return _epub_stdlib_fallback(path)
    except Exception as exc:  # pragma: no cover - depends on file
        raise LoaderError(f"Failed to read EPUB {path.name}: {exc}") from exc


_TAG_RE = re.compile(r"<[^>]+>")


def _epub_stdlib_fallback(path: Path) -> str:
    parts: List[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            names = [
                n for n in zf.namelist()
                if n.lower().endswith((".xhtml", ".html", ".htm"))
            ]
            for name in names:
                raw = zf.read(name).decode("utf-8", errors="replace")
                text = _TAG_RE.sub(" ", raw)
                parts.append(html.unescape(text))
    except Exception as exc:  # pragma: no cover - depends on file
        raise LoaderError(f"Failed to read EPUB {path.name}: {exc}") from exc
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
def load_document(path: Path) -> str:
    """Load any supported file into plain text, dispatching on extension."""
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return load_text(path)
    if suffix in TRANSCRIPT_EXTENSIONS:
        return load_transcript(path)
    if suffix in PDF_EXTENSIONS:
        return load_pdf(path)
    if suffix in EPUB_EXTENSIONS:
        return load_epub(path)
    raise LoaderError(
        f"Unsupported file type '{suffix}' for {path.name}. "
        f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
    )


# Filenames that are folder documentation, not knowledge content, and should
# never be ingested.
_IGNORED_NAMES = {"readme.md", "readme.txt", "readme"}


def iter_source_files(root: Path) -> List[Path]:
    """Return all supported knowledge files under ``root`` (recursively), sorted.

    Skips folder-documentation files (README) so they don't pollute the index.
    """
    if not root.exists():
        return []
    files = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
        and p.name.lower() not in _IGNORED_NAMES
    ]
    return sorted(files)
