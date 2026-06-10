"""Nº de registro sanitario + contador de visitas (gaps del buyer-review 2026-06-10).

Dos gaps cazados por la simulación de compra:
- Marta (clínica dental): la publicidad sanitaria debe llevar el nº de registro;
  la plantilla no lo pedía ni lo pintaba.
- Paco (bar) y Marta: "¿cuántos clientes me trae?" no tenía respuesta porque el
  pack no medía nada. GoatCounter (sin cookies, RGPD) es la pieza mínima.

Ambos campos son opcionales y degradan a vacío: un negocio que no los aporta
genera exactamente la misma web que antes.
"""

from __future__ import annotations

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.legal import legal_notice_html
from faro.seo import analytics_snippet


def _biz(**ov: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica Dental Sonríe",
        "sector": Sector.DENTAL,
        "city": "Puerto de Sagunto",
        "phone": "961234567",
        "services": ("Limpiezas",),
        "address": "Av. del Mediterráneo 12",
    }
    data.update(ov)
    return BusinessProfile(**data)  # type: ignore[arg-type]


# --- Nº de registro sanitario ------------------------------------------------


def test_registration_number_defaults_empty_and_truncates() -> None:
    assert _biz().registration_number == ""
    assert _biz(registration_number=" R.S. 12.345/V ").registration_number == "R.S. 12.345/V"
    assert len(_biz(registration_number="X" * 200).registration_number) == 80


def test_legal_notice_carries_registration_when_present() -> None:
    notice = legal_notice_html(_biz(registration_number="R.S. 12.345/V"))
    assert "Nº de registro sanitario: R.S. 12.345/V" in notice
    # Sin él, no aparece la línea.
    assert "registro sanitario" not in legal_notice_html(_biz())


def test_legal_notice_escapes_registration() -> None:
    notice = legal_notice_html(_biz(registration_number="<b>x</b>"))
    assert "<b>x</b>" not in notice
    assert "&lt;b&gt;" in notice


def test_landing_footer_shows_registration() -> None:
    html = build_landing(_biz(registration_number="R.S. 12.345/V"), use_live=False)
    assert "Nº de registro sanitario: R.S. 12.345/V" in html
    assert "registro sanitario" not in build_landing(_biz(), use_live=False)


def test_registration_number_flows_from_form() -> None:
    biz = BusinessProfile.from_form({
        "name": "Clínica X", "city": "Sagunto", "phone": "961234567",
        "sector": "dental", "services": "Limpieza",
        "registration_number": "R.S. 999/V",
    })
    assert biz.registration_number == "R.S. 999/V"


# --- Contador de visitas (GoatCounter) ---------------------------------------


def test_goatcounter_accepts_bare_code() -> None:
    assert _biz(analytics_goatcounter="mibar").analytics_goatcounter == "mibar"
    assert _biz(analytics_goatcounter=" MiBar ").analytics_goatcounter == "mibar"


def test_goatcounter_extracts_code_from_full_url() -> None:
    biz = _biz(analytics_goatcounter="https://mibar.goatcounter.com/count")
    assert biz.analytics_goatcounter == "mibar"


def test_goatcounter_rejects_invalid_code() -> None:
    # Inyección / charset fuera de [a-z0-9-] → se descarta (degrada a vacío).
    assert _biz(analytics_goatcounter='x"></script><script>alert(1)').analytics_goatcounter == ""
    assert _biz(analytics_goatcounter="otro.dominio.com/count").analytics_goatcounter == ""


def test_analytics_snippet_renders_endpoint_when_set() -> None:
    snippet = analytics_snippet(_biz(analytics_goatcounter="mibar"))
    assert 'data-goatcounter="https://mibar.goatcounter.com/count"' in snippet
    assert "gc.zgo.at/count.js" in snippet
    # Sin código, no inyecta nada.
    assert analytics_snippet(_biz()) == ""


def test_landing_injects_analytics_only_when_set() -> None:
    with_code = build_landing(_biz(analytics_goatcounter="mibar"), use_live=False)
    assert "gc.zgo.at/count.js" in with_code
    assert "gc.zgo.at" not in build_landing(_biz(), use_live=False)


def test_legal_notice_discloses_analytics_when_set() -> None:
    notice = legal_notice_html(_biz(analytics_goatcounter="mibar"))
    assert "GoatCounter" in notice
    assert "sin" in notice and "cookies" in notice
    # La promesa "sin cookies de seguimiento" sigue siendo cierta.
    assert "no usa cookies propias de seguimiento" in notice
    assert "GoatCounter" not in legal_notice_html(_biz())
