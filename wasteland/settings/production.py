from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ff6h42^=o)xwa)hq!62j!)b8f%qn+*nl$6ooc@@k-)w%7ycj83'    # os.environ['DJANGO_SECRET_KEY']          # 可以在supervisor中配置环境变量

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']