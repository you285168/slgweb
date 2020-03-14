from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from .models import WorldConfig, LoginConfig, GameConfig, DBConfig
from common import to_dict
from django.forms.models import model_to_dict
from wasteland import LOGIN_ID
from .interface import get_login_config
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def game_config(request):
    sid = int(request.GET.get('serverid'))
    gamelist = {}
    objs = GameConfig.objects.all()
    for obj in objs:
        if obj.serverid == sid:
            data = to_dict(obj, exclude=('id',))
        gamelist[obj.serverid] = to_dict(obj, fields=(
            'network_ip',
            'network_port',
            'serverid',
            'world',
            'login',
            'servername',
            'http_host',
            'status',
            'test',
            'arenaid',
            'trailnotice',
            'heroarena',
            'warbanner',
        ), deep=False)
    data['gamelist'] = gamelist
    return JsonResponse(data)


def login_config(request):
    sid = request.GET.get('loginid', None)
    obj = LoginConfig.objects.get(loginid=sid)
    data = to_dict(obj, exclude=('id',))
    return JsonResponse(data)


def world_config(request):
    sid = request.GET.get('worldid', None)
    obj = WorldConfig.objects.get(worldid=sid)
    data = to_dict(obj, exclude=('id',))
    return JsonResponse(data)


def all_server_dbconfig(request):
    ret = {
        'globallist': {},
    }
    objs = GameConfig.objects.all()
    for obj in objs:
        ret['globallist'][obj.pk] = model_to_dict(obj.dbc_global)
    login = get_login_config(LOGIN_ID)
    ret['playerlist'] = login['dbc_player']
    return JsonResponse(ret)


def _get_game_data(obj):
    data = to_dict(obj, exclude=('id',))
    data['worldid'] = data['world']['worldid']
    data['loginid'] = data['login']['loginid']
    data['gate'] = {
        'network_ip': data['network_ip'],
        'network_port': data['network_port'],
    }
    data.pop('world')
    data.pop('login')
    return data


def get_game_list(request):
    sid = request.GET.get('serverid', None)
    ret = []
    if not sid:
        objs = GameConfig.objects.all()
        for obj in objs:
            ret.append(_get_game_data(obj))
    else:
        try:
            obj = GameConfig.objects.get(serverid=sid)
            ret.append(_get_game_data(obj))
        except ObjectDoesNotExist:
            pass
    return JsonResponse(ret, safe=False)


def update_game_server(request):
    code = 1
    sid = request.GET.get('serverid')
    if sid:
        try:
            obj = GameConfig.objects.get(serverid=sid)
            for key, value in request.GET.items():
                if key != 'serverid':
                    setattr(obj, key, value)
            obj.save()
            code = 0
        except ObjectDoesNotExist:
            pass
    return HttpResponse(code)
