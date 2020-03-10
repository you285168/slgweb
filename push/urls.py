from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_push),
    path('unregister', views.unregister_push),
    path('broadcast', views.broadcast_push),
    path('test', views.test_push),
]