"""Enlaces de WhatsApp y teléfono para el negocio."""

from __future__ import annotations

from urllib.parse import quote

from faro.business import BusinessProfile


def default_message(business: BusinessProfile) -> str:
    """Mensaje pre-rellenado que el cliente envía al pulsar el botón de WhatsApp."""
    return f"Hola {business.name}, he visto vuestra página web y quería consultar una cosa."


def whatsapp_link(business: BusinessProfile, message: str | None = None) -> str:
    """Enlace wa.me con el mensaje pre-rellenado."""
    text = message if message is not None else default_message(business)
    return f"https://wa.me/{business.whatsapp_e164}?text={quote(text)}"


def phone_link(business: BusinessProfile) -> str:
    return f"tel:+{business.phone_e164}"
