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
    autoridad_extras,
    carta_extras,
    clinica_extras,
    core_brand,
    core_conversion,
    core_identity,
    core_offer,
    core_story,
    core_trust,
    estudio_extras,
    family_schema,
    gimnasio_extras,
    industrial_extras,
)
from faro.engine.spec import TemplateSpec

_ALL_SECTORS: tuple[Sector, ...] = tuple(Sector)


def _base_schema() -> FormSchema:
    """El formulario común: identidad, historia, confianza y marca."""
    return FormSchema(
        (core_identity(), core_offer(), core_story(), core_trust(),
         core_conversion(), core_brand())
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


def _family(
    id_: str, name: str, family: str, sectors: tuple[Sector, ...],
    summary: str, schema: FormSchema,
) -> TemplateSpec:
    return TemplateSpec(
        id=id_, name=name, family=family, sectors=sectors,
        form_schema=schema, summary=summary,
    )


# Familias con dirección de arte propia (tokens en engine.design). Cada una
# reclama sus sectores y pide lo que su sector necesita (esquema propio); la
# universal queda de red de seguridad final con el formulario base.
CARTA = _family("carta", "Carta editorial", "carta",
                (Sector.RESTAURANTE, Sector.BAR, Sector.PANADERIA),
                "Gastronomía: foto a sangre, carta tipográfica, serif cálida.",
                family_schema("Carta o productos (uno por línea)",
                              "Croissant — 1,80 €\nMenú del día — 12,50 €",
                              carta_extras()))
CLINICA = _family("clinica", "Confianza clínica", "clinica",
                  (Sector.DENTAL, Sector.FISIO, Sector.VETERINARIO, Sector.FARMACIA),
                  "Salud: sereno, sobrio, confianza; nada de pastel genérico.",
                  family_schema("Tratamientos y servicios (uno por línea)",
                                "Limpieza dental\nOrtodoncia invisible",
                                clinica_extras()))
AUTORIDAD = _family("autoridad", "Autoridad serif", "autoridad",
                    (Sector.ASESORIA, Sector.INMOBILIARIA),
                    "Profesional: serif de autoridad, sobrio, institucional.",
                    family_schema("Áreas de práctica / servicios (uno por línea)",
                                  "Derecho laboral\nHerencias y sucesiones",
                                  autoridad_extras()))
INDUSTRIAL = _family("industrial", "Robusto industrial", "industrial",
                     (Sector.TALLER, Sector.REFORMAS),
                     "Oficios: tipografía pesada, alto contraste, presupuesto.",
                     family_schema("Servicios y trabajos (uno por línea)",
                                   "Chapa y pintura\nDiagnosis electrónica",
                                   industrial_extras()))
ESTUDIO = _family("estudio", "Editorial moda", "estudio",
                  (Sector.PELUQUERIA, Sector.ESTETICA),
                  "Belleza: galería protagonista, editorial blanco y negro.",
                  family_schema("Servicios (uno por línea)",
                                "Corte y peinado — 18 €\nColoración",
                                estudio_extras()))
GIMNASIO = _family("gimnasio", "Energía fitness", "gimnasio",
                   (Sector.GIMNASIO,),
                   "Gimnasio: modo oscuro, acento vivo, tipografía potente.",
                   family_schema("Clases y actividades (una por línea)",
                                 "Sala de musculación\nSpinning, Body Pump",
                                 gimnasio_extras()))

_TEMPLATES: tuple[TemplateSpec, ...] = (
    CARTA, CLINICA, AUTORIDAD, INDUSTRIAL, ESTUDIO, GIMNASIO, AURORA,
)


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
