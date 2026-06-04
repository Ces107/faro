"""Genera el escaparate estático de Faro para GitHub Pages.

Produce, en ``docs/``:
- ``ejemplos/<sector>/index.html`` + ``aviso-legal.html``: la web de ejemplo
  COMPLETA de cada familia (lo que Faro genera, autocontenido).
- ``index.html``: una portada editorial que presenta Faro y enlaza a cada ejemplo.
- ``.nojekyll``: para que GitHub Pages sirva los ficheros tal cual.

Es un escaparate público: cualquiera puede ver lo que Faro produce, cuando sea.
Las fotos y reseñas son de muestra (en un encargo real las pone el negocio).

Uso: ``python tools/build_showcase.py``
"""

from __future__ import annotations

import shutil
from pathlib import Path

from faro.business import BusinessProfile, Sector
from faro.engine.demo import demo_data
from faro.engine.design import tokens_for
from faro.engine.fonts import font_face_css
from faro.engine.registry import template_for
from faro.pack import build_pack

_ROOT = Path(__file__).resolve().parents[1]
_DOCS = _ROOT / "docs"

# Una familia, su sector representativo y una frase de venta.
_FAMILIES: list[tuple[str, Sector, str]] = [
    ("carta", Sector.BAR, "Hostelería: foto a sangre, carta tipográfica con precios, serif cálida."),
    ("clinica", Sector.DENTAL, "Salud: sereno y de confianza, con cita y valoración real. Sin pastel."),
    ("autoridad", Sector.ASESORIA, "Profesional: serif de autoridad, sobrio, institucional."),
    ("industrial", Sector.TALLER, "Oficios: tipografía potente, alto contraste, presupuesto claro."),
    ("estudio", Sector.PELUQUERIA, "Belleza: la galería manda, editorial elegante."),
    ("gimnasio", Sector.GIMNASIO, "Gimnasio: modo oscuro, acento vivo, energía."),
    ("aurora", Sector.COMERCIO, "Universal: editorial limpio para cualquier negocio."),
]


def _write_example(sector: Sector) -> None:
    business = BusinessProfile.from_form(demo_data(sector))
    pack = build_pack(business, use_live=False)
    folder = _DOCS / "ejemplos" / sector.value
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(pack.landing_html, encoding="utf-8")
    (folder / "aviso-legal.html").write_text(pack.legal_html, encoding="utf-8")


def _card(family: str, sector: Sector, desc: str) -> str:
    tokens = tokens_for(family)
    spec = template_for(sector)
    business = BusinessProfile.from_form(demo_data(sector))
    return f"""
      <a class="card" href="ejemplos/{sector.value}/index.html">
        <span class="swatch" style="background:{tokens.brand}"></span>
        <span class="fam">{spec.name}</span>
        <span class="ex">{business.name}</span>
        <span class="desc">{desc}</span>
        <span class="go">Ver web de ejemplo &rarr;</span>
      </a>"""


def _index_html() -> str:
    cards = "".join(_card(f, s, d) for f, s, d in _FAMILIES)
    fonts = font_face_css(("fraunces", "archivo"))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Faro — webs para negocios locales que no parecen hechas por IA</title>
