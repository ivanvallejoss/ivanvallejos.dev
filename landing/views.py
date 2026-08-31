from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

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

# ticker de tecnologías (include parametrizado)
TICKER_ITEMS = [
    "Python", "Django", "FastAPI", "Celery", "PostgreSQL", "Redis",
    "Docker", "Go", "Linux", "pytest", "Sentry", "Cloudflare R2",
]


def resolve_hero_audience(audience):
    """Cae a default si la variante todavía no tiene su partial.

    base.html:26 arma el nombre de plantilla por concatenación, así que una
    variante declarada en VARIANTS sin hero_<variante>.html rompe el include
    con TemplateDoesNotExist y devuelve 500 (docs/frontend/cimientos.md:106).
    """
    try:
        get_template(f"landing/partials/hero_{audience}.html")
    except TemplateDoesNotExist:
        return "default"
    return audience


def landing(request):
    utm = request.GET.get("utm", "")
    # La allowlist va primero: es lo que impide que un utm arbitrario llegue al
    # loader de plantillas. La existencia del partial se chequea después.
    audience = utm if utm in VARIANTS else "default"
    # Visit registra la audiencia real, aunque el hero caiga a default.
    Visit.objects.create(audience=audience, path=request.path)
    context = {
        "audience": resolve_hero_audience(audience),
        "ticker_items": TICKER_ITEMS,
    }
    return render(request, "landing/base.html", context)


def go(request, destination):
    url = DESTINATIONS.get(destination)
    if url is None:
        return HttpResponseNotFound()
    audience = request.GET.get("a", "default")
    OutboundClick.objects.create(destination=destination, audience=audience)
    return GoRedirect(url)