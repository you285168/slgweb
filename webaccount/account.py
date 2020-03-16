from django.core.cache import cache
from .models import WebAccount
from django.forms.models import model_to_dict
from .platform import PLATFORM
from common import create_uuid


CACHE_TIME = 30 * 60
LOCK_IP = 'lockip'          #
LOCK_USER = 'lockuser'      #
LOCK_TIME = None


def get_account_device(accounts):
    devices = []
    if len(accounts) == 1:
        # 针对单人的进行cache缓存
        uid = accounts[0]
        data = get_cache_account(uid=uid)
        if data:
            device = data.get('lastdevice', '')
            if device == '':
                device = data.get('device', '')
            if device != '':
                devices.append(device)
    else:
        objs = WebAccount.objects.filter(uid__in=accounts)
        for obj in objs:
            if obj.lastdevice and obj.lastdevice != '':
                devices.append(obj.lastdevice)
            elif obj.device and obj.device != '':
                devices.append(obj.device)
    return devices


def clear_account_cache(obj):
    param = ['uid', 'device']
    param[2:] = iter(PLATFORM)
    keys = {k: v for k, v in model_to_dict(obj, fields=param).items() if v and len(v) > 0}
    for key, value in keys.items():
        cachekey = (key + value).replace(' ', '_')
        cache.delete(cachekey)


def get_account_info(device, platform, key, subplatform):
    if platform:
        data = get_cache_account(**{
            platform: key,
        })
    else:
        data = get_cache_account(device=device)
    if not data:
        params = {}
        if platform:
            params[platform] = key
        else:
            params['device'] = device
        if subplatform:
            params['subplatform'] = subplatform
        params['uid'] = create_uuid()
        obj = WebAccount.objects.create(**params)
        data = _get_account_detail(obj)
    else:
        if data['lastdevice'] != device:
            obj = WebAccount.objects.get(uid=data['uid'])
            obj.lastdevice = device
            obj.save()
    return data


def _get_account_detail(obj):
    ret = model_to_dict(obj, exclude=PLATFORM)
    ret['platform'] = {k: v for k, v in model_to_dict(obj, fields=PLATFORM).items() if v and str(v) != ''}
    return ret


def get_cache_account(**kwargs):
    for key, value in kwargs.items():
        cachekey = (key + str(value)).replace(' ', '_')
        break
    data = cache.get(cachekey)
    if not data:
        objs = WebAccount.objects.filter(**kwargs)
        if len(objs) > 0:
            data = _get_account_detail(objs[0])
            cache.set(cachekey, data, CACHE_TIME)
    return data


def is_lock_ip(ip):
    ips = get_lock_ip()
    if ips:
        return ip in ips


def get_lock_ip():
    return cache.get(LOCK_IP)


def add_lock_ip(ip):
    ips = get_lock_ip() or set()
    ips.add(ip)
    cache.set(LOCK_IP, ips, LOCK_TIME)


def del_lock_ip(ip):
    ips = get_lock_ip()
    if ips and ip in ips:
        ips.remove(ip)
        if len(ips) <= 0:
            cache.delete(LOCK_IP)
        else:
            cache.set(LOCK_IP, ips, LOCK_TIME)
