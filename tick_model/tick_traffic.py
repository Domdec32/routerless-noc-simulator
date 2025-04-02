import random
from models.packet import Packet

class TickTrafficGenerator:
    def __init__(self, nodes, packet_rate=1.0, stop_time=10):
        self.nodes = nodes
        self.packet_rate = packet_rate
        self.stop_time = stop_time
        self.generated_packets = []

    def schedule_traffic(self):
        for t in range(self.stop_time):
            for node in self.nodes:
                if random.random() < self.packet_rate:
                    dest_choices = [n.node_id for n in self.nodes if n.node_id != node.node_id]
                    dest = random.choice(dest_choices)
                    packet_id = len(self.generated_packets)
                    packet = Packet(packet_id, t, node.node_id, dest)
                    node.inject_packet(packet)
                    self.generated_packets.append(packet)