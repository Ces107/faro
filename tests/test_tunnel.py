"""Túnel público: localización del binario, parseo de la URL y limpieza."""

from __future__ import annotations

import queue
from pathlib import Path

import pytest

from faro import tunnel


def test_trycloudflare_regex_extracts_url() -> None:
    line = "2024-... INF |  https://blue-green-fox-12.trycloudflare.com  |"
    match = tunnel._TRYCLOUDFLARE_RE.search(line)
    assert match is not None
    assert match.group(0) == "https://blue-green-fox-12.trycloudflare.com"


def test_binary_name_matches_platform() -> None:
    name = tunnel._binary_name()
    assert name in {"cloudflared", "cloudflared.exe"}


def test_platform_key_known_pair_has_download_url() -> None:
    key = tunnel._platform_key()
    # La plataforma de CI (Linux/Windows amd64) siempre tiene descarga directa.
    if key[0] in {"windows", "linux"}:
        assert key in tunnel._DOWNLOAD_URLS


def test_cloudflared_path_raises_without_download(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(tunnel, "_which", lambda _name: None)
    monkeypatch.setattr(tunnel, "_BIN_DIR", tmp_path)
    with pytest.raises(tunnel.TunnelError):
        tunnel.cloudflared_path(auto_download=False)


def test_await_url_returns_queued_url() -> None:
    found: queue.Queue[str] = queue.Queue()
    found.put("https://x.trycloudflare.com")

    class _Proc:
        def poll(self) -> int | None:
            return None

    url = tunnel._await_url(_Proc(), found, [], timeout=2.0)  # type: ignore[arg-type]
    assert url == "https://x.trycloudflare.com"


def test_await_url_raises_when_process_dies() -> None:
    found: queue.Queue[str] = queue.Queue()

    class _DeadProc:
        def poll(self) -> int:
            return 1

    with pytest.raises(tunnel.TunnelError) as exc:
        tunnel._await_url(_DeadProc(), found, ["boom\n"], timeout=2.0)  # type: ignore[arg-type]
    assert "boom" in str(exc.value)


def test_tunnel_close_terminates_running_process() -> None:
    calls: list[str] = []

    class _Proc:
        def poll(self) -> int | None:
            return None

        def terminate(self) -> None:
            calls.append("terminate")

        def wait(self, timeout: float | None = None) -> int:
            return 0

        def kill(self) -> None:
            calls.append("kill")

    tunnel.Tunnel(url="https://x.trycloudflare.com", _process=_Proc()).close()  # type: ignore[arg-type]
    assert calls == ["terminate"]
