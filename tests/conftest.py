import pytest
from datetime import timedelta
from django.utils import timezone
from jazztunes.models import Tune, RepertoireTune, Play

TEN_TUNES = [
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


@pytest.fixture()
def create_base_tunes():
    """Creates Tune objects"""

    def _create_tunes(tunes_data=TEN_TUNES):
        for tune_data in tunes_data:
            Tune.objects.create(**tune_data)
        return Tune.objects.all()

    return _create_tunes


@pytest.fixture()
def create_tune_set_for_user(create_base_tunes):
    """Factory fixture that creates repertoire tunes for regular users"""

    def _create_tune_set(user, tunes_data=TEN_TUNES, is_admin=False):
        tunes = create_base_tunes(tunes_data)

        now = timezone.now()
        knowledges = ("know", "learning", "don't know")

        for i, tune in enumerate(tunes):
            rep_tune = RepertoireTune.objects.create(
                tune=tune,
                player=user,
                knowledge="know" if is_admin else knowledges[i % 3],
            )

            if not is_admin:
                Play.objects.create(repertoire_tune=rep_tune)
                # Backdate the auto_now_add timestamp
                played_at = now - timedelta(days=i + 1)
                Play.objects.filter(pk=rep_tune.plays.first().pk).update(
                    played_at=played_at
                )

        rep_tunes = RepertoireTune.objects.filter(player=user)
        return {"user": user, "tunes": rep_tunes}

    return _create_tune_set
