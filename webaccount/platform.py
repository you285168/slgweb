from django.core.cache import cache
import time
import requests
import logging
import json
from common import md5_sign

logger = logging.getLogger('wasteland')


PLATFORM_CACHE_TIME = 15 * 24 * 60 * 60
PLATFORM = ('gamecenter', 'googleplay', 'facebook', 'feiyu', 'xindong')
FEIYU_KEY = 'bdc96026c4fb2bdbe86cf2c29aaf39c9'
FEIYU_ID = '10029'
XINDONG_KEY = 'd013b9dfe96ab8396f45070fae87653d'
XINDONG_ID = '161414'


def platform_verify(platform, signture, subplatform, email):
    key = None
    if platform == 'gamecenter':
        key = _gamecenter_verify(signture, email)
    elif platform == 'googleplay':
        key = _googleplay_verify(platform, signture, email)
    elif platform == 'facebook':
        key = _facebook_verify(platform, signture, email)
    elif platform == 'feiyu':
        key = _feiyu_verify(signture, subplatform, email)
    elif platform == 'xindong':
        key = _googleplay_verify(platform, signture, email)
    return key


def _get_platform_cache(platform, key):
    d = cache.get(platform + 'cache')
    if d and key in d:
        return d[key]


def _set_platform_cache(platform, key, value):
    cachekey = platform + 'cache'
    d = cache.get(cachekey)
    if not d:
        d = {}
    d[key] = value
    cache.set(cachekey, d, PLATFORM_CACHE_TIME)


def _gamecenter_verify(signture):
    pass


def _feiyu_verify(token, platform, email):
    if not token or not email:
        return

    param = {
        'token': token,
        'time': int(time.time()),
    }
    param['sign'] = md5_sign(param, FEIYU_KEY)
    res = requests.get('https://sdk2-syapi.737.com/sdk/index/{0}/{1}/user_check'.format(FEIYU_ID, platform), params=param)
    if res.content == email:
        return email
    else:
        logger.error('feiyu verify fail token: {0} email:{1} ret:{2}'.format(token, email, res.content))


def _xindong_verify(token):
    if not token:
        return

    res = requests.get('http://p.txwy.tw/passport/auth', params={
        'sid': token,
    })
    data = json.loads(res.content)
    if 'uid' in data:
        return data['uid']
    else:
        logger.error('xindong verify fail ret:{0}'.format(res.content))


FBID = 362619877528441
FBSECRET = 'df2309bb1b5c58224434eec152a1aeb8'
def _facebook_verify(platform, token, email):
    if not email or not token:
        return
    oldtoken = _get_platform_cache(platform, email)
    found = False
    if oldtoken and token == oldtoken:
        found = True
    else:
        res = requests.get('https://graph.facebook.com/v2.8/debug_token', params={
            'input_token': token,
            'access_token': str(FBID) + '|' + FBSECRET,
        }, proxies={
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        })
        data = json.loads(res.content)
        if 'user_id' in data and data['user_id'] == email:
            found = True
        else:
            logger.error('facebook verify fail ret:{0}'.format(res.content))
    if found:
        _set_platform_cache(platform, email, token)
        return email


def _googleplay_verify(platform, token, email):
    if not email or not token:
        return
    oldtoken = _get_platform_cache(platform, email)
    found = False
    if oldtoken and token == oldtoken:
        found = True
    else:
        # 客户端请求一个TOKEN和EMAIL发给服务器，服务器拿这个TOKEN去https: // www.googleapis.com / oauth2 / v3 / tokeninfo地址请求EMAIL信息，然后比对TOKEN和EMAIL，并且根据返回的NAME来指定账号名
        res = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params={
            'access_token': token,
        }, proxies={
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        })
        data = json.loads(res.content)
        if 'email' in data and data['email'] == email:
            found = True
        else:
            logger.error('facebook verify fail ret:{0}'.format(res.content))
    if found:
        _set_platform_cache(platform, email, token)
        return email
