from django.contrib import admin
from .models import PushDevice

# Register your models here.


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    list_display = ('device', 'token', 'language', 'serverid')
    list_editable = ['token', 'language', 'serverid']

    search_fields = ('device', )  # 搜索字段