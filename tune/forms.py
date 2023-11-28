from django.forms import ModelForm
from .models import Tune
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class TuneForm(ModelForm):
    class Meta:
        model = Tune
        fields = ['title', 'composer', 'key', 'other_keys', 'song_form', 'style', 'meter', 'year']

    def clean_key(self):
        data = self.cleaned_data['key']
        if data.lower() not in Tune.KEYS:
            raise ValidationError(
                {_('Invalid key (all normal keys accepted plus "none" and "atonal").')}
                )
        return data
        
    def clean_other_keys(self):
        data = self.cleaned_data['other_keys']
        for other_key in data.split():
            if other_key.lower() not in Tune.KEYS:
                raise ValidationError(
                _(f'"{other_key}" is not a valid key.')
                )
        return data