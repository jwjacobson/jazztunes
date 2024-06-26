# jazztunes -- A jazz repertoire management app
# Copyright (C) 2024 Jeff Jacobson <jeffjacobsonhimself@gmail.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.forms import ModelForm
from django import forms
from .models import Tune, RepertoireTune
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import timedelta


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
            # "tags",
        ]

    def __init__(self, *args, **kwargs):
        super(TuneForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean_key(self):
        """
        Check if the key entered is a real key and raise a ValidationError if it is not;
        Properly format the key (title case)
        """
        data = self.cleaned_data["key"]
        if data and data.lower() not in Tune.KEYS:
            raise ValidationError(
                'Invalid key (all normal keys accepted plus "none" and "atonal").'
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


class DateInput(forms.DateInput):
    input_type = "date"


class RepertoireTuneForm(ModelForm):
    class Meta:
        model = RepertoireTune
        exclude = ["tune", "player", "started_learning", "play_count"]
        widgets = {"last_played": DateInput(), "tags": forms.SelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(RepertoireTuneForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        instance = super(RepertoireTuneForm, self).save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            # breakpoint()
        return instance


class SearchForm(forms.Form):
    TIMES = [
        ("anytime", "anytime"),
        ("day", "a day"),
        ("week", "a week"),
        ("month", "a month"),
        ("two_months", "2 months"),
        ("three_months", "3 months"),
    ]

    search_term = forms.CharField(label="search_term", max_length=200, required=False)
    timespan = forms.ChoiceField(choices=TIMES, required=False)

    def clean_timespan(self):
        timespan = self.cleaned_data["timespan"]
        if timespan == "day":
            return timezone.now() - timedelta(days=1)
        elif timespan == "week":
            return timezone.now() - timedelta(days=7)
        elif timespan == "month":
            return timezone.now() - timedelta(days=30)
        elif timespan == "two_months":
            return timezone.now() - timedelta(days=60)
        elif timespan == "three_months":
            return timezone.now() - timedelta(days=90)
        else:
            return None
