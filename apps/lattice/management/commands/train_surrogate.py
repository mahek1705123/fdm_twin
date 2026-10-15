from django.conf import settings
from django.core.management.base import BaseCommand

from apps.lattice.infrastructure.training import train_and_save


class Command(BaseCommand):
    help = "Train the lattice surrogate models and write them to the artifacts directory."

    def handle(self, *args, **opts):
        report = train_and_save(settings.LATTICE_DATASET_CSV, settings.LATTICE_ARTIFACT_DIR, log=self.stdout.write)
        self.stdout.write(self.style.SUCCESS(f"Saved models for {report['n']} rows to {settings.LATTICE_ARTIFACT_DIR}"))
