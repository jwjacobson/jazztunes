from django.urls import path, include
from tune import views

urlpatterns = [
    path('', views.tune_list, name='tune_list'),
]