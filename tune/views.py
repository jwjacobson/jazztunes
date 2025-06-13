# jazztunes -- A jazz repertoire management app
# Copyright (C) 2024 Jeff Jacobson <jeffjacobsonhimself@gmail.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from random import choice

from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .forms import TuneForm, RepertoireTuneForm, SearchForm
from .models import Tune, RepertoireTune
from .search import return_search_results


def get_user_repertoire(user):
    """Retrieves the user's cached repertoire, or stores it in the cache if not yet cached."""
    cache_key = f"repertoire_{user.id}"
    tunes = cache.get(cache_key)

    if tunes is None:
        tunes = list(
            RepertoireTune.objects.select_related("tune")
            .prefetch_related("tags")
            .filter(player=user)
        )
        cache.set(cache_key, tunes, 60 * 10)  # 10 minutes

    return tunes


def invalidate_user_repertoire(user_id):
    cache.delete(f"repertoire_{user_id}")


@login_required
def tune_list(request):
    """
    Show the user's home page, which displays a searchable repertoire and allows for tune management.
    """
    user = request.user
    search_term_string = " "
    tune_count = 0

    if user.username.endswith("s"):
        possessive = f"{user.username}'"
    else:
        possessive = f"{user.username}'s"

    if request.method == "POST":
        tunes = (
            RepertoireTune.objects.select_related("tune")
            .prefetch_related("tags")
            .filter(player=user)
        )
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            search_term_string = " ".join(search_terms)
            timespan = search_form.cleaned_data["timespan"]
            results = return_search_results(
                request, search_terms, tunes, search_form, timespan
            )
            tunes = results.get("tunes")
            tune_count = results.get("tune_count", 0)
            invalidate_user_repertoire(request.user.id)
    else:
        search_form = SearchForm()
        tunes = get_user_repertoire(user)
        tune_count = len(tunes)

    if request.headers.get("Hx-Request"):
        return render(
            request,
            "tune/partials/_table_list.html",
            {"tunes": tunes, "tune_count": tune_count, "possessive": possessive},
        )

    request.session["tune_count"] = tune_count
    return render(
        request,
        "tune/list.html",
        {
            "tunes": tunes,
            "search_form": search_form,
            "tune_count": tune_count,
            "search_term_string": search_term_string,
            "possessive": possessive,
        },
    )


@login_required
def tune_new(request):
    """
    Create a new tune in a user's repertoire.
    """
    if request.method != "POST":
        tune_form = TuneForm()
        rep_form = RepertoireTuneForm()
        return render(
            request, "tune/form.html", {"tune_form": tune_form, "rep_form": rep_form}
        )

    tune_form = TuneForm(request.POST)
    rep_form = RepertoireTuneForm(request.POST)

    if not tune_form.is_valid() or not rep_form.is_valid():
        return render(
            request, "tune/form.html", {"tune_form": tune_form, "rep_form": rep_form}
        )

    with transaction.atomic():
        new_tune = tune_form.save(commit=False)
        new_tune.created_by = request.user
        new_tune.save()
        tune_form.save_m2m()

        if rep_form.is_valid():
            last_played_cleaned = rep_form.cleaned_data.get("last_played")
            if not last_played_cleaned:
                last_played_cleaned = None

            rep_tune = RepertoireTune.objects.create(
                tune=new_tune,
                player=request.user,
                knowledge=rep_form.data["knowledge"],
                last_played=last_played_cleaned,
            )

            rep_tune.tags.set(rep_form.cleaned_data["tags"])
            invalidate_user_repertoire(request.user.id)

            messages.success(
                request,
                f"{new_tune.title} has been added to your repertoire.",
            )
    return redirect("tune:tune_list")


@login_required
def tune_edit(request, pk):
    """
    Edit a tune in a user's repertoire.
    """
    tune = get_object_or_404(Tune, pk=pk)
    rep_tune = get_object_or_404(RepertoireTune, tune=tune, player=request.user)

    tune_form = TuneForm(request.POST or None, instance=tune)
    rep_form = RepertoireTuneForm(request.POST or None, instance=rep_tune)

    if tune_form.is_valid() and rep_form.is_valid():
        with transaction.atomic():
            updated_tune = tune_form.save()
            _ = rep_form.save()
            messages.success(
                request,
                f"{updated_tune.title} has been updated.",
            )

            invalidate_user_repertoire(request.user.id)
        return redirect("tune:tune_list")

    return render(
        request,
        "tune/form.html",
        {
            "tune": tune,
            "rep_tune": rep_tune,
            "tune_form": tune_form,
            "rep_form": rep_form,
        },
    )


@login_required
def tune_delete(request, pk):
    """
    Delete a tune from a user's repertoire.
    """
    tune = get_object_or_404(Tune, pk=pk)
    rep_tune = get_object_or_404(RepertoireTune, tune=tune, player=request.user)

    with transaction.atomic():
        rep_tune.delete()
        invalidate_user_repertoire(request.user.id)

    tune_count = request.session["tune_count"] - 1
    request.session["tune_count"] = tune_count
    request.session.modified = True

    response = HttpResponse(status=200)
    response["HX-Trigger"] = "tuneDeleted, clearModal"
    return response


@login_required
def tune_delete_confirm(request, pk):
    """
    Return the delete confirmation modal HTML.
    """
    tune = get_object_or_404(Tune, pk=pk)
    row_id = f"tune-row-{pk}"
    get_object_or_404(RepertoireTune, tune=tune, player=request.user)

    return render(
        request, "tune/partials/_delete_confirm.html", {"tune": tune, "row_id": row_id}
    )


@login_required
def recount(request):
    """
    Update the tune count that displays on the home and public pages.
    """
    tune_count = request.session["tune_count"]
    return render(request, "tune/partials/_count.html", {"tune_count": tune_count})


