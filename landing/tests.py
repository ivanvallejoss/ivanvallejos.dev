import unittest

from django.test import Client, TestCase
from django.urls import reverse


class VariantResolutionTests(TestCase):
    """Resolución de variante por ?utm= en la view landing.

    La variante se resuelve en views.py:32, filtrando el querystring contra la
    allowlist VARIANTS (views.py:12). El string resultante se convierte en un
    nombre de plantilla por concatenación en base.html:26.

    El cliente se instancia con raise_request_exception=False para que un fallo
    de render llegue como respuesta 500 en lugar de propagar la excepción: así
    todos los tests pueden afirmar sobre el status code, incluso los rotos.

    Los tres tests de variantes válidas están marcados como expectedFailure. El
    día que exista el partial correspondiente van a pasar, unittest los va a
    reportar como unexpected success y el runner se va a poner en rojo, lo que
    obliga a sacar el decorador.
    """

    def setUp(self):
        self.client = Client(raise_request_exception=False)

    def assertHero(self, query, hero):
        response = self.client.get(reverse("landing") + query)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f"landing/partials/hero_{hero}.html")

    def test_sin_parametro(self):
        self.assertHero("", "default")

    def test_utm_vacio(self):
        self.assertHero("?utm=", "default")

    def test_utm_desconocido(self):
        self.assertHero("?utm=marketing", "default")

    @unittest.expectedFailure
    def test_variante_recruiter(self):
        # Falla hoy: "recruiter" pasa la allowlist, pero no existe
        # hero_recruiter.html, así que el include de base.html:26 levanta
        # TemplateDoesNotExist y la respuesta sale 500.
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=recruiter", "recruiter")

    @unittest.expectedFailure
    def test_variante_business(self):
        # Falla hoy: "business" pasa la allowlist, pero no existe
        # hero_business.html, así que el include de base.html:26 levanta
        # TemplateDoesNotExist y la respuesta sale 500.
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=business", "business")

    @unittest.expectedFailure
    def test_variante_tech(self):
        # Falla hoy: "tech" pasa la allowlist, pero no existe hero_tech.html,
        # así que el include de base.html:26 levanta TemplateDoesNotExist y la
        # respuesta sale 500.
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=tech", "tech")
