from .models import LoginConfig, GameConfig
from common import to_dict
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

CACHE_TIME = None


def _get_login_key(sid):
    return 'login' + str(sid)


def get_login_config(sid):
    key = _get_login_key(sid)
    data = cache.get(key)
    if not data:
        obj = LoginConfig.objects.get(loginid=sid)
        data = to_dict(obj)
        cache.set(key, data, CACHE_TIME)
    return data


def _clear_login_cache(sid):
    key = _get_login_key(sid)
    cache.delete(key)


def _get_game_key(sid):
    return 'game' + str(sid)


def get_game_config(sid):
    key = _get_game_key(sid)
    data = cache.get(key)
    if not data:
        try:
            obj = GameConfig.objects.get(serverid=sid)
            data = to_dict(obj, deep=False)
            cache.set(key, data, CACHE_TIME)
        except ObjectDoesNotExist:
            pass
    return data


def _clear_game_cache(sid):
    key = _get_game_key(sid)
    cache.delete(key)


def login_http_port(sid):
    return 9000 + (sid % 100) * 10 + 3


def world_http_port(sid):
    return 9000 + (sid % 100) * 10 + 8


def game_http_port(sid):
    return 10000 + (sid % 1000) * 10 + 3


def game_network_port(sid):
    return 10000 + (sid % 1000) * 10 + 2
