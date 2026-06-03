"""Contenido curado por sector (el "playbook").

Cada sector tiene un proceso ("cómo trabajamos"), unas preguntas frecuentes, un
mapa de beneficios por servicio, titulares y textos de apoyo. La plantilla es
100% agnóstica del sector: recorre estas estructuras. Añadir riqueza a un sector
es editar SU entrada aquí, nunca el HTML.

Honestidad: todo es contenido genérico-verdadero o se rellena con datos reales
del negocio. Nunca se inventan cifras, reseñas ni premios.
"""

from __future__ import annotations

from dataclasses import dataclass

from faro.business import Sector


@dataclass(frozen=True)
class ProcessStep:
    title: str
    description: str


@dataclass(frozen=True)
class FaqItem:
    question: str
    answer: str
    """Puede contener {phone}, {city}, {address}; se rellena con los datos del negocio."""
    needs_address: bool = False


@dataclass(frozen=True)
class SectorPlaybook:
    process: tuple[ProcessStep, ...]
    faq: tuple[FaqItem, ...]
    service_benefits: dict[str, str]
    service_icons: dict[str, str]
    final_cta_headline: str
    gallery_title: str
    stat_fallback: str
    trust_chip: str
    generic_benefit: str
    icon: str  # icono de sector por defecto (nombre en icons.py)
    # Vocabulario de la oferta: cómo se llama lo que vende este negocio. Evita
    # forzar "servicios" en una panadería (productos) o un bar (carta). Por
    # defecto "servicios"; se sobre-escribe en los sectores que difieren.
    offer_word: str = "servicios"  # plural, para la etiqueta de la cifra y el formulario
    offer_heading: str = "Nuestros servicios"  # título de la sección
    offer_verb: str = "ofrecemos"  # verbo para la frase de "sobre nosotros"


# Procesos reutilizables por arquetipo (varios sectores comparten flujo).
_APPOINTMENT = (
    ProcessStep("Pide cita", "Por WhatsApp o teléfono, cuando te venga bien."),
    ProcessStep(
        "Te valoramos",
        "En la primera visita te explicamos qué necesitas, sin compromiso.",
    ),
    ProcessStep("Tu tratamiento", "Un plan a tu medida y a tu ritmo."),
    ProcessStep("Seguimiento", "Te acompañamos hasta que estás como querías."),
)
_QUOTE = (
    ProcessStep("Cuéntanos", "Nos dices qué necesitas y le echamos un ojo."),
    ProcessStep("Presupuesto cerrado", "Precio claro, sin sorpresas ni letra pequeña."),
    ProcessStep("Lo hacemos", "Manos a la obra con materiales y trabajo de calidad."),
    ProcessStep("Entrega y garantía", "Te lo dejamos perfecto y respondemos por ello."),
)
_FOOD = (
    ProcessStep("Reserva o pásate", "Te guardamos sitio o te atendemos al momento."),
    ProcessStep("Elige", "Te ayudamos con la carta y lo que más te apetezca."),
    ProcessStep("Disfruta", "A comer tranquilo. Del resto nos encargamos nosotros."),
)
_RETAIL = (
    ProcessStep("Pregúntanos", "Dinos qué buscas, sin agobios."),
    ProcessStep("Te asesoramos", "Te ayudamos a elegir lo que de verdad necesitas."),
    ProcessStep("Llévatelo hoy", "Sin esperas, cuando lo necesitas."),
)
_ADVISORY = (
    ProcessStep("Cuéntanos tu caso", "Una primera charla para entender qué necesitas."),
    ProcessStep("Te proponemos", "Te explicamos las opciones con claridad."),
    ProcessStep("Nos encargamos", "Tú a lo tuyo; del papeleo nos ocupamos nosotros."),
)
_GIMNASIO = (
    ProcessStep(
        "Ven a probar",
        "Un día gratis para que conozcas las instalaciones sin compromiso.",
    ),
    ProcessStep(
        "Plan a tu nivel",
        "Te hacemos una rutina adaptada a tus objetivos y tu forma física.",
    ),
    ProcessStep(
        "A por tus objetivos",
        "Entrenamos contigo y ajustamos el plan según progresas.",
    ),
)

