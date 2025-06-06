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

from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import Tune, RepertoireTune


class BaseForm:
    """Base form mixin that applies consistent Tailwind styling to all form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = "w-full px-3 py-2 bg-orange-50 border border-black focus:outline-none focus:ring focus:ring-indigo-400"
        select_classes = "w-full px-3 py-2.5 bg-orange-50 border border-black focus:outline-none focus:ring focus:ring-indigo-400"

        for field_name, field in self.fields.items():
            if field_name in getattr(self, "exclude_styling", []):
                continue

            if (
                hasattr(field.widget, "choices")
                or "Select" in field.widget.__class__.__name__
            ):
                field.widget.attrs["class"] = select_classes
            else:
                field.widget.attrs["class"] = input_classes


class TuneForm(BaseForm, ModelForm):
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


class RepertoireTuneForm(BaseForm, ModelForm):
    exclude_styling = ["tags"]

    class Meta:
        model = RepertoireTune
        exclude = ["tune", "player", "started_learning", "play_count"]
        widgets = {"last_played": DateInput(), "tags": forms.CheckboxSelectMultiple()}

    def save(self, commit=True):
        instance = super(RepertoireTuneForm, self).save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SearchForm(BaseForm, forms.Form):
    TIMES = [
        ("anytime", "n/a"),
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
