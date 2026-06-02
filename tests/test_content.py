"""Tests de los generadores de contenido (copy, GMB, WhatsApp, reseñas, QR)."""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.content import generate_copy, scripted_copy
from faro.gmb import build_gmb
from faro.qr import qr_data_uri, qr_svg, review_qr, whatsapp_qr
from faro.reviews import review_replies, review_url
from faro.whatsapp import default_message, whatsapp_link


def _biz(**ov: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica Dental Sonríe",
        "sector": Sector.DENTAL,
        "city": "Puerto de Sagunto",
        "phone": "961234567",
        "services": ("Limpiezas", "Implantes", "Ortodoncia"),
        "highlights": ("20 años de experiencia",),
    }
    data.update(ov)
    return BusinessProfile(**data)  # type: ignore[arg-type]


def test_scripted_copy_is_complete() -> None:
    copy = scripted_copy(_biz())
    assert copy.slogan
    assert copy.hero_subtitle
    assert copy.about_text
    assert len(copy.value_props) == 3
    # Cada propuesta de valor tiene un título distinto (sin duplicar "Lo que nos diferencia").
    titles = [p.title for p in copy.value_props]
    assert len(set(titles)) == len(titles)


def test_generate_copy_scripted_when_no_live() -> None:
    copy = generate_copy(_biz(), use_live=False)
    assert "Puerto de Sagunto" in copy.hero_subtitle


def test_parse_live_valid_payload() -> None:
    from faro.content import _parse_live

    payload = (
        '{"slogan":"Tu sonrisa","hero_subtitle":"Dental en Sagunto",'
        '"about_title":"Sobre","about_text":"Texto.","services_intro":"Servicios",'
        '"value_props":[{"title":"A","description":"uno"},{"title":"B","description":"dos"},'
        '{"title":"C","description":"tres"}]}'
    )
    copy = _parse_live(payload, scripted_copy(_biz()))
    assert copy.slogan == "Tu sonrisa"
    assert len(copy.value_props) == 3


def test_parse_live_clamps_long_fields() -> None:
    from faro.content import _parse_live

    payload = (
        '{"slogan":"' + "x" * 500 + '","hero_subtitle":"h","about_title":"t",'
        '"about_text":"a","services_intro":"s",'
        '"value_props":[{"title":"A","description":"d"}]}'
    )
    copy = _parse_live(payload, scripted_copy(_biz()))
    assert len(copy.slogan) <= 90  # campo recortado, no rompe el diseño


def test_parse_live_invalid_falls_back() -> None:
    from faro.content import _parse_live

    fallback = scripted_copy(_biz())
    assert _parse_live("no es json", fallback) is fallback
    assert _parse_live('{"slogan":"x"}', fallback) is fallback  # faltan claves


def test_gmb_description_within_limit() -> None:
    gmb = build_gmb(_biz())
    assert len(gmb.description) <= 750
    assert gmb.categories == ("Dentista", "Clínica dental")
    assert len(gmb.posts) == 5
    assert gmb.services == ("Limpiezas", "Implantes", "Ortodoncia")


def test_whatsapp_link_has_message_and_number() -> None:
    biz = _biz()
    link = whatsapp_link(biz)
    assert link.startswith("https://wa.me/34961234567?text=")
    assert default_message(biz) != ""


def test_review_url_generated_when_missing() -> None:
    biz = _biz()
    url = review_url(biz)
    assert "google.com/maps/search" in url
    assert "Sagunto" in url


def test_review_url_uses_explicit_when_present() -> None:
    biz = _biz(google_review_url="https://g.page/r/abc/review")
    assert review_url(biz) == "https://g.page/r/abc/review"


def test_review_replies_present() -> None:
    replies = review_replies(_biz())
    assert replies.positive and replies.neutral and replies.negative


def test_qr_data_uri_and_svg() -> None:
    uri = qr_data_uri("https://example.com")
    assert uri.startswith("data:image/svg+xml")
    svg = qr_svg("https://example.com")
    assert "<svg" in svg
    assert whatsapp_qr(_biz()).startswith("data:image/svg+xml")
    assert review_qr(_biz()).startswith("data:image/svg+xml")
