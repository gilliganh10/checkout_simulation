from src.simulation.environment import SimulationEnvironment
from src.agents.q_learning_agent import QLearningAgent, train_agent, find_optimal_checkouts
from src.simulation.customer import TimePeriod, get_time_period
import matplotlib.pyplot as plt

def main():
    # Train the agent
    agent, rewards = train_agent(n_episodes=1000)

    # Plot the rewards
    plt.figure(figsize=(12, 6))
    plt.plot(rewards)
    plt.title('Rewards over Episodes')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.show()

    # Find and print the optimal number of checkouts
    env = SimulationEnvironment()  # Create a sample environment
    optimal_checkouts = find_optimal_checkouts(agent, env)

    print("\nOptimal number of checkouts by hour and time period:")
    for hour in range(24):
        time_period = get_time_period(hour * 60)
        n_checkouts = optimal_checkouts[(hour, time_period)]
        print(f"Hour: {hour:02d}:00, Time Period: {time_period.name}, Optimal Checkouts: {n_checkouts}")

    # Visualize optimal checkouts
    plt.figure(figsize=(12, 6))
    hours = range(24)
    checkouts = [optimal_checkouts[(hour, get_time_period(hour * 60))] for hour in hours]
    plt.plot(hours, checkouts, marker='o')
    plt.title('Optimal Number of Checkouts Throughout the Day')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Checkouts')
    plt.xticks(hours)
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()