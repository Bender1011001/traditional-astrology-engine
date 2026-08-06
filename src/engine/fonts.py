"""Unicode font support for PDF rendering.

ReportLab's built-in Type1 fonts (Times-Roman, Helvetica, ...) are limited to
WinAnsi encoding. Any non-Latin-1 text — Cyrillic, Greek, Polish diacritics —
renders as black boxes or vanishes entirely.

Registering a TrueType font under the SAME name as a built-in overrides it
everywhere, so existing stylesheets that ask for "Times-Roman" transparently
gain full Unicode coverage with no other code change.

This is best-effort and non-fatal by design: if no suitable font is found the
built-ins remain in place and Latin-script reports render exactly as before.
Never let a missing font break report generation.
"""

from __future__ import annotations

import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)

# Candidate files per logical font, in preference order. Windows first (dev
# machines), then the fonts commonly present in Linux containers.
#
# NOTE for deployment: the Cloud Run image is python:3.10-slim, which ships with
# NO fonts at all. To serve non-Latin reports in production, install
# `fonts-dejavu-core` (or bundle the TTFs) in the Dockerfile. Until then this
# helper is a no-op there and non-Latin PDFs must be generated locally.
_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Times-Roman": (
        r"C:\Windows\Fonts\times.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ),
    "Times-Bold": (
        r"C:\Windows\Fonts\timesbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
    ),
    "Times-Italic": (
        r"C:\Windows\Fonts\timesi.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
    ),
    "Times-BoldItalic": (
        r"C:\Windows\Fonts\timesbi.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf",
    ),
    "Helvetica": (
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ),
    "Helvetica-Bold": (
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ),
    "Helvetica-Oblique": (
        r"C:\Windows\Fonts\ariali.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ),
}

# A font carrying the astrological glyph range: zodiac signs (U+2648-2653),
# planets (U+2609, 263D, 263F, 2640, 2642-2644), nodes (U+260A-260B) and the
# retrograde mark (U+211E). Standard text faces do NOT have these — Times and
# Arial carry only two of the seven planets — so the chart wheel falls back to
# letter abbreviations when none of these is available.
ASTRO_GLYPH_FONT = "AstroGlyph"
_GLYPH_CANDIDATES: tuple[str, ...] = (
    r"C:\Windows\Fonts\seguisym.ttf",  # Segoe UI Symbol: full coverage
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    r"C:\Windows\Fonts\DejaVuSans.ttf",
)

_registered = False
_glyphs_registered = False


def _first_existing(paths: Iterable[str]) -> str | None:
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def ensure_astro_glyphs() -> bool:
    """Register a font able to draw zodiac and planet glyphs.

    Returns True when `ASTRO_GLYPH_FONT` is usable. Callers must fall back to
    text labels when this returns False.
    """
    global _glyphs_registered
    if _glyphs_registered:
        return True
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except Exception:  # pragma: no cover
        return False

    path = _first_existing(_GLYPH_CANDIDATES)
    if not path:
        logger.info("No astrological glyph font found; wheel will use text labels.")
        return False
    try:
        pdfmetrics.registerFont(TTFont(ASTRO_GLYPH_FONT, path))
        # Confirm the face actually carries the glyphs rather than trusting the
        # filename — a font can register successfully and still draw blanks.
        face = pdfmetrics.getFont(ASTRO_GLYPH_FONT).face
        probe = "\u2648\u2609\u263D\u2644"  # Aries, Sun, Moon, Saturn
        if any(face.charToGlyph.get(ord(ch)) in (None, 0) for ch in probe):
            logger.info("Glyph font %s lacks astrological glyphs; using text.", path)
            return False
    except Exception as exc:
        logger.warning("Could not register glyph font %s: %r", path, exc)
        return False

    _glyphs_registered = True
    return True


def ensure_unicode_fonts() -> bool:
    """Override the built-in PDF fonts with Unicode-capable TrueType files.

    Returns True when the serif face (the report body font) gained Unicode
    coverage. Safe to call repeatedly; the work happens once.
    """
    global _registered
    if _registered:
        return True

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except Exception as exc:  # pragma: no cover - reportlab always present
        logger.warning("Unicode fonts unavailable, reportlab import failed: %r", exc)
        return False

    body_ok = False
    for name, candidates in _CANDIDATES.items():
        path = _first_existing(candidates)
        if not path:
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            if name == "Times-Roman":
                body_ok = True
        except Exception as exc:
            logger.warning("Could not register %s from %s: %r", name, path, exc)

    if body_ok:
        _registered = True
        logger.info("Unicode fonts registered; non-Latin scripts will render.")
    else:
        logger.warning(
            "No Unicode serif font found. Non-Latin text will not render in PDFs. "
            "Install fonts-dejavu-core or liberation fonts in the image."
        )
    return body_ok


def supports_non_latin() -> bool:
    """True when a PDF generated now would render non-Latin text correctly."""
    return _registered or ensure_unicode_fonts()
