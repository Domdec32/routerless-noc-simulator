class Event:
    def __init__(self, timestamp, callback, description=""):
        self.timestamp = timestamp      
        self.callback = callback        
        self.description = description 

    def __lt__(self, other):
        return self.timestamp < other.timestamp 

    def execute(self):
        self.callback()
