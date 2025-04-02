class RoutingStrategy:
    def __init__(self, node):
        self.node = node

    def select_next_hop(self, packet):
        raise NotImplementedError("RoutingStrategy subclasses must implement this method.")
