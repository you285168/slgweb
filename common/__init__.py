from .cachext import add_page_cache, clear_page_cache
from .middleware import global_request
from urllib.parse import quote
from hashlib import md5
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField, ForeignKey
import geoip2.database
import logging
import uuid

reader = geoip2.database.Reader('./extend/GeoLite2-Country.mmdb')
logger = logging.getLogger('wasteland')


def get_country_code(ip):
    """获取国家code"""
    code = 'unkown'
    try:
        response = reader.country(ip)
        code = response.country.iso_code
    except Exception as e:
        logger.error('geoip2 error: {0}'.format(str(e)))
    return code


def get_ip(request):
    """获取ip"""
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def md5_sign(params, app_key):
    """md5加密"""
    after = dict(sorted(params.items(), key=lambda item: item[0]))
    sign = ''
    for key, value in after.items():
        sign += '&' + key + "=" + str(value)
    sign = quote(sign[1:])
    sign += '&' + str(app_key)
    return md5(sign.encode('utf8')).hexdigest()


def to_dict(obj, *, fields=None, exclude=None, deep=True):
    "mdoel_to_dict 的封装"
    data = {}

    for f in obj._meta.concrete_fields + obj._meta.many_to_many:
        value = f.value_from_object(obj)
        if fields and f.name not in fields:
            continue

        if exclude and f.name in exclude:
            continue

        if not value:
            continue

        if isinstance(f, ForeignKey) and deep:
            value = to_dict(f.remote_field.model.objects.get(pk=value))

        if isinstance(f, ManyToManyField):
            if deep:
                temp = f.remote_field.model.objects.filter(pk__in=[i.id for i in value] if obj.pk else [])
                value = [to_dict(i) for i in temp]
            else:
                value = [i.id for i in value] if obj.pk else None

        if isinstance(f, DateTimeField):
            value = value.strftime('%Y-%m-%d %H:%I:%S') if value else None

        data[f.name] = value
    return data


def create_uuid():
    return str(uuid.uuid1()).replace('-', '')


def _get_request_params(request):
    url = request.get_full_path()
    index = url.find('?')
    if index != -1:
        return url[index:]
    else:
        return ''


def get_admin_url(request):
    co_path = request.path.split('/')
    co_path.pop(-2)
    new_path = '/'.join(co_path) + _get_request_params(request)
    return new_path


def get_url_params():
    return _get_request_params(global_request)
