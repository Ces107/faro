"""Carta estructurada para gastronomía: categorías, precios y alérgenos UE.

Un restaurante, bar o panadería no vende "servicios": vende una carta con
secciones, precios y, por ley (Reglamento UE 1169/2011), la declaración de los
14 alérgenos. Este módulo convierte un texto que el dueño escribe de forma
natural en una carta estructurada que la web renderiza con precios alineados,
badges de alérgenos y datos estructurados schema.org (rich results de Google).

Formato de entrada (una categoría por línea acabada en ``:``; un plato por
línea, ``Nombre — precio (alérgenos)``)::

    Entrantes:
    Croquetas caseras de jamón — 6,50 (gluten, lácteos)
    Ensalada de la casa — 7,00
    Principales:
    Paella valenciana — 14,00 (gluten, crustáceos, pescado)

El precio y los alérgenos son opcionales: un plato puede ser solo su nombre.
Nada se inventa; lo que el dueño no escribe, no aparece.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Allergen(Enum):
    """Los 14 alérgenos de declaración obligatoria (UE 1169/2011, Anexo II).

    ``label`` es el nombre que se muestra; ``short`` el badge compacto en la
    carta; ``synonyms`` los términos que el dueño puede escribir y que se
    normalizan a este alérgeno.
    """

    GLUTEN = ("Gluten", "GLU", ("gluten", "cereales", "trigo", "harina"))
    CRUSTACEOS = ("Crustáceos", "CRU", ("crustaceos", "crustáceos", "gambas", "marisco"))
    HUEVOS = ("Huevos", "HUE", ("huevos", "huevo"))
    PESCADO = ("Pescado", "PES", ("pescado",))
    CACAHUETES = ("Cacahuetes", "CAC", ("cacahuetes", "cacahuete", "mani"))
    SOJA = ("Soja", "SOJ", ("soja",))
    LACTEOS = ("Lácteos", "LAC", ("lacteos", "lácteos", "leche", "lactosa"))
    FRUTOS_CASCARA = ("Frutos de cáscara", "FRU", ("frutos de cascara", "frutos secos",
                                                   "nueces", "almendras", "frutos de cáscara"))
    APIO = ("Apio", "API", ("apio",))
    MOSTAZA = ("Mostaza", "MOS", ("mostaza",))
    SESAMO = ("Sésamo", "SES", ("sesamo", "sésamo", "ajonjoli"))
    SULFITOS = ("Sulfitos", "SUL", ("sulfitos", "dioxido de azufre", "dióxido de azufre"))
    ALTRAMUCES = ("Altramuces", "ALT", ("altramuces", "altramuz"))
    MOLUSCOS = ("Moluscos", "MOL", ("moluscos", "calamar", "pulpo", "mejillones"))

    def __init__(self, label: str, short: str, synonyms: tuple[str, ...]) -> None:
        self.label = label
        self.short = short
        self.synonyms = synonyms


def _allergen_index() -> dict[str, Allergen]:
    """Sinónimo normalizado → alérgeno. Construido una vez."""
    index: dict[str, Allergen] = {}
    for allergen in Allergen:
        for syn in allergen.synonyms:
            index[syn] = allergen
    return index


_ALLERGEN_BY_SYNONYM = _allergen_index()
# Precio: "6,50", "6.50", "14", opcionalmente con € antes o después.
_PRICE_RE = re.compile(r"^\s*€?\s*(\d{1,4}(?:[.,]\d{1,2})?)\s*€?\s*$")
# Separadores nombre/precio que un dueño usaría de forma natural.
_SEP_RE = re.compile(r"\s+[—–\-|]\s+")
# Alérgenos entre paréntesis al final de la línea.
_ALLERGEN_TAIL_RE = re.compile(r"\(([^)]*)\)\s*$")


def normalize_allergens(raw: str) -> tuple[Allergen, ...]:
    """Convierte "gluten, lácteos" en alérgenos canónicos, sin duplicados ni ruido."""
    found: list[Allergen] = []
    for token in re.split(r"[,;/]", raw):
        key = token.strip().lower()
        allergen = _ALLERGEN_BY_SYNONYM.get(key)
        if allergen and allergen not in found:
            found.append(allergen)
    return tuple(found)


@dataclass(frozen=True)
class MenuItem:
    """Un plato: nombre obligatorio; precio y alérgenos opcionales."""

    name: str
    price: str = ""
    allergens: tuple[Allergen, ...] = ()

    @property
    def price_display(self) -> str:
        """Precio con el formato español ``12,50 €`` (vacío si no hay precio)."""
        if not self.price:
            return ""
        return f"{self.price} €"


@dataclass(frozen=True)
class MenuCategory:
    """Una sección de la carta (Entrantes, Principales, Postres...)."""

    title: str
    items: tuple[MenuItem, ...]


def _parse_item(line: str) -> MenuItem | None:
    """Parsea una línea de plato. Devuelve None si queda vacía tras limpiar."""
    rest = line.strip()
    if not rest:
        return None

    allergens: tuple[Allergen, ...] = ()
    tail = _ALLERGEN_TAIL_RE.search(rest)
    if tail:
        allergens = normalize_allergens(tail.group(1))
        rest = rest[: tail.start()].strip()

    price = ""
    parts = _SEP_RE.split(rest)
    if len(parts) >= 2:
        match = _PRICE_RE.match(parts[-1].strip())
        if match:
            price = match.group(1)
            rest = " — ".join(p.strip() for p in parts[:-1]).strip()

    name = rest.strip(" —–-|").strip()
    if not name:
        return None
    return MenuItem(name=name[:80], price=price, allergens=allergens)


def parse_menu(text: str) -> tuple[MenuCategory, ...]:
    """Convierte el texto de la carta en categorías con platos.

    Las líneas que terminan en ``:`` (sin precio) abren una categoría. Los platos
    antes de la primera categoría caen en una sección sin título ("Carta").
    """
    categories: list[MenuCategory] = []
    current_title = ""
    current_items: list[MenuItem] = []

    def flush() -> None:
        if current_items:
            categories.append(MenuCategory(current_title or "Carta", tuple(current_items)))

    for raw_line in text.replace(";", "\n").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and not _ALLERGEN_TAIL_RE.search(line):
            flush()
            current_title = line[:-1].strip()[:50]
            current_items = []
            continue
        item = _parse_item(line)
        if item:
            current_items.append(item)

    flush()
    return tuple(categories[:12])


def all_allergens_present(categories: tuple[MenuCategory, ...]) -> tuple[Allergen, ...]:
    """Alérgenos que aparecen en la carta, en orden canónico (para la leyenda)."""
    present = {a for cat in categories for item in cat.items for a in item.allergens}
    return tuple(a for a in Allergen if a in present)
