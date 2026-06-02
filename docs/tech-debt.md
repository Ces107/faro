# Tech-debt (sweep inicial 2026-06-02)

Revisión adversarial del propio código tras la primera versión. Ninguno bloquea
la demo ni la entrega de un pack; se listan para no esconderlos.

- **TD-001 MEDIUM — el QR de reseñas lleva a buscar el negocio, no a escribir la reseña directa.**
  `reviews.review_url` sin `google_review_url` genera una búsqueda de Google Maps
  (lo mejor posible sin el place_id del negocio). Para que el QR abra el diálogo
  de reseña directo hace falta el enlace `g.page/r/.../review` del negocio. El
  formulario ya lo pide; conviene capturarlo siempre en el alta del cliente.
  Fix futuro: resolver el place_id vía la API de Places (requiere clave) para
  generar el enlace directo automáticamente.

- **TD-002 MEDIUM — packs en memoria sin expiración.**
  `server.create_app` guarda los packs en un dict que no caduca. En la demo da
  igual; en un despliegue largo es una fuga. Fix: TTL o tope de packs.

- **TD-003 LOW — el copy en modo live no tiene test.**
  Requiere `ANTHROPIC_API_KEY`. El camino scripted (sin clave) sí está cubierto,
  incluido el fallback. Fix: test con un cliente Anthropic simulado.

- **TD-004 LOW — la web hay que subirla a un hosting a mano.**
  El pack genera `index.html` autocontenido, pero no hay despliegue automático.
  Para escalar la entrega, integrar un deploy de un clic (Netlify/GitHub Pages/
  Cloudflare Pages) reduciría el trabajo por cliente. De momento se sube a mano o
  se sirve desde el hosting del operador.

- **TD-005 LOW — los campos del formulario no limitan longitud.**
  Un servicio o un nombre muy largos podrían descuadrar el layout de la landing.
  Fix: validar longitudes máximas en `BusinessProfile` y avisar en el formulario.

- **TD-006 LOW — el contenido de Google Business se pega a mano.**
  No hay integración con la API de Google Business Profile (requiere OAuth y
  verificación del negocio). El dueño pega los textos. Es lo correcto para el MVP;
  la automatización es un paso posterior con permisos del cliente.
