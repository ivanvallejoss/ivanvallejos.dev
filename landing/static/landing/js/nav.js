/* Menú móvil de la landing (<820px).
   README del handoff § Interactions & Behavior, "Menú móvil".

   El estado inicial (panel cerrado, botón visible) lo da el HTML más la clase
   `js` que base.html pone en <html>; este script solo abre y cierra. El panel
   usa `hidden` cuando está cerrado; el nombre accesible del botón es "Menú" o
   "Cerrar". */
(function () {
  "use strict";

  var boton = document.querySelector(".site-nav__toggle");
  if (!boton) return;
  var panel = document.getElementById(boton.getAttribute("aria-controls"));
  if (!panel) return;

  var label = boton.querySelector(".site-nav__toggle-label");
  var icono = boton.querySelector(".site-nav__toggle-icon");
  var escritorio = window.matchMedia("(min-width: 820px)");

  function abierto() {
    return boton.getAttribute("aria-expanded") === "true";
  }

  function set(abrir) {
    boton.setAttribute("aria-expanded", String(abrir));
    panel.hidden = !abrir;
    label.textContent = abrir ? "Cerrar" : "Menú";
    icono.textContent = abrir ? "✕" : "☰";
  }

  boton.addEventListener("click", function () {
    set(!abierto());
  });

  // Tocar un link del panel lo cierra.
  panel.addEventListener("click", function (e) {
    if (e.target.closest("a")) set(false);
  });

  // Escape cierra y devuelve el foco al botón.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && abierto()) {
      set(false);
      boton.focus();
    }
  });

  // Al pasar a ≥820px el menú se cierra (el CSS ya oculta panel y botón).
  escritorio.addEventListener("change", function (e) {
    if (e.matches) set(false);
  });
})();
