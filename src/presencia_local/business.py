"""Modelo del negocio y su validación.

``BusinessProfile`` es el único dato de entrada del generador. Es inmutable y se
valida al construirse: si falta el nombre, el teléfono o algún servicio, falla
pronto y claro en vez de generar un pack a medias.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

_PHONE_RE = re.compile(r"^[6789]\d{8}$")


class Sector(str, Enum):
    """Tipo de negocio. Determina el tema visual y los textos por defecto."""

    DENTAL = "dental"
    FISIO = "fisio"
    VETERINARIO = "veterinario"
    PELUQUERIA = "peluqueria"
    ESTETICA = "estetica"
    RESTAURANTE = "restaurante"
    TALLER = "taller"
    ASESORIA = "asesoria"
    INMOBILIARIA = "inmobiliaria"
    REFORMAS = "reformas"
    OTRO = "otro"


@dataclass(frozen=True)
class SectorTheme:
    """Apariencia y vocabulario por defecto de un sector."""

    label: str
    emoji: str
    color: str
    accent: str
    headline: str
    cta: str


_THEMES: dict[Sector, SectorTheme] = {
    Sector.DENTAL: SectorTheme("Clínica dental", "🦷", "#0ea5e9", "#0369a1",
        "Tu sonrisa en las mejores manos", "Pedir cita"),
    Sector.FISIO: SectorTheme("Fisioterapia", "💪", "#10b981", "#047857",
        "Recupérate y vuelve a moverte sin dolor", "Pedir cita"),
    Sector.VETERINARIO: SectorTheme("Clínica veterinaria", "🐾", "#f59e0b", "#b45309",
        "El cuidado que tu mascota merece", "Pedir cita"),
    Sector.PELUQUERIA: SectorTheme("Peluquería", "💇", "#ec4899", "#be185d",
        "Tu mejor versión empieza aquí", "Reservar"),
    Sector.ESTETICA: SectorTheme("Centro de estética", "✨", "#a855f7", "#7e22ce",
        "Cuídate. Te lo mereces", "Reservar"),
    Sector.RESTAURANTE: SectorTheme("Restaurante", "🍽️", "#ef4444", "#b91c1c",
        "Buena comida, cerca de ti", "Reservar mesa"),
    Sector.TALLER: SectorTheme("Taller mecánico", "🔧", "#3b82f6", "#1d4ed8",
        "Tu coche, en buenas manos", "Pedir cita"),
    Sector.ASESORIA: SectorTheme("Asesoría", "📊", "#0d9488", "#0f766e",
        "Tu negocio, sin preocupaciones fiscales", "Consultar"),
    Sector.INMOBILIARIA: SectorTheme("Inmobiliaria", "🏠", "#0891b2", "#0e7490",
        "Encuentra tu próximo hogar", "Ver propiedades"),
    Sector.REFORMAS: SectorTheme("Reformas", "🛠️", "#ea580c", "#c2410c",
        "Transformamos tu espacio", "Pedir presupuesto"),
    Sector.OTRO: SectorTheme("Negocio", "📍", "#2563eb", "#1d4ed8",
        "Cerca de ti, cuando lo necesitas", "Contactar"),
}


def theme_for(sector: Sector) -> SectorTheme:
    return _THEMES[sector]


def _clean_phone(raw: str) -> str:
    """Normaliza a 9 dígitos nacionales (quita espacios, símbolos y el prefijo 34)."""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("34"):
        digits = digits[2:]
    return digits


@dataclass(frozen=True)
class BusinessProfile:
    """Datos de un negocio local. Inmutable y validado."""

    name: str
    sector: Sector
    city: str
    phone: str
    services: tuple[str, ...]
    whatsapp: str = ""
    hours: str = ""
    address: str = ""
    email: str = ""
    google_review_url: str = ""
    highlights: tuple[str, ...] = ()
    slogan: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("El nombre del negocio es obligatorio.")
        if not self.city.strip():
            raise ValueError("La ciudad es obligatoria.")
        phone = _clean_phone(self.phone)
        if not _PHONE_RE.match(phone):
            raise ValueError(f"Teléfono no válido: {self.phone!r} (debe ser un número español).")
        object.__setattr__(self, "phone", phone)
        if not self.services:
            raise ValueError("Indica al menos un servicio.")
        # WhatsApp por defecto = teléfono principal.
        wa = _clean_phone(self.whatsapp) if self.whatsapp else phone
        object.__setattr__(self, "whatsapp", wa)

    @property
    def theme(self) -> SectorTheme:
        return theme_for(self.sector)

    @property
    def phone_e164(self) -> str:
        """Teléfono en formato internacional (+34...) para enlaces wa.me/tel."""
        digits = self.phone
        return digits if digits.startswith("34") else f"34{digits}"

    @property
    def whatsapp_e164(self) -> str:
        digits = self.whatsapp
        return digits if digits.startswith("34") else f"34{digits}"

    @classmethod
    def from_form(cls, data: dict[str, str]) -> BusinessProfile:
        """Construye un perfil desde el formulario web (campos de texto plano)."""

        def split_lines(value: str) -> tuple[str, ...]:
            return tuple(s.strip() for s in value.replace(";", "\n").splitlines() if s.strip())

        return cls(
            name=data.get("name", "").strip(),
            sector=Sector(data.get("sector", "otro")),
            city=data.get("city", "").strip(),
            phone=data.get("phone", "").strip(),
            whatsapp=data.get("whatsapp", "").strip(),
            services=split_lines(data.get("services", "")),
            hours=data.get("hours", "").strip(),
            address=data.get("address", "").strip(),
            email=data.get("email", "").strip(),
            google_review_url=data.get("google_review_url", "").strip(),
            highlights=split_lines(data.get("highlights", "")),
            slogan=data.get("slogan", "").strip(),
        )
