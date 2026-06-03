"""Construcción del contenido de las secciones a partir del negocio + el playbook.

Resuelve, de forma honesta y agnóstica de la plantilla: las tarjetas de servicio
(con su beneficio e icono por sector), las preguntas frecuentes rellenadas con los
datos reales, y las cifras de la franja de estadísticas (solo datos verdaderos).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from faro.business import BusinessProfile
from faro.icons import get_icon
from faro.playbook import FaqItem, SectorPlaybook

_PRICE_RE = re.compile(r"\d+\s?€")
_ALL_WEEK_RE = re.compile(r"l\s*[-a]\s*d|todos los d|lunes a domingo|7 d|24\s*h", re.IGNORECASE)


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


@dataclass(frozen=True)
class ServiceCard:
    name: str
    benefit: str
    icon: str  # SVG interno (de icons.get_icon)
    price: str  # "" si no hay


@dataclass(frozen=True)
class Stat:
    value: str
    label: str


def build_service_cards(business: BusinessProfile, playbook: SectorPlaybook) -> list[ServiceCard]:
    cards: list[ServiceCard] = []
    for service in business.services:
        norm = _norm(service)
        benefit = playbook.generic_benefit
        icon_name = playbook.icon
        for keyword, text in playbook.service_benefits.items():
            if _norm(keyword) in norm:
                benefit = text
                break
        for keyword, name in playbook.service_icons.items():
            if _norm(keyword) in norm:
                icon_name = name
                break
        price_match = _PRICE_RE.search(service)
        cards.append(
            ServiceCard(
                name=service,
                benefit=benefit,
                icon=get_icon(icon_name),
                price=price_match.group(0) if price_match else "",
            )
        )
    return cards


def build_faq(business: BusinessProfile, playbook: SectorPlaybook) -> list[FaqItem]:
    """Rellena las FAQ con datos reales; descarta las que necesitan dirección si no hay."""
    out: list[FaqItem] = []
    for item in playbook.faq:
        # Descarta la pregunta si su respuesta necesita una dirección que no hay
        # (por el flag o porque el texto la interpola), para no dejar «Estamos en .».
        if (item.needs_address or "{address}" in item.answer) and not business.address:
            continue
        answer = (
            item.answer.replace("{phone}", business.phone)
            .replace("{city}", business.city)
            .replace("{address}", business.address)
        )
        out.append(FaqItem(item.question, answer, item.needs_address))
    return out


def build_stats(business: BusinessProfile, playbook: SectorPlaybook) -> list[Stat]:
    """Cifras honestas para la franja de estadísticas. Nunca se inventan números."""
    tiles: list[Stat] = []
    # Años de experiencia, solo si el dueño lo aporta (nunca inventado).
    years = business.years.strip()
    if years.isdigit() and len(years) == 4:
        tiles.append(Stat(f"Desde {years}", "en el barrio"))
    elif years.isdigit():
        tiles.append(Stat(f"{years}", "años de experiencia"))
    if len(business.services) >= 3:
        tiles.append(Stat(f"{len(business.services)}", playbook.offer_word))
    if business.hours and _ALL_WEEK_RE.search(business.hours):
        tiles.append(Stat("7 días", "te atendemos"))
    tiles.append(Stat(business.city, "cerca de ti"))
    for highlight in business.highlights:
        if len(highlight) <= 28 and len(tiles) < 4:
            tiles.append(Stat("✓", highlight))
    if len(tiles) < 3:
        tiles.append(Stat(playbook.stat_fallback, ""))
    return tiles[:4]
