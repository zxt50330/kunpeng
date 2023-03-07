import csv
from datetime import date, timedelta

from django.db import models, transaction
from django.db.models import Sum, Count
from django.db.models.functions import Round, TruncMonth, TruncDay
from django.utils.timezone import now


# Create your models here.
class AmazonOrder(models.Model):
    amazon_order_id = models.CharField(max_length=100, primary_key=True)
    merchant_order_id = models.CharField(max_length=100)
    purchase_date = models.DateTimeField()
    last_updated_date = models.DateTimeField()
    order_status = models.CharField(max_length=100)
    fulfillment_channel = models.CharField(max_length=100)
    sales_channel = models.CharField(max_length=100)
    order_channel = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    ship_service_level = models.CharField(max_length=100)
    product_name = models.CharField(max_length=500)
    sku = models.CharField(max_length=100)
    asin = models.CharField(max_length=100)
    item_status = models.CharField(max_length=100)
    quantity = models.IntegerField()
    currency = models.CharField(max_length=100)
    item_price = models.CharField(max_length=100)
    item_tax = models.CharField(max_length=100)
    shipping_price = models.CharField(max_length=100)
    shipping_tax = models.CharField(max_length=100)
    gift_wrap_price = models.CharField(max_length=100)
    gift_wrap_tax = models.CharField(max_length=100)
    item_promotion_discount = models.CharField(max_length=100)
    ship_promotion_discount = models.CharField(max_length=100)
    ship_city = models.CharField(max_length=100)
    ship_state = models.CharField(max_length=100)
    ship_postal_code = models.CharField(max_length=100)
    ship_country = models.CharField(max_length=100)
    promotion_ids = models.CharField(max_length=500)
    is_business_order = models.CharField(max_length=500)
    purchase_order_number = models.CharField(max_length=100)
    price_designation = models.CharField(max_length=100)
    customized_url = models.CharField(max_length=500)
    customized_page = models.CharField(max_length=500)

    @staticmethod
    @transaction.atomic
    def upload_file(path):
        with open(path, 'r') as f:
            if f.name.endswith('.csv'):
                reader = csv.DictReader(f, delimiter='\t')
            else:
                print('不是csv文件')
            for row in reader:
                print(row)
                order = AmazonOrder(
                    amazon_order_id=row['amazon-order-id'],
                    merchant_order_id=row['merchant-order-id'],
                    purchase_date=row['purchase-date'],
                    last_updated_date=row['last-updated-date'],
                    order_status=row['order-status'],
                    fulfillment_channel=row['fulfillment-channel'],
                    sales_channel=row['sales-channel'],
                    order_channel=row['order-channel'],
                    url=row['url'],
                    ship_service_level=row['ship-service-level'],
                    product_name=row['product-name'],
                    sku=row['sku'],
                    asin=row['asin'],
                    item_status=row['item-status'],
                    quantity=row['quantity'],
                    currency=row['currency'],
                    item_price=row['item-price'],
                    item_tax=row['item-tax'],
                    shipping_price=row['shipping-price'],
                    shipping_tax=row['shipping-tax'],
                    gift_wrap_price=row['gift-wrap-price'],
                    gift_wrap_tax=row['gift-wrap-tax'],
                    item_promotion_discount=row['item-promotion-discount'],
                    ship_promotion_discount=row['ship-promotion-discount'],
                    ship_city=row['ship-city'],
                    ship_state=row['ship-state'],
                    ship_postal_code=row['ship-postal-code'],
                    ship_country=row['ship-country'],
                    promotion_ids=row['promotion-ids'],
                    is_business_order=row['is-business-order'],
                    purchase_order_number=row['purchase-order-number'],
                    price_designation=row['price-designation'],
                    customized_url=row['customized-url'],
                    customized_page=row['customized-page']
                )
                print(order)
                order.save()


class DailySales(models.Model):
    """
    CREATE VIEW sales_daily_quantity AS
    SELECT date_trunc('day', purchase_date AT TIME ZONE 'UTC') AS date,
           sku,
           SUM(quantity) AS total_quantity
    FROM sales_amazonorder
    GROUP BY date, sku;
    CREATE VIEW sales_daily_quantity_30avg AS
    WITH latest_date AS (
      SELECT MAX(date) AS latest_date FROM sales_daily_quantity
    )
    SELECT sku,
           ROUND(sum(total_quantity)/30, 2) AS daily_average
    FROM sales_daily_quantity
    WHERE date >= (SELECT latest_date - INTERVAL '29 days' FROM latest_date)
    GROUP BY sku;

    """
    sku = models.CharField(primary_key=True, max_length=100)
    daily_average = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sales_daily_quantity_30avg'

    def __str__(self):
        return f'{self.sku}: {self.daily_average} units'
