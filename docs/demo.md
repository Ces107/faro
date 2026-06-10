# Demo en vivo y publicación (faro-demo / faro-publish)

Dos comandos cubren el ciclo de venta: enseñar la web en el móvil del cliente en
la puerta, y dejarla online de verdad cuando cierras.

## `faro-demo` — la web en el móvil del cliente, en la puerta

```bash
faro-demo                 # formulario en blanco, lo rellenas en vivo
faro-demo casa-paco       # negocio del censo (faro-prospect): web directa
faro-demo bar             # web de ejemplo del sector "bar"
```

Qué hace, de un comando:

1. Arranca el servidor de Faro en un puerto libre.
2. Abre un **túnel público efímero** con Cloudflare Quick Tunnel
   (`https://<algo>.trycloudflare.com`). No requiere cuenta ni tarjeta. El
   binario `cloudflared` se descarga solo la primera vez (~52 MB) a `tools/bin/`.
3. Imprime un **código QR** de esa URL en la terminal y abre el navegador local.

El cliente apunta la cámara del móvil al QR y ve **su** web a pantalla completa
(la ruta `/d/<negocio>` sirve solo la web, sin el panel del operador). La toca,
la comparte por WhatsApp. `Ctrl+C` cierra la demo y para todo.

La URL del túnel **es temporal**: vive mientras el comando esté abierto. Es para
la demo, no para entregar.

> Nota de red: algunas redes corporativas filtran los dominios `*.trycloudflare.com`.
> Si el QR no abre desde un equipo de oficina, prueba desde el móvil con datos
> (4G/5G), que es justo el caso de uso real en la puerta.

### De dónde salen los datos de la web

- Si el negocio está en el **censo** (`faro-prospect <municipio>`), se usan sus
  datos reales (nombre, dirección…) **superpuestos** sobre la plantilla del
  sector, de modo que la web sale completa aunque el censo traiga pocos campos.
  El resto (teléfono, horario, servicios) es de ejemplo y se corrige con el
  dueño delante.
- Si pasas un **sector** (`bar`, `dental`, …) en vez de un negocio, se usa la web
  de ejemplo de ese sector.

## `faro-publish` — la web online de verdad (URL persistente)

```bash
faro-publish output/casa-paco-ab12cd   # carpeta de salida o pack.zip
faro-publish casa-paco                  # negocio del censo / sector
faro-publish casa-paco --dry-run        # prepara y valida sin desplegar
```

Publica la web autocontenida en **Cloudflare Pages** (free tier) y devuelve una
URL persistente `https://faro-<negocio>.pages.dev` que perdura. Es lo que
entregas tras cerrar; luego se apunta ahí el dominio del cliente.

Acepta una carpeta con `index.html`, un `pack.zip`, una carpeta de salida de
Faro, o un slug del censo / nombre de sector.

### Requisito único (una sola vez)

Necesita Node (`npx`, ya disponible) y una cuenta de Cloudflare autenticada
**una vez**:

```bash
npx wrangler login          # abre el navegador, login con la cuenta Cloudflare
# o bien: export CLOUDFLARE_API_TOKEN=<token con permiso "Cloudflare Pages: Edit">
```

Crear la cuenta es gratis y sin tarjeta. Si no hay sesión, `faro-publish` no
publica: explica qué hacer y sale. No gasta dinero por sí solo.

## Tabla rápida

| | `faro-demo` | `faro-publish` |
|---|---|---|
| Para qué | enseñar en la puerta | entregar tras cerrar |
| URL | efímera (`trycloudflare.com`) | persistente (`pages.dev`) |
| Cuenta | ninguna | Cloudflare (gratis, login 1 vez) |
| Coste | €0 | €0 (free tier) |
| Vive mientras | el comando esté abierto | siempre |
