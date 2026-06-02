"""Tests del contenido por sección/sector (playbook, sections, icons) y render premium."""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.icons import get_icon, has_icon
from faro.landing import build_landing
from faro.playbook import _PLAYBOOK, playbook_for
from faro.sections import build_faq, build_service_cards, build_stats


def _biz(**ov: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica X",
        "sector": Sector.DENTAL,
        "city": "Sagunto",
        "phone": "961234567",
        "services": ("Limpieza dental", "Implantes"),
        "address": "Calle Mayor 1",
    }
    data.update(ov)
    return BusinessProfile(**data)  # type: ignore[arg-type]


def test_every_sector_has_playbook() -> None:
    assert len(_PLAYBOOK) == len(list(Sector))
    for sector in Sector:
        pb = playbook_for(sector)
        assert pb.process and pb.faq
        assert pb.final_cta_headline and pb.gallery_title and pb.stat_fallback


def test_service_card_benefit_by_keyword() -> None:
    cards = build_service_cards(_biz(), playbook_for(Sector.DENTAL))
    assert any("sarro" in c.benefit for c in cards)  # "limpieza" -> beneficio específico
    assert all(c.icon for c in cards)


def test_service_card_generic_fallback() -> None:
    biz = _biz(services=("Servicio rarísimo zzz",))
    cards = build_service_cards(biz, playbook_for(Sector.DENTAL))
    assert cards[0].benefit  # cae al beneficio genérico, nunca vacío


def test_faq_fills_placeholders_and_drops_address_when_missing() -> None:
    pb = playbook_for(Sector.DENTAL)
    with_addr = build_faq(_biz(), pb)
    assert any("Calle Mayor 1" in q.answer for q in with_addr)
    assert all("{phone}" not in q.answer for q in with_addr)  # rellenado
    no_addr = build_faq(_biz(address=""), pb)
    assert len(no_addr) < len(with_addr)  # la pregunta de dirección se descarta


def test_stats_are_honest_and_at_least_three() -> None:
    stats = build_stats(_biz(services=("A", "B", "C")), playbook_for(Sector.DENTAL))
    assert len(stats) >= 3
    joined = " ".join(s.value + s.label for s in stats)
    assert "500" not in joined and "clientes" not in joined  # nunca inventa cifras


def test_icons_valid_and_fallback() -> None:
    assert has_icon("tooth")
    assert "<" in get_icon("tooth")
    assert get_icon("inexistente") == get_icon("pin")  # fallback limpio


def test_all_sectors_render_full_landing() -> None:
    for sector in Sector:
        html = build_landing(_biz(sector=sector), use_live=False)
        assert "Cómo trabajamos" in html
        assert "Preguntas frecuentes" in html
        assert "Lo que nos diferencia" in html


def test_optional_sections_appear_and_vanish() -> None:
    from faro.business import Testimonial

    plain = build_landing(_biz(), use_live=False)
    assert 'id="galeria"' not in plain
    assert 'id="opiniones"' not in plain

    rich = build_landing(
        _biz(photos=("https://x.test/a.jpg",), testimonials=(Testimonial("Genial", "Ana"),)),
        use_live=False,
    )
    assert 'id="galeria"' in rich
    assert 'id="opiniones"' in rich
    assert "Genial" in rich
