import random
from models.packet import Packet

class TickTrafficGenerator:
    def __init__(self, nodes, packet_rate=1.0, stop_time=10, config=None):
        self.nodes = nodes
        self.packet_rate = int(packet_rate)
        self.stop_time = stop_time
        self.generated_packets = []
        self.packet_id = 0
        self.config = config or {}

    def schedule_traffic(self):
        for current_tick in range(self.stop_time):
            for _ in range(self.packet_rate):
                self._schedule_single_packet(current_tick)

    def _schedule_single_packet(self, current_tick):
        src = random.choice(self.nodes)
        dest_choices = [n.node_id for n in self.nodes if n.node_id != src.node_id]
        dest_id = random.choice(dest_choices)
        dest = next(n for n in self.nodes if n.node_id == dest_id)

        size_distribution = self.config.get("size_distribution", [0.5, 0.3, 0.2])
        size = random.choices(["small", "medium", "large"], weights=size_distribution)[0]

        packet = Packet(
            packet_id=self.packet_id,
            src=src.node_id,
            dest=dest.node_id,
            creation_time=current_tick,
            size=size
        )

        self.packet_id += 1
        src.inject_packet(packet, current_tick)
        self.generated_packets.append(packet)
