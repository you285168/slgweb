from django.urls import path

from . import views

urlpatterns = [
    path('feiyu/pay', views.feiyu_pay),
    path('player/info', views.charge_player_info),
    path('xindong/pay', views.xindong_pay),
]