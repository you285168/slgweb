from django.contrib import admin
from .models import WebAccount, LockIP
from .account import *
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404, redirect
from common import get_admin_url, get_url_params

# Register your models here.


class LockAccountFilter(admin.SimpleListFilter):
    # 提供一个可读的标题
    title = (u'是否冻结')

    # 用于URL查询的参数.
    parameter_name = 'lock'

    def lookups(self, request, model_admin):
        """
        返回一个二维元组。每个元组的第一个元素是用于URL查询的真实值，
        这个值会被self.value()方法获取，并作为queryset方法的选择条件。
        第二个元素则是可读的显示在admin页面右边侧栏的过滤选项。
        """
        return (
            ('1', ('已冻结')),
        )

    def queryset(self, request, queryset):
        """
        根据self.value()方法获取的条件值的不同执行具体的查询操作。
        并返回相应的结果。
        """
        if self.value() == '1':
            accounts = get_lock_account() or set()
            return queryset.filter(uid__in=accounts)


@admin.register(WebAccount)
class WebAccountAdmin(admin.ModelAdmin):
    list_display = ('uid', 'device', 'lastdevice', 'xindong', 'create_new_uuid', 'lock_and_unlock')
    list_display_links = ('uid', )
    list_editable = ['device', 'xindong']
    search_fields = ('uid', 'device', 'xindong')  # 搜索字段
    list_filter = (LockAccountFilter,)

    list_per_page = 20

    def save_model(self, request, obj, form, change):
        clear_account_cache(obj)
        super(WebAccountAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        clear_account_cache(obj)
        super(WebAccountAdmin, self).delete_model(request, obj)

    @mark_safe
    def create_new_uuid(self, obj):
        """自定义一个a标签,跳转到实现重新生成一个uuid,可以取消原来关联的游戏数据"""
        dest = '{}uuid/{}'.format(obj.pk, get_url_params())
        title = '删除游戏关联'

        return '<a href="{}">{}</a>'.format(dest, title)

    create_new_uuid.short_description = 'new uuid'
    create_new_uuid.allow_tags = True

    @mark_safe
    def lock_and_unlock(self, obj):
        if is_lock_account(obj.uid):
            title = '冻结'
            color_code = 'red'
            dest = '{}unlockuid/{}'.format(obj.pk, get_url_params())
        else:
            title = 'None'
            color_code = 'blue'
            dest = '{}lockuid/{}'.format(obj.pk, get_url_params())
        return '<a href="{}"><span style="color: {};">{}</span></a>'.format(dest, color_code, title)

    lock_and_unlock.short_description = 'lock'
    lock_and_unlock.allow_tags = True

    def get_urls(self):
        from django.conf.urls import url
        urls = [
            url('^(?P<pk>\d+)uuid/?$', self.admin_site.admin_view(self.create_uuid), name='create_uuid'),
            url('^(?P<pk>\d+)lockuid/?$', self.admin_site.admin_view(self.lock_uid), name='lock_uid'),
            url('^(?P<pk>\d+)unlockuid/?$', self.admin_site.admin_view(self.unlock_uid), name='unlock_uid'),
        ]
        return urls + super(WebAccountAdmin, self).get_urls()

    def create_uuid(self, request, *args, **kwargs):
        """函数实现复制本条数据，并跳转到新复制的数据的修改页面"""
        obj = get_object_or_404(WebAccount, pk=kwargs['pk'])
        obj.uid = create_uuid()
        obj.save()
        clear_account_cache(obj)
        return redirect(get_admin_url(request))

    def lock_uid(self, request, *args, **kwargs):
        obj = get_object_or_404(WebAccount, pk=kwargs['pk'])
        add_lock_account(obj.uid)
        return redirect(get_admin_url(request))

    def unlock_uid(self, request, *args, **kwargs):
        obj = get_object_or_404(WebAccount, pk=kwargs['pk'])
        del_lock_account(obj.uid)
        return redirect(get_admin_url(request))
