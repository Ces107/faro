"""Faro — genera el pack de presencia digital de un negocio local.

A partir de los datos de un negocio produce, en minutos:

- una landing de una página lista para publicar,
- el contenido para Google Business Profile (descripción, categorías, publicaciones, respuestas),
- el enlace y el QR de WhatsApp,
- la tarjeta de reseñas con su QR.

La demo funciona sin cuentas de pago. Con ``ANTHROPIC_API_KEY`` el copy lo
redacta el modelo; sin clave, se usan plantillas de calidad.
"""

from faro.business import BusinessProfile, Sector
from faro.pack import DigitalPresencePack, build_pack

__all__ = ["BusinessProfile", "Sector", "DigitalPresencePack", "build_pack"]

__version__ = "0.1.0"
