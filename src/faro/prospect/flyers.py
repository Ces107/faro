"""Folletos por sector. Eje de cambio: presentación imprimible de los folletos.

Un folleto A6 por familia visual presente en el censo (4 por hoja A4, con guías
de corte). El QR apunta a la demo de SECTOR del showcase público — marca
ficticia, nunca la marca de un negocio real (línea legal del red-team
2026-06-10: una "demo" pública con la marca de un negocio ajeno es RGPD + actos
de confusión; una demo de sector con marca inventada es solo un ejemplo).

Uso: buzonear en negocios cerrados o dejar en mano tras un no. La carta física
y el buzoneo quedan fuera de la LSSI (que solo regula comunicaciones
electrónicas); el contacto del operador se inyecta vía FARO_OPERATOR_*.
"""

from __future__ import annotations

import html

from faro.prospect.census import CensusResult
from faro.qr import qr_data_uri

__all__ = ["flyers_html"]

_SHOWCASE_BASE = "https://ces107.github.io/faro/ejemplos/"

# Familia visual → (demo de sector del showcase, nombre típico para el claim).
_FAMILY_EXAMPLE: dict[str, tuple[str, str]] = {
    "carta": ("bar", "un bar o restaurante"),
    "clinica": ("dental", "una clínica"),
    "industrial": ("taller", "un taller"),
    "estudio": ("peluqueria", "una peluquería o centro de estética"),
    "autoridad": ("asesoria", "una asesoría o despacho"),
    "gimnasio": ("gimnasio", "un gimnasio"),
    "aurora": ("comercio", "un comercio"),
}

_CSS = """
:root { font-family: Georgia, 'Times New Roman', serif; color: #1a1a1a; }
body { margin: 0; padding: 1rem; }
.sheet { display: grid; grid-template-columns: 1fr 1fr; gap: 0; max-width: 50rem; margin: 0 auto; }
.flyer { border: 1px dashed #999; padding: 1.1rem 1.2rem; min-height: 17rem;
         display: flex; flex-direction: column; page-break-inside: avoid; }
.flyer h2 { font-size: 1.15rem; margin: 0 0 .4rem; line-height: 1.25; }
.flyer p { font-size: .85rem; margin: .2rem 0; }
.flyer .qr { display: flex; align-items: center; gap: .8rem; margin: .6rem 0; }
.flyer .qr img { width: 7.2rem; height: 7.2rem; }
.flyer .qr .hint { font-size: .78rem; color: #444; }
.flyer .url { font-size: .72rem; color: #555; word-break: break-all; }
.flyer .contact { margin-top: auto; border-top: 1px solid #1a1a1a; padding-top: .4rem;
                  font-size: .88rem; font-weight: bold; }
.flyer .price { font-size: .8rem; color: #444; }
footer { max-width: 50rem; margin: .8rem auto 0; font-size: .72rem; color: #666; }
@media print { body { padding: 0; } footer { display: none; } }
"""


def _flyer(family: str, count: int, operator_name: str, operator_contact: str) -> str:
    example, noun = _FAMILY_EXAMPLE.get(family, _FAMILY_EXAMPLE["aurora"])
    url = f"{_SHOWCASE_BASE}{example}/"
    qr = qr_data_uri(url, scale=5)
    contact = " · ".join(filter(None, (operator_name, operator_contact))) or "[tu nombre y teléfono]"
    plural = "s" if count != 1 else ""
    return f"""<article class="flyer">
<h2>¿Tu negocio aún no sale bien en Google?</h2>
<p>Así se vería la web de {html.escape(noun)} como el tuyo. Es un ejemplo real
hecho con la misma herramienta: web propia, ficha de Google y WhatsApp, montado en el día.</p>
<div class="qr"><img src="{qr}" alt="QR a la web de ejemplo">
<span class="hint">Escanea y mírala en tu móvil ({count} negocio{plural} de tu sector
en tu zona aún no tienen web).</span></div>
<p class="url">{html.escape(url)}</p>
<p class="price">Pago único desde 290 €. La web es tuya: sin cuotas obligatorias.</p>
<p class="price">La ficha de Google es gratis y queda en tu cuenta: Google no llama
para cobrar. Esto es un trabajo de montaje, una vez.</p>
<p class="contact">{html.escape(contact)}</p>
</article>"""


def flyers_html(
    census: CensusResult, *, operator_name: str = "", operator_contact: str = ""
) -> str:
    """Folletos imprimibles para las familias con candidatos en el censo."""
    counts: dict[str, int] = {}
    for prospect in census.prospects:
        counts[prospect.family] = counts.get(prospect.family, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: -kv[1])
    flyers = "".join(
        _flyer(family, count, operator_name, operator_contact) for family, count in ordered
    )
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<title>Folletos por sector — {html.escape(census.municipality)}</title>
<style>{_CSS}</style></head><body>
<div class="sheet">{flyers}</div>
<footer>Imprime en A4 y recorta por la línea. Los QR llevan a demos de ejemplo con marca
ficticia del escaparate público de Faro. Edita FARO_OPERATOR_NAME / FARO_OPERATOR_CONTACT
antes de generar para que salga tu contacto.</footer>
</body></html>"""
