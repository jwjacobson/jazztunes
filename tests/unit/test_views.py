# Tests for the views in views.py

import pytest

from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages

from jazztunes.models import Tune, RepertoireTune
from jazztunes.forms import SearchForm, PlaySearchForm


@pytest.mark.django_db
def test_tune_new_success(user_tune_rep, client):
    url = reverse("jazztunes:tune_new")
    post_data = {
        "title": "New Tune",
        "composer": "Jacobson",
        "key": "G",
        "other_keys": "A B",
        "song_form": "ABAC",
        "style": "jazz",
        "meter": 3,
        "year": 2024,
        "knowledge": "learning",
        "last_played": timezone.now(),
    }

    response = client.post(url, post_data)

    assert response.status_code == 302
    assert response.url == reverse("jazztunes:home")
    assert Tune.objects.filter(title="New Tune").exists()
    assert RepertoireTune.objects.filter(knowledge="learning").exists()

    tune = Tune.objects.get(title="New Tune")
    rep_tune = RepertoireTune.objects.get(knowledge="learning")
    assert rep_tune.tune == tune


@pytest.mark.django_db
def test_tune_new_get(user_tune_rep, client):
    url = reverse("jazztunes:tune_new")

    response = client.get(url)

    assert response.status_code == 200
    assert "jazztunes/form.html" in [t.name for t in response.templates]
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
        "last_played": timezone.now(),
    }
    url = reverse("jazztunes:tune_edit", kwargs={"pk": tune.pk})

    response = client.post(url, updated_data)

    assert response.status_code == 302
    assert response.url == reverse("jazztunes:home")

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
    assert rep_tune.last_played <= timezone.now()


@pytest.mark.django_db
def test_tune_delete_success(user_tune_rep, client):
    rep_tune = user_tune_rep["rep_tune"]
    session = client.session
    session["tune_count"] = 1
    session.save()
    url = reverse("jazztunes:tune_delete", kwargs={"pk": rep_tune.pk})

    response = client.post(url)
    client.session.save()
    session = client.session

    assert response.status_code == 200
    assert session["tune_count"] == 0


