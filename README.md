# Faro

**Genera en minutos el pack de presencia digital de un negocio local: una página web lista para publicar, el contenido para su ficha de Google, el WhatsApp y la tarjeta de reseñas con QR. Rellenas un formulario, ves la web al momento y descargas todo en un .zip. Sin cuentas de pago para la demo.**

[![CI](https://github.com/Ces107/faro/actions/workflows/ci.yml/badge.svg)](https://github.com/Ces107/faro/actions/workflows/ci.yml)

---

## Para qué sirve

El 78% de los micro-negocios en España no tiene web y el 80% no está en los directorios. Una peluquería, un taller o una clínica de barrio existe para sus clientes, pero no para Google. Quien busca "dentista en mi pueblo" no los encuentra.

Faro convierte ese trabajo (que a mano son horas por cliente) en minutos: metes los datos del negocio una vez y sale todo lo que necesita para que lo encuentren.

## La demo

```bash
pip install -e ".[dev]"
faro                    # abre http://localhost:8000
```

Rellenas el formulario con los datos del negocio y pulsas "Generar pack". Al momento ves la web del negocio en la vista previa y puedes descargar el .zip con todo dentro.

![El generador](docs/ejemplo-generador.png)

## Qué genera

A partir de un formulario produce:

- **Una landing de una página**, responsive y lista para publicar. HTML autocontenido (los estilos y los QR van dentro): se sube a cualquier hosting y funciona. Incluye botón de WhatsApp, llamada directa, servicios, horario, sección de reseñas, logo con las iniciales del negocio y su color de marca. Trae **SEO de verdad**: datos estructurados de schema.org (`LocalBusiness`) que Google lee para el SEO local, etiquetas Open Graph para que el enlace se vea bien al compartirlo por WhatsApp, y favicon propio.
- **El contenido para Google Business Profile**: descripción optimizada (dentro del límite de Google), categorías sugeridas, cinco publicaciones para empezar y respuestas tipo para reseñas buenas, regulares y malas.
- **El WhatsApp**: enlace `wa.me` con mensaje pre-rellenado y su QR.
- **La tarjeta de reseñas**: una tarjeta imprimible con el QR que lleva a dejar la reseña en Google. Se deja en el mostrador.
- **El aviso legal** de la web (lo exige la ley en España, LSSI-CE), con los datos del negocio y un hueco para el NIF.

Para usarlo sin saber programar, hay un lanzador de un clic (`iniciar-faro.bat`) y una guía paso a paso ([`INICIO-RAPIDO.md`](INICIO-RAPIDO.md)). Para poner online la web del cliente y su ficha de Google, ver [`ENTREGA.md`](ENTREGA.md).

![Ejemplo de landing generada](docs/ejemplo-landing.png)

## Por qué así

El cliente no compra "una web". Compra ver SU negocio, con SU nombre, bien hecho, en dos minutos delante de él. Ese es el cierre: rellenas el formulario en el mostrador, le enseñas su propia página, y le entregas el pack. Lo que a otros les lleva días, aquí son minutos, y lo ve antes de pagar.

## Modo demostración y modo real

| | Modo *scripted* (por defecto) | Modo *live* |
|---|---|---|
| Copy de la web | Plantillas de calidad por sector | API de Anthropic (Claude) |
| Requiere | Nada | `ANTHROPIC_API_KEY` + `pip install -e ".[live]"` |

Sin clave de API, el copy sale de plantillas de calidad y la herramienta funciona entera. Con clave, el texto lo redacta el modelo. Si la API falla, se cae a las plantillas: el cliente nunca se queda sin pack.

## Cómo se vende

Material de venta en [`ventas/`](ventas/): hoja de una página (y versión imprimible A5), guion de puerta, precios, objetivos para el Camp de Morvedre / Sagunto, plantillas de mensajes, acuerdo de servicio, factura, recibo y registro de puertas. Resumen: pack de **290-500 €** (pago único, es suyo) + un mantenimiento mensual opcional. La venta es puerta a puerta con la web del cliente en pantalla.

**¿Qué falta para vender de verdad?** Ver [`LISTO-PARA-VENDER.md`](LISTO-PARA-VENDER.md): todo lo técnico y de proceso está hecho; lo único pendiente son cinco tareas que dependen de la identidad/fiscalidad del operador (alta de autónomo, medio de cobro, datos de contacto, dominio opcional, firma).

## Estructura

```
src/faro/
  business.py    modelo del negocio (datos + validación)
  content.py     copy de la landing (plantillas + LLM opcional)
  landing.py     render de la landing (Jinja2)
  gmb.py         contenido para Google Business Profile
  whatsapp.py    enlaces de WhatsApp y teléfono
  reviews.py     reseñas: enlace, QR, respuestas tipo
  qr.py          códigos QR en SVG (segno, sin dependencias de pago)
  pack.py        arma el pack completo y lo empaqueta en .zip
  server.py      API FastAPI + servidor de la demo
  templates/     plantilla de la landing
web/             el formulario y la vista previa
ventas/          material de venta
tests/           61 tests
```

## Calidad

```bash
python -m pytest      # 61 tests
python -m ruff check src tests
python -m mypy        # --strict
```

## Licencia

MIT. Ver [`LICENSE`](LICENSE).

> Las reseñas se invitan, nunca se incentivan ni se condicionan (eso va contra las normas de Google). El texto de la web y de Google es un punto de partida de calidad; el dueño lo revisa antes de publicar.
