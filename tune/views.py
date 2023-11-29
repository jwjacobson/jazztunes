from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Tune
from .forms import TuneForm

@login_required(login_url="/accounts/login/")
def tune_list(request):
    tunes = Tune.objects.all()

    return render(request,
                 'tune/list.html',
                 {'tunes': tunes})

@login_required(login_url="/accounts/login/")
def tune_new(request):
    if request.method == "POST":
        form = TuneForm(request.POST)
        if form.is_valid():
            new_tune = form.save()
            messages.success(request, f'Added Tune {new_tune.id}: {new_tune.title}')
            return redirect('tune:tune_list')
    else:
        form = TuneForm()

    return render(request, 'tune/form.html', {'form': form})

@login_required(login_url="/accounts/login/")
def tune_edit(request, pk):
    tune = get_object_or_404(Tune, pk=pk)
    form = TuneForm(request.POST or None, instance=tune)
    if form.is_valid():
        form.save()
        messages.success(request, 'Updated tune')
        return redirect('tune:tune_list')

    return render(request, 'tune/form.html', {'tune': tune,
                                              'form': form})


@login_required(login_url="/accounts/login/")
def tune_delete(request, pk):
    tune = get_object_or_404(Tune, pk=pk)

    if request.method == 'POST':
        tune.delete()
        messages.success(request, 'Deleted tune')
        return redirect('tune:tune_list')

    return render(request, 'tune/delete.html', {'tune': tune})


