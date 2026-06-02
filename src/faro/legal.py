"""Aviso legal mínimo para la web generada.

En España, una web de un negocio que ofrece servicios debe identificar a su
titular (LSSI-CE, art. 10). Generamos una página de aviso legal con los datos que
tenemos del negocio y un hueco para el NIF, que el dueño completa. No es un
dictamen jurídico: es el mínimo razonable, y el dueño lo revisa con su asesor.
"""

from __future__ import annotations

import html

from faro.business import BusinessProfile

_NIF_PLACEHOLDER = "[NIF del titular - a completar]"


def legal_notice_html(business: BusinessProfile) -> str:
    """Página de aviso legal autocontenida para acompañar a la web."""
    name = html.escape(business.name)
    raw_address = f"{business.address}, {business.city}" if business.address else business.city
    address = html.escape(raw_address)
    email = f"<li>Email: {html.escape(business.email)}</li>" if business.email else ""
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Aviso legal · {name}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 0 auto; padding: 40px 20px;
         color: #1f2937; line-height: 1.6; }}
  h1 {{ font-size: 26px; }} h2 {{ font-size: 18px; margin-top: 28px; }}
  a {{ color: {business.color}; }}
</style></head>
<body>
  <h1>Aviso legal</h1>

  <h2>Identificación del titular</h2>
  <ul>
    <li>Titular: {name}</li>
    <li>NIF: {_NIF_PLACEHOLDER}</li>
    <li>Domicilio: {address}</li>
    <li>Teléfono: {business.phone}</li>
    {email}
  </ul>

  <h2>Objeto</h2>
  <p>Este sitio web tiene como finalidad informar sobre los servicios de
  {name} y facilitar el contacto con el negocio.</p>

  <h2>Condiciones de uso</h2>
  <p>El acceso a este sitio es gratuito. El usuario se compromete a hacer un uso
  adecuado de los contenidos y a no emplearlos para actividades ilícitas.</p>

  <h2>Protección de datos</h2>
  <p>Si contactas con el negocio (por ejemplo, por WhatsApp o teléfono), los datos
  que facilites se usan únicamente para atender tu solicitud y no se ceden a
  terceros. Puedes ejercer tus derechos de acceso, rectificación y supresión
  escribiendo al titular en los datos de contacto indicados arriba.</p>

  <h2>Propiedad intelectual</h2>
  <p>Los contenidos de este sitio pertenecen a {name} o se usan con
  autorización. No está permitida su reproducción sin consentimiento.</p>

  <p style="margin-top:32px;font-size:13px;color:#6b7280">Este aviso es un modelo
  de partida. Revísalo con tu asesor y completa el NIF antes de publicarlo.</p>
</body></html>
"""
