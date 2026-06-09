"""CLI faro-prospect end-to-end con fetcher inyectado (sin red)."""

from __future__ import annotations

import json
from pathlib import Path

from faro.prospect.cli import main

_RESOLVE_RESPONSE = json.dumps(
    {
        "elements": [
            {
                "type": "relation",
                "id": 348833,
                "tags": {"name": "Sagunt / Sagunto", "admin_level": "8"},
            }
        ]
    }
).encode()

_POIS_RESPONSE = json.dumps(
    {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 39.68,
                "lon": -0.24,
                "timestamp": "2025-01-01T00:00:00Z",
                "tags": {
                    "amenity": "bar",
                    "name": "Cervecería Turia",
                    "addr:street": "Carrer Camí Reial",
                    "phone": "+34 600 111 222",
                },
            },
            {
                "type": "node",
                "id": 2,
                "lat": 39.50,
                "lon": -0.40,
                "tags": {"amenity": "bar", "name": "Bar Lejano"},
            },
            {
                "type": "node",
                "id": 3,
                "lat": 39.66,
                "lon": -0.23,
                "tags": {"shop": "supermarket", "name": "masymas", "brand": "masymas"},
            },
        ]
    }
).encode()


def _fake_fetch(url: str, data: bytes, timeout: float) -> bytes:
    return _RESOLVE_RESPONSE if b"boundary" in data else _POIS_RESPONSE


def test_cli_writes_all_artifacts(tmp_path: Path, capsys: object) -> None:
    out = tmp_path / "prospect"
    code = main(
        [
            "Sagunto",
            "--out",
            str(out),
            "--bbox",
            "39.62,-0.256,39.69,-0.19",
            "--city",
            "Puerto de Sagunto",
        ],
        fetch=_fake_fetch,
    )
    assert code == 0
    municipality_dir = out / "puerto-de-sagunto"
    census = json.loads((municipality_dir / "census.json").read_text(encoding="utf-8"))
    assert census["municipality"] == "Sagunt / Sagunto"
    assert [p["name"] for p in census["prospects"]] == ["Cervecería Turia"]
    assert census["excluded"]["fuera_de_zona"] == 1
    assert census["excluded"]["cadena_con_marca"] == 1
    prefills = json.loads((municipality_dir / "prospects.json").read_text(encoding="utf-8"))
    entry = prefills["cerveceria-turia"]
    assert entry["sector"] == "bar"
    assert entry["values"]["city"] == "Puerto de Sagunto"
    route = (municipality_dir / "ruta.html").read_text(encoding="utf-8")
    assert "Cervecería Turia" in route
    assert "© OpenStreetMap contributors" in route
    flyers = (municipality_dir / "folletos.html").read_text(encoding="utf-8")
    assert "data:image/svg+xml" in flyers


def test_cli_rel_id_skips_resolution(tmp_path: Path) -> None:
    calls: list[bytes] = []

    def tracking_fetch(url: str, data: bytes, timeout: float) -> bytes:
        calls.append(data)
        return _POIS_RESPONSE

    code = main(
        ["Sagunto", "--rel-id", "348833", "--out", str(tmp_path / "p")],
        fetch=tracking_fetch,
    )
    assert code == 0
    assert len(calls) == 1  # solo la query de POIs, sin resolución
    assert b"3600348833" in calls[0]


def test_cli_bad_bbox_fails_with_clear_error(tmp_path: Path, capsys: object) -> None:
    code = main(
        ["Sagunto", "--rel-id", "348833", "--bbox", "mal", "--out", str(tmp_path / "p")],
        fetch=_fake_fetch,
    )
    assert code == 2
