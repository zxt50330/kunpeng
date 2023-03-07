import math

from django.db import models, transaction
from datetime import datetime, timedelta

from inventory.models import Inventory
from products.models import Sku
from sales.models import DailySales


class ReplenishmentPlan(models.Model):
    arrival_date = models.DateField()
    sku = models.OneToOneField(Sku, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    # @staticmethod
    # def check_replenish():
    #     """
    #     判断是否要补货
    #     判断当前库存-天数x销量<安全库存 就要补货
    #     生产30天 物流60天 一次补货90条
    #     :return:
    #     """
    #     date_str = '2023-3-2'
    #     unfound_sku = []
    #     unfound_in = []
    #     start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #     daily_sales = DailySales.objects.all()
    #     for sku_ds in daily_sales:
    #         print(sku_ds.sku, sku_ds.daily_average)
    #         try:
    #             sku = Sku.objects.get(asku=sku_ds.sku)
    #         except Sku.DoesNotExist as e:
    #             unfound_sku.append(sku_ds.sku)
    #             print(f'未找到{sku_ds.sku}')
    #             continue
    #         # 当前库存
    #         try:
    #             inventory_obj = Inventory.objects.get(sku=sku)
    #         except Inventory.DoesNotExist as e:
    #             print(f'未找到{sku.name}库存')
    #             unfound_in.append(sku.name)
    #             continue
    #         # 当前库存能卖xx天
    #         inventory_coverage_days = inventory_obj.quantity / sku_ds.daily_average
    #         sku_inventory = inventory_obj.quantity
    #
    #         # 计算当前库存能支持的天数
    #         days_left = (inventory - batch_size * i) // daily_demand
    #
    #         # 计算距离现在需要多久开始备货
    #         lead_time = datetime.timedelta(days=days_per_batch * (i + 1) - days_left - 90)

    @staticmethod
    def sku_need(sku, quantity, present_stock, order_days=180, batch_size=90):
        """
        备货计算 根据日期预估一共需要多少货 然后反推订货以及发货的时间 目前先按180天计算
        :return:
        """
        # 预估指定天数内一共需要的销量
        total_sku_sales = quantity * order_days
        # 一共需要补的货
        need_re = total_sku_sales - present_stock
        if need_re > 0:
            # 需要补货的次数
            batch_times = need_re / batch_size

    @staticmethod
    def calculate_restock_date(stock=60, daily_sales=5, ship_date=60, batch_size=90):
        """
        根据当前库存和历史平均销量估计出未来销售情况，计算补货日期及数量
        :return:
        """
        can_sale_days = math.ceil(stock / daily_sales)
        # 每批次可售卖天数
        batch_sale_days = math.ceil(batch_size / daily_sales)
        if can_sale_days > ship_date:
            return print('不需要补货')
        else:
            print('补货')


class Ship(models.Model):
    SHIP_CHOICES = (
        ('fast', 'Fast Ship (30 days)'),
        ('slow', 'Slow Ship (60 days)'),
    )
    departure_date = models.DateField(null=True)
    arrival_date = models.DateField(null=True)
    sku = models.ForeignKey(Sku, on_delete=models.PROTECT)
    ship_type = models.CharField(max_length=4, choices=SHIP_CHOICES, null=True)
    quantity = models.IntegerField(null=True)
    arrival_quantity = models.IntegerField(null=True)
    cargo_loaded = models.BooleanField(default=False, null=True)
    remark = models.TextField(null=True)

    @staticmethod
    @transaction.atomic
    def create_plan(quantity, sku, order_date):
        """
        每次补货尽量满足只补90件
        ！！！理论上一天不超过90件就不会出问题 超过90件的话，会有问题，需要优化
        根据数量和到达时间，创建补货任务
        还需要判断到货那天之前的补货数量
        :return:
        """
        batch_size = 90
        # arrival_date = datetime.strptime(arrival_date_str, '%Y-%m-%d').date()

        # 计算最早需要下单的时间 目前按90天算 生产30先不算
        product_time = timedelta(days=30)
        lead_time = timedelta(days=60)
        # if quantity > 2000:
        #     lead_time = timedelta(days=60)
        arrival_date = order_date + lead_time

        # 创建补货计划
        # plan = ReplenishmentPlan(quantity=quantity, arrival_date=arrival_date)
        # plan.save()

        # 创建船只信息 目前写死补90
        # fast_ships_needed = 90
        # slow_ships_needed = 90
        # ships = []
        # for i in range(fast_ships_needed):
        # departure_date = order_date - timedelta(days=60)
        # arrival_date = order_date + timedelta(days=30)
        ship = Ship(departure_date=order_date, arrival_date=arrival_date, sku=sku,
                    ship_type='slow', quantity=batch_size)
        print(f'创建了补货 {sku} {arrival_date} 到达{batch_size}')
        ship.save()
        # ships.append(ship)
        # order_date = arrival_date
        # for i in range(slow_ships_needed):
        #     departure_date = order_date - timedelta(days=30)
        #     arrival_date = order_date + timedelta(days=60)
        #     ship = Ship(departure_date=departure_date, arrival_date=arrival_date,
        #                 ship_type='slow', cargo_quantity=500)
        #     ships.append(ship)
        #     order_date = arrival_date
        # Ship.objects.bulk_create(ships)
        return ship


def flow(sku, days=180):
    """
    设置安全库存 小于这个数就触发补货
    safe_stock = 0
    1. 获取平均销量
    2. 当前库存够售卖多久
    3.
    :return:
    """
    # 获取销量
    daily_sales = 1
    # 获取库存
    stock = 1
    # 获取初始在途库存
    on_way_stock = 0
    # 按日迭代
    for i in range(180):
        # 判断是否有在途到达
        if '日期相等':
            on_way_stock = ship.quantity
        stock = stock_flow(stock, daily_sales, on_way_stock)
        on_way_stock = 0
        # 判断是否需要补货
        if check_re():
            ship = Ship.create_ship()


