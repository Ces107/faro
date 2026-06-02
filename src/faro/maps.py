"""Mapa de Google Maps embebido (sin clave de API).

Para un negocio local, "cómo llegar" es de lo más buscado. El embed por URL
(``output=embed``) no necesita clave de API ni cuenta, así que entra directo en
la landing autocontenida.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from faro.business import BusinessProfile


def maps_query(business: BusinessProfile) -> str:
    """Texto de localización: dirección + ciudad, o solo la ciudad."""
    if business.address:
        return f"{business.address}, {business.city}"
    return business.city


def maps_embed_url(business: BusinessProfile) -> str:
    """URL para el ``src`` del iframe del mapa."""
    return f"https://www.google.com/maps?q={quote_plus(maps_query(business))}&output=embed"


def maps_link(business: BusinessProfile) -> str:
    """Enlace para abrir la ubicación en Google Maps (botón 'cómo llegar')."""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(maps_query(business))}"
