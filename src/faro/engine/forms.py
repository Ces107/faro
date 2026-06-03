"""Formulario declarativo: el contrato que hace que cada plantilla pida sus datos.

Una ``FormSchema`` es la única fuente de verdad del formulario de una plantilla:
el servidor la expone como JSON y el front la renderiza. Cambiar qué pide una
plantilla es editar su esquema, nunca el HTML del formulario.

El modelo (``BusinessProfile.from_form``) ya es agnóstico del esquema: lee las
claves estándar (``name``, ``services``, ``about``...) y mete cualquier clave
``x_<algo>`` como dato destacado. Por eso un campo nuevo específico de una
plantilla solo tiene que nombrarse ``x_terraza`` para aparecer en la web sin
tocar el parser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FieldKind(str, Enum):
    """Tipo de control del formulario. Determina cómo lo pinta el front."""

    TEXT = "text"
    TEXTAREA = "textarea"
    TEL = "tel"
    EMAIL = "email"
    URL = "url"
    NUMBER = "number"
    SELECT = "select"
    COLOR = "color"
    TOGGLE = "toggle"
    """Sí/No. Se serializa a 'Sí'/'' para que el modelo lo trate como destacado afirmativo."""
    LIST = "list"
    """Varias líneas, una por elemento (textarea que el modelo divide en tupla)."""


@dataclass(frozen=True)
class FormField:
    """Un campo del formulario de una plantilla.

    ``name`` es la clave que viaja al servidor. Si empieza por ``x_`` el modelo
    lo trata como dato destacado por sector (etiqueta = lo que sigue a ``x_``).
    """

    name: str
    label: str
    kind: FieldKind = FieldKind.TEXT
    required: bool = False
    placeholder: str = ""
    help: str = ""
    options: tuple[tuple[str, str], ...] = ()
    """Para SELECT: pares (valor, etiqueta)."""
    rows: int = 3
    """Para TEXTAREA/LIST: alto sugerido."""
    full_width: bool = False
    """Si ocupa toda la fila (True) o puede compartir fila con otro (False)."""

    def as_dict(self) -> dict[str, object]:
        """Forma JSON-serializable para el front."""
        return {
            "name": self.name,
            "label": self.label,
            "kind": self.kind.value,
            "required": self.required,
            "placeholder": self.placeholder,
            "help": self.help,
            "options": [list(o) for o in self.options],
            "rows": self.rows,
            "full_width": self.full_width,
        }


@dataclass(frozen=True)
class FieldGroup:
    """Un bloque de campos con un título (para estructurar el formulario)."""

    title: str
    fields: tuple[FormField, ...]
    description: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "description": self.description,
            "fields": [f.as_dict() for f in self.fields],
        }


@dataclass(frozen=True)
class FormSchema:
    """El formulario completo de una plantilla, en grupos ordenados."""

    groups: tuple[FieldGroup, ...] = field(default_factory=tuple)

    def fields(self) -> tuple[FormField, ...]:
        """Todos los campos, aplanados, en orden."""
        return tuple(f for g in self.groups for f in g.fields)

    def field_names(self) -> frozenset[str]:
        return frozenset(f.name for f in self.fields())

    def as_dict(self) -> dict[str, object]:
        return {"groups": [g.as_dict() for g in self.groups]}


# --- Campos comunes reutilizables por todas las plantillas -------------------
# El núcleo de identidad y contacto que cualquier negocio necesita. Las plantillas
# los componen con sus campos propios (carta, profesionales, antes/después...).


def core_identity() -> FieldGroup:
    """Identidad y contacto: el mínimo imprescindible, igual en toda plantilla."""
    return FieldGroup(
        "Lo básico",
        (
            FormField("name", "Nombre del negocio", required=True, full_width=True,
                      placeholder="Ej. Panadería La Espiga"),
            FormField("city", "Ciudad", required=True, placeholder="Ej. Puerto de Sagunto"),
            FormField("phone", "Teléfono", FieldKind.TEL, required=True, placeholder="961234567"),
            FormField("whatsapp", "WhatsApp (si es otro)", FieldKind.TEL,
                      placeholder="igual que el teléfono"),
            FormField("address", "Dirección", placeholder="Calle y número"),
            FormField("hours", "Horario", placeholder="L-V 9:00-20:00, S 9:00-14:00"),
            FormField("email", "Email", FieldKind.EMAIL),
        ),
    )


def core_offer(label: str = "Servicios o productos (uno por línea)",
               placeholder: str = "Uno por línea") -> FieldGroup:
    """Lo que vende el negocio. La etiqueta la afina cada familia (carta, productos...)."""
    return FieldGroup(
        "Lo que ofrecéis",
        (
            FormField("services", label, FieldKind.LIST, required=True, full_width=True, rows=4,
                      placeholder=placeholder),
        ),
    )


def core_story() -> FieldGroup:
    """La historia del negocio en sus palabras (para no inventar el 'sobre nosotros')."""
    return FieldGroup(
        "Vuestra historia",
        (
            FormField("about", "Contadlo vosotros", FieldKind.TEXTAREA, full_width=True, rows=3,
                      placeholder="Quiénes sois, desde cuándo, qué os hace diferentes. "
                      "Si lo dejáis vacío, se redacta una por vosotros.",
                      help="Lo que escribáis aquí se respeta tal cual, no se inventa."),
            FormField("differentiators", "¿Qué os hace diferentes? (uno por línea)",
                      FieldKind.LIST, full_width=True, rows=3,
                      placeholder="Atendemos sin esperas\nPresupuesto cerrado por escrito"),
            FormField("years", "En activo desde (año)", placeholder="Ej. 2008"),
        ),
    )


def core_trust() -> FieldGroup:
    """Pago, idiomas, redes: refuerzan la confianza sin inventar nada."""
    return FieldGroup(
        "Confianza y contacto",
        (
            FormField("payment_methods", "Formas de pago", placeholder="Efectivo, Tarjeta, Bizum"),
            FormField("parking", "Aparcamiento", placeholder="Fácil aparcar en la zona"),
            FormField("languages", "Idiomas", placeholder="Castellano, Valenciano"),
            FormField("instagram", "Instagram", placeholder="@tunegocio"),
            FormField("facebook", "Facebook", placeholder="enlace o página"),
            FormField("google_review_url", "Enlace para reseñas de Google", FieldKind.URL,
                      full_width=True,
                      placeholder="pega el enlace de tu ficha; si no, el QR lleva a una búsqueda"),
        ),
    )


def core_brand() -> FieldGroup:
    """Marca: color e identidad visual."""
    return FieldGroup(
        "Marca (opcional)",
        (
            FormField("brand_color", "Color de marca", FieldKind.COLOR),
            FormField("slogan", "Eslogan", placeholder="se genera si lo dejas vacío"),
            FormField("photos", "Fotos (una URL por línea)", FieldKind.LIST, full_width=True,
                      rows=2, placeholder="https://... activan la galería"),
            FormField("testimonials", "Opiniones reales (una por línea: «frase | nombre»)",
                      FieldKind.LIST, full_width=True, rows=2,
                      placeholder="Trato excelente | María L. | Cliente"),
        ),
    )
