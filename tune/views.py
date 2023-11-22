from django.shortcuts import render

def tune_list(request):
    tunes = Tune.objects.all()

    return render(request,
                 'tune/list.html',
                 {'tunes': tunes})