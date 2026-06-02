"""Generación del copy de la landing.

Dos vías con el mismo resultado (``LandingCopy``):

- ``scripted_copy``: plantillas de calidad por sector. Sin coste, sin internet.
- ``live_copy``: la API de Anthropic redacta el texto. Si no hay clave o falla,
  se cae a las plantillas. El cliente nunca se queda sin landing.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from presencia_local.business import BusinessProfile

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


def _default_value_props(business: BusinessProfile) -> tuple[ValueProp, ...]:
    theme = business.theme
    props = [
        ValueProp(
            "Cercanía",
            f"Estamos en {business.city}. Nos tienes al lado cuando nos necesitas.",
        ),
        ValueProp(
            "Trato de verdad",
            "Te atendemos personas, no centralitas. Dinos qué necesitas y te ayudamos.",
        ),
        ValueProp(
            "Profesionalidad",
            f"{theme.label} con la experiencia y el cuidado que tu confianza merece.",
        ),
    ]
    # Si el negocio aporta puntos fuertes, los anteponemos.
    for highlight in business.highlights[:2]:
        props.insert(0, ValueProp("Lo que nos diferencia", highlight))
    return tuple(props[:3])


def scripted_copy(business: BusinessProfile) -> LandingCopy:
    """Copy de calidad a partir de plantillas, sin LLM."""
    theme = business.theme
    slogan = business.slogan or theme.headline
    hl = f" {business.highlights[0]}." if business.highlights else ""
    hero_subtitle = f"{theme.label} en {business.city}.{hl}".strip()
    services_phrase = ", ".join(business.services[:3])
    about_text = (
        f"En {business.name} llevamos el día a día de {theme.label.lower()} en {business.city}. "
        f"Nos puedes encontrar para {services_phrase.lower()} y mucho más. "
        "Escríbenos por WhatsApp o llámanos y te atendemos enseguida."
    )
    return LandingCopy(
        slogan=slogan,
        hero_subtitle=hero_subtitle,
        about_title=f"Sobre {business.name}",
        about_text=about_text,
        services_intro="Esto es lo que podemos hacer por ti",
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


def _parse_live(payload: str, fallback: LandingCopy) -> LandingCopy:
    try:
        data = json.loads(payload)
        props = tuple(
            ValueProp(str(p["title"]), str(p["description"]))
            for p in data["value_props"][:3]
        )
        if not props:
            return fallback
        return LandingCopy(
            slogan=str(data["slogan"]),
            hero_subtitle=str(data["hero_subtitle"]),
            about_title=str(data["about_title"]),
            about_text=str(data["about_text"]),
            services_intro=str(data["services_intro"]),
            value_props=props,
        )
    except (json.JSONDecodeError, KeyError, TypeError):
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
        return fallback
    facts = {
        "nombre": business.name,
        "sector": business.theme.label,
        "ciudad": business.city,
        "servicios": list(business.services),
        "puntos_fuertes": list(business.highlights),
    }
    try:
        client = anthropic.Anthropic(api_key=api_key)
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
    except Exception:
        return fallback


def generate_copy(business: BusinessProfile, *, use_live: bool = True) -> LandingCopy:
    return live_copy(business) if use_live else scripted_copy(business)
