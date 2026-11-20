"use strict";
// Página de ordenación. Python calcula todos los pasos (/api/ordenar); aquí solo se dibujan.

const $ = s => document.querySelector(s);
const VELOCIDAD_MS = [900, 620, 430, 300, 210, 150, 100, 65, 40, 20];

const est = {
  algoritmos: {},       // clave -> {nombre, descripcion, mejor, promedio, peor, estable}
  datos: null,          // respuesta de /api/ordenar: elementos, pasos, orden, comparaciones, intercambios
  peticion: null,       // lo que se pidió para obtener 'datos'
  orden: [],            // orden[pos] = índice del elemento que está en esa posición
  burbujas: [],         // burbujas[k] = div del elemento k
  paso: 0, comp: 0, swap: 0,
  fijas: new Set(), pivote: null, marcas: new Map(),
  timer: null, corriendo: false,
};

// ---------------------------------------------------------------- utilidades
const esc = t => String(t).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ms = () => VELOCIDAD_MS[Number($("#velocidad").value) - 1];
const pasos = () => (est.datos ? est.datos.pasos : []);
const terminado = () => est.datos && est.paso >= pasos().length;
const nombreAlgoritmo = () => (est.algoritmos[$("#algoritmo").value] || {}).nombre || "";

let avisoTimer;
function aviso(texto) {
  const a = $("#aviso");
  a.textContent = texto;
  a.classList.add("ver");
  clearTimeout(avisoTimer);
  avisoTimer = setTimeout(() => a.classList.remove("ver"), 2800);
}

async function api(url, cuerpo) {
  const r = await fetch(url, cuerpo === undefined ? undefined : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo),
  });
  const d = await r.json().catch(() => ({ error: "Respuesta no válida del servidor" }));
  if (!r.ok) throw new Error(d.error || "Algo salió mal");
  return d;
}

function leerNumeros() {
  // Lo que no sea un entero se envía tal cual para que el servidor explique el error.
  return $("#numeros").value.split(/[\s,;]+/).filter(Boolean).map(t => (/^\d+$/.test(t) ? Number(t) : t));
}

function peticion() {
  const p = {
    fuente: $("#fuente").value,
    campo: $("#campo").value,
    algoritmo: $("#algoritmo").value,
    descendente: $("#sentido").value === "desc",
  };
  if (p.fuente === "numeros") p.numeros = leerNumeros();
  return p;
}

function describir(pos) {
  const e = est.datos.elementos[est.orden[pos]];
  return e.detalle ? `«${e.etiqueta}» (${e.corto})` : `el ${e.etiqueta}`;
}

function narrar(texto) { $("#narracion").textContent = texto; }

// ---------------------------------------------------------------- dibujo
function dibujar() {
  const cont = $("#burbujas");
  cont.innerHTML = "";
  est.burbujas = [];
  const elementos = est.datos ? est.datos.elementos : [];
  elementos.forEach(e => {
    const b = document.createElement("div");
    b.className = "burbuja";
    b.textContent = e.corto;
    b.title = e.detalle ? `${e.etiqueta} — ${e.detalle}` : e.etiqueta;
    cont.appendChild(b);
    est.burbujas.push(b);
  });
  posicionar();
  pintar();
  narrar(elementos.length
    ? `${elementos.length} elementos listos. Pulsa «Ordenar» para verlo con ${nombreAlgoritmo()}.`
    : "No hay nada que ordenar.");
}

function posicionar() {
  const n = est.burbujas.length;
  if (!n) return;
  const cont = $("#burbujas");
  const ancho = Math.max($("#escenario").clientWidth, n * 50);
  cont.style.width = ancho + "px";
  const hueco = ancho / n;
  // El ÁREA de la burbuja es proporcional al valor (por eso la raíz cuadrada).
  const valores = est.datos.elementos.map(e => Math.sqrt(e.valor));
  const min = Math.min(...valores), max = Math.max(...valores);
  const dMax = Math.min(84, hueco - 6), dMin = dMax * 0.5;
  est.orden.forEach((k, pos) => {
    const t = max === min ? 0.6 : (valores[k] - min) / (max - min);
    const d = dMin + (dMax - dMin) * t;
    const b = est.burbujas[k];
    b.style.setProperty("--d", d + "px");
    b.style.setProperty("--x", (pos * hueco + hueco / 2 - d / 2) + "px");
  });
}

