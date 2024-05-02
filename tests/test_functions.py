# Tests for the helper functions in views.py

import pytest
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest

from tune.models import Tune, RepertoireTune
from tune.views import query_tunes, return_search_results


@pytest.fixture()
def tune_set(db, client):
    """
    Create a tune set for use in tests that require one.
    """
    tunes = {
        Tune.objects.create(
            title="Confirmation",
            composer="Parker",
            key="F",
            other_keys="D- Bb Db",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1945,
        ),
        Tune.objects.create(
            title="Dewey Square",
            composer="Parker",
            key="Eb",
            other_keys="Ab",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1947,
        ),
        Tune.objects.create(
            title="All the Things You Are",
            composer="Kern",
            key="Ab",
            other_keys="C Eb G E",
            song_form="AABA",
            style="standard",
            meter=4,
            year=1939,
        ),
        Tune.objects.create(
            title="Dearly Beloved",
            composer="Kern",
            key="C",
            other_keys="Db",
            song_form="ABAC",
            style="standard",
            meter=4,
            year=1942,
        ),
        Tune.objects.create(
            title="Long Ago and Far Away",
            composer="Kern",
            key="F",
            other_keys="Ab C Bb",
            song_form="ABAC",
            style="standard",
            meter=4,
            year=1944,
        ),
        Tune.objects.create(
            title="Coming on the Hudson",
            composer="Monk",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1958,
        ),
        Tune.objects.create(
            title="Someday My Prince Will Come",
            composer="Churchill",
            key="Bb",
            other_keys="C- Eb",
            song_form="ABAC",
            style="standard",
            meter=3,
            year=1937,
        ),
        Tune.objects.create(
            title="Kary's Trance",
            composer="Konitz",
            key="A-",
            other_keys="D- C",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1956,
        ),
        Tune.objects.create(
            title="A Flower is a Lovesome Thing",
            composer="Strayhorn",
            key="Db",
            other_keys="D",
            song_form="AABA",
            style="jazz",
            meter=4,
            year=1941,
        ),
        Tune.objects.create(
            title="I Remember You",
            composer="Schertzinger",
            key="F",
            other_keys="Bb D C G-",
            song_form="AABA",
            style="standard",
            meter=4,
            year=1941,
        ),
    }

    user_model = get_user_model()
    user = user_model.objects.create_user(username="testuser", password="12345")
    client.force_login(user)

    now = timezone.now()
    for i, tune in enumerate(tunes):
        last_played_date = now - timedelta(days=i + 1)
        RepertoireTune.objects.create(tune=tune, player=user, last_played=last_played_date)

    return RepertoireTune.objects.all()


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

    assert result.count() == 3
    assert all("Kern" in tune.tune.composer for tune in result)

    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"All the Things You Are", "Dearly Beloved", "Long Ago and Far Away"}

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

    assert result.count() == 2

    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"Confirmation", "Dewey Square"}

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_common_fragment(tune_set):
    search_terms = ["love"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 2

    result_titles = {tune.tune.title for tune in result}
    expected_titles = {"Dearly Beloved", "A Flower is a Lovesome Thing"}

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_decade(tune_set):
    search_terms = ["194"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 6

    result_titles = {tune.tune.title for tune in result}
    expected_titles = {
        "Dearly Beloved",
        "A Flower is a Lovesome Thing",
        "Confirmation",
        "Dewey Square",
        "I Remember You",
        "Long Ago and Far Away",
    }

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_form(tune_set):
    search_terms = ["abac"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 3

    result_titles = {tune.tune.title for tune in result}
    expected_titles = {
        "Dearly Beloved",
        "Someday My Prince Will Come",
        "Long Ago and Far Away",
    }

    for title in expected_titles:
        assert title in result_titles


@pytest.mark.django_db
def test_query_tunes_exclude(tune_set):
    search_terms = ["-kern"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 7


# Two term tests
@pytest.mark.django_db
def test_query_tunes_kern2(tune_set):
    search_terms = ["kern", "love"]
    result = query_tunes(tune_set, search_terms)
    assert result.count() == 1

    expected_title = "Dearly Beloved"
    result_title = result.first().tune.title
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_monk(tune_set):
    search_terms = ["monk", "hudson"]
    result = query_tunes(tune_set, search_terms)
    assert result.count() == 1

    expected_title = "Coming on the Hudson"
    result_title = result.first().tune.title
    assert result_title == expected_title


@pytest.mark.django_db
def test_query_tunes_nickname2(tune_set):
    search_terms = ["bird", "dewey"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 1

    expected_title = "Dewey Square"
    result_title = result.first().tune.title
    assert result_title == expected_title


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
