"""Censo de prospección. Eje de cambio: reglas de filtrado, puntuación y prioridad.

Núcleo puro: recibe elementos Overpass ya descargados y produce la lista
priorizada de negocios candidatos. Sin red, sin disco, sin reloj.

Límite honesto (documentado en el red-team 2026-06-10): que un negocio no tenga
web mapeada en OSM NO garantiza que no tenga web real. El censo es una lista de
CANDIDATOS de baja confianza; la verificación final es el vistazo a Google en la
puerta que ya manda el guion de venta. Los teléfonos se conservan en el censo
local para el prefill, pero NUNCA se imprimen en la hoja de ruta (minimización).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import Enum

from faro.business import Sector
from faro.engine.registry import template_for
from faro.prospect.taxonomy import category_label, sector_for

__all__ = [
    "Prospect",
    "ExcludeReason",
    "CensusResult",
    "BoundingBox",
    "build_census",
    "prefill_values",
]

# Presencia digital ya mapeada en OSM → el negocio no es el cliente objetivo.
_WEB_PRESENCE_TAGS: tuple[str, ...] = (
    "website",
    "contact:website",
    "contact:facebook",
    "contact:instagram",
    "facebook",
    "instagram",
    "url",
)

# Ediciones anteriores a este año sin check_date se marcan como dato dudoso
# (riesgo real de negocio cerrado: 38% del pool de Sagunto no se toca desde 2016).
_STALE_BEFORE_YEAR = 2020
_FRESH_FROM_YEAR = 2024

# Peso de cada familia visual: la familia "carta" lleva el edge regulatorio del
# producto (alérgenos UE 1169/2011), las de resultados visuales van después.
_FAMILY_WEIGHT: dict[str, int] = {
    "carta": 3,
    "clinica": 2,
    "estudio": 2,
    "industrial": 2,
    "autoridad": 1,
    "gimnasio": 1,
    "aurora": 1,
}


class ExcludeReason(str, Enum):
    """Por qué un POI no entra en el censo (contadores de transparencia)."""

    NO_NAME = "sin_nombre"
    CHAIN = "cadena_con_marca"
    HAS_WEB_PRESENCE = "con_presencia_web"
    UNMAPPED_CATEGORY = "categoria_no_prospectable"
    OUT_OF_BBOX = "fuera_de_zona"
    NO_COORDS = "sin_coordenadas"


@dataclass(frozen=True)
class BoundingBox:
    """Recorte geográfico (sur, oeste, norte, este) en grados WGS84."""

    south: float
    west: float
    north: float
    east: float

    def contains(self, lat: float, lon: float) -> bool:
        return self.south <= lat <= self.north and self.west <= lon <= self.east


@dataclass(frozen=True)
class Prospect:
    """Un negocio candidato, con lo necesario para la ruta y el prefill."""

    slug: str
    name: str
    sector: Sector
    category: str
    family: str
    lat: float
    lon: float
    street: str
    housenumber: str
    postcode: str
    phone: str
    opening_hours: str
    last_edit_year: int
    checked_recently: bool
    score: int
    osm_ref: str

    @property
    def stale(self) -> bool:
        """Dato viejo sin verificación reciente: posible negocio cerrado."""
        return not self.checked_recently and 0 < self.last_edit_year < _STALE_BEFORE_YEAR


@dataclass(frozen=True)
class CensusResult:
    """Censo priorizado + contadores de lo excluido (transparencia del filtro)."""

    municipality: str
    prospects: tuple[Prospect, ...]
    excluded: tuple[tuple[ExcludeReason, int], ...]
    total_raw: int

    def excluded_count(self, reason: ExcludeReason) -> int:
        return dict(self.excluded).get(reason, 0)


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = "".join(c if c.isalnum() else "-" for c in normalized.lower())
    return "-".join(filter(None, slug.split("-")))[:48] or "negocio"


def _coords(element: dict[str, object]) -> tuple[float, float] | None:
    """Coordenadas de un node (lat/lon) o de un way/relation (center)."""
    lat, lon = element.get("lat"), element.get("lon")
    if isinstance(lat, int | float) and isinstance(lon, int | float):
        return float(lat), float(lon)
    center = element.get("center")
    if isinstance(center, dict):
        clat, clon = center.get("lat"), center.get("lon")
        if isinstance(clat, int | float) and isinstance(clon, int | float):
            return float(clat), float(clon)
    return None


def _edit_year(element: dict[str, object]) -> int:
    """Año de la última edición OSM (0 si la respuesta no trae metadatos)."""
    timestamp = element.get("timestamp")
    if isinstance(timestamp, str) and len(timestamp) >= 4 and timestamp[:4].isdigit():
        return int(timestamp[:4])
    return 0


def _checked_recently(tags: dict[str, str]) -> bool:
    for key in ("check_date", "survey:date"):
        value = tags.get(key, "")
        if len(value) >= 4 and value[:4].isdigit() and int(value[:4]) >= _FRESH_FROM_YEAR:
            return True
    return False


def _score(sector: Sector, family: str, tags: dict[str, str], edit_year: int, checked: bool) -> int:
    score = _FAMILY_WEIGHT.get(family, 1)
    if checked:
        score += 2
    elif edit_year >= _FRESH_FROM_YEAR:
        score += 1
    if tags.get("addr:street"):
        score += 1
    if tags.get("opening_hours"):
        score += 1
    if tags.get("phone") or tags.get("contact:phone"):
        score += 1
    return score


def _exclude_reason(
    tags: dict[str, str],
    coords: tuple[float, float] | None,
    sector: Sector | None,
    bbox: BoundingBox | None,
) -> ExcludeReason | None:
    if not tags.get("name", "").strip():
        return ExcludeReason.NO_NAME
    if coords is None:
        return ExcludeReason.NO_COORDS
    if bbox is not None and not bbox.contains(*coords):
        return ExcludeReason.OUT_OF_BBOX
    if tags.get("brand") or tags.get("brand:wikidata"):
        return ExcludeReason.CHAIN
    if any(tags.get(t) for t in _WEB_PRESENCE_TAGS):
        return ExcludeReason.HAS_WEB_PRESENCE
    if sector is None:
        return ExcludeReason.UNMAPPED_CATEGORY
    return None


def _build_prospect(
    element: dict[str, object],
    tags: dict[str, str],
    slug: str,
    coords: tuple[float, float],
    sector: Sector,
) -> Prospect:
    family = template_for(sector).family
    edit_year = _edit_year(element)
    checked = _checked_recently(tags)
    return Prospect(
        slug=slug,
        name=tags["name"].strip(),
        sector=sector,
        category=category_label(tags),
        family=family,
        lat=coords[0],
        lon=coords[1],
        street=tags.get("addr:street", "").strip(),
        housenumber=tags.get("addr:housenumber", "").strip(),
        postcode=tags.get("addr:postcode", "").strip(),
        phone=(tags.get("phone") or tags.get("contact:phone", "")).strip(),
        opening_hours=tags.get("opening_hours", "").strip(),
        last_edit_year=edit_year,
        checked_recently=checked,
        score=_score(sector, family, tags, edit_year, checked),
        osm_ref=f"{element.get('type', 'node')}/{element.get('id', 0)}",
    )


def build_census(
    elements: list[dict[str, object]],
    *,
    municipality: str,
    bbox: BoundingBox | None = None,
) -> CensusResult:
    """Convierte elementos Overpass en el censo priorizado de candidatos."""
    counters: dict[ExcludeReason, int] = {}
    prospects: list[Prospect] = []
    used_slugs: dict[str, int] = {}
    for element in elements:
        tags_raw = element.get("tags")
        tags: dict[str, str] = tags_raw if isinstance(tags_raw, dict) else {}
        coords = _coords(element)
        sector = sector_for(tags)
        reason = _exclude_reason(tags, coords, sector, bbox)
        if reason is not None:
            counters[reason] = counters.get(reason, 0) + 1
            continue
        base = _slugify(tags["name"])
        used_slugs[base] = used_slugs.get(base, 0) + 1
        slug = base if used_slugs[base] == 1 else f"{base}-{used_slugs[base]}"
        if coords is not None and sector is not None:  # garantizado por _exclude_reason
            prospects.append(_build_prospect(element, tags, slug, coords, sector))
    prospects.sort(key=lambda p: (-p.score, p.street or "zzz", p.name))
    return CensusResult(
        municipality=municipality,
        prospects=tuple(prospects),
        excluded=tuple(sorted(counters.items(), key=lambda kv: kv[0].value)),
        total_raw=len(elements),
    )


def prefill_values(prospect: Prospect, *, city: str) -> dict[str, str]:
    """Campos del formulario Faro que el censo puede rellenar SIN inventar nada.

    Solo datos públicos verificables: nombre, ciudad, dirección y teléfono.
    Servicios, horario y el resto los dicta el dueño en la puerta — el producto
    no inventa contenido (norma de honestidad del rediseño 2026-06-03).
    """
    values: dict[str, str] = {"name": prospect.name, "city": city}
    if prospect.street:
        address = prospect.street
        if prospect.housenumber:
            address += f" {prospect.housenumber}"
        if prospect.postcode:
            address += f", {prospect.postcode}"
        values["address"] = address
    if prospect.phone:
        # OSM admite varios teléfonos separados por ";": el formulario espera UNO
        # (alimenta el wa.me); el dueño confirma o corrige en la puerta.
        values["phone"] = prospect.phone.split(";")[0].strip()
    return values
