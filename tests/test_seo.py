"""Tests del SEO de la landing: datos estructurados, favicon, branding."""

from __future__ import annotations

import json

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.seo import favicon_data_uri, local_business_jsonld, schema_type


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


def test_schema_type_per_sector() -> None:
    assert schema_type(Sector.DENTAL) == "Dentist"
    assert schema_type(Sector.RESTAURANTE) == "Restaurant"
    assert schema_type(Sector.OTRO) == "LocalBusiness"


def test_schema_type_all_sectors_mapped() -> None:
    for s in Sector:
        assert schema_type(s)  # no KeyError for any sector
    assert schema_type(Sector.FARMACIA) == "Pharmacy"
    assert schema_type(Sector.BAR) == "BarOrPub"


def test_landing_obfuscates_email() -> None:
    html = build_landing(_biz(email="hola@bar.com"), use_live=False)
    assert "hola@bar.com" not in html
    assert "&#" in html


def test_jsonld_is_valid_and_complete() -> None:
    raw = local_business_jsonld(_biz()).replace("<\\/", "</")
    data = json.loads(raw)
    assert data["@type"] == "Dentist"
    assert data["@context"] == "https://schema.org"
    assert data["name"] == "Clínica Dental Sonríe"
    assert data["telephone"] == "+34961234567"
    assert data["address"]["addressLocality"] == "Puerto de Sagunto"
    assert data["address"]["streetAddress"] == "Av. del Mediterráneo 12"
    assert data["address"]["addressCountry"] == "ES"


def test_jsonld_escapes_script_close() -> None:
    # Un "</script>" en el nombre no debe poder cerrar el bloque <script> inline.
    biz = _biz(name="Bar </script> Pepe")
    raw = local_business_jsonld(biz)
    assert "</script>" not in raw
    assert "<\\/script>" in raw


def test_favicon_is_svg_data_uri_with_initials() -> None:
    uri = favicon_data_uri(_biz())
    assert uri.startswith("data:image/svg+xml,")
    assert "CD" in uri or "CDS" in uri  # iniciales codificadas


def test_landing_includes_seo_and_branding() -> None:
    html = build_landing(_biz(brand_color="#ff0000"), use_live=False)
    assert 'application/ld+json' in html
    assert '"Dentist"' in html
    assert 'property="og:title"' in html
    assert 'rel="icon"' in html
    assert "#ff0000" in html  # color de marca aplicado
    assert "CD" in html  # iniciales en el hero
