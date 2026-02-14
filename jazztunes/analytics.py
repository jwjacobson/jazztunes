from datetime import timedelta

from django.db.models import Count, Q, Value, Case, When
from django.db.models.functions import NullIf, Coalesce
from django.utils import timezone

from jazztunes.models import RepertoireTune


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


def get_top_composers(user, limit=10, days=None):
    """
    Group plays by composer. Empty composer strings are labeled "None".
    """
    play_filter = _play_count_filter(days)

    return (
        RepertoireTune.objects.filter(player=user)
        .annotate(
            composer=Case(
                When(tune__composer="", then=Value("None")),
                default="tune__composer",
            )
        )
        .values("composer")
        .annotate(play_count=Count("plays", filter=play_filter))
        .order_by("-play_count")[:limit]
    )
