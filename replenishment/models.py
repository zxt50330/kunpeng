# 为了制定补货和生产计划，我们可以考虑以下几个步骤：
#
# 计算补货点：补货点是指库存水平下降到一定程度时需要进行补货的点位。由于慢船运输周期为60天，快船运输周期为30天，因此我们可以设置一个慢船和快船到达时间的阈值。例如，当库存水平降至60天销售量（即3000件）时，需要下订单补货。这样可以保证我们有足够的时间接收到货物。
#
# 制定补货计划：一旦库存水平降至补货点以下，我们就需要下订单补货。为了确保及时补货，可以在库存水平降至补货点以下的第二天下订单补货。如果销量突然激增，我们可以调整补货计划以适应需求。
#
# 制定生产计划：由于供应商生产需要30天，因此我们需要在库存水平降至补货点以下的30天前下订单生产。这样可以确保我们有足够的时间收到新的货物并避免缺货。
#
# 多班次航运：为了适应销量突然激增的情况，我们可以增加船运的班次。可以与供应商协商增加船次的频率，以便在需要时能够更快地收到货物。
#
# 下面是一个Python代码示例，用于计算补货点和制定补货及生产计划：
# 定义库存水平的初始值
import time

from db_conn import Base
from db_conn.database import session
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import threading


class DatabaseConnection(object):
    """
    A singleton class for database connection
    """
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                engine = create_engine('postgresql://:@localhost:5432/kunpeng', poolclass=QueuePool)
                Session = sessionmaker(bind=engine)
                cls._instance = super().__new__(cls)
                cls._instance.Session = scoped_session(Session)
        return cls._instance

    def get_session(self):
        """
        Returns a session object from the connection pool
        """
        return self.Session()


db = DatabaseConnection()
session = db.get_session()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    inventory = Column(Integer)
    sales_speed = Column(Float)
    production_time = Column(Integer)

    def __init__(self, name, inventory, sales_speed, production_time):
        self.name = name
        self.inventory = inventory
        self.sales_speed = sales_speed
        self.production_time = production_time
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    order_day = Column(Integer)
    quantity = Column(Integer)
    is_shipped = Column(Integer)

    def __init__(self, product_id, order_day, quantity, is_shipped):
        self.product_id = product_id
        self.order_day = order_day
        self.quantity = quantity
        self.is_shipped = is_shipped

# Base.metadata.create_all(create_engine('postgresql://:@localhost:5432/kunpeng'))
#
#Product
# session.add(product)
# session.commit()

import datetime
product = session.query(Product).first()

def calculate_demand(product, inventory_dict, orders, day):
    demand = product.sales_speed
    inventory = inventory_dict.get(day, product.inventory)
    for order in orders:
        if order.order_day + product.production_time + 30 <= day and not order.is_shipped:
            order.is_shipped = 1
            inventory += order.quantity
            session.commit()
    inventory -= demand
    if inventory < product.production_time * product.sales_speed:
        days_to_order = product.production_time - (len(inventory_dict) - day)
        order_day = day + days_to_order
        quantity = (product.production_time + 30) * product.sales_speed - inventory
        order = Order(product.id, order_day, quantity, 0)
        session.add(order)
        session.commit()
        inventory = inventory_dict.get(order_day - 1, product.inventory)
    inventory_dict[day] = inventory
    return demand

def simulate(product, days):
    inventory_dict = {1: 200, 2: 300, 3: 66}
    orders = []
    for day in range(days):
        demand = calculate_demand(product, inventory_dict, orders, day)
        print(f"Day {day}: demand={demand}, inventory={inventory_dict[day]}")
        if inventory_dict[day] < 0:
            print(f"Error: inventory is negative on day {day}")
    session.close()

simulate(product, 2)