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

class Customer:
    def __init__(self, name, customer_type):
        self.name = name
        self.type = customer_type

    def shopping_time(self):
        if self.type == CustomerType.QUICK:
            return random.uniform(2, 5)
        elif self.type == CustomerType.REGULAR:
            return random.uniform(5, 15)
        elif self.type == CustomerType.LENGTHY:
            return random.uniform(10, 30)

    def checkout_time(self):
        return random.uniform(1, 5)

def get_time_period(current_time):
    hours = (current_time % (24 * 60)) // 60  # Convert to hours within a day
    if 6 <= hours < 8:
        return TimePeriod.EARLY_MORNING
    elif 8 <= hours < 11:
        return TimePeriod.MORNING
    elif 11 <= hours < 14:
        return TimePeriod.LUNCH
    elif 14 <= hours < 17:
        return TimePeriod.AFTERNOON
    else:
        return TimePeriod.EVENING

def get_arrival_rate(time_period):
    rates = {
        TimePeriod.EARLY_MORNING: 1/1,  # One customer every 5 minutes on average
        TimePeriod.MORNING: 1/1,       # One customer every 3 minutes on average
        TimePeriod.LUNCH: 1/.25,         # One customer every 1 minute on average
        TimePeriod.AFTERNOON: 1/2,     # One customer every 4 minutes on average
        TimePeriod.EVENING: 1/1        # One customer every 2 minutes on average
    }
    return rates[time_period]

def get_customer_type_probabilities(time_period):
    probabilities = {
        TimePeriod.EARLY_MORNING: [0.6, 0.3, 0.1],  # [QUICK, REGULAR, LENGTHY]
        TimePeriod.MORNING: [0.4, 0.4, 0.2],
        TimePeriod.LUNCH: [0.7, 0.2, 0.1],
        TimePeriod.AFTERNOON: [0.3, 0.5, 0.2],
        TimePeriod.EVENING: [0.2, 0.5, 0.3]
    }
    return probabilities[time_period]

def customer_process(env, customer, checkout_counters, stats_updater):
    stats_updater(customer, env.now)  # Update statistics when customer arrives
    shopping_time = customer.shopping_time()
    yield env.timeout(shopping_time)
    
    counter = min(checkout_counters, key=lambda x: len(x.queue))
    
    with counter.request() as request:
        yield request
        checkout_time = customer.checkout_time()
        yield env.timeout(checkout_time)
        # Customer leaves the counter here, and resource is released automatically

def customer_generator(env, checkout_counters, stats_updater):
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
        
        env.process(customer_process(env, customer, checkout_counters, stats_updater))
