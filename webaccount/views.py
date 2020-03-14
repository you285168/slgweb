from django.shortcuts import render
from django.http.response import JsonResponse
from django.http import HttpResponse
from .platform import platform_verify, FEIYU_KEY
import logging
from .account import *
from common import get_client_ip, md5_sign, get_country_code, get_country_weight, random_weight
import time
from .models import WebAccount
from django.core.exceptions import ObjectDoesNotExist
import requests
from serverconf.interface import get_login_config, login_http_port, get_game_config, game_http_port
from charge.views import request_charge
from wasteland import LOGIN_ID
import json
import time


# Create your views here.
logger = logging.getLogger('wasteland')
TAP_DB = [
    # "ds1vsnkc1pp9cdyc",     #全球包
    # "jkhup69o5huy7cnx",     #台湾包
    # "qoggr1neujjacw0t",     #taptap包
]


def account_test(request):
    uid = request.GET.get('account', None)
    obj = WebAccount.objects.get(uid=uid)
    platform = 'feiyu'
    setattr(obj, platform, '123')
    obj.save()
    return HttpResponse('')


def enter_game(request):
    uid = request.GET.get('account', None)
    sid = request.GET.get('serverid', None)
    playerid = request.GET.get('playerid', None)
    name = request.GET.get('name', None)
    data = get_cache_account(uid=uid)
    platform = {}
    if data:
        server = get_game_config(sid)
        if server and ('test' not in server or not server['test']):
            if data['lastserver'] != sid or data['playerid'] != playerid or data['name'] != name:
                obj = WebAccount.objects.get(uid=uid)
                obj.lastserver = sid
                obj.playerid = playerid
                obj.name = name
                obj.save()
        platform = data['platform']
        request_charge(sid, uid)
    return JsonResponse(platform)


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
        try:
            obj = WebAccount.objects.get(uid=uid)
        except ObjectDoesNotExist:
            obj = None
        if not obj:
            code = 4
            break
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
    idcard = ''
    minor = False
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
            platformkey, idcard, minor = platform_verify(platform, signture, subplatform, email)
            if not platformkey:
                code = 2
                break
        result = get_account_info(device, platform, platformkey, subplatform)
        break
    if result:
        if result['lock']:
            code = 6
        else:
            ret = _get_account_server(result['uid'], result.get('login', LOGIN_ID), result.get('lastserver', 0), get_country_code(ip))
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
        'idcard': idcard,
        'minor': minor,
    })
    '''code：0成功，1没有设备号，2平台验证失败，3不识别平台，4服务器繁忙，5ip被封，6账号被封'''
    return JsonResponse(ret)


def _get_account_server(account, loginid, sid, country):
    login = get_login_config(loginid)
    if sid == 0:
        res = requests.get('http://{0}:{1}/last_server'.format(login['http_host'], login_http_port(login['loginid'])), params={
            'account': account,
        })
        if res.status_code == requests.codes.ok:
            sid = int(res.text)
    if sid == 0:
        pool = get_country_weight(country)
        if len(pool) > 0:
            sid = random_weight(pool)
    game = get_game_config(sid)
    return {
        'serverid': game['serverid'],
        'ip': login['network_ip'],
        'port': login['network_port'],
        'status': game['status'],
        'appver': game['appver'],
        'resver': game['resver'],
    }


def xindong_online(request):
    now_time = int(time.time())
    text = request.GET.get('online')
    temp = json.loads(text)
    onlines = []
    for val in temp:
        val['timestamp'] = now_time
        onlines.append(val)
    url = 'https://se-sg.tapdb.net/tapdb/online'
    headers = {
        'Content-Type': 'application/json',
    }
    content = ''
    for key in TAP_DB:
        data = {
            'appid': key,
            'onlines': onlines,
        }
        res = requests.post(url, json=data, headers=headers)
        if res.status_code != requests.codes.ok:
            logger.error("xindong online post error {0} {1}".format(str(res.status_code), res.content))
        content = res.content
    return HttpResponse(content)


def head_status(request):
    playerid = request.GET.get('playerid', None)
    sid = int(request.GET.get('serverid', 0))
    status = request.GET.get('status', None)
    head = request.GET.get('head', None)
    code = 0
    server = get_game_config(sid)
    if not server:
        code = 2
    else:
        res = requests.get('http://{0}:{1}/headstatus'.format(server['http_host'], game_http_port(sid)), params={
            'playerid': playerid,
            'status': status,
            'head': head,
        })
        if res.status_code != requests.codes.ok:
            logger.error("head_status error {0} {1}".format(str(res.status_code), res.content))
        else:
            code = int(res.content)
    return HttpResponse(code)


def is_account_lock(request):
    uid = request.GET.get('account', None)
    data = get_cache_account(uid=uid)
    code = 0
    if 'lock' in data and data['lock']:
        code = 1
    return HttpResponse(code)


def lock_account(request):
    uid = request.GET.get('account', None)
    flag = request.GET.get('flag', None)
    obj = WebAccount.objects.get(uid=uid)
    if flag == 0:
        obj.lock = False
    else:
        obj.lock = True
    obj.save()
    return HttpResponse(0)


def get_lock_account(request):
    ret = []
    objs = WebAccount.objects.filter(lock=True)
    for obj in objs:
        ret.append(obj.uid)
    return JsonResponse(ret, safe=False)


def is_lockip(request):
    pass


def lockip_list(request):
    pass


def lock_ip(request):
    pass
