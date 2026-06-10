"""``faro-publish``: publica la web del negocio en una URL persistente.

A diferencia de ``faro-demo`` (túnel efímero para la puerta), esto deja la web
online de verdad en ``https://<negocio>.pages.dev`` (Cloudflare Pages, free tier),
para entregar tras cerrar la venta y luego apuntar ahí el dominio del cliente.

    faro-publish output/casa-paco-ab12cd      # carpeta con index.html o pack.zip
    faro-publish casa-paco                     # negocio del censo / sector

Requiere Node (npx) y una cuenta de Cloudflare autenticada UNA vez por el
principal (``npx wrangler login`` o la variable ``CLOUDFLARE_API_TOKEN``). El
comando NO crea la cuenta ni gasta dinero por sí solo: si no hay sesión, explica
qué hacer y sale sin publicar.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"
_PAGES_URL_RE = re.compile(r"https://[a-z0-9.-]+\.pages\.dev\S*")


class PublishError(RuntimeError):
    """No se pudo preparar o ejecutar la publicación."""


def project_name(slug: str) -> str:
    """Nombre de proyecto Cloudflare Pages válido: minúsculas, alfanumérico, guiones."""
    ascii_slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    cleaned = re.sub(r"[^a-z0-9-]+", "-", ascii_slug.lower()).strip("-")
    base = cleaned[:54] or "negocio"  # margen sobre el límite de 58 de Cloudflare
    return f"faro-{base}"


def _index_from_zip(zip_path: Path, dest: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        if "index.html" not in archive.namelist():
            raise PublishError(f"{zip_path} no contiene index.html")
        (dest / "index.html").write_bytes(archive.read("index.html"))


def _latest_output_dir(slug: str) -> Path | None:
    """Carpeta de salida más reciente cuyo nombre empieza por el slug."""
    if not _OUTPUT_DIR.exists():
        return None
    matches = sorted(
        (p for p in _OUTPUT_DIR.glob(f"{slug}*") if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def _generate_index(slug: str, dest: Path) -> None:
    """Genera index.html desde el censo o el sector (stub para demo persistente)."""
    from faro.business import BusinessProfile
    from faro.pack import build_pack
    from faro.server import _demo_form_for

    form = _demo_form_for(slug)
    if form is None:
        raise PublishError(
            f"'{slug}' no es una carpeta de salida, ni un pack.zip, ni un negocio "
            "del censo, ni un sector válido."
        )
    business = BusinessProfile.from_form(form)
    pack = build_pack(business, use_live=False)
    (dest / "index.html").write_text(pack.landing_html, encoding="utf-8")


def stage_site(target: str, dest: Path) -> str:
    """Deja un ``index.html`` listo en ``dest`` y devuelve el slug para el proyecto.

    ``target`` puede ser una carpeta con index.html, un pack.zip, una carpeta de
    salida de Faro, o un slug del censo / nombre de sector.
    """
    path = Path(target)
    if path.is_dir() and (path / "index.html").exists():
        shutil.copyfile(path / "index.html", dest / "index.html")
        return path.name
    if path.is_file() and path.suffix == ".zip":
        _index_from_zip(path, dest)
        return path.stem
    found = _latest_output_dir(target)
    if found is not None and (found / "pack.zip").exists():
        _index_from_zip(found / "pack.zip", dest)
        return target
    _generate_index(target, dest)
    return target


def _npx() -> str:
    npx = shutil.which("npx")
    if npx is None:
        raise PublishError(
            "Node no encontrado (falta 'npx'). Instala Node.js desde "
            "https://nodejs.org y reintenta."
        )
    return npx


def _is_authenticated(npx: str) -> bool:
    try:
        result = subprocess.run(
            [npx, "--yes", "wrangler@latest", "whoami"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0 and "not authenticated" not in result.stdout.lower()


def _auth_instructions() -> str:
    return (
        "Cloudflare no está autenticado. Una sola vez, el principal debe:\n"
        "  1) crear/abrir una cuenta gratis en https://dash.cloudflare.com (sin tarjeta), y\n"
        "  2) ejecutar:  npx wrangler login\n"
        "     (o exportar CLOUDFLARE_API_TOKEN con permiso 'Cloudflare Pages: Edit').\n"
        "Después, 'faro-publish' funciona sin más intervención."
    )


def _deploy(npx: str, site_dir: Path, name: str) -> str:
    proc = subprocess.run(
        [
            npx,
            "--yes",
            "wrangler@latest",
            "pages",
            "deploy",
            str(site_dir),
            "--project-name",
            name,
            "--commit-dirty=true",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        raise PublishError(f"wrangler falló:\n{output.strip()}")
    match = _PAGES_URL_RE.search(output)
    if match is None:
        raise PublishError(f"Deploy hecho pero sin URL en la salida:\n{output.strip()}")
    return match.group(0)


def publish(target: str, *, dry_run: bool = False) -> str:
    """Publica ``target`` en Cloudflare Pages y devuelve la URL pública.

    Con ``dry_run`` prepara el sitio y valida la sesión pero no despliega:
    devuelve la URL que TENDRÍA el proyecto. Útil para probar sin gastar.
    """
    npx = _npx()
    with tempfile.TemporaryDirectory(prefix="faro-publish-") as tmp:
        site_dir = Path(tmp)
        slug = stage_site(target, site_dir)
        name = project_name(slug)
        if dry_run:
            return f"https://{name}.pages.dev"
        if not _is_authenticated(npx):
            raise PublishError(_auth_instructions())
        return _deploy(npx, site_dir, name)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="faro-publish",
        description="Publica la web del negocio en una URL persistente (Cloudflare Pages).",
    )
    parser.add_argument(
        "target",
        help="Carpeta con index.html, pack.zip, carpeta de salida, slug del censo o sector.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepara y valida sin desplegar; muestra la URL que tendría.",
    )
    args = parser.parse_args(argv)
    try:
        url = publish(args.target, dry_run=args.dry_run)
    except PublishError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    prefix = "URL (dry-run): " if args.dry_run else "Publicado en: "
    print(prefix + url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
