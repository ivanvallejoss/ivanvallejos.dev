/* Pestañas de proyecto de la landing.
   README del handoff § Interactions & Behavior, "Pestañas de proyecto".

   El estado inicial (primera pestaña activa, demás paneles con `hidden`) lo da
   el HTML; este script solo cambia de pestaña. Cada tablist es independiente.
   Teclado: ←/→ (circular), Inicio y Fin mueven el foco y activan. Tabindex
   itinerante: la activa tiene 0 y las demás -1, así Tab entra por la activa y
   el siguiente Tab pasa al panel. */
(function () {
  "use strict";

  function activar(tabs, nueva) {
    tabs.forEach(function (tab) {
      var activa = tab === nueva;
      tab.setAttribute("aria-selected", String(activa));
      tab.tabIndex = activa ? 0 : -1;
      var panel = document.getElementById(tab.getAttribute("aria-controls"));
      if (panel) panel.hidden = !activa;
    });
  }

  document.querySelectorAll('[role="tablist"]').forEach(function (lista) {
    var tabs = Array.prototype.slice.call(lista.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;

    lista.addEventListener("click", function (e) {
      var tab = e.target.closest('[role="tab"]');
      if (tab) activar(tabs, tab);
    });

    lista.addEventListener("keydown", function (e) {
      var i = tabs.indexOf(document.activeElement);
      if (i === -1) return;
      var destino;
      if (e.key === "ArrowRight") destino = tabs[(i + 1) % tabs.length];
      else if (e.key === "ArrowLeft") destino = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === "Home") destino = tabs[0];
      else if (e.key === "End") destino = tabs[tabs.length - 1];
      else return;
      e.preventDefault();
      activar(tabs, destino);
      destino.focus();
    });
  });
})();
