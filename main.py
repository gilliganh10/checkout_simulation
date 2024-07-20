from src.simulation.environment import SimulationEnvironment
from src.agents.q_learning_agent import QLearningAgent, find_optimal_counters
from src.simulation.customer import TimePeriod

def main():
    # Create a simulation environment
    sim_env = SimulationEnvironment(duration=72*60, initial_counters=2, n_states=125, n_actions=5)
    
    # Create and set the Q-learning agent with specified parameters
    sim_env.agent = QLearningAgent(n_states=125, n_actions=5, alpha=0.1, gamma=0.99, epsilon=0.1)
    
    # Run the simulation
    agent = sim_env.run()
    
    # Print Q-table for analysis
    print("\nQ-table:")
    print(agent.q_table)

    # Analysis of Q-table by time period and queue state
    print("\nAnalysis of Q-table:")
    for time_period in TimePeriod:
        print(f"\nTime Period: {time_period.name}")
        for queue_state in range(5):
            print(f"  Queue State: {queue_state}")
            for counter_state in range(5):
                state = time_period.value * 25 + queue_state * 5 + counter_state
                optimal_action = agent.q_table[state].argmax()
                optimal_counters = optimal_action + 1  # +1 because actions are 0-indexed
                print(f"    Current Counters: {counter_state + 1}, Optimal Counters: {optimal_counters}")

if __name__ == "__main__":
    main()