import pytest  # noqa

from tune.models import Tune


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
