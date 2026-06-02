"""Renderizado de la landing de una página.

Toma el negocio y su copy, y produce un único HTML autocontenido (CSS y QR
incrustados) que se puede subir tal cual a cualquier hosting.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from faro.business import BusinessProfile
from faro.content import LandingCopy, generate_copy
from faro.qr import review_qr, whatsapp_qr
from faro.reviews import review_url
from faro.seo import favicon_data_uri, local_business_jsonld
from faro.whatsapp import phone_link, whatsapp_link

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_landing(business: BusinessProfile, copy: LandingCopy) -> str:
    """Renderiza la landing a un HTML autocontenido."""
    template = _env.get_template("landing.html")
    return template.render(
        business=business,
        theme=business.theme,
        copy=copy,
        brand_color=business.color,
        brand_accent=business.accent,
        whatsapp_url=whatsapp_link(business),
        phone_url=phone_link(business),
        review_url=review_url(business),
        whatsapp_qr=whatsapp_qr(business),
        review_qr=review_qr(business),
        favicon=favicon_data_uri(business),
        jsonld=local_business_jsonld(business),
    )


def build_landing(business: BusinessProfile, *, use_live: bool = True) -> str:
    """Atajo: genera el copy y renderiza la landing en un paso."""
    copy = generate_copy(business, use_live=use_live)
    return render_landing(business, copy)
