import pytest
from datetime import timedelta
from django.utils import timezone
from tune.models import Tune, RepertoireTune


@pytest.fixture()
def create_tune_set_for_user():
    """Factory fixture that creates a small set of real tunes for the user"""

    def _create_tune_set(user):
        tunes_data = [
            {
                "title": "Confirmation",
                "composer": "Parker",
                "key": "F",
                "other_keys": "D- Bb Db",
                "song_form": "AABA",
                "style": "jazz",
                "meter": 4,
                "year": 1945,
            },
            {
                "title": "Dewey Square",
                "composer": "Parker",
                "key": "Eb",
                "other_keys": "Ab",
                "song_form": "AABA",
                "style": "jazz",
                "meter": 4,
                "year": 1947,
            },
            {
                "title": "All the Things You Are",
                "composer": "Kern",
                "key": "Ab",
                "other_keys": "C Eb G E",
                "song_form": "AABA",
                "style": "standard",
                "meter": 4,
                "year": 1939,
            },
            {
                "title": "Dearly Beloved",
                "composer": "Kern",
                "key": "C",
                "other_keys": "Db",
                "song_form": "ABAC",
                "style": "standard",
                "meter": 4,
                "year": 1942,
            },
            {
                "title": "Long Ago and Far Away",
                "composer": "Kern",
                "key": "F",
                "other_keys": "Ab C Bb",
                "song_form": "ABAC",
                "style": "standard",
                "meter": 4,
                "year": 1944,
            },
            {
                "title": "Coming on the Hudson",
                "composer": "Monk",
                "song_form": "AABA",
                "style": "jazz",
                "meter": 4,
                "year": 1958,
            },
            {
                "title": "Someday My Prince Will Come",
                "composer": "Churchill",
                "key": "Bb",
                "other_keys": "C- Eb",
                "song_form": "ABAC",
                "style": "standard",
                "meter": 3,
                "year": 1937,
            },
            {
                "title": "Kary's Trance",
                "composer": "Konitz",
                "key": "A-",
                "other_keys": "D- C",
                "song_form": "AABA",
                "style": "jazz",
                "meter": 4,
                "year": 1956,
            },
            {
                "title": "A Flower is a Lovesome Thing",
                "composer": "Strayhorn",
                "key": "Db",
                "other_keys": "D",
                "song_form": "AABA",
                "style": "jazz",
                "meter": 4,
                "year": 1941,
            },
            {
                "title": "I Remember You",
                "composer": "Schertzinger",
                "key": "F",
                "other_keys": "Bb D C G-",
                "song_form": "AABA",
                "style": "standard",
                "meter": 4,
                "year": 1941,
            },
        ]

        now = timezone.now()

        for i, tune_data in enumerate(tunes_data):
            tune = Tune.objects.create(**tune_data)
            # Create a range of last_played dates
            last_played_date = now - timedelta(days=i + 1)
            _ = RepertoireTune.objects.create(
                tune=tune, player=user, last_played=last_played_date
            )

        rep_tunes = RepertoireTune.objects.filter(player=user)

        return {"user": user, "tunes": rep_tunes}

    return _create_tune_set
