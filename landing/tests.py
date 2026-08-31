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
        # hero_recruiter.html, así que resolve_hero_audience cae a "default"
        # y se renderiza el hero equivocado (200, no el partial esperado).
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=recruiter", "recruiter")

    @unittest.expectedFailure
    def test_variante_business(self):
        # Falla hoy: "business" pasa la allowlist, pero no existe
        # hero_recruiter.html, así que resolve_hero_audience cae a "default"
        # y se renderiza el hero equivocado (200, no el partial esperado).
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=business", "business")

    @unittest.expectedFailure
    def test_variante_tech(self):
        # Falla hoy: "tech" pasa la allowlist, pero no existe
        # hero_recruiter.html, así que resolve_hero_audience cae a "default"
        # y se renderiza el hero equivocado (200, no el partial esperado).
        # Bug preexistente registrado en docs/frontend/cimientos.md:106.
        self.assertHero("?utm=tech", "tech")

    def test_utm_path_traversal(self):
        # Candado sobre la protección que da la allowlist: el valor de ?utm= se
        # concatena a un nombre de plantilla en base.html:26, así que un utm
        # arbitrario llegaría al loader si views.py:32 no filtrara antes.
        # Al caer a "default" nunca sale de la allowlist. Si alguien reemplaza
        # el filtro por algo permisivo, este test se cae.
        self.assertHero("?utm=../../../etc/passwd", "default")

    def test_variante_valida_no_rompe(self):
        # A propósito SIN expectedFailure: deja la suite en rojo mientras una
        # variante declarada en VARIANTS (views.py:12) siga devolviendo 500 por
        # no tener su partial. Ver docs/frontend/cimientos.md:106.
        response = self.client.get(reverse("landing") + "?utm=recruiter")
        self.assertEqual(response.status_code, 200)
