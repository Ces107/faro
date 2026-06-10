"""``faro-demo``: página del QR y dibujo en terminal a prueba de codificación."""

from __future__ import annotations

import io

import segno

from faro import livedemo


def test_qr_page_embeds_qr_and_url() -> None:
    html = livedemo._qr_page_html("https://abc.trycloudflare.com/d/bar", "bar")
    assert "data:image/svg" in html  # el QR va incrustado, sin red
    assert "abc.trycloudflare.com/d/bar" in html
    assert "4G/5G" in html  # el aviso de red que evita el fallo de WiFi de oficina
    html.encode("utf-8")  # no lanza


def test_demo_path_fullscreen_for_business_root_otherwise() -> None:
    assert livedemo._demo_path("casa-paco") == "/d/casa-paco"
    assert livedemo._demo_path(None) == "/"


def test_terminal_qr_never_crashes_on_cp1252(monkeypatch) -> None:
    # Reproduce la consola de Windows: stdout que NO admite bloques Unicode.
    class _Cp1252Out:
        encoding = "cp1252"

        def write(self, text: str) -> int:
            text.encode("cp1252")  # lanza UnicodeEncodeError igual que la consola real
            return len(text)

        def flush(self) -> None:
            pass

    monkeypatch.setattr("sys.stdout", _Cp1252Out())
    # No debe propagar la excepción: el QR del navegador cubre la demo.
    livedemo._print_terminal_qr(segno.make("https://x.trycloudflare.com/d/bar"))


def test_terminal_qr_renders_on_utf8() -> None:
    out = io.StringIO()  # admite Unicode: el QR se dibuja sin error
    out.reconfigure = lambda **_kw: None  # type: ignore[attr-defined]
    import sys

    sys.stdout, prev = out, sys.stdout
    try:
        livedemo._print_terminal_qr(segno.make("https://x.trycloudflare.com/d/bar"))
    finally:
        sys.stdout = prev
    assert len(out.getvalue()) > 0
