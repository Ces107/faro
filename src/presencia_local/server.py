"""Servidor de la demo: formulario del negocio, vista previa de la landing y descarga del pack.

Corre en local sin cuentas de pago. El operador rellena los datos del negocio
delante del cliente, ve la web al momento y descarga el .zip listo para entregar.
"""

from __future__ import annotations

import secrets
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from presencia_local.business import BusinessProfile, Sector
from presencia_local.pack import DigitalPresencePack, build_pack, to_zip

_WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def _ascii_slug(text: str) -> str:
    """Slug ASCII para el nombre del fichero (las cabeceras HTTP no admiten Unicode)."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = "".join(c if c.isalnum() else "-" for c in normalized.lower())
    return "-".join(filter(None, slug.split("-")))[:40] or "negocio"


class GenerateRequest(BaseModel):
    name: str = ""
    sector: str = "otro"
    city: str = ""
    phone: str = ""
    whatsapp: str = ""
    services: str = ""
    hours: str = ""
    address: str = ""
    email: str = ""
    google_review_url: str = ""
    highlights: str = ""
    slogan: str = ""


def create_app(*, use_live: bool = True) -> FastAPI:
    app = FastAPI(title="Presencia Local", version="0.1.0")
    packs: dict[str, tuple[DigitalPresencePack, BusinessProfile]] = {}

    @app.get("/api/sectors")
    def sectors() -> dict[str, list[dict[str, str]]]:
        return {
            "sectors": [
                {"value": s.value, "label": s.value.capitalize()} for s in Sector
            ]
        }

    @app.post("/api/generate")
    def generate(req: GenerateRequest) -> JSONResponse:
        try:
            business = BusinessProfile.from_form(req.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        pack = build_pack(business, use_live=use_live)
        pack_id = secrets.token_hex(8)
        packs[pack_id] = (pack, business)
        return JSONResponse(
            {
                "pack_id": pack_id,
                "preview_url": f"/preview/{pack_id}",
                "download_url": f"/download/{pack_id}",
                "gmb": {
                    "description": pack.gmb.description,
                    "categories": list(pack.gmb.categories),
                    "posts": list(pack.gmb.posts),
                },
                "whatsapp_url": pack.whatsapp_url,
                "review_url": pack.review_url,
            }
        )

    @app.get("/preview/{pack_id}", response_class=HTMLResponse)
    def preview(pack_id: str) -> HTMLResponse:
        entry = packs.get(pack_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Pack no encontrado")
        return HTMLResponse(entry[0].landing_html)

    @app.get("/download/{pack_id}")
    def download(pack_id: str) -> Response:
        entry = packs.get(pack_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Pack no encontrado")
        pack, business = entry
        data = to_zip(pack, business)
        slug = _ascii_slug(business.name)
        return Response(
            content=data,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="presencia-{slug}.zip"'},
        )

    if _WEB_DIR.exists():

        @app.get("/", response_class=HTMLResponse)
        def index() -> HTMLResponse:
            return HTMLResponse((_WEB_DIR / "index.html").read_text(encoding="utf-8"))

        app.mount("/static", StaticFiles(directory=str(_WEB_DIR)), name="static")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    print("Presencia Local — demo en http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
