"""Galería antes/después: parsing, gate de consentimiento RGPD y render."""

from __future__ import annotations

from faro.business import BusinessProfile
from faro.landing import build_landing


def _estetica(**extra: object) -> BusinessProfile:
    data = {
        "name": "Estética Bella", "city": "Sagunto", "phone": "961234567",
        "sector": "estetica", "services": "Tratamientos faciales\nDepilación",
    }
    data.update(extra)  # type: ignore[arg-type]
    return BusinessProfile.from_form(data)  # type: ignore[arg-type]


_PAIR = "https://x.com/a.jpg | https://x.com/b.jpg | Blanqueamiento"


def test_consent_required_to_keep_gallery() -> None:
    """Sin consentimiento (RGPD) la galería se descarta, aunque haya pares."""
    biz = _estetica(before_after=_PAIR)  # sin before_after_consent
    assert biz.before_after == ()


def test_consent_yes_keeps_pairs() -> None:
    biz = _estetica(before_after=_PAIR, before_after_consent="Sí")
    assert len(biz.before_after) == 1
    pair = biz.before_after[0]
    assert pair.before == "https://x.com/a.jpg"
    assert pair.after == "https://x.com/b.jpg"
    assert pair.caption == "Blanqueamiento"


def test_pair_needs_two_http_urls() -> None:
    """Una línea sin dos URLs http válidas se descarta (no inventa imágenes)."""
    biz = _estetica(
        before_after="solo-texto | tampoco-url\nhttps://x.com/a.jpg | https://x.com/b.jpg",
        before_after_consent="si",
    )
    assert len(biz.before_after) == 1


def test_gallery_renders_with_labels_and_consent() -> None:
    biz = _estetica(before_after=_PAIR, before_after_consent="Sí")
    html = build_landing(biz, use_live=False)
    assert 'id="antes-despues"' in html
    assert "Antes" in html and "Después" in html
    assert "https://x.com/a.jpg" in html
    assert "Antes y después" in html  # ancla del nav


def test_no_gallery_without_consent_in_render() -> None:
    biz = _estetica(before_after=_PAIR)  # sin consent
    html = build_landing(biz, use_live=False)
    assert 'id="antes-despues"' not in html


def test_gallery_capped_at_six() -> None:
    lines = "\n".join(
        f"https://x.com/{i}a.jpg | https://x.com/{i}b.jpg" for i in range(10)
    )
    biz = _estetica(before_after=lines, before_after_consent="yes")
    assert len(biz.before_after) == 6
