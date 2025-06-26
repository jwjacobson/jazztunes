import pytest

from tune.forms import PlaySearchForm
from tune.helpers import suggest_key


@pytest.mark.django_db
def test_suggest_key_normal(user_tune_rep):
    tune = user_tune_rep["rep_tune"]

    suggested_key = suggest_key(
        tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.ENHARMONICS
    )

    assert suggested_key != tune.tune.key


@pytest.mark.django_db
def test_suggest_key_enharmonic(user_tune_rep):
    tune = user_tune_rep["rep_tune"]
    tune.tune.key = "C#"

    suggested_key = suggest_key(
        tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.ENHARMONICS
    )

    assert suggested_key != PlaySearchForm.ENHARMONICS[tune.tune.key]


@pytest.mark.django_db
def test_suggest_key_minor(user_tune_rep):
    tune = user_tune_rep["rep_tune"]
    tune.tune.key = "C-"

    suggested_key = suggest_key(
        tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.ENHARMONICS
    )

    assert suggested_key != tune.tune.key
    assert suggested_key.endswith("-")
