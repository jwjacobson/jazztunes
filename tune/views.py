import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Tune, RepertoireTune
from .forms import TuneForm


@login_required(login_url="/accounts/login/")
def tune_list(request):
    user = request.user
    rep_tunes = RepertoireTune.objects.filter(player=user)
    tunes = [rep_tune.rep_tune for rep_tune in rep_tunes]

    return render(request, "tune/list.html", {"tunes": tunes})


@login_required(login_url="/accounts/login/")
def tune_new(request):
    if request.method == "POST":
        form = TuneForm(request.POST)
        if form.is_valid():
            new_tune = form.save()
            RepertoireTune.objects.create(rep_tune=new_tune, player=request.user)
            messages.success(request, f"Added Tune {new_tune.id}: {new_tune.title}")
            # new_tune.players.add(request.user)

            return redirect("tune:tune_list")
    else:
        form = TuneForm()

    return render(request, "tune/form.html", {"form": form})


@login_required(login_url="/accounts/login/")
def tune_edit(request, pk):
    tune = get_object_or_404(Tune, pk=pk)
    form = TuneForm(request.POST or None, instance=tune)
    if form.is_valid():
        updated_tune = form.save()
        messages.success(
            request, f"Updated Tune {updated_tune.id}: {updated_tune.title}"
        )
        return redirect("tune:tune_list")

    return render(request, "tune/form.html", {"tune": tune, "form": form})


@login_required(login_url="/accounts/login/")
def tune_delete(request, pk):
    tune = get_object_or_404(Tune, pk=pk)

    if request.method == "POST":
        deleted_id, deleted_title = tune.id, tune.title
        tune.delete()
        messages.success(request, f"Deleted {deleted_id}: {deleted_title}")
        return redirect("tune:tune_list")

    return render(request, "tune/form.html", {"tune": tune})


@login_required(login_url="/accounts/login")
def tune_play(request):
    user = request.user
    rep_tunes = RepertoireTune.objects.filter(player=user)
    tunes = [rep_tune.rep_tune for rep_tune in rep_tunes]
    tune_to_play = random.choice(tunes)
    messages.success(request, f"You should play {tune_to_play.title}")

    return render(request, "tune/play.html")
