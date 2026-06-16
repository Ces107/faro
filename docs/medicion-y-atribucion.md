# Medir si la web funciona (contador + atribución por canal)

El gap más caro en la venta puerta a puerta es la pregunta *"¿cuántos clientes me
trae esto?"*. Sin un número, el argumento es no-falsable y un comprador quemado lo
huele. Faro no promete clientes (eso sería mentir), pero **sí** deja montado lo
necesario para enseñar **visitas reales y de dónde vienen**. Eso desbloquea tres
cosas: cerrar al escéptico, justificar el mantenimiento y fabricar la referencia
("a este le funcionó").

## 1. El contador: GoatCounter (gratis, sin cookies)

[GoatCounter](https://www.goatcounter.com/) cuenta páginas vistas **sin cookies y
sin recoger datos personales**, así que no rompe la promesa de "sin cookies de
seguimiento" del aviso legal ni obliga a banner de consentimiento.

Alta (una vez por cliente, ~2 min):

1. Crea una cuenta gratis en goatcounter.com **con el email del cliente** (o el de
   gestión que acuerdes), elige un código de sitio, p. ej. `casapaco`.
2. Ese código se mete en el formulario de Faro, campo **"Contador de visitas
   (GoatCounter)"**. Faro inyecta el script en la web automáticamente
   (`seo.analytics_snippet`). No hay que tocar HTML.
3. El panel queda en `https://casapaco.goatcounter.com`.

Plan gratis: hasta ~100k visitas/mes. De sobra para un negocio local.

## 2. La atribución: etiquetas UTM por canal

El contador cuenta visitas, pero por defecto no sabe **de dónde** vienen. Faro
resuelve esto poniendo la **misma URL del sitio con una etiqueta distinta** en cada
sitio donde aparece (`seo.tracked_url`). Así, en el panel, una visita desde el QR
del mostrador y otra desde la ficha de Google se ven separadas:

| Dónde aparece la URL | Etiqueta (`utm_source`) | Qué responde |
|---|---|---|
| Campo "Sitio web" de la ficha de Google | `google-business` | cuánta gente llega desde Google |
| QR del mostrador / escaparate (`web-qr.svg`) | `qr-mostrador` | si el QR físico mueve algo |

Estas URLs etiquetadas salen ya hechas en `google-business.md` (sección "Sitio
web") y en `web-qr.svg` del pack — **solo se generan cuando la web tiene una URL
publicada** (`canonical_url`); antes de publicar no existen, porque no habría a
dónde apuntar.

**Importante:** la etiqueta UTM va **solo** en esas colocaciones externas. El
`canonical`, el Open Graph y el JSON-LD de la propia página se quedan **sin
etiqueta** (limpios), como debe ser para el SEO. Eso es deliberado.

## 3. Cómo leerlo (lo que le enseñas al cliente al mes)

En el panel de GoatCounter:

- **Total de visitas** del mes → "tu web tuvo 80 visitas".
- En **Paths / Referrers** se ve la cola `?utm_source=...` → "30 vinieron desde el
  QR del mostrador, 25 desde tu ficha de Google".

Eso es lo que convierte la pregunta no-falsable en un dato. Sigue sin demostrar
*cubiertos* (una visita no es un cliente), y hay que decirlo con honestidad, pero
ya no es "créeme": es "míralo".

## 4. Límites honestos (dilos)

- Una visita no es un cliente; el contador no mide ventas, mide interés.
- GoatCounter cuenta del lado del navegador: bots y bloqueadores hacen que el
  número real sea un suelo, no un absoluto.
- La atribución por UTM solo cubre los canales donde ponemos la URL etiquetada
  (ficha de Google y QR). El boca a boca que teclea la dirección a pelo entra como
  visita directa, sin origen.
