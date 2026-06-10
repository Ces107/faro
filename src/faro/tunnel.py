"""Túnel público efímero para la demo en vivo (Cloudflare Quick Tunnel).

Expone el servidor local de Faro en una URL ``https://<algo>.trycloudflare.com``
sin cuenta ni configuración: el cliente escanea un QR y ve SU web en SU móvil,
en la puerta. La URL vive mientras el túnel esté abierto (es para la demo, no
para entregar; para una URL persistente se publica el pack con ``faro-publish``).

El binario ``cloudflared`` se localiza en el PATH o en ``tools/bin/``; si no está,
se descarga una vez (igual que ``iniciar-faro.bat`` prepara el venv la primera vez).
"""

from __future__ import annotations

import os
import platform
import queue
import re
import subprocess
import threading
import time
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BIN_DIR = _REPO_ROOT / "tools" / "bin"
_TRYCLOUDFLARE_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
_URL_TIMEOUT_SECONDS = 30.0

# Descarga oficial del binario (un solo fichero, sin instalador).
_DOWNLOAD_URLS = {
    ("windows", "amd64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
    ("windows", "arm64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-arm64.exe",
    ("linux", "amd64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
    ("linux", "arm64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64",
    ("darwin", "amd64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz",
    ("darwin", "arm64"): "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz",
}


class TunnelError(RuntimeError):
    """No se pudo abrir el túnel (binario ausente, descarga fallida o sin URL)."""


def _platform_key() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "arm64" if machine in {"arm64", "aarch64"} else "amd64"
    return system, arch


def _binary_name() -> str:
    return "cloudflared.exe" if _platform_key()[0] == "windows" else "cloudflared"


def _which(name: str) -> Path | None:
    """``cloudflared`` en el PATH, si está instalado a mano."""
    from shutil import which

    found = which(name)
    return Path(found) if found else None


def download_cloudflared(dest: Path | None = None) -> Path:
    """Descarga el binario de cloudflared para esta plataforma a ``tools/bin/``.

    Solo Windows y Linux se descargan como ejecutable directo; en macOS el
    release es un .tgz y se pide instalación manual (``brew install cloudflared``)
    para no implementar des-empaquetado por un caso que aquí no aplica.
    """
    key = _platform_key()
    url = _DOWNLOAD_URLS.get(key)
    if url is None or url.endswith(".tgz"):
        raise TunnelError(
            f"Sin descarga automática para {key}. Instala cloudflared a mano "
            "(https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)."
        )
    target = dest or (_BIN_DIR / _binary_name())
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, target)  # noqa: S310 (URL fija de GitHub releases)
    if key[0] != "windows":
        target.chmod(0o755)
    return target


def cloudflared_path(*, auto_download: bool = True) -> Path:
    """Localiza cloudflared (PATH → tools/bin → descarga). Lanza si no hay forma."""
    in_path = _which(_binary_name())
    if in_path is not None:
        return in_path
    local = _BIN_DIR / _binary_name()
    if local.exists():
        return local
    if auto_download:
        return download_cloudflared(local)
    raise TunnelError("cloudflared no encontrado y descarga desactivada.")


def _read_url_from_stream(
    stream: object, found: queue.Queue[str], sink: list[str]
) -> None:
    """Lee líneas del proceso buscando la URL pública; conserva el log para errores."""
    for raw in iter(stream.readline, ""):  # type: ignore[attr-defined]
        sink.append(raw)
        match = _TRYCLOUDFLARE_RE.search(raw)
        if match:
            found.put(match.group(0))


@dataclass
class Tunnel:
    """Un túnel abierto: la URL pública y el proceso que lo mantiene vivo."""

    url: str
    _process: subprocess.Popen[str]

    def close(self) -> None:
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()


@contextmanager
def open_tunnel(
    port: int, *, auto_download: bool = True, timeout: float = _URL_TIMEOUT_SECONDS
) -> Iterator[Tunnel]:
    """Abre un Quick Tunnel a ``127.0.0.1:<port>`` y cede la URL pública.

    El túnel se cierra al salir del ``with`` aunque haya excepción.
    """
    binary = cloudflared_path(auto_download=auto_download)
    process = subprocess.Popen(
        [
            str(binary),
            "tunnel",
            "--url",
            f"http://127.0.0.1:{port}",
            "--no-autoupdate",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "TUNNEL_METRICS": ""},
    )
    found: queue.Queue[str] = queue.Queue(maxsize=1)
    log: list[str] = []
    reader = threading.Thread(
        target=_read_url_from_stream, args=(process.stdout, found, log), daemon=True
    )
    reader.start()
    try:
        url = _await_url(process, found, log, timeout)
        tunnel = Tunnel(url=url, _process=process)
        try:
            yield tunnel
        finally:
            tunnel.close()
    except BaseException:
        if process.poll() is None:
            process.terminate()
        raise


def _await_url(
    process: subprocess.Popen[str],
    found: queue.Queue[str],
    log: list[str],
    timeout: float,
) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            return found.get(timeout=0.25)
        except queue.Empty:
            if process.poll() is not None:
                break
    tail = "".join(log[-15:]).strip()
    raise TunnelError(
        "cloudflared no devolvió una URL pública a tiempo.\n"
        f"Últimas líneas:\n{tail or '(sin salida)'}"
    )