def test_home_unauthenticated(client):
    response = client.get(reverse("jazztunes:home"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_home_authenticated(user_tune_rep, client):
    response = client.get(reverse("jazztunes:home"))

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1
    assert isinstance(response.context["search_form"], SearchForm)


@pytest.mark.django_db
def test_home_invalid_timespan(user_tune_rep, client):
    response = client.post(reverse("jazztunes:home"), {"timespan": "year"})

    assert response.status_code == 200
    assert "search_form" in response.context
    form = response.context["search_form"]

    assert form.is_valid() is False
    assert "timespan" in form.errors


@pytest.mark.django_db
def test_home_valid_form(user_tune_rep, client):
    response = client.post(reverse("jazztunes:home"), {"search_terms": [""]})

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1


def test_tune_browse_unauthenticated(client):
    response = client.get(reverse("jazztunes:tune_browse"))

    assert response.status_code == 302


@pytest.mark.django_db
def test_tune_browse_authenticated(admin_tune_rep, client):
    response = client.get(reverse("jazztunes:tune_browse"))

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1
    assert isinstance(response.context["search_form"], SearchForm)


@pytest.mark.django_db
def test_tune_browse_invalid_timespan(admin_tune_rep, client):
    response = client.post(reverse("jazztunes:tune_browse"), {"timespan": "year"})

    assert response.status_code == 200
    assert "search_form" in response.context
    form = response.context["search_form"]

    assert form.is_valid() is False
    assert "timespan" in form.errors


@pytest.mark.django_db
def test_tune_browse_valid_form(admin_tune_rep, client):
    response = client.post(reverse("jazztunes:tune_browse"), {"search_terms": [""]})

    assert response.status_code == 200
    assert len(response.context["tunes"]) == 1


@pytest.mark.django_db
def test_recount(user_tune_rep, client):
    user = user_tune_rep["user"]
    session = client.session
    session["tune_count"] = 5
    session.save()

    response = client.get(reverse("jazztunes:recount"))

    assert response.status_code == 200
    assert "tune_count" in response.context
    assert response.context["tune_count"] == 5
    assert "jazztunes/partials/_count.html" in [t.name for t in response.templates]
    assert response.context["user"] == user


@pytest.mark.django_db
def test_tune_take_success(client, user_tune_rep, admin_tune_rep):
    response = client.post(reverse("jazztunes:tune_take", args=[admin_tune_rep["tune"].pk]))

    assert response.status_code == 200
    assert RepertoireTune.objects.filter(
        player=user_tune_rep["user"], tune__title=admin_tune_rep["tune"].title
    ).exists()


@pytest.mark.django_db
def test_tune_take_nonpublic(client, user_tune_rep):
    response = client.post(reverse("jazztunes:tune_take", args=[user_tune_rep["tune"].pk]))

    assert response.status_code == 200

    messages = [msg.message for msg in get_messages(response.wsgi_request)]
    assert "You can only take public tunes into your repertoire." in messages


@pytest.mark.django_db
def test_set_rep_fields_success(client, user_tune_rep):
    tune_pk = user_tune_rep["rep_tune"].pk
    knowledge = "learning"
    last_played = timezone.now()

    response = client.post(
        reverse("jazztunes:set_rep_fields", args=[tune_pk]),
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
        reverse("jazztunes:set_rep_fields", args=[tune_pk]), {"knowledge": invalid_knowledge}
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
        reverse("jazztunes:set_rep_fields", args=[tune_pk]),
        {"last_played": invalid_last_played},
    )

    assert response.status_code == 200

    user_tune_rep["rep_tune"].refresh_from_db()
    assert user_tune_rep["rep_tune"].last_played == original_last_played


@pytest.mark.django_db
def test_get_random_tune_single_tune(user_tune_rep, client):
    tune = user_tune_rep["tune"]
    response = client.post(reverse("jazztunes:get_random_tune"), {"search_terms": [""]})

    assert response.status_code == 200
    assert "selected_tune" in response.context
    assert response.context["selected_tune"].id == tune.id


@pytest.mark.django_db
def test_get_random_tune_multiple(tune_set, client):
    tunes = tune_set["tunes"]
    response = client.post(reverse("jazztunes:get_random_tune"), {"search_terms": [""]})

    assert response.status_code == 200
    assert response.context["selected_tune"] in tunes


@pytest.mark.django_db
def test_get_random_tune_suggest_key(user_tune_rep, client):
    tune = user_tune_rep["tune"]
    response = client.post(
        reverse("jazztunes:get_random_tune"), {"search_terms": [""], "suggest_key": True}
    )

    assert response.status_code == 200
    assert response.context["suggested_key"] in PlaySearchForm.NORMAL_KEYS
    assert response.context["suggested_key"] != tune.key


@pytest.mark.django_db
def test_get_random_tune_no_tunes(tune_set, client):
    _ = tune_set["tunes"]
    response = client.post(reverse("jazztunes:get_random_tune"), {"search_term": ["xx"]})

    assert response.status_code == 200
    assert response.context["selected_tune"] is None


@pytest.mark.django_db
def test_change_tune(tune_set, client):
    tunes = tune_set["tunes"]
    session = client.session
    session["rep_tunes"] = [tune.id for tune in tunes]
    session.save()

    response = client.get(reverse("jazztunes:change_tune"))
    assert response.status_code == 200
    assert "selected_tune" in response.context

    selected_tune = response.context["selected_tune"]

    assert selected_tune.id not in client.session["rep_tunes"]
    assert len(client.session["rep_tunes"]) == len(tunes) - 1


@pytest.mark.django_db
def test_change_tune_suggest_key_enabled(tune_set, client):
    tunes = tune_set["tunes"]
    session = client.session
    session["rep_tunes"] = [tune.id for tune in tunes]
    session["suggest_key_enabled"] = True
    session.save()

    response = client.get(reverse("jazztunes:change_tune"))
    assert response.status_code == 200
    assert "selected_tune" in response.context
    if response.context["selected_tune"].tune.key is not None:
        assert "suggested_key" in response.context


@pytest.mark.django_db
def test_change_tune_no_tunes(user_tune_rep, client):
    _ = user_tune_rep["user"]
    session = client.session
    session["rep_tunes"] = []
    session.save()

    response = client.get(reverse("jazztunes:change_tune"))

    assert response.status_code == 200
    assert "selected_tune" in response.context
    assert response.context["selected_tune"] is None


@pytest.mark.django_db
def test_play_home(user_tune_rep, client):
    tune = user_tune_rep["rep_tune"]
    initial_last_played = tune.last_played
    initial_play_count = tune.play_count

    response = client.get(reverse("jazztunes:play_home", kwargs={"pk": tune.pk}))
    tune.refresh_from_db()

    assert response.status_code == 200
    assert tune.last_played > initial_last_played
    assert tune.play_count == initial_play_count + 1
    assert "last_played" in response.context
    assert "selected_tune" in response.context
    assert response.context["selected_tune"].last_played == tune.last_played


@pytest.mark.django_db
def test_play_play(user_tune_rep, client):
    tune = user_tune_rep["rep_tune"]
    initial_last_played = tune.last_played
    initial_play_count = tune.play_count

    response = client.get(reverse("jazztunes:play_play", kwargs={"pk": tune.pk}))
    tune.refresh_from_db()

    assert response.status_code == 200
    assert tune.last_played > initial_last_played
    assert tune.play_count == initial_play_count + 1
    assert "last_played" in response.context
    assert "selected_tune" in response.context
    assert response.context["selected_tune"].last_played == tune.last_played


@pytest.mark.django_db
def test_play_invalid_pk(user_tune_rep, client):
    tune = user_tune_rep["rep_tune"]
    wrong_pk = tune.pk * 7000

    response = client.get(reverse("jazztunes:play_home", kwargs={"pk": wrong_pk}))

    assert response.status_code == 404
