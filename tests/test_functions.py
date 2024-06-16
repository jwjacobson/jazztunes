# Tests for the helper functions in views.py

import pytest
from datetime import timedelta

from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest

from tune.views import query_tunes, return_search_results, exclude_term, search_field


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
    result = query_tunes(tune_set["tunes"], search_terms)
    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"All the Things You Are", "Dearly Beloved", "Long Ago and Far Away"}

    assert result.count() == 3
    assert all("Kern" in tune.tune.composer for tune in result)

    for title in expected_titles:
        assert title in result_titles

    for title in result_titles:
        assert title in expected_titles


@pytest.mark.django_db
def test_query_tunes_no_term(tune_set):
    search_terms = [""]
    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 10


@pytest.mark.django_db
def test_query_tunes_no_results(tune_set):
    search_terms = ["xx"]
    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 0


@pytest.mark.django_db
def test_query_tunes_nickname(tune_set):
    search_terms = ["bird"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_titles = {"Confirmation", "Dewey Square"}

    assert result.count() == 2

    for tune in result:
        assert tune.tune.title in expected_titles


@pytest.mark.django_db
def test_query_tunes_common_fragment(tune_set):
    search_terms = ["love"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_titles = {"Dearly Beloved", "A Flower is a Lovesome Thing"}

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles


@pytest.mark.django_db
def test_query_tunes_decade(tune_set):
    search_terms = ["194"]
    result = query_tunes(tune_set["tunes"], search_terms)
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
    result = query_tunes(tune_set["tunes"], search_terms)
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
    result = query_tunes(tune_set["tunes"], search_terms)
    result_composers = {tune.tune.composer for tune in result}

    assert result.count() == 7
    for composer in result_composers:
        assert "kern" not in composer


# Two term tests
@pytest.mark.django_db
def test_query_tunes_kern2(tune_set):
    search_terms = ["kern", "love"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_title = "Dearly Beloved"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_monk(tune_set):
    search_terms = ["monk", "hudson"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_title = "Coming on the Hudson"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_nickname2(tune_set):
    search_terms = ["bird", "dewey"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_title = "Dewey Square"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_exclude2_mixed(tune_set):
    search_terms = ["-kern", "love"]
    result = query_tunes(tune_set["tunes"], search_terms)
    expected_title = "A Flower is a Lovesome Thing"
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_exclude2(tune_set):
    search_terms = ["-kern", "-love"]
    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 6


# Timespan tests
@pytest.mark.django_db
def test_query_tunes_no_timespan(tune_set):
    search_terms = [""]
    timespan = None
    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 10


@pytest.mark.django_db
def test_query_tunes_timespan_day(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=1)
    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 9


@pytest.mark.django_db
def test_query_tunes_timespan_week(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=7)
    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 3


@pytest.mark.django_db
def test_query_tunes_timespan_month(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=30)
    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 0


def test_return_search_results_too_many(request_fixture, tune_set, search_form_fixture):
    search_terms = ["a", "b", "c", "d", "e"]
    _ = return_search_results(request_fixture, search_terms, tune_set["tunes"], search_form_fixture)

    assert any("Your query is too long" in msg.message for msg in request_fixture._messages)


def test_exclude_term(tune_set):
    excluded_term = "-kern"
    result = exclude_term(tune_set["tunes"], excluded_term)
    result_composers = {tune.tune.composer for tune in result}

    assert result.count() == 7
    for composer in result_composers:
        assert "kern" not in composer


def test_search_field_title(tune_set):
    search_term = "title:you"
    result = search_field(tune_set["tunes"], search_term)
    expected_titles = {"All the Things You Are", "I Remember You"}

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles


def test_search_field_composer(tune_set):
    search_term = "composer:parker"
    result = search_field(tune_set["tunes"], search_term)
    expected_composer = "Parker"
    expected_titles = {"Confirmation", "Dewey Square"}

    assert result.count() == 2
    for tune in result:
        assert tune.tune.composer == expected_composer
        assert tune.tune.title in expected_titles


def test_search_field_key(tune_set):
    search_term = "key:f"
    result = search_field(tune_set["tunes"], search_term)
    expected_key = "F"
    expected_titles = {"Confirmation", "Long Ago and Far Away", "I Remember You"}

    assert result.count() == 3
    for tune in result:
        assert tune.tune.key == expected_key
        assert tune.tune.title in expected_titles


def test_search_field_keys(tune_set):
    search_term = "keys:eb"
    result = search_field(tune_set["tunes"], search_term)
    expected_key = "Eb"
    expected_titles = {"Dewey Square", "All the Things You Are", "Someday My Prince Will Come"}

    assert result.count() == 3
    for tune in result:
        assert tune.tune.key == expected_key or expected_key in tune.tune.other_keys
        assert tune.tune.title in expected_titles


def test_search_field_form(tune_set):
    search_term = "form:abac"
    result = search_field(tune_set["tunes"], search_term)
    expected_form = "ABAC"
    expected_titles = {"Dearly Beloved", "Long Ago and Far Away", "Someday My Prince Will Come"}

    assert result.count() == 3
    for tune in result:
        assert tune.tune.song_form == expected_form
        assert tune.tune.title in expected_titles


def test_search_field_style(tune_set):
    search_term = "style:jazz"
    result = search_field(tune_set["tunes"], search_term)
    expected_style = "jazz"
    expected_titles = {
        "Confirmation",
        "Dewey Square",
        "Coming on the Hudson",
        "Kary's Trance",
        "A Flower is a Lovesome Thing",
    }

    assert result.count() == 5
    for tune in result:
        assert tune.tune.style == expected_style
        assert tune.tune.title in expected_titles


def test_search_field_meter(tune_set):
    search_term = "meter:3"
    result = search_field(tune_set["tunes"], search_term)
    expected_meter = 3
    expected_titles = {"Someday My Prince Will Come"}

    assert result.count() == 1
    for tune in result:
        assert tune.tune.meter == expected_meter
        assert tune.tune.title in expected_titles


def test_search_field_year(tune_set):
    search_term = "year:1941"
    result = search_field(tune_set["tunes"], search_term)
    expected_year = 1941
    expected_titles = {"I Remember You", "A Flower is a Lovesome Thing"}

    assert result.count() == 2
    for tune in result:
        assert tune.tune.year == expected_year
        assert tune.tune.title in expected_titles


def test_search_field_year_partial(tune_set):
    search_term = "year:195"
    result = search_field(tune_set["tunes"], search_term)
    expected_years = {1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959}
    expected_titles = {"Kary's Trance", "Coming on the Hudson"}

    assert result.count() == 2
    for tune in result:
        assert tune.tune.year in expected_years
        assert tune.tune.title in expected_titles
