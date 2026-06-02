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


def test_all_sectors_have_theme() -> None:
    for sector in Sector:
        theme = theme_for(sector)
        assert theme.label
        assert theme.color.startswith("#")


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
