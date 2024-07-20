# Retail Checkout Simulation

## Overview
This project simulates a retail environment to optimize the number of open checkouts throughout the day. It uses Q-learning, a reinforcement learning technique, to determine the optimal number of checkouts for different time periods, aiming to balance customer wait times and operational costs.

## Key Features
- Simulates customer arrivals and checkout processes
- Implements a Q-learning agent to optimize checkout management
- Considers different time periods and customer types
- Provides visualizations of rewards and optimal checkout numbers

## Project Structure
- `main.py`: Entry point of the application
- `src/simulation/`:
  - `environment.py`: Defines the simulation environment
  - `customer.py`: Implements customer behavior and time periods
  - `checkout.py`: Defines the checkout process
- `src/agents/`:
  - `q_learning_agent.py`: Implements the Q-learning agent and training process

## How to Run
1. Ensure you have Python 3.7+ installed
2. Install required dependencies: `pip install -r requirements.txt`
3. Run the main script: `python main.py`

## Results
The simulation provides insights into the optimal number of checkouts for each hour and time period. Here's a sample of the latest results:

```
Hour: 00:00, Time Period: EARLY_MORNING, Optimal Checkouts: 3
Hour: 09:00, Time Period: MORNING, Optimal Checkouts: 3
Hour: 12:00, Time Period: LUNCH, Optimal Checkouts: 3
Hour: 14:00, Time Period: AFTERNOON, Optimal Checkouts: 3
Hour: 17:00, Time Period: EVENING, Optimal Checkouts: 5
Hour: 20:00, Time Period: LATE_EVENING, Optimal Checkouts: 5
```

A full breakdown for each hour is available in the simulation output.

## Visualization
The project includes visualizations of:
1. Rewards over episodes during training
2. Optimal number of checkouts throughout the day

These visualizations help in understanding the learning process and the final recommendations for checkout management.

## Future Improvements
- Fine-tune hyperparameters for better convergence
- Implement more sophisticated customer behavior models
- Add real-time visualization of the simulation
- Incorporate more factors into the decision-making process (e.g., staff availability, seasonal variations)

## Contributing
Contributions to improve the simulation or extend its capabilities are welcome. Please feel free to submit issues or pull requests.
