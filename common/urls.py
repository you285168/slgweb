from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('cache/<str:key>', views.get_cache),
    path('clean/cache', views.clean_cache),
]