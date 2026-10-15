from django.urls import include, path

urlpatterns = [path("api/", include("apps.lattice.api.urls")), path("", include("apps.lattice.web.urls"))]
