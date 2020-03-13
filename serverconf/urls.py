from django.urls import path

from . import views

urlpatterns = [
    path('game', views.game_config),
    path('login', views.login_config),
    path('world', views.world_config),
]