import heapq

class EventQueue:
    def __init__(self):
        self.queue = []
        self.current_time = 0

    def schedule(self, event):
        heapq.heappush(self.queue, event)

    def run(self, until=float("inf")):
        while self.queue and self.current_time <= until:
            event = heapq.heappop(self.queue)
            self.current_time = event.timestamp
            event.execute()
