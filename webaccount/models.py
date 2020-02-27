from django.db import models

# Create your models here.


class WebAccount(models.Model):
    uid = models.CharField(max_length=64, db_index=True)
    device = models.CharField(max_length=64, db_index=True, default='')
    googleplay = models.CharField(max_length=64, db_index=True, default='')
    facebook = models.CharField(max_length=64, db_index=True, default='')
    lastdevice = models.CharField(max_length=64, default='')
    feiyu = models.CharField(max_length=64, db_index=True, default='')
    xindong = models.CharField(max_length=64, db_index=True, default='')
    subplatform = models.CharField(max_length=64, default='')

    class Meta:
        verbose_name_plural = "玩家"
