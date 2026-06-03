"""Servidor de la demo: formulario del negocio, vista previa de la landing y descarga del pack.

Corre en local sin cuentas de pago. El operador rellena los datos del negocio
delante del cliente, ve la web al momento y descarga el .zip listo para entregar.
"""

from __future__ import annotations

import os
import secrets
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from faro.business import BusinessProfile, Sector
from faro.pack import DigitalPresencePack, build_pack, to_zip

_WEB_DIR = Path(__file__).resolve().parents[2] / "web"


_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"
_MAX_PACKS_IN_MEMORY = 50


def _ascii_slug(text: str) -> str:
    """Slug ASCII para el nombre del fichero (las cabeceras HTTP no admiten Unicode)."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = "".join(c if c.isalnum() else "-" for c in normalized.lower())
    return "-".join(filter(None, slug.split("-")))[:40] or "negocio"


def _save_pack_to_disk(
    pack: DigitalPresencePack, business: BusinessProfile, pack_id: str
) -> None:
    """Guarda una copia del pack entregado para poder recuperarlo o re-editarlo.

    Persistir es un extra: si el disco falla, la generación no se interrumpe.
    """
    try:
        folder = _OUTPUT_DIR / f"{_ascii_slug(business.name)}-{pack_id}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "pack.zip").write_bytes(to_zip(pack, business))
    except OSError:
        pass


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
    cif: str = ""
    google_review_url: str = ""
    highlights: str = ""
    slogan: str = ""
    about: str = ""
    brand_color: str = ""
    photos: str = ""
    testimonials: str = ""
    canonical_url: str = ""
    years: str = ""
    differentiators: str = ""
    instagram: str = ""
    facebook: str = ""
    payment_methods: str = ""
    parking: str = ""
    languages: str = ""
    booking_style: str = ""

    model_config = {"extra": "allow"}  # acepta los campos por sector "x_*" del formulario


def create_app(*, use_live: bool = False) -> FastAPI:
    """Crea la app. ``use_live`` está apagado por defecto: la demo no debe llamar
    a un servicio de pago durante una venta. Se activa con ``FARO_LIVE=1`` (ver
    ``app`` más abajo) o pasándolo explícitamente."""
    app = FastAPI(title="Faro", version="0.1.0")
    packs: dict[str, tuple[DigitalPresencePack, BusinessProfile]] = {}

    @app.get("/api/sectors")
    def sectors() -> dict[str, list[dict[str, object]]]:
        from faro.business import theme_for
        from faro.engine.registry import template_for
        from faro.playbook import extra_hint, playbook_for

        return {
            "sectors": [
                {
                    "value": s.value,
                    "label": theme_for(s).label,
                    "offer_word": playbook_for(s).offer_word,
                    "extra_hint": extra_hint(s),
                    "template": template_for(s).id,
                }
                for s in Sector
            ]
        }

    @app.get("/api/demo/{sector}")
    def demo(sector: str) -> JSONResponse:
        """Datos de ejemplo completos para ver una web entera de un clic.

        Es contenido de demostración (el operador lo edita con los datos reales
        del negocio antes de entregar el pack).
        """
        from faro.engine.demo import demo_data

        try:
            return JSONResponse(demo_data(Sector(sector)))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Sector desconocido") from exc

    @app.get("/api/form/{sector}")
    def form_schema(sector: str) -> JSONResponse:
        """El formulario declarativo de la plantilla que cubre este sector.

        El front lo renderiza tal cual: así el formulario es DISTINTO según la
        plantilla, sin HTML escrito a mano por sector.
        """
        from faro.engine.registry import template_for

        try:
            spec = template_for(Sector(sector))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Sector desconocido") from exc
        return JSONResponse(
            {
                "template": spec.id,
                "name": spec.name,
                "family": spec.family,
                "schema": spec.form_schema.as_dict(),
            }
        )

    @app.post("/api/generate")
    def generate(req: GenerateRequest) -> JSONResponse:
        try:
            business = BusinessProfile.from_form(req.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        pack = build_pack(business, use_live=use_live)
        pack_id = secrets.token_hex(8)
        packs[pack_id] = (pack, business)
        _save_pack_to_disk(pack, business, pack_id)
        # Cap FIFO del store en memoria: no crece sin límite en sesiones largas.
        while len(packs) > _MAX_PACKS_IN_MEMORY:
            packs.pop(next(iter(packs)))
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
            headers={"Content-Disposition": f'attachment; filename="faro-{slug}.zip"'},
        )

    if _WEB_DIR.exists():

        @app.get("/", response_class=HTMLResponse)
        def index() -> HTMLResponse:
            return HTMLResponse((_WEB_DIR / "index.html").read_text(encoding="utf-8"))

        app.mount("/static", StaticFiles(directory=str(_WEB_DIR)), name="static")

    return app


app = create_app(use_live=os.environ.get("FARO_LIVE") == "1")


def main() -> None:
    import uvicorn

    print("Faro — demo en http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
