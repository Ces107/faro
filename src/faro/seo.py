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
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from faro.business import BusinessProfile, Sector
from faro.hours import parse_opening_hours

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


def _menu_schema(business: BusinessProfile) -> dict[str, object] | None:
    """schema.org ``Menu`` con secciones, platos y alérgenos suitableForDiet/...

    Devuelve None si el negocio no aportó carta. Los alérgenos se exponen como
    ``menuAddOn`` no — schema.org no tiene un campo de alérgenos canónico, así que
    se listan en el nombre legible del plato y como ``suitableForDiet`` se omite
    (no aplica). Se modela lo que schema.org sí soporta: Menu→MenuSection→MenuItem.
    """
    if not business.menu:
        return None
    sections: list[dict[str, object]] = []
    for cat in business.menu:
        items: list[dict[str, object]] = []
        for item in cat.items:
            entry: dict[str, object] = {"@type": "MenuItem", "name": item.name}
            if item.allergens:
                entry["description"] = "Alérgenos: " + ", ".join(
                    a.label for a in item.allergens
                )
            if item.price:
                entry["offers"] = {
                    "@type": "Offer",
                    "price": item.price.replace(",", "."),
                    "priceCurrency": "EUR",
                }
            items.append(entry)
        sections.append(
            {"@type": "MenuSection", "name": cat.title, "hasMenuItem": items}
        )
    return {"@type": "Menu", "hasMenuSection": sections}


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
        "areaServed": business.service_area or business.city,
    }
    opening_hours = parse_opening_hours(business.hours)
    if opening_hours:
        data["openingHoursSpecification"] = opening_hours
    if business.canonical_url:
        data["url"] = business.canonical_url
    # Valoración real de Google (nunca inventada): solo si el dueño la aporta.
    rating = business.rating
    if rating is not None and business.google_reviews_count.isdigit():
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "reviewCount": int(business.google_reviews_count),
        }
    same_as = [
        url
        for url in (business.google_profile_url, business.instagram, business.facebook)
        if url.startswith("http")
    ]
    if same_as:
        data["sameAs"] = same_as
    # Carta estructurada → schema.org Menu (rich results de restaurantes en Google).
    menu_jsonld = _menu_schema(business)
    if menu_jsonld is not None:
        data["hasMenu"] = menu_jsonld
    # El email no se incluye en el JSON-LD a propósito: lo dejaría en texto plano,
    # rastreable por bots de spam. El teléfono ya cubre el contacto estructurado.
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    # Evita que un "</script>" dentro de un dato cierre el bloque <script> inline.
    return payload.replace("</", "<\\/")


def faq_jsonld(faq: list[tuple[str, str]]) -> str:
    """JSON-LD ``FAQPage`` (rich results en Google). '' si no hay preguntas."""
    if not faq:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq
        ],
    }
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def analytics_snippet(business: BusinessProfile) -> str:
    """Contador de visitas (GoatCounter) para el ``<head>``, o '' si no hay código.

    GoatCounter cuenta páginas vistas sin cookies y sin recoger datos personales,
    así que NO rompe la promesa de "sin cookies de seguimiento" del aviso legal ni
    obliga a banner de consentimiento. Es la pieza que permite al operador
    demostrar que la web recibe visitas (el gap que mataba la pregunta "¿cuántos
    clientes me trae?"). El código ya viene validado a ``[a-z0-9-]`` por
    ``BusinessProfile``, así que es seguro incrustarlo sin escapar.
    """
    code = business.analytics_goatcounter
    if not code:
        return ""
    endpoint = f"https://{code}.goatcounter.com/count"
    return (
        f'<script data-goatcounter="{endpoint}" '
        'async src="//gc.zgo.at/count.js"></script>'
    )


def tracked_url(
    business: BusinessProfile,
    *,
    source: str,
    medium: str = "qr",
    campaign: str = "",
) -> str:
    """URL del sitio del negocio con etiquetas UTM, para atribución por canal.

    El contador (GoatCounter, ``analytics_snippet``) cuenta visitas pero no sabe
    de DÓNDE vienen. Si el QR del mostrador y el campo "Sitio web" de la ficha de
    Google llevan la misma URL pero con una etiqueta distinta, en el panel se ve
    cuántas visitas trae cada canal: eso es lo que permite responder con datos a
    "¿cuántos clientes me trae la web?" (el gap del buyer-review).

    SOLO para colocaciones EXTERNAS (ficha de Google, QR impreso, folleto). El
    canonical / Open Graph / JSON-LD de la propia página usan ``canonical_url``
    SIN tocar y deben quedar limpios; por eso esto es una función aparte y no se
    aplica nunca a esas piezas.

    Devuelve '' si el negocio aún no tiene URL publicada (``canonical_url``): la
    atribución solo existe cuando hay un sitio al que apuntar.
    """
    base = business.canonical_url
    if not base:
        return ""
    new_params = [("utm_source", source), ("utm_medium", medium)]
    if campaign:
        new_params.append(("utm_campaign", campaign))
    split = urlsplit(base)
    query = parse_qsl(split.query, keep_blank_values=True)
    existing = {key for key, _ in query}
    query.extend((key, value) for key, value in new_params if key not in existing)
    return urlunsplit(split._replace(query=urlencode(query)))


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
