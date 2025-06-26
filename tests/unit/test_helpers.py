import pytest

from tune.forms import PlaySearchForm
from tune.helpers import suggest_key


@pytest.mark.django_db
def test_suggest_key(user_tune_rep):
    tune = user_tune_rep["rep_tune"]

    suggested_key = suggest_key(
        tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.SUBSTITUTIONS
    )

    assert suggested_key != tune.tune.key
