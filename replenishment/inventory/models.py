from django.db import models, transaction
from django.db.models import F
from products.models import Sku


class Inventory(models.Model):
    """
    1.2 一箱 6条
    2cm 4条
    68*0.8 12条
    跪垫 25条
    """
    sku = models.OneToOneField(Sku, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=100, null=True)  # 海外仓 亚马逊等
    updated_at = models.DateTimeField(auto_now=True, null=True)
    notes = models.TextField(null=True)


class Adjustment(models.Model):
    sku = models.CharField(max_length=100)
    asin = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    quantity_change = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    @staticmethod
    @transaction.atomic
    def update_inventory(sku, quantity_adjusted, reason):
        # 创建一条新的Adjustment记录
        Adjustment.objects.create(
            sku=sku,
            quantity_adjusted=quantity_adjusted,
            reason=reason,
        )

        # 获取对应sku的最新Inventory记录
        latest_inventory = Inventory.objects.filter(sku=sku).order_by('-updated_at').first()

        # 如果存在对应sku的Inventory记录，则更新quantity字段
        if latest_inventory:
            latest_inventory.quantity = F('quantity') + quantity_adjusted
            latest_inventory.save()
        # 否则创建一条新的Inventory记录
        else:
            Inventory.objects.create(
                sku=sku,
                quantity=quantity_adjusted,
            )
        return
