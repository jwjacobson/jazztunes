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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.html import format_html

from .forms import TuneForm, RepertoireTuneForm, SearchForm, TakeForm, PlaySearchForm
from .helpers import suggest_a_key
from .models import Tune, RepertoireTune
from .repertoire import (
    get_user_repertoire,
    get_repertoire_queryset,
    invalidate_user_repertoire,
    play_tune,
    add_tune,
    take_tune,
    delete_tune,
    pick_random_tune,
    pick_next_tune,
)
from .search import query_tunes


def _empty_repertoire_warning(request):
    """Flash a warning with links to add tunes or browse public tunes."""
    add_url = reverse("jazztunes:tune_new")
    browse_url = reverse("jazztunes:tune_browse")
    messages.warning(
        request,
        format_html(
            'Your repertoire is empty. <a href="{}" class="font-medium text-blue-600 hover:text-blue-800 underline">Add some tunes</a> manually or <a href="{}" class="font-medium text-blue-600 hover:text-blue-800 underline">browse the public repertoire</a> for premade tunes!',
            add_url,
            browse_url,
        ),
    )


@login_required
def home(request):
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
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            search_term_string = " ".join(search_terms)
            timespan = search_form.cleaned_data["timespan"]

            tunes = query_tunes(
                get_repertoire_queryset(user), search_terms, timespan=timespan
            )
            tune_count = len(tunes)

            if not tune_count:
                messages.error(request, "No tunes match your search.")
        else:
            tunes = get_user_repertoire(user)
            tune_count = len(tunes)
    else:
        search_form = SearchForm()
        tunes = get_user_repertoire(user)
        tune_count = len(tunes)

        if tune_count == 0:
            _empty_repertoire_warning(request)

    if request.headers.get("Hx-Request"):
        return render(
            request,
            "jazztunes/partials/_table_home.html",
            {"tunes": tunes, "tune_count": tune_count, "possessive": possessive},
        )

    request.session["tune_count"] = tune_count
    return render(
        request,
        "jazztunes/home.html",
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
            request, "jazztunes/form.html", {"tune_form": tune_form, "rep_form": rep_form}
        )

    tune_form = TuneForm(request.POST)
    rep_form = RepertoireTuneForm(request.POST)

    if not tune_form.is_valid() or not rep_form.is_valid():
        return render(
            request, "jazztunes/form.html", {"tune_form": tune_form, "rep_form": rep_form}
        )

    with transaction.atomic():
        new_tune = tune_form.save(commit=False)
        new_tune.created_by = request.user
        new_tune.save()
        tune_form.save_m2m()

        add_tune(
            request.user,
            new_tune,
            knowledge=rep_form.cleaned_data["knowledge"],
            tags=rep_form.cleaned_data["tags"],
        )

    messages.success(request, f"{new_tune.title} has been added to your repertoire.")
    return redirect("jazztunes:home")


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
            invalidate_user_repertoire(request.user.id)

        messages.success(request, f"{updated_tune.title} has been updated.")
        return redirect("jazztunes:home")

    return render(
        request,
        "jazztunes/form.html",
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
        delete_tune(rep_tune)

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
        request, "jazztunes/partials/_delete_confirm.html", {"tune": tune, "row_id": row_id}
    )


@login_required
def recount(request):
    """
    Update the tune count that displays on the home and public pages.
    """
    tune_count = request.session["tune_count"]
    return render(request, "jazztunes/partials/_count.html", {"tune_count": tune_count})


@login_required
def get_random_tune(request):
    """
    Search the user's repertoire and select a random tune from the results.
    """
    search_form = PlaySearchForm(request.POST or None)
    if not search_form.is_valid():
        messages.error(request, "Invalid search")
        return render(request, "jazztunes/play.html")

    search_terms = search_form.cleaned_data["search_term"].split(" ")
    timespan = search_form.cleaned_data.get("timespan")
    suggest_key = search_form.cleaned_data.get("suggest_key")

    if len(search_terms) > Tune.MAX_SEARCH_TERMS:
        messages.error(
            request,
            f"Your query is too long ({len(search_terms)} terms, maximum of {Tune.MAX_SEARCH_TERMS}).",
        )
        return render(request, "jazztunes/play.html", {"search_form": search_form})

    tunes = query_tunes(
        get_repertoire_queryset(request.user), search_terms, timespan=timespan
    )

    selected_tune, remaining_ids = pick_random_tune(list(tunes))
    request.session["rep_tunes"] = remaining_ids

    if not selected_tune:
        messages.error(request, "No tunes match your search.")
        return render(request, "jazztunes/play.html", {"search_form": search_form})

    context = {"selected_tune": selected_tune}

    if suggest_key:
        suggested_key = suggest_a_key(
            selected_tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.ENHARMONICS
        )
        request.session["suggested_key"] = suggested_key
        request.session["suggest_key_enabled"] = True
        context["suggested_key"] = suggested_key
    else:
        request.session["suggested_key"] = None
        request.session["suggest_key_enabled"] = False

    request.session.save()
    return render(request, "jazztunes/partials/_play_card.html", context)


