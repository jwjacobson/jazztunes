from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q


from .models import Tune


def search_field(tune_set, field, term):
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
        return nickname_search(tune_set, term)

    else:
        return Q(**{f"tune__{field}__icontains": term})


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
    nickname_query = Q(tune__composer__icontains=Tune.NICKNAMES[search_term])
    return nickname_query


def query_tunes(tune_set, search_terms, timespan=None):
    """
    Run a search of the user's repertoire and return the results.
    """
    combined_query = Q()

    for term in search_terms:
        negate = False

        if term.startswith("-"):
            negate = True
            term = term[1:]

        # If the term contains a colon, attempt a field-specific search
        if ":" in term:
            field, search_value = term.split(":", 1)
            if field.lower() in Tune.field_names:
                term_query = search_field(tune_set, field, search_value)

        # Default, search across all fields
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

            # If the term is a nickname, add in the nickname search
            if term in Tune.NICKNAMES:
                term_query |= nickname_search(tune_set, term)

        if negate:
            term_query = ~term_query

        combined_query &= term_query

    tune_set = tune_set.filter(combined_query)

    if timespan is not None:
        tune_set = tune_set.exclude(last_played__gte=timespan)

    return tune_set


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
