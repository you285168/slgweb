from django.db import models

# Create your models here.


class ChargeOrder(models.Model):
    account = models.CharField(max_length=64, db_index=True, default='', blank=True)
    serverid = models.IntegerField(default=0)
    playerid = models.BigIntegerField(default=0)
    device = models.CharField(max_length=64, default='', blank=True)
    order_id = models.CharField(db_column='orderId', max_length=255, default='')
    product_id = models.CharField(db_column='productId', max_length=64, default='', blank=True)
    status = models.IntegerField(default=0)
    tester = models.IntegerField(default=0)
    platform = models.CharField(max_length=64, default='')
    pay_way = models.CharField(max_length=64, default='', blank=True)
    time = models.DateTimeField(db_column='purchaseTime', blank=True, null=True)

    class Meta:
        verbose_name_plural = "充值"
        unique_together = ('platform', 'order_id',)
        db_table = "charge_order"
        managed = True
