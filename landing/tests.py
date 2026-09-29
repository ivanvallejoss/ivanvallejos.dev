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
