"""
Tests for the analytics service module.

These tests define the expected behavior of analytics query functions:
- get_most_played_tunes(user, limit, days)
- get_least_played_tunes(user, limit, days)
- get_top_composers(user, limit, days)
- get_plays_by_style(user, days)

get_most_played_tunes, get_least_played_tunes, and get_top_composers accept:
    user: User instance
    limit: int (default 10) — max results to return
    days: int or None (default None) — if set, only count plays within this many days

get_plays_by_style accepts:
    user: User instance
    days: int or None (default None) — if set, only count plays within this many days

Return types:
    get_most_played_tunes -> QuerySet[RepertoireTune] annotated with play_count, desc
    get_least_played_tunes -> QuerySet[RepertoireTune] annotated with play_count, asc
    get_top_composers -> ValuesQuerySet[{composer: str, play_count: int}], desc
    get_plays_by_style -> ValuesQuerySet[{tune__style: str, play_count: int}], desc
"""

import pytest
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from jazztunes.models import Play, RepertoireTune, Tune
from jazztunes.analytics import (
    get_most_played_tunes,
    get_least_played_tunes,
    get_plays_by_style,
)

User = get_user_model()


@pytest.fixture
def analytics_data():
    """
    A user with 5 tunes and a controlled play distribution.

    Tune layout:
        "Donna Lee"      composer="Parker"   style="jazz"      plays: 10 (all recent)
        "Blue in Green"  composer="Evans"     style="jazz"      plays: 5  (all recent)
        "Footprints"     composer="Shorter"   style="jazz"      plays: 3  (all old, ~90 days)
        "Pannonica"      composer="Monk"      style="standard"  plays: 1  (recent)
        "Blues for Alice" composer="Parker"    style="jazz"      plays: 0
    """
    user = User.objects.create_user(username="testuser", password="testpass")
    now = timezone.now()
    recent = now - timedelta(days=7)
    old = now - timedelta(days=90)

    tune_data = [
        ("Donna Lee", "Parker", "jazz"),
        ("Blue in Green", "Evans", "jazz"),
        ("Footprints", "Shorter", "jazz"),
        ("Pannonica", "Monk", "standard"),
        ("Blues for Alice", "Parker", "jazz"),
    ]

    rep_tunes = {}
    for title, composer, style in tune_data:
        tune = Tune.objects.create(
            title=title, composer=composer, style=style, created_by=user
        )
        rep_tune = RepertoireTune.objects.create(tune=tune, player=user)
        key = title.split()[0].lower()
        rep_tunes[key] = rep_tune

    plays = []
    # Donna Lee: 10 recent plays
    for index in range(10):
        plays.append(Play(
            repertoire_tune=rep_tunes["donna"],
            played_at=recent - timedelta(hours=index),
        ))
    # Blue in Green: 5 recent plays
    for index in range(5):
        plays.append(Play(
            repertoire_tune=rep_tunes["blue"],
            played_at=recent - timedelta(hours=index),
        ))
    # Footprints: 3 old plays (>60 days ago)
    for index in range(3):
        plays.append(Play(
            repertoire_tune=rep_tunes["footprints"],
            played_at=old - timedelta(hours=index),
        ))
    # Pannonica: 1 recent play
    plays.append(Play(
        repertoire_tune=rep_tunes["pannonica"],
        played_at=recent,
    ))
    # Blues for Alice: 0 plays

    Play.objects.bulk_create(plays)

    return {"user": user, "rep_tunes": rep_tunes, "now": now}


# --- get_most_played_tunes ---


@pytest.mark.django_db
def test_most_played_returns_all_ordered_by_play_count(analytics_data):
    results = get_most_played_tunes(analytics_data["user"])
    counts = [result.play_count for result in results]
    assert counts == [10, 5, 3, 1, 0]


@pytest.mark.django_db
def test_most_played_limit(analytics_data):
    results = get_most_played_tunes(analytics_data["user"], limit=3)
    assert len(results) == 3
    assert results[0].play_count == 10
    assert results[2].play_count == 3


