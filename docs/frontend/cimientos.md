# CIMIENTO v1 — DISEÑO E IMPLEMENTACIÓN DEFAULT (rev. 3 — FINAL)

**Proyecto:** ivanvallejos.dev · variante default
**Sesión:** Implementación Django/CSS del diseño cerrado + partials + retoques de estilo
**Fecha:** 2026-07-24/25
**Estado:** Variante default IMPLEMENTADA, verificada en browser por Ivan, con
retoques de estilo aplicados y funcionando. Sin deploy (fuera de scope).

> Informe de recuperación de estado. Es el ÚNICO registro persistente del diseño
> y de esta sesión: redactado como si la sesión de Claude Design y esta pudieran
> perderse. Vuelve a la ventana orquestadora de la landing.

---

## 1. SISTEMA DE DISEÑO (registro persistente, con retoques incorporados)

### 1.1 Tokens (tokens.css)

```css
--amber:  oklch(0.78 0.13 70)   /* ÚNICO color de marca */
--signal: oklch(0.72 0.12 155)  /* verde semántico: SOLO estados vivos, nunca decorativo */
--ink:#f2f2f0 --ink-2:#c9c9c3 --ink-3:#a6a6a0 --ink-4:#77776f --ink-5:#5c5c58
--mod-neutral:#17171a --mod-warm:#201914 --mod-slate:#14161c --mod-deep:#0f0f12
--bg-solid:#0b0b0d --band-bg:rgba(10,10,11,.72) --line:rgba(255,255,255,.07)
--font-sans:"Geist" --font-mono:"Geist Mono"
--font-display:var(--font-mono)  /* H1 del nombre + .sec-title en MONO (decisión Ivan) */
--nav-h:60px --pad-x:clamp(20px,5vw,48px) --container:1100px
/* fondo página: gradient 180deg #100f0d→#0c0b0c(42%)→#08080a, fixed */
```

Fuentes SELF-HOSTED: variable fonts del paquete npm oficial `geist`
(Geist-Variable.woff2 69.652 B · GeistMono-Variable.woff2 71.368 B), preload en
base.html, fallback de sistema. Sin CDN.
Breakpoint único **841px**, mobile-first (base = mobile). Tokenización: núcleo
tokenizado; alphas de una sola aparición quedan literales (promover a token
recién cuando las variantes muestren reuso).

### 1.2 La firma: sistema de módulos (backdrop.html + layout.css)

- Desktop 4×4 / mobile 2×4 (módulos 9–16 ocultos), gap 10/8px, radius 3px.
- Pulso asimétrico 6s (pico 12%), delays col .45s + fila .3s → cresta diagonal.
- Intensidad por columna izq→der: .20/.33/.46/.58. Módulo 9 "hueco" (.10, estático).
- Señales en gaps: rieles 25/50/75%V + 50%H; v1(7s)/v3(9s,−3s)/h2(11s,−5s) con
  pulso ámbar; v2 estático en desktop. En mobile: solo v2 visible, CON señal
  (materializada vía .gapline.v2::after, <841px). REGLA DURA: máx 3 señales.
- prefers-reduced-motion: congela frags, señales, ring, ticker, bio-mods, esquema.

### 1.3 Composición default (base.html = shell + 11 partials)

``` mermaid
backdrop → nav → hero_{audience} → ticker → section_perfil → section_proyectos
→ interlude_blog → section_confianza → section_links → interlude_quote → footer
```

CTA primario "Contactame" = único botón sólido ámbar → /go/contacto (mailto
trackeado). Secundario default = CV → /go/cv. TODO link saliente por
`/go/<destino>?a={{ audience }}`.

## 2. RETOQUES DE ESTILO DE LA SESIÓN (registro completo)

