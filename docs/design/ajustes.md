# Registro de ajustes al diseño

Rediseño **Minimalismo Editorial** de `ivanvallejos.dev`. Handoff en
`docs/design/handoff/` (README.md es la especificación).

## Reglas

- **La fuente de verdad es el handoff más este registro.** Si hay conflicto entre los dos,
  gana el registro.
- **La identidad está cerrada:** tokens de color, Geist y Geist Mono, radio 0, sin sombras
  ni gradientes. No se ajustan.
- **Se puede ajustar:** espaciados, tamaños, orden en mobile y detalles de componentes.
  Solo los decide Ivan.
- **Los cambios estructurales** (una sección nueva, un componente nuevo) pasan antes por
  Claude Design.
- **Un agente de código nunca agrega entradas por su cuenta.** Solo registra las que le
  indica el prompt de su fase.

## Ajustes

| # | Fecha | Pantalla/sección | Cambio respecto del handoff | Decidido por |
|---|-------|------------------|-----------------------------|--------------|
| A-01 | 2026-09-29 | Botones (todo el sitio) | Por debajo de 820px todo botón mide al menos 44px de alto (el CTA de contacto pasa de ~41px a 44px). Desde 820px se respetan los tamaños del prototipo. | Ivan |
| A-02 | 2026-09-29 | Barra superior | El selector ES/EN queda detrás del flag `idiomas`, apagado hasta que exista la versión en inglés. | Ivan |
| A-03 | 2026-09-29 | Nav · menú móvil | Las filas del panel del menú pasan a `--accent-soft` en hover, como el resto de los links (README § Interactions). En el prototipo no cambian porque el color inline pisa la regla. | Ivan |
| A-04 | 2026-09-29 | Botones (todo el sitio) | `.btn--outline` pasa el texto a `--accent-soft` en hover, como los links (README § Interactions) y como A-03. El prototipo se contradice por sus estilos inline: en el hero no cambia y en contacto se pone verde. `.btn--primary` y `.btn--light` siguen sin cambio; `.btn--outline-accent` se sigue rellenando. | Ivan |
| A-05 | 2026-09-29 | Hero · retrato | La leyenda del retrato usa `.t-label--tight` y mide 11.5px (ls 0.09em), en lugar de los 11px del prototipo. | Ivan |
| A-06 | 2026-09-29 | Hero | Desde 1180px el retrato (4:5, 40% del ancho útil de la celda derecha, mín. 180px y máx. 340px, leyenda debajo) va a la izquierda de Antecedentes, que ocupa el resto del ancho; los dos alineados arriba y el bloque centrado en vertical como hoy. El padding vertical de las dos celdas pasa a `clamp(32px, 6vh, 88px)`. Por debajo de 1180px no cambia, porque Antecedentes quedaría tan angosto que sus filas pasan a dos líneas. Objetivo: desde 760px de alto de pantalla el hero entra y deja ver el comienzo de la sección siguiente. Se acepta un desborde de hasta ~70px entre 660 y 700px de alto; se revisa con la tipografía después de la fase 5. | Ivan |
| A-07 | 2026-09-30 | Trabajo entregado · pestañas | Con JS, el panel de cada proyecto toma el alto de su pestaña más larga, así el layout no se mueve al cambiar de pestaña (es lo que el README busca con el `min-height`; en el prototipo el panel crece cuando el contenido lo supera). Se mantiene el mínimo de 244px en total. Sin JS no cambia: todos los paneles se ven en orden. | Ivan |
