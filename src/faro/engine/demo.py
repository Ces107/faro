"""Datos de ejemplo por sector para ver una web COMPLETA de un clic.

El operador despliega en local, elige un tipo, pulsa "Ver ejemplo" y obtiene una
web entera y realista de esa familia (con todos los campos rellenos: servicios con
precios, valoración, oferta, reserva, credenciales...). Luego edita los datos del
negocio real. Es contenido de DEMO a propósito: NO se entrega tal cual; el operador
lo sustituye por los datos verdaderos antes de dar el pack al cliente.
"""

from __future__ import annotations

from faro.business import Sector

# Valores comunes a casi todos los ejemplos (contexto Camp de Morvedre).
_COMMON: dict[str, str] = {
    "city": "Puerto de Sagunto",
    "languages": "Castellano, Valenciano",
    "payment_methods": "Efectivo, Tarjeta, Bizum",
    "offer_end_date": "2026-12-31",
}

_DEMO: dict[Sector, dict[str, str]] = {
    Sector.BAR: {
        "name": "Bar El Faro",
        "phone": "961234567",
        "services": "Desayunos 2,50€\nAlmuerzos de obra 6€\nTapas variadas\nMenú del día 11€\nCafé y vermut",
        "hours": "L-D 7:00-23:00",
        "address": "Plaza Mayor 3",
        "about": "El bar de toda la vida en el Puerto. Desayunos de cuchara, almuerzos de obra "
                 "abundantes y buen tapeo por la tarde. Aquí se viene a estar a gusto.",
        "differentiators": "Terraza al sol todo el día\nPan de horno propio\nAlmuerzos abundantes de verdad",
        "years": "2012",
        "parking": "Fácil aparcar en la plaza",
        "instagram": "@barelfaro",
        "google_rating": "4.7",
        "google_reviews_count": "183",
        "google_profile_url": "https://g.page/bar-el-faro",
        "offer_title": "Almuerzo + café + chupito 7€",
        "offer_details": "de lunes a viernes, de 9:00 a 11:30",
        "delivery_links": "https://glovoapp.com/es/bar-el-faro",
        "slogan": "Tu sitio para un buen rato",
    },
    Sector.RESTAURANTE: {
        "name": "Restaurante La Marina",
        "phone": "961234568",
        "services": "Arroces (mín. 2 personas) 16€\nPescado del día\nTapas de la casa\nMenú degustación 32€\nPostres caseros",
        "hours": "M-D 13:00-16:00, 20:00-23:30",
        "address": "Avenida del Mediterráneo 45",
        "about": "Cocina mediterránea de producto, con el arroz como bandera. Pescado fresco "
                 "de la lonja y un trato de los de siempre, frente al mar.",
        "differentiators": "Arroces por encargo\nPescado de lonja diario\nTerraza frente al mar",
        "years": "2008",
        "instagram": "@lamarina.restaurante",
        "google_rating": "4.8",
        "google_reviews_count": "412",
        "google_profile_url": "https://g.page/restaurante-la-marina",
        "booking_url": "https://www.thefork.es/restaurante/la-marina",
        "offer_title": "Menú del día entre semana 14€",
        "offer_details": "incluye bebida y postre, de lunes a viernes al mediodía",
        "slogan": "Arroz, mar y producto",
    },
    Sector.PANADERIA: {
        "name": "Panadería La Espiga",
        "phone": "961234569",
        "services": "Pan artesano de masa madre\nBollería recién horneada\nTartas y repostería por encargo\nPan sin gluten",
        "hours": "L-S 7:00-14:00, 17:00-20:30",
        "address": "Calle San Cristóbal 12",
        "about": "Horneamos cada día con masa madre y harinas de calidad. Pan de verdad, "
                 "bollería del momento y encargos para tus celebraciones.",
        "differentiators": "Masa madre propia\nHorneado durante todo el día\nEncargos para eventos",
        "years": "1998",
        "google_rating": "4.9",
        "google_reviews_count": "97",
        "offer_title": "Café + napolitana 2€ por las mañanas",
        "offer_details": "de 7:00 a 10:00",
        "slogan": "Pan recién hecho cada día",
    },
    Sector.DENTAL: {
        "name": "Clínica Dental Sonríe",
        "phone": "961112233",
        "services": "Primera visita y diagnóstico\nLimpieza dental\nImplantes\nOrtodoncia invisible\nBlanqueamiento",
        "hours": "L-V 9:00-20:00",
        "address": "Calle Rambla 8",
        "about": "Cuidamos tu sonrisa con un trato cercano y sin sustos. Te explicamos cada "
                 "tratamiento con claridad y te damos un plan a tu medida.",
        "differentiators": "Primera visita sin coste\nFinanciación a tu medida\nUrgencias el mismo día",
        "years": "2009",
        "google_rating": "4.9",
        "google_reviews_count": "214",
        "google_profile_url": "https://g.page/dental-sonrie",
        "booking_url": "https://www.doctoralia.es/clinica-dental-sonrie",
        "offer_title": "Primera revisión + diagnóstico gratis",
        "offer_details": "pidiendo cita por WhatsApp o teléfono",
        "credentials": "Colegiado nº COEV 1234\nSeguro de responsabilidad civil\nEsterilización certificada",
        "slogan": "Tu sonrisa en las mejores manos",
    },
    Sector.FISIO: {
        "name": "Fisioterapia Equilibrio",
        "phone": "961112234",
        "services": "Sesión de fisioterapia 35€\nMasaje descontracturante\nPunción seca\nReadaptación deportiva\nPilates terapéutico",
        "hours": "L-V 9:00-21:00",
        "address": "Avenida 9 d'Octubre 22",
        "about": "Te ayudamos a moverte sin dolor y a recuperarte de verdad. Valoración "
                 "honesta en la primera visita y un plan adaptado a ti.",
        "differentiators": "Valoración inicial completa\nFisioterapia deportiva\nA domicilio según disponibilidad",
        "years": "2015",
        "google_rating": "4.8",
        "google_reviews_count": "131",
        "booking_url": "https://www.doctoralia.es/fisioterapia-equilibrio",
        "credentials": "Colegiado nº 567\nFormación en punción seca",
        "service_area": "Puerto de Sagunto, Sagunto, Canet d'En Berenguer",
        "slogan": "Recupérate y vuelve a moverte",
    },
    Sector.VETERINARIO: {
        "name": "Clínica Veterinaria Patitas",
        "phone": "961112235",
        "services": "Consulta general\nVacunación y desparasitación\nCirugía\nPeluquería canina\nAnalíticas",
        "hours": "L-V 10:00-14:00, 17:00-20:30, S 10:00-13:30",
        "address": "Calle Teruel 5",
        "about": "Cuidamos de tu mascota como de la familia. Trato cuidadoso, diagnóstico "
                 "claro y seguimiento de verdad.",
        "differentiators": "Urgencias 24h\nTrato sin estrés para el animal\nPlan de salud anual",
        "years": "2011",
        "google_rating": "4.9",
        "google_reviews_count": "168",
        "offer_title": "Primera consulta + revisión gratis",
        "credentials": "Colegiado nº 890\nCentro veterinario autorizado",
        "slogan": "El cuidado que tu mascota merece",
    },
    Sector.FARMACIA: {
        "name": "Farmacia Centro",
        "phone": "961112236",
        "services": "Medicamentos y recetas\nDermofarmacia\nOrtopedia\nFórmulas magistrales\nMedición de tensión y azúcar",
        "hours": "L-V 9:00-21:00, S 9:00-14:00",
        "address": "Plaza del Sol 1",
        "about": "Tu farmacia de confianza en el centro. Asesoramiento farmacéutico de verdad "
                 "y todo lo que necesitas para tu salud y cuidado.",
        "differentiators": "Asesoramiento farmacéutico\nEncargos en el día\nServicio de guardia",
        "years": "1995",
        "google_rating": "4.6",
        "google_reviews_count": "74",
        "slogan": "Tu salud, bien atendida",
    },
    Sector.PELUQUERIA: {
        "name": "Estudio Mara Peluqueros",
        "phone": "961445500",
        "services": "Corte y peinado 18€\nMechas / balayage\nColor\nTratamientos de hidratación\nRecogidos de novia",
        "hours": "M-S 9:30-20:00",
        "address": "Calle Valencia 30",
        "about": "Un estudio donde te escuchamos antes de tocar tijeras. Color y cortes que "
                 "te favorecen de verdad, cuidando siempre tu pelo.",
        "differentiators": "Asesoría de imagen incluida\nProductos sin sulfatos\nColor que cuida el cabello",
        "years": "2016",
        "instagram": "@marapeluqueros",
        "google_rating": "4.9",
        "google_reviews_count": "256",
        "booking_url": "https://booksy.com/es/estudio-mara",
        "offer_title": "Diagnóstico capilar gratis",
        "slogan": "Tu mejor versión empieza aquí",
    },
    Sector.ESTETICA: {
        "name": "Centro de Estética Luz",
        "phone": "961445501",
        "services": "Limpieza facial 40€\nDepilación láser\nPresoterapia\nManicura y pedicura\nTratamientos antiedad",
        "hours": "L-V 10:00-20:00, S 10:00-14:00",
        "address": "Calle Sevilla 14",
        "about": "Un espacio para cuidarte de verdad. Diagnosticamos tu piel y te recomendamos "
                 "solo lo que necesitas, con productos de calidad contrastada.",
        "differentiators": "Diagnóstico de piel personalizado\nAparatología de última generación\nProductos dermatológicos",
        "years": "2018",
        "instagram": "@esteticaluz",
        "google_rating": "4.8",
        "google_reviews_count": "142",
        "booking_url": "https://booksy.com/es/estetica-luz",
        "offer_title": "Primera limpieza facial -20%",
        "slogan": "Cuídate. Te lo mereces",
    },
    Sector.TALLER: {
        "name": "Talleres Morvedre",
        "phone": "961445566",
        "services": "Mecánica general\nMantenimiento y revisiones\nPre-ITV\nNeumáticos\nDiagnosis electrónica",
        "hours": "L-V 8:00-13:30, 15:30-19:00",
        "address": "Polígono Industrial, Calle B 7",
        "about": "Tu coche en buenas manos desde 1998. Presupuesto cerrado por escrito antes "
                 "de tocar nada y trabajo con garantía.",
        "differentiators": "Presupuesto cerrado por escrito\nCoche de cortesía\nTrabajamos todas las marcas",
        "years": "1998",
        "google_rating": "4.7",
        "google_reviews_count": "203",
        "offer_title": "Revisión pre-ITV gratis",
        "offer_details": "pidiendo cita previa",
        "credentials": "Taller autorizado nº 46/1234\nGarantía por escrito",
        "service_area": "Puerto de Sagunto, Sagunto, Canet, Almenara",
        "slogan": "Tu coche, en buenas manos",
    },
    Sector.REFORMAS: {
        "name": "Reformas Construnova",
        "phone": "961445567",
        "services": "Reforma integral\nReforma de baños\nReforma de cocinas\nPintura y alicatado\nInstalaciones",
        "hours": "L-V 8:00-18:00",
        "address": "Calle Industria 19",
        "about": "Transformamos tu casa con presupuesto cerrado y plazos que se cumplen. "
                 "Sin sorpresas y con todas las garantías.",
        "differentiators": "Presupuesto cerrado sin sorpresas\nPlazos por escrito\nGestionamos los permisos",
        "years": "2005",
        "google_rating": "4.8",
        "google_reviews_count": "88",
        "offer_title": "Proyecto y presupuesto gratis",
        "credentials": "Seguro de responsabilidad civil\nGarantía de obra",
        "service_area": "Camp de Morvedre y Valencia",
        "slogan": "Transformamos tu espacio",
    },
    Sector.ASESORIA: {
        "name": "Asesoría Morvedre",
        "phone": "961778800",
        "services": "Gestoría para autónomos\nContabilidad de empresas\nLaboral y nóminas\nFiscal e impuestos\nAlta de autónomos",
        "hours": "L-V 9:00-14:00, 16:00-19:00",
        "address": "Avenida País Valencià 50",
        "about": "Llevamos el papeleo de autónomos y pymes de la zona para que tú te dediques "
                 "a lo tuyo. Cercanía, claridad y sin letra pequeña.",
        "differentiators": "Trato directo, sin call center\nPresupuesto claro y cerrado\nRespuesta en 24h",
        "years": "2003",
        "google_rating": "4.9",
        "google_reviews_count": "61",
        "booking_url": "https://calendly.com/asesoria-morvedre",
        "offer_title": "Primera consulta gratuita",
        "credentials": "Colegiado en el Colegio de Gestores\nMiembro de la AECE",
        "slogan": "Tu negocio, sin preocupaciones",
    },
    Sector.INMOBILIARIA: {
        "name": "Inmobiliaria Costa Azahar",
        "phone": "961778801",
        "services": "Compraventa de viviendas\nAlquiler\nTasación gratuita\nGestión documental\nAsesoramiento hipotecario",
        "hours": "L-V 9:30-14:00, 17:00-20:00",
        "address": "Calle del Mar 11",
        "about": "Conocemos el mercado del Camp de Morvedre como nadie. Te acompañamos en "
                 "cada paso, con transparencia desde el primer día.",
        "differentiators": "Tasación gratuita y realista\nConocemos la zona al detalle\nComisión clara desde el inicio",
        "years": "2010",
        "google_rating": "4.7",
        "google_reviews_count": "94",
        "offer_title": "Valoración de tu vivienda gratis",
        "service_area": "Puerto de Sagunto, Sagunto, Canet, Almenara",
        "slogan": "Encuentra tu próximo hogar",
    },
    Sector.GIMNASIO: {
        "name": "Gimnasio Pulse",
        "phone": "961889900",
        "services": "Sala de musculación\nClases dirigidas (spinning, body pump)\nEntrenamiento personal\nZona cardio\nCrosstraining",
        "hours": "L-V 7:00-23:00, S-D 9:00-14:00",
        "address": "Avenida Constitución 100",
        "about": "Un gimnasio para entrenar a tu ritmo, sin permanencia y con gente que te "
                 "ayuda. Ven a probar y lo ves.",
        "differentiators": "Sin permanencia\nPrimer día gratis\nEntrenadores en sala siempre",
        "years": "2019",
        "instagram": "@gimnasiopulse",
        "google_rating": "4.8",
        "google_reviews_count": "177",
        "booking_url": "https://gimnasiopulse.es/prueba-gratis",
        "offer_title": "Tu primer día gratis",
        "offer_details": "ven a conocer las instalaciones sin compromiso",
        "slogan": "Ponte en forma a tu ritmo",
    },
    Sector.COMERCIO: {
        "name": "Tienda La Plaza",
        "phone": "961990011",
        "services": "Ropa y complementos\nAtención personalizada\nArreglos y encargos\nTarjeta regalo",
        "hours": "L-S 10:00-14:00, 17:00-20:30",
        "address": "Plaza del Mercado 4",
        "about": "Comercio de barrio con trato de verdad. Te ayudamos a encontrar lo que "
                 "buscas, sin agobios y con cosas que no hay en las grandes superficies.",
        "differentiators": "Atención de verdad, sin prisas\nProducto seleccionado\nSi no lo tenemos, lo pedimos",
        "years": "2007",
        "instagram": "@tiendalaplaza",
        "google_rating": "4.6",
        "google_reviews_count": "52",
        "slogan": "Lo que buscas, al lado de casa",
    },
    Sector.AUTONOMO: {
        "name": "Juan Martín · Servicios",
        "phone": "961990012",
        "services": "Presupuesto sin compromiso\nServicio a domicilio\nTrabajos urgentes\nMantenimiento",
        "hours": "L-V 8:00-19:00",
        "about": "Profesional de confianza en el Puerto. Cuéntame qué necesitas y te doy "
                 "presupuesto sin compromiso.",
        "differentiators": "Presupuesto sin compromiso\nServicio a domicilio\nTrato directo",
        "years": "2014",
        "google_rating": "4.8",
        "google_reviews_count": "39",
        "service_area": "Puerto de Sagunto y alrededores",
        "slogan": "El servicio que necesitas, cerca",
    },
}


