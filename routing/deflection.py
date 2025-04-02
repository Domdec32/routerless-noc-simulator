from routing.base_routing import RoutingStrategy
import random

class DeflectionRouting(RoutingStrategy):
    def select_next_hop(self, packet):
        
        if len(self.node.neighbors) == 1:
            return self.node.neighbors[0]

        
        preferred = self.node.neighbors[0]
        deflected = self.node.neighbors[1]

        
        if random.random() < 0.1:
            print(f"[Deflection] Packet {packet.packet_id} deflected from preferred path!")
            if self.node.metrics:
                self.node.metrics.record_deflection()
            return deflected
        else:
            return preferred
