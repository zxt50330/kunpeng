import csv
from django.shortcuts import render
from .models import AmazonOrder


def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            reader = csv.DictReader(file)
            for row in reader:
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
                order.save()
    return render(request, 'upload.html')
