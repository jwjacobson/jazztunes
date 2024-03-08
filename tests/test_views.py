import pytest

from django.urls import reverse
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


@pytest.mark.django_db
def test_tune_new_success(user_tune_repertoire, client):
    url = reverse("tune:tune_new")
    post_data = {
        "title": "New Tune",
        "composer": "Al Dimeola",
        "key": "G",
        "other_keys": "A B",
        "song_form": "ABAC",
        "style": "jazz",
        "meter": "3",
        "year": 2024,
        "knowledge": "learning",
        "last_played": "2024-03-01",
    }

    response = client.post(url, post_data)

    # Check that the response redirects to the tune list page
    assert response.status_code == 302
    assert response.url == reverse("tune:tune_list")

    # Verify that the new tune and repertoire tune have been created
    assert Tune.objects.filter(title="New Tune").exists()
    assert RepertoireTune.objects.filter(knowledge="learning").exists()
