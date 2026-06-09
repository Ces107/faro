"""Taxonomía OSM → sector Faro: mapeos, defaults y etiquetas."""

from __future__ import annotations

import pytest

from faro.business import Sector
from faro.prospect.taxonomy import category_label, regex_values, sector_for


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ({"amenity": "restaurant"}, Sector.RESTAURANTE),
        ({"amenity": "cafe"}, Sector.BAR),
        ({"shop": "bakery"}, Sector.PANADERIA),
        ({"shop": "hairdresser"}, Sector.PELUQUERIA),
        ({"shop": "car_repair"}, Sector.TALLER),
        ({"office": "estate_agent"}, Sector.INMOBILIARIA),
        ({"office": "accountant"}, Sector.ASESORIA),
        ({"leisure": "fitness_centre"}, Sector.GIMNASIO),
        ({"healthcare": "physiotherapist"}, Sector.FISIO),
        ({"craft": "electrician"}, Sector.REFORMAS),
        ({"craft": "photographer"}, Sector.AUTONOMO),
    ],
)
def test_exact_mappings(tags: dict[str, str], expected: Sector) -> None:
    assert sector_for(tags) is expected


def test_shop_unknown_value_falls_back_to_comercio() -> None:
    assert sector_for({"shop": "fishing"}) is Sector.COMERCIO
    assert category_label({"shop": "fishing"}) == "Fishing"
    # Los valores frecuentes tienen etiqueta cuidada en castellano, no el fallback.
    assert category_label({"shop": "furniture"}) == "Muebles"
    assert category_label({"shop": "books"}) == "Librería"
    assert category_label({"shop": "alcohol"}) == "Bodega"


def test_amenity_unknown_value_is_not_prospectable() -> None:
    assert sector_for({"amenity": "parking"}) is None
    assert sector_for({"amenity": "school"}) is None
    assert sector_for({}) is None


def test_labels_are_spanish() -> None:
    assert category_label({"amenity": "restaurant"}) == "Restaurante"
    assert category_label({"shop": "hairdresser"}) == "Peluquería"
    assert category_label({"office": "accountant"}) == "Gestoría"


def test_regex_values_cover_query_keys() -> None:
    # La query Overpass filtra estas claves por valores de la tabla: no pueden
    # quedarse vacías o el censo dejaría de ver esas categorías.
    for key in ("amenity", "office", "leisure", "healthcare"):
        assert regex_values(key), key
