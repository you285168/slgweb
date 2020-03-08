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
        res = requests.get('http://{0}:{1}'.format(server['http_host'], game_http_port(obj.serverid)), params={
            'account': obj.uid,
            'productid': obj.product_id,
            'platform': platform,
            'order': obj.order_id,
            'pay_way': obj.pay_way,
        })
        if res:
            obj.status = 1
            obj.save()
            return True
    except Exception as e:
        logger.error('_charge_ship error: {0}'.format(str(e)))
    return False


def _pay_logic(platform, param):
    cachekey = ORDER + param['order_id']
    if cache.get(cachekey):
        return
    cache.set(cachekey, 1, CACHE_TIME)
    try:
        try:
            obj = ChargeOrder.objects.get(order_id=param['order_id'], platform=platform)
        except ObjectDoesNotExist:
            obj = None
        if not obj:
            param['platform'] = platform
            param['time'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            obj = ChargeOrder.objects.create(**param)
        print(obj.status)
        if obj.status == 0:
            print('here')
            if not _charge_ship(obj):
                cache.delete(CHARGE + param['uid'])

    except Exception as e:
        logger.error('_pay_logic error: {0}'.format(str(e)))
    cache.delete(cachekey)


def xindong_pay(request):
    product_id = request.GET.get('productid', None)
    sign = request.GET.get('sign', None)
    sid = request.GET.get('server_id', None)
    mark = request.GET.get('mark', None)
    uid = request.GET.get('uid', None)
    order = request.GET.get('order', None)
    pay_way = request.GET.get('pay_way', None)

    code = 0
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
                    'uid': data['uid'],
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


def feiyu_pay(request):
    pass


def charge_player_info(request):
    pass
