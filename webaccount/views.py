from django.shortcuts import render
from django.http.response import JsonResponse
from django.http import HttpResponse
from .platform import platform_verify, FEIYU_KEY
import logging
from .account import *
from common import get_client_ip, md5_sign, get_country_code, create_uuid
import time
from .models import WebAccount
import requests
from serverconf.interface import get_login_config, login_http_port, get_game_config

logger = logging.getLogger('wasteland')
LOGIN_ID = 1

# Create your views here.


def account_test(request):
    uid = request.GET.get('account', None)
    obj = WebAccount.objects.get(uid=uid)
    platform = 'feiyu'
    setattr(obj, platform, '123')
    obj.save()
    return HttpResponse('')


def server_user_login(request):
    pass


def bind_account(request):
    """绑定帐号"""
    uid = request.GET.get('account', None)
    platform = request.GET.get('platform', None)
    signture = request.GET.get('signture', None)
    email = request.GET.get('email', None)

    while True:
        key = platform_verify(platform, signture, None, email)
        if not key:
            code = 3
            break
        objs = WebAccount.objects.filter(uid=uid)
        if len(objs) == 0:
            code = 4
            break
        obj = objs[0]
        if getattr(obj, platform, '') != '':
            code = 2
            break
        temp = get_cache_account(**{
            platform: key,
        })
        if temp:
            code = 5
            break
        setattr(obj, platform, key)
        obj.save()
        code = 1
        clear_account_cache(obj)
        break
    # code：1成功，2已经绑定过，3错误的平台token，4没有找到玩家, 5平台帐号已经被绑定
    return HttpResponse(code)


def user_login(request):
    """玩家请求要登录的服务器"""
    device = request.GET.get('device', None)
    platform = request.GET.get('platform', None)
    signture = request.GET.get('signture', None)
    email = request.GET.get('email', None)
    clientos = request.GET.get('clientos', None)
    subplatform = request.GET.get('subplatform', None)
    ip = get_client_ip(request)

    code = 0
    result = None
    ret = None
    if platform == 'nil':
        platform = None
    while True:
        if is_lock_ip(ip):
            code = 5
            break
        platformkey = None
        if not device and not platform:
            code = 1
            break
        if platform:
            platformkey = platform_verify(platform, signture, subplatform, email)
            if not platformkey:
                code = 2
                break
        result = get_account_info(device, platform, platformkey, subplatform)
        break
    if result:
        if is_lock_account(result['uid']):
            code = 6
        else:
            ret = _get_account_server(result['uid'], clientos, get_country_code(ip))
            curtime = int(time.time())
            ret.update({
                'bind': result['platform'],
                'account': result['uid'],
                'datetime': curtime,
                'sign': md5_sign({'account': result['uid'], 'datetime': curtime}, FEIYU_KEY)
            })
    if not ret:
        ret = {}
    ret.update({
        'code': code,
        'platform': platform,
    })
    '''code：0成功，1没有设备号，2平台验证失败，3不识别平台，4服务器繁忙，5ip被封，6账号被封'''
    return JsonResponse(ret)


def _get_account_server(account, clientos, country):
    login = get_login_config(LOGIN_ID)
    '''
    res = requests.get('http//{0}:{1}'.format(login['http_host'], login_http_port(login['id'])), params={
        'account': account,
        'clientos': clientos,
        'country': country,
    })
    sid = int(res.content)
    '''
    sid = get_last_sid(account)
    game = get_game_config(sid)
    return {
        'serverid': game['id'],
        'ip': login['network_ip'],
        'port': login['network_port'],
        'status': game['status'],
    }
