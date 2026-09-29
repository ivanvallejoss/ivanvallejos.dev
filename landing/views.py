import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render

from .content_loader import load_content
from .models import OutboundClick, Visit


class GoRedirect(HttpResponseRedirect):
    """Redirect de /go/ — habilita mailto: además de http(s) (Django lo bloquea por defecto)."""

    allowed_schemes = ["http", "https", "mailto"]

# Allowlist de audiencias. Es lo único que decide qué llega a la DB, tanto por
# ?utm= en la landing como por ?a= en los redirects: Visit.audience y
# OutboundClick.audience son CharField(max_length=20).
VARIANTS = {"recruiter", "business", "tech"}

DESTINATIONS = {
    "github": "https://github.com/ivanvallejoss",  # PENDIENTE: verificar handle
    "linkedin": "https://linkedin.com/in/ivanvallejoss",  # PENDIENTE: verificar handle
    "blog": "https://blog.ivanvallejos.dev",
    "smartexpense": "https://github.com/ivanvallejoss/smartexpense",
    "cv": "/static/cv.ivanvallejos.pdf",
    "contacto": "mailto:ivan@ivanvallejos.dev",  # CTA primario, trackeado como OutboundClick
}


def resolve_audience(value):
    """Todo lo que no esté declarado en VARIANTS cae a "default"."""
    return value if value in VARIANTS else "default"


def landing(request):
    audience = resolve_audience(request.GET.get("utm", ""))
    Visit.objects.create(audience=audience, path=request.path)
    # La audiencia viaja sin resolver contra plantillas: el sitio sirve una sola
    # landing y la audiencia solo alimenta el tracking y los links /go/?a=.
    context = {"audience": audience, **load_content("landing")}
    return render(request, "landing/landing.html", context)


def go(request, destination):
    url = DESTINATIONS.get(destination)
    if url is None:
        return HttpResponseNotFound()
    # Misma allowlist que la landing: un ?a= arbitrario más largo que el campo
    # daba 500 en PostgreSQL (SQLite lo truncaba en silencio).
    audience = resolve_audience(request.GET.get("a", ""))
    OutboundClick.objects.create(destination=destination, audience=audience)
    return GoRedirect(url)


# Rótulos de la muestra: clase, valor declarado y texto de demostración. Son
# rótulos técnicos a propósito — la muestra no lleva copy del sitio.
ESCALA = [
    ("t-h1", "clamp(34px, 4.2vw, 50px) · 600 · lh 1.1 · ls -0.025em", "H1 de landing"),
    ("t-h1-caso", "clamp(36px, 5vw, 60px) · 600 · lh 1.05 · ls -0.03em", "H1 de caso"),
    ("t-h2", "clamp(24px, 2.6vw, 30px) · 600 · ls -0.018em", "H2 de sección"),
    ("t-project", "clamp(22px, 2.4vw, 28px) · 600 · ls -0.022em", "Título de proyecto"),
    ("t-sub", "19px · 600", "Subtítulo o ítem"),
    ("t-lead", "clamp(16px, 1.5vw, 18px) · 400 · lh 1.65", "Lead: el párrafo de apertura de una sección, en color de cuerpo."),
    ("t-body", "15px · 400 · lh 1.65", "Cuerpo base: áreas de trabajo y celdas de contacto."),
    ("t-body-m", "15.5px · 400 · lh 1.65", "Cuerpo medio: descripciones de En curso."),
    ("t-body-l", "16.5px · 400 · lh 1.65", "Cuerpo grande: párrafo de proyecto entregado."),
    ("t-row", "14.5px · 400", "Fila de tabla"),
    ("t-label", "mono 11.5px · ls 0.11em · mayúsculas", "LABEL BASE"),
    ("t-label t-label--wide", "mono 11.5px · ls 0.13em", "KICKER DEL HERO"),
    ("t-label t-label--kicker", "mono 11.5px · ls 0.1em", "KICKER DE PROYECTO"),
    ("t-label t-label--tight", "mono 11.5px · ls 0.09em", "ESTADO Y CAPTION"),
    ("t-label t-label--bar", "mono 11.5px · ls 0.07em", "BARRA SUPERIOR"),
    ("t-label t-label--sm", "mono 11px · ls 0.1em", "NAV Y PESTAÑAS"),
    ("t-meta", "mono 12.5px", "Stack y metadata mono"),
]

_TOKEN = re.compile(r"^\s*(--[a-z0-9-]+):\s*([^;]+);", re.MULTILINE)


def _tokens_declarados():
    """Lee los tokens de tokens.css y los separa en colores y medidas.

    Se parsea en vez de repetir los valores acá: un catálogo que declara sus
    propios hex se desincroniza del sistema en el primer ajuste.
    """
    path = finders.find("landing/css/tokens.css")
    if path is None:
        return [], []
    css = Path(path).read_text(encoding="utf-8")
    colores, medidas = [], []
    for name, value in _TOKEN.findall(css):
        value = value.strip()
        (colores if value.startswith("#") else medidas).append((name, value))
    return colores, medidas


def muestra(request):
    """Catálogo visual de tokens y primitivas. Referencia de desarrollo.

    No es una página del sitio: existe para revisar el sistema contra el README
    del handoff a 375, 820 y 1280px. Fuera de DEBUG no existe.
    """
    if not settings.DEBUG:
        raise Http404
    colores, medidas = _tokens_declarados()
    context = {
        "meta": {"title": "Sistema editorial — muestra"},
        "colores": colores,
        "medidas": medidas,
        "escala": ESCALA,
    }
    return render(request, "landing/muestra.html", context)
