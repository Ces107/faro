"""Tests del mapa de Google Maps embebido."""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.maps import maps_embed_url, maps_link, maps_query


def _biz(**ov: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica Dental Sonríe",
        "sector": Sector.DENTAL,
        "city": "Puerto de Sagunto",
        "phone": "961234567",
        "services": ("Limpiezas",),
        "address": "Av. del Mediterráneo 12",
    }
    data.update(ov)
    return BusinessProfile(**data)  # type: ignore[arg-type]


def test_maps_query_with_and_without_address() -> None:
    assert maps_query(_biz()) == "Av. del Mediterráneo 12, Puerto de Sagunto"
    assert maps_query(_biz(address="")) == "Puerto de Sagunto"


def test_maps_embed_url_is_embeddable() -> None:
    url = maps_embed_url(_biz())
    assert url.startswith("https://www.google.com/maps?q=")
    assert "output=embed" in url


def test_maps_link_opens_search() -> None:
    assert "maps/search" in maps_link(_biz())


def test_landing_shows_map_only_with_address() -> None:
    with_addr = build_landing(_biz(), use_live=False)
    assert "Cómo llegar" in with_addr
    assert "output=embed" in with_addr

    without_addr = build_landing(_biz(address=""), use_live=False)
    assert "Cómo llegar" not in without_addr


def test_map_is_consent_gated() -> None:
    # El mapa NO debe cargar el iframe de Google directamente (cookies AEPD):
    # se ofrece un botón de consentimiento que lo carga al pulsar.
    html = build_landing(_biz(), use_live=False)
    assert "Ver el mapa" in html
    assert "faroLoadMap" in html
    assert "<iframe" not in html  # el iframe se crea por JS solo al consentir
