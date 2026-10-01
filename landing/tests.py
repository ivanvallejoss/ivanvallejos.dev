import copy
import re
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from . import content_loader
from .content_loader import load_content
from .models import OutboundClick, Visit
from .views import VARIANTS


class LandingTests(TestCase):
    """La landing y la atribución de audiencia por ?utm=.

    El sitio sirve una sola landing: la audiencia ya no elige plantilla, solo
    alimenta el tracking y los links /go/?a=. Se afirma sobre la Visit guardada
    y sobre el contexto, que es lo que consumen los links.
    """

    def test_landing_200(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing/landing.html")

    def test_variante_valida_se_registra_y_llega_al_contexto(self):
        for variante in sorted(VARIANTS):
            with self.subTest(variante=variante):
                Visit.objects.all().delete()
                response = self.client.get(reverse("landing") + f"?utm={variante}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["audience"], variante)
                self.assertEqual(Visit.objects.get().audience, variante)

    def test_utm_fuera_de_la_allowlist_cae_a_default(self):
        # Candado sobre la allowlist (views.py VARIANTS): es lo único que impide
        # que un querystring arbitrario llegue a un CharField(max_length=20).
        # Si alguien la reemplaza por algo permisivo, este test se cae.
        for utm in ["", "marketing", "../../../etc/passwd", "a" * 25]:
            with self.subTest(utm=utm):
                Visit.objects.all().delete()
                response = self.client.get(reverse("landing") + f"?utm={utm}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["audience"], "default")
                self.assertEqual(Visit.objects.get().audience, "default")


def con_contenido(flags=None, **bloques):
    """Parchea el loader de la vista para cambiar bloques de landing.yaml.

    `flags` se mezcla con los del YAML; cada bloque de `bloques` (p. ej.
    retrato={"ruta": ...}) se mezcla con el suyo. Devuelve una copia: con
    DEBUG=False el loader cachea el dict, y mutarlo en el lugar contaminaría
    a los demás tests.
    """

    def fake(name):
        data = copy.deepcopy(content_loader.load_content(name))
        if name == "landing":
            data["flags"].update(flags or {})
            for clave, valores in bloques.items():
                data[clave].update(valores)
        return data

    return mock.patch("landing.views.load_content", side_effect=fake)


def con_flags(**flags):
    """Atajo de con_contenido para cambiar solo flags."""
    return con_contenido(flags=flags)


class EstructuraTests(TestCase):
    """Barra superior, nav con menú móvil y footer (partials/)."""

    def get(self, query=""):
        response = self.client.get(reverse("landing") + query)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_nav_y_cta(self):
        html = self.get()
        for item in load_content("landing")["nav"]:
            with self.subTest(item=item["label"]):
                self.assertIn(f'href="{item["href"]}"', html)
                self.assertIn(item["label"], html)
        cta = load_content("sitio")["cta"]
        self.assertIn(f'href="/go/{cta["destino"]}?a=default">{cta["texto"]}</a>', html)

    def test_sin_escritura(self):
        with con_flags(escritura=False):
            html = self.get()
        self.assertNotIn("#escritura", html)
        self.assertNotIn("Escritura", html)

    def test_links_go_llevan_la_audiencia(self):
        html = self.get("?utm=recruiter")
        links = re.findall(r'href="(/go/[^"]*)"', html)
        self.assertTrue(links)
        for link in links:
            with self.subTest(link=link):
                self.assertTrue(link.endswith("?a=recruiter"))

    def test_selector_de_idioma_detras_del_flag(self):
        with con_flags(idiomas=False):
            self.assertNotIn("topbar__lang", self.get())
        # Control positivo: sin él, el test pasaría aunque la clase cambiara.
        with con_flags(idiomas=True):
            self.assertIn("topbar__lang", self.get())

    def test_boton_del_menu(self):
        html = self.get()
        boton = re.search(r"<button[^>]*site-nav__toggle[^>]*>", html)
        self.assertIsNotNone(boton)
        self.assertIn('aria-expanded="false"', boton.group())
        controls = re.search(r'aria-controls="([^"]+)"', boton.group()).group(1)
        self.assertIn(f'id="{controls}"', html)


class HeroTests(TestCase):
    """Hero (#perfil) con retrato y Antecedentes, y la fila de stack.

    Los textos se leen del YAML: el copy es provisorio y el autor lo reescribe.
    """

    def get(self, query=""):
        response = self.client.get(reverse("landing") + query)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_h1_y_ctas(self):
        hero = load_content("landing")["hero"]
        for query, audiencia in [("", "default"), ("?utm=recruiter", "recruiter")]:
            with self.subTest(audiencia=audiencia):
                html = self.get(query)
                self.assertIn(hero["titulo"], html)
                self.assertIn(
                    f'href="/go/contacto?a={audiencia}">{hero["cta_principal"]["texto"]}</a>', html
                )
                self.assertIn(
                    f'href="/go/cv?a={audiencia}">{hero["cta_secundario"]["texto"]}</a>', html
                )

    def test_ancla_perfil_y_un_solo_h1(self):
        html = self.get()
        self.assertIn('id="perfil"', html)
        self.assertEqual(html.count("<h1"), 1)

    def test_sin_retrato(self):
        leyenda = load_content("landing")["retrato"]["leyenda"]
        with con_flags(retrato=False):
            html = self.get()
        self.assertNotIn("retrato__marco", html)
        self.assertNotIn(leyenda, html)
        # Control positivo: con el flag, la caja y la leyenda están.
        with con_flags(retrato=True):
            html = self.get()
        self.assertIn("retrato__marco", html)
        self.assertIn(leyenda, html)

    def test_ruta_vacia_muestra_el_placeholder(self):
        with con_contenido(flags={"retrato": True}, retrato={"ruta": ""}):
            html = self.get()
        self.assertIn("retrato__marco", html)
        self.assertNotIn("<img", html)

    def test_con_ruta_hay_img_con_medidas(self):
        # Control positivo del anterior. Sin lazy-load: está arriba del pliegue.
        with con_contenido(flags={"retrato": True}, retrato={"ruta": "landing/img/retrato.jpg"}):
            html = self.get()
        img = re.search(r"<img[^>]*>", html)
        self.assertIsNotNone(img)
        self.assertIn('src="/static/landing/img/retrato.jpg"', img.group())
        self.assertIn(f'alt="{load_content("landing")["retrato"]["alt"]}"', img.group())
        self.assertRegex(img.group(), r'width="\d+"')
        self.assertRegex(img.group(), r'height="\d+"')
        self.assertNotIn("loading=", img.group())

    def test_antecedentes(self):
        filas = load_content("landing")["antecedentes"]["filas"]
        self.assertEqual(len(filas), 5)
        html = self.get()
        self.assertEqual(html.count("row row--split"), len(filas))
        for fila in filas:
            with self.subTest(fila=fila["label"]):
                self.assertIn(f'<span class="row__label">{fila["label"]}</span>', html)
                self.assertIn(f'<span class="row__value">{fila["valor"]}</span>', html)

    def test_stack(self):
        stack = load_content("landing")["stack"]
        self.assertEqual(len(stack), 12)
        html = self.get()
        ul = re.search(r'<ul class="stack[^"]*">(.*?)</ul>', html, re.S)
        self.assertIsNotNone(ul)
        self.assertEqual(re.findall(r"<li>(.*?)</li>", ul.group(1)), stack)


class AreasTests(TestCase):
    """01 Áreas de trabajo (#areas)."""

    def test_ancla_y_tres_items(self):
        items = load_content("landing")["areas"]["items"]
        self.assertEqual(len(items), 3)
        html = self.client.get(reverse("landing")).content.decode()
        self.assertIn('id="areas"', html)
        self.assertEqual(html.count('class="area '), len(items))
        for item in items:
            with self.subTest(item=item["titulo"]):
                self.assertIn(item["titulo"], html)
                self.assertIn(item["texto"], html)


class TrabajoTests(TestCase):
    """02 Trabajo entregado (#trabajo) y sus pestañas.

    La existencia del caso se parchea en la vista: los tests no crean archivos
    en content/casos/.
    """

    def get(self, tiene_caso=False):
        with mock.patch("landing.views.caso_existe", return_value=tiene_caso):
            response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_ancla_y_dos_proyectos(self):
        proyectos = load_content("landing")["trabajo"]["proyectos"]
        self.assertEqual(len(proyectos), 2)
        html = self.get()
        self.assertIn('id="trabajo"', html)
        self.assertEqual(len(re.findall(r'<article class="[^"]*\bproyecto\b', html)), len(proyectos))
        for proyecto in proyectos:
            with self.subTest(proyecto=proyecto["slug"]):
                self.assertIn(proyecto["titulo"], html)

    def test_pestanas_accesibles(self):
        html = self.get()
        listas = re.findall(r'role="tablist".*?</div>', html, re.S)
        self.assertEqual(len(listas), 2)
        for lista in listas:
            with self.subTest(lista=lista[:80]):
                self.assertEqual(lista.count('aria-selected="true"'), 1)
        # Solo las pestañas: el botón del menú también lleva aria-controls.
        controls = re.findall(r'role="tab"[^>]*aria-controls="([^"]+)"', html)
        self.assertEqual(len(controls), 5)
        for panel in controls:
            with self.subTest(panel=panel):
                self.assertRegex(html, rf'id="{panel}"[^>]*role="tabpanel"|role="tabpanel"[^>]*id="{panel}"')

    def test_ids_unicos(self):
        ids = re.findall(r'\sid="([^"]+)"', self.get())
        repetidos = {i for i in ids if ids.count(i) > 1}
        self.assertEqual(repetidos, set())

    def test_boton_del_caso_solo_con_caso(self):
        cta = load_content("landing")["trabajo"]["cta_caso"]
        html = self.get(tiene_caso=False)
        self.assertNotIn(cta, html)
        self.assertNotIn("/proyectos/", html)
        # Control positivo: con caso, el botón apunta a /proyectos/<slug>/.
        html = self.get(tiene_caso=True)
        self.assertIn(f'href="/proyectos/bricka/">{cta}</a>', html)

    def test_estado_en_produccion(self):
        # Bricka está en producción y Pipeline no: solo la fila marcada con
        # `produccion` lleva la clase. Los valores salen del YAML (copy provisorio).
        estado = {
            p["slug"]: next(f for f in p["filas"] if f["label"] == "Estado")
            for p in load_content("landing")["trabajo"]["proyectos"]
        }
        self.assertIs(estado["bricka"].get("produccion"), True)
        self.assertFalse(estado["pipeline"].get("produccion"))
        html = self.get()
        self.assertIn(f'<span class="row__value row__value--prod">{estado["bricka"]["valor"]}</span>', html)
        self.assertIn(f'<span class="row__value">{estado["pipeline"]["valor"]}</span>', html)
        self.assertEqual(html.count("row__value--prod"), 1)


def seccion(html, marca):
    """El <section> que abre con `marca` (p. ej. 'id="curso"'), hasta su cierre.

    Ninguna sección de la landing anida otra, así que el primer </section>
    después de la apertura es el suyo.
    """
    m = re.search(rf"<section [^>]*{marca}[^>]*>.*?</section>", html, re.S)
    return m.group() if m else None


class PaginaTests(TestCase):
    """La página completa con las secciones de la fase 5."""

    def get(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_anclas_un_h1_e_ids_unicos(self):
        # Con todos los flags de sección prendidos: es el caso con más ids.
        for flags in [{}, {"escritura": True, "verificable": True}]:
            with self.subTest(flags=flags), con_flags(**flags):
                html = self.get()
                for ancla in ["curso", "escritura", "contacto"]:
                    self.assertIn(f'id="{ancla}"', html)
                self.assertEqual(html.count("<h1"), 1)
                ids = re.findall(r'\sid="([^"]+)"', html)
                self.assertEqual({i for i in ids if ids.count(i) > 1}, set())


class CursoTests(TestCase):
    """03 En curso (#curso)."""

    def test_tres_items(self):
        items = load_content("landing")["curso"]["items"]
        self.assertEqual(len(items), 3)
        html = seccion(self.client.get(reverse("landing")).content.decode(), 'id="curso"')
        self.assertIsNotNone(html)
        self.assertEqual(html.count('class="curso__item"'), len(items))
        for item in items:
            with self.subTest(item=item["nombre"]):
                self.assertIn(item["nombre"], html)
                self.assertIn(
                    f'<span class="status status--{item["estado"]["tipo"]}">{item["estado"]["texto"]}</span>',
                    html,
                )

    def test_link_de_smartexpense(self):
        html = self.client.get(reverse("landing")).content.decode()
        self.assertIn('href="/go/smartexpense?a=default">↗ GitHub</a>', html)


class EscrituraTests(TestCase):
    """04 Escritura técnica (#escritura), detrás de flags.escritura."""

    def get(self, query=""):
        response = self.client.get(reverse("landing") + query)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_sin_flag_no_hay_seccion(self):
        titulo = load_content("landing")["escritura"]["titulo"]
        with con_flags(escritura=False):
            html = self.get()
        self.assertNotIn('id="escritura"', html)
        self.assertNotIn(titulo, html)
        # Control positivo.
        with con_flags(escritura=True):
            html = self.get()
        self.assertIn('id="escritura"', html)
        self.assertIn(titulo, html)

    def test_links_al_blog_pasan_por_go(self):
        escritura = load_content("landing")["escritura"]
        notas = next(
            i["link"]
            for i in load_content("landing")["curso"]["items"]
            if i.get("link", {}).get("destino") == "blog"
        )
        for query, audiencia in [("", "default"), ("?utm=recruiter", "recruiter")]:
            with self.subTest(audiencia=audiencia):
                html = self.get(query)
                self.assertIn(f'href="/go/blog?a={audiencia}">{escritura["blog"]["texto"]}</a>', html)
                self.assertIn(f'href="/go/blog?a={audiencia}">{notas["texto"]}</a>', html)

    def test_posts_van_directo_a_su_url(self):
        posts = load_content("landing")["escritura"]["posts"]
        self.assertEqual(len(posts), 3)
        html = seccion(self.get(), 'id="escritura"')
        self.assertIsNotNone(html)
        links = re.findall(r'<a class="post[^"]*" href="([^"]*)"', html)
        self.assertEqual(links, [p["url"] for p in posts])
        for link in links:
            with self.subTest(link=link):
                self.assertNotIn("/go/", link)
        for post in posts:
            with self.subTest(post=post["titulo"]):
                self.assertIn(post["titulo"], html)
                self.assertIn(f'{post["fecha"]} · {post["minutos"]} MIN', html)


class VerificableTests(TestCase):
    """05 Verificable, detrás de flags.verificable (apagado en el YAML).

    El flag se prende parcheando el loader: el YAML real no se toca.
    """

    def get(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_sin_flag_no_se_renderiza(self):
        verificable = load_content("landing")["verificable"]
        with con_flags(verificable=False):
            html = self.get()
        self.assertNotIn('class="verificable"', html)
        self.assertNotIn(verificable["label"], html)

    def test_con_flag_se_renderiza(self):
        verificable = load_content("landing")["verificable"]
        self.assertEqual(len(verificable["filas"]), 4)
        with con_flags(verificable=True):
            html = seccion(self.get(), 'class="verificable"')
        self.assertIsNotNone(html)
        self.assertIn(verificable["label"], html)
        self.assertIn(verificable["frase"], html)
        self.assertEqual(html.count('class="row row--inv"'), len(verificable["filas"]))
        for fila in verificable["filas"]:
            with self.subTest(fila=fila["label"]):
                self.assertIn(f'<span class="row__label">{fila["label"]}</span>', html)
                self.assertIn(f'<span class="row__value">{fila["texto"]}</span>', html)


class ContactoTests(TestCase):
    """Contacto (#contacto): dos celdas con CTA por /go/."""

    def test_ctas_llevan_la_audiencia(self):
        celdas = load_content("landing")["contacto"]["celdas"]
        self.assertEqual(len(celdas), 2)
        self.assertEqual([c["cta"]["destino"] for c in celdas], ["cv", "contacto"])
        for query, audiencia in [("", "default"), ("?utm=recruiter", "recruiter")]:
            with self.subTest(audiencia=audiencia):
                html = seccion(self.client.get(reverse("landing") + query).content.decode(), 'id="contacto"')
                self.assertIsNotNone(html)
                for celda in celdas:
                    cta = celda["cta"]
                    self.assertIn(
                        f'class="btn btn--{cta["variante"]} btn--compact contacto__cta" '
                        f'href="/go/{cta["destino"]}?a={audiencia}">{cta["texto"]}</a>',
                        html,
                    )


class CasoExisteTests(TestCase):
    """content_loader.caso_existe: decide si hay "Ver el caso completo"."""

    def test_sin_archivo_de_caso(self):
        self.assertIs(content_loader.caso_existe("no-existe"), False)

    def test_slug_invalido(self):
        for slug in ["../landing", "/etc/passwd", "casos/../x"]:
            with self.subTest(slug=slug):
                with self.assertRaises(ValueError):
                    content_loader.caso_existe(slug)


class ComentariosTests(TestCase):
    """{# #} de Django es de una sola línea: uno de varias líneas sale como texto.

    Pasó en base.html dentro del <head>: el parser cerraba el head ahí y el
    comentario quedaba visible arriba de la página.
    """

    def test_ningun_comentario_se_filtra_al_html(self):
        with self.settings(DEBUG=True):
            for url in [reverse("landing"), reverse("muestra")]:
                with self.subTest(url=url):
                    html = self.client.get(url).content.decode()
                    self.assertNotIn("{#", html)
                    self.assertNotIn("#}", html)


class GoTests(TestCase):
    """Los redirects /go/<destino>?a=<audiencia> y su OutboundClick."""

    def test_audiencia_valida(self):
        response = self.client.get(reverse("go", args=["github"]) + "?a=recruiter")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(OutboundClick.objects.get().audience, "recruiter")

    def test_audiencia_fuera_de_la_allowlist_cae_a_default(self):
        # El caso largo es el que daba 500 en PostgreSQL: el valor entraba sin
        # validar en un CharField(max_length=20).
        for a in ["", "marketing", "x" * 25]:
            with self.subTest(a=a):
                OutboundClick.objects.all().delete()
                response = self.client.get(reverse("go", args=["github"]) + f"?a={a}")
                self.assertEqual(response.status_code, 302)
                self.assertEqual(OutboundClick.objects.get().audience, "default")

    def test_destino_inexistente(self):
        response = self.client.get(reverse("go", args=["inexistente"]))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(OutboundClick.objects.exists())

    def test_cv_apunta_al_archivo_que_existe(self):
        # El destino apuntaba a /static/cv-ivan-vallejos.pdf y el archivo del
        # repo es landing/static/cv.ivanvallejos.pdf.
        response = self.client.get(reverse("go", args=["cv"]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/static/cv.ivanvallejos.pdf")

    def test_destino_mailto(self):
        # GoRedirect habilita el esquema mailto:, que Django bloquea por defecto.
        response = self.client.get(reverse("go", args=["contacto"]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("mailto:"))


class ContentLoaderTests(TestCase):
    """El loader de YAML (landing/content_loader.py)."""

    def test_flags(self):
        flags = load_content("landing")["flags"]
        self.assertIs(flags["verificable"], False)
        self.assertIs(flags["retrato"], True)
        self.assertIs(flags["escritura"], True)

    def test_meta_llega_al_documento(self):
        response = self.client.get(reverse("landing"))
        meta = load_content("landing")["meta"]
        self.assertContains(response, f"<title>{meta['title']}</title>", html=False)
        self.assertContains(response, meta["description"])

    def test_contenido_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            load_content("no-existe")

    def test_nombre_invalido(self):
        for name in ["../config/settings", "/etc/passwd", "casos/../../x"]:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    load_content(name)


class MuestraTests(TestCase):
    """El catálogo del sistema visual: /_muestra/ es solo de desarrollo."""

    def test_responde_con_debug(self):
        with self.settings(DEBUG=True):
            response = self.client.get(reverse("muestra"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing/muestra.html")

    def test_404_sin_debug(self):
        with self.settings(DEBUG=False):
            response = self.client.get(reverse("muestra"))
        self.assertEqual(response.status_code, 404)

    def test_las_fichas_salen_de_tokens_css(self):
        # El catálogo parsea tokens.css en vez de declarar sus propios hex.
        # Si el parseo se rompe, la muestra queda vacía sin avisar.
        with self.settings(DEBUG=True):
            response = self.client.get(reverse("muestra"))
        colores = dict(response.context["colores"])
        self.assertEqual(colores["--bg"], "#0C0E0C")
        self.assertEqual(colores["--accent-soft"], "#8FB596")
        self.assertEqual(len(colores), 18)
        self.assertIn("--gutter", dict(response.context["medidas"]))
