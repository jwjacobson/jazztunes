# Tests for the views in views.py

import pytest
from datetime import date

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.conf import settings

from tune.models import Tune, RepertoireTune
from tune.forms import SearchForm


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
        last_played=date(2024, 2, 1),
    )

    return {"tune": tune, "rep_tune": rep_tune, "user": user}


@pytest.fixture
def admin_tune_rep(client):
    """
    Create an admin user, tune, and associated repertoire tune for use by tune_browse
    """
    user_model = get_user_model()
    admin = user_model.objects.create_user(username="admin", password="secret")
    client.force_login(admin)

    settings.ADMIN_USER_ID = admin.id

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
        player=admin,
        knowledge="know",
        last_played=date(2024, 2, 1),
    )

    return {"tune": tune, "rep_tune": rep_tune, "admin": admin}


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
        "last_played": date(2024, 3, 1),
    }

    response = client.post(url, post_data)

    assert response.status_code == 302
    assert response.url == reverse("tune:tune_list")

    assert Tune.objects.filter(title="New Tune").exists()
    assert RepertoireTune.objects.filter(knowledge="learning").exists()


@pytest.mark.django_db
def test_tune_new_get(user_tune_rep, client):
    url = reverse("tune:tune_new")
    response = client.get(url)

    assert response.status_code == 200
    assert "tune/form.html" in [t.name for t in response.templates]
    assert "tune_form" in response.context
    assert "rep_form" in response.context
    assert not response.context["tune_form"].is_bound
    assert not response.context["rep_form"].is_bound


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
        "last_played": date(2024, 3, 1),
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


def test_tune_list_unauthenticated(client):
    response = client.get(reverse("tune:tune_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_tune_list_authenticated(user_tune_rep, client):
    response = client.get(reverse("tune:tune_list"))

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1
    assert isinstance(response.context["search_form"], SearchForm)


@pytest.mark.django_db
def test_tune_list_invalid_timespan(user_tune_rep, client):
    response = client.post(reverse("tune:tune_list"), {"timespan": "year"})

    assert response.status_code == 200
    assert "search_form" in response.context
    form = response.context["search_form"]

    assert form.is_valid() is False
    assert "timespan" in form.errors


@pytest.mark.django_db
def test_tune_list_valid_form(user_tune_rep, client):
    response = client.post(reverse("tune:tune_list"), {"search_terms": [""]})
    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1


def test_tune_browse_unauthenticated(client):
    response = client.get(reverse("tune:tune_browse"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_tune_browse_authenticated(admin_tune_rep, client):
    response = client.get(reverse("tune:tune_browse"))

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1
    assert isinstance(response.context["search_form"], SearchForm)


@pytest.mark.django_db
def test_tune_browse_invalid_timespan(admin_tune_rep, client):
    response = client.post(reverse("tune:tune_browse"), {"timespan": "year"})

    assert response.status_code == 200
    assert "search_form" in response.context
    form = response.context["search_form"]

    assert form.is_valid() is False
    assert "timespan" in form.errors


@pytest.mark.django_db
def test_tune_browse_valid_form(admin_tune_rep, client):
    response = client.post(reverse("tune:tune_browse"), {"search_terms": [""]})
    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1


@pytest.mark.django_db
def test_recount(user_tune_rep, client):
    user = user_tune_rep["user"]
    session = client.session
    session["tune_count"] = 5
    session.save()
    response = client.get(reverse("tune:recount"))

    assert response.status_code == 200
    assert "tune_count" in response.context
    assert response.context["tune_count"] == 5
    assert "tune/_count.html" in [t.name for t in response.templates]
    assert response.context["user"] == user


@pytest.mark.django_db
def test_tune_take_success(client, user_tune_rep, admin_tune_rep):
    response = client.post(reverse("tune:tune_take", args=[admin_tune_rep["tune"].pk]))

    assert response.status_code == 200
    assert RepertoireTune.objects.filter(
        player=user_tune_rep["user"], tune__title=admin_tune_rep["tune"].title
    ).exists()


@pytest.mark.django_db
def test_tune_take_nonpublic(client, user_tune_rep):
    response = client.post(reverse("tune:tune_take", args=[user_tune_rep["tune"].pk]))

    assert response.status_code == 200

    messages = [msg.message for msg in get_messages(response.wsgi_request)]
    assert "You can only take public tunes into your repertoire." in messages


@pytest.mark.django_db
def test_set_rep_fields_success(client, user_tune_rep):
    tune_pk = user_tune_rep["rep_tune"].pk
    knowledge = "learning"
    last_played = date(2024, 3, 1)

    response = client.post(
        reverse("tune:set_rep_fields", args=[tune_pk]),
        {"knowledge": knowledge, "last_played": last_played},
    )

    assert response.status_code == 200

    user_tune_rep["rep_tune"].refresh_from_db()
    assert user_tune_rep["rep_tune"].knowledge == knowledge
    assert user_tune_rep["rep_tune"].last_played == last_played


@pytest.mark.django_db
def test_set_rep_fields_invalid_knowledge(client, user_tune_rep):
    tune_pk = user_tune_rep["rep_tune"].pk
    original_knowledge = user_tune_rep["rep_tune"].knowledge
    invalid_knowledge = "whatever"

    response = client.post(
        reverse("tune:set_rep_fields", args=[tune_pk]), {"knowledge": invalid_knowledge}
    )

    assert response.status_code == 200

    user_tune_rep["rep_tune"].refresh_from_db()
    assert user_tune_rep["rep_tune"].knowledge == original_knowledge


@pytest.mark.django_db
def test_set_rep_fields_invalid_last_played(client, user_tune_rep):
    tune_pk = user_tune_rep["rep_tune"].pk
    original_last_played = user_tune_rep["rep_tune"].last_played
    invalid_last_played = "tomorrow"

    response = client.post(
        reverse("tune:set_rep_fields", args=[tune_pk]), {"last_played": invalid_last_played}
    )

    assert response.status_code == 200

    user_tune_rep["rep_tune"].refresh_from_db()
    assert user_tune_rep["rep_tune"].last_played == original_last_played


@pytest.mark.django_db
def test_get_random_tunes(tune_set):
    user = tune_set["user"]
    tunes = tune_set["tunes"]

    for tune in tunes:
        assert tune.player == user
