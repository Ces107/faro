"""Renderizado de la landing de una página.

Toma el negocio y su copy, reúne el contenido de cada sección (servicios, proceso,
FAQ, estadísticas) y produce un único HTML autocontenido (CSS, JS, iconos y QR
incrustados) que se sube tal cual a cualquier hosting estático.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from faro.business import BusinessProfile, mix_hex
from faro.content import LandingCopy, generate_copy
from faro.hours import parse_opening_hours
from faro.icons import get_icon
from faro.maps import maps_embed_url, maps_link
from faro.playbook import playbook_for
from faro.qr import review_qr, whatsapp_qr
from faro.reviews import review_url
from faro.sections import build_faq, build_service_cards, build_stats
from faro.seo import favicon_data_uri, local_business_jsonld
from faro.whatsapp import phone_link, whatsapp_link

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def _obfuscate_email(email: str) -> str:
    """Codifica el email como entidades HTML para que los rastreadores de spam no
    lo lean en texto plano. El navegador lo muestra con normalidad."""
    return "".join(f"&#{ord(c)};" for c in email)


def _anchors(
    business: BusinessProfile, has_photos: bool, has_testimonials: bool
) -> list[dict[str, str]]:
    """Enlaces de navegación, solo para las secciones que de verdad se renderizan."""
    items = [
        {"id": "servicios", "label": "Servicios"},
        {"id": "proceso", "label": "Cómo trabajamos"},
    ]
    if has_photos:
        items.append({"id": "galeria", "label": "Galería"})
    if has_testimonials:
        items.append({"id": "opiniones", "label": "Opiniones"})
    items.append({"id": "sobre", "label": "Sobre nosotros"})
    items.append({"id": "faq", "label": "Preguntas"})
    if business.address:
        items.append({"id": "como-llegar", "label": "Cómo llegar"})
    return items


def _fallback_hexes(color: str) -> dict[str, str]:
    """Hexes pre-calculados para navegadores sin color-mix (se inyectan en @supports)."""
    return {
        "brand_050_hex": mix_hex(color, "#ffffff", 0.08),
        "brand_100_hex": mix_hex(color, "#ffffff", 0.14),
        "line_hex": mix_hex(color, "#ffffff", 0.14),
        "ink_hex": mix_hex(color, "#0b1220", 0.20),
        "surf1_hex": mix_hex(color, "#ffffff", 0.03),
        "surf2_hex": mix_hex(color, "#ffffff", 0.06),
    }


def render_landing(business: BusinessProfile, copy: LandingCopy) -> str:
    """Renderiza la landing a un HTML autocontenido."""
    template = _env.get_template("landing.html")
    playbook = playbook_for(business.sector)
    context = {
        "business": business,
        "theme": business.theme,
        "copy": copy,
        "playbook": playbook,
        "brand_color": business.color,
        "brand_accent": business.accent,
        "on_brand": business.on_brand,
        "hero_start": business.hero_start,
        "hero_end": business.hero_end,
        "sector_icon": get_icon(playbook.icon),
        "trust_chip": playbook.trust_chip.replace("{city}", business.city).replace(
            "{phone}", business.phone
        ),
        "service_cards": build_service_cards(business, playbook),
        "process": playbook.process,
        "faq": build_faq(business, playbook),
        "stats": build_stats(business, playbook),
        "whatsapp_url": whatsapp_link(business),
        "phone_url": phone_link(business),
        "review_url": review_url(business),
        "whatsapp_qr": whatsapp_qr(business),
        "review_qr": review_qr(business),
        "favicon": favicon_data_uri(business),
        "jsonld": local_business_jsonld(business),
        "maps_embed_url": maps_embed_url(business) if business.address else "",
        "maps_link": maps_link(business),
        "email_html": _obfuscate_email(business.email) if business.email else "",
        "anchors": _anchors(business, bool(business.photos), bool(business.testimonials)),
        "opening_hours_json": json.dumps(parse_opening_hours(business.hours)),
        "current_year": datetime.datetime.now().year,
        "icon": get_icon,
        **_fallback_hexes(business.color),
    }
    return template.render(**context)


def build_landing(business: BusinessProfile, *, use_live: bool = True) -> str:
    """Atajo: genera el copy y renderiza la landing en un paso."""
    copy = generate_copy(business, use_live=use_live)
    return render_landing(business, copy)
