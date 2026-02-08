from django.db.models import Q

from .models import Tune


def search_field(field, term):
    """
    Search a specific field for a term.
    """
    if field.lower() == "key":
        return Q(tune__key__exact=term)

    elif field.lower() == "keys":
        return Q(tune__key__icontains=term) | Q(tune__other_keys__icontains=term)

    elif field.lower() == "form":
        if term.lower() == "blues" or term.lower() == "irregular":
            return Q(tune__song_form=term)
        else:
            return Q(tune__song_form=term.upper())

    elif field.lower() == "tags":
        return Q(tags__name__icontains=term)

    elif field.lower() == "composer" and term in Tune.NICKNAMES:
        return nickname_search(term)

    else:
        return Q(**{f"tune__{field}__icontains": term})


def nickname_search(search_term):
    """
    Search for a composer by their nickname.
    """
    return Q(tune__composer__icontains=Tune.NICKNAMES[search_term])


def query_tunes(tune_set, search_terms, timespan=None):
    """
    Filter a RepertoireTune queryset by search terms and an optional timespan.
    Returns a filtered queryset.
    """
    combined_query = Q()

    for term in search_terms:
        negate = False

        if term.startswith("-"):
            negate = True
            term = term[1:]

        if ":" in term:
            field, search_value = term.split(":", 1)
            if field.lower() in Tune.field_names:
                term_query = search_field(field, search_value)

        else:
            term_query = (
                Q(tune__title__icontains=term)
                | Q(tune__composer__icontains=term)
                | Q(tune__key__icontains=term)
                | Q(tune__other_keys__icontains=term)
                | Q(tune__song_form__icontains=term)
                | Q(tune__style__icontains=term)
                | Q(tune__meter__icontains=term)
                | Q(tune__year__icontains=term)
                | Q(knowledge__icontains=term)
                | Q(tags__name__icontains=term)
            )

            if term in Tune.NICKNAMES:
                term_query |= nickname_search(term)

        if negate:
            term_query = ~term_query

        combined_query &= term_query

    tune_set = tune_set.filter(combined_query)

    if timespan is not None:
        tune_set = tune_set.exclude(last_played__gte=timespan)

    return tune_set.distinct()