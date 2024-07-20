import simpy
from collections import Counter
from .customer import customer_generator, customer_process, Customer, CustomerType, get_time_period, TimePeriod
from ..agents.q_learning_agent import QLearningAgent

class SimulationEnvironment:
    def __init__(self, duration=720, initial_counters=2, n_states=125, n_actions=5):
        self.env = simpy.Environment()
        self.duration = duration
        self.checkout_counters = [simpy.Resource(self.env, capacity=1) for _ in range(initial_counters)]
        self.agent = None  # Will be set later
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
        return self.agent

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

    def get_current_state(self):
        queue_length = sum(len(counter.queue) for counter in self.checkout_counters)
        n_counters = len(self.checkout_counters)
        current_time_period = get_time_period(self.env.now)
        
        # Discretize the state space
        if queue_length == 0:
            queue_state = 0
        elif queue_length <= 5:
            queue_state = 1
        elif queue_length <= 10:
            queue_state = 2
        elif queue_length <= 20:
            queue_state = 3
        else:
            queue_state = 4
        
        # Combine time period, queue state, and number of counters into a single state
        return current_time_period.value * 25 + queue_state * 5 + (n_counters - 1)

    def get_reward(self, state, action):
        queue_length = sum(len(counter.queue) for counter in self.checkout_counters)
        n_counters = action + 1
        current_time_period = get_time_period(self.env.now)
        
        # Cost per counter per time unit
        counter_cost = 10
        
        # Estimated cost of customer waiting (higher during busy periods)
        wait_cost = 5 if current_time_period in [TimePeriod.LUNCH, TimePeriod.EVENING] else 2
        
        # Calculate total cost
        total_cost = (counter_cost * n_counters) + (wait_cost * queue_length)
        
        # Convert cost to reward (negative cost)
        reward = -total_cost
        
        return reward

    def manage_counters(self):
        while True:
            yield self.env.timeout(5)  # Check every 5 minutes
            self.log_queue_length()  # Log before taking action
            current_state = self.get_current_state()
            action = self.agent.choose_action(current_state)
            self.adjust_counters(action)
            yield self.env.timeout(5)  # Wait for 5 minutes to see the effect
            self.log_queue_length()  # Log after taking action
            next_state = self.get_current_state()
            reward = self.get_reward(next_state, action)
            self.agent.learn(current_state, action, reward, next_state)

    def adjust_counters(self, action):
        required_counters = action + 1  # Ensure at least one counter is open
        current_counters = len(self.checkout_counters)
        if required_counters > current_counters:
            for _ in range(required_counters - current_counters):
                self.checkout_counters.append(simpy.Resource(self.env, capacity=1))
        elif required_counters < current_counters:
            for _ in range(current_counters - required_counters):
                self.checkout_counters.pop()

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
        """
        print("\nQueue Length Log:")
        for time, queue_length, n_counters in self.queue_log:
            if queue_length > 0:
                print(f"Time: {time:.2f}, Queue Length: {queue_length}, Open Counters: {n_counters}")
"""
def run_simulation(duration=24*60):
    sim_env = SimulationEnvironment(duration=duration, n_states=125, n_actions=5)
    sim_env.agent = QLearningAgent(n_states=125, n_actions=5, alpha=0.1, gamma=0.99, epsilon=0.1)
    return sim_env.run()