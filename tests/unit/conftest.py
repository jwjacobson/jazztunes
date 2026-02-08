import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from jazztunes.models import Tune, RepertoireTune, Play


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
    )

    Play.objects.create(repertoire_tune=rep_tune)

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
    )

    return {"tune": tune, "rep_tune": rep_tune, "admin": admin}


@pytest.fixture()
def tune_set(db, client, create_tune_set_for_user):
    """Unit test tune set with its own user"""
    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    return create_tune_set_for_user(user)
