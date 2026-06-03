"use strict";

// Consola del operador. El formulario NO está escrito a mano: se genera desde el
// esquema declarativo de la plantilla que cubre el sector (/api/form/<sector>),
// de modo que es distinto según el tipo de negocio. Al cambiar de sector se
// conservan los valores de los campos que se llaman igual.

const el = (id) => document.getElementById(id);

let SECTORS = [];
let currentValues = {};

async function loadSectors() {
  const res = await fetch("/api/sectors");
  const data = await res.json();
  SECTORS = data.sectors;
  const sel = el("sector");
  for (const s of SECTORS) {
    const opt = document.createElement("option");
    opt.value = s.value;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = "dental";
  await renderForm();
}

// --- Render de un campo según su tipo ---------------------------------------

function fieldControl(f, value) {
  const v = value == null ? "" : value;
  if (f.kind === "textarea" || f.kind === "list") {
    const ta = document.createElement("textarea");
    ta.rows = f.rows || 3;
    ta.value = v;
    return ta;
  }
  if (f.kind === "select") {
    const sel = document.createElement("select");
    for (const [val, label] of f.options) {
      const o = document.createElement("option");
      o.value = val;
      o.textContent = label;
      sel.appendChild(o);
    }
    sel.value = v;
    return sel;
  }
  if (f.kind === "toggle") {
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = v === "Sí" || v === "si" || v === true;
    cb.classList.add("toggle");
    return cb;
  }
  if (f.kind === "color") {
    const wrap = document.createElement("span");
    wrap.className = "color-control";
    const enable = document.createElement("input");
    enable.type = "checkbox";
    enable.className = "color-enable";
    const color = document.createElement("input");
    color.type = "color";
    color.value = v || "#2563eb";
    color.disabled = !v;
    enable.checked = !!v;
    enable.addEventListener("change", () => { color.disabled = !enable.checked; });
    wrap.appendChild(enable);
    wrap.appendChild(color);
    return wrap;
  }
  const input = document.createElement("input");
  input.type = { tel: "tel", email: "email", url: "url", number: "number" }[f.kind] || "text";
  input.value = v;
  return input;
}

function renderField(f, value) {
  const label = document.createElement("label");
  label.className = "field" + (f.full_width ? " full" : "") + (f.kind === "toggle" ? " toggle-field" : "");
  label.dataset.name = f.name;
  label.dataset.kind = f.kind;

  const caption = document.createElement("span");
  caption.className = "field-label";
  caption.textContent = f.label + (f.required ? " *" : "");

  const control = fieldControl(f, value);
  if (f.placeholder && (control.tagName === "INPUT" || control.tagName === "TEXTAREA")) {
    control.placeholder = f.placeholder;
  }
  if (f.required && control.tagName) control.required = true;
  control.classList.add("control");
  control.dataset.name = f.name;

  if (f.kind === "toggle") {
    // checkbox a la izquierda del texto
    label.appendChild(control);
    label.appendChild(caption);
  } else {
    label.appendChild(caption);
    label.appendChild(control);
  }
  if (f.help) {
    const help = document.createElement("small");
    help.className = "field-help";
    help.textContent = f.help;
    label.appendChild(help);
  }
  return label;
}

async function renderForm() {
  const sector = el("sector").value;
  // Conserva lo que ya hay escrito antes de re-pintar, sin pisar valores ya
  // presentes (p.ej. los del modo demo) con los campos vacíos del DOM actual.
  const collected = collectValues();
  for (const k in collected) if (collected[k]) currentValues[k] = collected[k];
  const res = await fetch("/api/form/" + encodeURIComponent(sector));
  const data = await res.json();
  el("templateTag").textContent = "Plantilla: " + data.name;

  const host = el("formFields");
  host.innerHTML = "";
  for (const group of data.schema.groups) {
    const fs = document.createElement("fieldset");
    fs.className = "group";
    const legend = document.createElement("legend");
    legend.textContent = group.title;
    fs.appendChild(legend);
    if (group.description) {
      const d = document.createElement("p");
      d.className = "group-desc";
      d.textContent = group.description;
      fs.appendChild(d);
    }
    const grid = document.createElement("div");
    grid.className = "field-grid";
    for (const f of group.fields) grid.appendChild(renderField(f, currentValues[f.name]));
    fs.appendChild(grid);
    host.appendChild(fs);
  }
}

// --- Recogida de valores -----------------------------------------------------

function collectValues() {
  const out = {};
  document.querySelectorAll("#formFields .field").forEach((label) => {
    const name = label.dataset.name;
    const kind = label.dataset.kind;
    if (kind === "toggle") {
      out[name] = label.querySelector("input.toggle").checked ? "Sí" : "";
    } else if (kind === "color") {
      const enable = label.querySelector(".color-enable");
      const color = label.querySelector('input[type="color"]');
      out[name] = enable && enable.checked ? color.value : "";
    } else {
      const c = label.querySelector(".control");
      if (c) out[name] = c.value;
    }
  });
  return out;
}

function formToJson() {
  const values = collectValues();
  values.sector = el("sector").value;
  return values;
}

// --- Generar -----------------------------------------------------------------

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
      body: JSON.stringify(formToJson()),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Error" }));
      el("error").textContent = err.detail || "No se pudo generar.";
      return;
    }
    showResult(await res.json());
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
  const v = collectValues();
  el("downloadBtn").dataset.name = (v.name || "").trim();
  el("downloadBtn").dataset.phone = (v.phone || "").trim();

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

// Confirmación antes de descargar el pack para entregar: evita datos equivocados.
el("downloadBtn").addEventListener("click", (e) => {
  const b = e.target.dataset;
  if (!confirm(`Vas a descargar el pack de "${b.name}" (tel. ${b.phone}). ¿Son correctos los datos?`)) {
    e.preventDefault();
  }
});

// Datos de ejemplo solo en modo demostración (?demo=1), nunca por defecto.
function fillDemo() {
  if (new URLSearchParams(location.search).get("demo") !== "1") return;
  currentValues = Object.assign(currentValues, {
    name: "Clínica Dental Sonríe",
    city: "Puerto de Sagunto",
    phone: "961234567",
    services: "Limpiezas dentales\nImplantes\nOrtodoncia invisible",
    hours: "L-V 9:00-20:00, S 9:00-14:00",
    address: "Av. del Mediterráneo 12",
    differentiators: "20 años cuidando sonrisas en el Puerto\nPrimera visita sin coste",
  });
  renderForm();
}

el("sector").addEventListener("change", renderForm);
el("bizForm").addEventListener("submit", generate);
loadSectors().then(fillDemo);
