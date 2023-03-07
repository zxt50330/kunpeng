from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date, datetime
from plans.models import Ship
from sales.models import DailySales
from inventory.models import Inventory
from products.models import Sku


def check_re(sku, stock, daily_sales, ship_day, order_date):
    """
    是否需要补货
    根据天数计算出当前库存是否够卖
    结合批次数量够卖天数

    ship_day: 补货周期
    :return:
    """
    if (stock / daily_sales) > ship_day:
        return False
    else:
        # 节省性能
        lead_time = timedelta(days=60)
        arrival_date = order_date + lead_time
        on_way_stock = sum([ship.quantity for ship in Ship.objects.filter(sku=sku,
                                                                          arrival_date__lt=arrival_date,
                                                                          cargo_loaded=False)])
        if ((stock + on_way_stock) / daily_sales) > ship_day:
            print(f'xxxxxxxxxxxx触发了在途库存逻辑 {arrival_date} 之前有 {on_way_stock} 到达')
            return False
        return True


def stock_flow(stock, daily_sales, on_way_stock=0):
    """
    库存流水 分为2部分
    在途和fba
    每日跑一次
    :return:
    """
    # 库存每日减少
    stock -= daily_sales
    # 库存到达，库存增加
    if on_way_stock:
        stock += on_way_stock
    return stock


class Command(BaseCommand):
    help = 'Check inventory levels and create replenishment plans if necessary'

    def handle(self, *args, **options):
        """
        一批货补90条
        :param args:
        :param options:
        :return:
        """
        # Calculate average daily sales from last 30 days sales data
        # last_month_sales = DailySales.objects.filter(date__range=(timezone.now().date() - timedelta(days=30), timezone.now().date()))
        # total_sales = sum(sales.sales for sales in last_month_sales)
        # average_sales = total_sales / 30 if total_sales else 50  # Default to 50 if there is no sales data
        # Calculate number of days of slow shipping and fast shipping
        slow_shipping_days = 60
        fast_shipping_days = 30
        # 获取平均销量
        date_str = '2023-3-2'
        unfound_sku = []
        unfound_in = []
        start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        daily_sales = DailySales.objects.all()
        for sku_ds in daily_sales:
            if sku_ds.sku not in ['01-ROZS-TNOT']:
                continue
            print(sku_ds.sku, sku_ds.daily_average)
            try:
                sku = Sku.objects.get(asku=sku_ds.sku)
            except Sku.DoesNotExist as e:
                unfound_sku.append(sku_ds.sku)
                print(f'未找到{sku_ds.sku}')
                continue
            # 当前库存
            try:
                inventory_obj = Inventory.objects.get(sku=sku)
            except Inventory.DoesNotExist as e:
                print(f'未找到{sku.name}库存')
                unfound_in.append(sku.name)
                continue
            # 当前库存能卖xx天
            inventory_coverage_days = inventory_obj.quantity / sku_ds.daily_average
            sku_inventory = inventory_obj.quantity
            print(inventory_coverage_days)
            print('---------'*100)
            print(f'sku:{sku_ds.sku}, 库存:{sku_inventory}, 日平均销量:{sku_ds.daily_average}, '
                  f'预估天数:{inventory_coverage_days}')
            # for i in range(90):
            #     today = start_date + timedelta(days=i)
            #     if sku_inventory <= 0:
            #         print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}'
            #           f', 日平均销量:{sku_ds.daily_average} -----------------断货')
            #         sku_inventory = 0  # 断货清0 可以不用重复赋值
            #     else:
            #         sku_inventory -= sku_ds.daily_average
            #         print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}'
            #               f', 日平均销量:{sku_ds.daily_average}')
            #     # 在途库存
            #     ships = Ship.objects.filter(sku=sku, arrival_date=today)
            #     if ships:
            #         tmp = 0
            #         for ship in ships:
            #             # 加库存
            #             tmp += ship.quantity
            #         sku_inventory += tmp
            #         print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}'
            #               f', 补货:{tmp}')
            for i in range(90):
                on_way_stock = 0
                today = start_date + timedelta(days=i)
                # 在途计算
                for ship in Ship.objects.filter(sku=sku, arrival_date=today, cargo_loaded=False):
                    on_way_stock = sum([ship.quantity])
                    ship.cargo_loaded = True
                    ship.save()
                if on_way_stock:
                    print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}, 补货:{on_way_stock}+++++++')
                sku_inventory = stock_flow(sku_inventory, sku_ds.daily_average, on_way_stock)
                if sku_inventory <= 0:
                    print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}'
                          f', 日平均销量:{sku_ds.daily_average} -----------------断货')
                    sku_inventory = 0  # 断货清0 可以不用重复赋值
                else:
                    print(f'日期:{today}, sku:{sku_ds.sku}, 库存:{sku_inventory}, 日平均销量:{sku_ds.daily_average}')
                if check_re(sku, sku_inventory, sku_ds.daily_average, 90, today):
                    # 可以建快船 生产30天先不计算
                    Ship.create_plan(90, sku, today)
        print(f'未找到sku{unfound_sku}, 未找到库存{unfound_in}')


            # Check if inventory coverage is below slow shipping time
            # if inventory_coverage_days < slow_shipping_days:
            #     # Create replenishment plan for 1000 units, fast shipping time from now
            #     arrival_date = timezone.now().date() + timedelta(days=fast_shipping_days)
            #     quantity = 1000
            #     plan = ReplenishmentPlan.objects.create(arrival_date=arrival_date, quantity=quantity)
            #     plan.calculate_shipment_information()
            #
            #     self.stdout.write(self.style.SUCCESS(f'Created replenishment plan: {plan.arrival_date}, {plan.quantity}, {plan.ships}'))
            # else:
            #     self.stdout.write(self.style.SUCCESS('Inventory levels are sufficient'))

        # Log daily sales
        # today = timezone.now().date()
        # try:
        #     daily_sales = DailySales.objects.get(date=today)
        #     daily_sales.sales = current_inventory if current_inventory > 0 else 0
        #     daily_sales.save()
        # except DailySales.DoesNotExist:
        #     daily_sales = DailySales.objects.create(date=today, sales=current_inventory if current_inventory > 0 else 0)

        # Print inventory and sales information
        # self.stdout.write(self.style.SUCCESS(f'Inventory: {current_inventory} units'))
        # self.stdout.write(self.style.SUCCESS(f'Average daily sales: {average_sales} units'))
        # self.stdout.write(self.style.SUCCESS(f'Inventory coverage: {inventory_coverage_days:.1f} days'))
        # self.stdout.write(self.style.SUCCESS(f'Sales today: {daily_sales.sales} units'))
