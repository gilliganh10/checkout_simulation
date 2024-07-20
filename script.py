import simpy
import random
import numpy as np

# Define the customer process
def customer(env, name, checkout_counters):
    print(f'{name} arrives at the store at {env.now:.2f}')
    shopping_time = random.uniform(5, 15)  # Time spent shopping
    yield env.timeout(shopping_time)
    print(f'{name} finishes shopping and arrives at checkout at {env.now:.2f}')
    # Choose the shortest queue
    counter = min(checkout_counters, key=lambda x: len(x.queue))
    with counter.request() as request:
        yield request
        print(f'{name} starts checkout at {env.now:.2f}')
        checkout_time = random.uniform(2, 5)  # Time spent at checkout
        yield env.timeout(checkout_time)
        print(f'{name} leaves the store at {env.now:.2f}')

# Define the customer generator process
def customer_generator(env, checkout_counters):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1/2))  # New customer every ~3 minutes
        i += 1
        env.process(customer(env, f'Customer {i}', checkout_counters))

# Define the AI agent (Q-learning)
class QLearningAgent:
    def __init__(self, n_states, n_actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(self.q_table.shape[1]))  # Explore
        else:
            return np.argmax(self.q_table[state])  # Exploit

    def learn(self, state, action, reward, next_state):
        predict = self.q_table[state, action]
        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (target - predict)

# Function to find the optimal number of counters for a given state
def find_optimal_counters(q_table, state):
    optimal_action = np.argmax(q_table[state])
    optimal_counters = optimal_action + 1  # Assuming action + 1 gives the number of counters
    return optimal_counters

# Define the AI-managed checkout counter process
def manage_counters(env, checkout_counters, agent):
    while True:
        yield env.timeout(1)  # Check every minute
        current_state = min(sum(len(counter.queue) for counter in checkout_counters), agent.q_table.shape[0] - 1)
        action = agent.choose_action(current_state)
        required_counters = action + 1  # Ensure at least one counter is open
        current_counters = len(checkout_counters)
        if required_counters > current_counters:
            for _ in range(required_counters - current_counters):
                checkout_counters.append(simpy.Resource(env, capacity=1))
        elif required_counters < current_counters:
            for _ in range(current_counters - required_counters):
                checkout_counters.pop()
        next_state = min(sum(len(counter.queue) for counter in checkout_counters), agent.q_table.shape[0] - 1)
        reward = -next_state  # Reward is negative queue length to minimize waiting
        agent.learn(current_state, action, reward, next_state)

# Set up the environment and run the simulation
env = simpy.Environment()
checkout_counters = [simpy.Resource(env, capacity=1) for _ in range(2)]  # Initial number of checkout counters
agent = QLearningAgent(n_states=50, n_actions=5)  # Example state and action spaces
env.process(customer_generator(env, checkout_counters))
env.process(manage_counters(env, checkout_counters, agent))
env.run(until=600)  # Run the simulation for 120 minutes

# Print Q-table for analysis
print(agent.q_table)

# Example: Finding the optimal number of counters for state 3
state = 3
optimal_counters = find_optimal_counters(agent.q_table, state)
print(f"Optimal number of checkout counters for state {state}: {optimal_counters}")
