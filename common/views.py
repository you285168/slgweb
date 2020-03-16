from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from . import clear_page_cache
from .clientver import client_version, save_client_version
from webaccount.platform import XINDONG_ID
from .translate import baidu_translate
from django.http.response import JsonResponse
from .loginweight import clear_country_weight

# Create your views here.


def index(request):
    cache.set('username', 'zhiliao', 12000)
    username = cache.get('username')
    print(username)
    return render(request, 'wasteland/index.html', context={
        'title': '我的博客首页',
        'welcome': '欢迎访问我的博客首页'
    })


def get_cache(request, key):
    value = cache.get(key)
    return HttpResponse(value)


def clean_cache(request):
    clear_page_cache()
    return HttpResponse("success")


def get_client_version(request):
    return HttpResponse(client_version(XINDONG_ID))


def set_client_version(request):
    ver = request.GET.get('clientstr', None)
    save_client_version(XINDONG_ID, ver)
    return HttpResponse(0)


def translate(request):
    text = request.GET.get('text', None)
    language = request.GET.get('language', None)
    data = baidu_translate(text, language)
    return JsonResponse(data)


def save_country_weight(request):
    clear_country_weight()
    return HttpResponse(0)
