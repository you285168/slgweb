import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# django 日志配置

# django memcached缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': None,  # 缓存的默认超时时间（以秒为单位）
        'OPTIONS': {
            'server_max_value_length': 1024 * 1024 * 1024,     # python-memcached的后端对象大小限制为1GB
        }
    }
}

# 管理员邮箱
ADMINS = (
    ('root', '530830311@qq.com'),
)

# 非空链接，却发生404错误，发送通知MANAGERS
SEND_BROKEN_LINK_EMAILS = True
MANAGERS = ADMINS

# Email设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # QQ邮箱SMTP服务器(邮箱需要开通SMTP服务)
EMAIL_PORT = 25  # QQ邮箱SMTP服务端口
EMAIL_HOST_USER = '530830311@qq.com'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = 'dpzpvwwstcefcaga'  # 授权码
EMAIL_SUBJECT_PREFIX = 'wasteland'  # 为邮件标题的前缀,默认是'[django]'
EMAIL_USE_TLS = True  # 开启安全链接
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER  # 设置发件人

LOGGING = {
    'version': 1,   # 指明dictConnfig的版本，目前就只有一个版本
    'disable_existing_loggers': False,   # 禁用所有的已经存在的日志配置

    # 格式器
    'formatters': {
        'simple': {  # 简单
            'format': '时间:%(asctime)s | %(levelname)s | %(message)s',
         },
        'standard': {   # 详细
            'format': '\n%(asctime)s [%(threadName)s:%(thread)d] [%(name)s: %(pathname)s: %(funcName)s: %(lineno)d] [%(levelname)s]- %(message)s\n\n------------------------------------------------------------'
        },
    },

    # 过滤器
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',# 此过滤器仅在settings.DEBUG为True时传递记录
         },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',# 此过滤器仅在settings.DEBUG为False时传递记录
        },
    },

    # 处理器，在这里定义了三个处理器。主要指明：处理引擎类、格式器、过滤器、日志等级
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file_handler': {   # 文件处理器，所有高于(包括)debug的消息会被传到
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, "log", 'debug.log'),     # 日志输出文件
         },
        'console': {     # 流处理器(控制台)，所有的高于(包括)debug的消息会被传到stderr，使用的是simple格式器
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
         },
        'mail_admins': {    # AdminEmail处理器，所有高于(包括)而error的消息会被发送给站点管理员，使用的是standard格式器
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'standard',
            'include_html': False,   # 是否发送那些回溯信息，因为这些都是很敏感的系统系统，如果被人截获，可能会发生危险，所以要谨慎
            'filters': ['require_debug_false'],     # 当settings.DEBUG=False的时候，AdminEmailHandler才生效
         },
    },

    # 记录器。主要指明：处理器、日志等级
    'loggers': {
        'django': {     # 使用file_handler处理器，所有高于(包括)info的消息会被发往console和file_handler处理器，向父层次传递信息
            'handlers': ['file_handler', 'console'],
            'level': 'INFO',
            'propagate': False,  # 是否继承父类的log信息
         },
        'django.request': {     # 所有高于(包括)error的消息会被发往console和mail_admins处理器，消息不向父层次发送
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG',
            'propagate': False,
         },
        'django.security.DisallowedHost': {        # 对于不在 ALLOWED_HOSTS 中的请求不发送报错邮件
            'handlers': ['null'],
            'propagate': False,
         },
        'wasteland': {   # 所有高于(包括)ERROR的消息同时会被发往console和mail_admins处理器
            'handlers': ['mail_admins', 'console', 'file_handler'],
            'level': 'INFO',
            'propagate': False,
         },
    }
}