# faro-prospect — censo de prospección sobre OpenStreetMap

Convierte un municipio en una salida de venta organizada: qué negocios de la
zona no tienen presencia web mapeada, por qué calles caminar, y el formulario
de Faro ya precargado con los datos públicos de cada negocio.

## Uso

```bash
faro-prospect "Sagunto" --city "Puerto de Sagunto" --bbox "39.62,-0.256,39.69,-0.19"
```

- `municipio` — nombre del municipio. La búsqueda es insensible a mayúsculas y
  cubre nombres bilingües ("Sagunt / Sagunto" responde a "sagunt" y "sagunto").
- `--bbox sur,oeste,norte,este` — opcional, recorta a un núcleo urbano.
- `--city` — nombre de ciudad que se precarga en el formulario.
- `--rel-id` — fija la relación OSM si el nombre es ambiguo.
- `--base-url` — URL de la consola local (por defecto `http://127.0.0.1:8000/`).

Salida en `prospect/<municipio>/`:

| Fichero | Qué es |
|---|---|
| `ruta.html` | Hoja de ruta imprimible agrupada por calle, con casillas y notas |
| `prospects.json` | Precarga del formulario por negocio (la consola la sirve) |
| `folletos.html` | Folletos A6 por sector con QR a las demos de ejemplo |
| `census.json` | Censo completo con métricas y motivos de exclusión |

## El flujo en la puerta

1. Genera el censo y abre `ruta.html` en el portátil (o imprímela).
2. En cada negocio, el enlace «buscar en Google» confirma si de verdad no tiene
   web (la ausencia en OSM es una pista, no una garantía).
3. «Formulario precargado» abre la consola con nombre, ciudad, dirección y
   teléfono ya puestos. Confírmalos con el dueño, añade servicios y horario, y
   genera la web delante. De ~10 minutos de demo a ~1.
4. Los folletos se dejan en negocios cerrados o tras un no.

## Qué filtra el censo

- **Sin nombre** — no se puede vender a un POI anónimo.
- **Cadenas** (etiqueta `brand`) — masymas o Supercor no compran webs locales.
- **Con presencia web mapeada** (`website`, redes) — ya tienen.
- **Categorías no prospectables** — parkings, colegios, etc.
- **Fuera del bbox** — si se pidió recorte.

Los negocios sin editar en OSM desde hace años se marcan «dato antiguo:
confirmar abierto»; los verificados recientemente, «verificado 2024+».

## Límites honestos y reglas de uso

- **La ausencia de web en OSM no garantiza que no tengan web.** Por eso la hoja
  obliga al vistazo a Google en la puerta antes de entrar.
- **La lista es interna y efímera.** No contiene teléfonos (se quedan en
  `census.json`, local), no se publica ni se comparte: minimización de datos.
- **Atribución ODbL.** Los datos son © OpenStreetMap contributors; la hoja la
  lleva impresa en el pie. Si alguna vez se publicara una base derivada,
  aplicaría share-alike (ODbL); el uso interno no lo dispara.
- **Nada de envíos electrónicos en frío.** El censo alimenta visitas en
  persona y buzoneo físico. WhatsApp/email comercial sin consentimiento previo
  es infracción de la LSSI (art. 21).
- **Las demos con la marca del negocio se generan SOLO en local**, delante del
  dueño y con sus datos confirmados. Nunca se publican demos con marcas ajenas;
  los QR de los folletos llevan a ejemplos con marca ficticia.

## El directorio `prospect/` no se commitea

Está en `.gitignore`: contiene nombres de negocios reales. El código es
público; los datos generados son locales.
