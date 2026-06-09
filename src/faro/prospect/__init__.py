"""faro.prospect — censo de prospección sobre OpenStreetMap.

Convierte un municipio en una salida de venta: censo priorizado de negocios
sin presencia web mapeada, hoja de ruta imprimible por calles, formulario
precargado por negocio y folletos por sector. Ver ``docs/prospect.md``.
"""

from faro.prospect.census import (
    BoundingBox,
    CensusResult,
    ExcludeReason,
    Prospect,
    build_census,
    prefill_values,
)
from faro.prospect.flyers import flyers_html
from faro.prospect.overpass import (
    Municipality,
    ProspectError,
    fetch_pois,
    resolve_municipality,
)
from faro.prospect.route import route_sheet_html

__all__ = [
    "BoundingBox",
    "CensusResult",
    "ExcludeReason",
    "Municipality",
    "Prospect",
    "ProspectError",
    "build_census",
    "fetch_pois",
    "flyers_html",
    "prefill_values",
    "resolve_municipality",
    "route_sheet_html",
]