@pytest.mark.django_db
def test_most_played_days_filters_recent(analytics_data):
    """With days=30, Footprints' old plays shouldn't count."""
    results = get_most_played_tunes(analytics_data["user"], days=30)
    counts = {result.tune.title: result.play_count for result in results}
    assert counts["Donna Lee"] == 10
    assert counts["Blue in Green"] == 5
    assert counts["Footprints"] == 0
    assert counts["Pannonica"] == 1


@pytest.mark.django_db
def test_most_played_days_and_limit(analytics_data):
    results = get_most_played_tunes(analytics_data["user"], limit=2, days=30)
    assert len(results) == 2
    assert results[0].tune.title == "Donna Lee"
    assert results[1].tune.title == "Blue in Green"


@pytest.mark.django_db
def test_most_played_excludes_other_users(analytics_data):
    other = User.objects.create_user(username="other", password="pass")
    results = get_most_played_tunes(other)
    assert len(results) == 0


# --- get_least_played_tunes ---


@pytest.mark.django_db
def test_least_played_returns_all_ordered_asc(analytics_data):
    results = get_least_played_tunes(analytics_data["user"])
    counts = [result.play_count for result in results]
    assert counts == [0, 1, 3, 5, 10]


@pytest.mark.django_db
def test_least_played_includes_zero_plays(analytics_data):
    results = get_least_played_tunes(analytics_data["user"], limit=1)
    assert results[0].play_count == 0
    assert results[0].tune.title == "Blues for Alice"


@pytest.mark.django_db
def test_least_played_limit(analytics_data):
    results = get_least_played_tunes(analytics_data["user"], limit=2)
    assert len(results) == 2
    titles = [result.tune.title for result in results]
    assert titles == ["Blues for Alice", "Pannonica"]


@pytest.mark.django_db
def test_least_played_days_filters_recent(analytics_data):
    """With days=30, Footprints has 0 recent plays — tied with Blues for Alice."""
    results = get_least_played_tunes(analytics_data["user"], days=30)
    zero_play_tunes = [result for result in results if result.play_count == 0]
    zero_titles = {result.tune.title for result in zero_play_tunes}
    assert "Blues for Alice" in zero_titles
    assert "Footprints" in zero_titles


# --- get_plays_by_style ---


@pytest.mark.django_db
def test_plays_by_style_counts_plays_per_style(analytics_data):
    """Jazz: 10 (Donna Lee) + 5 (Blue in Green) + 3 (Footprints) = 18. Standard: 1 (Pannonica)."""
    results = list(get_plays_by_style(analytics_data["user"]))
    style_counts = {result["tune__style"]: result["play_count"] for result in results}
    assert style_counts["jazz"] == 18
    assert style_counts["standard"] == 1


@pytest.mark.django_db
def test_plays_by_style_days_filters_recent(analytics_data):
    """With days=30, Footprints' 3 old jazz plays shouldn't count."""
    results = list(get_plays_by_style(analytics_data["user"], days=30))
    style_counts = {result["tune__style"]: result["play_count"] for result in results}
    assert style_counts["jazz"] == 15
    assert style_counts["standard"] == 1


@pytest.mark.django_db
def test_plays_by_style_excludes_blank_style(analytics_data):
    """Tunes with no style set should not appear in results."""
    user = analytics_data["user"]
    now = analytics_data["now"]

    tune = Tune.objects.create(title="Mystery Tune", style="", created_by=user)
    rep_tune = RepertoireTune.objects.create(tune=tune, player=user)
    Play.objects.create(repertoire_tune=rep_tune, played_at=now - timedelta(hours=1))

    results = list(get_plays_by_style(user))
    styles = {result["tune__style"] for result in results}
    assert "" not in styles


@pytest.mark.django_db
def test_plays_by_style_excludes_other_users(analytics_data):
    other = User.objects.create_user(username="other3", password="pass")
    results = list(get_plays_by_style(other))
    assert len(results) == 0
