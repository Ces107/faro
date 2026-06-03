"""Los datos de ejemplo por sector deben construir un perfil válido y completo.

Así, al elegir un tipo en la consola, los campos vienen pre-rellenados y «Generar
pack» produce una web entera sin que el operador tenga que escribir nada (luego
edita los datos reales del negocio).
"""

from __future__ import annotations

import pytest

from faro.business import BusinessProfile, Sector
from faro.engine.demo import demo_data
from faro.landing import build_landing


@pytest.mark.parametrize("sector", list(Sector))
def test_demo_builds_complete_site(sector: Sector) -> None:
    data = demo_data(sector)
    biz = BusinessProfile.from_form(data)
    assert biz.name and biz.city and biz.services
    # El ejemplo trae datos ricos (al menos servicios y una descripción o lema).
    assert len(biz.services) >= 2
    html = build_landing(biz, use_live=False)
    assert biz.name in html
    assert len(html) > 50_000  # web completa con fuentes embebidas


def test_demo_rating_is_decimal_safe() -> None:
    """La valoración de ejemplo es un decimal válido (no rompe el input number)."""
    for sector in Sector:
        rating = demo_data(sector).get("google_rating", "")
        if rating:
            value = float(rating)
            assert 0 < value <= 5


def test_demo_sector_key_matches() -> None:
    assert demo_data(Sector.BAR)["sector"] == "bar"
    assert demo_data(Sector.TALLER)["name"] == "Talleres Morvedre"