function pintar() {
  est.burbujas.forEach((b, k) => {
    const marca = est.marcas.get(k);
    b.classList.toggle("fija", est.fijas.has(k));
    b.classList.toggle("pivote", est.pivote === k);
    b.classList.toggle("compara", marca === "compara");
    b.classList.toggle("intercambia", marca === "intercambia");
  });

  const total = pasos().length;
  $("#n-comp").textContent = est.comp;
  $("#n-swap").textContent = est.swap;
  $("#n-paso").textContent = `${est.paso} / ${total}`;
  $("#progreso").style.width = total ? (100 * est.paso / total) + "%" : "0";

  const elementos = est.datos ? est.datos.elementos : [];
  $("#lista").innerHTML = est.orden.map(k => {
    const e = elementos[k];
    const clases = [est.marcas.get(k) || "", est.fijas.has(k) ? "fija" : ""].join(" ").trim();
    const texto = e.detalle ? `${esc(e.etiqueta)}<small>${esc(e.detalle)}</small>` : "";
    return `<li class="${clases}"><b>${esc(e.corto)}</b><span>${texto}</span></li>`;
  }).join("");

  const btnPlay = $("#play");
  btnPlay.textContent = est.corriendo ? "Pausa" : terminado() ? "Ordenar de nuevo" : est.paso ? "Continuar" : "Ordenar";
  btnPlay.disabled = !est.datos;
  $("#paso").disabled = !est.datos || terminado();
  $("#reiniciar").disabled = !est.datos || est.paso === 0;
}

// ---------------------------------------------------------------- pasos
function aplicarPaso(p) {
  const o = est.orden;
  est.marcas = new Map();
  if (p.tipo === "comparar") {
    est.comp++;
    est.marcas.set(o[p.i], "compara").set(o[p.j], "compara");
    narrar(`Compara ${describir(p.i)} con ${describir(p.j)}.`);
  } else if (p.tipo === "intercambiar") {
    est.swap++;
    [o[p.i], o[p.j]] = [o[p.j], o[p.i]];
    est.marcas.set(o[p.i], "intercambia").set(o[p.j], "intercambia");
    narrar(`Están al revés: intercambia ${describir(p.j)} y ${describir(p.i)}.`);
    posicionar();
  } else if (p.tipo === "pivote") {
    est.pivote = o[p.i];
    narrar(`Pivote: ${describir(p.i)}. Lo que va antes que él pasa a su izquierda.`);
  } else if (p.tipo === "fijar") {
    est.fijas.add(o[p.i]);
    if (est.pivote === o[p.i]) est.pivote = null;
    narrar(`${describir(p.i)} ya está en su sitio: posición ${p.i + 1}.`);
  }
  est.paso++;
}

function tic() {
  if (!est.datos || terminado()) return terminar();
  aplicarPaso(pasos()[est.paso]);
  if (terminado()) return terminar();
  pintar();
  est.timer = setTimeout(tic, ms());
}

function detener() {
  clearTimeout(est.timer);
  est.timer = null;
  est.corriendo = false;
}

function terminar() {
  detener();
  est.marcas = new Map();
  est.pivote = null;
  pintar();
  narrar(`Lista ordenada con ${nombreAlgoritmo()}: ${est.comp} comparaciones y ${est.swap} intercambios.`);
  $("#aplicar").hidden = !(est.peticion && est.peticion.fuente === "playlist");
}

function reiniciar() {
  detener();
  est.orden = est.datos ? est.datos.elementos.map((_, k) => k) : [];
  est.paso = est.comp = est.swap = 0;
  est.fijas = new Set();
  est.pivote = null;
  est.marcas = new Map();
  $("#aplicar").hidden = true;
  dibujar();
}

async function preparar() {
  detener();
  const p = peticion();
  try {
    est.datos = await api("/api/ordenar", p);
    est.peticion = p;
  } catch (e) {
    est.datos = null;
    est.peticion = null;
    aviso(e.message);
  }
  reiniciar();
  return est.datos !== null;
}

