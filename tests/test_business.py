"""Tests del modelo de negocio."""

from __future__ import annotations

import pytest

from faro.business import BusinessProfile, Sector, theme_for


def _valid(**overrides: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica Dental Sonríe",
        "sector": Sector.DENTAL,
        "city": "Puerto de Sagunto",
        "phone": "961234567",
        "services": ("Limpiezas", "Implantes"),
    }
    data.update(overrides)
    return BusinessProfile(**data)  # type: ignore[arg-type]


def test_valid_profile() -> None:
    biz = _valid()
    assert biz.name == "Clínica Dental Sonríe"
    assert biz.whatsapp == "961234567"  # por defecto = teléfono
    assert biz.phone_e164 == "34961234567"


def test_phone_is_cleaned() -> None:
    biz = _valid(phone="+34 961 23 45 67")
    assert biz.phone == "961234567"
    assert biz.phone_e164 == "34961234567"


def test_separate_whatsapp() -> None:
    biz = _valid(whatsapp="600111222")
    assert biz.whatsapp == "600111222"
    assert biz.whatsapp_e164 == "34600111222"


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "  "},
        {"city": ""},
        {"phone": "12345"},
        {"phone": "abcdefghi"},
        {"services": ()},
    ],
)
def test_invalid_profiles_raise(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _valid(**overrides)


def test_brand_color_override() -> None:
    biz = _valid(brand_color="#ff0000")
    assert biz.color == "#ff0000"
    assert biz.accent != "#ff0000"  # acento oscurecido
    assert biz.accent.startswith("#")


def test_color_defaults_to_sector() -> None:
    biz = _valid()
    assert biz.color == biz.theme.color


def test_hero_gradient_dark_color_unchanged() -> None:
    # Un color de marca oscuro se usa tal cual en el hero (contrasta con blanco).
    biz = _valid(brand_color="#1d4ed8")
    assert biz.hero_start == "#1d4ed8"


def test_hero_gradient_light_color_is_darkened() -> None:
    # Un color claro (amarillo) NO se usa tal cual: se oscurece para que el texto
    # blanco del hero siga siendo legible (TD-007).
    biz = _valid(brand_color="#ffff00")
    assert biz.hero_start != "#ffff00"
    # El inicio del degradado debe quedar claramente más oscuro que el amarillo puro.
    from faro.business import _luminance

    assert _luminance(biz.hero_start) < 0.6


def test_invalid_brand_color_raises() -> None:
    with pytest.raises(ValueError):
        _valid(brand_color="rojo")


def test_initials() -> None:
    assert _valid(name="Clínica Dental Sonríe").initials == "CD"
    assert _valid(name="Pepe").initials == "P"


def test_all_sectors_have_theme() -> None:
    for sector in Sector:
        theme = theme_for(sector)
        assert theme.label
        assert theme.color.startswith("#")
        assert theme.noun.startswith(("un ", "una "))


def test_long_fields_are_truncated() -> None:
    biz = _valid(name="X" * 200, services=("Y" * 200,))
    assert len(biz.name) == 60
    assert len(biz.services[0]) == 70


def test_new_sectors_work() -> None:
    for s in (Sector.BAR, Sector.FARMACIA, Sector.GIMNASIO, Sector.PANADERIA):
        biz = _valid(sector=s)
        assert biz.theme.label


def test_from_form_splits_lines() -> None:
    biz = BusinessProfile.from_form(
        {
            "name": "Taller Paco",
            "sector": "taller",
            "city": "Sagunto",
            "phone": "961112233",
            "services": "Cambio de aceite\nITV\nFrenos",
            "highlights": "30 años; Presupuesto gratis",
        }
    )
    assert biz.sector is Sector.TALLER
    assert biz.services == ("Cambio de aceite", "ITV", "Frenos")
    assert biz.highlights == ("30 años", "Presupuesto gratis")


def test_profile_is_immutable() -> None:
    biz = _valid()
    with pytest.raises(AttributeError):
        biz.name = "otro"  # type: ignore[misc]
