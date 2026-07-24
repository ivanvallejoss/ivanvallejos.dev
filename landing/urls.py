from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("go/<slug:destination>", views.go, name="go"),
]