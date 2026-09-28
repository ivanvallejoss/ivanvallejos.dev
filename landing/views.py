from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from .models import OutboundClick, Visit


class GoRedirect(HttpResponseRedirect):
    """Redirect de /go/ — habilita mailto: además de http(s) (Django lo bloquea por defecto)."""

    allowed_schemes = ["http", "https", "mailto"]

VARIANTS = {"recruiter", "business", "tech"}

DESTINATIONS = {
    "github": "https://github.com/ivanvallejoss",  # PENDIENTE: verificar handle
    "linkedin": "https://linkedin.com/in/ivanvallejoss",  # PENDIENTE: verificar handle
    "blog": "https://blog.ivanvallejos.dev",
    "smartexpense": "https://github.com/ivanvallejoss/smartexpense",
    "cv": "/static/cv-ivan-vallejos.pdf",  # placeholder hasta tener el CV subido
    "contacto": "mailto:ivan@ivanvallejos.dev",  # CTA primario, trackeado como OutboundClick
}


def landing(request):
    utm = request.GET.get("utm", "")
    # La allowlist es lo que impide que un utm arbitrario llegue a la DB o al
    # contexto. Todo lo que no esté declarado en VARIANTS cae a "default".
    audience = utm if utm in VARIANTS else "default"
    Visit.objects.create(audience=audience, path=request.path)
    context = {
        "audience": audience,
    }
    return render(request, "landing/base.html", context)


def go(request, destination):
    url = DESTINATIONS.get(destination)
    if url is None:
        return HttpResponseNotFound()
    audience = request.GET.get("a", "default")
    OutboundClick.objects.create(destination=destination, audience=audience)
    return GoRedirect(url)
