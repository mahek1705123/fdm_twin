"""Server-rendered pages. All data arrives later through the JSON API."""
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def ml_dashboard(request):
    return render(request, "lattice/ml.html", {"page": "ml"})


@ensure_csrf_cookie
def twin_dashboard(request):
    return render(request, "lattice/twin.html", {"page": "twin"})
