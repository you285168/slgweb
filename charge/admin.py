from django.contrib import admin
from .models import ChargeOrder

# Register your models here.


@admin.register(ChargeOrder)
class ChargeOrderAdmin(admin.ModelAdmin):
    list_display = ('account', 'serverid', 'playerid', 'device', 'order_id', 'product_id', 'status', 'tester', 'platform', 'pay_way', 'time')

    '''
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields] 
    '''
