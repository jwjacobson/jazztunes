import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import Tune, RepertoireTune
from .forms import TuneForm, RepertoireTuneForm, SearchForm, PlayForm


def query_tunes(tune_set, search_terms):
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
        searches.add(term_query)

    search_results = tune_set.intersection(*searches)

    return search_results


@login_required(login_url="/accounts/login/")
def tune_list(request):
    user = request.user
    tunes = RepertoireTune.objects.select_related("tune").filter(player=user)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            if len(search_terms) > 4:
                messages.error(
                    request,
                    f"Your query is too long ({len(search_terms)} terms, maximum of 4). Consider using advanced search for more granularity.",
                )
                return render(
                    request,
                    "tune/list.html",
                    {"tunes": tunes, "search_form": search_form},
                )

            tunes = query_tunes(tunes, search_terms)

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


@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login")
def tune_play(request):
    user = request.user
    tunes = RepertoireTune.objects.select_related("tune").filter(player=user)
    original_search_string = ""
    search_form = SearchForm(request.POST or None)
    play_form = PlayForm(request.POST or None)
    is_search = False

    if request.method == "POST":
        if "search_term" in request.POST:
            if search_form.is_valid():
                is_search = True
                original_search_string = search_form.cleaned_data["search_term"]
                search_terms = original_search_string.split(" ")

                if len(search_terms) > 4:
                    messages.error(
                        request,
                        f"Your query is too long ({len(search_terms)} terms, maximum of 4). Consider using advanced search for more granularity.",
                    )
                    return render(
                        request,
                        "tune/play.html",
                        {"tunes": tunes, "search_form": search_form},
                    )

                tunes = query_tunes(tunes, search_terms)
                if not tunes:
                    messages.error(request, "No tunes match your search.")
                    return render(
                        request,
                        "tune/play.html",
                        {"tunes": tunes, "search_form": search_form},
                    )

                if len(tunes) == 1:
                    suggested_tune = tunes.get()

                else:
                    suggested_tune = random.choice(tunes)

                play_form = PlayForm(initial={"suggested_tune": suggested_tune})
                return render(request, "tune/play.html", locals())

        elif "choice" in request.POST:
            if play_form.is_valid():
                choice = request.POST.get("choice")
                suggested_tune = play_form.cleaned_data.get("suggested_tune")
                breakpoint()
                if choice == "Play!":
                    suggested_tune.last_played = timezone.now()
                    suggested_tune.save()
                    messages.success(request, f"Played {suggested_tune.tune.title}!")

    else:
        search_form = SearchForm()
        play_form = PlayForm()

    return render(request, "tune/play.html", locals())