@login_required
def change_tune(request):
    """
    Select a different tune from the play search results if the previous one is rejected.
    """
    remaining_ids = request.session.get("rep_tunes", [])
    selected_tune, remaining_ids = pick_next_tune(remaining_ids)
    request.session["rep_tunes"] = remaining_ids

    if not selected_tune:
        return render(request, "jazztunes/partials/_play_card.html", {"selected_tune": None})

    context = {"selected_tune": selected_tune}

    if request.session.get("suggest_key_enabled"):
        suggested_key = suggest_a_key(
            selected_tune, PlaySearchForm.NORMAL_KEYS, PlaySearchForm.ENHARMONICS
        )
        request.session["suggested_key"] = suggested_key
        context["suggested_key"] = suggested_key

    request.session.save()
    return render(request, "jazztunes/partials/_play_card.html", context)


@login_required
def play(request, pk):
    """
    Record that a tune was played.
    """
    url_name = request.resolver_match.url_name

    rep_tune = get_object_or_404(RepertoireTune, id=pk, player=request.user)
    play_obj = play_tune(rep_tune)

    context = {"last_played": play_obj.played_at, "selected_tune": rep_tune}

    if url_name == "play_play":
        return render(request, "jazztunes/partials/_another_button.html", context)

    templates = {
        "play_home": "jazztunes/partials/_play_home.html",
        "play_play": "jazztunes/partials/_play_play.html",
    }
    return render(request, templates.get(url_name, "/"), context)


@login_required
def tune_play(request):
    """
    Load the play page.
    """
    search_form = PlaySearchForm()
    tunes = get_user_repertoire(request.user)

    if not tunes:
        _empty_repertoire_warning(request)

    return render(request, "jazztunes/play.html", {"search_form": search_form})


@login_required
def tune_browse(request):
    """
    Show the public page of preloaded tunes.
    """
    user = request.user
    user_tune_titles = {tune.tune.title for tune in get_user_repertoire(user)}
    admin_user = User.objects.get(id=settings.ADMIN_USER_ID)

    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_terms = search_form.cleaned_data["search_term"].split(" ")
            tunes = query_tunes(get_repertoire_queryset(admin_user), search_terms)
            tune_count = len(tunes)

            if not tune_count:
                messages.error(request, "No tunes match your search.")
        else:
            tunes = get_user_repertoire(admin_user)
            tune_count = len(tunes)
    else:
        search_form = SearchForm()
        tunes = get_user_repertoire(admin_user)
        tune_count = len(tunes)

    if request.headers.get("Hx-Request"):
        return render(
            request,
            "jazztunes/partials/_table_browse.html",
            {
                "tunes": tunes,
                "tune_count": tune_count,
                "user_tune_titles": user_tune_titles,
            },
        )

    return render(
        request,
        "jazztunes/browse.html",
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
    admin_tune = get_object_or_404(RepertoireTune, pk=pk)
    rep_form = TakeForm(request.POST)

    if admin_tune.player_id != settings.ADMIN_USER_ID:
        messages.error(request, "You can only take public tunes into your repertoire.")
        return render(request, "jazztunes/browse.html")

    with transaction.atomic():
        tune, new_rep_tune = take_tune(request.user, admin_tune)

    return render(
        request,
        "jazztunes/partials/_take.html",
        {"rep_form": rep_form, "tune": tune, "new_rep_tune": new_rep_tune},
    )


@login_required
def set_rep_fields(request, pk):
    """
    Set the knowledge and tags of a tune when a user takes it into their repertoire.
    """
    rep_tune = RepertoireTune.objects.get(pk=pk)
    rep_form = RepertoireTuneForm(request.POST)

    if rep_form.is_valid():
        rep_tune.knowledge = rep_form.cleaned_data["knowledge"]
        rep_tune.tags.set(rep_form.cleaned_data["tags"])
        with transaction.atomic():
            rep_tune.save()
            invalidate_user_repertoire(request.user.id)

    return render(request, "jazztunes/partials/_taken.html", {"rep_form": rep_form})
