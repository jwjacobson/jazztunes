from random import choice

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse

from .models import Tune, RepertoireTune
from .forms import TuneForm, RepertoireTuneForm, SearchForm

MAX_SEARCH_TERMS = 4
NICKNAMES = {
    "bird": "Parker",
    "bud": "Powell",
    "miles": "Davis",
    "wayne": "Shorter",
    "joe": "Henderson",
    "lee": "Konitz",
    "diz": "Gillespie",
    "dizzy": "Gillespie",
    "duke": "Ellington",
    "sonny": "Rollins",
    "bill": "Evans",
    "herbie": "Hancock",
    "cedar": "Walton",
}


def query_tunes(tune_set, search_terms, timespan=None):
    searches = set()

    for term in search_terms:
        if term in NICKNAMES:
            term_query = tune_set.filter(Q(tune__composer__icontains=NICKNAMES[term]))
            searches.add(term_query)

        term_query = tune_set.filter(
            Q(tune__title__icontains=term)
            | Q(tune__composer__icontains=term)
            | Q(tune__key__icontains=term)
            | Q(tune__other_keys__icontains=term)
            | Q(tune__song_form__icontains=term)
            | Q(tune__style__icontains=term)
            | Q(tune__meter__icontains=term)
            | Q(tune__year__icontains=term)
            | Q(tune__tags__name__icontains=term)
            | Q(knowledge__icontains=term)
        )

        if timespan is not None:
            term_query = term_query.exclude(last_played__gte=timespan)

        searches.add(term_query)

    search_results = searches.pop()

    while searches:
        search_results = search_results & searches.pop()

    return search_results


@login_required
def tune_list(request):
    user = request.user
    tunes = RepertoireTune.objects.select_related("tune").filter(player=user)
    tune_count = len(tunes)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            results = return_search_results(request, search_terms, tunes, search_form)
            tunes = results.get("tunes")
            tune_count = results.get("tune_count")

    else:
        search_form = SearchForm()

    request.session["tune_count"] = tune_count
    return render(
        request,
        "tune/list.html",
        {"tunes": tunes, "search_form": search_form, "tune_count": tune_count},
    )


@login_required
def tune_new(request):
    if request.method == "POST":
        tune_form = TuneForm(request.POST)
        rep_form = RepertoireTuneForm(request.POST)
        if tune_form.is_valid():
            with transaction.atomic():
                new_tune = tune_form.save(commit=False)
                new_tune.created_by = request.user
                new_tune.save()
                tune_form.save_m2m()

                RepertoireTune.objects.create(
                    tune=new_tune, player=request.user, knowledge=rep_form.data["knowledge"]
                )
                messages.success(
                    request,
                    f"{new_tune.title} has been added to your repertoire.",
                )
            return redirect("tune:tune_list")
    else:
        tune_form = TuneForm()
        rep_form = RepertoireTuneForm()

    return render(request, "tune/form.html", {"tune_form": tune_form, "rep_form": rep_form})


@login_required
def tune_edit(request, pk):
    tune = get_object_or_404(Tune, pk=pk)
    rep_tune = get_object_or_404(RepertoireTune, tune=tune, player=request.user)

    tune_form = TuneForm(request.POST or None, instance=tune)
    rep_form = RepertoireTuneForm(request.POST or None, instance=rep_tune)

    if tune_form.is_valid() and rep_form.is_valid():
        with transaction.atomic():
            updated_tune = tune_form.save()
            rep_form.save()
            messages.success(
                request,
                f"{updated_tune.title} has been updated.",
            )
        return redirect("tune:tune_list")

    return render(
        request,
        "tune/form.html",
        {"tune": tune, "rep_tune": rep_tune, "tune_form": tune_form, "rep_form": rep_form},
    )


@login_required
def tune_delete(request, pk):
    tune = get_object_or_404(Tune, pk=pk)
    rep_tune = get_object_or_404(RepertoireTune, tune=tune, player=request.user)

    rep_tune.delete()

    tune_count = request.session["tune_count"] - 1
    request.session["tune_count"] = tune_count
    request.session.modified = True

    response = HttpResponse(status=200)
    response["HX-Trigger"] = "tuneDeleted"
    return response


@login_required
def recount(request):
    tune_count = request.session["tune_count"]
    return render(request, "tune/_count.html", {"tune_count": tune_count})


