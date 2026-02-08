# Tests for the repertoire service layer

import pytest

from jazztunes.models import Tune, RepertoireTune, Play
from jazztunes.repertoire import (
    get_user_repertoire,
    get_repertoire_queryset,
    play_tune,
    add_tune,
    take_tune,
    delete_tune,
    pick_random_tune,
    pick_next_tune,
)


@pytest.mark.django_db
def test_get_user_repertoire(tune_set):
    user = tune_set["user"]

    result = get_user_repertoire(user)

    assert len(result) == 10
    for rep_tune in result:
        assert hasattr(rep_tune, "last_played")
        assert hasattr(rep_tune, "play_count")


@pytest.mark.django_db
def test_get_repertoire_queryset(tune_set):
    user = tune_set["user"]

    result = get_repertoire_queryset(user)

    assert result.count() == 10
    for rep_tune in result:
        assert hasattr(rep_tune, "last_played")
        assert hasattr(rep_tune, "play_count")


@pytest.mark.django_db
def test_play_tune(user_tune_rep):
    rep_tune = user_tune_rep["rep_tune"]
    initial_count = Play.objects.filter(repertoire_tune=rep_tune).count()

    play = play_tune(rep_tune)

    assert Play.objects.filter(repertoire_tune=rep_tune).count() == initial_count + 1
    assert play.repertoire_tune == rep_tune
    assert play.played_at is not None


@pytest.mark.django_db
def test_add_tune(user_tune_rep):
    user = user_tune_rep["user"]
    tune = Tune.objects.create(title="New Tune", composer="Test")

    rep_tune = add_tune(user, tune, knowledge="learning")

    assert rep_tune.tune == tune
    assert rep_tune.player == user
    assert rep_tune.knowledge == "learning"


@pytest.mark.django_db
def test_add_tune_with_tags(user_tune_rep):
    from jazztunes.models import Tag

    user = user_tune_rep["user"]
    tune = Tune.objects.create(title="Tagged Tune", composer="Test")
    tag = Tag.objects.create(name="bop")

    rep_tune = add_tune(user, tune, tags=[tag])

    assert tag in rep_tune.tags.all()


@pytest.mark.django_db
def test_add_tune_defaults(user_tune_rep):
    user = user_tune_rep["user"]
    tune = Tune.objects.create(title="Default Tune")

    rep_tune = add_tune(user, tune)

    assert rep_tune.knowledge == "know"
    assert rep_tune.tags.count() == 0


@pytest.mark.django_db
def test_take_tune(user_tune_rep, admin_tune_rep):
    user = user_tune_rep["user"]
    admin_rep_tune = admin_tune_rep["rep_tune"]
    original_tune_pk = admin_rep_tune.tune.pk

    new_tune, new_rep_tune = take_tune(user, admin_rep_tune)

    assert new_tune.pk != original_tune_pk
    assert new_tune.title == admin_rep_tune.tune.title
    assert new_tune.created_by == user
    assert new_rep_tune.player == user
    assert new_rep_tune.tune == new_tune


@pytest.mark.django_db
def test_delete_tune(user_tune_rep):
    rep_tune = user_tune_rep["rep_tune"]
    rep_tune_pk = rep_tune.pk

    delete_tune(rep_tune)

    assert not RepertoireTune.objects.filter(pk=rep_tune_pk).exists()


@pytest.mark.django_db
def test_pick_random_tune(tune_set):
    tunes = list(tune_set["tunes"])

    selected, remaining = pick_random_tune(tunes)

    assert selected in tunes
    assert selected.id not in remaining
    assert len(remaining) == len(tunes) - 1


@pytest.mark.django_db
def test_pick_random_tune_empty():
    selected, remaining = pick_random_tune([])

    assert selected is None
    assert remaining == []


@pytest.mark.django_db
def test_pick_next_tune(tune_set):
    tune_ids = [t.id for t in tune_set["tunes"]]

    selected, remaining = pick_next_tune(tune_ids)

    assert selected is not None
    assert selected.id not in remaining
    assert len(remaining) == len(tune_ids) - 1


@pytest.mark.django_db
def test_pick_next_tune_empty():
    selected, remaining = pick_next_tune([])

    assert selected is None
    assert remaining == []
