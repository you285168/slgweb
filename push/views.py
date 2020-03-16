from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import PushDevice
from django.core.cache import cache
import json
import requests
import logging
from webaccount.account import get_account_device
from django.conf import settings

# Create your views here.

logger = logging.getLogger('wasteland')

PUSH_KEY = "push:"      #push cache key
CACHE_TIME = 15 * 60    #push cache time
PUSH_LIMIT = 500    #单次推送上限
PUSH_KEY = "AAAAST_4tL8:APA91bGU9J7zEqb8vlfiHov3Q0sXTSkz0XOzfIScC5zH1htV3SZw6DrRK-e-yg2HG6lLCZrzmLpWEuVhMHk" \
           "ot2mPRlGYxHhOXoGuw0rxcAs1xwuygZgRH3LIXyPyAHFIClyYosG1cVGY"
PUSH_LANGUAGE = {       #推送语言
    "us": "En",
    "zh": "Ch",
    "en": "En",
    "cn": "Ch",
    'tw': "Ch_T",
    "zh-Hans-CN": "Ch",
    "zh_Hant_TW": "Ch_T",
    "zh-TW": "Ch_T",
    "zh-HK": "Ch_T",
    "de": "De",        #德语
    "jp": "Jp",        #日语
    "kr": "Kr",        #韩语
    "th": "Th",        #泰国
    "vi": "Vh",        #越南
    "tr": "Tr",        #土耳其语
    "es": "Es",        #西班牙语
    "ru": "Ru",        #俄语
    "fr": "Fr",        #法语
    "pt": "Pt",        #葡萄牙语
    "id": "Id",        #印尼语
}


def _get_push_key(device):
    return (PUSH_KEY + device).replace(' ', '_')


def _get_cache_device(device):
    push_key = _get_push_key(device)
    return cache.get(push_key)


def _set_cache_device(obj):
    push_key = _get_push_key(obj.device)
    cache.set(push_key, {
        'device': obj.device,
        'token': obj.token,
        'serverid': obj.serverid,
        'language': obj.language,
    }, CACHE_TIME)


def _remove_cache_device(device):
    push_key = _get_push_key(device)
    cache.delete(push_key)


def register_push(request):
    token = request.GET.get('d_regid', None)
    language = request.GET.get('d_language', None)
    if not language:
        language = 'us'
    # 区分安卓 / IOS
    sid = request.GET.get('d_ios_server_id', None)
    if sid:
        device = request.GET.get('d_ios_id', None)
    else:
        sid = request.GET.get('d_android_server_id', None)
        device = request.GET.get('d_android_id', None)
    code = 1
    if token and device and len(token) > 20:
        data = _get_cache_device(device)
        if not data or data['token'] != token or data['serverid'] != sid or data['language'] != language:
            try:
                obj = PushDevice.objects.get(device=device)
            except ObjectDoesNotExist:
                obj = PushDevice(device=device)
            obj.token = token
            obj.serverid = sid
            obj.language = language
            obj.save()
            _set_cache_device(obj)
        code = 0
    return HttpResponse(code)


def unregister_push(request):
    code = 1
    device = request.GET.get('d_ios_id', None)
    if not device:
        device = request.GET.get('d_android_id', None)
    if device:
        _remove_cache_device(device)
        PushDevice.objects.filter(device=device).delete()
        code = 0
    return HttpResponse(code)


def _get_cache_tokens(sid, devices):
    result = []
    if len(devices) == 1:
        # 针对单人的进行cache缓存
        device = devices[0]
        data = _get_cache_device(device)
        if data:
            result.append(data)
            devices.clear()
    if len(devices) <= 0:
        return result
    temp = PushDevice.objects.filter(serverid=sid, device__in=devices)
    for obj in temp:
        _set_cache_device(obj)
        result.append(obj)
    return result


def test_push(request):
    obj = PushDevice(device='gjg')
    device = obj['device']
    return HttpResponse(device)


def broadcast_push(request):
    code = 0
    while True:
        accounts = request.POST.get('accounts', None)
        if accounts:
            accounts = json.loads(accounts)
        package = request.POST.get('package', None)
        if package:
            package = json.loads(package)
        excludes = request.POST.get('excludes', None)
        if excludes:
            excludes = json.loads(excludes)
        broadcast = request.POST.get('allflag', None)
        sid = request.POST.get('serverid', None)
        result = None
        if broadcast:
            if excludes and len(excludes) > 0:
                devices = get_account_device(excludes)
                result = PushDevice.objects.filter(serverid=sid).exclude(device__in=devices)
            else:
                result = PushDevice.objects.filter(serverid=sid)
        elif accounts and len(accounts) > 0:
            devices = get_account_device(accounts)
            result = _get_cache_tokens(sid, devices)
        else:
            code = 2
            break
        if not result or len(result) <= 0:
            code = 3
            break
        tokens = {}
        for obj in result:
            lan_key = 'En'
            if obj['language'] in PUSH_LANGUAGE:
                lan_key = PUSH_LANGUAGE[obj['language']]
            if lan_key not in tokens:
                tokens[lan_key] = {}
            tokens[lan_key][obj['device']] = obj['token']
        for key, value in tokens.items():
            title = package['Name' + key]
            text = package['Text' + key]
            push_type = package['type']
            _push_message(title, text, push_type, value)
        break
    return HttpResponse(code)


def _push_message(title, text, push_type, tokens):
    push_token = []
    for device, token in tokens.items():
        push_token.append(token)
        if len(push_token) >= PUSH_LIMIT:
            _raw_push_message(push_token, title, text, push_type)
            push_token.clear()
    if len(push_token) > 0:
        _raw_push_message(push_token, title, text, push_type)


def _raw_push_message(push_token, title, text, push_type):
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': 'key=' + PUSH_KEY,
        'Content-Type': 'application/json',
    }
    proxies = settings.REQUEST_PROXIES
    data = {
        'registration_ids': push_token,
        'data': {  # android
            'message': text,
            'title': title,
            'type': push_type,
        },
        'notification': {  # ios
            'body': text,
            'title': title,
            'sound': 'default',
        },
    }
    try:
        res = requests.post(url, json=data, headers=headers, proxies=proxies)
        logger.warning('push message ret: {0}'.format(res.content))
    except Exception as e:
        logger.warning(str(e))
