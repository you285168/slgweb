from django.contrib import admin
from .models import ClientVersion

# Register your models here.


@admin.register(ClientVersion)
class ClientVersionAdmin(admin.ModelAdmin):
    list_display = ('appid', 'version')
    list_editable = ['version']
