from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from .models import Tune
from .forms import TuneForm

def tune_list(request):
    tunes = Tune.objects.all()

    return render(request,
                 'tune/list.html',
                 {'tunes': tunes})

# def blog_detail(request, pk):
#     post = get_object_or_404(Blog, pk=pk)
#     return render(request, 'blog/detail.html', {'post': post})

def tune_new(request):
    form = TuneForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Added tune')
        return redirect('tune:tune_list')
    return render(request, 'tune/form.html', {'form': form})


def tune_edit(request, pk):
    tune = get_object_or_404(Tune, pk=pk)
    form = TuneForm(request.POST or None, instance=tune)
    if form.is_valid():
        form.save()
        messages.success(request, 'Updated tune')
        return redirect('tune:tune_list')

    return render(request, 'tune/form.html', {'tune': tune,
                                              'form': form})


def tune_delete(request, pk):
    tune = get_object_or_404(Tune, pk=pk)

    if request.method == 'POST':
        tune.delete()
        messages.success(request, 'Deleted tune')
        return redirect('tune:tune_list')

    return render(request, 'tune/delete.html', {'tune': tune})


