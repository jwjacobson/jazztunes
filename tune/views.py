from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import Tune, RepertoireTune
from .forms import TuneForm, RepertoireTuneForm, SearchForm


def query_tunes(initial_query, search_terms):
    additional_queries = set()
    for term in search_terms:
        term_query = initial_query.filter(
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
        additional_queries.add(term_query)

    all_tunes = initial_query.intersection(*additional_queries)
    return all_tunes


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

    is_search = False

    if request.method == "POST" and "search_term" in request.POST:
        is_search = True
        search_form = SearchForm(request.POST)

        if search_form.is_valid():
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

    else:
        search_form = SearchForm()

    # TODO: figure out why shuffling does not work
    if len(tunes) < 3:
        suggested_tune = tunes.first()
    else:
        suggested_tune = tunes.order_by("?").first()

    if request.method == "POST":
        if "yes" in request.POST:
            tune_to_play = suggested_tune
            tune_to_play.last_played = timezone.now()
            tune_to_play.save()
            messages.success(request, f"Played {tune_to_play.tune.title}!")
        elif "no" in request.POST:
            # TODO: suggest another tune
            messages.info(request, "Please search again")

    return render(
        request,
        "tune/play.html",
        {
            "tunes": tunes,
            "search_form": search_form,
            "original_search_string": original_search_string,
            "suggested_tune": suggested_tune,
            "is_search": is_search,
        },
    )
