"""Carta estructurada: parser, alérgenos UE, render y schema.org."""

from __future__ import annotations

from faro.business import BusinessProfile
from faro.landing import build_landing
from faro.menu import Allergen, all_allergens_present, normalize_allergens, parse_menu
from faro.seo import local_business_jsonld


def test_parser_splits_categories_and_items() -> None:
    menu = parse_menu(
        "Entrantes:\n"
        "Croquetas — 6,50 (gluten, lácteos)\n"
        "Ensalada — 7,00\n"
        "Principales:\n"
        "Paella — 14,00 (gluten, crustáceos, pescado)\n"
    )
    assert [c.title for c in menu] == ["Entrantes", "Principales"]
    assert [i.name for i in menu[0].items] == ["Croquetas", "Ensalada"]
    croquetas = menu[0].items[0]
    assert croquetas.price == "6,50"
    assert croquetas.price_display == "6,50 €"
    assert croquetas.allergens == (Allergen.GLUTEN, Allergen.LACTEOS)


def test_item_without_price_or_allergens() -> None:
    menu = parse_menu("Tapas:\nPan con tomate")
    item = menu[0].items[0]
    assert item.name == "Pan con tomate"
    assert item.price == ""
    assert item.allergens == ()
    assert item.price_display == ""


def test_items_before_a_category_fall_into_carta() -> None:
    menu = parse_menu("Café — 1,50\nTostada — 2,00")
    assert len(menu) == 1
    assert menu[0].title == "Carta"
    assert len(menu[0].items) == 2


def test_price_accepts_dot_and_euro_sign() -> None:
    menu = parse_menu("Bebidas:\nAgua | 1.20\nVino — 3 €")
    prices = [i.price for i in menu[0].items]
    assert prices == ["1.20", "3"]


def test_allergen_synonyms_normalise() -> None:
    assert normalize_allergens("trigo, leche, marisco") == (
        Allergen.GLUTEN, Allergen.LACTEOS, Allergen.CRUSTACEOS,
    )
    # Ruido y duplicados se descartan.
    assert normalize_allergens("gluten, gluten, xyz") == (Allergen.GLUTEN,)


def test_all_allergens_present_in_canonical_order() -> None:
    menu = parse_menu(
        "X:\nA — 1 (lácteos)\nB — 1 (gluten)\nC — 1 (gluten, huevos)"
    )
    present = all_allergens_present(menu)
    # Orden canónico del enum (gluten antes que huevos antes que lácteos).
    assert present == (Allergen.GLUTEN, Allergen.HUEVOS, Allergen.LACTEOS)


def test_empty_menu_is_falsy() -> None:
    assert parse_menu("") == ()
    assert parse_menu("   \n  ") == ()


def _resto(**extra: object) -> BusinessProfile:
    data = {
        "name": "Bar La Plaza", "city": "Sagunto", "phone": "961234567",
        "sector": "restaurante", "services": "Tapas\nMenú",
    }
    data.update(extra)  # type: ignore[arg-type]
    return BusinessProfile.from_form(data)  # type: ignore[arg-type]


def test_menu_renders_structured_when_present() -> None:
    biz = _resto(menu="Entrantes:\nCroquetas — 6,50 (gluten, lácteos)")
    html = build_landing(biz, use_live=False)
    assert 'class="menu"' in html
    assert "Croquetas" in html
    assert "6,50 €" in html
    # Badge y leyenda de alérgenos.
    assert "GLU" in html and "LAC" in html
    assert "1169/2011" in html


def test_without_menu_falls_back_to_service_list() -> None:
    biz = _resto()  # sin carta estructurada
    html = build_landing(biz, use_live=False)
    assert 'class="menu"' not in html
    assert 'class="carta"' in html  # la lista de servicios de la familia


def test_menu_emits_schema_org_menu() -> None:
    biz = _resto(menu="Principales:\nPaella — 14,00 (gluten)")
    jsonld = local_business_jsonld(biz)
    assert '"hasMenu"' in jsonld
    assert '"MenuSection"' in jsonld
    assert '"MenuItem"' in jsonld
    assert '"priceCurrency": "EUR"' in jsonld
    assert '"price": "14.00"' in jsonld  # coma española → punto para schema.org
