"""``faro-demo``: demo en vivo en el móvil del cliente, de un comando.

Arranca el servidor local, abre un túnel público efímero (Cloudflare Quick
Tunnel, sin cuenta) y muestra en la terminal un QR que el cliente escanea para
ver SU web en SU móvil, en la puerta. Al cerrar (Ctrl+C) se para todo.

    faro-demo                 # formulario en blanco, lo rellenas en vivo
    faro-demo casa-paco       # negocio del censo (faro-prospect), web directa
    faro-demo bar             # web de ejemplo del sector "bar"

La URL del túnel es temporal: vive mientras el comando esté abierto. Es para la
demo, no para entregar. Para una URL persistente que perdure, ``faro-publish``.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import segno

from faro.tunnel import TunnelError, open_tunnel

_SERVER_BOOT_TIMEOUT = 25.0


def _free_port() -> int:
    """Un puerto TCP libre que el SO nos asigna (evita choques con otra demo)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_server(port: int) -> subprocess.Popen[bytes]:
    """Arranca ``python -m faro.server`` en el puerto dado, en segundo plano."""
    env = {**os.environ, "FARO_HOST": "127.0.0.1", "FARO_PORT": str(port)}
    return subprocess.Popen(
        [sys.executable, "-m", "faro.server"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_until_up(port: int, timeout: float = _SERVER_BOOT_TIMEOUT) -> bool:
    """Espera a que el servidor responda en ``/api/sectors`` (señal de listo)."""
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/api/sectors"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):  # noqa: S310 (localhost)
                return True
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.3)
    return False


def _demo_path(target: str | None) -> str:
    """Ruta a abrir: web a pantalla completa si hay negocio, formulario si no."""
    return f"/d/{target}" if target else "/"


def _qr_page_html(url: str, target: str | None) -> str:
    """Página local con el QR grande y la URL, para enseñar al cliente."""
    data_uri = segno.make(url, error="m").svg_data_uri(scale=10, border=2)
    title = target or "Demo"
    return (
        "<!doctype html><html lang=es><head><meta charset=utf-8>"
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        f"<title>Faro - {title}</title><style>"
        "body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;text-align:center;"
        "padding:5vh 4vw;background:#0f172a;color:#f8fafc;margin:0}"
        ".card{background:#fff;color:#0f172a;display:inline-block;padding:28px 36px;"
        "border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,.4)}"
        "h1{font-size:1.25rem;margin:0 0 6px}.sub{color:#475569;margin:0 0 18px;font-size:.95rem}"
        "img{width:300px;height:300px;display:block;margin:0 auto}"
        ".u{font-size:.8rem;word-break:break-all;color:#64748b;margin-top:16px;max-width:320px}"
        ".tip{margin-top:22px;opacity:.75;font-size:.9rem}</style></head><body>"
        '<div class=card><h1>Escanea con la camara del movil</h1>'
        '<p class=sub>El cliente apunta la camara a este codigo</p>'
        f'<img src="{data_uri}" alt="QR"><div class=u>{url}</div></div>'
        "<p class=tip>Importante: el movil debe estar en datos (4G/5G), "
        "no en el WiFi de oficina.<br>"
        "Cierra la ventana de la terminal para terminar la demo.</p></body></html>"
    )


def _open_qr_page(url: str, target: str | None) -> None:
    """Escribe la página del QR a un fichero temporal y la abre en el navegador."""
    path = Path(tempfile.gettempdir()) / "faro-demo-qr.html"
    path.write_text(_qr_page_html(url, target), encoding="utf-8")
    webbrowser.open(path.as_uri())


def _print_terminal_qr(qr: segno.QRCode) -> None:
    """Dibuja el QR en la terminal sin reventar en consolas no-UTF8 (Windows cp1252)."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        qr.terminal(compact=True, border=2)
    except (UnicodeError, OSError, ValueError):
        # La consola no admite los bloques Unicode: el QR del navegador ya cubre la demo.
        print("  (El QR se ha abierto en el navegador.)")


def _print_qr(url: str, target: str | None) -> None:
    print()
    print(f"  Demo lista{f' ({target})' if target else ''}:")
    print(f"  {url}")
    print()
    _print_terminal_qr(segno.make(url, error="m"))
    print()
    print("  El cliente escanea el QR (camara del movil, en datos 4G/5G) y ve su web.")
    print("  Ctrl+C o cerrar esta ventana para terminar la demo.")
    print()


def run_demo(target: str | None, *, open_browser: bool = True) -> int:
    """Orquesta servidor + túnel + QR. Devuelve un código de salida de proceso."""
    port = _free_port()
    server = _start_server(port)
    try:
        if not _wait_until_up(port):
            print("No se pudo arrancar el servidor de Faro.", file=sys.stderr)
            return 1
        try:
            tunnel_cm = open_tunnel(port)
        except TunnelError as exc:
            print(f"No se pudo abrir el túnel: {exc}", file=sys.stderr)
            return 2
        with tunnel_cm as tunnel:
            demo_url = tunnel.url + _demo_path(target)
            _print_qr(demo_url, target)
            if open_browser:
                _open_qr_page(demo_url, target)
            _wait_for_interrupt()
        return 0
    finally:
        _stop(server)


def _wait_for_interrupt() -> None:
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Cerrando la demo…")


def _stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="faro-demo",
        description="Demo en vivo de Faro en el móvil del cliente (túnel + QR).",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Slug del negocio en el censo (faro-prospect) o nombre de un sector. "
        "Si se omite, abre el formulario en blanco.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="No abrir el navegador local automáticamente.",
    )
    args = parser.parse_args(argv)
    return run_demo(args.target, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
