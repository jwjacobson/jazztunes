import pytest
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from tune.models import Tune, RepertoireTune


@pytest.fixture()
def tune_set(db, client):
    """
    Create a tune set for use in tests that require one.
    """
    tunes = {
        Tune.objects.create(
            title="Confirmation",
            composer="Parker",
            key="F",
            other_keys="D- Bb Db",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1945,
        ),
        Tune.objects.create(
            title="Dewey Square",
            composer="Parker",
            key="Eb",
            other_keys="Ab",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1947,
        ),
        Tune.objects.create(
            title="All the Things You Are",
            composer="Kern",
            key="Ab",
            other_keys="C Eb G E",
            song_form="AABA",
            style="standard",
            meter=4,
            year=1939,
        ),
        Tune.objects.create(
            title="Dearly Beloved",
            composer="Kern",
            key="C",
            other_keys="Db",
            song_form="ABAC",
            style="standard",
            meter=4,
            year=1942,
        ),
        Tune.objects.create(
            title="Long Ago and Far Away",
            composer="Kern",
            key="F",
            other_keys="Ab C Bb",
            song_form="ABAC",
            style="standard",
            meter=4,
            year=1944,
        ),
        Tune.objects.create(
            title="Coming on the Hudson",
            composer="Monk",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1958,
        ),
        Tune.objects.create(
            title="Someday My Prince Will Come",
            composer="Churchill",
            key="Bb",
            other_keys="C- Eb",
            song_form="ABAC",
            style="standard",
            meter=3,
            year=1937,
        ),
        Tune.objects.create(
            title="Kary's Trance",
            composer="Konitz",
            key="A-",
            other_keys="D- C",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1956,
        ),
        Tune.objects.create(
            title="A Flower is a Lovesome Thing",
            composer="Strayhorn",
            key="Db",
            other_keys="D",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1941,
        ),
        Tune.objects.create(
            title="I Remember You",
            composer="Schertzinger",
            key="F",
            other_keys="Bb D C G-",
            song_form="AABA",
            style="standard",
            meter=4,
            year=1941,
        ),
    }

    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    now = timezone.now()
    for i, tune in enumerate(tunes):
        last_played_date = now - timedelta(days=i + 1)
        RepertoireTune.objects.create(tune=tune, player=user, last_played=last_played_date)

    return {"user": user, "tunes": RepertoireTune.objects.all()}
