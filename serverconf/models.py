from django.db import models
from django.utils.html import format_html

# Create your models here.


class DBConfig(models.Model):
    host = models.CharField(max_length=64)
    port = models.IntegerField(default=3306)
    user = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    dbname = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "数据库配置"

    def __str__(self):
        return self.dbname


# Create your models here.
class WorldConfig(models.Model):
    dbc_world = models.ForeignKey(DBConfig, on_delete=models.PROTECT, verbose_name='world数据库')
    gmt = models.IntegerField(default=0, verbose_name='时区')
    http_host = models.CharField(max_length=64, verbose_name='内网IP')

    class Meta:
        verbose_name_plural = "世界服配置"

    def __str__(self):
        return str(self.id)


class LoginConfig(models.Model):
    dbc_player = models.ManyToManyField(DBConfig, blank=True)
    network_ip = models.CharField(max_length=64)
    network_port = models.IntegerField()
    http_host = models.CharField(max_length=64)
    port = models.IntegerField()

    class Meta:
        verbose_name_plural = "登陆服配置"

    def __str__(self):
        return str(self.id)


class GameConfig(models.Model):
    network_ip = models.CharField(max_length=64)
    network_port = models.IntegerField()
    http_host = models.CharField(max_length=64)
    dbc_player = models.ForeignKey(DBConfig, null=True, on_delete=models.PROTECT, blank=True)
    dbc_log = models.ForeignKey(DBConfig, on_delete=models.PROTECT, related_name="game_log")
    dbc_global = models.ForeignKey(DBConfig, on_delete=models.PROTECT, related_name="game_global")
    standalone = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    test = models.IntegerField(default=0)
    arenaid = models.IntegerField(default=0)
    trailnotice = models.DateTimeField(blank=True, null=True)
    servername = models.CharField(max_length=64, default='')
    resver = models.CharField(max_length=64)
    appver = models.CharField(max_length=64)
    world = models.ForeignKey(WorldConfig, on_delete=models.PROTECT)
    login = models.ForeignKey(LoginConfig, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "游戏服配置"

    # 给状态设置颜色显示
    def colored_status(self):
        if self.status != 1:
            color_code = 'red'
            status_str = '关闭'
        else:
            color_code = 'green'
            status_str = '开启'
        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            status_str,
        )

    # 设置标题
    colored_status.short_description = 'status'

