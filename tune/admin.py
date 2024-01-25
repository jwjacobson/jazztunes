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
    search_fields = ('name',)