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

from django.db import models
from django.contrib.auth import get_user_model


# class Tag(models.Model):
#     name = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name


class Tune(models.Model):
    """
    The Tune is the heart of this app; each tune is one song that can be added to a user's repertoire and should contain all relevant musical information.
    """

    METERS = [(3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (0, "irregular")]

    STYLES = [("standard", "standard"), ("jazz", "jazz")]

    FORMS = [
        ("AABA", "AABA"),
        ("ABAC", "ABAC"),
        ("ABA", "ABA"),
        ("ABAB", "ABAB"),
        ("ABCD", "ABCD"),
        ("AB", "AB"),
        ("AAB", "AAB"),
        ("AABC", "AABC"),
        ("blues", "blues"),
        ("irregular", "irregular"),
    ]

    KEYS = {
        "c",
        "f",
        "bb",
        "eb",
        "ab",
        "db",
        "gb",
        "b",
        "e",
        "a",
        "d",
        "g",
        "a#",
        "d#",
        "g#",
        "c#",
        "f#",
        "c-",
        "f-",
        "bb-",
        "eb-",
        "ab-",
        "db-",
        "gb-",
        "b-",
        "e-",
        "a-",
        "d-",
        "g-",
        "a#-",
        "d#-",
        "g#-",
        "c#-",
        "f#-",
        "none",
        "atonal",
    }

    MAX_SEARCH_TERMS = 4

    NICKNAMES = {
        "bird": "Parker",
        "bud": "Powell",
        "miles": "Davis",
        "wayne": "Shorter",
        "joe": "Henderson",
        "lee": "Konitz",
        "diz": "Gillespie",
        "dizzy": "Gillespie",
        "duke": "Ellington",
        "sonny": "Rollins",
        "bill": "Evans",
        "herbie": "Hancock",
        "cedar": "Walton",
    }

    field_names = {"title", "composer", "key", "keys", "form", "style", "meter", "year"}

    title = models.CharField(max_length=90, help_text="The only required field")
    composer = models.CharField(max_length=30, blank=True)
    key = models.CharField(
        max_length=10,
        blank=True,
    )
    other_keys = models.CharField(
        max_length=20,
        blank=True,
    )
    song_form = models.CharField(choices=FORMS, max_length=15, blank=True)
    style = models.CharField(choices=STYLES, max_length=15, blank=True)
    meter = models.PositiveSmallIntegerField(choices=METERS, blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_contrafact = models.BooleanField(blank=True, null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )

    @property
    def decade(self):
        """
        Calculate the decade of composition based on the year of composition.
        """
        decade = f"{str(self.year)[2]}0s"
        return decade

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Tune {self.id} | {self.title}"


class RepertoireTune(models.Model):
    """
    RepertoireTune is the ManyToMany table connecting tunes to users ("players").
    It holds lots of essential data about a player's relationship to the tune,
    such as when it was last played or how well they know it.
    """

    KNOWLEDGES = [("know", "know"), ("learning", "learning"), ("don't know", "don't know")]

    tune = models.ForeignKey(Tune, on_delete=models.CASCADE)
    player = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    last_played = models.DateField(blank=True, null=True)
    knowledge = models.CharField(choices=KNOWLEDGES, max_length=15, default="know", blank=True)
    started_learning = models.DateTimeField(blank=True, null=True)
    play_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("tune", "player")

    def __str__(self):
        return f"{self.tune} | {self.player}"


# class Plays(models.Model):
