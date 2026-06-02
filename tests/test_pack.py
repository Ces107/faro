"""Tests del renderizado de la landing y del empaquetado del pack."""

from __future__ import annotations

import io
import zipfile

import pytest

from faro.business import BusinessProfile, Sector
from faro.landing import build_landing
from faro.pack import build_pack, to_zip


def _biz(**ov: object) -> BusinessProfile:
    data: dict[str, object] = {
        "name": "Clínica Dental Sonríe",
        "sector": Sector.DENTAL,
        "city": "Puerto de Sagunto",
        "phone": "961234567",
        "services": ("Limpiezas", "Implantes"),
        "hours": "L-V 9:00-20:00",
        "address": "Av. del Mediterráneo 12",
        "highlights": ("20 años de experiencia",),
    }
    data.update(ov)
    return BusinessProfile(**data)  # type: ignore[arg-type]


def test_landing_contains_key_pieces() -> None:
    html = build_landing(_biz(), use_live=False)
    assert "Clínica Dental Sonríe" in html
    assert "wa.me/34961234567" in html
    assert "data:image/svg+xml" in html  # QR incrustado
    assert "L-V 9:00-20:00" in html
    assert "Av. del Mediterráneo 12" in html


def test_landing_escapes_html() -> None:
    # Un nombre con HTML no debe romper la página (autoescape de Jinja2).
    html = build_landing(_biz(name="Bar <script>alert(1)</script>"), use_live=False)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_pack_zip_has_all_files() -> None:
    biz = _biz()
    pack = build_pack(biz, use_live=False)
    data = to_zip(pack, biz)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        assert names == {
            "index.html",
            "google-business.md",
            "tarjeta-resenas.html",
            "resenas-qr.svg",
            "whatsapp-qr.svg",
            "aviso-legal.html",
            "LEEME.txt",
        }
        assert "Clínica Dental Sonríe" in zf.read("index.html").decode("utf-8")
        legal = zf.read("aviso-legal.html").decode("utf-8")
        assert "Aviso legal" in legal
        assert "NIF" in legal
        assert "<svg" in zf.read("resenas-qr.svg").decode("utf-8")
        assert "Google Business" in zf.read("google-business.md").decode("utf-8")


def test_review_card_escapes_html() -> None:
    pack = build_pack(_biz(name="Bar <script>alert(1)</script> & Co"), use_live=False)
    assert "<script>alert(1)</script>" not in pack.review_card_html
    assert "&lt;script&gt;" in pack.review_card_html


def test_legal_notice_escapes_html() -> None:
    pack = build_pack(_biz(name="Bar <script>x</script>"), use_live=False)
    assert "<script>x</script>" not in pack.legal_html
    assert "&lt;script&gt;" in pack.legal_html


def test_readme_includes_operator_contact_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FARO_OPERATOR_NAME", "César")
    monkeypatch.setenv("FARO_OPERATOR_CONTACT", "600111222")
    biz = _biz()
    data = to_zip(build_pack(biz, use_live=False), biz)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        leeme = zf.read("LEEME.txt").decode("utf-8")
    assert "César" in leeme
    assert "600111222" in leeme


def test_pack_without_optional_fields() -> None:
    biz = BusinessProfile(
        name="Peluquería Ana",
        sector=Sector.PELUQUERIA,
        city="Canet",
        phone="600111222",
        services=("Corte",),
    )
    pack = build_pack(biz, use_live=False)
    assert "Peluquería Ana" in pack.landing_html
    # Sin horario ni dirección, la landing sigue siendo válida.
    assert to_zip(pack, biz)
