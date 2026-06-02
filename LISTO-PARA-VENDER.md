# Listo para vender — qué está hecho y qué falta (solo lo tuyo)

Esto resume el estado de Faro tras la auditoría de "listo para vender". Todo lo que podía hacer está hecho. Lo que queda son cinco cosas que **obligatoriamente** tienes que hacer tú, porque dependen de tu identidad, tu dinero o tu firma.

## Lo que ya está hecho (no tienes que tocar nada)

**Producto**
- Genera web + ficha de Google + WhatsApp + tarjeta de reseñas + aviso legal, en minutos.
- Web responsive con tu color de marca, logo de iniciales, SEO real (datos estructurados de Google), Open Graph y mapa "cómo llegar" con consentimiento de cookies.
- 17 sectores cubiertos. Seguridad: sin inyección de código (escapado), sin fugas de email.
- Arranca solo en modo gratis (sin llamar a servicios de pago) y aguanta textos largos sin romperse.
- 63 tests, CI verde. Repo: https://github.com/Ces107/faro

**Para usarlo sin saber programar**
- `iniciar-faro.bat`: doble clic y arranca. Guía: `INICIO-RAPIDO.md`.

**Para entregar**
- `ENTREGA.md`: cómo publicar la web gratis (Netlify) y poner en marcha la ficha de Google, con checklist.
- Cada web lleva su aviso legal y política de cookies.

**Para vender**
- `ventas/`: hoja de una página (y versión imprimible A5), guion de puerta, precios, objetivos de Sagunto, plantillas de mensajes, acuerdo de servicio, factura, recibo y registro de puertas.

---

## Lo único que falta (TUYO, no lo puedo hacer yo)

### 1. Darte de alta como autónomo + poder facturar
Antes de la primera venta. Lo que obliga es la actividad habitual, no un umbral de euros.
- Alta en Hacienda (modelo 036/037), epígrafe IAE correcto (servicios informáticos/publicidad).
- Alta en RETA (Seguridad Social). Mira la tarifa plana (~80 €/mes el primer año si te aplica).
- Elige régimen de IVA.
- Pásame tu NIF y tus datos fiscales y los meto en las plantillas de factura/recibo/acuerdo (ya están listas con huecos).

### 2. Un medio de cobro a tu nombre (KYC)
- Un teléfono con Bizum y/o un IBAN (tu cuenta personal vale para las primeras ventas puntuales).
- Si vas a cobrar suscripciones, abre Stripe.
- Pásame el número/IBAN y lo pongo en el acuerdo y el recibo.

### 3. Tus datos de contacto reales
- Decide y pásame tu teléfono/WhatsApp + email (o una línea dedicada).
- Los inyecto en: el folleto, el LEEME de cada pack (con las variables `FARO_OPERATOR_NAME` y `FARO_OPERATOR_CONTACT`), el recibo y el acuerdo. Ahora mismo están como huecos `[tu número]`.

### 4. Dominio propio (opcional)
- Para empezar, la web va en un subdominio gratis (tipo `negocio.netlify.app`): no necesitas comprar nada.
- Si un cliente quiere su `sunegocio.com`, se compra el dominio (~10-12 €/año) bajo tu cuenta y lo apunto yo al hosting gratis. La cláusula ya está en el acuerdo.

### 5. Firmar el acuerdo en cada venta
- Revisa y firma `ventas/contrato-servicio.md` en cada cierre (y, para clientes de mantenimiento, el anexo de protección de datos).
- Todo está redactado menos tu firma y tus datos fiscales.

---

## Cómo arrancar (cuando tengas lo de arriba)

1. Doble clic en `iniciar-faro.bat` para probar la herramienta (`INICIO-RAPIDO.md`).
2. Sal a la calle con el portátil y el guion (`ventas/guion-puerta.md`). Anota cada visita en `ventas/registro-puertas.md`.
3. Cuando cierres: cobra, publica la web y monta la ficha de Google siguiendo `ENTREGA.md`, y entrega el recibo.

**Kill-gate honesto:** si tras 40 puertas frías cierras menos de 3, para y replanteamos. El cuello de botella no es el producto, es caminar y cerrar en persona. La confianza de que esto da dinero en 90 días es de ~60-70%, condicionada a que se hagan las puertas.
