import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from jazztunes.models import Play, RepertoireTune, Tag

TAG_NAMES = ["ballad", "up", "medium", "rhythm", "latin", "modal", "bop", "free"]

# Weighted play distribution: (percent_of_tunes, (min_plays, max_plays))
# Percentages must add to 100.
PLAY_TIERS = [
    (10, (30, 60)),  # heavy rotation
    (20, (10, 29)),  # regular plays
    (40, (2, 9)),  # occasional
    (20, (1, 1)),  # played once
    (10, (0, 0)),  # never played
]


class Command(BaseCommand):
    help = (
        "Create a test user with repertoire and play history for analytics development"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="miles",
            help="Username for the test user (default: miles)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=365,
            help="Days of play history to generate (default: 365)",
        )
        parser.add_argument(
            "--num-tunes",
            type=int,
            default=100,
            help="Number of tunes to include (default: 100)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        days = options["days"]
        num_tunes = options["num_tunes"]

        admin_rep_tunes = list(
            RepertoireTune.objects.filter(
                player_id=settings.ADMIN_USER_ID
            ).select_related("tune")
        )

        if not admin_rep_tunes:
            self.stderr.write(
                self.style.ERROR(
                    "Admin user has no tunes. Run import_admin_tunes first."
                )
            )
            return

        if num_tunes > len(admin_rep_tunes):
            self.stdout.write(
                self.style.WARNING(
                    f"Requested {num_tunes} tunes but admin only has "
                    f"{len(admin_rep_tunes)}. Using all {len(admin_rep_tunes)}."
                )
            )
            num_tunes = len(admin_rep_tunes)

        user = self._create_user(username)
        tags = self._create_tags()
        rep_tunes = self._create_repertoire(user, admin_rep_tunes, tags, num_tunes)
        play_count = self._generate_plays(rep_tunes, days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created '{username}' with {len(rep_tunes)} tunes "
                f"and {play_count} plays across {days} days"
            )
        )

    def _create_user(self, username):
        """Create or reset the test user. Cascade-deletes all related data."""
        User = get_user_model()
        User.objects.filter(username=username).delete()
        self.stdout.write(f"  Creating user '{username}'...")
        return User.objects.create_user(username=username, password="password")

    def _create_tags(self):
        """Ensure tags exist, return list of Tag objects."""
        tags = []
        for name in TAG_NAMES:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        return tags

    def _create_repertoire(self, user, admin_rep_tunes, tags, num_tunes):
        """Clone a sample of admin tunes into the test user's repertoire."""
        sample = random.sample(admin_rep_tunes, num_tunes)
        rep_tunes = []

        for admin_rt in sample:
            with transaction.atomic():
                tune = admin_rt.tune
                tune.pk = None
                tune.created_by = user
                tune.save()

                rt = RepertoireTune.objects.create(
                    tune=tune,
                    player=user,
                    knowledge=random.choice(
                        ["know", "know", "know", "learning", "don't know"]
                    ),
                )
                rt.tags.set(random.sample(tags, k=random.randint(0, 3)))

            rep_tunes.append(rt)

        self.stdout.write(f"  Created {len(rep_tunes)} repertoire tunes")
        return rep_tunes

    def _generate_plays(self, rep_tunes, days):
        """
        Generate play history with a realistic long-tail distribution.
        """
        now = timezone.now()
        shuffled = rep_tunes[:]
        random.shuffle(shuffled)

        plays = []
        index = 0

        for percent, (low, high) in PLAY_TIERS:
            count = max(1, len(shuffled) * percent // 100)
            tier_tunes = shuffled[index : index + count]
            index += count

            for rt in tier_tunes:
                num_plays = random.randint(low, high)
                for _ in range(num_plays):
                    played_at = now - timedelta(
                        days=random.randint(0, days),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )
                    plays.append(Play(repertoire_tune=rt, played_at=played_at))

        Play.objects.bulk_create(plays)
        self.stdout.write(f"  Generated {len(plays)} plays across {days} days")
        return len(plays)
