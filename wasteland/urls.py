"""wasteland URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import webaccount.views
import serverconf.views
import push.views
import common.views
import charge.views

'''对原有做兼容修改'''

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('common/', include('common.urls')),
    # ('server/', include('serverconf.urls')),
    # path('weight/', include('serverweight.urls')),
    # path('charge/', include('charge.urls')),
    # path('push/', include('push.urls')),
    # path('account/', include('webaccount.urls')),

    # 兼容之前
    path('accountserver.php', webaccount.views.user_login),
    path('playerlogin.php', webaccount.views.enter_game),
    path('delaccount', webaccount.views.delete_account),
    path('bindaccount.php', webaccount.views.bind_account),     #
    path('servercfg.php', serverconf.views.game_config),
    path('allserverdbcfg', serverconf.views.all_server_dbconfig),
    path('xindong/onlines', webaccount.views.xindong_online),
    path('fcm_broadcast.php', push.views.broadcast_push),       #
    path('fcm_register.php', push.views.register_push),
    path('fcm_unregister.php', push.views.unregister_push),
    path('translate.php', common.views.translate),
    path('clientversion', common.views.get_client_version),
    path('saveclientver', common.views.set_client_version),
    path('gmserverlist.php', serverconf.views.get_game_list),
    path('gmupdateserver.php', serverconf.views.update_game_server),
    path('countryweight', common.views.save_country_weight),
    path('xindong/pay', charge.views.xindong_pay),
    path('chargeplayer', charge.views.charge_player),

    path('islockaccount.php', webaccount.views.is_account_lock),
    path('lockaccount.php', webaccount.views.lock_account),
    path('accountoflock.php', webaccount.views.get_lock_account),
    path('islockip.php', webaccount.views.is_lockip),
    path('ipoflock.php', webaccount.views.lockip_list),
    path('lockip.php', webaccount.views.lock_ip),
]