from django.contrib import admin
from tune.models import Tune, RepertoireTune


@admin.register(Tune)
class TuneAdmin(admin.ModelAdmin):
    list_display = ["title", "composer", "key"]


@admin.register(RepertoireTune)
class RepertoireTuneAdmin(admin.ModelAdmin):
    list_display = ["tune", "player", "last_played", "knowledge"]
