from datetime import timedelta

from django.db.models import Count, Q, Value, Case, When
from django.db.models.functions import NullIf, Coalesce
from django.utils import timezone

from jazztunes.models import RepertoireTune


TIMESPAN_CHOICES = [
    (None, "All time"),
    (7, "Past week"),
    (30, "Past month"),
    (90, "Past 3 months"),
]

DEFAULT_LIMIT = 10


def _play_count_filter(days=None):
    """
    Build a Q filter for counting plays, optionally restricted to a time window.
    """
    if days is not None:
        cutoff = timezone.now() - timedelta(days=days)
        return Q(plays__played_at__gte=cutoff)
    return Q()


def get_most_played_tunes(user, limit=10, days=None):
    return (
        RepertoireTune.objects.filter(player=user)
        .select_related("tune")
        .annotate(play_count=Count("plays", filter=_play_count_filter(days)))
        .order_by("-play_count")[:limit]
    )


def get_least_played_tunes(user, limit=10, days=None):
    return (
        RepertoireTune.objects.filter(player=user)
        .select_related("tune")
        .annotate(play_count=Count("plays", filter=_play_count_filter(days)))
        .order_by("play_count")[:limit]
    )


def get_plays_by_style(user, days=None):
    play_filter = _play_count_filter(days)

    return (
        RepertoireTune.objects.filter(player=user)
        .exclude(tune__style="")
        .values("tune__style")
        .annotate(play_count=Count("plays", filter=play_filter))
    )
