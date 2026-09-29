# Sistema visual editorial

Referencia de implementación del rediseño **Minimalismo Editorial**. Es el documento
que citan las fases 2–6: si una sección necesita algo que no está acá, o lo agrega a
las primitivas porque se repite en todas las pantallas, o lo resuelve en su propio
CSS de sección.

- **Especificación:** `docs/design/handoff/README.md` (los `.dc.html` son prototipos de
  referencia, no código a copiar; su runtime `support.js` no va a producción).
- **Desvíos respecto del handoff:** `docs/design/ajustes.md`. Si hay conflicto entre el
  handoff y ese registro, gana el registro.
- **Catálogo vivo:** `/_muestra/` con `DEBUG=True`. Revisar a 375, 820 y 1280px.
- **Historia:** `docs/frontend/cimientos.md` documenta Cimiento v1, el frontend anterior,
  recuperable desde el tag `cimiento-v1`.

## Archivos

| Archivo | Qué tiene |
|---|---|
| `landing/static/landing/css/fonts.css` | los dos `@font-face` |
| `landing/static/landing/css/tokens.css` | todas las custom properties. **Ningún hex vive fuera de acá** |
| `landing/static/landing/css/base.css` | reset y decisiones de documento |
| `landing/static/landing/css/primitives.css` | lo que se repite en todas las pantallas |
| `landing/templates/landing/base.html` | layout del documento |
| `landing/templates/landing/landing.html` | la landing |
| `landing/content/landing.yaml` | el contenido editable |

El orden de carga importa: `tokens.css` define las variables que consumen las otras dos.

## Tipografía

**Geist** y **Geist Mono** variables se sirven **desde el propio sitio**
(`landing/static/landing/fonts/*.woff2`), precargadas en `base.html`. El handoff usa
Google Fonts, pero son las mismas familias — no se agrega el enlace externo. Si se
cambia la ruta de una fuente hay que cambiarla en los dos lugares: el `<link rel="preload">`
y el `@font-face`.

## Breakpoints

Mobile-first: la base es mobile y se crece con `min-width`. Dos breakpoints, los del
prototipo (que allá eran JS y acá son media queries):

| Ancho | Qué cambia |
|---|---|
| **820px** | nav de la landing: abajo, botón "MENÚ ☰"; arriba, los links y el CTA |
| **900px** | índice del caso: abajo, barra horizontal sticky; arriba, columna lateral sticky |

## Tokens

Los nombres son **por uso, no por color**. Es lo que permite que una futura versión light
solo tenga que redefinir estas variables. No se agrega un token nombrando un color.

### Superficies y reglas

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#0C0E0C` | fondo de página, y de las celdas de `.grid-div` |
| `--surface` | `#101310` | barra superior, paneles, sección "En curso" |
| `--rule-strong` | `#2E3329` | reglas de 2px: entre secciones, sobre cada bloque, divisores de grilla |
| `--rule-soft` | `#23271F` | reglas de 1px: entre filas de tabla |

### Texto

| Token | Valor | Uso |
|---|---|---|
| `--ink` | `#ECE6D9` | títulos, valores de tabla, estado activo |
| `--text` | `#C9C3B4` | cuerpo y leads |
| `--muted` | `#9C9789` | labels, metadata, cuerpo secundario |

`--muted` es el piso de contraste: el README dice que todo el texto de cuerpo y metadata
pasa ≥4.5:1 sobre `--bg` y que **no se baja de `#9C9789`**.

### Verde (acento de marca) y siena (señal)

| Token | Valor | Uso |
|---|---|---|
| `--accent` | `#4F7A57` | CTA primario, monograma, fondo de selección |
| `--on-accent` | `#F2EFE6` | texto sobre verde |
| `--accent-soft` | `#8FB596` | links, `a:hover`, outline de foco, estado "producción", "ELEGÍ" |
| `--signal` | `#C0662F` | números de sección, indicador de pestaña activa |
| `--signal-soft` | `#D07B45` | estados "EN DESARROLLO", "COSTO" |

