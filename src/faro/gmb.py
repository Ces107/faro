"""Contenido para la ficha de Google Business Profile.

Genera lo que el dueño necesita pegar en su ficha de Google: descripción,
categorías sugeridas, publicaciones iniciales y la lista de servicios. Texto de
plantilla de calidad; el dueño lo revisa y lo sube.
"""

from __future__ import annotations

from dataclasses import dataclass

from faro.business import BusinessProfile, Sector

_CATEGORIES: dict[Sector, tuple[str, ...]] = {
    Sector.DENTAL: ("Dentista", "Clínica dental"),
    Sector.FISIO: ("Fisioterapeuta", "Centro de fisioterapia"),
    Sector.VETERINARIO: ("Veterinario",),
    Sector.PELUQUERIA: ("Peluquería",),
    Sector.ESTETICA: ("Centro de estética", "Spa"),
    Sector.RESTAURANTE: ("Restaurante",),
    Sector.BAR: ("Bar", "Cafetería"),
    Sector.COMERCIO: ("Tienda",),
    Sector.PANADERIA: ("Panadería", "Pastelería"),
    Sector.TALLER: ("Taller de reparación de automóviles",),
    Sector.GIMNASIO: ("Gimnasio",),
    Sector.FARMACIA: ("Farmacia",),
    Sector.ASESORIA: ("Asesoría fiscal", "Gestoría"),
    Sector.INMOBILIARIA: ("Agencia inmobiliaria",),
    Sector.REFORMAS: ("Empresa de reformas", "Contratista general"),
    Sector.AUTONOMO: ("Servicio profesional",),
    Sector.OTRO: ("Empresa local",),
}

_GMB_DESCRIPTION_MAX = 750


@dataclass(frozen=True)
class GmbContent:
    """Lo que se pega en la ficha de Google Business Profile."""

    description: str
    categories: tuple[str, ...]
    services: tuple[str, ...]
    posts: tuple[str, ...]


def _description(business: BusinessProfile) -> str:
    theme = business.theme
    parts = [
        f"{business.name} es {theme.noun} en {business.city}.",
    ]
    if business.services:
        parts.append("Servicios: " + ", ".join(business.services) + ".")
    if business.highlights:
        parts.append(" ".join(h.rstrip(".") + "." for h in business.highlights))
    if business.hours:
        parts.append(f"Horario: {business.hours}.")
    parts.append(f"Pide cita o información por teléfono o WhatsApp al {business.phone}.")
    text = " ".join(parts)
    if len(text) > _GMB_DESCRIPTION_MAX:
        text = text[: _GMB_DESCRIPTION_MAX - 1].rstrip() + "…"
    return text


def _posts(business: BusinessProfile) -> tuple[str, ...]:
    theme = business.theme
    first_service = business.services[0] if business.services else "nuestros servicios"
    return (
        f"👋 ¡Bienvenidos a {business.name}! {theme.label} en {business.city}. "
        f"Escríbenos por WhatsApp al {business.phone} y te atendemos enseguida.",
        f"¿Sabías que ofrecemos {first_service.lower()}? Pregúntanos sin compromiso. "
        f"Estamos en {business.city}.",
        (f"🕐 Nuestro horario: {business.hours}. Te esperamos."
         if business.hours
         else "Llámanos o escríbenos por WhatsApp y te decimos disponibilidad."),
        "⭐ Si has venido y te hemos ayudado, déjanos una reseña en Google. "
        "Nos ayuda muchísimo y nos toma 30 segundos de tu tiempo.",
        f"📍 Estamos en {business.city}"
        + (f", {business.address}." if business.address else ".")
        + " Ven a vernos o contáctanos para lo que necesites.",
    )


def build_gmb(business: BusinessProfile) -> GmbContent:
    return GmbContent(
        description=_description(business),
        categories=_CATEGORIES[business.sector],
        services=business.services,
        posts=_posts(business),
    )
