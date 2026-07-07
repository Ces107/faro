"""Motor de motion del producto (autocontenido, sin CDN).

Concatena las librerías vendorizadas (``faro.engine.vendor`` las embebe inline) con
un IIFE de inicialización (``_INIT_JS``) que AUGMENTA la capa vanilla de
``blocks/script.html`` sin sustituirla. Todo cuelga de un único *gate*: si no hay
GSAP o el usuario pide ``prefers-reduced-motion``, se revela todo en estático y se
sale — nunca hay scroll-jacking ni contenido que dependa de JS para verse.

Cada familia activa UNA firma (un momento pinneado/parallax) despachada por el
atributo ``data-signature`` del ``<body>``; ``signature_for`` resuelve la firma por
defecto de la familia (sobrescribible por cliente con ``DesignTokens.signature``).
"""

from __future__ import annotations

from functools import lru_cache

from faro.engine.design import DesignTokens
from faro.engine.vendor import motion_libs_inline

# Firma por defecto de cada familia (el "momento wow"). Sobrescribible por token.
_DEFAULT_SIG: dict[str, str] = {
    "carta": "carta",
    "clinica": "clinica",
    "autoridad": "authority",
    "industrial": "poster",
    "estudio": "gallery",
    "gimnasio": "poster-gym",
    "aurora": "deck",
}


def signature_for(tokens: DesignTokens) -> str:
    """La firma de motion de la familia (o la sobrescrita por el token)."""
    return tokens.signature or _DEFAULT_SIG.get(tokens.name, "deck")


