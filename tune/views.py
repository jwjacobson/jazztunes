from django.shortcuts import render
from tune.models import Tune

def tune_list(request):
    tunes = Tune.objects.all()

    return render(request,
                 'tune/list.html',
                 {'tunes': tunes})