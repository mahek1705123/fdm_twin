import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = ["django.contrib.staticfiles", "apps.lattice"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.middleware.common.CommonMiddleware",
              "django.middleware.csrf.CsrfViewMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "apps" / "lattice" / "web" / "templates"], "APP_DIRS": True,
              "OPTIONS": {"context_processors": ["django.template.context_processors.request"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {}  # the app is stateless: models are files, nothing is stored in a database
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "apps" / "lattice" / "web" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LATTICE_DATASET_CSV = BASE_DIR / "data" / "fdm_lattice_ml_dataset_clean.csv"
LATTICE_ARTIFACT_DIR = BASE_DIR / "artifacts"