# Plantilla de FAQ común reutilizable (la ubicación se rellena con datos reales).
_FAQ_WHERE = FaqItem(
    "¿Dónde estáis y cómo os contacto?",
    "Estamos en {address}, en {city}."
    " Escríbenos por WhatsApp al {phone} y te atendemos enseguida.",
    needs_address=True,
)


_PLAYBOOK: dict[Sector, SectorPlaybook] = {
    Sector.DENTAL: SectorPlaybook(
        process=_APPOINTMENT,
        faq=(
            FaqItem(
                "¿La primera visita tiene coste?",
                "Te lo decimos al pedir cita."
                " Lo importante es que vengas y te valoremos sin compromiso.",
            ),
            FaqItem(
                "¿Atendéis urgencias?",
                "Sí. Si tienes dolor o se te ha roto algo, escríbenos al {phone}"
                " y te damos hueco lo antes posible.",
            ),
            FaqItem(
                "¿Se pueden financiar los tratamientos?",
                "Muchos tratamientos se pueden pagar a plazos."
                " Pregúntanos y te lo explicamos sin compromiso.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "limpieza": "eliminamos sarro y placa para una boca más sana",
            "implante": "recupera las piezas que te faltan",
            "ortodoncia": "alineamos tu sonrisa a tu ritmo",
            "blanqueamiento": "una sonrisa más blanca en pocas sesiones",
            "endodoncia": "salvamos la pieza y te quitamos el dolor",
        },
        service_icons={
            "limpieza": "sparkle",
            "implante": "tooth",
            "ortodoncia": "tooth",
            "revisión": "check",
        },
        final_cta_headline="Pide tu cita hoy",
        gallery_title="Nuestra clínica",
        stat_fallback="Sin esperas",
        trust_chip="Trato cercano y profesional",
        generic_benefit="te lo dejamos perfecto",
        icon="tooth",
        offer_word="tratamientos",
        offer_heading="Nuestros tratamientos",
    ),
    Sector.FISIO: SectorPlaybook(
        process=_APPOINTMENT,
        faq=(
            FaqItem(
                "¿Necesito derivación médica?",
                "No es obligatorio. Puedes venir directamente"
                " y te hacemos una valoración inicial.",
            ),
            FaqItem(
                "¿Cuántas sesiones necesitaré?",
                "Depende de cada caso."
                " En la primera visita te damos una estimación honesta.",
            ),
            FaqItem(
                "¿Atendéis lesiones deportivas?",
                "Sí, trabajamos con deportistas de todos los niveles,"
                " desde lesiones hasta prevención.",
            ),
            FaqItem(
                "¿Hacéis fisioterapia a domicilio?",
                "Consúltanos. Según disponibilidad podemos valorarlo."
                " Escríbenos al {phone}.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "fisioterapia": "recupera movilidad y reduce el dolor sin pastillas",
            "masaje": "alivia la tensión acumulada y mejora la circulación",
            "electroterapia": "acelera la recuperación de lesiones musculares",
            "pilates": "fortalece el core y mejora tu postura",
            "osteopatía": "tratamiento global para bloqueos y dolores crónicos",
        },
        service_icons={
            "fisioterapia": "heart",
            "masaje": "heart",
            "pilates": "leaf",
            "osteopatía": "shield",
            "electroterapia": "sparkle",
        },
        final_cta_headline="Pide tu cita",
        gallery_title="Nuestro centro",
        stat_fallback="Primera valoración sin compromiso",
        trust_chip="Profesionales con experiencia real",
        generic_benefit="te ayudamos a recuperarte",
        icon="heart",
        offer_word="tratamientos",
        offer_heading="Tratamientos y terapias",
    ),
    Sector.VETERINARIO: SectorPlaybook(
        process=_APPOINTMENT,
        faq=(
            FaqItem(
                "¿Atendéis urgencias?",
                "Sí. Si tu mascota necesita atención urgente,"
                " llámanos al {phone} y te decimos cómo actuar.",
            ),
            FaqItem(
                "¿Hacéis vacunaciones y desparasitaciones?",
                "Sí, llevamos el calendario sanitario completo de tu mascota.",
            ),
            FaqItem(
                "¿Atendéis perros y gatos? ¿Y otras mascotas?",
                "Atendemos perros y gatos."
                " Consúltanos si tienes otro tipo de mascota.",
            ),
            FaqItem(
                "¿Puedo pedir cita online?",
                "Escríbenos por WhatsApp al {phone}"
                " o llámanos y lo gestionamos rápido.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "consulta": "diagnóstico claro y trato cuidadoso con tu mascota",
            "vacunación": "protege a tu animal con el calendario al día",
            "cirugía": "procedimientos seguros con seguimiento postoperatorio",
            "peluquería canina": "tu mascota guapa y cómoda",
            "analíticas": "detectamos problemas antes de que se noten",
        },
        service_icons={
            "consulta": "paw",
            "vacunación": "shield",
            "cirugía": "heart",
            "peluquería canina": "scissors",
            "analíticas": "check",
        },
        final_cta_headline="Pide cita para tu mascota",
        gallery_title="Nuestra clínica",
        stat_fallback="Trato cuidadoso con cada animal",
        trust_chip="Tu mascota en buenas manos",
        generic_benefit="cuidamos de tu mascota",
        icon="paw",
    ),
    Sector.PELUQUERIA: SectorPlaybook(
        process=_APPOINTMENT,
        faq=(
            FaqItem(
                "¿Hay que pedir cita?",
                "Recomendamos pedir cita para evitar esperas."
                " Escríbenos al {phone} o por WhatsApp.",
            ),
            FaqItem(
                "¿Hacéis tratamientos de color?",
                "Sí, hacemos mechas, tintes, balayage y más."
                " Consúltanos y te asesoramos.",
            ),
            FaqItem(
                "¿Atendéis a niños?",
                "Sí, cortamos el pelo a toda la familia.",
            ),
            FaqItem(
                "¿Cuánto tarda un servicio?",
                "Un corte suele llevar 30-45 minutos."
                " Coloraciones y tratamientos pueden llevar más."
                " Te lo decimos al reservar.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "corte": "el look que te queda bien, adaptado a tu cara y tu estilo",
            "mechas": "color natural y luminoso sin estropear el cabello",
            "tinte": "cubre canas con un acabado natural y duradero",
            "alisado": "cabello liso y manejable durante meses",
            "tratamiento": "recupera el brillo y la salud de tu pelo",
        },
        service_icons={
            "corte": "scissors",
            "mechas": "sparkle",
            "tinte": "sparkle",
            "alisado": "leaf",
            "tratamiento": "heart",
        },
        final_cta_headline="Reserva tu cita",
        gallery_title="Algunos de nuestros trabajos",
        stat_fallback="Cita disponible esta semana",
        trust_chip="Profesionales de confianza en {city}",
        generic_benefit="te dejamos perfecto",
        icon="scissors",
    ),
    Sector.ESTETICA: SectorPlaybook(
        process=_APPOINTMENT,
        faq=(
            FaqItem(
                "¿Hay que pedir cita?",
                "Sí, trabajamos con cita para dedicarte el tiempo que mereces."
                " Escríbenos al {phone}.",
            ),
            FaqItem(
                "¿Hacéis diagnóstico de piel?",
                "En la primera visita analizamos tu piel"
                " y te recomendamos el tratamiento más adecuado.",
            ),
            FaqItem(
                "¿Cuántas sesiones necesito para ver resultados?",
                "Depende del tratamiento."
                " Te lo explicamos con claridad antes de empezar.",
            ),
            FaqItem(
                "¿Los productos que usáis son seguros?",
                "Trabajamos con productos de calidad contrastada,"
                " testados dermatológicamente.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "facial": "piel más limpia, hidratada y luminosa desde la primera sesión",
            "depilación": "piel suave y sin irritaciones",
            "masaje": "relájate y elimina la tensión acumulada",
            "manicura": "uñas cuidadas con un acabado duradero",
            "pestañas": "mirada más expresiva sin esfuerzo diario",
        },
        service_icons={
            "facial": "sparkle",
            "depilación": "leaf",
            "masaje": "heart",
            "manicura": "scissors",
            "pestañas": "sparkle",
        },
        final_cta_headline="Reserva tu tratamiento",
        gallery_title="Nuestro centro",
        stat_fallback="Trato personalizado en cada visita",
        trust_chip="Tu bienestar, nuestra prioridad",
        generic_benefit="te cuidas y se nota",
        icon="scissors",
        offer_word="tratamientos",
        offer_heading="Nuestros tratamientos",
    ),
    Sector.RESTAURANTE: SectorPlaybook(
        process=_FOOD,
        faq=(
            FaqItem(
                "¿Hay que reservar?",
                "No es obligatorio, pero para grupos o fines de semana"
                " recomendamos llamar al {phone}.",
            ),
            FaqItem(
                "¿Tenéis opciones sin gluten o vegetarianas?",
                "Sí. Avísanos al reservar y lo preparamos con gusto.",
            ),
            FaqItem(
                "¿Hacéis para llevar?",
                "Sí. Llama al {phone} o escríbenos por WhatsApp"
                " y pedimos que lo tengan listo.",
            ),
            FaqItem(
                "¿Aceptáis grupos o celebraciones?",
                "Sí. Cuéntanos qué necesitas"
                " y buscamos la mejor opción para tu evento.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "menú del día": "cocina casera a precio justo, de lunes a viernes",
            "carta": "platos elaborados con producto fresco y de temporada",
            "para llevar": "la misma calidad del restaurante, en tu casa",
            "celebraciones": "organizamos tu evento sin complicaciones",
        },
        service_icons={
            "menú del día": "fork",
            "carta": "fork",
            "para llevar": "bag",
            "celebraciones": "calendar",
        },
        final_cta_headline="Reserva tu mesa",
        gallery_title="Nuestra carta",
        stat_fallback="Producto fresco cada día",
        trust_chip="Cocina de verdad, sin artificios",
        generic_benefit="te lo ponemos fácil",
        icon="fork",
        offer_word="platos",
        offer_heading="Nuestra carta",
        offer_verb="servimos",
    ),
    Sector.BAR: SectorPlaybook(
        process=_FOOD,
        faq=(
            FaqItem(
                "¿A qué hora abrís?",
                "Estamos en {address}."
                " Consúltanos el horario al {phone} o por WhatsApp.",
            ),
            FaqItem(
                "¿Tenéis tapas o bocadillos?",
                "Sí, tenemos una selección de tapas y bocadillos"
                " para acompañar tu rato.",
            ),
            FaqItem(
                "¿Ponéis desayunos?",
                "Sí. Ven a empezar bien el día con un buen café y algo de comer.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "café": "el mejor café para empezar el día con buen pie",
            "tapas": "tapas caseras para acompañar la caña o el vermut",
            "bocadillos": "bocadillos generosos con pan de calidad",
            "desayunos": "desayuno completo para arrancar con energía",
        },
        service_icons={
            "café": "coffee",
            "tapas": "fork",
            "bocadillos": "bread",
            "desayunos": "coffee",
        },
        final_cta_headline="Pásate a tomar algo",
        gallery_title="Nuestro local",
        stat_fallback="Abierto cada mañana",
        trust_chip="Tu bar de siempre",
        generic_benefit="te atendemos como mereces",
        icon="coffee",
        offer_word="platos",
        offer_heading="Nuestra carta",
        offer_verb="servimos",
    ),
    Sector.COMERCIO: SectorPlaybook(
        process=_RETAIL,
        faq=(
            FaqItem(
                "¿Puedo hacer devoluciones?",
                "Sí. Consúltanos las condiciones al {phone}"
                " y lo gestionamos sin complicaciones.",
            ),
            FaqItem(
                "¿Hacéis pedidos o encargos?",
                "Sí. Si no tenemos algo en tienda, podemos pedirlo. Pregúntanos.",
            ),
            FaqItem(
                "¿Tenéis tienda online?",
                "Consúltanos al {phone} o escríbenos por WhatsApp para más información.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "atención personalizada": "te ayudamos a encontrar lo que buscas sin agobios",
            "producto local": (
                "apoya el comercio de {city}"
                " y encuentra cosas que no hay en las grandes superficies"
            ),
            "encargos": "si no lo tenemos, lo pedimos por ti",
        },
        service_icons={
            "atención personalizada": "heart",
            "producto local": "leaf",
            "encargos": "bag",
        },
        final_cta_headline="Pásate o contáctanos",
        gallery_title="Nuestra tienda",
        stat_fallback="Atención sin prisas",
        trust_chip="Comercio de {city} de toda la vida",
        generic_benefit="lo tenemos o lo pedimos",
        icon="bag",
        offer_word="productos",
        offer_heading="Lo que encontrarás",
        offer_verb="tenemos",
    ),
    Sector.PANADERIA: SectorPlaybook(
        process=_FOOD,
        faq=(
            FaqItem(
                "¿A qué hora está listo el pan?",
                "El pan recién hecho sale por la mañana."
                " Consúltanos el horario exacto al {phone}.",
            ),
            FaqItem(
                "¿Hacéis pan sin gluten?",
                "Consúltanos. Dependiendo de la demanda"
                " podemos elaborarlo o encargarlo.",
            ),
            FaqItem(
                "¿Se puede encargar para eventos?",
                "Sí. Llámanos al {phone} con antelación"
                " y preparamos lo que necesites.",
            ),
            FaqItem(
                "¿Vendéis bollería y pasteles?",
                "Sí, tenemos una selección de bollería y repostería elaborada cada día.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "pan artesano": "elaborado cada día con harinas de calidad",
            "bollería": "croissants, magdalenas y dulces recién horneados",
            "repostería": "tartas y pasteles para tus celebraciones",
            "encargos": "preparamos lo que necesitas para bodas, comuniones o eventos",
        },
        service_icons={
            "pan artesano": "bread",
            "bollería": "bread",
            "repostería": "sparkle",
            "encargos": "calendar",
        },
        final_cta_headline="Pasa a por el pan",
        gallery_title="Nuestros productos",
        stat_fallback="Pan recién hecho cada mañana",
        trust_chip="Elaboración propia, cada día",
        generic_benefit="hecho con cariño y buenos ingredientes",
        icon="bread",
        offer_word="productos",
        offer_heading="Nuestros productos",
        offer_verb="tenemos",
    ),
    Sector.TALLER: SectorPlaybook(
        process=_QUOTE,
        faq=(
            FaqItem(
                "¿El presupuesto es gratis?",
                "Sí. Te miramos el coche y te damos precio sin compromiso,"
                " sin cobrarte por ello.",
            ),
            FaqItem(
                "¿Pasáis la ITV?",
                "Sí, hacemos las revisiones previas a la ITV"
                " y te acompañamos en el proceso.",
            ),
            FaqItem(
                "¿Trabajáis con todas las marcas?",
                "Trabajamos con la mayoría de marcas de turismos y furgonetas."
                " Consúltanos.",
            ),
            FaqItem(
                "¿Cuánto tarda la reparación?",
                "Depende de la avería."
                " Te damos un plazo estimado al hacer el presupuesto.",
            ),
            FaqItem(
                "¿Hacéis sustitución de neumáticos?",
                "Sí. Escríbenos al {phone} y te decimos disponibilidad y precios.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "mecánica": "reparamos lo que falla con rapidez y garantía",
            "mantenimiento": "revisiones periódicas para que tu coche no te falle",
            "neumáticos": "montaje y equilibrado al mejor precio",
            "pre-itv": "te preparamos para pasar la ITV sin sustos",
            "electricidad": "diagnóstico y reparación del sistema eléctrico",
        },
        service_icons={
            "mecánica": "wrench",
            "mantenimiento": "car",
            "neumáticos": "car",
            "pre-itv": "check",
            "electricidad": "sparkle",
        },
        final_cta_headline="Pide presupuesto sin compromiso",
        gallery_title="Nuestro taller",
        stat_fallback="Presupuesto sin compromiso",
        trust_chip="Tu coche, en buenas manos",
        generic_benefit="te lo dejamos a punto",
        icon="wrench",
    ),
    Sector.GIMNASIO: SectorPlaybook(
        process=_GIMNASIO,
        faq=(
            FaqItem(
                "¿Hay permanencia?",
                "No. Puedes apuntarte y darte de baja cuando quieras,"
                " sin penalización.",
            ),
            FaqItem(
                "¿Puedo venir a probar?",
                "Sí. El primer día es gratis para que veas las instalaciones"
                " sin compromiso.",
            ),
            FaqItem(
                "¿Hay clases dirigidas?",
                "Sí, tenemos clases de grupo para todos los niveles."
                " Consúltanos el horario.",
            ),
            FaqItem(
                "¿Tenéis entrenador personal?",
                "Sí. Podemos asignarte un entrenador personal"
                " para que progreses más rápido.",
            ),
            FaqItem(
                "¿Cuál es el horario?",
                "Consúltanos el horario actualizado al {phone} o pásate a vernos.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "sala de musculación": "equipamiento moderno para entrenar a tu ritmo",
            "clases dirigidas": "cardio, fuerza y flexibilidad con instructor",
            "entrenamiento personal": (
                "plan 100% a tu medida para llegar a tus objetivos"
            ),
            "zona cardio": "máquinas de última generación para quemar calorías",
        },
        service_icons={
            "sala de musculación": "dumbbell",
            "clases dirigidas": "calendar",
            "entrenamiento personal": "heart",
            "zona cardio": "dumbbell",
        },
        final_cta_headline="Ven a probar gratis",
        gallery_title="Nuestras instalaciones",
        stat_fallback="Tu primer día gratis",
        trust_chip="Sin permanencia, sin excusas",
        generic_benefit="te ayudamos a ponerte en forma",
        icon="dumbbell",
        offer_heading="Clases y servicios",
    ),
    Sector.FARMACIA: SectorPlaybook(
        process=_RETAIL,
        faq=(
            FaqItem(
                "¿Hacéis pedidos o encargos?",
                "Sí. Si no tenemos algo en stock,"
                " lo pedimos y te avisamos cuando llega.",
            ),
            FaqItem(
                "¿Preparáis fórmulas magistrales?",
                "Consúltanos. Trabajamos con laboratorios"
                " de fórmulas magistrales de confianza.",
            ),
            FaqItem(
                "¿Podéis asesorarme sin receta?",
                "Sí. Nuestros farmacéuticos pueden orientarte"
                " sobre medicamentos sin receta y parafarmacia.",
            ),
            FaqItem(
                "¿Medís la tensión o el azúcar?",
                "Sí. Pásate y te lo hacemos en el momento, sin cita previa.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "medicamentos": "dispensación rápida con asesoramiento farmacéutico",
            "parafarmacia": "dermocosméticos, higiene y cuidado personal de calidad",
            "consejo farmacéutico": (
                "resolvemos tus dudas de salud con criterio profesional"
            ),
            "ortopedia": "productos de movilidad, vendajes y ayudas técnicas",
            "encargos": "si no lo tenemos, lo pedimos",
        },
        service_icons={
            "medicamentos": "pill",
            "parafarmacia": "sparkle",
            "consejo farmacéutico": "shield",
            "ortopedia": "heart",
            "encargos": "bag",
        },
        final_cta_headline="Pásate o llámanos",
        gallery_title="Nuestra farmacia",
        stat_fallback="Asesoramiento farmacéutico gratuito",
        trust_chip="Tu farmacia de siempre",
        generic_benefit="te orientamos con criterio profesional",
        icon="pill",
        offer_word="productos y servicios",
        offer_heading="Productos y servicios",
        offer_verb="tenemos",
    ),
    Sector.ASESORIA: SectorPlaybook(
        process=_ADVISORY,
        faq=(
            FaqItem(
                "¿Lleváis autónomos y pymes?",
                "Sí, es nuestro perfil habitual."
                " Nos adaptamos a negocios de cualquier tamaño.",
            ),
            FaqItem(
                "¿Qué incluye la gestoría mensual?",
                "IVA, IRPF, nóminas, seguridad social y todo el papeleo al día."
                " Cuéntanos tu caso.",
            ),
            FaqItem(
                "¿Podéis ayudarme a darme de alta como autónomo?",
                "Sí. Te guiamos en el proceso completo"
                " sin que tengas que entender de burocracia.",
            ),
            FaqItem(
                "¿Lleváis la contabilidad completa?",
                "Sí, desde la contabilidad analítica hasta el depósito de cuentas.",
            ),
            FaqItem(
                "¿Cuánto cuesta?",
                "Depende del volumen de trabajo."
                " Te hacemos un presupuesto personalizado sin compromiso.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "asesoría fiscal": "paga lo justo, sin errores ni sustos de Hacienda",
            "contabilidad": "cuentas al día y listas para cualquier auditoría",
            "laboral": "nóminas, altas y bajas sin complicaciones",
            "sociedades": "constitución y gestión de empresas de principio a fin",
            "alta autónomos": "te damos de alta y te explicamos lo que necesitas saber",
        },
        service_icons={
            "asesoría fiscal": "chart",
            "contabilidad": "chart",
            "laboral": "briefcase",
            "sociedades": "briefcase",
            "alta autónomos": "check",
        },
        final_cta_headline="Pide una consulta gratuita",
        gallery_title="Nuestra asesoría",
        stat_fallback="Primera consulta sin compromiso",
        trust_chip="Profesionales de la zona, sin letra pequeña",
        generic_benefit="del papeleo nos encargamos nosotros",
        icon="chart",
    ),
    Sector.INMOBILIARIA: SectorPlaybook(
        process=_ADVISORY,
        faq=(
            FaqItem(
                "¿Cobráis por enseñar pisos?",
                "No. Enseñar propiedades es gratis y sin compromiso.",
            ),
            FaqItem(
                "¿Gestionáis pisos de alquiler?",
                "Sí, gestionamos alquileres de principio a fin:"
                " búsqueda de inquilinos, contratos y seguimiento.",
            ),
            FaqItem(
                "¿Cuánto cobráis de comisión por vender?",
                "Te lo explicamos con transparencia"
                " desde el primer momento, sin sorpresas.",
            ),
            FaqItem(
                "¿Cuánto tiempo se tarda en vender un piso?",
                "Depende del precio y la zona."
                " Te damos una estimación realista desde el primer día.",
            ),
            FaqItem(
                "¿Tasáis pisos gratis?",
                "Sí. Llámanos al {phone} y concertamos una valoración sin compromiso.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "compraventa": "te acompañamos en cada paso hasta firmar ante notario",
            "alquiler": "encontramos al inquilino adecuado y gestionamos el contrato",
            "tasación": "valoración realista del inmueble, sin inflar precios",
            "gestión documental": (
                "nos ocupamos del papeleo para que no tengas que hacerlo tú"
            ),
        },
        service_icons={
            "compraventa": "house",
            "alquiler": "key",
            "tasación": "chart",
            "gestión documental": "briefcase",
        },
        final_cta_headline="Encuentra tu hogar",
        gallery_title="Nuestras propiedades",
        stat_fallback="Asesoramiento inmobiliario gratuito",
        trust_chip="Conocemos el mercado de {city}",
        generic_benefit="te ayudamos a encontrar lo que buscas",
        icon="house",
    ),
    Sector.REFORMAS: SectorPlaybook(
        process=_QUOTE,
        faq=(
            FaqItem(
                "¿El presupuesto es cerrado?",
                "Sí. Te damos un precio cerrado antes de empezar"
                " para que no haya sorpresas al final.",
            ),
            FaqItem(
                "¿Hacéis reformas integrales?",
                "Sí, desde cocinas y baños hasta reformas completas"
                " de pisos y locales.",
            ),
            FaqItem(
                "¿Cuánto tarda una reforma?",
                "Depende del alcance."
                " Te damos un plazo concreto en el presupuesto.",
            ),
            FaqItem(
                "¿Tenéis seguro de responsabilidad civil?",
                "Sí. Trabajamos con todas las garantías legales"
                " para protegerte a ti y a la obra.",
            ),
            FaqItem(
                "¿Gestionáis los permisos de obra?",
                "Sí, nos encargamos de la documentación y los permisos necesarios.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={
            "reforma de baño": "baño nuevo en el plazo acordado, sin polvo extra",
            "reforma de cocina": "cocina funcional y a tu gusto, llave en mano",
            "pintura": "acabados limpios y duraderos",
            "reforma integral": "transformamos el espacio de principio a fin",
            "instalaciones": "fontanería, electricidad y carpintería con garantía",
        },
        service_icons={
            "reforma de baño": "hammer",
            "reforma de cocina": "hammer",
            "pintura": "sparkle",
            "reforma integral": "wrench",
            "instalaciones": "wrench",
        },
        final_cta_headline="Pide presupuesto sin compromiso",
        gallery_title="Trabajos realizados",
        stat_fallback="Presupuesto cerrado, sin sorpresas",
        trust_chip="Precio claro desde el primer día",
        generic_benefit="te lo dejamos como nuevo",
        icon="hammer",
    ),
    Sector.AUTONOMO: SectorPlaybook(
        process=_RETAIL,
        faq=(
            FaqItem(
                "¿En qué podéis ayudarme?",
                "Somos profesionales con experiencia."
                " Cuéntanos lo que necesitas y te decimos si podemos ayudarte.",
            ),
            FaqItem(
                "¿Dais presupuesto sin compromiso?",
                "Sí. Escríbenos al {phone} y valoramos tu caso sin coste.",
            ),
            FaqItem(
                "¿Cuánto tiempo tardaréis?",
                "Depende del trabajo."
                " Te damos un plazo concreto al hacerte el presupuesto.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={},
        service_icons={},
        final_cta_headline="Pide información",
        gallery_title="Nuestros trabajos",
        stat_fallback="Presupuesto sin compromiso",
        trust_chip="Profesional de confianza en {city}",
        generic_benefit="te ayudamos a resolverlo",
        icon="briefcase",
    ),
    Sector.OTRO: SectorPlaybook(
        process=_RETAIL,
        faq=(
            FaqItem(
                "¿Cómo os contacto?",
                "Escríbenos por WhatsApp al {phone} y te atendemos enseguida.",
            ),
            _FAQ_WHERE,
        ),
        service_benefits={},
        service_icons={},
        final_cta_headline="Contáctanos",
        gallery_title="Nuestro trabajo",
        stat_fallback="Cerca de ti",
        trust_chip="Cerca de ti, cuando lo necesitas",
        generic_benefit="te ayudamos con lo que necesites",
        icon="pin",
    ),
}

# Arquetipos para los sectores que aún no tienen entrada propia (se completan abajo).
_ARCHETYPE_DEFAULT = _PLAYBOOK[Sector.OTRO]


def playbook_for(sector: Sector) -> SectorPlaybook:
    return _PLAYBOOK.get(sector, _ARCHETYPE_DEFAULT)


# Ejemplos de "datos destacados" sugeridos por sector (placeholder del formulario).
# Guían al dueño para que aporte hechos reales en vez de que se inventen.
_EXTRA_HINTS: dict[Sector, str] = {
    Sector.DENTAL: "Primera visita: gratis\nFinanciación: Sí\nUrgencias: Sí",
    Sector.FISIO: "A domicilio: Sí\nFisioterapia deportiva: Sí",
    Sector.VETERINARIO: "Urgencias 24h: Sí\nAnimales: perros, gatos\nPeluquería canina: Sí",
    Sector.PELUQUERIA: "Con cita o sin cita: Ambas\nMarcas: L'Oréal",
    Sector.ESTETICA: "Tratamientos estrella: láser, presoterapia",
    Sector.RESTAURANTE: "Tipo de cocina: mediterránea\nMenú del día: 13€\nTerraza: Sí",
    Sector.BAR: "Desayunos: Sí\nTerraza: Sí\nTapas: Sí",
    Sector.COMERCIO: "Qué vendéis: ropa de mujer\nEnvíos: Sí",
    Sector.PANADERIA: "Horneado propio: Sí\nSin gluten: Sí\nEncargos: Sí",
    Sector.TALLER: "Marcas: todas\nITV: te la gestionamos\nCoche de cortesía: Sí",
    Sector.GIMNASIO: "Sin permanencia: Sí\nClases: spinning, yoga\nEntrenador personal: Sí",
    Sector.FARMACIA: "Guardia: Sí\nOrtopedia: Sí\nEncargos: Sí",
    Sector.ASESORIA: "Clientes: autónomos y pymes\nÁreas: laboral, fiscal, contable",
    Sector.INMOBILIARIA: "Operaciones: venta y alquiler\nTasación: gratis\nZona: Camp de Morvedre",
    Sector.REFORMAS: "Tipos: baños, cocinas, integral\nPresupuesto: gratis\nGarantía: Sí",
    Sector.AUTONOMO: "Servicio: lo que ofreces\nZona: a domicilio",
}


def extra_hint(sector: Sector) -> str:
    """Placeholder sugerido para el campo 'datos destacados' del formulario."""
    return _EXTRA_HINTS.get(sector, "Algo que te haga destacar: Sí")
