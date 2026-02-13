import json

from django.conf import settings
from django.core.management.base import BaseCommand

from jazztunes.models import RepertoireTune


class Command(BaseCommand):
    help = "Export admin user's tunes to JSON for seeding other environments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="jazztunes/fixtures/admin_tunes.json",
            help="Output file path (default: jazztunes/fixtures/admin_tunes.json)",
        )

    def handle(self, *args, **options):
        output_path = options["output"]

        rep_tunes = (
            RepertoireTune.objects.filter(player_id=settings.ADMIN_USER_ID)
            .select_related("tune")
        )

        if not rep_tunes.exists():
            self.stderr.write(
                self.style.ERROR("Admin user has no tunes to export.")
            )
            return

        data = []
        for rt in rep_tunes:
            tune = rt.tune
            data.append({
                "title": tune.title,
                "composer": tune.composer,
                "key": tune.key,
                "other_keys": tune.other_keys,
                "song_form": tune.song_form,
                "style": tune.style,
                "meter": tune.meter,
                "year": tune.year,
                "is_contrafact": tune.is_contrafact,
                "knowledge": rt.knowledge,
            })

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Exported {len(data)} tunes to {output_path}")
        )
