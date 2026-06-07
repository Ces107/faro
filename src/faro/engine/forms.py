"""Formulario declarativo: el contrato que hace que cada plantilla pida sus datos.

Una ``FormSchema`` es la única fuente de verdad del formulario de una plantilla:
el servidor la expone como JSON y el front la renderiza. Cambiar qué pide una
plantilla es editar su esquema, nunca el HTML del formulario.

El modelo (``BusinessProfile.from_form``) ya es agnóstico del esquema: lee las
claves estándar (``name``, ``services``, ``about``...) y mete cualquier clave
``x_<algo>`` como dato destacado (etiqueta = ``Algo``, capitalizada). Por eso un
campo nuevo específico de una plantilla solo tiene que nombrarse ``x_terraza``
para aparecer en la web (chip si es Sí/No, fila de ficha si lleva valor) sin
tocar el parser.

Cada familia visual compone su propio esquema con ``family_schema``: el núcleo
común (identidad, historia, confianza, conversión, marca) más una etiqueta de
oferta propia y un grupo de campos ``x_`` específicos de su sector. Así el
formulario es DISTINTO según la plantilla (lo que pide una carta no es lo que
pide una clínica) sin que el parser ni el render sepan de familias.
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


def core_conversion() -> FieldGroup:
    """Palancas de conversión reales: rating de Google, reserva, oferta, credenciales.

    Todo opcional y nunca inventado: un campo vacío no pinta su bloque.
    """
    return FieldGroup(
        "Más conversión (opcional)",
        (
            FormField("google_rating", "Valoración en Google (1-5)", FieldKind.NUMBER,
                      placeholder="4.8", help="Solo si es real. Nunca se inventa."),
            FormField("google_reviews_count", "Nº de reseñas", FieldKind.NUMBER, placeholder="127"),
            FormField("google_profile_url", "Ficha de Google", FieldKind.URL, full_width=True,
                      placeholder="enlace a tu ficha (verifica la valoración)"),
            FormField("booking_url", "Enlace de reserva / cita online", FieldKind.URL,
                      full_width=True,
                      placeholder="Booksy, Doctoralia, TheFork... (botón de reserva)"),
            FormField("offer_title", "Oferta (título)", placeholder="2x1 en cafés de 8 a 10h"),
            FormField("offer_end_date", "La oferta termina el", placeholder="2026-07-31"),
            FormField("offer_details", "Condiciones de la oferta", full_width=True,
                      placeholder="de lunes a viernes, no acumulable"),
            FormField("delivery_links", "Pedido a domicilio (una URL por línea)", FieldKind.LIST,
                      full_width=True, rows=2, placeholder="https://glovoapp.com/...\nhttps://just-eat.es/..."),
            FormField("service_area", "Zonas donde trabajáis", full_width=True,
                      placeholder="Sagunto, Puerto de Sagunto, Canet, Almenara"),
            FormField("credentials", "Certificaciones / licencias / colegiación (una por línea)",
                      FieldKind.LIST, full_width=True, rows=2,
                      placeholder="Colegiado nº 1234\nSeguro de responsabilidad civil"),
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


# --- Esquema por familia -----------------------------------------------------
# Cada familia visual pide lo que su sector necesita. El núcleo común no cambia;
# cambian la etiqueta de "lo que ofrecéis" y un grupo de campos x_ propios. Los
# campos x_ los renderiza el modelo sin saber de familias (chip afirmativo si es
# Sí/No, fila de ficha si llevan valor), así que añadir una familia es datos, no
# fontanería.


def family_schema(
    offer_label: str, offer_placeholder: str, extra: FieldGroup
) -> FormSchema:
    """Esquema completo de una familia: núcleo común + su oferta + sus detalles."""
    return FormSchema(
        (
            core_identity(),
            core_offer(offer_label, offer_placeholder),
            extra,
            core_story(),
            core_trust(),
            core_conversion(),
            core_brand(),
        )
    )


def carta_extras() -> FieldGroup:
    """Gastronomía: carta con precios y alérgenos + terraza, para llevar, dietas."""
    return FieldGroup(
        "Detalles de la carta (opcional)",
        (
            FormField(
                "menu", "Carta con precios y alérgenos", FieldKind.TEXTAREA,
                full_width=True, rows=8,
                placeholder=("Entrantes:\n"
                             "Croquetas caseras — 6,50 (gluten, lácteos)\n"
                             "Ensalada de la casa — 7,00\n"
                             "Principales:\n"
                             "Paella valenciana — 14,00 (gluten, crustáceos, pescado)\n"
                             "Postres:\n"
                             "Flan de la abuela — 4,00 (huevos, lácteos)"),
                help=("Una categoría por línea acabada en «:». Un plato por línea: "
                      "Nombre — precio (alérgenos). El precio y los alérgenos son "
                      "opcionales. Alérgenos según el Reglamento UE 1169/2011."),
            ),
            FormField("x_terraza", "Terraza", FieldKind.TOGGLE),
            FormField("x_para_llevar", "Comida para llevar", FieldKind.TOGGLE),
            FormField("x_opciones", "Opciones dietéticas", full_width=True,
                      placeholder="Vegano, sin gluten, sin lactosa"),
        ),
    )


def before_after_fields() -> tuple[FormField, ...]:
    """Galería antes/después + la casilla de consentimiento RGPD obligatoria.

    Sin marcar el consentimiento, la galería no se renderiza (el modelo la
    descarta). Reutilizada por las familias cuyo sector enseña resultados:
    estética, reformas, dental.
    """
    return (
        FormField(
            "before_after", "Galería antes / después", FieldKind.LIST,
            full_width=True, rows=4,
            placeholder=("https://...antes.jpg | https://...despues.jpg | Blanqueamiento dental\n"
                         "https://...antes2.jpg | https://...despues2.jpg | Reforma de cocina"),
            help="Una línea por trabajo: URL antes | URL después | descripción (opcional).",
        ),
        FormField(
            "before_after_consent",
            "Confirmo que tengo el consentimiento de las personas que aparecen (RGPD)",
            FieldKind.TOGGLE, full_width=True,
            help="Obligatorio para mostrar la galería. Sin esta confirmación no se publica.",
        ),
    )


def clinica_extras() -> FieldGroup:
    """Salud: seguros, primera visita, urgencias + galería antes/después (dental)."""
    return FieldGroup(
        "Detalles de la consulta (opcional)",
        (
            FormField("x_seguros", "Seguros que aceptáis", full_width=True,
                      placeholder="Adeslas, Sanitas, DKV, Asisa"),
            FormField("x_primera_visita", "Primera visita",
                      placeholder="Valoración sin coste"),
            FormField("x_urgencias", "Atendemos urgencias", FieldKind.TOGGLE),
            *before_after_fields(),
        ),
    )


def autoridad_extras() -> FieldGroup:
    """Despacho profesional: primera consulta, experiencia, modalidad."""
    return FieldGroup(
        "Detalles del despacho (opcional)",
        (
            FormField("x_primera_consulta", "Primera consulta sin compromiso",
                      FieldKind.TOGGLE),
            FormField("x_experiencia", "Experiencia",
                      placeholder="+20 años, +500 casos"),
            FormField("x_modalidad", "Modalidad",
                      placeholder="Presencial y online"),
        ),
    )


def industrial_extras() -> FieldGroup:
    """Oficios: presupuesto, urgencias, garantía + galería antes/después (reformas)."""
    return FieldGroup(
        "Detalles del servicio (opcional)",
        (
            FormField("x_presupuesto", "Presupuesto sin compromiso", FieldKind.TOGGLE),
            FormField("x_urgencias", "Urgencias",
                      placeholder="24h, fines de semana"),
            FormField("x_garantia", "Garantía",
                      placeholder="2 años en la mano de obra"),
            *before_after_fields(),
        ),
    )


def estudio_extras() -> FieldGroup:
    """Belleza: cita previa, marcas + galería antes/después (estética)."""
    return FieldGroup(
        "Detalles del estudio (opcional)",
        (
            FormField("x_cita_previa", "Solo con cita previa", FieldKind.TOGGLE),
            FormField("x_marcas", "Marcas que trabajáis", full_width=True,
                      placeholder="L'Oréal, Wella, Olaplex"),
            *before_after_fields(),
        ),
    )


def gimnasio_extras() -> FieldGroup:
    """Gimnasio: clase de prueba, cuotas, horario de acceso."""
    return FieldGroup(
        "Detalles del centro (opcional)",
        (
            FormField("x_clase_prueba", "Clase de prueba gratis", FieldKind.TOGGLE),
            FormField("x_cuotas", "Cuotas",
                      placeholder="Desde 29 €/mes, sin permanencia"),
            FormField("x_acceso", "Horario de acceso",
                      placeholder="L-D 7:00-23:00"),
        ),
    )
