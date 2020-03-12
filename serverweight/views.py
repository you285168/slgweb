from django.shortcuts import render
from django.http.response import JsonResponse
from .models import LoginWeight
from django.views.decorators.cache import cache_page
from common import add_page_cache

# Create your views here.


@cache_page(30 * 60)
def login_weight(request):
    add_page_cache(request, 'serverweight')
    data = {}
    for obj in LoginWeight.objects.all():
        weight = {}
        for i in obj.weight.all():
            weight[i.server] = i.weight
        for i in obj.country.all():
            data[i.name] = weight
    return JsonResponse(data)


def save_country_weight(request):
    pass
