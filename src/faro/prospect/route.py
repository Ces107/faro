"""Hoja de ruta de venta. Eje de cambio: presentación imprimible de la ruta.

HTML autocontenido (sin CDN, sin JS) pensado para imprimirse en A4 y usarse en
el portátil durante la salida: cada negocio enlaza con su formulario precargado.

Reglas no negociables (red-team legal 2026-06-10):
- SIN teléfonos: la hoja lleva solo nombre comercial, categoría y calle
  (minimización RGPD; los teléfonos se quedan en el censo local).
- Atribución ODbL visible: los datos vienen de OpenStreetMap.
- Documento interno y efímero: se imprime, se anota y no se publica.
"""

from __future__ import annotations

import html
import urllib.parse
from collections import defaultdict

from faro.prospect.census import CensusResult, Prospect

__all__ = ["route_sheet_html"]

_NO_STREET = "Sin calle mapeada (abrir el mapa)"

_CSS = """
:root { font-family: Georgia, 'Times New Roman', serif; color: #1a1a1a; }
body { max-width: 52rem; margin: 1.5rem auto; padding: 0 1rem; }
h1 { font-size: 1.6rem; margin: 0 0 .25rem; }
.meta { color: #555; font-size: .9rem; margin-bottom: 1rem; }
.howto { border: 1px solid #1a1a1a; padding: .6rem .8rem; font-size: .92rem; margin-bottom: 1.2rem; }
h2 { font-size: 1.05rem; border-bottom: 2px solid #1a1a1a; padding-bottom: .2rem; margin: 1.4rem 0 .4rem; }
table { width: 100%; border-collapse: collapse; }
td { padding: .35rem .4rem; border-bottom: 1px solid #ddd; vertical-align: top; font-size: .95rem; }
.box { font-size: 1.05rem; width: 1.4rem; }
.cat { color: #555; font-size: .85rem; }
.badge { display: inline-block; border: 1px solid #888; border-radius: 2px; padding: 0 .3rem; font-size: .72rem; margin-left: .35rem; color: #444; }
.badge.warn { border-color: #b45309; color: #b45309; }
.badge.fresh { border-color: #166534; color: #166534; }
.links a { font-size: .8rem; margin-right: .6rem; }
.notes { width: 9rem; border-bottom: 1px dotted #999; }
footer { margin-top: 2rem; font-size: .78rem; color: #555; border-top: 1px solid #ccc; padding-top: .6rem; }
@media print {
  .links { display: none; }
  body { margin: 0; max-width: none; }
  .howto { page-break-inside: avoid; }
  h2 { page-break-after: avoid; }
}
"""


def _badges(prospect: Prospect) -> str:
    badges = [f'<span class="badge">{html.escape(prospect.category)}</span>']
    if prospect.checked_recently:
        badges.append('<span class="badge fresh">verificado 2024+</span>')
    elif prospect.stale:
        badges.append('<span class="badge warn">dato antiguo: confirmar abierto</span>')
    return "".join(badges)


def _links(prospect: Prospect, prefill_base: str, municipality: str) -> str:
    prefill = f"{prefill_base}?prefill={urllib.parse.quote(prospect.slug)}"
    osm = f"https://www.openstreetmap.org/{prospect.osm_ref}"
    google = "https://www.google.com/search?q=" + urllib.parse.quote(
        f"{prospect.name} {municipality}"
    )
    return (
        f'<span class="links"><a href="{html.escape(prefill)}">formulario precargado</a>'
        f'<a href="{html.escape(google)}">buscar en Google</a>'
        f'<a href="{html.escape(osm)}">mapa</a></span>'
    )


def _row(prospect: Prospect, prefill_base: str, municipality: str) -> str:
    number = f" {html.escape(prospect.housenumber)}" if prospect.housenumber else ""
    return (
        '<tr><td class="box">&#9744;</td>'
        f"<td><strong>{html.escape(prospect.name)}</strong>{number} "
        f"{_badges(prospect)}<br>{_links(prospect, prefill_base, municipality)}</td>"
        f'<td class="notes"></td></tr>'
    )


def _grouped(census: CensusResult) -> list[tuple[str, list[Prospect]]]:
    groups: dict[str, list[Prospect]] = defaultdict(list)
    for prospect in census.prospects:
        groups[prospect.street or _NO_STREET].append(prospect)
    ordered = sorted(
        groups.items(),
        key=lambda kv: (kv[0] == _NO_STREET, -max(p.score for p in kv[1])),
    )
    return [(street, sorted(ps, key=lambda p: (p.housenumber or "~", p.name))) for street, ps in ordered]


def route_sheet_html(
    census: CensusResult, *, generated_on: str, prefill_base: str = "http://127.0.0.1:8000/"
) -> str:
    """Hoja de ruta imprimible: candidatos agrupados por calle, priorizados."""
    sections: list[str] = []
    for street, prospects in _grouped(census):
        rows = "".join(_row(p, prefill_base, census.municipality) for p in prospects)
        sections.append(
            f"<h2>{html.escape(street)} <small>({len(prospects)})</small></h2>"
            f"<table>{rows}</table>"
        )
    excluded = ", ".join(f"{reason.value}: {count}" for reason, count in census.excluded)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<title>Ruta de venta — {html.escape(census.municipality)}</title>
<style>{_CSS}</style></head><body>
<h1>Ruta de venta — {html.escape(census.municipality)}</h1>
<p class="meta">Generada el {html.escape(generated_on)} · {len(census.prospects)} candidatos
de {census.total_raw} POIs ({html.escape(excluded)})</p>
<div class="howto"><strong>Antes de entrar:</strong> busca el negocio en Google delante de la
puerta (enlace en cada fila). Si ya tiene web decente, pasa al siguiente: esta lista son
candidatos, no clientes seguros. El enlace «formulario precargado» abre Faro con los datos
públicos ya puestos: confírmalos con el dueño, completa servicios y horario, y genera delante.
Marca cada visita y pasa el resultado a ventas/registro-puertas.md al volver.</div>
{"".join(sections)}
<footer>Datos: © OpenStreetMap contributors (ODbL) — openstreetmap.org/copyright.
Documento interno de trabajo, uso efímero. No contiene teléfonos. No publicar ni difundir.</footer>
</body></html>"""
