"""Folletos por sector: QR al showcase, contrato de familias y contacto."""

from __future__ import annotations

from faro.business import Sector
from faro.engine.registry import template_for
from faro.prospect.census import build_census
from faro.prospect.flyers import _FAMILY_EXAMPLE, flyers_html

_ELEMENTS = [
    {
        "type": "node",
        "id": 1,
        "lat": 39.68,
        "lon": -0.28,
        "tags": {"amenity": "bar", "name": "Bar Murillo"},
    },
    {
        "type": "node",
        "id": 2,
        "lat": 39.66,
        "lon": -0.23,
        "tags": {"amenity": "dentist", "name": "Clínica Dental Norte"},
    },
]


def _census() -> object:
    return build_census(list(_ELEMENTS), municipality="Sagunt / Sagunto")


def test_every_registered_family_has_showcase_example() -> None:
    # Contrato: si se añade una familia al registro, el folleto debe saber a qué
    # demo del showcase apuntar (o caer en aurora a propósito, no por accidente).
    families = {template_for(sector).family for sector in Sector}
    assert families <= set(_FAMILY_EXAMPLE)


def test_only_present_families_get_flyer() -> None:
    html = flyers_html(_census())
    assert "un bar o restaurante" in html  # carta presente
    assert "una clínica" in html  # clinica presente
    assert "un taller" not in html  # industrial ausente del censo


def test_qr_data_uri_and_showcase_url() -> None:
    html = flyers_html(_census())
    assert 'src="data:image/svg+xml' in html
    assert "https://ces107.github.io/faro/ejemplos/bar/" in html


def test_operator_contact_placeholder_and_injection() -> None:
    assert "[tu nombre y teléfono]" in flyers_html(_census())
    html = flyers_html(_census(), operator_name="César", operator_contact="600 000 000")
    assert "César · 600 000 000" in html


def test_no_index_meta() -> None:
    assert 'name="robots" content="noindex,nofollow"' in flyers_html(_census())
