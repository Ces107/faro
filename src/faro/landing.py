"""Renderizado de la landing de una página.

Punto de entrada de alto nivel. ``build_landing`` genera el copy y delega el
render en el motor de plantillas (``faro.engine.render``), que produce un único
HTML autocontenido (CSS, JS, fuentes y QR incrustados) listo para subir a
cualquier hosting estático. El render clásico de plantilla única quedó retirado;
la dirección de arte por familia vive en ``faro.engine``.
"""

from __future__ import annotations

from faro.business import BusinessProfile
from faro.content import LandingCopy, generate_copy


def render_landing(business: BusinessProfile, copy: LandingCopy) -> str:
    """Renderiza la landing a un HTML autocontenido con el motor de plantillas."""
    from faro.engine.render import render_site

    return render_site(business, copy)


def build_landing(business: BusinessProfile, *, use_live: bool = True) -> str:
    """Atajo: genera el copy y renderiza la landing en un paso."""
    copy = generate_copy(business, use_live=use_live)
    return render_landing(business, copy)
