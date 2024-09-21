from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q


from .models import Tune


def search_field(tune_set, search_term):
    """
    Search a specific field for a term.
    """
    split_term = search_term.split(":")
    field, term = split_term[0], split_term[1]

    if field.lower() == "keys":
        term_query = tune_set.filter(
            Q(tune__key__icontains=term) | Q(tune__other_keys__icontains=term)
        )

    elif field.lower() == "form":
        if term.lower() == "blues" or term.lower() == "irregular":
            term_query = tune_set.filter(Q(tune__song_form=term))
        else:
            term_query = tune_set.filter(Q(tune__song_form=term.upper()))

    elif field.lower() == "tags":
        term_query = tune_set.filter(Q(tags__name__icontains=term))

    else:
        term_query = tune_set.filter(Q(**{f"tune__{field}__icontains": term}))

    return term_query


def exclude_term(tune_set, search_term):
    """
    Exclude a term from a search.
    """
    excluded_term = search_term[1:]

    term_query = tune_set.exclude(
        Q(tune__title__icontains=excluded_term)
        | Q(tune__composer__icontains=excluded_term)
        | Q(tune__key__icontains=excluded_term)
        | Q(tune__other_keys__icontains=excluded_term)
        | Q(tune__song_form__icontains=excluded_term)
        | Q(tune__style__icontains=excluded_term)
        | Q(tune__meter__icontains=excluded_term)
        | Q(tune__year__icontains=excluded_term)
        | Q(knowledge__icontains=excluded_term)
        | Q(tags__name__icontains=excluded_term)
    )

    return term_query


def nickname_search(tune_set, search_term):
    """
    Search for a composer by their nickname.
    """
    nickname_query = tune_set.filter(
        Q(tune__composer__icontains=Tune.NICKNAMES[search_term])
    )
    return nickname_query


def query_tunes(tune_set, search_terms, timespan=None):
    """
    Run a search of the user's repertoire and return the results.
    """
    searches = set()

    for term in search_terms:
        if term.startswith("-"):
            term_query = exclude_term(tune_set, term)

        elif (
            term
            and len(term.split(":")) > 1
            and term.split(":")[0].lower() in Tune.field_names
        ):
            term_query = search_field(tune_set, term)

        else:
            term_query = tune_set.filter(
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
                term_query |= nickname_search(tune_set, term)

        if timespan is not None:
            term_query = term_query.exclude(last_played__gte=timespan)

        searches.add(term_query)

    search_results = searches.pop()

    while searches:
        search_results &= searches.pop()

    return search_results


def return_search_results(request, search_terms, tunes, search_form, timespan=None):
    """
    Run query_tunes and return the results to the view that called it.
    """
    if len(search_terms) > Tune.MAX_SEARCH_TERMS:
        messages.error(
            request,
            f"Your query is too long ({len(search_terms)} terms, maximum of {Tune.MAX_SEARCH_TERMS}).",
        )
        return render(
            request,
            "tune/list.html",
            {"tunes": tunes, "search_form": search_form},
        )

    tunes = query_tunes(tunes, search_terms, timespan=timespan)

    tune_count = len(tunes)
    if not tune_count:
        messages.error(request, "No tunes match your search.")
        return render(
            request,
            "tune/browse.html",
            {"tunes": tunes, "search_form": search_form, "tune_count": tune_count},
        )

    return {"tunes": tunes, "tune_count": tune_count}
