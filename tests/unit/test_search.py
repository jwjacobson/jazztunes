# Tests for the helper functions in views.py

import pytest
from datetime import timedelta

from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest

from tune.search import query_tunes, return_search_results, search_field


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
def test_query_tunes_one_term(tune_set):
    search_terms = ["kern"]
    expected_titles = {
        "All the Things You Are",
        "Dearly Beloved",
        "Long Ago and Far Away",
    }
    expected_composer = "Kern"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.composer == expected_composer
        assert tune.tune.title in expected_titles


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
def test_query_tunes_one_term_nickname(tune_set):
    search_terms = ["bird"]
    expected_titles = {"Confirmation", "Dewey Square"}
    expected_composer = "Parker"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.composer == expected_composer


@pytest.mark.django_db
def test_query_tunes_one_term_fragment(tune_set):
    search_terms = ["love"]
    expected_titles = {"Dearly Beloved", "A Flower is a Lovesome Thing"}

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles


@pytest.mark.django_db
def test_query_tunes_one_term_decade(tune_set):
    search_terms = ["194"]
    expected_titles = {
        "Dearly Beloved",
        "A Flower is a Lovesome Thing",
        "Confirmation",
        "Dewey Square",
        "I Remember You",
        "Long Ago and Far Away",
    }

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 6
    for tune in result:
        assert tune.tune.title in expected_titles


@pytest.mark.django_db
def test_query_tunes_one_tune_form(tune_set):
    search_terms = ["abac"]
    expected_titles = {
        "Dearly Beloved",
        "Someday My Prince Will Come",
        "Long Ago and Far Away",
    }

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.title in expected_titles


@pytest.mark.django_db
def test_query_tunes_one_term_exclude(tune_set):
    search_terms = ["-kern"]

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 7
    for tune in result:
        assert tune.tune.composer != "Kern"


@pytest.mark.django_db
def test_query_tunes_one_term_exclude_fragment(tune_set):
    search_terms = ["-ab"]

    result = query_tunes(tune_set["tunes"], search_terms)

    assert len(result) == 0


@pytest.mark.django_db
def test_query_tunes_one_term_exclude_nickname(tune_set):
    search_terms = ["-lee"]
    excluded_composer = "Konitz"
    excluded_title = "Kary's Trance"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 9
    for tune in result:
        assert tune.tune.composer != excluded_composer
        assert tune.tune.title != excluded_title


@pytest.mark.django_db
def test_query_tunes_one_term_field_key(tune_set):
    search_terms = ["key:F"]
    expected_titles = {"Confirmation", "Long Ago and Far Away", "I Remember You"}

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.title in expected_titles
    for title in expected_titles:
        assert title in {tune.tune.title for tune in result}


@pytest.mark.django_db
def test_query_tunes_one_term_exclude_field_key(tune_set):
    search_terms = ["-key:F"]
    excluded_titles = {"Confirmation", "Long Ago and Far Away", "I Remember You"}

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 7
    for tune in result:
        assert tune.tune.title not in excluded_titles
    for title in excluded_titles:
        assert title not in {tune.tune.title for tune in result}


@pytest.mark.django_db
def test_query_tunes_one_term_exclude_field_nickname(tune_set):
    search_terms = ["-composer:bird"]
    excluded_titles = {"Confirmation", "Dewey Square"}
    excluded_composer = "Parker"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 8
    for tune in result:
        assert tune.tune.composer != excluded_composer
        assert tune.tune.title not in excluded_titles
    for title in excluded_titles:
        assert title not in {tune.tune.title for tune in result}


@pytest.mark.django_db
def test_query_tunes_one_term_field_keys(tune_set):
    search_terms = ["keys:Bb"]
    expected_titles = {
        "Confirmation",
        "Long Ago and Far Away",
        "I Remember You",
        "Someday My Prince Will Come",
    }

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 4
    for tune in result:
        assert tune.tune.title in expected_titles
    for title in expected_titles:
        assert title in {tune.tune.title for tune in result}


