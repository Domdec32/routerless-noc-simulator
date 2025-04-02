class TickNode:
    def __init__(self, node_id, max_input_buffer=2, max_injection_buffer=2, routing_strategy=None):
        self.node_id = node_id
        self.input_buffer = []
        self.injection_buffer = []
        self.max_input_buffer = max_input_buffer
        self.max_injection_buffer = max_injection_buffer
        self.routing_strategy = routing_strategy
        self.neighbors = []
        self.delivered = []
        self.deflections = 0
        self.dropped = 0

    def add_neighbor(self, neighbor_node):
        self.neighbors.append(neighbor_node)

    def inject_packet(self, packet):
        if len(self.injection_buffer) < self.max_injection_buffer:
            self.injection_buffer.append(packet)
        else:
            self.dropped += 1

    def tick(self, current_tick):
        forwarding = []

        
        for packet in self.input_buffer:
            if packet.dest == self.node_id:
                self.delivered.append((packet, current_tick))
            else:
                forwarding.append(packet)

        self.input_buffer.clear()

        
        if self.injection_buffer:
            forwarding.append(self.injection_buffer.pop(0))

        
        for packet in forwarding:
            next_node = None
            if self.routing_strategy:
                next_node = self.routing_strategy.select_next_hop(packet)
            elif self.neighbors:
                next_node = self.neighbors[0]

            if next_node and len(next_node.input_buffer) < next_node.max_input_buffer:
                next_node.input_buffer.append(packet)
                packet.hops += 1
            else:
                self.deflections += 1
                self.input_buffer.append(packet)