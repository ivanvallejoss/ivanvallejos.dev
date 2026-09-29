from django.test import TestCase
from django.urls import reverse

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
