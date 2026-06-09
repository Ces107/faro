"""Censo de prospección: filtrado, puntuación, slugs y recorte geográfico."""

from __future__ import annotations

from faro.business import Sector
from faro.prospect.census import (
    BoundingBox,
    ExcludeReason,
    build_census,
    prefill_values,
)

# Elementos con la forma real de la respuesta Overpass (los dos primeros son
# POIs reales de Sagunto del probe 2026-06-10; el resto, casos límite).
# Coordenadas dentro del bbox del Puerto (el bar real está en el casco, fuera).
_TURIA = {
    "type": "node",
    "id": 1911936649,
    "lat": 39.6799214,
    "lon": -0.2400000,
    "timestamp": "2025-03-12T10:00:00Z",
    "tags": {
        "addr:housenumber": "6",
        "addr:street": "Carrer Camí Reial",
        "amenity": "bar",
        "name": "Cervecería Turia",
    },
}
_VETERINARIA = {
    "type": "node",
    "id": 2,
    "lat": 39.66,
    "lon": -0.23,
    "timestamp": "2019-01-01T00:00:00Z",
    "tags": {
        "amenity": "veterinary",
        "name": "Clínica Veterinaria Namaste",
        "check_date": "2026-02-19",
        "phone": "+34 962 000 000",
        "opening_hours": "Mo-Fr 09:00-20:00",
        "addr:street": "Av. del Camp de Morvedre",
    },
}
_CADENA = {
    "type": "node",
    "id": 3,
    "lat": 39.66,
    "lon": -0.23,
    "tags": {"shop": "supermarket", "name": "masymas", "brand": "masymas"},
}
_CON_WEB = {
    "type": "node",
    "id": 4,
    "lat": 39.66,
    "lon": -0.23,
    "tags": {"shop": "clothes", "name": "Boutique Eva", "website": "https://eva.example"},
}
_WAY_TALLER = {
    "type": "way",
    "id": 5,
    "center": {"lat": 39.662, "lon": -0.234},
    "timestamp": "2015-06-01T00:00:00Z",
    "tags": {"shop": "car_repair", "name": "Taller Máximo Lizana"},
}
_SIN_NOMBRE = {"type": "node", "id": 6, "lat": 39.66, "lon": -0.23, "tags": {"shop": "bakery"}}
_PARKING = {
    "type": "node",
    "id": 7,
    "lat": 39.66,
    "lon": -0.23,
    "tags": {"amenity": "parking", "name": "Parking Centro"},
}
_FUERA = {
    "type": "node",
    "id": 8,
    "lat": 39.50,
    "lon": -0.40,
    "tags": {"amenity": "bar", "name": "Bar Lejano"},
}

_ALL = [_TURIA, _VETERINARIA, _CADENA, _CON_WEB, _WAY_TALLER, _SIN_NOMBRE, _PARKING, _FUERA]
_BBOX = BoundingBox(south=39.62, west=-0.256, north=39.69, east=-0.19)


def _census() -> object:
    return build_census(list(_ALL), municipality="Sagunt / Sagunto", bbox=_BBOX)


def test_filters_and_counters() -> None:
    census = _census()
    names = [p.name for p in census.prospects]
    assert "Cervecería Turia" in names
    assert "Clínica Veterinaria Namaste" in names
    assert "Taller Máximo Lizana" in names
    assert "masymas" not in names  # cadena con brand
    assert "Boutique Eva" not in names  # ya tiene web
    assert "Parking Centro" not in names  # categoría no prospectable
    assert "Bar Lejano" not in names  # fuera del bbox
    assert census.total_raw == len(_ALL)
    assert census.excluded_count(ExcludeReason.CHAIN) == 1
    assert census.excluded_count(ExcludeReason.HAS_WEB_PRESENCE) == 1
    assert census.excluded_count(ExcludeReason.NO_NAME) == 1
    assert census.excluded_count(ExcludeReason.UNMAPPED_CATEGORY) == 1
    assert census.excluded_count(ExcludeReason.OUT_OF_BBOX) == 1


def test_scoring_prioritises_fresh_and_edge_families() -> None:
    census = _census()
    by_name = {p.name: p for p in census.prospects}
    turia = by_name["Cervecería Turia"]
    veterinaria = by_name["Clínica Veterinaria Namaste"]
    taller = by_name["Taller Máximo Lizana"]
    # carta (3) + editado 2025 (1) + calle (1) = 5
    assert turia.score == 5
    # clinica (2) + check_date 2026 (2) + calle (1) + horario (1) + teléfono (1) = 7
    assert veterinaria.score == 7
    # industrial (2) + sin frescura + sin calle = 2; además es dato viejo
    assert taller.score == 2
    assert taller.stale is True
    assert veterinaria.stale is False
    assert census.prospects[0] is veterinaria  # orden por score desc


def test_way_center_coordinates_and_sector_mapping() -> None:
    census = _census()
    taller = next(p for p in census.prospects if p.name == "Taller Máximo Lizana")
    assert (taller.lat, taller.lon) == (39.662, -0.234)
    assert taller.sector is Sector.TALLER
    assert taller.family == "industrial"
    assert taller.osm_ref == "way/5"


def test_slug_collisions_get_suffix() -> None:
    duplicated = [
        dict(_TURIA),
        {**_TURIA, "id": 99, "tags": {**_TURIA["tags"], "addr:housenumber": "8"}},
    ]
    census = build_census(duplicated, municipality="Sagunt")
    slugs = sorted(p.slug for p in census.prospects)
    assert slugs == ["cerveceria-turia", "cerveceria-turia-2"]


def test_prefill_takes_first_phone_of_multivalue() -> None:
    multi = {
        "type": "node",
        "id": 10,
        "lat": 39.66,
        "lon": -0.23,
        "tags": {
            "amenity": "veterinary",
            "name": "Multi Tel",
            "phone": "+34 96 268 11 76;+34 96 378 44 40",
        },
    }
    census = build_census([multi], municipality="Sagunt")
    values = prefill_values(census.prospects[0], city="Puerto de Sagunto")
    assert values["phone"] == "+34 96 268 11 76"


def test_prefill_only_real_public_data() -> None:
    census = _census()
    veterinaria = next(p for p in census.prospects if "Veterinaria" in p.name)
    values = prefill_values(veterinaria, city="Puerto de Sagunto")
    assert values["name"] == "Clínica Veterinaria Namaste"
    assert values["city"] == "Puerto de Sagunto"
    assert values["phone"] == "+34 962 000 000"
    assert values["address"].startswith("Av. del Camp de Morvedre")
    # Nada inventado: ni servicios, ni horario, ni descripción.
    assert "services" not in values
    assert "hours" not in values
    assert "about" not in values
