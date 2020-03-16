from django.shortcuts import render
from webaccount.account import get_cache_account
from webaccount.platform import XINDONG_KEY
from hashlib import md5
import logging
from .models import ChargeOrder
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from serverconf.interface import get_game_config, game_http_port
import requests
from django.http import HttpResponse
from django.core.cache import cache
import json
from django.http.response import JsonResponse

logger = logging.getLogger('wasteland')

# Create your views here.
ORDER = 'ORDER-'
CHARGE = 'CHARGE-'
CACHE_TIME = 15 * 60


def _charge_ship(obj):
    try:
        server = get_game_config(obj.serverid)
        if not server:
            raise Exception("not found server {0}".format(obj.serverid))
        platform = 0
        if obj.tester == 1:
            platform = 1
        elif obj.platform == 'android':
            platform = 3
        elif obj.platform == 'ios':
            platform = 2
        elif obj.platform == 'feiyu':
            platform = 4
        res = requests.get('http://{0}:{1}/charge'.format(server['http_host'], game_http_port(obj.serverid)), params={
            'account': obj.account,
            'product_id': obj.product_id,
            'platform': platform,
            'order': obj.order_id,
            'pay_way': obj.pay_way,
        })
        if res and res.content:
            obj.status = 1
            obj.save()
            return True
    except Exception as e:
        logger.error('_charge_ship error: {0}'.format(str(e)))
    return False


def _pay_logic(platform, param):
    order_key = ORDER + param['order_id']
    if cache.get(order_key):
        return
    cache.set(order_key, 1, CACHE_TIME)
    try:
        try:
            obj = ChargeOrder.objects.get(order_id=param['order_id'], platform=platform)
        except ObjectDoesNotExist:
            obj = None
        if not obj:
            param['platform'] = platform
            param['time'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            obj = ChargeOrder.objects.create(**param)
        if obj.status == 0:
            if not _charge_ship(obj):
                cache.delete(CHARGE + param['account'])
    except Exception as e:
        logger.error('_pay_logic error: {0}'.format(str(e)))
    cache.delete(order_key)


def xindong_pay(request):
    product_id = request.GET.get('productid', None)
    sign = request.GET.get('sign', None)
    sid = request.GET.get('server_id', None)
    mark = request.GET.get('mark', None)
    uid = request.GET.get('uid', None)
    order = request.GET.get('order', None)
    pay_way = request.GET.get('pay_way', None)

    code = 0
    print(product_id, sign, sid, uid, order)
    if not product_id or not sign or not sid or not uid or not order:
        code = 2
    else:
        data = get_cache_account(xindong=uid)
        if not data:
            code = 7
        else:
            my_sign = str.lower(md5((uid + '_' + order + '_' + product_id
                                     + '_' + mark + '_' + XINDONG_KEY).encode('utf8')).hexdigest())
            if my_sign != sign:
                code = 5
            else:
                param = {
                    'serverid': sid,
                    'account': data['uid'],
                    'product_id': product_id,
                    'pay_way': pay_way,
                    'order_id': order,
                }
                if 'device' in data:
                    param['device'] = data['device']
                _pay_logic('xindong', param)
                code = 1
    '''
    {
        code：
        1 充值成功(重复订单号储值也返回1)
        2 充值的服务器不存在，请确认游戏服域名正确并已被添加到后台
        3 充值游戏币有误
        5 md5错误，请确认密钥正确，充值票据算法跟文档描述一致，参与票据计算的参数于传递给接口的参数一致
        7 不存在此账号，请确认用户名和登录接口传递的是一致的
        0 充值失败，订单处于待充状态，可以重复请求直到返回值为1
        - 1 充值请求参数错误
    }
    '''
    return HttpResponse(code)


def charge_player(request):
    playerid = request.GET.get('uid', None)
    serverid = request.GET.get('sid', None)
    server = get_game_config(serverid)
    ret = {
        'ret': 1,
        'error': 'not found user',
    }
    if server:
        res = requests.get('http://{0}:{1}/reqchargeplayer'.format(server['http_host'], game_http_port(serverid)), params={
            'playerid': playerid,
        })
        if res and res.content:
            data = json.loads(res.content)
            user = get_cache_account(uid=data['account'])
            if user:
                ret = data
                ret['ret'] = 0
                ret['uid'] = playerid
                if 'xindong' in user['platform']:
                    ret['account'] = user['platform']['xindong']
    return JsonResponse(ret)


def request_charge(sid, uid):
    charge_key = CHARGE + uid
    if cache.get(charge_key):
        return
    objs = ChargeOrder.objects.filter(serverid=sid, account=uid, status=0)
    result = True
    for obj in objs:
        order_key = ORDER + obj.order_id
        if not cache.get(order_key):
            cache.set(order_key, 1, CACHE_TIME)
            if not _charge_ship(obj):
                result = False
            cache.delete(order_key)
        else:
            result = False
    if result:
        cache.set(charge_key, 1, CACHE_TIME)