@login_required
def get_random_tune(request):
    user = request.user
    tunes = (
        RepertoireTune.objects.select_related("tune")
        .filter(player=user)
        .exclude(knowledge="don't know")
    )
    search_form = SearchForm(request.POST or None)

    # A flatter way to validate the form, rather than indenting everything under it
    if not search_form.is_valid():
        # This should never trigger
        messages.error(request, "Invalid search")
        return render(request, "tune/play.html")

    search_terms = search_form.cleaned_data["search_term"].split(" ")
    timespan = search_form.cleaned_data.get("timespan", None)
    result_dict = return_search_results(
        request, search_terms, tunes, search_form, timespan
    )

    if "error" in result_dict:
        messages.error(request, result_dict["error"])
        return render(request, result_dict["template"])

    tunes = result_dict.get("tunes")

    if tunes:
        selected_tune = choice(tunes)
        remaining_rep_tunes_ids = [tune.id for tune in tunes if tune != selected_tune]
        request.session["rep_tunes"] = remaining_rep_tunes_ids
    else:
        selected_tune = None
    request.session.save()

    return render(
        request, "tune/partials/_play_card.html", {"selected_tune": selected_tune}
    )


@login_required
def change_tune(request):
    """
    Select a different tune from the play search results if the previous one is rejected.
    """
    if not request.session.get("rep_tunes"):
        return render(request, "tune/partials/_play_card.html", {"selected_tune": None})

    chosen_tune_id = choice(request.session["rep_tunes"])
    request.session["rep_tunes"].remove(chosen_tune_id)
    request.session.save()

    selected_tune = RepertoireTune.objects.get(id=chosen_tune_id)
    return render(
        request, "tune/partials/_play_card.html", {"selected_tune": selected_tune}
    )


@login_required
def play(request, pk):
    """
    Update a tune's last_played field to now.
    """
    url_name = request.resolver_match.url_name
    templates = {
        "play_list": "tune/partials/_play_list.html",
        "play_play": "tune/partials/_play_play.html",
    }

    rep_tune = get_object_or_404(RepertoireTune, id=pk, player=request.user)
    rep_tune.last_played = timezone.now()
    rep_tune.play_count += 1
    rep_tune.save()
    invalidate_user_repertoire(request.user.id)

    if url_name == "play_play":
        return render(
            request,
            "tune/partials/_another_button.html",
            {"last_played": rep_tune.last_played, "selected_tune": rep_tune},
        )

    return render(
        request,
        templates.get(url_name, "/"),
        {"last_played": rep_tune.last_played, "selected_tune": rep_tune},
    )


@login_required
def tune_play(request):
    """
    Load the play page.
    """
    search_form = SearchForm()
    return render(request, "tune/play.html", {"search_form": search_form})


@login_required
def tune_browse(request):
    """
    Show the public page of preloaded tunes.
    """

    user = request.user
    user_tunes = get_user_repertoire(user)
    user_tune_titles = {tune.tune.title for tune in user_tunes}

    admin_user = User.objects.get(id=settings.ADMIN_USER_ID)
    tunes = get_user_repertoire(admin_user)
    tune_count = len(tunes)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            results = return_search_results(request, search_terms, tunes, search_form)
            tunes = results.get("tunes")
            tune_count = results.get("tune_count", 0)
            invalidate_user_repertoire(request.user.id)

    else:
        search_form = SearchForm()

    if request.headers.get("Hx-Request"):
        return render(
            request,
            "tune/partials/_table_browse.html",
            {
                "tunes": tunes,
                "tune_count": tune_count,
                "user_tune_titles": user_tune_titles,
            },
        )

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
    """
    Take a public tune into a user's repertoire.
    """
    user = request.user
    admin_tune = get_object_or_404(RepertoireTune, pk=pk)
    rep_form = RepertoireTuneForm(request.POST)

    if admin_tune.player_id != settings.ADMIN_USER_ID:
        messages.error(request, "You can only take public tunes into your repertoire.")
        return render(request, "tune/browse.html")

    tune = admin_tune.tune

    tune.pk = None
    tune.created_by = user

    with transaction.atomic():
        tune.save()
        invalidate_user_repertoire(request.user.id)

    new_rep_tune = RepertoireTune.objects.create(tune=tune, player=request.user)

    # Change input backgrounds and accents to indigo because the default is orange-50, which is also the table row hover background
    for field_name, field in rep_form.fields.items():
        current_classes = field.widget.attrs.get("class", "")
        if field_name == "tags":
            new_classes = current_classes.replace(
                "accent-orange-100", "accent-indigo-100"
            )
            field.widget.attrs["class"] = new_classes
        else:
            new_classes = current_classes.replace("bg-orange-50", "bg-indigo-50")
            field.widget.attrs["class"] = new_classes

    return render(
        request,
        "tune/partials/_take.html",
        {"rep_form": rep_form, "tune": tune, "new_rep_tune": new_rep_tune},
    )


@login_required
def set_rep_fields(request, pk):
    """
    Set the knowledge, last_played, and tags of a public tune when a user takes it into their repertoire.
    """
    rep_tune = RepertoireTune.objects.get(pk=pk)
    rep_form = RepertoireTuneForm(request.POST)

    if rep_form.is_valid():
        rep_tune.knowledge = rep_form.cleaned_data["knowledge"]
        rep_tune.last_played = rep_form.cleaned_data["last_played"]
        rep_tune.tags.set(rep_form.cleaned_data["tags"])
        rep_tune.save()
    else:
        print("invalid")
        print(rep_form.errors)

    return render(request, "tune/partials/_taken.html", {"rep_form": rep_form})
