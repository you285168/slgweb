from django.core.cache import cache
import requests
import json

LOGIN_WEIGHT = "login:weight"
WEIGHT_URL = "http://192.168.1.5:9002/index.php/Api/maintain/dealData"
CACHE_TIME = 60 * 60


def get_country_weight(country):
    data = cache.get(LOGIN_WEIGHT)
    if not data:
        res = requests.get(WEIGHT_URL)
        data = json.loads(res.text)
        cache.set(LOGIN_WEIGHT, data, CACHE_TIME)
    pool = {}
    if data:
        if country in data:
            pool = data[country]
        elif 'UNKNOW' in data:
            pool = data['UNKNOW']
    return pool


def clear_country_weight():
    cache.delete(LOGIN_WEIGHT)
