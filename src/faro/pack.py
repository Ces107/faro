"""El pack completo de presencia digital y su empaquetado en zip.

``build_pack`` reúne todas las piezas (landing, Google Business, reseñas, QR) en
un objeto. ``to_zip`` lo convierte en un .zip que el dueño descarga con todo
listo y un LEEME que explica qué hacer con cada cosa.
"""

from __future__ import annotations

import html
import io
import zipfile
from dataclasses import dataclass

from faro.business import BusinessProfile
from faro.content import generate_copy
from faro.gmb import GmbContent, build_gmb
from faro.landing import render_landing
from faro.legal import legal_notice_html
from faro.qr import qr_svg, review_qr
from faro.reviews import (
    ReviewReplies,
    review_card_invite,
    review_replies,
    review_url,
)
from faro.whatsapp import whatsapp_link


@dataclass(frozen=True)
class DigitalPresencePack:
    """Todas las piezas generadas para un negocio."""

    landing_html: str
    gmb: GmbContent
    replies: ReviewReplies
    review_card_html: str
    legal_html: str
    whatsapp_url: str
    review_url: str


def _review_card_html(business: BusinessProfile) -> str:
    invite = html.escape(review_card_invite(business)).replace("\n", "<br>")
    name = html.escape(business.name)
    qr = review_qr(business)
    theme = business.theme
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8" />
<title>Tarjeta de reseñas · {name}</title>
<style>
  body {{
    font-family: system-ui, sans-serif; display: grid; place-items: center;
    min-height: 100vh; margin: 0; background: #f1f5f9;
  }}
  .card {{
    width: 320px; background: #fff; border-radius: 18px; padding: 28px;
    text-align: center; box-shadow: 0 12px 30px rgba(0,0,0,.12);
    border-top: 6px solid {theme.color};
  }}
  .card .emoji {{ font-size: 40px; }}
  .card h1 {{ font-size: 20px; margin: 10px 0; color: #0f172a; }}
  .card p {{ color: #475569; font-size: 15px; }}
  .card img {{ width: 180px; height: 180px; margin: 14px 0; }}
  .card .stars {{ color: #f59e0b; font-size: 22px; letter-spacing: 3px; }}
  @media print {{ body {{ background: #fff; }} .card {{ box-shadow: none; }} }}
</style></head>
<body><div class="card">
  <div class="emoji">{theme.emoji}</div>
  <div class="stars">★★★★★</div>
  <h1>{name}</h1>
  <p>{invite}</p>
  <img src="{qr}" alt="QR para dejar reseña" />
</div></body></html>
"""


def _gmb_markdown(business: BusinessProfile, gmb: GmbContent, replies: ReviewReplies) -> str:
    posts = "\n\n".join(f"**Publicación {i}:**\n{p}" for i, p in enumerate(gmb.posts, 1))
    services = "\n".join(f"- {s}" for s in gmb.services)
    return f"""# Google Business Profile — {business.name}

Pega esto en tu ficha de Google Business (business.google.com).

## Descripción del negocio

{gmb.description}

## Categorías sugeridas

{", ".join(gmb.categories)}

## Servicios

{services}

## Publicaciones para empezar (una por semana)

{posts}

## Respuestas tipo para reseñas

**Reseña buena (4-5 estrellas):**
{replies.positive}

**Reseña regular (3 estrellas):**
{replies.neutral}

**Reseña mala (1-2 estrellas):**
{replies.negative}
"""


def _readme(business: BusinessProfile) -> str:
    return f"""PACK DE PRESENCIA DIGITAL — {business.name}
=================================================

Esto es todo lo que necesitas para que te encuentren en internet. Qué es cada cosa:

1. index.html — Tu página web de una sola página.
   Súbela a cualquier hosting (o pídeselo a quien te montó esto). Funciona sola,
   no necesita nada más. Ábrela con doble clic para verla.

2. google-business.md — Los textos para tu ficha de Google.
   Entra en business.google.com, busca tu negocio y pega la descripción, las
   categorías y las publicaciones. Es lo que hace que aparezcas en Google Maps.

3. tarjeta-resenas.html — Tarjeta para el mostrador.
   Ábrela e imprímela. Cuando un cliente esté contento, que escanee el QR y te
   deje una reseña en Google. Las reseñas son lo que más te sube en las búsquedas.

4. resenas-qr.svg y whatsapp-qr.svg — Los códigos QR sueltos,
   por si los quieres poner en un cartel, en el escaparate o en redes.

5. aviso-legal.html — El aviso legal de tu web (lo exige la ley).
   Súbelo junto a la web (ya va enlazado en el pie). Completa tu NIF antes de
   publicarlo y, si tienes dudas, revísalo con tu asesor.

Tu WhatsApp de contacto: {whatsapp_link(business)}
Tu enlace de reseñas: {review_url(business)}

Cualquier duda, pregunta a quien te montó el pack.
"""


def build_pack(business: BusinessProfile, *, use_live: bool = True) -> DigitalPresencePack:
    """Genera todas las piezas del pack para un negocio."""
    copy = generate_copy(business, use_live=use_live)
    gmb = build_gmb(business)
    replies = review_replies(business)
    return DigitalPresencePack(
        landing_html=render_landing(business, copy),
        gmb=gmb,
        replies=replies,
        review_card_html=_review_card_html(business),
        legal_html=legal_notice_html(business),
        whatsapp_url=whatsapp_link(business),
        review_url=review_url(business),
    )


def to_zip(pack: DigitalPresencePack, business: BusinessProfile) -> bytes:
    """Empaqueta el pack en un .zip listo para descargar y entregar."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", pack.landing_html)
        zf.writestr("google-business.md", _gmb_markdown(business, pack.gmb, pack.replies))
        zf.writestr("tarjeta-resenas.html", pack.review_card_html)
        zf.writestr("resenas-qr.svg", qr_svg(pack.review_url))
        zf.writestr("whatsapp-qr.svg", qr_svg(pack.whatsapp_url, dark=business.theme.accent))
        zf.writestr("aviso-legal.html", pack.legal_html)
        zf.writestr("LEEME.txt", _readme(business))
    return buffer.getvalue()
