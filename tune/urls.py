from django.urls import path, include
from tune import views

urlpatterns = [
    path('', tune_list),
]