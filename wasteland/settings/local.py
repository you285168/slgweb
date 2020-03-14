from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ff6h42^=o)xwa)hq!62j!)b8f%qn+*nl$6ooc@@k-)w%7ycj83'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

REQUEST_PROXIES = {'http': '192.168.1.113:1080', 'https': '192.168.1.113:1080'}
BACK_STAGE = "192.168.1.5:9002"

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 配置使用mysql
        'ENGINE': 'django.db.backends.mysql',     # 数据库产品
        'HOST': "127.0.0.1",               # 数据库ip
        'PORT': 3306,                          # 数据库端口
        'USER': "root",                        # 用户名
        'PASSWORD': "123",        # 密码
        'NAME': "web",                       # 数据库名
    },
}