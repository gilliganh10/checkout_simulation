import simpy
from collections import Counter
from .customer import customer_generator, get_time_period, TimePeriod

class SimulationEnvironment:
    def __init__(self, duration=720, initial_counters=2):
        self.env = simpy.Environment()
        self.duration = duration
        self.checkout_counters = [simpy.Resource(self.env, capacity=1) for _ in range(initial_counters)]
        self.customer_types = Counter()
        self.time_period_stats = {period: Counter() for period in TimePeriod}
        self.queue_log = []
    
    def log_queue_length(self):
        total_queue_length = sum(len(counter.queue) for counter in self.checkout_counters)
        n_counters = len(self.checkout_counters)
        self.queue_log.append((self.env.now, total_queue_length, n_counters))
        if total_queue_length > 0:
            print(f"Time: {self.env.now:.2f}, Queue Length: {total_queue_length}, Open Counters: {n_counters}")

    def run(self):
        self.env.process(self.customer_generator_process())
        self.env.process(self.manage_counters())
        self.env.process(self.queue_logger_process())
        self.env.run(until=self.duration)
        self.print_statistics()

    def queue_logger_process(self):
        while True:
            yield self.env.timeout(5)  # Log every 5 minutes
            self.log_queue_length()

    def update_customer_stats(self, customer, time):
        self.customer_types[customer.type] += 1
        current_time_period = get_time_period(time)
        self.time_period_stats[current_time_period][customer.type] += 1

    def customer_generator_process(self):
        return customer_generator(self.env, self.checkout_counters, self.update_customer_stats)

    def get_total_queue_length(self):
        return sum(len(counter.queue) for counter in self.checkout_counters)

    def manage_counters(self):
        while True:
            yield self.env.timeout(1)  # Check every 5 minutes
            total_queue_length = self.get_total_queue_length()
            current_counters = len(self.checkout_counters)

            if total_queue_length > 5 and current_counters < 100:  # Assuming a maximum of 5 counters
                print(f"Adding a counter. Queue length: {total_queue_length}")
                self.checkout_counters.append(simpy.Resource(self.env, capacity=1))
            elif total_queue_length < 3 and current_counters > 1:  # Ensuring at least 1 counter is always open
                print(f"Removing a counter. Queue length: {total_queue_length}")
                self.checkout_counters.pop()

            self.log_queue_length()

    def print_statistics(self):
        print("Overall customer type statistics:")
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

def run_simulation(duration=24*60):
    sim_env = SimulationEnvironment(duration=duration)
    sim_env.run()
    return sim_env