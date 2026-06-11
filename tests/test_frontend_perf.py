"""Mejoras de rendimiento y ajuste móvil del frontend de las webs generadas.

Tres palancas objetivas, generales a todas las familias y de bajo riesgo:
- LCP: el hero a sangre usa la foto como fondo CSS (prioridad mínima por
  defecto); se precarga con prioridad alta para que pinte cuanto antes en la
  demo en el móvil a 4G. Los heroes sin foto (póster de color, editorial) no
  precargan nada (no hay imagen que sea el LCP).
- Ajuste móvil: las alturas del hero usan unidades de viewport dinámico (dvh)
  con fallback a vh, para que el hero encaje en el viewport real del móvil sin
  el salto que provoca la barra de URL.
- Pulido: la barra de navegación gana una sombra sutil al hacer scroll (la
  clase la pone el JS; antes era una clase sin estilo).
"""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing

_PHOTO = "https://example.com/local.jpg"


def _biz(sector: Sector, **kw: object) -> BusinessProfile:
    base: dict[str, object] = {
        "name": "Negocio", "sector": sector, "city": "Sagunto",
        "phone": "961112233", "services": ("Uno", "Dos"),
    }
    base.update(kw)
    return BusinessProfile(**base)  # type: ignore[arg-type]


def test_photo_hero_preloads_lcp_image() -> None:
    # DENTAL -> familia clinica -> hero 'photo': la 1ª foto es el LCP.
    html = build_landing(_biz(Sector.DENTAL, photos=(_PHOTO,)), use_live=False)
    assert f'<link rel="preload" as="image" href="{_PHOTO}" fetchpriority="high" />' in html
    # La foto se usa de fondo del hero (no es solo precarga huérfana).
    assert f"url('{_PHOTO}')" in html


def test_no_preload_when_hero_has_no_photo() -> None:
    # Sin fotos no hay imagen que precargar.
    assert 'rel="preload" as="image"' not in build_landing(
        _biz(Sector.DENTAL), use_live=False
    )
    # ASESORIA -> familia autoridad -> hero 'editorial': no usa la foto como
    # fondo (va a la galería), así que no se precarga aunque haya fotos.
    editorial = build_landing(_biz(Sector.ASESORIA, photos=(_PHOTO,)), use_live=False)
    assert "hero-editorial" in editorial
    assert 'rel="preload" as="image"' not in editorial


def test_hero_heights_use_dynamic_viewport_with_fallback() -> None:
    html = build_landing(_biz(Sector.DENTAL, photos=(_PHOTO,)), use_live=False)
    # dvh para el viewport real del móvil + el vh como fallback (navegadores viejos).
    assert "93dvh" in html and "93vh" in html
    assert "82dvh" in html and "82vh" in html


def test_nav_gains_shadow_on_scroll() -> None:
    # El JS togglea .scrolled pasados 8px; el CSS debe darle estilo (antes no).
    html = build_landing(_biz(Sector.DENTAL), use_live=False)
    assert ".nav.scrolled{" in html


def test_photo_hero_is_cinematic() -> None:
    # Hero con foto: capa ::before con ken-burns + indicador de scroll.
    html = build_landing(_biz(Sector.DENTAL, photos=(_PHOTO,)), use_live=False)
    assert ".hero-photo::before{" in html
    assert "@keyframes faro-ken{" in html
    assert '<div class="scroll-cue" aria-hidden="true"></div>' in html


def test_no_scroll_cue_without_photo_hero() -> None:
    # El indicador de scroll es un elemento del hero con foto, no del editorial.
    editorial = build_landing(_biz(Sector.ASESORIA, photos=(_PHOTO,)), use_live=False)
    assert "hero-editorial" in editorial
    assert '<div class="scroll-cue"' not in editorial


def test_cookie_notice_is_compact_toast() -> None:
    # El aviso es un toast fino en una esquina, no el cajón ancho de antes.
    html = build_landing(_biz(Sector.DENTAL), use_live=False)
    assert "width:min(340px,calc(100% - 32px))" in html
