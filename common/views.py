from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from . import clear_page_cache

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
    print(value)
    return HttpResponse(value)


def clean_cache(request):
    clear_page_cache()
    return HttpResponse("success")

