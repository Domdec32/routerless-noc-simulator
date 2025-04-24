from core.event import Event

class Node:
        def __init__(self, node_id, event_queue, routing_strategy_cls=None, metrics_collector=None,
             max_input_buffer=2, max_injection_buffer=2):

            self.node_id = node_id
            self.event_queue = event_queue
            self.metrics = metrics_collector
            self.neighbors = []
            self.routing_strategy = None
            self.contention_event_scheduled = False

            if routing_strategy_cls:
                self.routing_strategy = routing_strategy_cls(self)

            self.input_buffer = []
            self.injection_buffer = []

            self.max_input_buffer = max_input_buffer
            self.max_injection_buffer = max_injection_buffer


        def add_neighbor(self, neighbor_node):
            self.neighbors.append(neighbor_node)

        def inject_packet(self, packet, delay=0):
            def store():
                if len(self.injection_buffer) >= self.max_injection_buffer:
                    #print(f"[Time {self.event_queue.current_time}] [DROP] Node {self.node_id} dropped Packet {packet.packet_id} (injection buffer full)")
                    if self.metrics:
                        self.metrics.record_packet_drop()
                    return

                self.injection_buffer.append(packet)

                if len(self.input_buffer) + len(self.injection_buffer) == 1:
                    self.event_queue.schedule(Event(self.event_queue.current_time, self.resolve_contention, f"Resolve contention at Node {self.node_id}"))

            self.event_queue.schedule(Event(packet.creation_time + delay, store, f"Inject {packet}"))



        def forward_packet(self, packet):
            if packet.dest == self.node_id:
                #print(f"[Time {self.event_queue.current_time}] [Node {self.node_id}] Received {packet} after {packet.hops} hops!")
                if self.metrics:
                    self.metrics.record_packet_delivery(packet, self.event_queue.current_time)
            else:
                if self.routing_strategy:
                    next_node = self.routing_strategy.select_next_hop(packet)
                else:
                    next_node = self.neighbors[0]  

                packet.hops += 1
                #print(f"[Time {self.event_queue.current_time}] [Node {self.node_id}] Forwarding {packet} to Node {next_node.node_id}")
                next_node.receive_packet(packet)


        def receive_packet(self, packet):
            if len(self.input_buffer) >= self.max_input_buffer:
                #print(f"[Time {self.event_queue.current_time}] [DROP] Node {self.node_id} dropped incoming Packet {packet.packet_id} (input buffer full)")
                if self.metrics:
                    self.metrics.record_packet_drop()
                return

            self.input_buffer.append(packet)

            if not self.contention_event_scheduled:
                self.event_queue.schedule(Event(
                    self.event_queue.current_time + 1,
                    self.resolve_contention,
                    f"Resolve contention at Node {self.node_id}"
                ))
                self.contention_event_scheduled = True

        def resolve_contention(self):
            self.contention_event_scheduled = False
            contenders = self.input_buffer + self.injection_buffer

            if not contenders:
                return

            
            contenders.sort(key=lambda pkt: (pkt.creation_time, pkt.packet_id))

            preferred = self.neighbors[0]
            alternate = self.neighbors[1] if len(self.neighbors) > 1 else None

            for i, packet in enumerate(contenders):
                
                if packet.dest == self.node_id:
                    #print(f"[Time {self.event_queue.current_time}] [Node {self.node_id}] Received {packet} after {packet.hops} hops!")
                    if self.metrics:
                        self.metrics.record_packet_delivery(packet, self.event_queue.current_time)
                    continue
                
                packet.hops += 1

                if i == 0:
                    next_node = preferred
                elif alternate:
                    next_node = alternate
                    if self.metrics:
                        self.metrics.record_deflection()
                    #print(f"[Time {self.event_queue.current_time}] [Node {self.node_id}] Deflected Packet {packet.packet_id} to Node {next_node.node_id}")
                else:
                    #print(f"[Node {self.node_id}] WARNING: No route for Packet {packet.packet_id}")
                    continue

                #print(f"[Time {self.event_queue.current_time}] [Node {self.node_id}] Forwarding {packet} to Node {next_node.node_id}")
                next_node.receive_packet(packet)

            
            self.input_buffer.clear()
            self.injection_buffer.clear()


