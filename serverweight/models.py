from django.db import models

# Create your models here.


class ServerWeight(models.Model):
    server = models.IntegerField()
    weight = models.IntegerField(default=100)

    def __str__(self):
        return "{{{0} : {1}}}".format(self.server, self.weight)

    class Meta:
        verbose_name_plural = "服务器权重"


class CountryConfig(models.Model):
    name = models.CharField(max_length=64)
    # weight = models.ForeignKey(LoginWeight, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "————"


class LoginWeight(models.Model):
    name = models.CharField(max_length=64)
    weight = models.ManyToManyField(ServerWeight, verbose_name='服务器权重')
    country = models.ManyToManyField(CountryConfig, verbose_name='国家')

    class Meta:
        verbose_name_plural = "————"

    # 国家列表
    def country_list(self):
        value = [i.name for i in self.country.all()]
        return ", ".join(value)

    # 设置标题
    country_list.short_description = '国家'

    # 权重列表
    def weight_list(self):
        value = [str(i) for i in self.weight.all()]
        return ", ".join(value)

    # 设置标题
    weight_list.short_description = '服务器权重'

