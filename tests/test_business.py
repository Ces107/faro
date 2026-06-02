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


def test_hero_gradient_readable_with_white_for_any_brand() -> None:
    # El texto blanco del hero debe cumplir contraste WCAG AA (>=4.5) con cualquier
    # color de marca, incluidos los claros (amarillo) y los saturados (cian).
    from faro.business import contrast_ratio

    for color in ("#1d4ed8", "#ffff00", "#0ea5e9", "#ec4899", "#10b981"):
        biz = _valid(brand_color=color)
        assert contrast_ratio("#ffffff", biz.hero_start) >= 4.5


def test_light_color_is_darkened_for_hero() -> None:
    biz = _valid(brand_color="#ffff00")
    assert biz.hero_start != "#ffff00"


def test_accent_readable_on_white() -> None:
    # El color de acento (eyebrows, cifras, chips) debe leerse sobre blanco.
    from faro.business import contrast_ratio

    for color in ("#ffe066", "#0ea5e9", "#10b981"):
        assert contrast_ratio("#ffffff", _valid(brand_color=color).accent) >= 4.5


def test_on_brand_picks_max_contrast() -> None:
    from faro.business import contrast_ratio

    for color in ("#ffff00", "#0a3d62", "#0ea5e9"):
        biz = _valid(brand_color=color)
        chosen = biz.on_brand
        other = "#0f172a" if chosen == "#ffffff" else "#ffffff"
        assert contrast_ratio(chosen, color) >= contrast_ratio(other, color)


def test_invalid_brand_color_raises() -> None:
    with pytest.raises(ValueError):
        _valid(brand_color="rojo")


def test_on_brand_contrast() -> None:
    assert _valid(brand_color="#ffff00").on_brand == "#0f172a"  # claro -> texto oscuro
    assert _valid(brand_color="#0a3d62").on_brand == "#ffffff"  # oscuro -> texto blanco


def test_photos_filtered_and_capped() -> None:
    biz = _valid(photos=("https://a/1.jpg", "no-url", "http://b/2.jpg"))
    assert biz.photos == ("https://a/1.jpg", "http://b/2.jpg")


def test_testimonials_kept() -> None:
    from faro.business import Testimonial

    biz = _valid(testimonials=(Testimonial("Muy bueno", "Ana", "Cliente"),))
    assert biz.testimonials[0].author == "Ana"


def test_canonical_only_http() -> None:
    assert _valid(canonical_url="https://x.com").canonical_url == "https://x.com"
    assert _valid(canonical_url="javascript:alert(1)").canonical_url == ""


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
