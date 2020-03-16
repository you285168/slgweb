from django.contrib import admin
from .models import DBConfig, WorldConfig, LoginConfig, GameConfig
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.forms.models import model_to_dict
from .interface import _clear_game_cache, _clear_login_cache
from .interface import *
from common import get_admin_url, get_url_params

# Register your models here.
admin.site.site_header = 'wasteland后台'
admin.site.site_title = 'wasteland后台'


@admin.register(GameConfig)
class GameConfigAdmin(admin.ModelAdmin):
    # 设置哪些字段可以点击进入编辑界面(默认可以点击每条记录第一个字段的值可以进入编辑界面)
    list_display_links = ('serverid',)

    # listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
    list_display = ('serverid', 'world', 'login', 'colored_status', 'http_host',
                    'dbc_player', 'arenaid', 'heroarena', 'warbanner', 'copy_current_data')

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 50

    # ordering设置默认排序字段，负号表示降序排序
    ordering = ('serverid',)

    # list_editable 设置默认可编辑字段
    list_editable = ['dbc_player', 'arenaid', 'heroarena', 'warbanner', 'world', 'login']

    # fk_fields 设置显示外键字段
    fk_fields = ('world', 'login')

    # 筛选器
    # list_filter = ('dbc_player', )  # ManyToManyField多对多字段用过滤器过滤器
    search_fields = ('serverid', 'arenaid', 'heroarena', 'warbanner')          # 搜索字段
    # date_hierarchy = 'go_time'      # 详细时间分层筛选　

    # 可以用fields或exclude控制显示或者排除的字段，二选一即可
    # fieldsets设置可以对字段分块，看起来比较整洁。
    '''
    fieldsets = (
        ("base info", {'fields': ['world', 'login', ('network_ip', 'network_port')]}),
        ("databse", {'fields': ['dbc_player', 'dbc_global', 'dbc_log']})
    )
    '''

    readonly_fields = ('network_ip', 'network_port')

    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser:
            return []
        else:
            return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """  保存时触发 """
        if change:  # 更改的时候
            pass
        else:  # 新增的时候
            pass
        super(GameConfigAdmin, self).save_model(request, obj, form, change)
        _clear_game_cache(obj.pk)
        reload_config(obj.http_host, game_http_port(obj.serverid))
        reload_login_config()
        reload_world_config()

    def delete_model(self, request, obj):
        """  删除时触发 """
        _clear_game_cache(obj.pk)
        super(GameConfigAdmin, self).delete_model(request, obj)
        reload_login_config()
        reload_world_config()

    # 允许您在渲染之前轻松自定义响应数据。（凡是对单条数据操作的定制，都可以通过这个方法配合实现）
    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super(GameConfigAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    @mark_safe
    def copy_current_data(self, obj):
        """自定义一个a标签，跳转到实现复制数据功能的url"""
        dest = '{}copy/{}'.format(obj.pk, get_url_params())
        title = '复制'
        return '<a href="{}">{}</a>'.format(dest, title)

    copy_current_data.short_description = 'copy'
    copy_current_data.allow_tags = True

    def get_urls(self):
        """添加一个url，指向实现复制功能的函数copy_one"""
        from django.conf.urls import url
        urls = [
            url('^(?P<pk>\d+)copy/?$',
                self.admin_site.admin_view(self.copy_one),
                name='copy_data'),
        ]
        return urls + super(GameConfigAdmin, self).get_urls()

    def copy_one(self, request, *args, **kwargs):
        """函数实现复制本条数据，并跳转到新复制的数据的修改页面"""
        obj = get_object_or_404(GameConfig, pk=kwargs['pk'])
        old_data = model_to_dict(obj, exclude=('id', 'dbc_player', 'dbc_log', 'dbc_global', 'world', 'login'))
        old_data['world'] = obj.world
        old_data['login'] = obj.login
        new_id = obj.serverid + 1
        old_data['serverid'] = new_id
        old_data['arenaid'] = new_id
        old_data['heroarena'] = new_id
        old_data['warbanner'] = new_id
        old_data['servername'] = 's' + str(new_id)
        old_data['network_port'] = game_network_port(new_id)
        dbobj = obj.dbc_log
        dbdata = model_to_dict(dbobj, exclude=('id',))
        dbdata['dbname'] = 'game_log_' + str(new_id)
        old_data['dbc_log'] = DBConfig.objects.create(**dbdata)
        dbobj = obj.dbc_global
        dbdata = model_to_dict(dbobj, exclude=('id',))
        dbdata['dbname'] = 'game_global_' + str(new_id)
        old_data['dbc_global'] = DBConfig.objects.create(**dbdata)
        new_obj = GameConfig.objects.create(**old_data)
        return redirect(get_admin_url(request))


@admin.register(LoginConfig)
class LoginConfigAdmin(admin.ModelAdmin):
    list_display = ('loginid', 'network_ip', 'network_port', 'port', 'http_host')
    list_editable = ['network_ip', 'network_port', 'port', 'http_host']

    # ManyToMany多对多字段设置。可以用filter_horizontal或filter_vertical
    filter_horizontal = ('dbc_player',)

    list_filter = ('dbc_player', )  # 过滤器

    def save_model(self, request, obj, form, change):
        """  保存时触发 """
        if change:  # 更改的时候
            pass
        else:  # 新增的时候
            pass
        _clear_login_cache(obj.pk)
        reload_config(obj.http_host, obj.loginid)
        super(LoginConfigAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        _clear_login_cache(obj.pk)
        super(LoginConfigAdmin, self).delete_model(request, obj)


@admin.register(WorldConfig)
class WorldConfigAdmin(admin.ModelAdmin):
    list_display = ('worldid', 'gmt', 'http_host', 'dbc_world')
    list_editable = ['gmt', 'http_host', 'dbc_world']

    def save_model(self, request, obj, form, change):
        """  保存时触发 """
        if change:  # 更改的时候
            pass
        else:  # 新增的时候
            pass
        reload_config(obj.http_host, obj.worldid)
        super(WorldConfigAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        super(WorldConfigAdmin, self).delete_model(request, obj)


@admin.register(DBConfig)
class DBConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'port', 'user', 'password', 'dbname')
    list_editable = ['host', 'port', 'user', 'password', 'dbname']

    def copy_action(self, request, queryset):
        # 定义actions函数
        # 判断用户选择了几条数据，如果是一条以上，则报错
        for old_data in queryset.values():
            old_data.pop('id')
            # 将原数据复制并去掉id字段后，插入数据库，以实现复制数据功能，返回值即新数据的id（这是在model里__str__中定义的）
            r_pk = DBConfig.objects.create(**old_data)
        # 修改数据后重定向url到新加数据页面
        # return HttpResponseRedirect('{}{}/change'.format(request.path, r_pk))

    copy_action.short_description = "复制所选数据"

    # 定义行为
    actions = [copy_action]

    def save_model(self, request, obj, form, change):
        """  保存时触发 """
        if change:  # 更改的时候
            pass
        else:  # 新增的时候
            pass
        super(DBConfigAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """  删除时触发 """
        super(DBConfigAdmin, self).delete_model(request, obj)


