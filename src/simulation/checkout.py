import simpy

class Checkout:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.queue = simpy.Resource(env, capacity=1)
        self.queue_length = 0  # Add this line

    def get_queue_length(self):
        return self.queue_length  # Change this line

    def update_queue_length(self, change):
        self.queue_length = max(0, self.queue_length + change)  # Add this method

    
    def is_available(self):
        return self.queue.count == 0

    def __str__(self):
        return f"Checkout {self.id}"