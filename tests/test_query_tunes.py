import pytest
from django.contrib.auth import get_user_model

from tune.models import Tune, RepertoireTune
from tune.views import query_tunes


@pytest.fixture
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

    for tune in tunes:
        RepertoireTune.objects.create(tune=tune, player=user)

    return RepertoireTune.objects.all()


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
def test_query_tunes_nickname2(tune_set):
    search_terms = ["bird", "dewey"]
    result = query_tunes(tune_set, search_terms)

    assert result.count() == 1

    expected_title = "Dewey Square"
    result_title = result.first().tune.title
    assert result_title == expected_title
