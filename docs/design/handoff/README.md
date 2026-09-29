# Handoff: Portfolio ivanvallejos.dev — Landing + Caso Bricka

## Overview
Sitio personal de Iván Vallejos (backend & fullstack, Python). Dos audiencias: recruiters (primer rol formal) y clientes freelance. Dos páginas:
1. **Landing** — perfil, áreas, trabajo entregado, en curso, escritura, verificable, contacto bifurcado.
2. **Caso Bricka** — caso de estudio largo del proyecto principal en producción.

## About the Design Files
Los archivos de este paquete son **referencias de diseño hechas en HTML**: prototipos que muestran el aspecto y el comportamiento buscados, no código de producción para copiar. La tarea es **recrearlos en el stack elegido** (sugerido: sitio estático — Astro, Next export o Django templates si se quiere mantener todo en Python), con sus propios patrones. Los `.dc.html` usan un runtime propio (`support.js`) que no debe llevarse a producción. Todo el estilo está inline; al implementar, extraer a tokens/CSS.

## Fidelity
**Alta fidelidad** en layout, color, tipografía, espaciado e interacciones. **Los textos son provisorios** — el autor los reescribe; implementar con el copy actual como placeholder y dejarlo fácil de editar (Markdown/MDX o contenido en JSON).

## Design Tokens

### Colores
| Rol | Hex |
|---|---|
| Fondo página | `#0C0E0C` |
| Superficie (barra superior, paneles, "En curso") | `#101310` |
| Regla fuerte (2px, separadores de sección, grillas) | `#2E3329` |
| Regla suave (1px, filas de tablas) | `#23271F` |
| Tinta principal | `#ECE6D9` |
| Texto de cuerpo | `#C9C3B4` |
| Texto atenuado (labels, metadata) | `#9C9789` |
| Verde primario (CTA, monograma) | `#4F7A57` |
| Texto sobre verde | `#F2EFE6` |
| Verde claro (links, estado "producción", "ELEGÍ") | `#8FB596` |
| Siena (números de sección, indicador activo) | `#C0662F` |
| Siena claro (estados "EN DESARROLLO", "COSTO") | `#D07B45` |
| Panel Verificable — fondo | `#E8E2D5` |
| Panel Verificable — tinta / cuerpo / regla suave / label | `#16180F` / `#3E4237` / `#C9C1B0` / `#8A4520` |
| Selección de texto | fondo `#4F7A57`, texto `#ECE6D9` |

Contraste: todo el texto de cuerpo y metadata pasa ≥4.5:1 sobre `#0C0E0C`. No bajar `#9C9789`.

### Tipografía
- **Geist** (300–700) para todo el texto; **Geist Mono** (400–500) para labels, metadata, stack, diagramas.
- Google Fonts: `family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500`.
- Suavizado: `-webkit-font-smoothing: antialiased`. Párrafos: `text-wrap: pretty`.

| Uso | Familia | Tamaño | Peso | Otros |
|---|---|---|---|---|
| H1 landing | Geist | `clamp(34px,4.2vw,50px)` | 600 | lh 1.1, ls -0.025em, max-w 660 |
| H1 caso | Geist | `clamp(36px,5vw,60px)` | 600 | lh 1.05, ls -0.03em |
| H2 sección | Geist | `clamp(24px,2.6vw,30px)` | 600 | ls -0.018em |
| Título proyecto | Geist | `clamp(22px,2.4vw,28px)` | 600 | ls -0.022em |
| Subtítulo / ítem | Geist | 17–19px | 600 | |
| Lead | Geist | `clamp(16px,1.5vw,18px)` | 400 | lh 1.6–1.65, color cuerpo |
| Cuerpo | Geist | 15–16.5px | 400 | lh 1.6–1.7 |
| Fila de tabla | Geist | 14.5–15px | 400/600 | |
| Label / kicker | Geist Mono | 11–11.5px | 400 | ls 0.09–0.13em, MAYÚSCULAS |
| Stack / meta mono | Geist Mono | 12.5px | 400 | |
| Diagrama | Geist Mono | 12.5px (landing) / 13.5px (caso) | 400 | lh 1.75–1.85, `white-space: pre` |

### Espaciado
- Gutter lateral: `clamp(20px, 4vw, 60px)`.
- Padding vertical de sección: `clamp(48px, 6vw, 76px)` (hero: `clamp(48px,7vw,88px)`).
- Gap título→contenido: 30–44px. Gaps de grilla: `clamp(28px,3.4vw,44px)`.
- Filas de tabla: padding 12–19px vertical.

### Forma
- **Radio 0** en todo. Sin sombras. Sin gradientes.
- Jerarquía por reglas: 2px `#2E3329` entre secciones y sobre cada bloque; 1px `#23271F` entre filas.
- **Grillas con divisores**: contenedor con `background:#2E3329; gap:2px`, celdas con fondo `#0C0E0C` → las líneas se reacomodan solas al apilar en móvil. Usar este patrón en vez de `border-right`.