def _u(pid: str) -> str:
    """URL de una foto de Unsplash (solo para los ejemplos; el operador pone las reales)."""
    return f"https://images.unsplash.com/{pid}?w=1400&q=72&auto=format&fit=crop"


# Fotos topicales por sector: la foto a sangre es el protagonista del hero y llena
# la galería (es lo que más diferencia una web de estudio de una "pobre"). Son de
# muestra; el operador las sustituye por fotos reales del negocio.
_PHOTOS: dict[Sector, tuple[str, ...]] = {
    Sector.BAR: ("photo-1554118811-1e0d58224f24", "photo-1414235077428-338989a2e8c0",
                 "photo-1509440159596-0249088772ff"),
    Sector.RESTAURANTE: ("photo-1517248135467-4c7edcad34c4", "photo-1414235077428-338989a2e8c0",
                         "photo-1554118811-1e0d58224f24"),
    Sector.PANADERIA: ("photo-1509440159596-0249088772ff", "photo-1414235077428-338989a2e8c0",
                       "photo-1554118811-1e0d58224f24"),
    Sector.DENTAL: ("photo-1629909613654-28e377c37b09", "photo-1588776814546-1ffcf47267a5"),
    Sector.FISIO: ("photo-1519823551278-64ac92734fb1", "photo-1629909613654-28e377c37b09"),
    Sector.VETERINARIO: ("photo-1576201836106-db1758fd1c97", "photo-1629909613654-28e377c37b09"),
    Sector.FARMACIA: ("photo-1576602976047-174e57a47881", "photo-1576201836106-db1758fd1c97"),
    Sector.PELUQUERIA: ("photo-1560066984-138dadb4c035", "photo-1570172619644-dfd03ed5d881",
                        "photo-1521590832167-7bcbfaa6381f"),
    Sector.ESTETICA: ("photo-1570172619644-dfd03ed5d881", "photo-1560066984-138dadb4c035",
                      "photo-1519823551278-64ac92734fb1"),
    Sector.TALLER: ("photo-1486262715619-67b85e0b08d3", "photo-1487754180451-c456f719a1fc"),
    Sector.REFORMAS: ("photo-1503387762-592deb58ef4e", "photo-1486262715619-67b85e0b08d3"),
    Sector.ASESORIA: ("photo-1497366216548-37526070297c", "photo-1554118811-1e0d58224f24"),
    Sector.INMOBILIARIA: ("photo-1560518883-ce09059eeffa", "photo-1497366216548-37526070297c"),
    Sector.GIMNASIO: ("photo-1534438327276-14e5300c3a48", "photo-1486262715619-67b85e0b08d3"),
    Sector.COMERCIO: ("photo-1441986300917-64674bd600d8", "photo-1560066984-138dadb4c035"),
    Sector.AUTONOMO: ("photo-1503387762-592deb58ef4e", "photo-1487754180451-c456f719a1fc"),
}

