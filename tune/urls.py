from django.urls import path
from tune import views

app_name = "tune"

urlpatterns = [
    path("", views.tune_list, name="tune_list"),
    path("new", views.tune_new, name="tune_new"),
    path("edit/<int:pk>", views.tune_edit, name="tune_edit"),
    path("delete/<int:pk>", views.tune_delete, name="tune_delete"),
    path("play", views.tune_play, name="tune_play"),
    path("change", views.change_tune, name="change_tune"),
    path("search", views.search, name="search"),
    path("browse", views.tune_browse, name="tune_browse"),
    path("take/<int:pk>", views.tune_take, name="tune_take"),
    path("play/<int:pk>", views.play, name="play"),
]
