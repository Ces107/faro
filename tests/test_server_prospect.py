"""Endpoints /api/prospect del servidor: índice y precarga del formulario."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import faro.server as server_module
from faro.server import create_app

_PROSPECTS = {
    "cerveceria-turia": {
        "sector": "bar",
        "values": {"name": "Cervecería Turia", "city": "Puerto de Sagunto"},
    }
}


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    municipality = tmp_path / "puerto-de-sagunto"
    municipality.mkdir(parents=True)
    (municipality / "prospects.json").write_text(
        json.dumps(_PROSPECTS, ensure_ascii=False), encoding="utf-8"
    )
    monkeypatch.setattr(server_module, "_PROSPECT_DIR", tmp_path)
    return TestClient(create_app(use_live=False))


def test_prospect_index_lists_census(client: TestClient) -> None:
    res = client.get("/api/prospect")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    assert data["prospects"][0]["slug"] == "cerveceria-turia"


def test_prefill_found(client: TestClient) -> None:
    res = client.get("/api/prospect/prefill/cerveceria-turia")
    assert res.status_code == 200
    data = res.json()
    assert data["sector"] == "bar"
    assert data["values"]["name"] == "Cervecería Turia"


def test_prefill_missing_404(client: TestClient) -> None:
    assert client.get("/api/prospect/prefill/no-existe").status_code == 404


def test_no_census_dir_means_empty_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server_module, "_PROSPECT_DIR", tmp_path / "nada")
    client = TestClient(create_app(use_live=False))
    res = client.get("/api/prospect")
    assert res.status_code == 200
    assert res.json()["count"] == 0
