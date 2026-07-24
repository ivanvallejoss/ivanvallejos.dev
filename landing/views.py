from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from .models import OutboundClick, Visit

VARIANTS = {"recruiter", "business", "tech"}

DESTINATIONS = {
    "github": "https://github.com/tu-usuario",
    "linkedin": "https://linkedin.com/in/tu-usuario",
    "blog": "https://blog.ivanvallejos.dev",
    "cv": "/static/cv-ivan-vallejos.pdf",  # placeholder hasta tener el CV subido
}


def landing(request):
    utm = request.GET.get("utm", "")
    audience = utm if utm in VARIANTS else "default"
    Visit.objects.create(audience=audience, path=request.path)
    return render(request, "landing/base.html", {"audience": audience})


def go(request, destination):
    url = DESTINATIONS.get(destination)
    if url is None:
        return HttpResponseNotFound()
    audience = request.GET.get("a", "default")
    OutboundClick.objects.create(destination=destination, audience=audience)
    return HttpResponseRedirect(url)