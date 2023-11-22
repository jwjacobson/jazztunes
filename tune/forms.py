from django.forms import ModelForm
from .models import Tune

class TuneForm(ModelForm):
    class Meta:
        model = Tune
        fields = ['title', 'composer', 'key', 'other_keys', 'song_form', 'style', 'meter', 'year']