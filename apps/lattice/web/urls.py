from django.urls import path

from . import views

urlpatterns = [path("", views.ml_dashboard, name="ml"), path("twin/", views.twin_dashboard, name="twin")]