# Two term tests
@pytest.mark.django_db
def test_query_tunes_two_terms(tune_set):
    search_terms = ["kern", "love"]
    expected_title = "Dearly Beloved"

    result = query_tunes(tune_set["tunes"], search_terms)
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_two_terms2(tune_set):
    search_terms = ["monk", "hudson"]
    expected_title = "Coming on the Hudson"

    result = query_tunes(tune_set["tunes"], search_terms)
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_two_terms_nickname(tune_set):
    search_terms = ["bird", "dewey"]
    expected_title = "Dewey Square"

    result = query_tunes(tune_set["tunes"], search_terms)
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_two_terms_exclude_one(tune_set):
    search_terms = ["-kern", "love"]
    expected_title = "A Flower is a Lovesome Thing"

    result = query_tunes(tune_set["tunes"], search_terms)
    result_title = result.first().tune.title

    assert result.count() == 1
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_two_terms_exclude_both(tune_set):
    search_terms = ["-kern", "-love"]

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 6
    for tune in result:
        assert tune.tune.composer != "Kern"
        assert "love" not in tune.tune.title.lower()


@pytest.mark.django_db
def test_query_tunes_two_terms_one_field(tune_set):
    search_terms = ["style:jazz", "parker"]
    expected_titles = {"Confirmation", "Dewey Square"}
    expected_style = "jazz"
    expected_composer = "Parker"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.style == expected_style
        assert tune.tune.composer == expected_composer


@pytest.mark.django_db
def test_query_tunes_two_terms_field(tune_set):
    search_terms = ["style:standard", "keys:Eb"]
    expected_titles = {"Someday My Prince Will Come", "All the Things You Are"}
    expected_style = "standard"
    expected_key = "Eb"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.style == expected_style
        assert tune.tune.key == expected_key or expected_key in tune.tune.other_keys


@pytest.mark.django_db
def test_query_tunes_two_terms_field_exclude_one(tune_set):
    search_terms = ["style:standard", "-keys:Eb"]
    expected_titles = {"Long Ago and Far Away", "I Remember You", "Dearly Beloved"}
    expected_style = "standard"
    excluded_key = "Eb"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.style == expected_style
        assert (
            tune.tune.key != excluded_key and excluded_key not in tune.tune.other_keys
        )


@pytest.mark.django_db
def test_query_tunes_two_terms_one_field_exclude_nickname(tune_set):
    search_terms = ["style:jazz", "-bird"]
    expected_titles = {
        "Coming on the Hudson",
        "Kary's Trance",
        "A Flower is a Lovesome Thing",
    }
    expected_style = "jazz"
    excluded_composer = "Parker"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.style == expected_style
        assert tune.tune.composer != excluded_composer


@pytest.mark.django_db
def test_query_tunes_two_terms_field_exclude_both(tune_set):
    search_terms = ["-style:standard", "-keys:Eb"]
    expected_titles = {
        "Coming on the Hudson",
        "Confirmation",
        "Kary's Trance",
        "A Flower is a Lovesome Thing",
    }
    excluded_style = "standard"
    excluded_key = "Eb"

    result = query_tunes(tune_set["tunes"], search_terms)

    assert result.count() == 4
    for tune in result:
        assert tune.tune.title in expected_titles
        assert tune.tune.style != excluded_style
        assert (
            tune.tune.key != excluded_key and excluded_key not in tune.tune.other_keys
        )


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

    assert result.count() == 10


@pytest.mark.django_db
def test_query_tunes_timespan_week(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=7)

    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 4


@pytest.mark.django_db
def test_query_tunes_timespan_month(tune_set):
    search_terms = [""]
    timespan = timezone.now() - timedelta(days=30)

    result = query_tunes(tune_set["tunes"], search_terms, timespan)

    assert result.count() == 0


