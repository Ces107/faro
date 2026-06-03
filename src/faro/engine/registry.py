"""Catálogo de plantillas y resolución por sector o por id.

Hoy hay una plantilla universal (``aurora``) que cubre todos los sectores con el
formulario base. Las familias visuales con su propio formulario (carta, clínica,
obra, estudio, despacho...) se registran aquí a medida que se construyen: cada
una declara los sectores que cubre y ``template_for`` la prefiere sobre la
universal. Añadir una familia = añadir un ``TemplateSpec`` a ``_TEMPLATES``.
"""

from __future__ import annotations

from faro.business import Sector
from faro.engine.forms import (
    FormSchema,
    core_brand,
    core_identity,
    core_offer,
    core_story,
    core_trust,
)
from faro.engine.spec import TemplateSpec

_ALL_SECTORS: tuple[Sector, ...] = tuple(Sector)


def _base_schema() -> FormSchema:
    """El formulario común: identidad, historia, confianza y marca."""
    return FormSchema(
        (core_identity(), core_offer(), core_story(), core_trust(), core_brand())
    )


# La plantilla universal. Cubre cualquier sector que ninguna familia reclame.
AURORA = TemplateSpec(
    id="aurora",
    name="Universal",
    family="aurora",
    sectors=_ALL_SECTORS,
    form_schema=_base_schema(),
    summary="Plantilla base, válida para cualquier negocio.",
)

# Las familias específicas se insertan ANTES de la universal: la primera que
# cubre el sector gana. La universal queda siempre como red de seguridad final.
_TEMPLATES: tuple[TemplateSpec, ...] = (AURORA,)


def all_templates() -> tuple[TemplateSpec, ...]:
    return _TEMPLATES


def template_for(sector: Sector) -> TemplateSpec:
    """La plantilla específica que cubre el sector, o la universal."""
    for spec in _TEMPLATES:
        if spec.family != "aurora" and spec.covers(sector):
            return spec
    return AURORA


def template_by_id(template_id: str) -> TemplateSpec:
    for spec in _TEMPLATES:
        if spec.id == template_id:
            return spec
    return AURORA