<meta name="description" content="Faro genera la web, la ficha de Google y el WhatsApp de un negocio local en minutos. Cada tipo de negocio, con su propio estilo." />
<meta property="og:title" content="Faro — webs para negocios locales" />
<meta property="og:description" content="Cada tipo de negocio, con su propio estilo. Mira los ejemplos." />
<style>
{fonts}
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--ink:#f4ece0;--bg:#161310;--brand:#d6754a;--soft:#a99e8e;--line:rgba(255,255,255,.12)}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--ink);font-family:'Archivo','Helvetica Neue',Arial,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}}
.wrap{{width:min(1140px,92vw);margin-inline:auto}}
a{{color:inherit;text-decoration:none}}
header{{padding:clamp(56px,9vw,120px) 0 clamp(30px,5vw,60px)}}
.kicker{{font-size:.8rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--brand)}}
h1{{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:clamp(2.6rem,1.4rem+6vw,6rem);line-height:.98;letter-spacing:-.03em;margin:.2em 0 .25em;max-width:16ch}}
.lead{{font-size:clamp(1.1rem,1rem+.5vw,1.4rem);color:var(--soft);max-width:54ch}}
.meta{{margin-top:30px;display:flex;flex-wrap:wrap;gap:10px 26px;font-size:.92rem;font-weight:600;color:var(--soft)}}
.meta b{{color:var(--ink);font-weight:700}}
.sec-h{{border-top:1px solid var(--line);padding-top:22px;margin-top:30px;display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}}
.sec-h h2{{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:clamp(1.5rem,1.2rem+1.4vw,2.2rem)}}
.sec-h span{{color:var(--soft);font-size:.92rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;padding:30px 0 80px}}
.card{{display:flex;flex-direction:column;gap:6px;padding:24px;border:1px solid var(--line);border-radius:4px;background:rgba(255,255,255,.02);transition:transform .15s ease,border-color .2s,background .2s}}
.card:hover{{transform:translateY(-4px);border-color:var(--brand);background:rgba(255,255,255,.04)}}
.swatch{{width:46px;height:8px;border-radius:2px;margin-bottom:8px}}
.fam{{font-family:'Fraunces',Georgia,serif;font-size:1.5rem;font-weight:600}}
.ex{{font-size:.82rem;color:var(--brand);font-weight:700;letter-spacing:.04em;text-transform:uppercase}}
.desc{{color:var(--soft);font-size:.95rem;margin:6px 0 4px}}
.go{{margin-top:auto;font-weight:700;font-size:.92rem;color:var(--ink)}}
footer{{border-top:1px solid var(--line);padding:34px 0;color:var(--soft);font-size:.9rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}}
footer a{{text-decoration:underline}}
.note{{background:rgba(214,117,74,.1);border:1px solid rgba(214,117,74,.3);border-radius:4px;padding:14px 18px;margin:8px 0 0;font-size:.88rem;color:var(--soft)}}
</style>
</head>
<body>
<header><div class="wrap">
  <p class="kicker">Faro · presencia digital para negocios locales</p>
  <h1>Webs que no parecen hechas por una IA.</h1>
  <p class="lead">Faro genera la web de una página, el contenido de Google Business y el WhatsApp de un negocio local en minutos. Cada tipo de negocio entra en su propia familia de diseño: una panadería no se parece a un bufete.</p>
  <div class="meta"><span><b>7</b> familias con estilo propio</span><span>Tipografía real embebida</span><span>Sin cookies de seguimiento</span><span>Lista para subir a cualquier hosting</span></div>
</div></header>
<main class="wrap">
  <div class="sec-h"><h2>Ejemplos en vivo</h2><span>Datos, fotos y reseñas de muestra · en un encargo real los pone el negocio</span></div>
  <div class="grid">{cards}</div>
  <p class="note">Esto es un escaparate de lo que Faro produce. La web de cada ejemplo es autocontenida (un solo HTML con las fuentes dentro) y se sube tal cual a cualquier sitio.</p>
</main>
<footer><div class="wrap" style="display:flex;justify-content:space-between;width:100%;flex-wrap:wrap;gap:12px">
  <span>Hecho con Faro</span>
  <span><a href="https://github.com/Ces107/faro">Código en GitHub</a></span>
</div></footer>
</body>
</html>
"""


def main() -> None:
    examples = _DOCS / "ejemplos"
    if examples.exists():
        shutil.rmtree(examples)
    for _, sector, _desc in _FAMILIES:
        _write_example(sector)
    (_DOCS / "index.html").write_text(_index_html(), encoding="utf-8")
    (_DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"escaparate generado en {_DOCS} ({len(_FAMILIES)} ejemplos)")


if __name__ == "__main__":
    main()
