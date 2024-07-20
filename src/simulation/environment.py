import simpy
from collections import Counter
from statistics import mean
from .customer import customer_generator, get_time_period, TimePeriod
from .checkout import Checkout

class SimulationEnvironment:
    def __init__(self, duration=1020, initial_counters=5):  # 1020 minutes = 17 hours (06:00 to 23:00)
        self.env = simpy.Environment()
        self.duration = duration
        self.checkouts = [Checkout(self.env, i) for i in range(initial_counters)]
        self.customer_types = Counter()
        self.time_period_stats = {period: Counter() for period in TimePeriod}
        self.queue_log = []
        self.current_time = 0
        self.initial_counters = initial_counters

    def step(self):
        # Advance the simulation by one time step (e.g., 1 minute)
        self.env.run(until=self.current_time + 1)
        self.current_time += 1

    def log_queue_length(self):
        queue_lengths = [checkout.get_queue_length() for checkout in self.checkouts]
        total_queue_length = sum(queue_lengths)
        avg_queue_length = mean(queue_lengths) if queue_lengths else 0
        n_counters = len(self.checkouts)
        self.queue_log.append((self.env.now, queue_lengths, n_counters))
        
        current_time = (self.env.now + 360) % 1440  # Convert to 24-hour clock
        hours, minutes = divmod(current_time, 60)
        
        print(f"\nTime: {hours:02d}:{minutes:02d}")
        print(f"Total Queue Length: {total_queue_length}")
        print(f"Average Queue Length: {avg_queue_length:.2f}")
        print(f"Open Counters: {n_counters}")
        print("Queue lengths for each checkout:")
        for i, length in enumerate(queue_lengths):
            print(f"  Checkout {i}: {length} customers")

    def run(self):
        self.env.process(self.customer_generator_process())
        # Remove the manage_counters process to disable automatic counter management
        # self.env.process(self.manage_counters())
        self.env.process(self.queue_logger_process())
        self.env.run(until=self.duration)
        self.print_statistics()

    def queue_logger_process(self):
        while True:
            yield self.env.timeout(15)  # Log every 15 minutes
            self.log_queue_length()

    def update_customer_stats(self, customer, time):
        self.customer_types[customer.type] += 1
        current_time = (time + 360) % 1440  # Convert to 24-hour clock
        current_time_period = get_time_period(current_time)
        self.time_period_stats[current_time_period][customer.type] += 1

    def customer_generator_process(self):
        return customer_generator(self.env, self.checkouts, self.update_customer_stats)

    def get_average_queue_length(self):
        queue_lengths = [checkout.get_queue_length() for checkout in self.checkouts]
        return mean(queue_lengths) if queue_lengths else 0
    
    def add_checkout(self):
        self.checkouts.append(Checkout(self.env, len(self.checkouts)))

    def remove_checkout(self):
        if len(self.checkouts) > 3:  # Ensure at least 3 checkouts remain open
            checkout_to_remove = min(self.checkouts, key=lambda x: x.get_queue_length())
            self.checkouts.remove(checkout_to_remove)

    def get_current_time_period(self):
        return get_time_period(self.current_time)

    # Remove the manage_counters method to avoid confusion
    # def manage_counters(self):
    #     while True:
    #         yield self.env.timeout(5)  # Check every 5 minutes
    #         avg_queue_length = self.get_average_queue_length()
    #         current_counters = len(self.checkouts)

    #         if avg_queue_length > 2.5 and current_counters < 20:  # Increased max counters to 20
    #             print(f"\nAdding a new checkout. Current average queue length: {avg_queue_length:.2f}")
    #             self.checkouts.append(Checkout(self.env, len(self.checkouts)))
    #         elif avg_queue_length < 2 and current_counters > 2:  # Ensuring at least 3 checkouts are always open
    #             print(f"\nRemoving a checkout. Current average queue length: {avg_queue_length:.2f}")
    #             # Remove the checkout with the shortest queue
    #             checkout_to_remove = min(self.checkouts, key=lambda x: x.get_queue_length())
    #             self.checkouts.remove(checkout_to_remove)

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

def run_simulation():
    sim_env = SimulationEnvironment()
    sim_env.run()
    return sim_env
