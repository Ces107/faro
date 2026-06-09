"""CLI ``faro-prospect``. Eje de cambio: flags y salida de consola.

Capa imperativa: resuelve el municipio, descarga POIs, construye el censo y
escribe los artefactos de la salida de venta en ``prospect/<municipio>/``:

- ``census.json``      censo completo (incluye teléfonos: SOLO uso local)
- ``prospects.json``   datos de precarga del formulario por negocio
- ``ruta.html``        hoja de ruta imprimible agrupada por calle
- ``folletos.html``    folletos A6 por sector con QR al showcase

El directorio ``prospect/`` está en .gitignore: contiene nombres de negocios
reales y no debe publicarse (minimización RGPD + ODbL share-alike).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import unicodedata
from dataclasses import asdict
from pathlib import Path

from faro.prospect.census import BoundingBox, CensusResult, build_census, prefill_values
from faro.prospect.flyers import flyers_html
from faro.prospect.overpass import (
    HttpFetcher,
    Municipality,
    ProspectError,
    default_fetcher,
    fetch_pois,
    resolve_municipality,
)
from faro.prospect.route import route_sheet_html

__all__ = ["main"]


def _dir_slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = "".join(c if c.isalnum() else "-" for c in normalized.lower())
    return "-".join(filter(None, slug.split("-")))[:40] or "municipio"


def _parse_bbox(raw: str) -> BoundingBox:
    try:
        south, west, north, east = (float(part) for part in raw.split(","))
    except ValueError as exc:
        raise ProspectError("--bbox debe ser 'sur,oeste,norte,este' en grados") from exc
    return BoundingBox(south=south, west=west, north=north, east=east)


def _default_city(municipality_name: str) -> str:
    """Nombre castellano por defecto: la última parte de un nombre bilingüe OSM."""
    return municipality_name.split(" / ")[-1].strip() or municipality_name


def _write_outputs(
    out_dir: Path, census: CensusResult, *, city: str, base_url: str, generated_on: str
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    census_path = out_dir / "census.json"
    census_path.write_text(
        json.dumps(
            {
                "municipality": census.municipality,
                "generated_on": generated_on,
                "total_raw": census.total_raw,
                "excluded": {reason.value: count for reason, count in census.excluded},
                "prospects": [asdict(p) | {"sector": p.sector.value} for p in census.prospects],
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    prefill_path = out_dir / "prospects.json"
    prefill_path.write_text(
        json.dumps(
            {
                p.slug: {"sector": p.sector.value, "values": prefill_values(p, city=city)}
                for p in census.prospects
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    route_path = out_dir / "ruta.html"
    route_path.write_text(
        route_sheet_html(census, generated_on=generated_on, prefill_base=base_url),
        encoding="utf-8",
    )
    flyers_path = out_dir / "folletos.html"
    flyers_path.write_text(
        flyers_html(
            census,
            operator_name=os.environ.get("FARO_OPERATOR_NAME", ""),
            operator_contact=os.environ.get("FARO_OPERATOR_CONTACT", ""),
        ),
        encoding="utf-8",
    )
    return [census_path, prefill_path, route_path, flyers_path]


def _summary(census: CensusResult) -> str:
    top_families: dict[str, int] = {}
    for prospect in census.prospects:
        top_families[prospect.family] = top_families.get(prospect.family, 0) + 1
    by_count = sorted(top_families.items(), key=lambda kv: -kv[1])
    families = ", ".join(f"{fam}: {n}" for fam, n in by_count)
    excluded = ", ".join(f"{reason.value}: {n}" for reason, n in census.excluded)
    return (
        f"Censo de {census.municipality}: {len(census.prospects)} candidatos "
        f"de {census.total_raw} POIs.\n"
        f"  Por familia: {families or '—'}\n"
        f"  Excluidos: {excluded or '—'}\n"
        "  Recuerda: candidato no es cliente; verifica en Google delante de la puerta.\n"
        "  Datos © OpenStreetMap contributors (ODbL). Uso interno: no publiques la lista."
    )


def main(argv: list[str] | None = None, *, fetch: HttpFetcher | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="faro-prospect",
        description="Censo de negocios sin web de un municipio + hoja de ruta de venta.",
    )
    parser.add_argument("municipality", help="Nombre del municipio (p. ej. 'Sagunto')")
    parser.add_argument("--rel-id", type=int, default=0, help="ID de relación OSM (si es ambiguo)")
    parser.add_argument("--bbox", default="", help="Recorte 'sur,oeste,norte,este' (núcleo urbano)")
    parser.add_argument(
        "--city", default="", help="Nombre de ciudad para la web (p. ej. 'Puerto de Sagunto')"
    )
    parser.add_argument("--out", default="prospect", help="Directorio de salida (def: prospect/)")
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:8000/", help="URL base de la consola Faro local"
    )
    args = parser.parse_args(argv)
    fetcher = fetch or default_fetcher
    try:
        if args.rel_id:
            municipality = Municipality(rel_id=args.rel_id, name=args.municipality)
        else:
            municipality = resolve_municipality(args.municipality, fetch=fetcher)
        elements = fetch_pois(municipality, fetch=fetcher)
        bbox = _parse_bbox(args.bbox) if args.bbox else None
        census = build_census(elements, municipality=municipality.name, bbox=bbox)
    except ProspectError as exc:
        print(f"ERROR: {exc}")
        return 2
    city = args.city or _default_city(municipality.name)
    generated_on = _dt.date.today().isoformat()
    out_dir = Path(args.out) / _dir_slug(args.city or municipality.name)
    paths = _write_outputs(
        out_dir, census, city=city, base_url=args.base_url, generated_on=generated_on
    )
    print(_summary(census))
    print("  Ficheros:")
    for path in paths:
        print(f"    {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
