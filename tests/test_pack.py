"""Tests del renderizado de la landing y del empaquetado del pack."""

from __future__ import annotations

import io
import zipfile

from presencia_local.business import BusinessProfile, Sector
from presencia_local.landing import build_landing
from presencia_local.pack import build_pack, to_zip


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
            "LEEME.txt",
        }
        assert "Clínica Dental Sonríe" in zf.read("index.html").decode("utf-8")
        assert "<svg" in zf.read("resenas-qr.svg").decode("utf-8")
        assert "Google Business" in zf.read("google-business.md").decode("utf-8")


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
