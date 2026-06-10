"""Publicación a URL persistente: staging del sitio, nombre de proyecto, auth."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from faro import publish


def test_project_name_sanitizes_accents_and_symbols() -> None:
    assert publish.project_name("Casa Pacó S.L.") == "faro-casa-paco-s-l"
    assert publish.project_name("") == "faro-negocio"


def test_stage_site_from_directory(tmp_path: Path) -> None:
    src = tmp_path / "casa-paco"
    src.mkdir()
    (src / "index.html").write_text("<html>hola</html>", encoding="utf-8")
    dest = tmp_path / "out"
    dest.mkdir()
    slug = publish.stage_site(str(src), dest)
    assert slug == "casa-paco"
    assert (dest / "index.html").read_text(encoding="utf-8") == "<html>hola</html>"


def test_stage_site_from_zip(tmp_path: Path) -> None:
    zip_path = tmp_path / "pack.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("index.html", "<html>pack</html>")
    dest = tmp_path / "out"
    dest.mkdir()
    slug = publish.stage_site(str(zip_path), dest)
    assert slug == "pack"
    assert "pack" in (dest / "index.html").read_text(encoding="utf-8")


def test_stage_site_from_sector_generates_index(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    slug = publish.stage_site("bar", dest)
    assert slug == "bar"
    assert (dest / "index.html").read_text(encoding="utf-8").lower().count("<html") == 1


def test_stage_site_unknown_target_raises(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    with pytest.raises(publish.PublishError):
        publish.stage_site("ni-carpeta-ni-sector-xyz", dest)


def test_publish_dry_run_returns_url_without_deploy(monkeypatch) -> None:
    monkeypatch.setattr(publish, "_npx", lambda: "npx")
    # _is_authenticated y _deploy NO deben llamarse en dry-run.
    monkeypatch.setattr(
        publish, "_is_authenticated", lambda _n: pytest.fail("no auth en dry-run")
    )
    assert publish.publish("bar", dry_run=True) == "https://faro-bar.pages.dev"


def test_publish_without_auth_raises_with_instructions(monkeypatch) -> None:
    monkeypatch.setattr(publish, "_npx", lambda: "npx")
    monkeypatch.setattr(publish, "_is_authenticated", lambda _n: False)
    with pytest.raises(publish.PublishError) as exc:
        publish.publish("bar")
    assert "wrangler login" in str(exc.value)


def test_publish_deploys_when_authenticated(monkeypatch) -> None:
    monkeypatch.setattr(publish, "_npx", lambda: "npx")
    monkeypatch.setattr(publish, "_is_authenticated", lambda _n: True)
    captured: dict[str, str] = {}

    def _fake_deploy(npx: str, site_dir: Path, name: str) -> str:
        captured["name"] = name
        assert (site_dir / "index.html").exists()
        return f"https://{name}.pages.dev/abc123"

    monkeypatch.setattr(publish, "_deploy", _fake_deploy)
    url = publish.publish("bar")
    assert captured["name"] == "faro-bar"
    assert url.startswith("https://faro-bar.pages.dev")
