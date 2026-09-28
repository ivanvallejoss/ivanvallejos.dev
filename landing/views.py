from django.http import HttpResponseRedirect, HttpResponseNotFound
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
