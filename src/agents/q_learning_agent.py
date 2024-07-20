import numpy as np
import random

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
        print(f"Learning: State {state}, Action {action}, Reward {reward}, Next State {next_state}")
        print(f"Q-value updated from {predict} to {self.q_table[state, action]}")

def find_optimal_counters(q_table, state):
    optimal_action = np.argmax(q_table[state])
    optimal_counters = optimal_action + 1  # Assuming action + 1 gives the number of counters
    return optimal_counters