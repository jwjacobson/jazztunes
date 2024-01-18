from random import choice

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import Tune, RepertoireTune
from .forms import TuneForm, RepertoireTuneForm, SearchForm, PlayForm

MAX_SEARCH_TERMS = 4


def query_tunes(tune_set, search_terms, timespan=None):
    searches = set()

    for term in search_terms:
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
        )

        if timespan:
            term_query = term_query.exclude(last_played__gte=timespan)

        searches.add(term_query)

    search_results = tune_set.intersection(*searches)

    return search_results


@login_required
def tune_list(request):
    user = request.user
    tunes = RepertoireTune.objects.select_related("tune").filter(player=user)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
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

            timespan = search_form.cleaned_data["timespan"]

            tunes = query_tunes(tunes, search_terms, timespan)

            if not tunes:
                messages.error(request, "No tunes match your search.")
                return render(
                    request,
                    "tune/play.html",
                    {"tunes": tunes, "search_form": search_form},
                )

    else:
        search_form = SearchForm()

    return render(
        request,
        "tune/list.html",
        {"tunes": tunes, "search_form": search_form},
    )


@login_required
def tune_new(request):
    if request.method == "POST":
        tune_form = TuneForm(request.POST)
        rep_form = RepertoireTuneForm(request.POST)
        if tune_form.is_valid():
            with transaction.atomic():
                new_tune = tune_form.save()
                rep_tune = RepertoireTune.objects.create(
                    tune=new_tune, player=request.user, knowledge=rep_form.data["knowledge"]
                )
                messages.success(
                    request,
                    f"Added Tune {new_tune.id}: {new_tune.title} to {rep_tune.player}'s repertoire.",
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
                f"Updated Tune {updated_tune.id}: {updated_tune.title} in {rep_tune.player}'s repertoire.",
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

    if request.method == "POST":
        deleted_id, deleted_title = tune.id, tune.title
        with transaction.atomic():
            tune.delete()
            rep_tune.delete()
            messages.success(
                request,
                f"Deleted Tune {deleted_id}: {deleted_title} from {rep_tune.player}'s repertoire.",
            )
        return redirect("tune:tune_list")

    return render(request, "tune/form.html", {"tune": tune})


@login_required
def search(request):
    # TODO: rename this view to get_random_tune
    original_search_string = request.GET.get("search", "")
    search_terms = original_search_string.split(" ")
    tunes = RepertoireTune.objects.select_related("tune").filter(player=request.user)
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
    rep_tune = get_object_or_404(RepertoireTune, id=pk)
    rep_tune.last_played = timezone.now()
    rep_tune.save()
    # messages.success(request, f"Played {rep_tune.tune.title}!")
    return render(request, "tune/_play.html")


@login_required
def tune_play(request):
    return render(request, "tune/play.html")


@login_required
def tune_browse(request):
    user = request.user
    user_tunes = RepertoireTune.objects.select_related("tune").filter(player=user)
    user_tune_ids = {tune.tune_id for tune in user_tunes}
    tunes = Tune.objects.all().filter(created_by=2)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            if len(search_terms) > MAX_SEARCH_TERMS:
                messages.error(
                    request,
                    f"Your query is too long ({len(search_terms)} terms, maximum of {MAX_SEARCH_TERMS}). Consider using advanced search for more granularity.",
                )
                return render(
                    request,
                    "tune/browse.html",
                    {"tunes": tunes, "search_form": search_form},
                )

            tunes = query_tunes(tunes, search_terms)

            if not tunes:
                messages.error(request, "No tunes match your search.")
                return render(
                    request,
                    "tune/browse.html",
                    {"tunes": tunes, "search_form": search_form},
                )

    else:
        search_form = SearchForm()

    return render(
        request,
        "tune/browse.html",
        {"tunes": tunes, "search_form": search_form, "user_tune_ids": user_tune_ids},
    )


@login_required
def tune_take(request, pk):
    tune = get_object_or_404(Tune, pk=pk)

    if request.method == "POST":
        RepertoireTune.objects.create(tune=tune, player=request.user)
        # rep_tune.save()
        # messages.success(
        #     request,
        #     f"Tune {rep_tune.tune.id}: {rep_tune.tune.title} copied to repertoire.",
        # )
        # return redirect("tune:tune_browse")

    return render(request, "tune/browse.html", {"tune": tune})
