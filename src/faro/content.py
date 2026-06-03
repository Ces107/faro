"""Generación del copy de la landing.

Dos vías con el mismo resultado (``LandingCopy``):

- ``scripted_copy``: plantillas de calidad por sector. Sin coste, sin internet.
- ``live_copy``: la API de Anthropic redacta el texto. Si no hay clave o falla,
  se cae a las plantillas. El cliente nunca se queda sin landing.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, replace

from faro.business import BusinessProfile

_LOG = logging.getLogger("faro.content")
_MODEL = "claude-haiku-4-5-20251001"


@dataclass(frozen=True)
class ValueProp:
    title: str
    description: str


@dataclass(frozen=True)
class LandingCopy:
    """Todos los textos que necesita la landing."""

    slogan: str
    hero_subtitle: str
    about_title: str
    about_text: str
    services_intro: str
    value_props: tuple[ValueProp, ...]


_DIFF_TITLES = ("Lo que nos diferencia", "Por qué elegirnos", "Nuestro compromiso")


def _default_value_props(business: BusinessProfile) -> tuple[ValueProp, ...]:
    theme = business.theme
    # Si el dueño nos dice qué les diferencia, esos son los puntos fuertes reales
    # (con títulos distintos, no el genérico repetido tres veces).
    if business.differentiators:
        return tuple(
            ValueProp(_DIFF_TITLES[i % len(_DIFF_TITLES)], d)
            for i, d in enumerate(business.differentiators[:3])
        )
    # Si no, tres motivos honestos y genéricos (cada uno con su propio título).
    return (
        ValueProp("Cercanía", f"Estamos en {business.city}, al lado cuando lo necesites."),
        ValueProp("Trato de verdad", "Te atienden personas, no centralitas. Dinos qué necesitas."),
        ValueProp(
            "Profesionalidad",
            f"{theme.label} con la experiencia y el cuidado que mereces.",
        ),
    )


def scripted_copy(business: BusinessProfile) -> LandingCopy:
    """Copy de calidad a partir de plantillas, sin LLM.

    Si el negocio aporta su propia descripción (``about``), se respeta tal cual en
    vez de auto-redactar; así no inventamos texto cuando el dueño nos lo da.
    """
    from faro.playbook import playbook_for

    theme = business.theme
    playbook = playbook_for(business.sector)
    slogan = business.slogan or theme.headline
    hl = f" {business.highlights[0]}." if business.highlights else ""
    hero_subtitle = f"{theme.label} en {business.city}.{hl}".strip()
    if business.about.strip():
        about_text = business.about.strip()
    else:
        services_phrase = ", ".join(business.services[:3]).lower()
        about_text = (
            f"En {business.name} {playbook.offer_verb} {services_phrase} en {business.city}. "
            "Escríbenos por WhatsApp o llámanos y te atendemos enseguida."
        )
    return LandingCopy(
        slogan=slogan,
        hero_subtitle=hero_subtitle,
        about_title=f"Sobre {business.name}",
        about_text=about_text,
        services_intro=playbook.offer_heading,
        value_props=_default_value_props(business),
    )


_LIVE_SYSTEM = (
    "Eres copywriter de negocios locales en España. Te doy los datos de un negocio "
    "y devuelves SOLO un JSON con estas claves exactas: slogan (max 8 palabras), "
    "hero_subtitle (max 16 palabras), about_title, about_text (2-3 frases, cercano, "
    "sin inventar datos que no te doy), services_intro, value_props (lista de 3 "
    "objetos con title de 1-3 palabras y description de 1 frase). Castellano de "
    "España, cercano y honesto, sin palabras de relleno ni superlativos vacíos. "
    "No inventes premios, cifras ni años de experiencia que no aparezcan en los datos."
)


def _clamp(value: object, limit: int) -> str:
    return str(value).strip()[:limit]


def _parse_live(payload: str, fallback: LandingCopy) -> LandingCopy:
    try:
        data = json.loads(payload)
        props = tuple(
            ValueProp(_clamp(p["title"], 40), _clamp(p["description"], 160))
            for p in data["value_props"][:3]
        )
        if not props:
            return fallback
        return LandingCopy(
            slogan=_clamp(data["slogan"], 90),
            hero_subtitle=_clamp(data["hero_subtitle"], 160),
            about_title=_clamp(data["about_title"], 80),
            about_text=_clamp(data["about_text"], 400),
            services_intro=_clamp(data["services_intro"], 80),
            value_props=props,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        _LOG.warning("Respuesta del modo live no válida (%s); uso plantillas.", exc)
        return fallback


def live_copy(business: BusinessProfile) -> LandingCopy:
    """Copy redactado por el LLM; cae a ``scripted_copy`` si no es posible."""
    fallback = scripted_copy(business)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return fallback
    try:
        import anthropic
    except ImportError:
        _LOG.warning("Modo live pedido pero falta el paquete 'anthropic'; uso plantillas.")
        return fallback
    facts = {
        "nombre": business.name,
        "sector": business.theme.label,
        "ciudad": business.city,
        "servicios": list(business.services),
        "puntos_fuertes": list(business.highlights),
    }
    try:
        # Timeout y un solo reintento: una venta presencial no puede quedarse
        # colgada esperando a la red. Si tarda o falla, se cae a las plantillas.
        client = anthropic.Anthropic(api_key=api_key, timeout=15.0, max_retries=1)
        message = client.messages.create(
            model=_MODEL,
            max_tokens=700,
            system=_LIVE_SYSTEM,
            messages=[{"role": "user", "content": json.dumps(facts, ensure_ascii=False)}],
        )
        for block in message.content:
            if block.type == "text":
                return _parse_live(block.text, fallback)
        return fallback
    except Exception as exc:
        _LOG.warning("El modo live falló (%s); uso plantillas.", exc)
        return fallback


def generate_copy(business: BusinessProfile, *, use_live: bool = True) -> LandingCopy:
    copy = live_copy(business) if use_live else scripted_copy(business)
    # Si el dueño dictó su descripción, se respeta SIEMPRE (también en modo live):
    # no inventamos un "sobre nosotros" cuando nos lo han dado.
    if business.about.strip():
        copy = replace(copy, about_text=business.about.strip())
    return copy