### Panel invertido (sección Verificable)

`--inv-bg` `#E8E2D5` · `--inv-ink` `#16180F` · `--inv-text` `#3E4237` ·
`--inv-rule-strong` `#16180F` · `--inv-rule-soft` `#C9C1B0` · `--inv-label` `#8A4520`

### Tipografía y espaciado

| Token | Valor |
|---|---|
| `--font-sans` | `"Geist", system-ui, -apple-system, sans-serif` |
| `--font-mono` | `"Geist Mono", ui-monospace, "SFMono-Regular", Menlo, monospace` |
| `--gutter` | `clamp(20px, 4vw, 60px)` — margen lateral de todo el sitio |
| `--pad-section` | `clamp(48px, 6vw, 76px)` |
| `--pad-hero` | `clamp(48px, 7vw, 88px)` |

## base.css

Reset mínimo; `--bg` y `--ink` en el body; Geist con `-webkit-font-smoothing: antialiased`;
`text-wrap: pretty` en párrafos; selección `--accent` sobre `--ink`; `a:hover` a
`--accent-soft`; `:focus-visible` con outline de 2px `--accent-soft` y offset de 2px
(no está en el prototipo, lo pide el README); **radio 0 global**.

Radio 0, ausencia de sombras y ausencia de gradientes son identidad cerrada: no se
ajustan por componente.

## Primitivas

### Sección

| Clase | Cuándo |
|---|---|
| `.section` | toda sección de la página: padding vertical + gutter lateral |
| `.section--hero` | el hero, que lleva el padding más alto |
| `.section--surface` | secciones sobre `--surface` ("En curso") |

`.section--surface` y `.grid-div` no se combinan: las celdas de la grilla pintan `--bg`.

### Reglas

`.rule-top-strong` · `.rule-top-soft` · `.rule-bottom-strong` · `.rule-bottom-soft`

La jerarquía del sistema es por líneas: **2px separa bloques, 1px separa filas dentro de
un bloque**. Nunca sombras.

### Grillas

| Clase | Cuándo |
|---|---|
| `.grid-div` | grilla **con divisores**: el contenedor pinta `--rule-strong` de fondo con `gap: 2px` y las celdas tapan con `--bg` |
| `.grid-gap` | la misma fórmula separada por aire, sin divisores |

El mínimo de columna se configura con `--col`, y el gap de `.grid-gap` con `--gap`:

```html
<div class="grid-div" style="--col: 420px"> … </div>
```

| `--col` | Dónde |
|---|---|
| `420px` | hero (2 columnas) |
| `320px` | proyecto entregado, celdas de contacto |
| `260px` | áreas de trabajo, artículos de escritura |
| `220px` | filas de "En curso" |
| `200px` | fila meta del caso |

**Por qué este patrón y no `border-right`:** al apilarse en mobile las líneas se
reacomodan solas, sin media queries que apaguen bordes.

### Encabezado de sección

```html
<div class="sec-head">
  <div class="sec-head__title">
    <span class="sec-num">01</span>
    <h2 class="t-h2">Áreas de trabajo</h2>
  </div>
  <span class="sec-note">nota opcional a la derecha</span>
</div>
```

Sin nota, alcanza con `.sec-head__title` solo.

### Escala tipográfica

