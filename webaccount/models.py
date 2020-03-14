from django.db import models

# Create your models here.


class WebAccount(models.Model):
    uid = models.CharField(max_length=64, db_index=True, primary_key=True)
    device = models.CharField(max_length=64, db_index=True, default='', blank=True)
    googleplay = models.CharField(max_length=64, db_index=True, default='', blank=True)
    facebook = models.CharField(max_length=64, db_index=True, default='', blank=True)
    lastdevice = models.CharField(max_length=64, default='', blank=True)
    feiyu = models.CharField(max_length=64, db_index=True, default='', blank=True)
    xindong = models.CharField(max_length=64, db_index=True, default='', blank=True)
    subplatform = models.CharField(max_length=64, default='', blank=True)
    loginid = models.IntegerField(default=1)
    playerid = models.IntegerField(default=0)
    lastserver = models.IntegerField(default=0)
    name = models.CharField(max_length=255, default='', blank=True)
    lock = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "玩家"
        db_table = "webaccount"
        managed = True
