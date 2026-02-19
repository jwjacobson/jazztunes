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


from django.urls import path
from jazztunes import views
from jazztunes import views_analytics

app_name = "jazztunes"

urlpatterns = [
    path("", views.home, name="home"),
    path("new", views.tune_new, name="tune_new"),
    path("edit/<int:pk>", views.tune_edit, name="tune_edit"),
    path(
        "tune/<int:pk>/delete/confirm/",
        views.tune_delete_confirm,
        name="tune_delete_confirm",
    ),
    path("delete/<int:pk>", views.tune_delete, name="tune_delete"),
    path("play", views.tune_play, name="tune_play"),
    path("change", views.change_tune, name="change_tune"),
    path("random", views.get_random_tune, name="get_random_tune"),
    path("browse", views.tune_browse, name="tune_browse"),
    path("take/<int:pk>", views.tune_take, name="tune_take"),
    path("play/home/<int:pk>", views.play, name="play_home"),
    path("play/play/<int:pk>", views.play, name="play_play"),
    path("set/<int:pk>", views.set_rep_fields, name="set_rep_fields"),
    path("count", views.recount, name="recount"),
    # Analytics
    path("analytics/", views.analytics_home, name="analytics"),
    path("analytics/refresh/", views.analytics_refresh, name="analytics_refresh"),
]
