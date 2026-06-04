"""Librerías de motion vendorizadas (inline, sin CDN) para el producto.

GSAP core + ScrollTrigger + SplitText (gratis y redistribuibles desde 2025, las
liberó Webflow) y Lenis (MIT) se embeben como ``<script>`` en cada landing, de
modo que la web sigue siendo autocontenida —sin CDN, sin cookies de terceros, sin
dependencia de red en runtime— pero con motion de nivel agencia. ~144 KB sin
comprimir (~50 KB con gzip del hosting), un precio razonable para una one-page
premium que el cliente sube tal cual.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_JS_DIR = Path(__file__).resolve().parent / "assets" / "js"
_LIBS: tuple[str, ...] = (
    "gsap.min.js",
    "ScrollTrigger.min.js",
    "SplitText.min.js",
)


@lru_cache(maxsize=1)
def motion_libs_inline() -> str:
    """Las librerías de motion como bloques ``<script>`` inline, en orden de carga."""
    blocks: list[str] = []
    for name in _LIBS:
        code = (_JS_DIR / name).read_text(encoding="utf-8")
        blocks.append(f"<script>{code}</script>")
    return "".join(blocks)
