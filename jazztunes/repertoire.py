from random import choice

from django.core.cache import cache
from django.db.models import Count, Max

from .models import Play, RepertoireTune


def _base_queryset():
    """
    The single source of truth for how we query RepertoireTunes.
    Always includes play stats and related data.
    """
    return (
        RepertoireTune.objects
        .select_related("tune")
        .prefetch_related("tags")
        .annotate(
            last_played=Max("plays__played_at"),
            play_count=Count("plays"),
        )
    )


def get_repertoire_queryset(user):
    """
    Return an unevaluated queryset for the user's repertoire.
    Use this instead of get_user_repertoire when you need to filter further (e.g. search).
    """
    return _base_queryset().filter(player=user)


def invalidate_user_repertoire(user_id):
    cache.delete(f"repertoire_{user_id}")


def get_user_repertoire(user):
    """
    Return the user's full repertoire, annotated with play stats and cached.
    """
    cache_key = f"repertoire_{user.id}"
    tunes = cache.get(cache_key)

    if tunes is None:
        tunes = list(
            _base_queryset()
            .filter(player=user)
        )
        cache.set(cache_key, tunes, 60 * 10)

    return tunes


def play_tune(rep_tune):
    """
    Record that a tune was played. Creates a Play object and invalidates cache.
    Returns the created Play.
    """
    play = Play.objects.create(repertoire_tune=rep_tune)
    invalidate_user_repertoire(rep_tune.player_id)
    return play

def add_tune(user, tune, knowledge="know", tags=None):
    """
    Add a tune to a user's repertoire. Returns the new RepertoireTune.
    """
    rep_tune = RepertoireTune.objects.create(
        tune=tune,
        player=user,
        knowledge=knowledge,
    )
    if tags:
        rep_tune.tags.set(tags)

    invalidate_user_repertoire(user.id)
    return rep_tune


def take_tune(user, admin_rep_tune):
    """
    Clone a public (admin) tune into a user's repertoire.
    Returns (new_tune, new_rep_tune).
    """
    tune = admin_rep_tune.tune
    tune.pk = None
    tune.created_by = user
    tune.save()

    rep_tune = RepertoireTune.objects.create(tune=tune, player=user)
    invalidate_user_repertoire(user.id)
    return tune, rep_tune


def delete_tune(rep_tune):
    """
    Remove a tune from a user's repertoire.
    """
    user_id = rep_tune.player_id
    rep_tune.delete()
    invalidate_user_repertoire(user_id)


def pick_random_tune(tunes):
    """
    Pick a random tune from a list. Returns (selected_tune, remaining_ids).
    """
    if not tunes:
        return None, []

    selected = choice(tunes)
    remaining = [t.id for t in tunes if t != selected]
    return selected, remaining


def pick_next_tune(remaining_ids):
    """
    Pick the next random tune from remaining IDs.
    Returns (selected_tune, updated_remaining_ids), or (None, []) if exhausted.
    """
    if not remaining_ids:
        return None, []

    chosen_id = choice(remaining_ids)
    remaining_ids = [id for id in remaining_ids if id != chosen_id]

    selected = (
        _base_queryset()
        .get(id=chosen_id)
    )
    return selected, remaining_ids
