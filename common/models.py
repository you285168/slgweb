from django.db import models

# Create your models here.


class ClientVersion(models.Model):
    appid = models.CharField(max_length=128)
    version = models.TextField()

    class Meta:
        verbose_name_plural = "客户端版本"
