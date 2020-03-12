from django.contrib import admin
from .models import ServerWeight, CountryConfig, LoginWeight
from common import clear_page_cache

# Register your models here.

admin.site.register(ServerWeight)
admin.site.register(CountryConfig)


@admin.register(LoginWeight)
class LoginWeightAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_list', 'weight_list')
    filter_horizontal = ('weight', 'country')

    def save_model(self, request, obj, form, change):
        clear_page_cache('serverweight')
        super(LoginWeightAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        clear_page_cache('serverweight')
        super(LoginWeightAdmin, self).delete_model(request, obj)


@admin.register(ServerWeight)
class ServerWeightAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        clear_page_cache('serverweight')
        super(ServerWeightAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        clear_page_cache('serverweight')
        super(ServerWeightAdmin, self).delete_model(request, obj)


@admin.register(CountryConfig)
class CountryConfigAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        clear_page_cache('serverweight')
        super(CountryConfigAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        clear_page_cache('serverweight')
        super(CountryConfigAdmin, self).delete_model(request, obj)
