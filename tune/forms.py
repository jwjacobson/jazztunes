from django.forms import ModelForm
from .models import Tune
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class TuneForm(ModelForm):
    class Meta:
        model = Tune
        fields = [
            "title",
            "composer",
            "key",
            "other_keys",
            "song_form",
            "style",
            "meter",
            "year",
        ]

    def clean_key(self):
        """
        Check if the key entered is a real key and raise a ValidationError if it is not.
        """
        data = self.cleaned_data["key"]
        if data is not None and data.lower() not in Tune.KEYS:
            raise ValidationError(
                {_('Invalid key (all normal keys accepted plus "none" and "atonal").')}
            )
        return data.title()

    def clean_other_keys(self):
        """
        Check if the other keys entered are real keays and raise ValidationErrors if they are not.
        """
        data = self.cleaned_data["other_keys"]
        if data is not None:
            for other_key in data.split():
                if other_key.lower() not in Tune.KEYS:
                    raise ValidationError(_(f'"{other_key}" is not a valid key.'))
        return data
