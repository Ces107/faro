"""El formulario declarativo: estructura, serialización y compatibilidad con el modelo."""

from __future__ import annotations

from faro.business import BusinessProfile
from faro.engine.forms import (
    FieldKind,
    FormField,
    FormSchema,
    core_brand,
    core_identity,
    core_story,
    core_trust,
)


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
        "services": "Tapas", "x_terraza": "Sí",
    })
    assert ("terraza", "Sí") in biz.extras
