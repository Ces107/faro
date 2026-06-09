"""Hoja de ruta: agrupación, enlaces, minimización de datos y atribución ODbL."""

from __future__ import annotations

from faro.prospect.census import build_census
from faro.prospect.route import route_sheet_html

_ELEMENTS = [
    {
        "type": "node",
        "id": 1,
        "lat": 39.68,
        "lon": -0.28,
        "tags": {
            "amenity": "bar",
            "name": "Cervecería Turia",
            "addr:street": "Carrer Camí Reial",
            "addr:housenumber": "6",
            "phone": "+34 600 111 222",
        },
    },
    {
        "type": "node",
        "id": 2,
        "lat": 39.66,
        "lon": -0.23,
        "tags": {"shop": "hairdresser", "name": 'Peluquería <script>alert("x")</script>'},
    },
    {
        "type": "node",
        "id": 3,
        "lat": 39.67,
        "lon": -0.24,
        "tags": {
            "amenity": "restaurant",
            "name": "Mesón Del Cordero",
            "addr:street": "Carrer Camí Reial",
            "timestamp": "2016-01-01T00:00:00Z",
        },
    },
]


def _sheet() -> str:
    census = build_census(list(_ELEMENTS), municipality="Sagunt / Sagunto")
    return route_sheet_html(census, generated_on="2026-06-10")


def test_odbl_attribution_and_no_index() -> None:
    sheet = _sheet()
    assert "© OpenStreetMap contributors" in sheet
    assert "ODbL" in sheet
    assert 'name="robots" content="noindex,nofollow"' in sheet


def test_phones_never_printed() -> None:
    # Minimización RGPD: el censo conserva el teléfono pero la hoja NUNCA lo imprime.
    sheet = _sheet()
    assert "600 111 222" not in sheet
    assert "+34" not in sheet


def test_grouped_by_street_with_fallback_group() -> None:
    sheet = _sheet()
    assert "Carrer Camí Reial" in sheet
    assert "Sin calle mapeada" in sheet
    # La calle con candidatos aparece antes que el grupo sin calle.
    assert sheet.index("Carrer Camí Reial") < sheet.index("Sin calle mapeada")


def test_names_escaped_and_links_present() -> None:
    sheet = _sheet()
    assert "<script>alert(" not in sheet
    assert "&lt;script&gt;" in sheet
    assert "?prefill=cerveceria-turia" in sheet
    assert "openstreetmap.org/node/1" in sheet
    assert "google.com/search" in sheet


def test_checkbox_and_notes_column() -> None:
    sheet = _sheet()
    assert "&#9744;" in sheet  # casilla imprimible
    assert 'class="notes"' in sheet
