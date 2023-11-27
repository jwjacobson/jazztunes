from django.forms import ModelForm
from .models import Tune
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class TuneForm(ModelForm):
    class Meta:
        model = Tune
        fields = ['title', 'composer', 'key', 'other_keys', 'song_form', 'style', 'meter', 'year']

    def clean_key(self):
        keys = {'c', 'f', 'bb', 'eb', 'ab', 'db', 'gb', 'b', 'e', 'a', 'd', 'g', 'a#', 'd#', 'g#', 'c#', 'f#',
                'c-', 'f-', 'bb-', 'eb-', 'ab-', 'db-', 'gb-', 'b-', 'e-', 'a-', 'd-', 'g-', 'a#-', 'd#-', 'g#-', 'c#-', 'f#-',
                'none', 'atonal'}
        data = self.cleaned_data['key']
        if data.lower() not in keys:
            raise ValidationError(
                {_('Invalid key (all normal keys accepted plus "none" and "atonal").')}
                )
        return data
        
    def clean_other_keys(self):
        keys = {'c', 'f', 'bb', 'eb', 'ab', 'db', 'gb', 'b', 'e', 'a', 'd', 'g', 'a#', 'd#', 'g#', 'c#', 'f#',
                'c-', 'f-', 'bb-', 'eb-', 'ab-', 'db-', 'gb-', 'b-', 'e-', 'a-', 'd-', 'g-', 'a#-', 'd#-', 'g#-', 'c#-', 'f#-',
                'none', 'atonal'}
        data = self.cleaned_data['other_keys']
        for other_key in data.split():
            if other_key.lower() not in keys:
                raise ValidationError(
                _(f'"{other_key}" is not a valid key.')
                )
        return data