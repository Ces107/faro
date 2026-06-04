"""Genera el escaparate estático de Faro para GitHub Pages.

Produce, en ``docs/``:
- ``ejemplos/<sector>/index.html`` + ``aviso-legal.html``: la web de ejemplo
  COMPLETA de cada familia (lo que Faro genera, autocontenida).
- ``shots/<sector>.png``: captura real de página completa de cada ejemplo, hecha
  con Playwright en el momento del build (es la prueba de que Faro produce webs
  de verdad: el escaparate enseña, no solo cuenta).
- ``shots/_aislop.png`` + ``shots/_faro-compare.png``: el mismo negocio por una
  IA del montón vs. por Faro (para el deslizador antes/después).
- ``shots/og.png``: imagen Open Graph 1200x630 para compartir en redes.
- ``index.html``: la portada premium (hero con baraja en perspectiva, antes/
  después, familias con scroll horizontal, rejilla de ejemplos con scroll al
  pasar el ratón y lightbox). Plantilla en ``tools/showcase_assets/``.

Las fotos y reseñas son de muestra (en un encargo real las pone el negocio).

Uso: ``python tools/build_showcase.py``  (requiere ``playwright`` + chromium).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from faro.business import BusinessProfile, Sector
from faro.engine.demo import demo_data
from faro.engine.design import tokens_for
from faro.engine.fonts import font_face_css
from faro.engine.registry import template_for
from faro.pack import build_pack

_ROOT = Path(__file__).resolve().parents[1]
_DOCS = _ROOT / "docs"
_SHOTS = _DOCS / "shots"
_ASSETS = Path(__file__).resolve().parent / "showcase_assets"


@dataclass(frozen=True)
class Family:
    """Una familia del escaparate: su sector representativo y su gancho."""

    key: str
    sector: Sector
    desc: str


_FAMILIES: list[Family] = [
    Family("carta", Sector.BAR, "Foto a sangre, carta tipográfica con precios y serif cálida."),
    Family("clinica", Sector.DENTAL, "Sereno, de confianza, con cita y valoración real."),
    Family("autoridad", Sector.ASESORIA, "Serif de autoridad, sobrio, institucional, sin adornos."),
    Family("industrial", Sector.TALLER, "Tipografía potente, alto contraste, presupuesto claro."),
    Family("estudio", Sector.PELUQUERIA, "La galería manda: editorial elegante, fotográfico."),
    Family("gimnasio", Sector.GIMNASIO, "Modo oscuro, acento vivo, energía de cartel."),
    Family("aurora", Sector.COMERCIO, "Editorial limpio y versátil para cualquier negocio."),
]


def _business(sector: Sector) -> BusinessProfile:
    return BusinessProfile.from_form(demo_data(sector))


def _write_example(sector: Sector) -> None:
    pack = build_pack(_business(sector), use_live=False)
    folder = _DOCS / "ejemplos" / sector.value
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(pack.landing_html, encoding="utf-8")
    (folder / "aviso-legal.html").write_text(pack.legal_html, encoding="utf-8")


def _aislop_html(sector: Sector) -> str:
    business = _business(sector)
    tpl = (_ASSETS / "aislop.template.html").read_text(encoding="utf-8")
    return tpl.replace("__NAME__", business.name).replace("__CITY__", business.city)


# --- Capturas (Playwright) ---------------------------------------------------

# Fuerza la carga de TODAS las imágenes (las galerías usan loading="lazy" y de lo
# contrario no aparecen en una captura sin scroll), revela los bloques con
# data-reveal y oculta el aviso de cookies. Devuelve una promesa que Playwright espera.
_PREP_JS = """() => {
  document.querySelectorAll('[data-reveal]').forEach(e => e.classList.add('vis'));
  document.querySelectorAll('[data-r]').forEach(e => e.classList.add('in'));
  var ck = document.getElementById('cookie'); if (ck) ck.classList.remove('show');
  document.body.classList.remove('cookie-open');
  var imgs = [].slice.call(document.images);
  imgs.forEach(i => { i.loading = 'eager'; });
  return new Promise(res => {
    // Recorre TODA la página en pasos de un viewport para disparar cada imagen
    // lazy (un solo scroll-a-fondo deja sin cargar las de media página).
    var H = document.body.scrollHeight, step = Math.max(320, innerHeight * 0.85), y = 0;
    (function walk(){
      window.scrollTo(0, y);
      if (y < H) { y += step; setTimeout(walk, 130); return; }
      var t0 = Date.now();
      (function poll(){
        var done = imgs.filter(i => i.complete && i.naturalWidth > 0).length;
        if (done >= imgs.length || Date.now() - t0 > 15000) {
          window.scrollTo(0, 0); setTimeout(res, 450);
        } else setTimeout(poll, 250);
      })();
    })();
  });
}"""


def _shoot(page, url: str, out: Path, *, full: bool = True, quality: int = 72) -> None:
    page.goto(url, wait_until="networkidle")
    page.evaluate(_PREP_JS)
    page.screenshot(path=str(out), type="jpeg", quality=quality, full_page=full)


def _capture_all() -> None:
    """Captura JPEG (no PNG: las páginas con foto pesan megas en PNG) a 1x: las
    tarjetas se muestran pequeñas y no necesitan retina, así el sitio vuela."""
    from playwright.sync_api import sync_playwright

    _SHOTS.mkdir(parents=True, exist_ok=True)
    tmp_aislop = _SHOTS / "_aislop.html"
    tmp_aislop.write_text(_aislop_html(Sector.DENTAL), encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Páginas completas de cada ejemplo (para las tarjetas con scroll al pasar
        # el ratón). En reduced-motion: el motor GSAP se apaga y rinde el layout
        # estático limpio (sin pins ni Lenis que descoloquen la captura).
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.emulate_media(reduced_motion="reduce")
        for fam in _FAMILIES:
            url = (_DOCS / "ejemplos" / fam.sector.value / "index.html").as_uri()
            _shoot(page, url, _SHOTS / f"{fam.sector.value}.jpg", full=True)
            print(f"  captura {fam.sector.value}.jpg")
        page.close()
        # Antes/después: recorte de visor a igual encuadre (1100x820), algo más nítido.
        comp = browser.new_page(viewport={"width": 1100, "height": 820}, device_scale_factor=2)
        comp.emulate_media(reduced_motion="reduce")
        _shoot(comp, tmp_aislop.as_uri(), _SHOTS / "_aislop.jpg", full=False, quality=80)
        faro_url = (_DOCS / "ejemplos" / Sector.DENTAL.value / "index.html").as_uri()
        _shoot(comp, faro_url, _SHOTS / "_faro-compare.jpg", full=False, quality=80)
        comp.close()
        # Imagen Open Graph 1200x630 (2x para nitidez al compartir).
        og_html = _SHOTS / "_og.html"
        og_html.write_text(_og_html(), encoding="utf-8")
        og = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
        og.goto(og_html.as_uri(), wait_until="networkidle")
        og.screenshot(path=str(_SHOTS / "og.jpg"), type="jpeg", quality=84, full_page=False)
        og.close()
        browser.close()
    tmp_aislop.unlink(missing_ok=True)
    (_SHOTS / "_og.html").unlink(missing_ok=True)


# --- Composición del index ---------------------------------------------------


def _og_html() -> str:
    tpl = (_ASSETS / "og.template.html").read_text(encoding="utf-8")
    return tpl.replace("{{FONTS}}", font_face_css(("fraunces", "archivo")))


def _palette(key: str) -> str:
    t = tokens_for(key)
    chips = (t.brand, t.accent, t.paper, t.ink)
    return "".join(f'<i style="background:{c}"></i>' for c in chips)


def _family_panel(fam: Family) -> str:
    from faro.engine.fonts import family_name

    t = tokens_for(fam.key)
    spec = template_for(fam.sector)
    font = family_name(t.font_display) or "Sistema"
    url = f"ces107.github.io/faro/ejemplos/{fam.sector.value}"
    return f"""
      <article class="fam-panel" data-r>
        <div class="fam-mock">
          <div class="fam-bar"><i></i><i></i><i></i><span class="url">{url}</span></div>
          <div class="fam-shot"><img src="shots/{fam.sector.value}.jpg" loading="lazy"
            alt="Web de ejemplo de la familia {spec.name}" width="1280" /></div>
        </div>
        <div class="fam-meta">
          <div><div class="name">{spec.name}</div><div class="desc">{fam.desc}</div></div>
          <div class="tags"><span class="fam-font">{font}</span>
            <div class="fam-palette">{_palette(fam.key)}</div></div>
        </div>
      </article>"""


def _card(fam: Family) -> str:
    t = tokens_for(fam.key)
    spec = template_for(fam.sector)
    biz = _business(fam.sector)
    href = f"ejemplos/{fam.sector.value}/index.html"
    return f"""
      <a class="exa" href="{href}" data-fam="{fam.key}" data-href="{href}"
         data-title="{spec.name} · {biz.name}" style="--cb:{t.brand}"
         aria-label="Ejemplo: {biz.name}, familia {spec.name}">
        <div class="exa-frame">
          <div class="exa-bar"><i></i><i></i><i></i></div>
          <div class="exa-scroll"><img src="shots/{fam.sector.value}.jpg" loading="lazy"
            alt="Web de {biz.name}" width="1280" /></div>
          <span class="exa-open">Abrir web ↗</span>
        </div>
        <div class="exa-cap">
          <div><div class="fam">{spec.name}</div><div class="biz">{biz.name}</div></div>
          <span class="swatch"></span>
        </div>
      </a>"""


def _filters() -> str:
    chips = ['<button class="chip on" data-f="all">Todas</button>']
    for fam in _FAMILIES:
        name = template_for(fam.sector).name
        chips.append(f'<button class="chip" data-f="{fam.key}">{name}</button>')
    return "".join(chips)


def _ribbon() -> str:
    words = []
    for fam in _FAMILIES:
        words.append(f"<span>{template_for(fam.sector).name}</span>")
    extras = ["Tipografía real", "Sin cookies", "Un solo HTML", "Listo en minutos"]
    for e in extras:
        words.append(f"<span>{e}</span>")
    return "".join(words)


def _hero_deck() -> str:
    picks = [(Sector.BAR, "s1"), (Sector.DENTAL, "s2"), (Sector.GIMNASIO, "s3")]
    out = []
    for sector, cls in picks:
        out.append(
            f'<div class="shot {cls}"><div class="winbar"><i></i><i></i><i></i></div>'
            f'<div class="winshot"><img src="shots/{sector.value}.jpg" loading="eager" '
            f'alt="" width="1280" /></div></div>'
        )
    return "".join(out)


def _hero_legend() -> str:
    """Siete muestras con el color de marca de cada familia (prueba visual de '7 mundos')."""
    out = []
    for fam in _FAMILIES:
        out.append(
            f'<i style="background:{tokens_for(fam.key).brand}" '
            f'title="{template_for(fam.sector).name}"></i>'
        )
    return "".join(out)


def _foot_fams() -> str:
    items = []
    for fam in _FAMILIES:
        name = template_for(fam.sector).name
        items.append(f'<li><a href="ejemplos/{fam.sector.value}/index.html">{name}</a></li>')
    return "".join(items)


def _favicon() -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
        "<rect width='32' height='32' rx='7' fill='%230d0f15'/>"
        "<circle cx='16' cy='16' r='6' fill='none' stroke='%233f63e8' stroke-width='2.5'/>"
        "<circle cx='16' cy='16' r='2' fill='%238aa9ff'/></svg>"
    )
    return "data:image/svg+xml," + svg


def _index_html() -> str:
    tpl = (_ASSETS / "index.template.html").read_text(encoding="utf-8")
    panels = "".join(_family_panel(f) for f in _FAMILIES)
    cards = "".join(_card(f) for f in _FAMILIES)
    replacements = {
        "{{FONTS}}": font_face_css(("fraunces", "archivo")),
        "{{FAVICON}}": _favicon(),
        "{{HERO_DECK}}": _hero_deck(),
        "{{HERO_LEGEND}}": _hero_legend(),
        "{{RIBBON}}": _ribbon(),
        "{{FAMILY_PANELS}}": panels,
        "{{CARDS}}": cards,
        "{{FILTERS}}": _filters(),
        "{{FOOT_FAMS}}": _foot_fams(),
    }
    for needle, value in replacements.items():
        tpl = tpl.replace(needle, value)
    return tpl


def main() -> None:
    examples = _DOCS / "ejemplos"
    if examples.exists():
        shutil.rmtree(examples)
    for fam in _FAMILIES:
        _write_example(fam.sector)
    print("capturando webs con Playwright…")
    _capture_all()
    (_DOCS / "index.html").write_text(_index_html(), encoding="utf-8")
    (_DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"escaparate generado en {_DOCS} ({len(_FAMILIES)} familias)")


if __name__ == "__main__":
    main()
