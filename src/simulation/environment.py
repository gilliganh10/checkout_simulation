# In environment.py

import simpy
from collections import Counter
from statistics import mean
from .customer import customer_generator, get_time_period, TimePeriod, Customer, CustomerType
from .checkout import Checkout
import random

class SimulationEnvironment:
    def __init__(self, duration=1020, initial_counters=5):
        self.env = simpy.Environment()
        self.duration = duration
        self.checkouts = [Checkout(self.env, i) for i in range(initial_counters)]
        self.customer_types = Counter()
        self.time_period_stats = {period: Counter() for period in TimePeriod}
        self.queue_log = []
        self.current_time = 0
        self.initial_counters = initial_counters
        self.customer_count = 0

        # Start the customer generator process
        self.env.process(self.customer_generator_process())

    def step(self):
        #print(f"Stepping simulation at time {self.current_time}")
        self.env.run(until=self.current_time + 1)
        self.current_time += 1
        self.update_queue_lengths()

    def customer_generator_process(self):
        while True:
            yield self.env.timeout(random.expovariate(1/5))  # Generate a customer every 5 minutes on average
            self.customer_count += 1
            customer = Customer(f'Customer {self.customer_count}', random.choice(list(CustomerType)))
            #print(f"Generated {customer.name} at time {self.env.now}")
            self.env.process(self.customer_process(customer))

    def customer_process(self, customer):
        #print(f"Processing {customer.name} at time {self.env.now}")
        shopping_time = customer.shopping_time()
        yield self.env.timeout(shopping_time)
        
        chosen_checkout = min(self.checkouts, key=lambda x: x.get_queue_length())
        #print(f"{customer.name} choosing checkout {chosen_checkout.id} at time {self.env.now}")
        
        chosen_checkout.update_queue_length(1)  # Increment queue length
        #print(f"Queue length for checkout {chosen_checkout.id} is now {chosen_checkout.get_queue_length()}")
        
        with chosen_checkout.queue.request() as request:
            yield request
            #print(f"{customer.name} started checkout at {chosen_checkout.id} at time {self.env.now}")
            checkout_time = customer.checkout_time()
            yield self.env.timeout(checkout_time)
        
        chosen_checkout.update_queue_length(-1)  # Decrement queue length
        #print(f"{customer.name} finished checkout at time {self.env.now}")
        #print(f"Queue length for checkout {chosen_checkout.id} is now {chosen_checkout.get_queue_length()}")

    def update_queue_lengths(self):
        queue_lengths = [checkout.get_queue_length() for checkout in self.checkouts]
        #print(f"Current time: {self.current_time}, Queue lengths: {queue_lengths}")
        #print(f"Total customers generated: {self.customer_count}")
        self.queue_log.append((self.current_time, queue_lengths, len(self.checkouts)))

    def get_average_queue_length(self):
        queue_lengths = [checkout.get_queue_length() for checkout in self.checkouts]
        avg_length = mean(queue_lengths) if queue_lengths else 0
        #print(f"Average queue length: {avg_length}")
        return avg_length

    def add_checkout(self):
        new_checkout = Checkout(self.env, len(self.checkouts))
        self.checkouts.append(new_checkout)
        #print(f"Added new checkout. Total checkouts: {len(self.checkouts)}")

    def remove_checkout(self):
        if len(self.checkouts) > 3:  # Ensure at least 3 checkouts remain open
            checkout_to_remove = min(self.checkouts, key=lambda x: x.get_queue_length())
            self.checkouts.remove(checkout_to_remove)
            #print(f"Removed a checkout. Total checkouts: {len(self.checkouts)}")

    def get_current_time_period(self):
        return get_time_period(self.current_time)

    def run(self):
        print("Starting simulation")
        self.env.run(until=self.duration)
        print("Simulation completed")
        self.print_statistics()

    def print_statistics(self):
        print("\nOverall customer type statistics:")
        for customer_type, count in self.customer_types.items():
            print(f"{customer_type.name}: {count}")

        print("\nCustomer type statistics by time period:")
        for period, stats in self.time_period_stats.items():
            print(f"\n{period.name}:")
            if not stats:
                print("  No customers")
            else:
                for customer_type, count in stats.items():
                    print(f"  {customer_type.name}: {count}")

    def update_customer_stats(self, customer, time):
        self.customer_types[customer.type] += 1
        current_time = (time + 360) % 1440  # Convert to 24-hour clock
        current_time_period = get_time_period(current_time)
        self.time_period_stats[current_time_period][customer.type] += 1
    

def run_simulation():
    sim_env = SimulationEnvironment()
    sim_env.run()
    return sim_env
