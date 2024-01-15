from django.forms import ModelForm
from django import forms
from .models import Tune, RepertoireTune
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
        return data.title()

    def clean_other_keys(self):
        """
        Check if the other keys entered are real keys and raise ValidationErrors if they are not;
        Properly format the keys (title case)
        """
        data = self.cleaned_data["other_keys"]
        if data is None:
            return data
        formatted_data = []
        for other_key in data.split():
            if other_key.lower() not in Tune.KEYS:
                raise ValidationError(_(f'"{other_key}" is not a valid key.'))
            formatted_data.append(other_key.title())
        data = " ".join(formatted_data)
        return data


class RepertoireTuneForm(ModelForm):
    class Meta:
        model = RepertoireTune
        exclude = ["tune", "player", "last_played", "started_learning"]


class SearchForm(forms.Form):
    TIMES = [("day", "Last day"), ("week", "Last week"), ("month", "Last month")]

    search_term = forms.CharField(label="search_term", max_length=200)
    timespan = forms.ChoiceField(choices=TIMES, required=False)


class PlayForm(forms.Form):
    matching_tunes = forms.ModelMultipleChoiceField(
        queryset=RepertoireTune.objects.none(), widget=forms.HiddenInput(), required=False
    )
    suggested_tune = forms.ModelChoiceField(
        queryset=RepertoireTune.objects.all(), widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        matching_tunes_queryset = kwargs.pop("matching_tunes_queryset", None)
        super(PlayForm, self).__init__(*args, **kwargs)

        if matching_tunes_queryset is not None:
            self.fields["matching_tunes"].queryset = matching_tunes_queryset
