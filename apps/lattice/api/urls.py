from django.urls import path

from . import views

urlpatterns = [
    path("meta", views.meta), path("predict", views.predict), path("compare", views.compare),
    path("sensitivity", views.sensitivity), path("optimise", views.optimise), path("models", views.models),
    path("dataset", views.dataset), path("geometry", views.geometry), path("curves", views.curves),
    path("apdl", views.apdl), path("validate", views.validate),
]
