"""Identidad visual de una familia de plantilla, como datos (no CSS a mano).

``DesignTokens`` captura las decisiones que separan una web de estudio de una web
"vibecoded": qué tipografía de display real usa, una paleta audaz (no pastel) con
neutro cálido (no el gris-azulado frío de demo), bordes intencionales (gruesos de
tinta o ninguno, nunca el 1px gris por defecto), radios pequeños (0-4px, no 16),
y el tratamiento del hero. ``to_css_vars`` lo traduce a variables CSS que el
chasis y los bloques consumen.

Las paletas y emparejamientos salen de la investigación de diseño
(``state/work/out/faro-vibecoded-research-*``): Fraunces/Instrument para lo
editorial, Bricolage/Archivo para lo contemporáneo; terracota+crema para
gastronomía, verde profundo+hueso para salud, tinta+un acento para autoridad.
"""

from __future__ import annotations

from dataclasses import dataclass

from faro.engine.fonts import family_name

# Fallbacks del sistema con carácter (si la fuente embebida no cargara): una
# serif de verdad (Georgia/Iowan) y una grotesque, nunca system-ui a secas.
_SERIF_FB = "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Times New Roman', serif"
_SANS_FB = "'Helvetica Neue', Helvetica, Arial, system-ui, sans-serif"
_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


@dataclass(frozen=True)
class DesignTokens:
    """La identidad visual de una familia. Inmutable; se traduce a CSS."""

    name: str
    font_display: str  # id de fuente embebida (engine.fonts)
    display_is_serif: bool
    ink: str  # tinta (casi negro, cálido)
    paper: str  # fondo (neutro cálido, NO gris-azulado)
    brand: str  # color de marca audaz (no pastel)
    accent: str  # acento nítido
    body_font: str = ""  # id de fuente embebida para el cuerpo; "" = sistema
    dark: bool = False
    radius: int = 3  # px; 0-4, nunca 16
    border_px: int = 2  # grosor de las reglas de tinta (0 = sin bordes)
    hero: str = "editorial"  # editorial | poster | photo | gallery | split
    service_style: str = "index"  # carta | grid | index | list
    eyebrow: str = "caps"  # caps | smallcaps
    texture: bool = False
    paper_2: str = ""  # superficie alterna (bloques); se deriva si vacío

    def fonts(self) -> tuple[str, ...]:
        ids = [self.font_display]
        if self.body_font:
            ids.append(self.body_font)
        return tuple(ids)

    def display_stack(self) -> str:
        fam = family_name(self.font_display)
        fb = _SERIF_FB if self.display_is_serif else _SANS_FB
        return f"'{fam}', {fb}" if fam else fb

    def body_stack(self) -> str:
        if self.body_font:
            fam = family_name(self.body_font)
            if fam:
                return f"'{fam}', {_SANS_FB}"
        return _SANS_FB

    def _surface_2(self) -> str:
        if self.paper_2:
            return self.paper_2
        return "#11131a" if self.dark else "#ffffff"

    def to_css_vars(self) -> str:
        """Bloque ``:root`` con las variables de la familia."""
        text_soft = "#b9b3a7" if self.dark else "#5b5650"
        line = "rgba(255,255,255,.16)" if self.dark else "rgba(20,18,15,.14)"
        return (
            ":root{"
            f"--ink:{self.ink};--paper:{self.paper};--paper-2:{self._surface_2()};"
            f"--brand:{self.brand};--accent:{self.accent};"
            f"--text-soft:{text_soft};--line:{line};"
            f"--radius:{self.radius}px;--border:{self.border_px}px;"
            f"--font-display:{self.display_stack()};"
            f"--font-body:{self.body_stack()};"
            f"--font-mono:{_MONO};"
            "}"
        )


# --- Presets por familia -----------------------------------------------------
# Cada uno es una dirección de arte distinta, no el mismo con otro color.

AURORA = DesignTokens(
    name="aurora",
    font_display="bricolage", display_is_serif=False,
    ink="#181410", paper="#f6f3ee", brand="#1f6f5c", accent="#c2410c",
    body_font="archivo", radius=4, border_px=2, hero="editorial",
    service_style="index", eyebrow="caps",
)

CARTA = DesignTokens(
    name="carta",
    font_display="fraunces", display_is_serif=True,
    ink="#26140d", paper="#f3e9dd", brand="#9a3412", accent="#b45309",
    body_font="archivo", radius=2, border_px=2, hero="photo",
    service_style="carta", eyebrow="smallcaps", texture=True,
    paper_2="#efe2d2",
)

CLINICA = DesignTokens(
    name="clinica",
    font_display="fraunces", display_is_serif=True,
    ink="#10211c", paper="#f1f4f0", brand="#15564a", accent="#2f7d6b",
    body_font="archivo", radius=4, border_px=1, hero="split",
    service_style="grid", eyebrow="caps", paper_2="#ffffff",
)

AUTORIDAD = DesignTokens(
    name="autoridad",
    font_display="instrument", display_is_serif=True,
    ink="#14181f", paper="#f4f2ec", brand="#1e293b", accent="#9a7b4f",
    body_font="archivo", radius=0, border_px=1, hero="editorial",
    service_style="index", eyebrow="smallcaps", paper_2="#ffffff",
)

INDUSTRIAL = DesignTokens(
    name="industrial",
    font_display="archivo", display_is_serif=False,
    ink="#16130f", paper="#ece7df", brand="#b91c1c", accent="#1f2937",
    body_font="archivo", radius=0, border_px=3, hero="poster",
    service_style="list", eyebrow="caps", texture=True, paper_2="#e2dccf",
)

ESTUDIO = DesignTokens(
    name="estudio",
    font_display="fraunces", display_is_serif=True,
    ink="#0f0f10", paper="#f4f1ec", brand="#171717", accent="#a16207",
    body_font="archivo", radius=0, border_px=1, hero="gallery",
    service_style="grid", eyebrow="smallcaps", paper_2="#ffffff",
)

GIMNASIO = DesignTokens(
    name="gimnasio",
    font_display="bricolage", display_is_serif=False,
    ink="#f4f4f5", paper="#0d0d0f", brand="#84cc16", accent="#f59e0b",
    body_font="archivo", dark=True, radius=2, border_px=2, hero="poster",
    service_style="list", eyebrow="caps", paper_2="#15151a",
)

_PRESETS: dict[str, DesignTokens] = {
    t.name: t for t in (AURORA, CARTA, CLINICA, AUTORIDAD, INDUSTRIAL, ESTUDIO, GIMNASIO)
}


def tokens_for(family: str) -> DesignTokens:
    return _PRESETS.get(family, AURORA)
