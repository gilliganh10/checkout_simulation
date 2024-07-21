import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from src.simulation.environment import SimulationEnvironment
from src.simulation.customer import TimePeriod

class QLearningAgent:
    def __init__(self, n_actions, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.1):
        self.q_table = defaultdict(lambda: np.zeros(n_actions))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate

    def get_state(self, env):
        avg_queue_length = env.get_average_queue_length()
        time_period = env.get_current_time_period()
        return (avg_queue_length, time_period)

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.choice(len(self.q_table[state]))
        else:
            return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        current_q = self.q_table[state][action]
        next_max_q = np.max(self.q_table[next_state])
        new_q = current_q + self.lr * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state][action] = new_q

def run_episode(env, agent, episode):
    state = agent.get_state(env)
    total_reward = 0
    
    print(f"Starting episode {episode}")
    
    for step in range(env.duration):
        action = agent.choose_action(state)
        
        #print(f"Step {step}: Chosen action: {action}")
        
        if action == 0:  # Do nothing
            pass
        elif action == 1:  # Add a checkout
            env.add_checkout()
            #print(f"Added checkout. Total checkouts: {len(env.checkouts)}")
        elif action == 2:  # Remove a checkout
            env.remove_checkout()
            #print(f"Removed checkout. Total checkouts: {len(env.checkouts)}")
        
        env.step()
        
        reward = calculate_reward(env)
        total_reward += reward
        
        next_state = agent.get_state(env)
        
        agent.learn(state, action, reward, next_state)
        
        state = next_state
        
        #print(f"Step {step} completed. Reward: {reward}, Total reward: {total_reward}")
    
    print(f"Episode {episode} completed with total reward: {total_reward}")
    return total_reward


def calculate_reward(env):
    avg_queue_length = env.get_average_queue_length()
    n_checkouts = len(env.checkouts)
    
    reward = -avg_queue_length - 0.5 * n_checkouts
    
    #print(f"Calculating reward: avg_queue_length = {avg_queue_length}, n_checkouts = {n_checkouts}")
    
    if avg_queue_length > 2.5:
        reward -= (avg_queue_length - 2.5) ** 2
    
    if n_checkouts > 4:
        reward -= (n_checkouts - 5) ** 2
    
    
    return reward

def train_agent(n_episodes=1000):
    agent = QLearningAgent(n_actions=3)
    rewards = []
    
    for episode in range(n_episodes):
        #print(f"\nStarting episode {episode}")
        env = SimulationEnvironment()
        episode_reward = run_episode(env, agent, episode)
        rewards.append(episode_reward)
        #print(f"Episode {episode} completed. Total reward: {episode_reward}")
    
    return agent, rewards

def find_optimal_strategy(agent):
    optimal_strategy = {}
    for time_period in TimePeriod:
        for avg_queue_length in range(0, 21):  # Assuming max average queue length of 20
            state = (avg_queue_length, time_period)
            action = np.argmax(agent.q_table[state])
            optimal_strategy[state] = action
    return optimal_strategy


def find_optimal_checkouts(agent, env):
    optimal_checkouts = {}
    for time_period in TimePeriod:
        for hour in range(24):
            state = (0, time_period)  # Start with 0 average queue length
            n_checkouts = env.initial_counters  # Start with initial number of counters
            
            # Simulate decision making for this hour
            for _ in range(60):  # Assume decisions can be made every minute
                action = np.argmax(agent.q_table[state])
                if action == 1:  # Add checkout
                    n_checkouts += 1
                elif action == 2 and n_checkouts > 3:  # Remove checkout, but keep at least 3
                    n_checkouts -= 1
                
                # Update state (assume average queue length stays at 0 for simplicity)
                state = (0, time_period)
            
            optimal_checkouts[(hour, time_period)] = n_checkouts
    
    return optimal_checkouts

def plot_metrics(env):
    # Extracting logged data
    times = [log[0] for log in env.queue_log]
    avg_queue_lengths = [np.mean(log[1]) for log in env.queue_log]
    num_checkouts = [log[2] for log in env.queue_log]
    
    # Plotting Average Queue Length over Time
    plt.figure(figsize=(12, 6))
    plt.plot(times, avg_queue_lengths, label='Average Queue Length')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Average Queue Length')
    plt.title('Average Queue Length over Time')
    plt.legend()
    plt.show()
    
    # Plotting Number of Checkouts over Time
    plt.figure(figsize=(12, 6))
    plt.plot(times, num_checkouts, label='Number of Checkouts', color='orange')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Number of Checkouts')
    plt.title('Number of Checkouts over Time')
    plt.legend()
    plt.show()
