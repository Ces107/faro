"""Aviso de WhatsApp-sobre-fijo: property, API y LEEME del pack.

Gap cazado por la simulación de compra 2026-06-10 (bar con teléfono fijo): el
botón wa.me apuntando a un fijo sin WhatsApp moría EN SILENCIO. El producto no
bloquea (hay fijos con WhatsApp Business): avisa al operador donde puede
corregirlo, con el dueño delante.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from faro.business import BusinessProfile
from faro.pack import build_pack, to_zip
from faro.prospect.census import build_census
from faro.prospect.flyers import flyers_html
from faro.server import create_app

_BASE = {
    "name": "Casa Paco",
    "sector": "bar",
    "city": "Puerto de Sagunto",
    "services": "Almuerzos\nPaella por encargo",
}


def _profile(phone: str, whatsapp: str = "") -> BusinessProfile:
    return BusinessProfile.from_form(_BASE | {"phone": phone, "whatsapp": whatsapp})


def test_whatsapp_looks_mobile_property() -> None:
    assert _profile("612 345 678").whatsapp_looks_mobile is True
    assert _profile("962 681 176").whatsapp_looks_mobile is False
    # Fijo de llamada + móvil explícito para WhatsApp: correcto.
    assert _profile("962 681 176", whatsapp="612 345 678").whatsapp_looks_mobile is True


def test_generate_warns_on_landline_whatsapp() -> None:
    client = TestClient(create_app(use_live=False))
    res = client.post("/api/generate", json=_BASE | {"phone": "962 681 176"})
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert len(warnings) == 1
    assert "fijo" in warnings[0]
    res_mobile = client.post("/api/generate", json=_BASE | {"phone": "612 345 678"})
    assert res_mobile.json()["warnings"] == []


def test_pack_readme_carries_landline_warning() -> None:
    business = _profile("962 681 176")
    pack = build_pack(business, use_live=False)
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(to_zip(pack, business))) as zf:
        readme = zf.read("LEEME.txt").decode("utf-8")
    assert "AVISO" in readme
    assert "fijo" in readme
    business_mobile = _profile("612 345 678")
    pack_mobile = build_pack(business_mobile, use_live=False)
    with zipfile.ZipFile(io.BytesIO(to_zip(pack_mobile, business_mobile))) as zf:
        readme_mobile = zf.read("LEEME.txt").decode("utf-8")
    assert "AVISO" not in readme_mobile


def test_flyer_carries_anti_scam_line() -> None:
    census = build_census(
        [
            {
                "type": "node",
                "id": 1,
                "lat": 39.68,
                "lon": -0.24,
                "tags": {"amenity": "bar", "name": "Bar Murillo"},
            }
        ],
        municipality="Sagunt",
    )
    html = flyers_html(census)
    assert "Google no llama" in html