| # | Retoque | Estado |
| --- | --- | --- |
| R1 | **Bio-mods mobile en fila con wrap**: 2 por fila (`flex: 1 1 calc(50% - 5px)`, min 150px), el 3.º baja a ancho completo; desktop vuelve a fila simple. | ✅ conforme |
| R2 | **Esquema orquestado en profile-main** (SVG inline, no Higgsfield — coherente con el descarte de raster): hub central warm SIN etiqueta + 4 servicios sin nombrar + módulo hueco (guiño al backdrop), rieles ortogonales, **3 puntos ámbar** (círculo 2.2 + halo) viajando con `animateMotion` a timings independientes (4.2/6.5/5.3s). 4.º riel silencioso POR REGLA DURA (máx 3) — Ivan puede habilitarlo bajo su riesgo agregando un `<g>` con `path="M78 134 H178 V102"`. Nodos pulsan escalonados (6s, como los frags). | ✅ conforme |
| R3 | **Tercer módulo lateral "En el radar"** (Go · ingeniería de datos, framing honesto: "lo que estoy incorporando, no lo que vendo todavía") — reemplaza la línea .path-radar. Grid fix: `.profile-main{grid-row:1/span 3}` + `.profile-grid{grid-auto-rows:1fr}` → los 3 laterales reparten EXACTO la altura del main, contenido centrado con flex. Nota: la altura del main manda; si un path queda justo, reducir padding de .path o el viewBox del esquema. | ✅ conforme |
| R4 | **Blog como pila de posts navegable**: card principal (último post, con metadata `12 jul 2026 · 6 min de lectura`) + 2 hojas que asoman debajo (38px c/u) que SON links reales a posts anteriores, título + ↗ siempre visibles (sin depender de hover → funciona en mobile). Ghosts eliminados (markup y CSS). Sigue siendo UN objeto (regla del interludio, no carrusel). | ✅ conforme |
| R5 | Prueba social: SIN retoque a propósito — bloqueada por contenido real (nombres/testimonio), no por diseño. Recomendación registrada: nombres en mono uppercase, no logos a color; opción de comentar la sección hasta tener datos. | ⏸ espera contenido |

Componentes CSS nuevos: `.asm .asm-rail .asm-node(.warm/.hollow) .asm-sig(-halo)`
· `.blog-stack .blog-sheet(.s1/.s2)`. Eliminados: `.path-radar` (uso), `.blog-ghosts`.

## 3. ARCHIVOS — ESTADO FINAL EN EL REPO DE IVAN

```python
landing/views.py                       1.578 B  (DESTINATIONS +contacto/handles, GoRedirect
                                                 con mailto, ticker_items; Visit intacto)
landing/static/landing/css/fonts.css     493 B
landing/static/landing/css/tokens.css  1.820 B
landing/static/landing/css/layout.css  6.774 B
landing/static/landing/css/components.css 17.226 B  (incluye R1–R4)
landing/static/landing/fonts/Geist-Variable.woff2      69.652 B
landing/static/landing/fonts/GeistMono-Variable.woff2  71.368 B
landing/templates/landing/base.html    1.883 B  (shell de composición)
landing/templates/landing/partials/
  backdrop.html 767 · nav.html 503 · ticker.html 477 · hero_default.html 2.169
  section_perfil.html 3.647 (R2+R3) · section_proyectos.html 2.641
  interlude_blog.html 960 (R4) · section_confianza.html 1.365
  section_links.html 1.331 · interlude_quote.html 235 · footer.html 534
```

Los tamaños en bytes sirven como checksum rápido (`wc -c`) tras cualquier copia
manual — ya nos salvó una vez (layout.css duplicado con el contenido de tokens.css).

## 4. VERIFICADO

- Contratos intactos: `include hero_<audience>, 16 links /go/?a=`r
  audiencia, OutboundClick con redirect 302 (mailto y https).
- Render en browser de Ivan: backdrop + señales, secciones contenidas a 1100px,
  Geist Mono en H1/títulos, esquema animado, pila del blog, 3 laterales encastrados.
- collectstatic OK · h1×1/h2×4/h3×2 · focus-visible ámbar · reduced-motion total
  · SVG del esquema validado como XML.
- Nota AA registrada: --ink-5 bajo AA solo en uso decorativo/meta (aceptado).

## 5. PENDIENTES Y FASE SIGUIENTE

**Preexistente:** `?utm=recruiter|business|tech` → 500 (solo existe hero_default).
Resolver en fase de variantes (o fallback a default en la view para blindar antes).
**Contenido (no bloquea):** copy definitivo, screenshots reales (.shot), clientes
y testimonio reales (desbloquea R5), PDF del CV en /static/cv-ivan-vallejos.pdf,
posts reales del blog (título/fecha/minutos de la pila — hoy placeholders
marcados EN PRODUCCIÓN; con títulos largos agregar ellipsis a .blog-sheet),
verificar handles `ivanvallejoss` (marcados PENDIENTE en views.py).
**Fase lógica siguiente — VARIANTES POR AUDIENCIA:**

1. Formalizar composición vs partial-por-variante (la composición ya está montada
   y probada; los partials son agnósticos).
2. hero_recruiter / hero_business / hero_tech (secundario: CV / ninguno / GitHub).
3. section_formacion para recruiter·tech (CSS .edu-grid/.stack-domain ya listo;
   tech invierte énfasis: stack primero).
4. Después: OG image (asset Higgsfield — guardarlo antes de que expire), i18n del
   selector ES/EN, subdominio del blog, deploy (collectstatic en prod).
