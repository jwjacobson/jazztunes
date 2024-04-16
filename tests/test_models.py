import pytest  # noqa

from tune.models import Tune
from django.contrib.auth import get_user_model


@pytest.fixture()
def tune_object():
    tune = Tune(
        title="test title",
        composer="test composer",
        key="C",
        other_keys="D Eb F#",
        song_form="aaba",
        style="standard",
        meter=4,
        year=2023,
    )

    return tune


@pytest.fixture()
def basic_user(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    return user


def test_tune_field_access(tune_object):
    tune = tune_object
    assert tune.title == "test title"
    assert tune.composer == "test composer"
    assert tune.key == "C"
    assert tune.other_keys == "D Eb F#"
    assert tune.song_form == "aaba"
    assert tune.style == "standard"
    assert tune.meter == 4
    assert tune.year == 2023


def test_tune_defaults():
    tune = Tune(title="test tune")

    assert tune.title == "test tune"
    assert tune.composer == ""
    assert tune.key == ""
    assert tune.other_keys == ""
    assert tune.song_form == ""
    assert tune.style == "standard"
    assert tune.meter == 4
    assert tune.year is None
