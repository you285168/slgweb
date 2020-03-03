from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ff6h42^=o)xwa)hq!62j!)b8f%qn+*nl$6ooc@@k-)w%7ycj83'    # os.environ['DJANGO_SECRET_KEY']          # 可以在supervisor中配置环境变量

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 配置使用mysql
        'ENGINE': 'django.db.backends.mysql',     # 数据库产品
        'HOST': "127.0.0.1",               # 数据库ip
        'PORT': 3306,                          # 数据库端口
        'USER': "masterroot",                        # 用户名
        'PASSWORD': "icesola1@Abc.com",        # 密码
        'NAME': "pyweb",                       # 数据库名
    },
}