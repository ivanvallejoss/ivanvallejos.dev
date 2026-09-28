from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("go/<slug:destination>", views.go, name="go"),
    # Catálogo del sistema visual. Solo con DEBUG (ver views.muestra).
    path("_muestra/", views.muestra, name="muestra"),
]