def test_return_search_results_too_many(request_fixture, tune_set, search_form_fixture):
    search_terms = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]

    _ = return_search_results(
        request_fixture, search_terms, tune_set["tunes"], search_form_fixture
    )

    assert any(
        "Your query is too long" in msg.message for msg in request_fixture._messages
    )


def test_search_field_title(tune_set):
    field = "title"
    term = "you"
    query = search_field(tune_set["tunes"], field, term)
    expected_titles = {"All the Things You Are", "I Remember You"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.title in expected_titles


def test_search_field_composer(tune_set):
    field = "composer"
    term = "parker"
    query = search_field(tune_set["tunes"], field, term)
    expected_composer = "Parker"
    expected_titles = {"Confirmation", "Dewey Square"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.composer == expected_composer
        assert tune.tune.title in expected_titles


def test_search_field_composer_nickname(tune_set):
    field = "composer"
    term = "bird"
    query = search_field(tune_set["tunes"], field, term)
    expected_composer = "Parker"
    expected_titles = {"Confirmation", "Dewey Square"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.composer == expected_composer
        assert tune.tune.title in expected_titles


def test_search_field_key(tune_set):
    field = "key"
    term = "F"
    query = search_field(tune_set["tunes"], field, term)
    expected_key = "F"
    expected_titles = {"Confirmation", "Long Ago and Far Away", "I Remember You"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.key == expected_key
        assert tune.tune.title in expected_titles


def test_search_field_keys(tune_set):
    field = "keys"
    term = "eb"
    query = search_field(tune_set["tunes"], field, term)
    expected_key = "Eb"
    expected_titles = {
        "Dewey Square",
        "All the Things You Are",
        "Someday My Prince Will Come",
    }

    result = tune_set["tunes"].filter(query)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.key == expected_key or expected_key in tune.tune.other_keys
        assert tune.tune.title in expected_titles


def test_search_field_form(tune_set):
    field = "form"
    term = "abac"
    query = search_field(tune_set["tunes"], field, term)
    expected_form = "ABAC"
    expected_titles = {
        "Dearly Beloved",
        "Long Ago and Far Away",
        "Someday My Prince Will Come",
    }

    result = tune_set["tunes"].filter(query)

    assert result.count() == 3
    for tune in result:
        assert tune.tune.song_form == expected_form
        assert tune.tune.title in expected_titles


def test_search_field_style(tune_set):
    field = "style"
    term = "jazz"
    query = search_field(tune_set["tunes"], field, term)
    expected_style = "jazz"
    expected_titles = {
        "Confirmation",
        "Dewey Square",
        "Coming on the Hudson",
        "Kary's Trance",
        "A Flower is a Lovesome Thing",
    }

    result = tune_set["tunes"].filter(query)

    assert result.count() == 5
    for tune in result:
        assert tune.tune.style == expected_style
        assert tune.tune.title in expected_titles


def test_search_field_meter(tune_set):
    field = "meter"
    term = "3"
    query = search_field(tune_set["tunes"], field, term)
    expected_meter = 3
    expected_titles = {"Someday My Prince Will Come"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 1
    for tune in result:
        assert tune.tune.meter == expected_meter
        assert tune.tune.title in expected_titles


def test_search_field_year(tune_set):
    field = "year"
    term = "1941"
    query = search_field(tune_set["tunes"], field, term)
    expected_year = 1941
    expected_titles = {"I Remember You", "A Flower is a Lovesome Thing"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.year == expected_year
        assert tune.tune.title in expected_titles


def test_search_field_year_partial(tune_set):
    field = "year"
    term = "195"
    query = search_field(tune_set["tunes"], field, term)
    expected_years = {1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959}
    expected_titles = {"Kary's Trance", "Coming on the Hudson"}

    result = tune_set["tunes"].filter(query)

    assert result.count() == 2
    for tune in result:
        assert tune.tune.year in expected_years
        assert tune.tune.title in expected_titles
