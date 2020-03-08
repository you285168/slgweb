from django.db import models

# Create your models here.


class ChargeOrder(models.Model):
    uid = models.CharField(max_length=64, db_index=True, default='')
    serverid = models.IntegerField(default=0)
    playerid = models.IntegerField(default=0)
    device = models.CharField(max_length=64, default='')
    order_id = models.CharField(max_length=255, default='')
    product_id = models.CharField(max_length=64, default='')
    status = models.IntegerField(default=0)
    tester = models.IntegerField(default=0)
    platform = models.CharField(max_length=64, default='')
    pay_way = models.CharField(max_length=64, default='')
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "充值"
        unique_together = ('platform', 'order_id',)
