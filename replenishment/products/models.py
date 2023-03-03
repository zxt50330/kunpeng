from django.db import models


# Create your models here.
class Sku(models.Model):
    sku = models.CharField(primary_key=True, max_length=50)
    asin = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    remark = models.TextField(null=True)

    def __str__(self):
        return self.asin + ' ' + self.name

    # class Meta:
    #     unique_together = [('asin', 'sku')]
