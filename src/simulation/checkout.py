import simpy

class Checkout:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.queue = simpy.Resource(env, capacity=1)
    
    def get_queue_length(self):
        return len(self.queue.queue)
    
    def is_available(self):
        return self.queue.count == 0

    def __str__(self):
        return f"Checkout {self.id}"