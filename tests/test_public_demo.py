"""La ruta pública ``/d/{slug}`` sirve la web del cliente a pantalla completa."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from faro.server import _demo_form_for, create_app


def test_demo_by_sector_returns_full_page() -> None:
    client = TestClient(create_app())
    response = client.get("/d/bar")
    assert response.status_code == 200
    body = response.text.lower()
    assert "<html" in body and "</html>" in body
    # Es la web completa, no el panel del operador (sin el formulario de Faro).
    assert "api/generate" not in body


def test_demo_unknown_slug_is_404() -> None:
    client = TestClient(create_app())
    assert client.get("/d/no-existe-este-sector").status_code == 404


def test_demo_prefers_census_over_sector(tmp_path: Path, monkeypatch) -> None:
    census = tmp_path / "saguntoxx" / "prospects.json"
    census.parent.mkdir(parents=True)
    census.write_text(
        json.dumps(
            {
                "casa-paco": {
                    "sector": "bar",
                    "values": {"name": "Casa Paco", "city": "Puerto de Sagunto"},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("faro.server._PROSPECT_DIR", tmp_path)
    form = _demo_form_for("casa-paco")
    assert form is not None
    assert form["name"] == "Casa Paco"
    assert form["sector"] == "bar"

    client = TestClient(create_app())
    response = client.get("/d/casa-paco")
    assert response.status_code == 200
    assert "Casa Paco" in response.text


def test_demo_form_for_unknown_returns_none() -> None:
    assert _demo_form_for("ni-censo-ni-sector") is None
