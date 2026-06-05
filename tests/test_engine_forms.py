"""El formulario declarativo: estructura, serialización y compatibilidad con el modelo."""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.engine.forms import (
    FieldKind,
    FormField,
    FormSchema,
    core_brand,
    core_identity,
    core_story,
    core_trust,
)
from faro.engine.registry import all_templates, template_for


def _full_schema() -> FormSchema:
    return FormSchema((core_identity(), core_story(), core_trust(), core_brand()))


def test_schema_flattens_fields_in_order() -> None:
    schema = _full_schema()
    names = [f.name for f in schema.fields()]
    assert names[0] == "name"
    assert "about" in names
    assert "brand_color" in names
    # Sin duplicados.
    assert len(names) == len(set(names))


def test_required_core_fields_present() -> None:
    required = {f.name for f in _full_schema().fields() if f.required}
    assert {"name", "city", "phone"} <= required


def test_as_dict_is_json_shaped() -> None:
    data = _full_schema().as_dict()
    assert isinstance(data["groups"], list)
    first = data["groups"][0]
    assert "title" in first and "fields" in first
    field0 = first["fields"][0]
    assert set(field0) == {
        "name", "label", "kind", "required", "placeholder", "help", "options", "rows", "full_width",
    }


def test_select_options_serialize_as_pairs() -> None:
    f = FormField("x_cocina", "Tipo de cocina", FieldKind.SELECT,
                  options=(("med", "Mediterránea"), ("ita", "Italiana")))
    assert f.as_dict()["options"] == [["med", "Mediterránea"], ["ita", "Italiana"]]


def test_schema_field_names_drive_a_real_business() -> None:
    """Todo campo del esquema base existe en el modelo o es un destacado x_."""
    model_fields = set(BusinessProfile.__dataclass_fields__)
    for f in _full_schema().fields():
        assert f.name in model_fields or f.name.startswith("x_"), f.name


def test_x_prefixed_field_becomes_extra() -> None:
    """Un campo específico de plantilla (x_*) entra como dato destacado, sin tocar el parser."""
    biz = BusinessProfile.from_form({
        "name": "Bar Pepe", "city": "Sagunto", "phone": "961234567",
        "services": "Tapas", "x_terraza": "Sí", "x_para_llevar": "Sí",
    })
    # La etiqueta se capitaliza (chip legible en el hero), no se queda en minúscula.
    assert ("Terraza", "Sí") in biz.extras
    assert ("Para llevar", "Sí") in biz.extras


def test_each_family_asks_for_distinct_fields() -> None:
    """La demanda del principal: el formulario es DISTINTO según la plantilla.

    Las familias visuales (no la universal) divergen en al menos un campo x_
    propio; ninguna comparte exactamente el mismo conjunto de nombres.
    """
    visual = [t for t in all_templates() if t.family != "aurora"]
    name_sets = {t.family: t.form_schema.field_names() for t in visual}
    # Cada familia trae algún campo que otra no tiene.
    for family, names in name_sets.items():
        others = frozenset().union(
            *(n for f, n in name_sets.items() if f != family)
        )
        assert names - others, f"{family} no aporta ningún campo propio"


def test_family_offer_label_varies_by_template() -> None:
    """La etiqueta de 'lo que ofrecéis' cambia por familia (carta vs tratamientos)."""
    def offer_label(sector: Sector) -> str:
        schema = template_for(sector).form_schema
        return next(f.label for f in schema.fields() if f.name == "services")

    assert "Carta" in offer_label(Sector.RESTAURANTE)
    assert "Tratamientos" in offer_label(Sector.DENTAL)
    assert "Clases" in offer_label(Sector.GIMNASIO)


def test_family_specific_field_flows_to_web() -> None:
    """Un campo propio de la clínica (x_seguros) llega al modelo como dato real."""
    schema = template_for(Sector.DENTAL).form_schema
    assert "x_seguros" in schema.field_names()
    biz = BusinessProfile.from_form({
        "name": "Clínica Sonrisa", "city": "Sagunto", "phone": "961234567",
        "sector": "dental", "services": "Limpieza dental",
        "x_seguros": "Adeslas, Sanitas",
    })
    assert ("Seguros", "Adeslas, Sanitas") in biz.extras


def test_universal_template_keeps_generic_offer() -> None:
    """La plantilla universal (aurora) no impone vocabulario de un sector concreto."""
    schema = template_for(Sector.OTRO).form_schema
    label = next(f.label for f in schema.fields() if f.name == "services")
    assert "Servicios o productos" in label
