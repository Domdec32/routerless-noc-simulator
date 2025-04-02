from routing.base_routing import RoutingStrategy

class ClockwiseRouting(RoutingStrategy):
    def select_next_hop(self, packet):
        return self.node.neighbors[0]
