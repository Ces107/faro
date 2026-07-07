"""Funcionalidades de conversión nuevas: rating real, oferta, reserva, SEO rico.

Disciplina de honestidad: nada se inventa; un campo vacío no pinta su bloque.
"""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.seo import faq_jsonld, local_business_jsonld


def _biz(**kw: object) -> BusinessProfile:
    base: dict[str, object] = {
        "name": "Negocio", "sector": Sector.DENTAL, "city": "Sagunto",
        "phone": "961112233", "services": ("Limpieza", "Implantes"),
    }
    base.update(kw)
    return BusinessProfile(**base)  # type: ignore[arg-type]


def test_rating_parses_and_clamps() -> None:
    assert _biz(google_rating="4.8").rating == 4.8
    assert _biz(google_rating="4,8").rating == 4.8  # coma decimal española
    assert _biz(google_rating="9").rating is None  # fuera de rango
    assert _biz(google_rating="").rating is None
    assert _biz(google_rating="4.8").rating_stars == "★★★★★"
    assert _biz(google_rating="3").rating_stars == "★★★☆☆"


def test_aggregate_rating_only_when_real() -> None:
    with_rating = local_business_jsonld(_biz(google_rating="4.8", google_reviews_count="120"))
    assert "aggregateRating" in with_rating and "4.8" in with_rating
    # Sin nº de reseñas no se emite el aggregateRating (dato a medias = no se afirma).
    assert "aggregateRating" not in local_business_jsonld(_biz(google_rating="4.8"))
    assert "aggregateRating" not in local_business_jsonld(_biz())


def test_faq_jsonld_shape() -> None:
    assert faq_jsonld([]) == ""
    js = faq_jsonld([("¿Abrís sábados?", "Sí, por la mañana.")])
    assert '"@type": "FAQPage"' in js and "¿Abrís sábados?" in js


def test_offer_block_present_and_dated() -> None:
    html = build_landing(
        _biz(offer_title="Revisión gratis", offer_end_date="2026-07-31"), use_live=False
    )
    assert 'id="offerBar"' in html
    assert "Revisión gratis" in html
    assert 'data-end="2026-07-31"' in html
    # Sin oferta, no hay barra (el id del elemento; la clase CSS siempre está en el <style>).
    assert 'id="offerBar"' not in build_landing(_biz(), use_live=False)


def test_booking_and_delivery_render() -> None:
    html = build_landing(_biz(booking_url="https://doctoralia.es/x"), use_live=False)
    assert "doctoralia.es/x" in html
    food = build_landing(
        BusinessProfile(name="Bar", sector=Sector.BAR, city="Sagunto", phone="961112233",
                        services=("Tapas",), delivery_links=("https://glovoapp.com/x",)),
        use_live=False,
    )
    assert "glovoapp.com/x" in food and "domicilio" in food


def test_credentials_and_service_area_render() -> None:
    html = build_landing(
        _biz(credentials=("Colegiado nº 1234",), service_area="Sagunto, Canet"), use_live=False
    )
    assert "Colegiado nº 1234" in html
    assert "Sagunto, Canet" in html


def test_nothing_invented_when_empty() -> None:
    """Sin datos de conversión, ninguno de sus marcadores aparece."""
    html = build_landing(_biz(), use_live=False)
    markers = (
        'id="offerBar"', "aggregateRating", 'class="rating"', 'class="creds"', 'class="delivery"',
    )
    for marker in markers:
        assert marker not in html, marker


def test_contact_form_always_renders_with_whatsapp_fallback() -> None:
    """El formulario de contacto sale siempre y trae el WhatsApp de respaldo."""
    html = build_landing(_biz(whatsapp="620000000"), use_live=False)
    assert 'id="contactForm"' in html
    for field in ('name="name"', 'name="email"', 'name="phone"', 'name="message"'):
        assert field in html, field
    # Respaldo estático: el WhatsApp va en data-wa; sin endpoint dinámico por defecto.
    assert "data-wa=" in html
    assert 'data-endpoint="' not in html  # el atributo no se emite (la JS sí menciona la cadena)
    # Contacto está en la navegación.
    assert 'href="#contacto"' in html


def test_contact_form_wires_dynamic_endpoint_when_set() -> None:
    """Con contact_endpoint (tier dinámico), el formulario apunta a faro-backend."""
    url = "https://saguntweb.com/api/v1/negocio/contact"
    html = build_landing(_biz(contact_endpoint=url), use_live=False)
    assert f'data-endpoint="{url}"' in html
    # El respaldo de WhatsApp sigue presente para no perder el lead si el backend cae.
    assert "data-wa=" in html


def test_contact_form_required_fields_marked() -> None:
    html = build_landing(_biz(), use_live=False)
    # nombre, email y mensaje son obligatorios; teléfono no.
    assert html.count("required") >= 3
