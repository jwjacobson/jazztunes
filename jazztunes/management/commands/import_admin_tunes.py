import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from jazztunes.models import RepertoireTune, Tune


class Command(BaseCommand):
    help = "Import admin tunes from JSON export"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            default="jazztunes/fixtures/admin_tunes.json",
            help="Input file path (default: jazztunes/fixtures/admin_tunes.json)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing admin tunes before importing",
        )

    def handle(self, *args, **options):
        input_path = options["input"]
        User = get_user_model()

        try:
            admin_user = User.objects.get(id=settings.ADMIN_USER_ID)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"Admin user (id={settings.ADMIN_USER_ID}) not found. "
                    "Create the admin user first."
                )
            )
            return

        try:
            with open(input_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {input_path}"))
            return

        if options["clear"]:
            with transaction.atomic():
                count, _ = RepertoireTune.objects.filter(player=admin_user).delete()
            self.stdout.write(f"  Cleared {count} existing admin records")

        created = 0
        skipped = 0

        for entry in data:
            entry.pop("tags", None)
            knowledge = entry.pop("knowledge", "know")

            # skip if admin already has a tune with this title
            if RepertoireTune.objects.filter(
                player=admin_user, tune__title=entry["title"]
            ).exists():
                skipped += 1
                continue

            with transaction.atomic():
                tune = Tune.objects.create(created_by=admin_user, **entry)
                RepertoireTune.objects.create(
                    tune=tune,
                    player=admin_user,
                    knowledge=knowledge,
                )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created} tunes, skipped {skipped} duplicates"
            )
        )
