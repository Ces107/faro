"""Códigos QR (WhatsApp y reseñas) en SVG, sin dependencias de pago.

Usa segno (Python puro). Devuelve data-URI SVG, listo para incrustar en un
``<img src=...>`` de la landing o de la tarjeta de reseñas, y también el SVG
crudo por si hay que guardarlo como fichero en el pack.
"""

from __future__ import annotations

import segno

from faro.business import BusinessProfile
from faro.reviews import review_url
from faro.whatsapp import whatsapp_link


def qr_data_uri(data: str, *, dark: str = "#0f172a", scale: int = 6) -> str:
    """Data-URI de un QR en SVG para incrustar directamente en HTML."""
    qr = segno.make(data, error="m")
    return qr.svg_data_uri(dark=dark, scale=scale, border=2)


def qr_svg(data: str, *, dark: str = "#0f172a", scale: int = 6) -> str:
    """SVG crudo de un QR (para guardar como fichero en el pack)."""
    import io

    qr = segno.make(data, error="m")
    buffer = io.BytesIO()
    qr.save(buffer, kind="svg", dark=dark, scale=scale, border=2)
    return buffer.getvalue().decode("utf-8")


def whatsapp_qr(business: BusinessProfile) -> str:
    """Data-URI del QR que abre el WhatsApp del negocio."""
    return qr_data_uri(whatsapp_link(business), dark=business.theme.accent)


def review_qr(business: BusinessProfile) -> str:
    """Data-URI del QR que lleva a dejar una reseña en Google."""
    return qr_data_uri(review_url(business), dark="#0f172a")
