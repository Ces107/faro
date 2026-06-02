"""SEO de la landing: datos estructurados, favicon y metadatos para compartir.

Lo que de verdad ayuda a "que te encuentren en Google":

- **Datos estructurados** (schema.org ``LocalBusiness``): Google los lee para el
  panel de negocio local y el SEO local. Es la pieza que más diferencia una web
  "bonita" de una web que posiciona.
- **Open Graph**: cuando alguien comparte el enlace por WhatsApp o redes, sale
  con título y descripción en condiciones.
- **Favicon** con la inicial del negocio, para la pestaña del navegador.
"""

from __future__ import annotations

import json
from urllib.parse import quote

from faro.business import BusinessProfile, Sector

_SCHEMA_TYPES: dict[Sector, str] = {
    Sector.DENTAL: "Dentist",
    Sector.FISIO: "Physiotherapy",
    Sector.VETERINARIO: "VeterinaryCare",
    Sector.PELUQUERIA: "HairSalon",
    Sector.ESTETICA: "BeautySalon",
    Sector.RESTAURANTE: "Restaurant",
    Sector.BAR: "BarOrPub",
    Sector.COMERCIO: "Store",
    Sector.PANADERIA: "Bakery",
    Sector.TALLER: "AutoRepair",
    Sector.GIMNASIO: "ExerciseGym",
    Sector.FARMACIA: "Pharmacy",
    Sector.ASESORIA: "AccountingService",
    Sector.INMOBILIARIA: "RealEstateAgent",
    Sector.REFORMAS: "GeneralContractor",
    Sector.AUTONOMO: "ProfessionalService",
    Sector.OTRO: "LocalBusiness",
}


def schema_type(sector: Sector) -> str:
    return _SCHEMA_TYPES[sector]


def local_business_jsonld(business: BusinessProfile) -> str:
    """JSON-LD schema.org del negocio (string para incrustar en un <script>)."""
    address: dict[str, str] = {
        "@type": "PostalAddress",
        "addressLocality": business.city,
        "addressCountry": "ES",
    }
    if business.address:
        address["streetAddress"] = business.address
    data: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": schema_type(business.sector),
        "name": business.name,
        "telephone": f"+{business.phone_e164}",
        "address": address,
        "areaServed": business.city,
    }
    # El email no se incluye en el JSON-LD a propósito: lo dejaría en texto plano,
    # rastreable por bots de spam. El teléfono ya cubre el contacto estructurado.
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    # Evita que un "</script>" dentro de un dato cierre el bloque <script> inline.
    return payload.replace("</", "<\\/")


def favicon_data_uri(business: BusinessProfile) -> str:
    """Favicon SVG (inicial del negocio sobre el color de marca)."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{business.color}"/>'
        f'<text x="32" y="44" font-size="34" fill="#ffffff" text-anchor="middle" '
        f'font-family="system-ui,sans-serif" font-weight="700">{business.initials}</text>'
        f"</svg>"
    )
    return "data:image/svg+xml," + quote(svg)
