"""Servidor de la demo: formulario del negocio, vista previa de la landing y descarga del pack.

Corre en local sin cuentas de pago. El operador rellena los datos del negocio
delante del cliente, ve la web al momento y descarga el .zip listo para entregar.
"""

from __future__ import annotations

import json
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
_PROSPECT_DIR = Path(__file__).resolve().parents[2] / "prospect"
_MAX_PACKS_IN_MEMORY = 50


def _load_prospects() -> dict[str, dict[str, object]]:
    """Une los prospects.json de todos los municipios censados (faro-prospect).

    Lectura perezosa en cada petición: los ficheros son pequeños y locales, y
    así un censo recién generado aparece sin reiniciar la consola.
    """
    merged: dict[str, dict[str, object]] = {}
    if not _PROSPECT_DIR.exists():
        return merged
    for path in sorted(_PROSPECT_DIR.glob("*/prospects.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            for slug, entry in data.items():
                if isinstance(entry, dict):
                    merged[slug] = entry
    return merged


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


def _demo_form_for(slug: str) -> dict[str, str] | None:
    """Datos de formulario para la demo pública de un negocio.

    Si el slug está en el censo (``faro-prospect``), superpone sus datos reales
    (nombre, dirección…) sobre los datos de ejemplo del sector: así la web sale
    completa y presentable aunque el censo traiga pocos campos, y el operador
    sustituye el resto con el dueño delante. Si el slug no está en el censo pero
    es un sector válido, usa solo el ejemplo. Devuelve ``None`` si no hay ninguno.
    """
    from faro.engine.demo import demo_data

    prospect = _load_prospects().get(slug)
    if prospect is not None:
        raw = prospect.get("values", {})
        items = raw.items() if isinstance(raw, dict) else []
        real = {str(k): str(v) for k, v in items if str(v).strip()}
        sector = str(prospect.get("sector", "otro"))
        try:
            base = demo_data(Sector(sector))
        except ValueError:
            base = {}
        return {**base, **real, "sector": sector}

    try:
        sector_enum = Sector(slug)
    except ValueError:
        return None
    return {**demo_data(sector_enum), "sector": sector_enum.value}


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

    @app.get("/api/prospect")
    def prospect_index() -> JSONResponse:
        """Censo local de prospección (si se generó con ``faro-prospect``)."""
        prospects = _load_prospects()
        return JSONResponse(
            {
                "count": len(prospects),
                "prospects": [
                    {
                        "slug": slug,
                        "sector": entry.get("sector", ""),
                        "values": entry.get("values", {}),
                    }
                    for slug, entry in sorted(prospects.items())
                ],
            }
        )

    @app.get("/api/prospect/prefill/{slug}")
    def prospect_prefill(slug: str) -> JSONResponse:
        """Datos de precarga de un negocio del censo (enlazado desde ruta.html)."""
        entry = _load_prospects().get(slug)
        if entry is None:
            raise HTTPException(status_code=404, detail="Negocio no encontrado en el censo")
        return JSONResponse({"slug": slug, **entry})

    @app.get("/d/{slug}", response_class=HTMLResponse)
    def public_demo(slug: str) -> HTMLResponse:
        """Web del negocio a pantalla completa para la demo en el móvil del cliente.

        Toma los datos públicos del censo (``faro-prospect``); si el slug no está
        en el censo pero es un sector válido (p. ej. ``/d/bar``), usa los datos de
        ejemplo de ese sector. El cliente ve SOLO su web, sin el panel del operador.
        Es lo que sirve ``faro-demo`` detrás del túnel público.
        """
        form = _demo_form_for(slug)
        if form is None:
            raise HTTPException(
                status_code=404,
                detail="No está en el censo ni es un sector válido.",
            )
        try:
            business = BusinessProfile.from_form(form)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        pack = build_pack(business, use_live=use_live)
        return HTMLResponse(pack.landing_html)

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
        warnings: list[str] = []
        if not business.whatsapp_looks_mobile:
            warnings.append(
                f"El botón de WhatsApp apunta a {business.whatsapp}, que parece un fijo. "
                "Confirma con el dueño que ese número tiene WhatsApp; si no, pon un móvil "
                "en el campo «WhatsApp (si es otro)» y vuelve a generar."
            )
        return JSONResponse(
            {
                "pack_id": pack_id,
                "preview_url": f"/preview/{pack_id}",
                "download_url": f"/download/{pack_id}",
                "warnings": warnings,
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

    host = os.environ.get("FARO_HOST", "127.0.0.1")
    port = int(os.environ.get("FARO_PORT", "8000"))
    print(f"Faro — demo en http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
