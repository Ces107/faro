"""QA de tolerancia cero: rinde los 17 sectores (datos mínimos y ricos) y verifica
que NUNCA aparece contenido genérico, placeholders sin sustituir ni vocabulario
equivocado. Es el guardia contra los fallos que un dueño detectaría en 30 segundos.
"""

from __future__ import annotations

import pytest

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.playbook import playbook_for

# Cadenas que NUNCA deben aparecer en la web generada de ningún sector.
_BLOCKLIST = [
    "Esto es lo que podemos hacer por ti",  # intro genérica vieja
    "y mucho más",  # relleno
    "Nos puedes encontrar para",  # about robótico viejo
    "Estamos en .",  # dirección colgante
    "{address}",
    "{city}",
    "{phone}",
    "{name}",
    "{offer",
    "Lo que hacemos",  # eyebrow viejo
]

_PRODUCT_SECTORS = {Sector.PANADERIA, Sector.COMERCIO, Sector.FARMACIA}


def _minimal(sector: Sector) -> BusinessProfile:
    return BusinessProfile(
        name="Negocio Demo",
        sector=sector,
        city="Sagunto",
        phone="961234567",
        services=("Una cosa", "Otra cosa", "Y una tercera"),
    )


def _rich(sector: Sector) -> BusinessProfile:
    return BusinessProfile.from_form(
        {
            "name": "Negocio Demo",
            "sector": sector.value,
            "city": "Puerto de Sagunto",
            "phone": "961234567",
            "services": "Servicio uno\nServicio dos\nServicio tres\nServicio cuatro",
            "hours": "L-V 9:00-14:00, 17:00-20:00, S 10:00-14:00",
            "address": "Calle Mayor 1",
            "email": "hola@demo.es",
            "highlights": "Atención cercana\nMás de 10 años",
            "about": "Somos un negocio de barrio con trato cercano.",
            "years": "2008",
            "differentiators": "Te atendemos sin esperas\nPrecios claros\nGarantía por escrito",
            "instagram": "@negociodemo",
            "facebook": "negociodemo",
            "payment_methods": "Efectivo, Tarjeta, Bizum",
            "parking": "Fácil aparcar en la zona",
            "languages": "Castellano, Valenciano",
            "brand_color": "#0ea5e9",
            "testimonials": "Muy contentos | Ana G. | Clienta",
            "x_Detalle": "Sí",
        }
    )


@pytest.mark.parametrize("sector", list(Sector))
def test_no_blocklisted_content_minimal(sector: Sector) -> None:
    html = build_landing(_minimal(sector), use_live=False)
    for bad in _BLOCKLIST:
        assert bad not in html, f"[{sector.value}] apareció prohibido: {bad!r}"


@pytest.mark.parametrize("sector", list(Sector))
def test_no_blocklisted_content_rich(sector: Sector) -> None:
    html = build_landing(_rich(sector), use_live=False)
    for bad in _BLOCKLIST:
        assert bad not in html, f"[{sector.value}] apareció prohibido: {bad!r}"


@pytest.mark.parametrize("sector", list(Sector))
def test_offer_heading_present_and_right(sector: Sector) -> None:
    pb = playbook_for(sector)
    html = build_landing(_minimal(sector), use_live=False)
    assert pb.offer_heading in html
    if sector in _PRODUCT_SECTORS:
        # Una tienda/panadería/farmacia NO debe titular su oferta como "servicios".
        assert pb.offer_word != "servicios"
        assert "Nuestros servicios" not in html


@pytest.mark.parametrize("sector", list(Sector))
def test_rich_data_surfaces(sector: Sector) -> None:
    html = build_landing(_rich(sector), use_live=False)
    assert "Desde 2008" in html  # año real, no inventado
    assert "Efectivo, Tarjeta, Bizum" in html  # formas de pago
    assert "Te atendemos sin esperas" in html  # diferenciador real como value-prop
    assert "Somos un negocio de barrio" in html  # about propio respetado
    assert "instagram.com/negociodemo" in html  # red social
