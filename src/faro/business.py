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
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _darken(hex_color: str, factor: float = 0.78) -> str:
    """Oscurece un color hex (para el degradado del hero) sin librerías externas."""
    r, g, b = (max(0, min(255, round(c * factor))) for c in _rgb(hex_color))
    return f"#{r:02x}{g:02x}{b:02x}"


def _luminance(hex_color: str) -> float:
    """Luminancia perceptual aproximada (0 = negro, 1 = blanco)."""
    r, g, b = _rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def mix_hex(base: str, other: str, pct: float) -> str:
    """Mezcla ``base`` con ``other`` (RGB lineal). pct = proporción de base (0..1).

    Aproximación del ``color-mix`` de CSS para los navegadores que no lo soportan
    (se inyecta como fallback). No hace falta exactitud oklab para un fallback.
    """
    br, bg, bb = _rgb(base)
    orr, og, ob = _rgb(other)
    r = round(br * pct + orr * (1 - pct))
    g = round(bg * pct + og * (1 - pct))
    b = round(bb * pct + ob * (1 - pct))
    return f"#{r:02x}{g:02x}{b:02x}"


# Por encima de esta luminancia, el texto blanco del hero no contrasta y hay que
# oscurecer el fondo del degradado de forma agresiva.
_LIGHT_THRESHOLD = 0.6


class Sector(str, Enum):
    """Tipo de negocio. Determina el tema visual y los textos por defecto."""

    DENTAL = "dental"
    FISIO = "fisio"
    VETERINARIO = "veterinario"
    PELUQUERIA = "peluqueria"
    ESTETICA = "estetica"
    RESTAURANTE = "restaurante"
    BAR = "bar"
    COMERCIO = "comercio"
    PANADERIA = "panaderia"
    TALLER = "taller"
    GIMNASIO = "gimnasio"
    FARMACIA = "farmacia"
    ASESORIA = "asesoria"
    INMOBILIARIA = "inmobiliaria"
    REFORMAS = "reformas"
    AUTONOMO = "autonomo"
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
    noun: str
    """Forma con artículo para frases tipo «X es {noun} en {ciudad}»."""


