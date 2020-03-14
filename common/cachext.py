from django.core.cache import cache
from django.conf import settings
from django.utils.cache import _generate_cache_header_key, _generate_cache_key
from django.core.cache import cache

PAGE_CACHE = {}


def _page_cache_dict():
    return cache.get('_page_cache') or {}


def _save_page_cache(d):
    cache.set('_page_cache', d)


def add_page_cache(request, group='default', key_prefix=None):
    """增加视图缓存key，清除缓存时使用，不支持reponse has_header 'Vary'"""
    group = group or 'page'
    page_cache = _page_cache_dict()
    if group not in page_cache:
        page_cache[group] = {}

    if request.get_full_path() in page_cache[group]:
        return

    if key_prefix is None:
        key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    headerkey = _generate_cache_header_key(key_prefix, request)
    cachekey = _generate_cache_key(request, request.method, [], key_prefix)
    page_cache[group][request.get_full_path()] = {
        'header': headerkey,
        'cache': cachekey,
    }
    _save_page_cache(page_cache)


def _delete_page_cache(group):
    for v in group.values():
        cache.delete(v['header'])
        cache.delete(v['cache'])


def clear_page_cache(group=None):
    """清除指定视图缓存信息"""
    page_cache = _page_cache_dict()
    if not group:
        for i in page_cache.values():
            _delete_page_cache(i)
    elif group in page_cache:
        temp = page_cache[group]
        if temp:
            _delete_page_cache(temp)

