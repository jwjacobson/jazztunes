import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from tune.models import Tune


@pytest.fixture
def logged_in_user(client):
    """
    Create a user and logs them in, to be used by all tests which require a user.
    """
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)
    return client


@pytest.fixture
def new_tune_form(logged_in_user):
    """
    Create a tune object with the specified attributes, to be used by all tests which require a tune.
    """
    title = "test title"
    composer = "test composer"
    key = "C"
    other_keys = "D Eb F#"
    song_form = "aaba"
    style = "standard"
    meter = 4
    year = 2023

    response = logged_in_user.post(
        reverse("tune:tune_new"),
        {
            "title": title,
            "composer": composer,
            "key": key,
            "other_keys": other_keys,
            "song_form": song_form,
            "style": style,
            "meter": meter,
            "year": year,
        },
    )

    return response


@pytest.mark.django_db
def test_new_tune(logged_in_user, new_tune_form):
    response = logged_in_user.get(reverse("tune:tune_new"))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].instance.pk is None

    assert new_tune_form.status_code == 302
    assert new_tune_form.url == "/"
    tune = Tune.objects.get(title="test title")
    assert tune.title == "test title"
    assert tune.composer == "test composer"
    assert tune.key == "C"
    assert tune.other_keys == "D Eb F#"
    assert tune.song_form == "aaba"
    assert tune.style == "standard"
    assert tune.meter == 4
    assert tune.year == 2023
    assert tune.created_at <= timezone.now()


@pytest.mark.django_db
def test_delete_tune(logged_in_user, new_tune_form):
    tune = Tune.objects.get(title="test title")

    response = logged_in_user.get(reverse("tune:tune_delete", kwargs={"pk": tune.pk}))
    assert response.status_code == 200

    response = logged_in_user.post(reverse("tune:tune_delete", kwargs={"pk": tune.pk}))
    assert response.status_code == 302
    assert response.url == "/"
    with pytest.raises(Tune.DoesNotExist):
        Tune.objects.get(title="test title")


@pytest.mark.django_db
def test_edit_tune(logged_in_user, new_tune_form):
    tune = Tune.objects.get(title="test title")

    response = logged_in_user.get(reverse("tune:tune_edit", kwargs={"pk": tune.pk}))
    assert response.status_code == 200

    edited_title = "edited title"
    edited_composer = "edited composer"
    edited_key = "G"
    edited_other_keys = "Ab A B#"
    edited_song_form = "abac"
    edited_style = "jazz"
    edited_meter = 3
    edited_year = 1939

    response = logged_in_user.post(
        reverse("tune:tune_edit", kwargs={"pk": tune.pk}),
        {
            "title": edited_title,
            "composer": edited_composer,
            "key": edited_key,
            "other_keys": edited_other_keys,
            "song_form": edited_song_form,
            "style": edited_style,
            "meter": edited_meter,
            "year": edited_year,
        },
    )
