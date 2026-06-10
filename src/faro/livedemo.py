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
import time
import urllib.error
import urllib.request
import webbrowser

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


def _print_qr(url: str, target: str | None) -> None:
    qr = segno.make(url, error="m")
    print()
    print(f"  Demo lista{f' — {target}' if target else ''}:")
    print(f"  {url}")
    print()
    qr.terminal(compact=True, border=2)
    print()
    print("  El cliente escanea el QR con la cámara del móvil → ve su web.")
    print("  Ctrl+C para cerrar la demo.")
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
                webbrowser.open(demo_url)
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
