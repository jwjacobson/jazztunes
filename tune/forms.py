from django.forms import ModelForm
from .models import Tune

class TuneForm(ModelForm):
    class Meta:
        model = Tune