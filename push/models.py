from django.db import models

# Create your models here.


class PushDevice(models.Model):
    device = models.CharField(db_index=True, max_length=64)
    token = models.CharField(max_length=255)
    language = models.CharField(max_length=64)
    serverid = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "推送注册信息"
        db_table = "fcm_token"
        managed = True

    def __getitem__(self, key):
        return getattr(self, key)
