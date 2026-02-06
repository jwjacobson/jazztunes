# Tests for the models, as far as possible removed from app context

import pytest

from django.contrib.auth import get_user_model
from django.utils import timezone

from jazztunes.models import Tune, RepertoireTune


@pytest.fixture()
def basic_tune():
    """
    Create a Tune.
    """
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
    """
    Create a user and log them in.
    """
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    return user


@pytest.fixture()
def basic_reptune(basic_tune, basic_user):
    """
    Create a RepertoireTune associated with the tune and user above.
    """
    tune = basic_tune
    user = basic_user
    rep_tune = RepertoireTune(
        tune=tune,
        player=user,
        knowledge="learning",
        last_played=timezone.now(),
    )

    return rep_tune, tune, user


def test_tune_field_access(basic_tune):
    tune = basic_tune

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
    assert tune.style == ""
    assert tune.meter == 4
    assert tune.year is None


@pytest.mark.django_db
def test_reptune_field_access(basic_reptune):
    rep_tune, tune, user = basic_reptune

    assert rep_tune.tune == tune
    assert rep_tune.player == user
    assert rep_tune.knowledge == "learning"
    assert rep_tune.last_played <= timezone.now()


@pytest.mark.django_db
def test_reptune_tune_field_access(basic_reptune):
    rep_tune, tune, user = basic_reptune

    assert rep_tune.tune.title == "test title"
    assert rep_tune.tune.composer == "test composer"
    assert rep_tune.tune.key == "C"
    assert rep_tune.tune.other_keys == "D Eb F#"
    assert rep_tune.tune.song_form == "aaba"
    assert rep_tune.tune.style == "standard"
    assert rep_tune.tune.meter == 4
    assert rep_tune.tune.year == 2023


@pytest.mark.django_db
def test_reptune_defaults(basic_tune, basic_user):
    rep_tune = RepertoireTune(tune=basic_tune, player=basic_user)

    assert rep_tune.knowledge == "know"
    assert rep_tune.last_played is None