@login_required
def get_random_tune(request):
    original_search_string = request.GET.get("search", "")
    search_terms = original_search_string.split(" ")
    tunes = (
        RepertoireTune.objects.select_related("tune")
        .filter(player=request.user)
        .exclude(knowledge="don't know")
    )

    rep_tunes = query_tunes(tunes, search_terms)

    if not rep_tunes:
        return render(request, "tune/_tunes.html", {"selected_tune": None})

    rep_tunes = list(rep_tunes)
    selected_tune = choice(rep_tunes)

    rep_tunes.remove(selected_tune)
    request.session["rep_tunes"] = [rt.id for rt in rep_tunes]
    request.session.save()

    return render(request, "tune/_tunes.html", {"selected_tune": selected_tune})


@login_required
def change_tune(request):
    if not request.session.get("rep_tunes"):
        return render(request, "tune/_tunes.html", {"selected_tune": None})

    chosen_tune_id = choice(request.session["rep_tunes"])
    request.session["rep_tunes"].remove(chosen_tune_id)
    request.session.save()

    selected_tune = RepertoireTune.objects.get(id=chosen_tune_id)
    return render(request, "tune/_tunes.html", {"selected_tune": selected_tune})


@login_required
def play(request, pk):
    url_name = request.resolver_match.url_name
    templates = {
        "play_list": "tune/_play_list.html",
        "play_play": "tune/_play_play.html",
    }

    rep_tune = get_object_or_404(RepertoireTune, id=pk, player=request.user)
    rep_tune.last_played = timezone.now()
    rep_tune.save()
    return render(request, templates.get(url_name, "/"), {"last_played": rep_tune.last_played})


@login_required
def tune_play(request):
    return render(request, "tune/play.html")


@login_required
def tune_browse(request):
    user = request.user
    admin = User.objects.get(id=settings.ADMIN_USER_ID)

    user_tunes = RepertoireTune.objects.select_related("tune").filter(player=user)
    user_tune_titles = {
        tune.tune.title for tune in user_tunes
    }  # using title now since the user's and the admin's id for the same tune are now distinct

    tunes = RepertoireTune.objects.select_related("tune").filter(player=admin)
    tune_count = len(tunes)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            results = return_search_results(request, search_terms, tunes, search_form)
            tunes = results.get("tunes")
            tune_count = results.get("tune_count")

    else:
        search_form = SearchForm()

    request.session["tune_count"] = tune_count
    return render(
        request,
        "tune/browse.html",
        {
            "tunes": tunes,
            "search_form": search_form,
            "user_tune_titles": user_tune_titles,
            "tune_count": tune_count,
        },
    )


@login_required
def tune_take(request, pk):
    user = request.user
    admin_tune = get_object_or_404(RepertoireTune, pk=pk)
    rep_form = RepertoireTuneForm(request.POST)

    if admin_tune.player_id != settings.ADMIN_USER_ID:
        messages.error(request, "You can only take public tunes into your repertoire.")
        return render(request, "tune/browse.html", {"admin_tune": admin_tune})

    tune = admin_tune.tune

    tune.pk = None
    tune.created_by = user
    tune.save()

    new_rep_tune = RepertoireTune.objects.create(tune=tune, player=request.user)

    return render(
        request,
        "tune/_take.html",
        {"rep_form": rep_form, "tune": tune, "new_rep_tune": new_rep_tune},
    )


@login_required
def set_knowledge(request, pk):
    rep_tune = RepertoireTune.objects.get(pk=pk)
    rep_form = RepertoireTuneForm(request.POST)

    if rep_form.is_valid():
        rep_tune.knowledge = rep_form.cleaned_data["knowledge"]
        rep_tune.save()
    else:
        print("invalid")
        print(rep_form.errors)

    return render(request, "tune/_taken.html", {"rep_form": rep_form})


def return_search_results(request, search_terms, tunes, search_form, timespan=None):
    """
    Return a list of tunes that match the search terms.
    """
    if len(search_terms) > MAX_SEARCH_TERMS:
        messages.error(
            request,
            f"Your query is too long ({len(search_terms)} terms, maximum of {MAX_SEARCH_TERMS}). Consider using advanced search for more granularity.",
        )
        return render(
            request,
            "tune/list.html",
            {"tunes": tunes, "search_form": search_form},
        )
    if not timespan:
        tunes = query_tunes(tunes, search_terms)
    else:
        tunes = query_tunes(tunes, search_terms, timespan)

    if not tunes:
        tune_count = 0
        messages.error(request, "No tunes match your search.")
        return render(
            request,
            "tune/browse.html",
            {"tunes": tunes, "search_form": search_form, "tune_count": tune_count},
        )
    else:
        tune_count = len(tunes)

    return {"tunes": tunes, "tune_count": tune_count}
