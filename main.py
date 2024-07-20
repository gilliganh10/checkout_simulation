from src.simulation.environment import SimulationEnvironment
from src.agents.q_learning_agent import QLearningAgent, find_optimal_counters
from src.simulation.customer import TimePeriod
from src.simulation.environment import run_simulation

def main():
    sim_env = run_simulation()  # Run for 12 hours
    return sim_env

if __name__ == "__main__":
    main()