_THEMES: dict[Sector, SectorTheme] = {
    Sector.DENTAL: SectorTheme("Clínica dental", "🦷", "#0ea5e9", "#0369a1",
        "Tu sonrisa en las mejores manos", "Pedir cita", "una clínica dental"),
    Sector.FISIO: SectorTheme("Fisioterapia", "💪", "#10b981", "#047857",
        "Recupérate y vuelve a moverte sin dolor", "Pedir cita", "un centro de fisioterapia"),
    Sector.VETERINARIO: SectorTheme("Clínica veterinaria", "🐾", "#f59e0b", "#b45309",
        "El cuidado que tu mascota merece", "Pedir cita", "una clínica veterinaria"),
    Sector.PELUQUERIA: SectorTheme("Peluquería", "💇", "#ec4899", "#be185d",
        "Tu mejor versión empieza aquí", "Reservar", "una peluquería"),
    Sector.ESTETICA: SectorTheme("Centro de estética", "✨", "#a855f7", "#7e22ce",
        "Cuídate. Te lo mereces", "Reservar", "un centro de estética"),
    Sector.RESTAURANTE: SectorTheme("Restaurante", "🍽️", "#ef4444", "#b91c1c",
        "Buena comida, cerca de ti", "Reservar mesa", "un restaurante"),
    Sector.BAR: SectorTheme("Bar / Cafetería", "☕", "#d97706", "#92400e",
        "Tu sitio para un buen rato", "Ver carta", "un bar"),
    Sector.COMERCIO: SectorTheme("Tienda", "🛍️", "#db2777", "#9d174d",
        "Lo que buscas, al lado de casa", "Contactar", "una tienda"),
    Sector.PANADERIA: SectorTheme("Panadería", "🥖", "#ca8a04", "#854d0e",
        "Pan recién hecho cada día", "Contactar", "una panadería"),
    Sector.TALLER: SectorTheme("Taller mecánico", "🔧", "#3b82f6", "#1d4ed8",
        "Tu coche, en buenas manos", "Pedir cita", "un taller mecánico"),
    Sector.GIMNASIO: SectorTheme("Gimnasio", "🏋️", "#16a34a", "#15803d",
        "Ponte en forma a tu ritmo", "Apúntate", "un gimnasio"),
    Sector.FARMACIA: SectorTheme("Farmacia", "💊", "#059669", "#047857",
        "Tu salud, bien atendida", "Contactar", "una farmacia"),
    Sector.ASESORIA: SectorTheme("Asesoría", "📊", "#0d9488", "#0f766e",
        "Tu negocio, sin preocupaciones fiscales", "Consultar", "una asesoría"),
    Sector.INMOBILIARIA: SectorTheme("Inmobiliaria", "🏠", "#0891b2", "#0e7490",
        "Encuentra tu próximo hogar", "Ver propiedades", "una inmobiliaria"),
    Sector.REFORMAS: SectorTheme("Reformas", "🛠️", "#ea580c", "#c2410c",
        "Transformamos tu espacio", "Pedir presupuesto", "una empresa de reformas"),
    Sector.AUTONOMO: SectorTheme("Servicios profesionales", "🧰", "#4f46e5", "#3730a3",
        "El servicio que necesitas, cerca", "Contactar", "un profesional"),
    Sector.OTRO: SectorTheme("Negocio", "📍", "#2563eb", "#1d4ed8",
        "Cerca de ti, cuando lo necesitas", "Contactar", "un negocio"),
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
class Testimonial:
    """Una reseña real dictada por el dueño. Nunca se inventa."""

    quote: str
    author: str
    role: str = ""


def _parse_testimonials(value: str) -> tuple[Testimonial, ...]:
    """Parsea líneas 'cita | autor' (o 'cita | autor | rol') en testimonios."""
    out: list[Testimonial] = []
    for line in value.replace(";", "\n").splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        quote = parts[0]
        if not quote:
            continue
        author = parts[1] if len(parts) > 1 and parts[1] else "Cliente"
        role = parts[2] if len(parts) > 2 else ""
        out.append(Testimonial(quote, author, role))
    return tuple(out)


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
    cif: str = ""
    google_review_url: str = ""
    highlights: tuple[str, ...] = ()
    slogan: str = ""
    brand_color: str = ""
    photos: tuple[str, ...] = ()
    testimonials: tuple[Testimonial, ...] = ()
    canonical_url: str = ""

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
        if self.brand_color and not _HEX_RE.match(self.brand_color):
            raise ValueError(
                f"Color de marca no válido: {self.brand_color!r} (usa formato #RRGGBB)."
            )
        # Truncado de longitudes: un texto desmedido rompería el diseño de la web
        # en plena demo. Truncar (en vez de rechazar) no corta la venta.
        object.__setattr__(self, "name", self.name.strip()[:60])
        object.__setattr__(self, "city", self.city.strip()[:50])
        object.__setattr__(self, "address", self.address.strip()[:120])
        object.__setattr__(self, "slogan", self.slogan.strip()[:90])
        object.__setattr__(self, "hours", self.hours.strip()[:120])
        object.__setattr__(self, "email", self.email.strip()[:120])
        object.__setattr__(self, "services", tuple(s[:70] for s in self.services[:12]))
        object.__setattr__(self, "highlights", tuple(h[:90] for h in self.highlights[:6]))
        object.__setattr__(
            self,
            "photos",
            tuple(p.strip() for p in self.photos if p.strip().startswith(("http://", "https://")))[:9],
        )
        object.__setattr__(
            self,
            "testimonials",
            tuple(
                Testimonial(t.quote[:280], t.author[:60], t.role[:60])
                for t in self.testimonials[:3]
            ),
        )
        canonical = self.canonical_url.strip()
        object.__setattr__(
            self, "canonical_url", canonical[:200] if canonical.startswith("http") else ""
        )

    @property
    def theme(self) -> SectorTheme:
        return theme_for(self.sector)

    @property
    def color(self) -> str:
        """Color de marca: el elegido por el negocio o, si no, el del sector."""
        return self.brand_color or self.theme.color

    @property
    def on_brand(self) -> str:
        """Color de texto legible (#fff o casi negro) sobre el color de marca (WCAG)."""
        return "#ffffff" if _luminance(self.color) < 0.55 else "#0f172a"

    @property
    def accent(self) -> str:
        """Color de acento para el degradado (derivado del color de marca o del sector)."""
        return _darken(self.brand_color) if self.brand_color else self.theme.accent

    @property
    def hero_start(self) -> str:
        """Color inicial del degradado del hero, garantizando contraste con texto blanco."""
        base = self.color
        return _darken(base, 0.55) if _luminance(base) > _LIGHT_THRESHOLD else base

    @property
    def hero_end(self) -> str:
        """Color final del degradado del hero (siempre más oscuro que el inicial)."""
        base = self.color
        return _darken(base, 0.4) if _luminance(base) > _LIGHT_THRESHOLD else self.accent

    @property
    def initials(self) -> str:
        """Iniciales para el logo del hero (hasta 2 letras de las primeras palabras)."""
        words = [w for w in self.name.split() if w[:1].isalnum()]
        letters = "".join(w[0] for w in words[:2]) or self.name[:1]
        return letters.upper()

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
            cif=data.get("cif", "").strip(),
            google_review_url=data.get("google_review_url", "").strip(),
            highlights=split_lines(data.get("highlights", "")),
            slogan=data.get("slogan", "").strip(),
            brand_color=data.get("brand_color", "").strip(),
            photos=split_lines(data.get("photos", "")),
            testimonials=_parse_testimonials(data.get("testimonials", "")),
            canonical_url=data.get("canonical_url", "").strip(),
        )