function reproducir() {
  if (est.corriendo) { detener(); pintar(); return; }
  if (!est.datos) return;
  if (terminado()) reiniciar();
  est.corriendo = true;
  $("#aplicar").hidden = true;
  tic();
}

function unPaso() {
  if (!est.datos || terminado()) return;
  detener();
  aplicarPaso(pasos()[est.paso]);
  if (terminado()) terminar(); else pintar();
}

// ---------------------------------------------------------------- información y comparación
function pintarInfo() {
  const a = est.algoritmos[$("#algoritmo").value];
  if (!a) return;
  $("#info").innerHTML = `<h3>${esc(a.nombre)}</h3><p>${esc(a.descripcion)}</p>
    <div class="chips"><span>Mejor caso ${esc(a.mejor)}</span><span>Promedio ${esc(a.promedio)}</span>
    <span>Peor caso ${esc(a.peor)}</span><span>${a.estable ? "Estable" : "No estable"}</span></div>`;
}

async function comparar() {
  let d;
  try { d = await api("/api/ordenar/comparar", peticion()); } catch (e) { aviso(e.message); return; }
  const menorComp = Math.min(...d.resultados.map(r => r.comparaciones));
  const menorSwap = Math.min(...d.resultados.map(r => r.intercambios));
  const tabla = $("#tabla");
  tabla.innerHTML = `<caption class="suave" style="text-align:left;padding-bottom:6px">Lista de ${d.n} elementos</caption>
    <thead><tr><th>Algoritmo</th><th>Comparaciones</th><th>Intercambios</th><th>Pasos</th></tr></thead><tbody>` +
    d.resultados.map(r => `<tr><td>${esc(r.nombre)}</td>
      <td class="${r.comparaciones === menorComp ? "mejor" : ""}">${r.comparaciones}</td>
      <td class="${r.intercambios === menorSwap ? "mejor" : ""}">${r.intercambios}</td>
      <td>${r.pasos}</td></tr>`).join("") + "</tbody>";
  tabla.hidden = false;
}

async function aplicarAPlaylist() {
  try {
    await api("/api/playlist/ordenar", est.peticion);
    aviso("Playlist ordenada. Ábrela en el reproductor.");
    $("#aplicar").hidden = true;
  } catch (e) { aviso(e.message); }
}

// ---------------------------------------------------------------- eventos
function mostrarCampos() {
  const numeros = $("#fuente").value === "numeros";
  $("#caja-campo").hidden = numeros;
  $("#caja-numeros").hidden = !numeros;
}

let numerosTimer;
$("#fuente").addEventListener("change", () => { mostrarCampos(); preparar(); });
$("#campo").addEventListener("change", preparar);
$("#sentido").addEventListener("change", preparar);
$("#algoritmo").addEventListener("change", () => { pintarInfo(); preparar(); });
$("#numeros").addEventListener("input", () => { clearTimeout(numerosTimer); numerosTimer = setTimeout(preparar, 450); });
$("#aleatorios").addEventListener("click", () => {
  $("#numeros").value = Array.from({ length: 12 }, () => 1 + Math.floor(Math.random() * 99)).join(", ");
  preparar();
});
$("#velocidad").addEventListener("input", e => e.target.setAttribute("aria-valuetext", `${e.target.value} de 10`));
$("#play").addEventListener("click", reproducir);
$("#paso").addEventListener("click", unPaso);
$("#reiniciar").addEventListener("click", reiniciar);
$("#comparar").addEventListener("click", comparar);
$("#btn-aplicar").addEventListener("click", aplicarAPlaylist);
window.addEventListener("resize", posicionar);

(async function iniciar() {
  try {
    const d = await api("/api/ordenacion/algoritmos");
    d.algoritmos.forEach(a => { est.algoritmos[a.clave] = a; });
    $("#algoritmo").innerHTML = d.algoritmos.map(a => `<option value="${a.clave}">${esc(a.nombre)}</option>`).join("");
  } catch (e) { aviso(e.message); return; }
  mostrarCampos();
  pintarInfo();
  preparar();
})();
