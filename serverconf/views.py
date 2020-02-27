from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from .models import WorldConfig, LoginConfig, GameConfig
from common import to_dict
# Create your views here.


def game_config(request, sid):
    gamelist = []
    objs = GameConfig.objects.all()
    for obj in objs:
        if obj.pk == sid:
            data = to_dict(obj)
        gamelist.append(to_dict(obj, fields=(
            'network_ip',
            'network_port',
            'id',
            'world',
            'login',
            'servername',
            'http_host',
            'status',
            'test',
            'arenaid',
            'trailnotice',
        ), deep=False))
    data['gamelist'] = gamelist
    return JsonResponse(data)


def login_config(request, sid):
    obj = LoginConfig.objects.get(pk=sid)
    data = to_dict(obj)
    return JsonResponse(data)


def world_config(request, sid):
    obj = WorldConfig.objects.get(pk=sid)
    data = to_dict(obj)
    return JsonResponse(data)

