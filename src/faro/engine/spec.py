"""``TemplateSpec``: qué es una plantilla de Faro.

Una plantilla compone tres cosas independientes:

- ``form_schema``: qué datos pide (formulario declarativo, ``engine.forms``).
- ``tokens``: cómo se ve (identidad visual, ``engine.design`` — se rellena por familia).
- ``blocks``: qué secciones tiene y en qué orden (``BlockRef`` — se rellena por familia).

Los campos visuales (``tokens``/``blocks``) son opcionales aquí a propósito: el
formulario declarativo funciona sin ellos, y las familias visuales se montan
encima cuando están definidas. Así el motor de formularios se entrega y prueba
sin esperar al rediseño visual.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from faro.business import Sector
from faro.engine.forms import FormSchema


@dataclass(frozen=True)
class BlockRef:
    """Una sección en el layout: qué bloque, con qué variante y opciones."""

    block: str
    variant: str = "default"
    opts: tuple[tuple[str, str], ...] = ()

    def opt(self, key: str, default: str = "") -> str:
        for k, v in self.opts:
            if k == key:
                return v
        return default


@dataclass(frozen=True)
class TemplateSpec:
    """Una plantilla = identidad (id/nombre/familia) + sectores + formulario + visual."""

    id: str
    name: str
    family: str
    sectors: tuple[Sector, ...]
    form_schema: FormSchema
    blocks: tuple[BlockRef, ...] = field(default_factory=tuple)
    summary: str = ""

    def covers(self, sector: Sector) -> bool:
        return sector in self.sectors
