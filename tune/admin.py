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


from django.contrib import admin
from tune.models import Tune, RepertoireTune, Tag


@admin.register(Tune)
class TuneAdmin(admin.ModelAdmin):
    list_display = ["title", "composer", "key"]
    search_fields = ("title",)
    list_filter = ("song_form", "style")


@admin.register(RepertoireTune)
class RepertoireTuneAdmin(admin.ModelAdmin):
    list_display = ["tune", "player", "last_played", "knowledge"]
    search_fields = ("tune__title", "player__username")
    autocomplete_fields = ("tune", "player")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ("name",)
