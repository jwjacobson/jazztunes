from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Tune, RepertoireTune
from .forms import TuneForm, RepertoireTuneForm


@login_required(login_url="/accounts/login/")
def tune_list(request):
    user = request.user
    rep_tunes = RepertoireTune.objects.filter(player=user)
    tunes = [tune.tune for tune in rep_tunes]

    return render(request, "tune/list.html", {"tunes": tunes})


@login_required(login_url="/accounts/login/")
def tune_new(request):
    if request.method == "POST":
        tune_form = TuneForm(request.POST)
        rep_form = RepertoireTuneForm(request.POST)
        if tune_form.is_valid():
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
    form = TuneForm(request.POST or None, instance=tune)
    if form.is_valid():
        updated_tune = form.save()
        messages.success(request, f"Updated Tune {updated_tune.id}: {updated_tune.title}")
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
    rep_tune_to_play = RepertoireTune.objects.filter(player=user).order_by("?").first()
    rep_tune_to_play.last_played = timezone.now()
    rep_tune_to_play.save()

    return render(request, "tune/play.html", {"rep_tune_to_play": rep_tune_to_play})
