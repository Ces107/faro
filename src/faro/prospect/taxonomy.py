"""Taxonomía OSM → sector Faro. Eje de cambio: cobertura de etiquetas OpenStreetMap.

Mapea pares ``(clave, valor)`` de OpenStreetMap al :class:`~faro.business.Sector`
que mejor cubre ese tipo de negocio, con una etiqueta legible en castellano para
la hoja de ruta. Lo que no está aquí no es prospectable (colegios, parkings…).
"""

from __future__ import annotations

from faro.business import Sector

__all__ = ["OSM_KEYS", "sector_for", "category_label", "amenity_values", "regex_values"]

# Claves OSM que el censo consulta y sabe interpretar.
OSM_KEYS: tuple[str, ...] = ("shop", "amenity", "craft", "office", "leisure", "healthcare")

# Pares exactos (clave, valor) → (sector, etiqueta en castellano).
_EXACT: dict[tuple[str, str], tuple[Sector, str]] = {
    # Hostelería (familia carta: el edge de alérgenos UE 1169/2011).
    ("amenity", "restaurant"): (Sector.RESTAURANTE, "Restaurante"),
    ("amenity", "fast_food"): (Sector.RESTAURANTE, "Comida rápida"),
    ("amenity", "food_court"): (Sector.RESTAURANTE, "Zona de restauración"),
    ("amenity", "cafe"): (Sector.BAR, "Cafetería"),
    ("amenity", "bar"): (Sector.BAR, "Bar"),
    ("amenity", "pub"): (Sector.BAR, "Pub"),
    ("amenity", "ice_cream"): (Sector.BAR, "Heladería"),
    ("shop", "bakery"): (Sector.PANADERIA, "Panadería"),
    ("shop", "pastry"): (Sector.PANADERIA, "Pastelería"),
    ("shop", "confectionery"): (Sector.PANADERIA, "Confitería"),
    ("shop", "ice_cream"): (Sector.BAR, "Heladería"),
    # Salud (familia clínica).
    ("amenity", "pharmacy"): (Sector.FARMACIA, "Farmacia"),
    ("amenity", "dentist"): (Sector.DENTAL, "Clínica dental"),
    ("amenity", "clinic"): (Sector.FISIO, "Clínica"),
    ("amenity", "doctors"): (Sector.FISIO, "Consulta médica"),
    ("amenity", "veterinary"): (Sector.VETERINARIO, "Veterinario"),
    ("healthcare", "physiotherapist"): (Sector.FISIO, "Fisioterapia"),
    ("healthcare", "dentist"): (Sector.DENTAL, "Clínica dental"),
    ("healthcare", "clinic"): (Sector.FISIO, "Clínica"),
    ("healthcare", "pharmacy"): (Sector.FARMACIA, "Farmacia"),
    # Belleza (familia estudio).
    ("shop", "hairdresser"): (Sector.PELUQUERIA, "Peluquería"),
    ("shop", "beauty"): (Sector.ESTETICA, "Centro de estética"),
    ("shop", "massage"): (Sector.ESTETICA, "Masajes"),
    ("shop", "tattoo"): (Sector.ESTETICA, "Estudio de tatuaje"),
    # Oficios y motor (familia industrial).
    ("shop", "car_repair"): (Sector.TALLER, "Taller mecánico"),
    ("shop", "tyres"): (Sector.TALLER, "Neumáticos"),
    ("craft", "electrician"): (Sector.REFORMAS, "Electricista"),
    ("craft", "plumber"): (Sector.REFORMAS, "Fontanería"),
    ("craft", "carpenter"): (Sector.REFORMAS, "Carpintería"),
    ("craft", "painter"): (Sector.REFORMAS, "Pintura"),
    ("craft", "tiler"): (Sector.REFORMAS, "Alicatados"),
    ("craft", "roofer"): (Sector.REFORMAS, "Tejados"),
    ("craft", "metal_construction"): (Sector.REFORMAS, "Carpintería metálica"),
    ("craft", "photographer"): (Sector.AUTONOMO, "Fotógrafo"),
    ("craft", "dressmaker"): (Sector.AUTONOMO, "Modista"),
    ("craft", "shoemaker"): (Sector.AUTONOMO, "Zapatero"),
    # Profesionales (familia autoridad).
    ("office", "lawyer"): (Sector.ASESORIA, "Despacho de abogados"),
    ("office", "accountant"): (Sector.ASESORIA, "Gestoría"),
    ("office", "tax_advisor"): (Sector.ASESORIA, "Asesoría fiscal"),
    ("office", "insurance"): (Sector.ASESORIA, "Correduría de seguros"),
    ("office", "architect"): (Sector.ASESORIA, "Estudio de arquitectura"),
    ("office", "employment_agency"): (Sector.ASESORIA, "Agencia de empleo"),
    ("office", "estate_agent"): (Sector.INMOBILIARIA, "Inmobiliaria"),
    # Deporte (familia gimnasio).
    ("leisure", "fitness_centre"): (Sector.GIMNASIO, "Gimnasio"),
    ("leisure", "sports_centre"): (Sector.GIMNASIO, "Centro deportivo"),
    ("leisure", "dance"): (Sector.GIMNASIO, "Escuela de baile"),
    # Comercio con etiqueta cuidada (el resto de ``shop`` cae al genérico).
    ("shop", "butcher"): (Sector.COMERCIO, "Carnicería"),
    ("shop", "greengrocer"): (Sector.COMERCIO, "Frutería"),
    ("shop", "seafood"): (Sector.COMERCIO, "Pescadería"),
    ("shop", "florist"): (Sector.COMERCIO, "Floristería"),
    ("shop", "optician"): (Sector.COMERCIO, "Óptica"),
    ("shop", "clothes"): (Sector.COMERCIO, "Tienda de ropa"),
    ("shop", "shoes"): (Sector.COMERCIO, "Zapatería"),
    ("shop", "jewelry"): (Sector.COMERCIO, "Joyería"),
    ("shop", "hardware"): (Sector.COMERCIO, "Ferretería"),
    ("shop", "doityourself"): (Sector.COMERCIO, "Bricolaje"),
    ("shop", "convenience"): (Sector.COMERCIO, "Alimentación"),
    ("shop", "variety_store"): (Sector.COMERCIO, "Bazar"),
    ("shop", "herbalist"): (Sector.COMERCIO, "Herbolario"),
    ("shop", "travel_agency"): (Sector.COMERCIO, "Agencia de viajes"),
    ("shop", "supermarket"): (Sector.COMERCIO, "Supermercado"),
    ("shop", "kiosk"): (Sector.COMERCIO, "Quiosco"),
    ("shop", "furniture"): (Sector.COMERCIO, "Muebles"),
    ("shop", "books"): (Sector.COMERCIO, "Librería"),
    ("shop", "stationery"): (Sector.COMERCIO, "Papelería"),
    ("shop", "electronics"): (Sector.COMERCIO, "Electrodomésticos"),
    ("shop", "mobile_phone"): (Sector.COMERCIO, "Telefonía"),
    ("shop", "pet"): (Sector.COMERCIO, "Tienda de mascotas"),
    ("shop", "toys"): (Sector.COMERCIO, "Juguetería"),
    ("shop", "sports"): (Sector.COMERCIO, "Deportes"),
    ("shop", "gift"): (Sector.COMERCIO, "Regalos"),
    ("shop", "alcohol"): (Sector.COMERCIO, "Bodega"),
    ("shop", "garden_centre"): (Sector.COMERCIO, "Jardinería"),
}

