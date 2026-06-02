"""Reseñas: enlace para captarlas y respuestas listas para el dueño.

Conseguir reseñas y responderlas es lo que más mueve el ranking local en Google.
Aquí se genera el enlace donde el cliente deja la reseña (para la tarjeta con QR)
y un juego de respuestas que el dueño puede usar tal cual.

Importante: nunca se incentiva ni se condiciona la reseña (eso va contra las
normas de Google). Solo se invita a quien ya ha sido cliente.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from presencia_local.business import BusinessProfile


def review_url(business: BusinessProfile) -> str:
    """Enlace para dejar una reseña.

    Si el negocio aporta su enlace directo de Google (lo ideal), se usa. Si no,
    se genera una búsqueda en Google Maps que lleva a su ficha, desde donde el
    cliente puede valorar.
    """
    if business.google_review_url:
        return business.google_review_url
    query = quote_plus(f"{business.name} {business.city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


@dataclass(frozen=True)
class ReviewReplies:
    """Respuestas tipo para reseñas, por número de estrellas."""

    positive: str
    neutral: str
    negative: str


def review_replies(business: BusinessProfile) -> ReviewReplies:
    name = business.name
    return ReviewReplies(
        positive=(
            f"¡Muchas gracias por tu reseña! En {name} nos alegra un montón haberte "
            "ayudado. Te esperamos siempre que lo necesites."
        ),
        neutral=(
            "Gracias por tu valoración y por tomarte el tiempo de dejarnos tu opinión. "
            "Tomamos nota para seguir mejorando. Si quieres contarnos algo más, "
            f"escríbenos al {business.phone}."
        ),
        negative=(
            "Sentimos que tu experiencia no haya sido la que esperabas. Nos gustaría "
            f"entender qué pasó y arreglarlo. ¿Nos escribes al {business.phone}? "
            "Gracias por ayudarnos a mejorar."
        ),
    )


def review_card_invite(business: BusinessProfile) -> str:
    """Texto de la tarjeta física de reseñas (la que se deja en el mostrador)."""
    return (
        f"¿Te hemos ayudado en {business.name}?\n"
        "Déjanos tu reseña en Google. Nos toma 30 segundos y a ti también.\n"
        "Escanea el código y cuéntanos qué tal."
    )