# Opiniones de muestra (el operador las sustituye por reseñas reales con permiso).
_TESTI: dict[Sector, str] = {
    Sector.BAR: "Se almuerza de maravilla y el trato es de los de antes | Marta G.\n"
                "El mejor almuerzo de obra del Puerto, sin discusión | Vicente R.",
    Sector.RESTAURANTE: "El arroz, espectacular. Repetiremos seguro | Laura M.\n"
                        "Producto de primera y trato cercano. Una joya | Andrés P.",
    Sector.PANADERIA: "El pan de masa madre es otro nivel | Carmen L.\n"
                      "Las tartas por encargo siempre perfectas | Nuria S.",
    Sector.DENTAL: "Me explicaron todo con claridad y sin prisas. Encantada | Pilar V.\n"
                   "Pánico al dentista y aquí me lo quitaron. Profesionales | Jorge T.",
    Sector.FISIO: "En tres sesiones volví a entrenar sin dolor | Raúl D.\n"
                  "Saben lo que hacen y te lo explican. Recomendable | Ana C.",
    Sector.VETERINARIO: "Cuidaron a mi perro como si fuera suyo | Elena B.\n"
                        "Urgencia de noche resuelta. Eternamente agradecida | Marcos F.",
    Sector.PELUQUERIA: "Salí con el color soñado y el pelo cuidadísimo | Sara N.\n"
                       "Por fin alguien que escucha lo que quieres | Lucía H.",
    Sector.ESTETICA: "Trato exquisito y resultados desde la primera sesión | Beatriz O.\n"
                     "Un sitio para desconectar y cuidarte de verdad | Cristina A.",
    Sector.TALLER: "Presupuesto cerrado y cumplido al céntimo | José M.\n"
                   "Honrados y rápidos. Mi taller de confianza | Fernando G.",
    Sector.REFORMAS: "Reformaron el baño en plazo y sin sorpresas | Rosa P.\n"
                     "Limpios, serios y buen acabado. Muy contentos | Daniel V.",
    Sector.ASESORIA: "Me quitaron el papeleo de encima. Un alivio | Óscar L.\n"
                     "Cercanos y siempre disponibles. Un lujo para el autónomo | Eva R.",
    Sector.INMOBILIARIA: "Vendieron mi piso en tres semanas. Increíble | Manuel S.\n"
                         "Transparencia total desde el primer día | Patricia D.",
    Sector.GIMNASIO: "Ambiente genial y entrenadores que se implican | Pablo A.\n"
                     "Sin permanencia y con resultados. Enganchado | Iván M.",
    Sector.COMERCIO: "Trato de barrio y producto que no encuentras en otro sitio | Teresa G.\n"
                     "Siempre me asesoran bien. Da gusto comprar aquí | Rubén C.",
}


def demo_data(sector: Sector) -> dict[str, str]:
    """Datos de ejemplo COMPLETOS de un sector (con los comunes mezclados)."""
    base = dict(_COMMON)
    base.update(_DEMO.get(sector, _DEMO[Sector.AUTONOMO]))
    base["sector"] = sector.value
    photos = _PHOTOS.get(sector)
    if photos:
        base["photos"] = "\n".join(_u(p) for p in photos)
    testi = _TESTI.get(sector)
    if testi:
        base["testimonials"] = testi
    return base