# Valor no listado → sector por defecto de la clave (None = no prospectable).
_KEY_DEFAULT: dict[str, Sector | None] = {
    "shop": Sector.COMERCIO,
    "craft": Sector.REFORMAS,
    "amenity": None,
    "office": None,
    "leisure": None,
    "healthcare": None,
}


def sector_for(tags: dict[str, str]) -> Sector | None:
    """Sector Faro para las etiquetas de un POI, o ``None`` si no es prospectable."""
    for key in OSM_KEYS:
        value = tags.get(key)
        if not value:
            continue
        exact = _EXACT.get((key, value))
        if exact is not None:
            return exact[0]
        default = _KEY_DEFAULT.get(key)
        if default is not None:
            return default
    return None


def category_label(tags: dict[str, str]) -> str:
    """Etiqueta legible en castellano de la categoría del POI."""
    for key in OSM_KEYS:
        value = tags.get(key)
        if not value:
            continue
        exact = _EXACT.get((key, value))
        if exact is not None:
            return exact[1]
        if _KEY_DEFAULT.get(key) is not None:
            return value.replace("_", " ").capitalize()
    return "Negocio"


def amenity_values() -> tuple[str, ...]:
    """Valores de ``amenity`` que la taxonomía entiende (para la query Overpass)."""
    return regex_values("amenity")


def regex_values(key: str) -> tuple[str, ...]:
    """Valores listados en la tabla para una clave (claves sin default cerrado)."""
    return tuple(sorted({v for (k, v) in _EXACT if k == key}))
