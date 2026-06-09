"""Cliente Overpass (OpenStreetMap). Eje de cambio: protocolo de la API Overpass.

Capa de E/S del censo: resuelve el municipio (los valencianos usan nombre
bilingüe, "Sagunt / Sagunto", así que NUNCA se busca por nombre exacto) y
descarga los POIs de negocio. Sin dependencias nuevas: ``urllib`` de la stdlib.

Lecciones del probe empírico 2026-06-10 incorporadas:
- overpass-api.de devuelve 406 sin un User-Agent identificable.
- El área de un municipio es ``3600000000 + id`` de su relación administrativa.
- Hay réplicas públicas para cuando el endpoint principal está saturado.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from faro.prospect.taxonomy import regex_values

__all__ = [
    "ProspectError",
    "Municipality",
    "HttpFetcher",
    "default_fetcher",
    "resolve_municipality",
    "fetch_pois",
]

_ENDPOINTS: tuple[str, ...] = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
_USER_AGENT = "faro-prospect/0.1 (+https://github.com/Ces107/faro)"
_TIMEOUT_S = 90.0
_AREA_OFFSET = 3_600_000_000  # convención Overpass: área de una relación


class ProspectError(RuntimeError):
    """Fallo de prospección con mensaje accionable para el operador."""


class HttpFetcher(Protocol):
    """E/S inyectable: POST del cuerpo ``data`` y devuelve los bytes de respuesta."""

    def __call__(self, url: str, data: bytes, timeout: float) -> bytes: ...


def _urllib_fetch(url: str, data: bytes, timeout: float) -> bytes:
    request = urllib.request.Request(  # noqa: S310 — endpoints https fijos de módulo
        url, data=data, headers={"User-Agent": _USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        return bytes(response.read())


# Fetcher por defecto, expuesto para las capas imperativas (CLI).
default_fetcher: HttpFetcher = _urllib_fetch


@dataclass(frozen=True)
class Municipality:
    """Relación administrativa OSM resuelta para un municipio."""

    rel_id: int
    name: str

    @property
    def area_id(self) -> int:
        return _AREA_OFFSET + self.rel_id


def _post_query(query: str, fetch: HttpFetcher) -> dict[str, object]:
    body = ("data=" + urllib.parse.quote(query)).encode()
    last_error: Exception | None = None
    for endpoint in _ENDPOINTS:
        try:
            raw = fetch(endpoint, body, _TIMEOUT_S)
            result = json.loads(raw)
            if isinstance(result, dict):
                return result
            last_error = ProspectError(f"Respuesta no reconocida de {endpoint}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last_error = exc
    raise ProspectError(
        "No se pudo consultar Overpass en ningún endpoint "
        f"({', '.join(_ENDPOINTS)}). Último error: {last_error}"
    )


def _elements(result: dict[str, object]) -> list[dict[str, object]]:
    elements = result.get("elements")
    if not isinstance(elements, list):
        return []
    return [e for e in elements if isinstance(e, dict)]


def resolve_municipality(name: str, *, fetch: HttpFetcher = _urllib_fetch) -> Municipality:
    """Encuentra la relación administrativa (admin_level=8) cuyo nombre contiene ``name``.

    Búsqueda por regex insensible a mayúsculas: cubre los nombres bilingües
    valencianos ("Sagunt / Sagunto" responde tanto a "sagunt" como a "sagunto").
    """
    pattern = re.escape(name.strip())
    if not pattern:
        raise ProspectError("Indica el nombre del municipio (p. ej. 'Sagunto').")
    query = (
        '[out:json][timeout:30];relation["boundary"="administrative"]'
        f'["admin_level"="8"]["name"~"{pattern}",i];out tags;'
    )
    matches = [
        (int(str(e.get("id", 0))), str(_tags(e).get("name", "")))
        for e in _elements(_post_query(query, fetch))
    ]
    if not matches:
        raise ProspectError(
            f"Ningún municipio (admin_level=8) contiene '{name}'. "
            "Prueba el nombre oficial (puede ser bilingüe, p. ej. 'Sagunt')."
        )
    if len(matches) > 1:
        listing = "; ".join(f"{mid}: {mname}" for mid, mname in matches[:8])
        raise ProspectError(
            f"'{name}' es ambiguo ({len(matches)} municipios): {listing}. "
            "Re-lanza con --rel-id <id> para fijar uno."
        )
    rel_id, full_name = matches[0]
    return Municipality(rel_id=rel_id, name=full_name or name)


def _tags(element: dict[str, object]) -> dict[str, str]:
    tags = element.get("tags")
    return tags if isinstance(tags, dict) else {}


def _pois_query(area_id: int) -> str:
    amenity = "|".join(regex_values("amenity"))
    office = "|".join(regex_values("office"))
    leisure = "|".join(regex_values("leisure"))
    healthcare = "|".join(regex_values("healthcare"))
    selectors = (
        'node["shop"](area.a);way["shop"](area.a);'
        f'node["amenity"~"^({amenity})$"](area.a);way["amenity"~"^({amenity})$"](area.a);'
        'node["craft"](area.a);way["craft"](area.a);'
        f'node["office"~"^({office})$"](area.a);way["office"~"^({office})$"](area.a);'
        f'node["leisure"~"^({leisure})$"](area.a);way["leisure"~"^({leisure})$"](area.a);'
        f'node["healthcare"~"^({healthcare})$"](area.a);'
        f'way["healthcare"~"^({healthcare})$"](area.a);'
    )
    return f"[out:json][timeout:90];area({area_id})->.a;({selectors});out meta center;"


def fetch_pois(
    municipality: Municipality, *, fetch: HttpFetcher = _urllib_fetch
) -> list[dict[str, object]]:
    """Descarga los POIs de negocio del municipio (con metadatos de frescura)."""
    return _elements(_post_query(_pois_query(municipality.area_id), fetch))
