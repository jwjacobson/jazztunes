from django.contrib import admin
from tune.models import Tune


@admin.register(Tune)
class TuneAdmin(admin.ModelAdmin):
    display_fields = ["title"]