## Screens / Views

### 1. Landing (`Landing Oscura.dc.html`)
De arriba hacia abajo:

1. **Barra superior** — fondo `#101310`, borde inferior 1px, padding 10px gutter. Mono 11.5px, ls 0.07em, `#9C9789`. Izq: "DESARROLLO DE SOFTWARE · ARGENTINA, REMOTO". Der: mail (se oculta <820px) + "ES" (activo, `#ECE6D9`) / "EN".
2. **Nav** — padding 24px gutter, borde inferior 2px. Izq: monograma 36×36 verde con "IV" 14px/600 + nombre 16.5px/600 + "BACKEND & FULLSTACK · PYTHON" mono 11px. Der (≥820px): links 14px `#C9C3B4` (Perfil, Áreas, Trabajo, En curso, Escritura) + CTA verde "Agendar una llamada" (padding 11×20, 14px/600). <820px: botón "MENÚ ☰" (borde 1px, alto 44px mono 11.5px) que abre panel (ver Interacciones).
3. **Hero** (`#perfil`) — grilla 2 col `repeat(auto-fit,minmax(min(100%,420px),1fr))` con divisor de 2px (patrón grilla).
   - Izq: kicker siena "DESARROLLO DE SISTEMAS A MEDIDA", H1, lead (max-w 580), CTAs: "Consultar disponibilidad" (fondo `#ECE6D9`, texto `#0C0E0C`, 14×24, 15px/600) + "Descargar CV (PDF)" (borde 1px `#2E3329`).
   - Der: retrato 4:5, `filter: grayscale(1) contrast(1.05)`, borde 1px, caption mono 11px. Debajo, tabla **Antecedentes**: label mono + 5 filas (Experiencia +2 años / Formación Analista en Sistemas / Inglés C1 / Sistemas en producción 1 cliente / Modalidad Remoto · AR). Label 14.5px atenuado, valor 15.5px/600, `justify-content: space-between`. Primera y última regla 2px, intermedias 1px suave.
4. **Stack** — fila mono 12.5px atenuada, gap 22px, wrap, borde superior 2px.
5. **01 Áreas de trabajo** (`#areas`) — encabezado de sección (número mono siena + H2, gap 22px). 3 columnas `minmax(min(100%,260px),1fr)`, cada una con regla superior 2px, título 19px/600 y cuerpo 15px atenuado.
6. **02 Trabajo entregado** (`#trabajo`) — encabezado + nota a la derecha. Por proyecto, grilla 2 col `minmax(min(100%,320px),1fr)` con regla superior 2px:
   - Izq: kicker verde claro (CLIENTE · …), título, párrafo, tabla Alcance / Stack / Estado (label de 160px fijo), acciones.
   - Der (max-w 420): **panel con pestañas** (ver Interacciones) + caption 12.5px.
   - Bricka: pestañas Arquitectura / Flujo / Decisiones. Acciones: botón outline verde "Ver el caso completo →" (hover: relleno verde) + "Código privado" atenuado.
   - Pipeline: pestañas Flujo / Decisiones. Nota "Código privado — disponible a pedido en una llamada."
7. **03 En curso** (`#curso`) — fondo `#101310`. Filas en grilla `minmax(min(100%,220px),1fr)`: nombre + estado (siena claro "EN DESARROLLO" o atenuado "FORMACIÓN"), descripción (span 2 col), stack mono + link.
8. **04 Escritura técnica** (`#escritura`, ocultable) — 3 columnas de artículos: fecha mono + título 18px/600, toda la celda es link.
9. **05 Verificable** (ocultable) — panel beige invertido, sin título grande: fila label "05 — VERIFICABLE" + frase a la derecha; tabla de 4 hechos, label flex 0 0 240px /600 + descripción flexible; reglas 2px `#16180F` en extremos, 1px `#C9C1B0` intermedias. **Copy pendiente de reescritura** (hoy dice "código público", contradice Bricka privado).
10. **Contacto** (`#contacto`) — dos celdas con patrón grilla: "PARA EQUIPOS Y RECRUITERS" (verde claro, CTA outline "Descargar CV") y "PARA EMPRESAS Y PARTICULARES" (siena claro, CTA verde "Agendar una llamada").
11. **Footer** — © mono 12px + links GitHub / LinkedIn / Blog / mail.

