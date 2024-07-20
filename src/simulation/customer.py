from enum import Enum
import random

class CustomerType(Enum):
    QUICK = 1
    REGULAR = 2
    LENGTHY = 3

class TimePeriod(Enum):
    EARLY_MORNING = 0
    MORNING = 1
    LUNCH = 2
    AFTERNOON = 3
    EVENING = 4
    LATE_EVENING = 5

class Customer:
    def __init__(self, name, customer_type):
        self.name = name
        self.type = customer_type

    def shopping_time(self):
        if self.type == CustomerType.QUICK:
            return random.uniform(5, 10)
        elif self.type == CustomerType.REGULAR:
            return random.uniform(11, 20)
        elif self.type == CustomerType.LENGTHY:
            return random.uniform(21, 40)

    def checkout_time(self):
        if self.type == CustomerType.QUICK:
            return random.uniform(1, 2)
        elif self.type == CustomerType.REGULAR:
            return random.uniform(3, 5)
        elif self.type == CustomerType.LENGTHY:
            return random.uniform(5, 7)
        
        

def get_time_period(current_time):
    hours = (current_time // 60) % 24  # Convert minutes to hours
    if 6 <= hours < 9:
        return TimePeriod.EARLY_MORNING
    elif 9 <= hours < 12:
        return TimePeriod.MORNING
    elif 12 <= hours < 14:
        return TimePeriod.LUNCH
    elif 14 <= hours < 17:
        return TimePeriod.AFTERNOON
    elif 17 <= hours < 20:
        return TimePeriod.EVENING
    elif 20 <= hours < 23:
        return TimePeriod.LATE_EVENING
    else:
        return TimePeriod.EARLY_MORNING  # From 23:00 to 06:00, consider it early morning of the next day

print("Time periods:")
for hour in range(24):
    period = get_time_period(hour * 60)
    print(f"{hour:02d}:00 - {period.name}")
def get_arrival_rate(time_period):
    rates = {
        TimePeriod.EARLY_MORNING: 1/1.5,  # 1 customer every 1.5 minutes
        TimePeriod.MORNING: 1/1,          # 1 customer every minute
        TimePeriod.LUNCH: 1/0.5,          # 2 customers every minute
        TimePeriod.AFTERNOON: 1/0.75,        # 1 customer every minute
        TimePeriod.EVENING: 1/1,       
        TimePeriod.LATE_EVENING: 1/2      # 1 customer every 2 minutes
    }
    return rates[time_period]

def get_customer_type_probabilities(time_period):
    probabilities = {
        TimePeriod.EARLY_MORNING: [0.5, 0.4, 0.1],  # [QUICK, REGULAR, LENGTHY]
        TimePeriod.MORNING: [0.4, 0.4, 0.2],
        TimePeriod.LUNCH: [0.7, 0.2, 0.1],
        TimePeriod.AFTERNOON: [0.3, 0.4, 0.3],
        TimePeriod.EVENING: [0.3, 0.5, 0.2],
        TimePeriod.LATE_EVENING: [0.8, 0.2, 0]
    }
    return probabilities[time_period]

def customer_process(env, customer, checkouts, stats_updater):
    stats_updater(customer, env.now)  # Update statistics when customer arrives
    shopping_time = customer.shopping_time()
    yield env.timeout(shopping_time)
    
    # Choose the checkout with the shortest queue
    chosen_checkout = min(checkouts, key=lambda x: x.get_queue_length())
    
    with chosen_checkout.queue.request() as request:
        yield request
        checkout_time = customer.checkout_time()
        yield env.timeout(checkout_time)

def customer_generator(env, checkouts, stats_updater):
    i = 0
    while True:
        current_time = env.now
        time_period = get_time_period(current_time)
        arrival_rate = get_arrival_rate(time_period)
        customer_type_probabilities = get_customer_type_probabilities(time_period)

        inter_arrival_time = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival_time)

        i += 1
        customer_type = random.choices(list(CustomerType), weights=customer_type_probabilities)[0]
        customer = Customer(f'Customer {i}', customer_type)
        
        env.process(customer_process(env, customer, checkouts, stats_updater))