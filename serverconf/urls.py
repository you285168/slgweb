from django.urls import path

from . import views

urlpatterns = [
    path('game/<int:sid>/', views.game_config),
    path('login', views.login_config),
    path('world', views.world_config),
]