### 2. Caso Bricka (`Caso Bricka.dc.html`)
1. **Nav simplificada** — monograma + nombre + "← VOLVER AL PORTFOLIO" (link a la landing) · CTA verde.
2. **Hero** — kicker (CASO 01 siena · CLIENTE · INMOBILIARIA atenuado · ● EN PRODUCCIÓN verde claro), H1, lead max-w 680.
3. **Fila meta** — grilla `minmax(min(100%,200px),1fr)`, gap 0 28px, padding lateral = gutter (alinea con el H1), reglas 2px arriba/abajo. 4 celdas: ROL / PERÍODO / USUARIOS / CÓDIGO ("Privado · recorrido en llamada"). Label mono 11px + valor 15.5px/500.
4. **Cuerpo** — flex: índice lateral 200px + contenido `flex:1; max-width:820px`, gap `clamp(32px,5vw,80px)`.
   - **Índice** (≥900px): sticky top 0, label "ÍNDICE", 6 ítems (número mono + nombre 14.5px), borde izq 2px — siena en el activo, transparente en el resto; activo `#ECE6D9`, resto `#9C9789`.
   - **Índice móvil** (<900px): barra horizontal sticky arriba, scroll-x, activo con borde inferior 2px siena.
   - Secciones con `scroll-margin-top: 60px`, separadas por regla 2px:
     - **01 Contexto** — párrafo 17px + grilla Antes / Después (patrón grilla, "DESPUÉS" en verde claro y texto en tinta plena).
     - **02 Arquitectura** — diagrama árbol mono 13.5px en panel `#101310` (overflow-x auto; descripciones en atenuado) + tabla Componente (180px) / Responsabilidad.
     - **03 Flujo** — timeline vertical: línea 1px a la izquierda, marcador cuadrado 11×11 (borde atenuado; el último relleno verde), título 17px/600 + descripción, tag outline mono a la derecha ("dónde corre").
     - **04 Decisiones** — lista en patrón grilla; cada decisión: título 19px/600 + 3 columnas ELEGÍ (verde claro) / DESCARTÉ (atenuado) / COSTO (siena claro).
     - **05 Operación** — grilla 4 celdas (Deploy, Monitoreo, Backups, Tests) + bloque "INCIDENTE" (placeholder para un caso real).
     - **06 Qué sigue** — fila Fase 2 + estado EN DESARROLLO.
5. **Cierre** — dos celdas-link: "← VOLVER / Todos los proyectos" y "¿UN PROBLEMA PARECIDO? → / Agendar una llamada". Hover: fondo `#101310`.
6. **Footer**.

## Interactions & Behavior
- **Pestañas de proyecto (landing)**: fila de botones mono 11px ls 0.1em, padding 13×16, divisores 1px; activa en `#ECE6D9` con barra superior 2px siena (`position:absolute; top:-2px`), inactivas `#9C9789`, hover `#ECE6D9`. Panel de contenido con `min-height:196px` para que no salte el layout al cambiar. Estado independiente por proyecto; default = primera pestaña. Implementar con `role="tablist"` / `aria-selected` y navegación con flechas.
- **Menú móvil (landing, <820px)**: toggle "MENÚ ☰" / "CERRAR ✕". Panel inline bajo la nav (no overlay): 5 filas de 52px (nombre 17px + número mono), CTA verde 48px alto, mail. Tocar un link cierra el menú. Al pasar a ≥820px se cierra.
- **Scroll-spy (caso)**: sección activa = última cuyo `top` está a <180px del viewport. Recomendado `IntersectionObserver` en producción.
- `scroll-behavior: smooth` en el caso.
- **Links**: `a:hover` → `#8FB596`. Focus: agregar `:focus-visible { outline: 2px solid #8FB596; outline-offset: 2px }` (no está en el prototipo).
- Hit targets móviles ≥44px.

## Responsive
- Todo fluido; las grillas usan `repeat(auto-fit, minmax(min(100%, Npx), 1fr))` y se apilan solas.
- Breakpoints con JS en el prototipo: 820px (nav landing), 900px (índice del caso). En producción, pasar a media queries.
- Ningún elemento de texto con ancho fijo que desborde; los diagramas mono usan `overflow-x: auto`.

## State Management
- Landing: `tab` por proyecto (`bricka: 'arq'|'flujo'|'dec'`, `pipe: 'flujo'|'dec'`), `menuOpen`.
- Caso: `activeSection`.
- Flags de contenido (para decidir en build/CMS): mostrar retrato, mostrar Escritura, mostrar Verificable.
- Sin fetching. El blog debería alimentar la sección Escritura (3 últimos posts).

## Assets
- **Retrato**: 4:5 vertical, se muestra en escala de grises por CSS. Lo provee el autor.
- **CV PDF**: pendiente.
- Sin íconos; flechas como caracteres (↗ → ←), menú como ☰ / ✕.

## Pendientes
- Copy definitivo (lo escribe el autor), incluido Verificable.
- Posible repo público de docs para Bricka → volvería el link "↗ Documentación técnica".
- Caso del pipeline con la misma estructura (opcional).
- Versión EN (el toggle ES/EN ya está en la barra).

## Files
- `Landing Oscura.dc.html` — landing (referencia principal).
- `Caso Bricka.dc.html` — caso de estudio.
- `support.js`, `image-slot.js` — runtime del prototipo, solo para abrir los archivos localmente. No son parte de la implementación.
