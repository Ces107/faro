# Ejemplo de uso

## Desde la web (la forma normal de venderlo)

```bash
presencia-local        # abre http://localhost:8000
```

Rellena el formulario con los datos del negocio, pulsa "Generar pack", y verás la
web al momento en la vista previa. Descarga el .zip y entrégalo.

## Desde Python (para automatizar o probar)

```python
from presencia_local.business import BusinessProfile, Sector
from presencia_local.pack import build_pack, to_zip

negocio = BusinessProfile(
    name="Clínica Dental Sonríe",
    sector=Sector.DENTAL,
    city="Puerto de Sagunto",
    phone="961234567",
    services=("Limpiezas dentales", "Implantes", "Ortodoncia invisible"),
    hours="L-V 9:00-20:00, S 9:00-14:00",
    address="Av. del Mediterráneo 12",
    highlights=("20 años cuidando sonrisas en el Puerto", "Primera visita sin coste"),
)

pack = build_pack(negocio, use_live=False)        # use_live=True usa la API de Anthropic

# La web, lista para subir a cualquier hosting:
open("index.html", "w", encoding="utf-8").write(pack.landing_html)

# El pack completo en un .zip (web + Google Business + reseñas + QR + LEEME):
open("presencia-clinica.zip", "wb").write(to_zip(pack, negocio))
```

## Qué hay en el .zip

```
index.html            la web de una página, lista para publicar
google-business.md    descripción, categorías y publicaciones para Google Business
tarjeta-resenas.html  tarjeta imprimible con QR para el mostrador
resenas-qr.svg        QR a las reseñas de Google
whatsapp-qr.svg       QR al WhatsApp del negocio
LEEME.txt             instrucciones para el dueño: qué hacer con cada cosa
```
