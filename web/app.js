"use strict";

const el = (id) => document.getElementById(id);

async function loadSectors() {
  const res = await fetch("/api/sectors");
  const data = await res.json();
  const sel = el("sector");
  for (const s of data.sectors) {
    const opt = document.createElement("option");
    opt.value = s.value;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = "dental";
}

function formToJson(form) {
  const out = {};
  for (const [k, v] of new FormData(form).entries()) out[k] = v;
  if (!el("useColor").checked) out.brand_color = "";
  return out;
}

async function generate(e) {
  e.preventDefault();
  el("error").textContent = "";
  const btn = el("genBtn");
  btn.disabled = true;
  btn.textContent = "Generando…";
  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formToJson(e.target)),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Error" }));
      el("error").textContent = err.detail || "No se pudo generar.";
      return;
    }
    const data = await res.json();
    showResult(data);
  } finally {
    btn.disabled = false;
    btn.textContent = "✨ Generar pack";
  }
}

function showResult(data) {
  el("empty").classList.add("hidden");
  const frame = el("preview");
  frame.src = data.preview_url + "?t=" + Date.now();
  frame.classList.remove("hidden");
  el("actions").classList.remove("hidden");
  el("downloadBtn").href = data.download_url;
  el("openBtn").href = data.preview_url;
  el("downloadBtn").dataset.name = el("bizForm").name.value.trim();
  el("downloadBtn").dataset.phone = el("bizForm").phone.value.trim();

  el("gmb").classList.remove("hidden");
  el("gmbDesc").textContent = data.gmb.description;
  const posts = el("gmbPosts");
  posts.innerHTML = "";
  for (const p of data.gmb.posts) {
    const li = document.createElement("li");
    li.textContent = p;
    posts.appendChild(li);
  }
}

document.addEventListener("click", (e) => {
  if (e.target.classList.contains("copy")) {
    const text = el(e.target.dataset.target).textContent;
    navigator.clipboard.writeText(text).then(() => {
      e.target.textContent = "¡Copiado!";
      setTimeout(() => (e.target.textContent = "Copiar"), 1500);
    });
  }
});

el("useColor").addEventListener("change", (e) => {
  el("brandColor").disabled = !e.target.checked;
});

// Confirmación antes de descargar el pack para entregar: evita entregar datos equivocados.
el("downloadBtn").addEventListener("click", (e) => {
  const b = e.target.dataset;
  if (!confirm(`Vas a descargar el pack de "${b.name}" (tel. ${b.phone}). ¿Son correctos los datos?`)) {
    e.preventDefault();
  }
});

// Datos de ejemplo solo en modo demostración (?demo=1), nunca por defecto.
function fillDemo() {
  if (new URLSearchParams(location.search).get("demo") !== "1") return;
  const f = el("bizForm");
  f.name.value = "Clínica Dental Sonríe";
  f.city.value = "Puerto de Sagunto";
  f.phone.value = "961234567";
  f.services.value = "Limpiezas dentales\nImplantes\nOrtodoncia invisible";
  f.hours.value = "L-V 9:00-20:00, S 9:00-14:00";
  f.address.value = "Av. del Mediterráneo 12";
  f.highlights.value = "20 años cuidando sonrisas en el Puerto\nPrimera visita sin coste";
}

el("bizForm").addEventListener("submit", generate);
loadSectors();
fillDemo();
