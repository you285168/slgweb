from django.urls import path

from . import views

urlpatterns = [
    path('player/info', views.charge_player),
    path('xindong/pay', views.xindong_pay),
]