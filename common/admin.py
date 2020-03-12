from django.contrib import admin
from .models import ClientVersion
from .clientver import clear_client_version_cache

# Register your models here.


@admin.register(ClientVersion)
class ClientVersionAdmin(admin.ModelAdmin):
    list_display = ('appid', 'version')
    list_editable = ['version']

    def save_model(self, request, obj, form, change):
        clear_client_version_cache(obj.appid)
        super(ClientVersionAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        clear_client_version_cache(obj.appid)
        super(ClientVersionAdmin, self).delete_model(request, obj)