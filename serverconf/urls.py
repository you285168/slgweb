from django.urls import path

from . import views

urlpatterns = [
    path('game/<int:sid>/', views.game_config),
    path('login/<int:sid>/', views.login_config),
    path('world/<int:sid>/', views.world_config),
]