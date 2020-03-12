from django.core.cache import cache
from .models import ClientVersion
from django.core.exceptions import ObjectDoesNotExist


CACHE_TIME = 16 * 60


def _client_version_key(appid):
    return 'clientver:' + appid


def client_version(appid):
    key = _client_version_key(appid)
    data = cache.get(key)
    if not data:
        try:
            obj = ClientVersion.objects.get(appid=appid)
            cache.set(key, obj.version, CACHE_TIME)
            data = obj.version
        except ObjectDoesNotExist:
            data = ""
    return data


def clear_client_version_cache(appid):
    key = _client_version_key(appid)
    cache.delete(key)


def save_client_version(appid, version):
    try:
        obj = ClientVersion.objects.get(appid=appid)
        obj.version = version
        obj.save()
    except ObjectDoesNotExist:
        ClientVersion.objects.create(appid=appid, version=version)
