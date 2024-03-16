import pytest
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model

from tune.models import Tune, RepertoireTune


@pytest.fixture
def user_tune_rep(client):
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

    rep_tune = RepertoireTune.objects.create(
        tune=tune,
        player=user,
        knowledge="know",
        last_played="2024-02-01",
    )

    return {"tune": tune, "rep_tune": rep_tune, "user": user}


@pytest.mark.django_db
def test_tune_new_success(user_tune_rep, client):
    url = reverse("tune:tune_new")
    post_data = {
        "title": "New Tune",
        "composer": "Al Dimeola",
        "key": "G",
        "other_keys": "A B",
        "song_form": "ABAC",
        "style": "jazz",
        "meter": 3,
        "year": 2024,
        "knowledge": "learning",
        "last_played": "2024-03-01",
    }

    response = client.post(url, post_data)

    assert response.status_code == 302
    assert response.url == reverse("tune:tune_list")

    assert Tune.objects.filter(title="New Tune").exists()
    assert RepertoireTune.objects.filter(knowledge="learning").exists()


@pytest.mark.django_db
def test_tune_edit_success(user_tune_rep, client):
    tune = user_tune_rep["tune"]
    user = user_tune_rep["user"]
    rep_tune = user_tune_rep["rep_tune"]

    updated_data = {
        "title": "Updated Title",
        "composer": "Updated Composer",
        "key": "C-",
        "other_keys": "Db",
        "song_form": "irregular",
        "meter": 3,
        "style": "jazz",
        "year": 1939,
        "knowledge": "learning",
        "last_played": "2024-03-01",
    }

    url = reverse("tune:tune_edit", kwargs={"pk": tune.pk})
    response = client.post(url, updated_data)

    assert response.status_code == 302
    assert response.url == reverse("tune:tune_list")

    tune.refresh_from_db()
    rep_tune = RepertoireTune.objects.get(tune=tune, player=user)

    assert tune.title == "Updated Title"
    assert tune.composer == "Updated Composer"
    assert tune.key == "C-"
    assert tune.other_keys == "Db"
    assert tune.song_form == "irregular"
    assert tune.meter == 3
    assert tune.style == "jazz"
    assert tune.year == 1939
    assert rep_tune.knowledge == "learning"
    assert rep_tune.last_played == date(2024, 3, 1)


@pytest.mark.django_db
def test_tune_delete_success(user_tune_rep, client):
    rep_tune = user_tune_rep["rep_tune"]

    session = client.session
    session["tune_count"] = 1
    session.save()

    url = reverse("tune:tune_delete", kwargs={"pk": rep_tune.pk})
    response = client.post(url)

    client.session.save()
    session = client.session

    assert response.status_code == 200
    assert session["tune_count"] == 0
