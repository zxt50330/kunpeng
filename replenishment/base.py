from datetime import datetime, timedelta

class Product:
    def __init__(self, production_time: int):
        self.production_time = production_time
        self.stock = 0

class Supplier:
    def __init__(self, product: Product):
        self.product = product

    def produce(self, quantity: int):
        self.product.stock += quantity

class Ship:
    def __init__(self, capacity: int, time_to_arrive: int):
        self.capacity = capacity
        self.time_to_arrive = time_to_arrive
        self.cargo = 0

class LogisticsSystem:
    def __init__(self, product: Product):
        self.product = product
        self.supplier = Supplier(self.product)
        self.ships = []
        self.stock = self.product.stock

    def add_ship(self, capacity: int, time_to_arrive: int):
        self.ships.append(Ship(capacity, time_to_arrive))

    def next_arrival(self):
        return min(ship.time_to_arrive for ship in self.ships)

    def update_ships(self):
        for ship in self.ships:
            if ship.time_to_arrive == 0:
                self.stock += ship.cargo
                ship.cargo = 0
            else:
                ship.time_to_arrive -= 1

    def replenish(self, quantity: int):
        self.supplier.produce(quantity)
        self.stock += quantity

    def ship_cargo(self, quantity: int):
        for ship in self.ships:
            if ship.cargo + quantity <= ship.capacity:
                ship.cargo += quantity
                return
        raise ValueError("No ship available to transport cargo")

    def simulate(self, days: int):
        for i in range(days):
            if i % self.product.production_time == 0:
                self.replenish(100)
            self.update_ships()
            sold = min(self.stock, 50)
            self.stock -= sold
            if self.stock < 100:
                self.supplier.produce(1000)
                self.stock += 1000
            while sold > 0:
                try:
                    self.ship_cargo(sold)
                    break
                except ValueError:
                    self.add_ship(5000, 30)
            print(f"Day {i}: Stock {self.stock}, Next arrival in {self.next_arrival()} days")


product = Product(30)
logistics = LogisticsSystem(product)

# Add one ship initially
logistics.add_ship(5000, 30)

# Simulate 200 days of sales
logistics.simulate(200)
