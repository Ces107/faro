"""Render del sitio con el motor de plantillas (chasis editorial anti-vibecoded).

Elige la plantilla que cubre el sector, carga sus ``DesignTokens`` y sus fuentes
embebidas, y compone ``site.html`` con los bloques de la familia. Reutiliza los
mismos builders honestos de contenido (servicios, FAQ, cifras) que el render
clásico: solo cambia la piel, nunca se inventan datos.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from faro.business import BusinessProfile
from faro.content import LandingCopy
from faro.engine.design import tokens_for
from faro.engine.fonts import font_face_css
from faro.engine.registry import template_for
from faro.hours import parse_opening_hours
from faro.maps import maps_embed_url, maps_link
from faro.playbook import playbook_for
from faro.qr import review_qr
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
    return "".join(f"&#{ord(c)};" for c in email)


def _social_url(value: str, base: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("http"):
        return value
    return f"https://{base}/{value.lstrip('@')}"


def _anchors(business: BusinessProfile, offer_label: str) -> list[dict[str, str]]:
    items = [{"id": "servicios", "label": offer_label}, {"id": "proceso", "label": "Proceso"}]
    if business.photos:
        items.append({"id": "galeria", "label": "Galería"})
    if business.testimonials:
        items.append({"id": "opiniones", "label": "Opiniones"})
    items.append({"id": "sobre", "label": "Nosotros"})
    items.append({"id": "faq", "label": "Preguntas"})
    if business.address:
        items.append({"id": "como-llegar", "label": "Cómo llegar"})
    return items


def render_site(business: BusinessProfile, copy: LandingCopy) -> str:
    """Renderiza la web con la familia que corresponde al sector."""
    spec = template_for(business.sector)
    tokens = tokens_for(spec.family)
    playbook = playbook_for(business.sector)

    is_carta = tokens.service_style == "carta"
    offer_label = "Carta" if is_carta else playbook.offer_word.split()[0].capitalize()
    offer_eyebrow = "La carta" if is_carta else "Lo que ofrecemos"

    # La familia fija la dirección de arte (tipografía, layout, neutros); si el
    # negocio aporta su color de marca, personaliza el acento sin romperla.
    css_vars = tokens.to_css_vars()
    if business.brand_color:
        css_vars += f":root{{--brand:{business.color};--accent:{business.accent};}}"

    context = {
        "business": business,
        "copy": copy,
        "playbook": playbook,
        "tokens": tokens,
        "font_css": font_face_css(tokens.fonts()),
        "css_vars": css_vars,
        "offer_eyebrow": offer_eyebrow,
        "proceso_title": "Cómo trabajamos",
        "service_cards": build_service_cards(business, playbook),
        "process": playbook.process,
        "faq": build_faq(business, playbook),
        "stats": build_stats(business, playbook),
        "whatsapp_url": whatsapp_link(business),
        "phone_url": phone_link(business),
        "review_url": review_url(business),
        "review_qr": review_qr(business),
        "favicon": favicon_data_uri(business),
        "jsonld": local_business_jsonld(business),
        "maps_embed_url": maps_embed_url(business) if business.address else "",
        "maps_link": maps_link(business),
        "email_html": _obfuscate_email(business.email) if business.email else "",
        "instagram_url": _social_url(business.instagram, "instagram.com"),
        "facebook_url": _social_url(business.facebook, "facebook.com"),
        "anchors": _anchors(business, offer_label),
        "opening_hours_json": json.dumps(parse_opening_hours(business.hours)),
        "current_year": datetime.datetime.now().year,
    }
    return _env.get_template("site.html").render(**context)
