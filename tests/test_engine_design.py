"""Invariantes WCAG de las familias visuales: contraste real, no por suposición."""

from __future__ import annotations

from faro.business import contrast_ratio
from faro.engine.design import _PRESETS, DesignTokens


def _families() -> tuple[DesignTokens, ...]:
    return tuple(_PRESETS.values())


def test_body_text_contrast_meets_aa() -> None:
    """El texto de cuerpo (ink sobre paper) cumple AA (>=4.5) en toda familia."""
    for t in _families():
        assert contrast_ratio(t.ink, t.paper) >= 4.5, t.name


def test_accent_text_is_readable_on_its_paper() -> None:
    """El accent se usa como color de texto; debe cumplir AA (>=4.5) sobre su paper.

    Regresión de TD-064: el bronce de autoridad (3.53:1 crudo) y el ámbar de
    estudio (4.37:1) suspendían AA como texto pequeño (.index .n a 15px). El
    accent emitido se oscurece ahora contra el paper real hasta >=4.5.
    """
    for t in _families():
        accent = t._accent_text()
        assert contrast_ratio(accent, t.paper) >= 4.5, f"{t.name}: {accent}"


def test_on_brand_text_meets_aa_over_brand() -> None:
    """El texto sobre el color de marca (botones) cumple AA en toda familia."""
    for t in _families():
        assert contrast_ratio(t.on_brand(), t.brand) >= 4.5, t.name


def test_dark_family_keeps_light_accent() -> None:
    """En familia oscura el accent NO se oscurece (empeoraría el contraste)."""
    gym = _PRESETS["gimnasio"]
    assert gym.dark
    assert gym._accent_text() == gym.accent
    assert contrast_ratio(gym._accent_text(), gym.paper) >= 4.5


def test_css_vars_emits_corrected_accent() -> None:
    """El bloque :root emite el accent corregido, no el crudo, en paper claro."""
    autoridad = _PRESETS["autoridad"]
    css = autoridad.to_css_vars()
    assert f"--accent:{autoridad._accent_text()};" in css
    # El crudo (3.53:1) ya no debe viajar al CSS como valor de --accent.
    assert f"--accent:{autoridad.accent};" not in css
