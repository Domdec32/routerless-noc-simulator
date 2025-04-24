import random
from core.event import Event
from models.packet import Packet

class TrafficGenerator:
    def __init__(self, nodes, event_queue, config):
        self.nodes = nodes
        self.config = config
        self.event_queue = event_queue
        self.packet_rate = config["packet_rate"] 
        self.start_time = 0
        self.stop_time = config["traffic_stop_time"]
        self.packet_size_distribution = config.get("packet_size_distribution", {"small": 1.0})
        self.traffic_distribution = config.get("traffic_distribution", "balanced")
        self.packet_id_counter = 0

    def schedule_traffic(self):
        time = self.start_time
        while time < self.stop_time:
            self._schedule_single_packet(time)
            time += 1 / self.packet_rate

    def _schedule_single_packet(self, time):
        src = random.choice(self.nodes)

        if self.traffic_distribution == "unbalanced":
            weights = [len(self.nodes) - i for i in range(len(self.nodes))]
            dest_node_ids = [node.node_id for node in self.nodes if node.node_id != src.node_id]
            dest_weights = [weights[int(node_id)] for node_id in dest_node_ids]
            dest = random.choices([n for n in self.nodes if n.node_id != src.node_id], weights=dest_weights)[0]
        else:
            dest = random.choice([n for n in self.nodes if n.node_id != src.node_id])

        size_distribution = self.config.get("size_distribution", [0.5, 0.3, 0.2])
        size = random.choices(["small", "medium", "large"], weights=size_distribution)[0]

        packet = Packet(
            packet_id=self.packet_id_counter,
            src=src.node_id,
            dest=dest.node_id,
            creation_time=time,
            size=size
        )

        self.packet_id_counter += 1

        def inject():
            src.inject_packet(packet)

        description = f"Inject Packet({packet.packet_id}) from {packet.src} to {packet.dest}"
        delay = packet.get_delay()
        scheduled_time = time + delay
        self.event_queue.schedule(Event(scheduled_time, inject, description))
