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
        Check if the key entered is a real key and raise a ValidationError if it is not;
        Properly format the key (title case)
        """
        data = self.cleaned_data["key"]
        if data and data.lower() not in Tune.KEYS:
            raise ValidationError(
                {_('Invalid key (all normal keys accepted plus "none" and "atonal").')}
            )
        return data.title()  # Title case formats the string like a proper key

    def clean_other_keys(self):
        """
        Check if the other keys entered are real keys and raise ValidationErrors if they are not;
        Properly format the keys (title case)
        """
        data = self.cleaned_data["other_keys"]
        if data:
            formatted_data = []
            for other_key in data.split():
                if other_key.lower() not in Tune.KEYS:
                    raise ValidationError(_(f'"{other_key}" is not a valid key.'))
                formatted_data.append(
                    other_key.title()
                )  # Title case formats the substring like a proper key
            data = " ".join(formatted_data)  # Convert the list back into a string
        return data
