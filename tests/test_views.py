import pytest

# from django.urls import reverse
from django.contrib.auth import get_user_model
# from django.utils import timezone

from tune.models import Tune, RepertoireTune


@pytest.fixture
def user_tune_repertoire(client):
    """
    Create a user, tune, and associated repertoire tune for use by views that require a single tune
    """
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    tune = Tune.objects.create(
        title="test title",
        composer="test composer",
        key="C",
        other_keys="D Eb F#",
        song_form="aaba",
        style="standard",
        meter=4,
        year=2023,
    )

    repertoire_tune = RepertoireTune.objects.create(
        tune=tune,
        player=user,
        knowledge="know",
        last_played="2024-02-01",
    )

    return {"tune": tune, "repertoire_tune": repertoire_tune, "user": user}
