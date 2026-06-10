"""Modelo del negocio y su validación.

``BusinessProfile`` es el único dato de entrada del generador. Es inmutable y se
valida al construirse: si falta el nombre, el teléfono o algún servicio, falla
pronto y claro en vez de generar un pack a medias.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from faro.menu import MenuCategory, parse_menu

_PHONE_RE = re.compile(r"^[6789]\d{8}$")
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_GOATCOUNTER_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


def _rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _darken(hex_color: str, factor: float = 0.78) -> str:
    """Oscurece un color hex (para el degradado del hero) sin librerías externas."""
    r, g, b = (max(0, min(255, round(c * factor))) for c in _rgb(hex_color))
    return f"#{r:02x}{g:02x}{b:02x}"


def _rel_luminance(hex_color: str) -> float:
    """Luminancia relativa WCAG (con corrección de gamma sRGB)."""

    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(a: str, b: str) -> float:
    """Ratio de contraste WCAG entre dos colores (1 = igual, 21 = blanco/negro)."""
    la, lb = _rel_luminance(a), _rel_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def readable_on_white(color: str, ratio: float = 4.5) -> str:
    """Oscurece el color lo justo para que contraste >= ratio sobre blanco."""
    return readable_on(color, "#ffffff", ratio)


def readable_on(color: str, background: str, ratio: float = 4.5) -> str:
    """Oscurece ``color`` lo justo para que contraste >= ratio sobre ``background``.

    Generaliza ``readable_on_white`` a un fondo arbitrario: los papers de Faro son
    crema/hueso (más oscuros que blanco), así que un accent legible sobre blanco no
    lo es necesariamente sobre el paper real. Solo oscurece (asume fondo claro); para
    fondos oscuros, aclarar es otra estrategia y no se necesita aquí (los accents
    sobre paper oscuro ya contrastan de sobra).
    """
    current = color
    for _ in range(24):
        if contrast_ratio(background, current) >= ratio:
            return current
        current = _darken(current, 0.86)
    return current


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


def _clean_goatcounter(raw: str) -> str:
    """Normaliza el código de GoatCounter a un subdominio seguro.

    Acepta el código pelado ('mibar') o la URL completa de la cuenta
    ('https://mibar.goatcounter.com/count') y devuelve solo el código si es
    válido. Si no lo es, cadena vacía: como el resto de campos opcionales,
    degrada en silencio en vez de romper la generación del pack. El charset se
    restringe a [a-z0-9-] para que sea seguro incrustarlo en el <script> sin
    escapar (lo consume ``seo.analytics_snippet``).
    """
    value = raw.strip().lower()
    if not value:
        return ""
    match = re.match(r"^https?://([a-z0-9-]+)\.goatcounter\.com", value)
    if match:
        value = match.group(1)
    return value if _GOATCOUNTER_RE.match(value) else ""


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
class BeforeAfter:
    """Un par antes/después: dos fotos del mismo trabajo y una descripción."""

    before: str
    after: str
    caption: str = ""


def _parse_before_after(value: str, consent: bool) -> tuple[BeforeAfter, ...]:
    """Parsea líneas 'url_antes | url_después | descripción' en pares antes/después.

    RGPD: las fotos de antes/después suelen mostrar personas (dental, estética).
    Sin la declaración de consentimiento del dueño NO se renderiza la galería —
    proteger al cliente y al negocio prima sobre enseñar resultados.
    """
    if not consent:
        return ()
    out: list[BeforeAfter] = []
    for line in value.replace(";", "\n").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        before, after = parts[0], parts[1]
        if not (before.startswith(("http://", "https://"))
                and after.startswith(("http://", "https://"))):
            continue
        caption = parts[2][:120] if len(parts) > 2 else ""
        out.append(BeforeAfter(before[:300], after[:300], caption))
    return tuple(out[:6])


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
    about: str = ""
    brand_color: str = ""
    photos: tuple[str, ...] = ()
    testimonials: tuple[Testimonial, ...] = ()
    canonical_url: str = ""
    # Datos reales que antes se inventaban (todos opcionales, degradan a vacío).
    years: str = ""  # años de experiencia o "desde 1998"
    differentiators: tuple[str, ...] = ()  # qué os hace diferentes (sustituye props genéricas)
    instagram: str = ""
    facebook: str = ""
    payment_methods: tuple[str, ...] = ()  # Efectivo, Tarjeta, Bizum...
    parking: str = ""
    languages: tuple[str, ...] = ()
    booking_style: str = ""  # "", cita, sin_cita, reserva
    extras: tuple[tuple[str, str], ...] = ()  # hechos por sector: (etiqueta, valor)
    # Funcionalidades de conversión (todas opcionales, nunca inventadas).
    google_rating: str = ""  # valoración real 1-5 (badge); vacío = no se muestra
    google_reviews_count: str = ""  # nº de reseñas reales
    google_profile_url: str = ""  # ficha de Google (verifica el rating; alimenta sameAs)
    booking_url: str = ""  # enlace externo de reserva/cita (Booksy, Doctoralia, TheFork...)
    offer_title: str = ""  # gancho de oferta
    offer_details: str = ""  # condiciones de la oferta
    offer_end_date: str = ""  # YYYY-MM-DD; la oferta se auto-oculta tras esta fecha
    delivery_links: tuple[str, ...] = ()  # enlaces de pedido (Glovo, Just Eat...)
    service_area: str = ""  # zonas donde trabaja (negocios móviles)
    credentials: tuple[str, ...] = ()  # certificaciones/licencias/colegiación reales
    menu: tuple[MenuCategory, ...] = ()  # carta estructurada: categorías + precios + alérgenos
    before_after: tuple[BeforeAfter, ...] = ()  # galería antes/después (con consentimiento RGPD)
    registration_number: str = ""  # nº de registro sanitario u oficial (publicidad sanitaria)
    analytics_goatcounter: str = ""  # código GoatCounter: contador de visitas sin cookies (RGPD)

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
        object.__setattr__(self, "about", self.about.strip()[:600])
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
        object.__setattr__(self, "years", self.years.strip()[:20])
        object.__setattr__(self, "instagram", self.instagram.strip()[:120])
        object.__setattr__(self, "facebook", self.facebook.strip()[:200])
        object.__setattr__(self, "parking", self.parking.strip()[:60])
        object.__setattr__(self, "booking_style", self.booking_style.strip()[:20])
        object.__setattr__(
            self, "differentiators", tuple(d[:90] for d in self.differentiators[:3])
        )
        object.__setattr__(
            self, "payment_methods", tuple(p[:30] for p in self.payment_methods[:6])
        )
        object.__setattr__(self, "languages", tuple(lang[:30] for lang in self.languages[:5]))
        object.__setattr__(
            self,
            "extras",
            tuple((k[:40], v[:120]) for k, v in self.extras if k and v)[:12],
        )
        object.__setattr__(self, "google_rating", self.google_rating.strip()[:3])
        object.__setattr__(self, "google_reviews_count", self.google_reviews_count.strip()[:7])
        gp = self.google_profile_url.strip()
        object.__setattr__(self, "google_profile_url", gp[:200] if gp.startswith("http") else "")
        bk = self.booking_url.strip()
        object.__setattr__(self, "booking_url", bk[:200] if bk.startswith("http") else "")
        object.__setattr__(self, "offer_title", self.offer_title.strip()[:80])
        object.__setattr__(self, "offer_details", self.offer_details.strip()[:200])
        object.__setattr__(self, "offer_end_date", self.offer_end_date.strip()[:10])
        object.__setattr__(
            self,
            "delivery_links",
            tuple(d.strip() for d in self.delivery_links if d.strip().startswith("http"))[:4],
        )
        object.__setattr__(self, "service_area", self.service_area.strip()[:160])
        object.__setattr__(self, "credentials", tuple(c[:90] for c in self.credentials[:6]))
        object.__setattr__(
            self, "registration_number", self.registration_number.strip()[:80]
        )
        object.__setattr__(
            self, "analytics_goatcounter", _clean_goatcounter(self.analytics_goatcounter)
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
        """Color de texto (#fff o casi negro) con MÁS contraste WCAG sobre el color de marca."""
        if contrast_ratio("#ffffff", self.color) >= contrast_ratio("#0f172a", self.color):
            return "#ffffff"
        return "#0f172a"

    @property
    def accent(self) -> str:
        """Color de marca legible como texto sobre blanco (eyebrows, cifras, chips). WCAG >=4.5."""
        return readable_on_white(self.color)

    @property
    def hero_start(self) -> str:
        """Inicio del degradado del hero, oscurecido lo justo para texto blanco legible (WCAG)."""
        return readable_on_white(self.color)

    @property
    def hero_end(self) -> str:
        """Final del degradado del hero (más oscuro que el inicio)."""
        return _darken(self.hero_start, 0.8)

    @property
    def initials(self) -> str:
        """Iniciales para el logo del hero (hasta 2 letras de las primeras palabras)."""
        words = [w for w in self.name.split() if w[:1].isalnum()]
        letters = "".join(w[0] for w in words[:2]) or self.name[:1]
        return letters.upper()

    @property
    def rating(self) -> float | None:
        """Valoración de Google como número 1-5, o None si no es válida/no hay."""
        raw = self.google_rating.replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            return None
        return value if 0 < value <= 5 else None

    @property
    def rating_stars(self) -> str:
        """Estrellas llenas/vacías para el rating real (★/☆). '' si no hay rating."""
        r = self.rating
        if r is None:
            return ""
        full = int(round(r))
        return "★" * full + "☆" * (5 - full)

    @property
    def offer_active(self) -> bool:
        """Hay oferta que mostrar (tiene título; la caducidad la gestiona el JS)."""
        return bool(self.offer_title)

    @property
    def phone_e164(self) -> str:
        """Teléfono en formato internacional (+34...) para enlaces wa.me/tel."""
        digits = self.phone
        return digits if digits.startswith("34") else f"34{digits}"

    @property
    def whatsapp_e164(self) -> str:
        digits = self.whatsapp
        return digits if digits.startswith("34") else f"34{digits}"

    @property
    def whatsapp_looks_mobile(self) -> bool:
        """¿El número del botón de WhatsApp parece un móvil español (6xx/7xx)?

        Un fijo (8xx/9xx) PUEDE tener WhatsApp Business, pero lo normal es que
        no: el botón quedaría muerto en silencio. La consola y el LEEME avisan
        al operador para que lo confirme con el dueño antes de entregar.
        """
        national = self.whatsapp_e164.removeprefix("34")
        return national.startswith(("6", "7"))

    @classmethod
    def from_form(cls, data: dict[str, str]) -> BusinessProfile:
        """Construye un perfil desde el formulario web (campos de texto plano)."""

        def split_lines(value: str) -> tuple[str, ...]:
            return tuple(s.strip() for s in value.replace(";", "\n").splitlines() if s.strip())

        def split_commas(value: str) -> tuple[str, ...]:
            return tuple(s.strip() for s in value.split(",") if s.strip())

        # Hechos por sector. Dos vías: claves "x_<etiqueta>" (formulario dinámico)
        # y un campo "destacados" con líneas "Etiqueta: valor".
        extras: list[tuple[str, str]] = [
            (k[2:].replace("_", " ").strip().capitalize(), v.strip())
            for k, v in data.items()
            if k.startswith("x_") and v.strip()
        ]
        for line in split_lines(data.get("destacados", "")):
            label, sep, value = line.partition(":")
            if sep and label.strip() and value.strip():
                extras.append((label.strip(), value.strip()))

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
            about=data.get("about", "").strip(),
            brand_color=data.get("brand_color", "").strip(),
            photos=split_lines(data.get("photos", "")),
            testimonials=_parse_testimonials(data.get("testimonials", "")),
            canonical_url=data.get("canonical_url", "").strip(),
            years=data.get("years", "").strip(),
            differentiators=split_lines(data.get("differentiators", "")),
            instagram=data.get("instagram", "").strip(),
            facebook=data.get("facebook", "").strip(),
            payment_methods=split_commas(data.get("payment_methods", "")),
            parking=data.get("parking", "").strip(),
            languages=split_commas(data.get("languages", "")),
            booking_style=data.get("booking_style", "").strip(),
            extras=tuple(extras),
            google_rating=data.get("google_rating", "").strip(),
            google_reviews_count=data.get("google_reviews_count", "").strip(),
            google_profile_url=data.get("google_profile_url", "").strip(),
            booking_url=data.get("booking_url", "").strip(),
            offer_title=data.get("offer_title", "").strip(),
            offer_details=data.get("offer_details", "").strip(),
            offer_end_date=data.get("offer_end_date", "").strip(),
            delivery_links=split_lines(data.get("delivery_links", "")),
            service_area=data.get("service_area", "").strip(),
            credentials=split_lines(data.get("credentials", "")),
            registration_number=data.get("registration_number", "").strip(),
            analytics_goatcounter=data.get("analytics_goatcounter", "").strip(),
            menu=parse_menu(data.get("menu", "")),
            before_after=_parse_before_after(
                data.get("before_after", ""),
                data.get("before_after_consent", "").strip().lower()
                in ("sí", "si", "yes", "true", "on"),
            ),
        )
