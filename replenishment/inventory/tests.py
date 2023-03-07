from datetime import datetime, timedelta
import math


def calculate_restock_date(stock, daily_sales, ship_time, batch_size):
    """
    根据当前库存和历史平均销量估计出未来销售情况，计算补货日期及数量
    """
    restock_days = math.ceil((stock + ship_time * daily_sales) / (batch_size * daily_sales)) * 90
    restock_date = datetime.now() + timedelta(days=restock_days)
    restock_qty = batch_size * math.ceil((stock + ship_time * daily_sales) / (batch_size * daily_sales))
    return restock_date, restock_qty


def calculate_optimal_restock_date(stock, daily_sales, ship_time, batch_size, in_transit):
    """
    根据当前库存、历史平均销量和在途数量，计算最优的补货日期及数量
    """
    restock_date_1, restock_qty_1 = calculate_restock_date(stock, daily_sales, ship_time[0], batch_size)
    restock_date_2, restock_qty_2 = calculate_restock_date(stock + sum([i[1] for i in in_transit]), daily_sales, ship_time[1], batch_size)

    if in_transit:
        transit_arrival_dates = [i[0] for i in in_transit]
        next_arrival_date = min(transit_arrival_dates)
        days_to_next_arrival = (next_arrival_date - datetime.now()).days

        if days_to_next_arrival <= restock_date_1:
            # 下一批货物到达时刻比第一次补货时刻更早
            return next_arrival_date, in_transit[0][1] + batch_size
        elif restock_date_1 < days_to_next_arrival <= restock_date_2:
            # 第一次补货时刻比下一批货物到达时刻早，但比第二次补货时刻早
            return restock_date_1, restock_qty_1
        else:
            # 第二次补货时刻比下一批货物到达时刻早，或者到达时间超出了补货周期
            return restock_date_2, restock_qty_2
    else:
        return restock_date_2, restock_qty_2


def calculate_optimal_restock_dates(stock, daily_sales, ship_time, batch_size, in_transit=None, num_of_restocks=4):
    """
    根据历史销量和在途信息计算多批次补货计划
    """
    restock_plan = []
    for i in range(num_of_restocks):
        if i == 0:
            restock_date, restock_qty = calculate_optimal_restock_date(stock, daily_sales, ship_time, batch_size, in_transit)
        else:
            in_transit = [(i[0] - datetime.now(), i[1]) for i in restock_plan[-1][2]]
            restock_date, restock_qty = calculate_optimal_restock_date(stock, daily_sales, ship_time, batch_size, in_transit)
        stock += restock_qty
        restock_plan.append((restock_date, restock_qty, in_transit))
    return restock_plan

print(calculate_optimal_restock_dates(60, 5, 60, 90))