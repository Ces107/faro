"""Tests del servidor con TestClient (sin red, sin LLM)."""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from faro import server as server_mod
from faro.server import create_app

client = TestClient(create_app(use_live=False))

_FORM = {
    "name": "Clínica Dental Sonríe",
    "sector": "dental",
    "city": "Puerto de Sagunto",
    "phone": "961234567",
    "services": "Limpiezas\nImplantes\nOrtodoncia",
    "hours": "L-V 9:00-20:00",
    "address": "Av. del Mediterráneo 12",
    "highlights": "20 años de experiencia",
}


def test_sectors_endpoint() -> None:
    res = client.get("/api/sectors")
    assert res.status_code == 200
    values = [s["value"] for s in res.json()["sectors"]]
    assert "dental" in values


def test_generate_preview_download_flow() -> None:
    res = client.post("/api/generate", json=_FORM)
    assert res.status_code == 200
    body = res.json()
    assert body["pack_id"]
    assert len(body["gmb"]["posts"]) == 5
    assert body["whatsapp_url"].startswith("https://wa.me/")

    preview = client.get(body["preview_url"])
    assert preview.status_code == 200
    assert "Clínica Dental Sonríe" in preview.text

    dl = client.get(body["download_url"])
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(dl.content)) as zf:
        assert "index.html" in zf.namelist()


def test_generate_validation_error() -> None:
    bad = dict(_FORM, phone="123")
    res = client.post("/api/generate", json=bad)
    assert res.status_code == 422
    assert "no válido" in res.json()["detail"]


def test_preview_unknown_404() -> None:
    assert client.get("/preview/nope").status_code == 404
    assert client.get("/download/nope").status_code == 404


def test_serves_form_index() -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert "Faro" in res.text


def test_pack_persisted_to_disk(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server_mod, "_OUTPUT_DIR", tmp_path)
    local = TestClient(create_app(use_live=False))
    local.post("/api/generate", json=_FORM)
    saved = list(tmp_path.rglob("pack.zip"))  # type: ignore[attr-defined]
    assert len(saved) == 1
    assert saved[0].stat().st_size > 0