| Clase | Valor | Cuándo |
|---|---|---|
| `.t-h1` | `clamp(34px,4.2vw,50px)` · 600 · lh 1.1 · ls -0.025em · max-w 660 | H1 de la landing |
| `.t-h1-caso` | `clamp(36px,5vw,60px)` · 600 · lh 1.05 · ls -0.03em | H1 del caso |
| `.t-h2` | `clamp(24px,2.6vw,30px)` · 600 · ls -0.018em | título de sección |
| `.t-project` | `clamp(22px,2.4vw,28px)` · 600 · ls -0.022em | nombre de proyecto |
| `.t-sub` | 19px · 600 | ítem de área, nombre en "En curso" |
| `.t-lead` | `clamp(16px,1.5vw,18px)` · 400 · lh 1.65 · `--text` | lead del hero y de sección |
| `.t-body` | 15px · lh 1.65 | cuerpo base: áreas, celdas de contacto |
| `.t-body-m` | 15.5px · lh 1.65 | descripciones de "En curso" |
| `.t-body-l` | 16.5px · lh 1.65 | párrafo de proyecto entregado |
| `.t-row` | 14.5px | fila de tabla, nota de sección |
| `.t-label` | mono 11.5px · ls 0.11em · mayúsculas · `--muted` | label de tabla, número de sección |
| `.t-meta` | mono 12.5px · `--muted` | stack, caption, metadata |

**Tres cuerpos y no uno.** El README da el cuerpo como rango `15–16.5px`; el prototipo usa
los tres valores según el contexto y la instrucción de la fase fue tomar el valor inline
exacto. Unificarlos es un ajuste de diseño: va a `ajustes.md`, no se decide en el código.

**Modificadores de label.** El prototipo usa seis combinaciones de tamaño y tracking.
La base es 11.5px / 0.11em; los modificadores cubren el resto:

| Modificador | Valor | Dónde |
|---|---|---|
| `.t-label--wide` | ls 0.13em | kicker del hero |
| `.t-label--kicker` | ls 0.1em | kicker de proyecto y de contacto |
| `.t-label--tight` | ls 0.09em | estados, caption del retrato |
| `.t-label--bar` | ls 0.07em | barra superior |
| `.t-label--sm` | 11px · ls 0.1em | nav, pestañas |

### Botones

| Clase | Cuándo |
|---|---|
| `.btn` | base obligatoria: alto mínimo de 44px, padding 14×24, 15px |
| `.btn--primary` | CTA principal: fondo `--accent` |
| `.btn--light` | CTA del hero: fondo `--ink` sobre texto `--bg` |
| `.btn--outline` | secundario: borde `--rule-strong` |
| `.btn--outline-accent` | borde `--accent`, **se rellena de verde en hover** |
| `.btn--compact` | variante chica (12×20, 14.5px) para nav y celdas de contacto |

Sirven para `<a>` y para `<button>`. El alto mínimo de 44px lo pide el README para mobile;
`.btn--compact` lo suelta recién en ≥820px, así que en mobile ningún botón queda por
debajo del hit target.

Los botones de color no viran a `--accent-soft` en hover como los links: `.btn--outline-accent`
es el único con hover de relleno del sistema.

### Filas de etiqueta y valor

```html
<div class="rows rows--closed">
  <div class="row row--split">
    <span class="row__label">Experiencia</span>
    <span class="row__value">+2 años</span>
  </div>
  …
</div>
```

`.rows` pone 2px `--rule-strong` arriba de la primera fila y 1px `--rule-soft` entre las
demás. `.rows--closed` agrega el cierre de 2px abajo de la última — se omite cuando la
regla de la sección siguiente ya hace de cierre.

| Modificador | Cuándo |
|---|---|
| `.row--split` | etiqueta y valor a los extremos (tabla Antecedentes) |
| `.row--keyed` | etiqueta de 160px fijos y valor corrido (Alcance / Stack / Estado) |
| `.row--inv` + `.rows--inv` | filas del panel invertido, con las reglas `--inv-rule-*` |

### Etiquetas de estado

`.status` más `.status--prod` (`--accent-soft`), `.status--dev` (`--signal-soft`) o
`.status--form` (`--muted`).

## Lo que NO está en las primitivas

Son componentes de una sola pantalla; los trae la fase que implementa esa sección, con su
propio CSS:

- **pestañas de proyecto** y **menú móvil** (landing);
- **índice lateral / barra sticky**, **timeline** y **diagrama mono** (caso Bricka).

El criterio: una primitiva es algo que se repite en todas las pantallas. Si aparece una
sola vez, no sube acá.
