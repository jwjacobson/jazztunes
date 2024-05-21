# Tests for the helper functions in views.py

import pytest
from datetime import timedelta

from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest

from tune.views import query_tunes, return_search_results, exclude_term


@pytest.fixture
def request_fixture():
    """
    Create an HTTP request.
    """
    request = HttpRequest()
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@pytest.fixture
def search_form_fixture():
    """
    Create a search form.
    """
    from tune.forms import SearchForm

    form = SearchForm()
    return form


# Single term tests
@pytest.mark.django_db
def test_query_tunes_kern(tune_set):
    search_terms = ["kern"]
    result = query_tunes(tune_set, search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"All the Things You Are", "Dearly Beloved", "Long Ago and Far Away"}

    assert result.count() == 3
    assert all("Kern" in tune.tune.composer for tune in result)

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_no_term(tune_set):
    search_terms = [""]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 10


@pytest.mark.django_db
def test_query_tunes_no_results(tune_set):
    search_terms = ["xx"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 0


@pytest.mark.django_db
def test_query_tunes_nickname(tune_set):
    search_terms = ["bird"]
    result = query_tunes(tune_set, search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"Confirmation", "Dewey Square"}

    assert result.count() == 2

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_common_fragment(tune_set):
    search_terms = ["love"]
    result = query_tunes(tune_set, search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"Dearly Beloved", "A Flower is a Lovesome Thing"}

    assert result.count() == 2
    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_decade(tune_set):
    search_terms = ["194"]
    result = query_tunes(tune_set, search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {
        "Dearly Beloved",
        "A Flower is a Lovesome Thing",
        "Confirmation",
        "Dewey Square",
        "I Remember You",
        "Long Ago and Far Away",
    }

    assert result.count() == 6
    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_form(tune_set):
    search_terms = ["abac"]
    result = query_tunes(tune_set, search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {
        "Dearly Beloved",
        "Someday My Prince Will Come",
        "Long Ago and Far Away",
    }

    assert result.count() == 3
    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_exclude(tune_set):
    search_terms = ["-kern"]
    result = query_tunes(tune_set, search_terms)
    result_composers = {tune.tune.composer for tune in result}

    assert result.count() == 7
    for composer in result_composers:
        assert "kern" not in composer


# Two term tests
@pytest.mark.django_db
def test_query_tunes_kern2(tune_set):
    search_terms = ["kern", "love"]
    result = query_tunes(tune_set, search_terms)
    expected_title = "Dearly Beloved"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_monk(tune_set):
    search_terms = ["monk", "hudson"]
    result = query_tunes(tune_set, search_terms)
    expected_title = "Coming on the Hudson"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_nickname2(tune_set):
    search_terms = ["bird", "dewey"]
    result = query_tunes(tune_set, search_terms)
    expected_title = "Dewey Square"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_exclude2_mixed(tune_set):
    search_terms = ["-kern", "love"]
    result = query_tunes(tune_set, search_terms)
    expected_title = "A Flower is a Lovesome Thing"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_exclude2(tune_set):
    search_terms = ["-kern", "-love"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 6


# Timespan tests
@pytest.mark.django_db
def test_query_tunes_no_timespan(tune_set):
    search_terms = [""]
    timespan = None
    result = query_tunes(tune_set, search_terms, timespan)

    assert result.count() == 10


@pytest.mark.django_db
def test_query_tunes_timespan_day(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=1)
    result = query_tunes(tune_set, search_terms, timespan)

    assert result.count() == 9


@pytest.mark.django_db
def test_query_tunes_timespan_week(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=7)
    result = query_tunes(tune_set, search_terms, timespan)

    assert result.count() == 3


@pytest.mark.django_db
def test_query_tunes_timespan_month(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=30)
    result = query_tunes(tune_set, search_terms, timespan)

    assert result.count() == 0


def test_return_search_results_too_many(request_fixture, tune_set, search_form_fixture):
    search_terms = ["a", "b", "c", "d", "e"]
    _ = return_search_results(request_fixture, search_terms, tune_set, search_form_fixture)

    assert any("Your query is too long" in msg.message for msg in request_fixture._messages)


def test_exclude_term(tune_set):
    excluded_term = "-kern"
    result = exclude_term(tune_set, excluded_term)
    result_composers = {tune.tune.composer for tune in result}

    assert result.count() == 7
    for composer in result_composers:
        assert "kern" not in composer
