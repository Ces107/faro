"""Tipografías reales embebidas (la palanca nº1 contra el "look IA").

La investigación es tajante: el delator número uno de una web hecha por IA es
``system-ui``/Inter sin una serif de display con carácter. Faro embebe fuentes
OFL de verdad (subset latino, woff2, 20-44 KB) como ``@font-face`` en base64, de
modo que la web sigue siendo autocontenida (sin CDN, sin cookies de terceros, sin
dependencia de red en tiempo de ejecución) pero tiene tipografía de estudio.

Cada familia de plantilla declara qué fuentes usa; solo se inyectan esas, para no
cargar peso de más. Las fuentes son SIL Open Font License (ver assets/fonts/OFL).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"


@dataclass(frozen=True)
class FontFace:
    """Una fuente embebible: nombre CSS, fichero y rango de pesos (variable)."""

    family: str
    file: str
    weight: str = "400"
    style: str = "normal"


# Catálogo de fuentes disponibles para las familias (todas OFL, subset latino).
_FONTS: dict[str, FontFace] = {
    "fraunces": FontFace("Fraunces", "fraunces-vf.woff2", "100 900"),
    "fraunces-italic": FontFace("Fraunces", "fraunces-italic-vf.woff2", "100 900", "italic"),
    "bricolage": FontFace("Bricolage Grotesque", "bricolage-vf.woff2", "200 800"),
    "archivo": FontFace("Archivo", "archivo-vf.woff2", "100 900"),
    "instrument": FontFace("Instrument Serif", "instrument-serif.woff2", "400"),
}


@lru_cache(maxsize=32)
def _b64(file: str) -> str:
    return base64.b64encode((_FONT_DIR / file).read_bytes()).decode("ascii")


def _face_rule(face: FontFace) -> str:
    data = _b64(face.file)
    return (
        "@font-face{font-family:'" + face.family + "';font-style:" + face.style
        + ";font-weight:" + face.weight + ";font-display:swap;"
        + "src:url(data:font/woff2;base64," + data + ") format('woff2');}"
    )


def font_face_css(ids: tuple[str, ...]) -> str:
    """CSS ``@font-face`` (base64) de las fuentes pedidas, deduplicado y en orden."""
    seen: set[str] = set()
    rules: list[str] = []
    for fid in ids:
        face = _FONTS.get(fid)
        if face is None or fid in seen:
            continue
        seen.add(fid)
        rules.append(_face_rule(face))
    return "".join(rules)


def family_name(font_id: str) -> str:
    """Nombre CSS de la familia (para construir el font-family stack)."""
    face = _FONTS.get(font_id)
    return face.family if face else ""


def available() -> tuple[str, ...]:
    return tuple(_FONTS)
