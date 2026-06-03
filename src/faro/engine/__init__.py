"""Motor de plantillas de Faro.

Separa el *qué* (datos del negocio, en ``faro.business``) del *cómo se ve*:

- ``forms``: el formulario es declarativo. Cada plantilla declara su ``FormSchema``
  (qué campos pide). El formulario web se genera desde ese esquema, así que el
  formulario es DISTINTO según la plantilla, sin escribir HTML a mano.
- ``design``: ``DesignTokens`` describe la identidad visual de una familia
  (tipografía, color, formas, densidad, tratamiento del hero) y la traduce a CSS.
- ``spec``: ``TemplateSpec`` compone una plantilla = familia de bloques + tokens
  + esquema de formulario + sectores que cubre.
- ``registry``: el catálogo de plantillas y la resolución por sector o por id.

Añadir una plantilla nueva = declarar un ``TemplateSpec`` (no tocar el chasis).
"""

from __future__ import annotations

from faro.engine.forms import FieldKind, FormField, FormSchema

__all__ = ["FieldKind", "FormField", "FormSchema"]