# El IIFE de inicialización. Se ejecuta DESPUÉS de blocks/script.html (la capa
# vanilla que ya gobierna nav/progreso/contadores/cookies/mapa/FAQ). Primera línea
# ejecutable = el gate, para que todo camino de fallo aterrice en el reveal estático.
_INIT_JS = """
(function () {
  "use strict";
  var RM = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function revealAll(){
    document.querySelectorAll("[data-reveal]:not(.vis)").forEach(function(e){ e.classList.add("vis"); });
  }
  if (!window.gsap || RM) { revealAll(); return; }      // GATE: sin GSAP o reduced-motion -> estatico
  var gsap = window.gsap, ST = window.ScrollTrigger, STX = window.SplitText;
  try { gsap.registerPlugin(ST, STX); } catch (e) {}
  try { ST.config({ ignoreMobileResize: true }); } catch (e) {}
  var FINE = matchMedia("(pointer:fine)").matches;
  var root = document.documentElement;
  root.classList.add("faro-gsap");                       // apaga las @keyframes CSS de reveal (las maneja GSAP)
  window.__faroGsap = true;
  // La IO de reveal vanilla se creó en script.html justo antes; su callback es
  // async, así que la desconectamos AHORA (sincrónico) y GSAP toma los reveals.
  try { if (window.__faroRevealIO) window.__faroRevealIO.disconnect(); } catch (e) {}

  // SIN scroll suave (Lenis): el scroll es NATIVO. El smooth-scroll secuestra la
  // rueda/trackpad y se siente lento y roto en una web de negocio. Los anclas y el
  // botón "subir" los gobierna la capa vanilla (script.html) con scroll nativo.

  function park(el, props) {        // tween defensivo: si algo falla, el contenido queda visible
    try { return gsap.fromTo(el, props.from, props.to); } catch (e) { if (el.classList) el.classList.add("vis"); }
  }

  // Difiere hasta que carguen las fuentes. SplitText mide la geometría de los glifos;
  // partir con la fuente fallback y re-maquetar al entrar la web font provoca un flash
  // visible en los titulares (GSAP avisa "SplitText called before fonts loaded"). Si el
  // API de fuentes no existe, ejecuta ya (degradación segura: el titular queda visible).
  function whenFontsReady(fn) {
    try { if (document.fonts && document.fonts.ready) { document.fonts.ready.then(fn); } else { fn(); } }
    catch (e) { fn(); }
  }

  // --- Titular cinético del hero (SplitText, líneas enmascaradas) ---
  // Diferido a whenFontsReady: el titular es el WOW del hero, no puede parpadear.
  whenFontsReady(function () {
    try {
      var h1 = document.querySelector(".hero h1");
      var sig0 = document.body.getAttribute("data-signature") || "";
      if (h1 && STX && sig0 !== "poster-gym") {
        var split = new STX(h1, { type: "lines,words", mask: "lines" });
        gsap.from(split.words, { yPercent: 118, duration: 0.9, ease: "expo.out", stagger: { each: 0.045 } });
      }
    } catch (e) {}
  });

  // --- Sistema de reveal con ScrollTrigger (reusa .vis + el stagger --i) ---
  // Solo oculta EN onEnter (nunca pre-oculta inline lo de bajo del fold), así la
  // red de seguridad de 3s (CSS .vis) siempre puede recuperar lo no alcanzado.
  // Salta lo marcado data-owned (lo gobierna una firma) y no re-anima lo ya .vis.
  function setupReveals() {
    var all = gsap.utils.toArray("[data-reveal]:not(.vis):not([data-owned])");
    var fade = all.filter(function (e) { return e.getAttribute("data-reveal") !== "img"; });
    var imgs = all.filter(function (e) { return e.getAttribute("data-reveal") === "img"; });
    try {
      ST.batch(fade, {
        start: "top 88%", once: true,
        onEnter: function (b) {
          var fresh = b.filter(function (el) { return !el.classList.contains("vis"); });
          if (!fresh.length) return;
          gsap.fromTo(fresh, { autoAlpha: 0, y: 22 },
            { autoAlpha: 1, y: 0, duration: 0.62, ease: "power3.out", stagger: 0.07,
              onComplete: function () { fresh.forEach(function (el) { el.classList.add("vis"); }); } });
        }
      });
    } catch (e) { fade.forEach(function (el) { el.classList.add("vis"); }); }
    imgs.forEach(function (el) {
      try {
        ST.create({ trigger: el, start: "top 90%", once: true, onEnter: function () {
          if (el.classList.contains("vis")) return;
          gsap.fromTo(el, { clipPath: "inset(0 100% 0 0)", autoAlpha: 1 },
            { clipPath: "inset(0 0% 0 0)", duration: 0.9, ease: "power3.inOut",
              onComplete: function () { el.classList.add("vis"); } });
        } });
      } catch (e) { el.classList.add("vis"); }
    });
  }

  // --- Parallax acotado (<=18 yPercent, <=14px), nunca mareante ---
  function parallax(sel, yp, trigger) {
    var el = document.querySelector(sel); if (!el) return;
    try { gsap.to(el, { yPercent: yp, ease: "none",
      scrollTrigger: { trigger: trigger || ".hero", start: "top top", end: "bottom top", scrub: true } }); } catch (e) {}
  }

  // --- Firmas por familia (UNA por pagina). SIN pins: nada secuestra el scroll. ---
  function posterParallax() {
    parallax(".hero-poster .wm", -13, ".hero-poster");
    parallax(".hero-poster h1", -4, ".hero-poster");
  }
  var SIG = {
    "deck": function () {                                   // aurora (universal): hero parallax sobrio
      parallax(".hero h1", -16, ".hero");
      parallax(".hero-photo", -6, ".hero");
    },
    "clinica": function () {                                // unmask clip-path del panel split
      var panel = document.querySelector(".hero-split .panel");
      if (panel) park(panel, { from: { clipPath: "inset(0 50% 0 50%)" },
        to: { clipPath: "inset(0 0% 0 0%)", ease: "power3.out",
          scrollTrigger: { trigger: ".hero-split", start: "top 82%", end: "top 38%", scrub: 0.6 } } });
      parallax(".hero h1", -10, ".hero");
    },
    "authority": function () {                              // hairline que se dibuja + titular con foco
      parallax(".hero h1", -12, ".hero");
      var hr = document.querySelector(".hero .hero-meta");
      if (hr) { try { gsap.fromTo(hr, { "--auth": 0 }, { "--auth": 1,
        scrollTrigger: { trigger: hr, start: "top 92%", end: "top 70%", scrub: true } }); } catch (e) {} }
      gsap.utils.toArray(".index .item").forEach(function (it) {
        try { ST.create({ trigger: it, start: "top 70%", end: "bottom 40%",
          onToggle: function (self) { it.classList.toggle("active", self.isActive); } }); } catch (e) {}
      });
    },
    "poster": function () {                                 // industrial: parallax multicapa + filas que entran
      posterParallax();
      gsap.utils.toArray(".slist .item").forEach(function (it, i) {
        it.setAttribute("data-owned", "1");                 // la gobierna la firma; setupReveals la salta
        try {
          ST.create({ trigger: it, start: "top 90%", once: true, onEnter: function () {
            if (it.classList.contains("vis")) return;        // ya revelada por la red de seguridad
            gsap.fromTo(it, { x: i % 2 ? 70 : -70, autoAlpha: 0 },
              { x: 0, autoAlpha: 1, duration: 0.6, ease: "power4.out",
                onComplete: function () { it.classList.add("vis"); } });
          } });
        } catch (e) { it.classList.add("vis"); }
      });
    },
    "poster-gym": function () {                             // gimnasio: titular slam + marquee reactivo a velocidad
      whenFontsReady(function () {                           // el slam mide chars: espera la web font (evita reflow)
        try {
          var h = document.querySelector(".hero-poster h1");
          if (h && STX) { var s = new STX(h, { type: "chars" });
            gsap.from(s.chars, { yPercent: 135, autoAlpha: 0, duration: 0.5, stagger: 0.02, ease: "back.out(2)" }); }
        } catch (e) {}
      });
      posterParallax();
      var track = document.querySelector(".marquee .track");
      if (track) {
        try {
          var skew = gsap.quickTo(track, "skewX", { duration: 0.45, ease: "power3" });
          ST.create({ onUpdate: function (self) {
            var v = self.getVelocity() / -280; v = Math.max(-12, Math.min(12, v)); skew(v);
          } });
        } catch (e) {}
      }
    },
    "carta": function () { parallax(".hero h1", -9, ".hero"); parallax(".hero-photo", -6, ".hero"); },
    "gallery": function () { parallax(".hero h1", -8, ".hero"); }
  };

  function run() {
    // La firma PRIMERO (puede marcar elementos data-owned); luego el reveal genérico
    // los salta, evitando doble animación.
    var sig = document.body.getAttribute("data-signature") || "deck";
    var fn = SIG[sig]; if (fn) { try { fn(); } catch (e) {} }
    setupReveals();
    if (FINE) {                                             // CTA magnetica (solo puntero fino)
      var btn = document.querySelector(".hero-cta .btn-brand");
      if (btn && gsap.quickTo) {
        try {
          var xTo = gsap.quickTo(btn, "x", { duration: 0.4, ease: "power3" });
          var yTo = gsap.quickTo(btn, "y", { duration: 0.4, ease: "power3" });
          btn.addEventListener("mousemove", function (e) { var r = btn.getBoundingClientRect();
            xTo((e.clientX - r.left - r.width / 2) * 0.33); yTo((e.clientY - r.top - r.height / 2) * 0.4); });
          btn.addEventListener("mouseleave", function () { xTo(0); yTo(0); });
        } catch (e) {}
      }
    }
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ST.refresh(); }); } catch (e) {}
    setTimeout(function () { try { ST.refresh(); } catch (e) {} }, 600);
  }

  // El script va al final del <body>: el DOM ya está parseado, así que corremos
  // YA (no en 'load', que esperaría a las imágenes y dejaría huecos arriba).
  run();
  addEventListener("load", function () { try { ST.refresh(); } catch (e) {} });
})();
"""


@lru_cache(maxsize=1)
def _bundle() -> str:
    # Cada librería en su propio <script> (evita problemas de ASI al concatenar
    # 4 UMD) + el IIFE de inicialización en el suyo.
    return motion_libs_inline() + "<script>" + _INIT_JS + "</script>"


def motion_js() -> str:
    """Las librerías de motion + el IIFE de inicialización, como markup de <script>."""
    return _bundle()
