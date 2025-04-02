import random
from core.event import Event
from models.packet import Packet

class TrafficGenerator:
    def __init__(self, nodes, event_queue, packet_rate=1.0, start_time=0, stop_time=50):
        self.nodes = nodes
        self.event_queue = event_queue
        self.packet_rate = packet_rate 
        self.start_time = start_time
        self.stop_time = stop_time
        self.packet_id_counter = 0

    def schedule_traffic(self):
        time = self.start_time
        while time < self.stop_time:
            self._schedule_single_packet(time)
            time += 1 / self.packet_rate

    def _schedule_single_packet(self, time):
        src = random.choice(self.nodes)
        dest = random.choice(self.nodes)

        while dest.node_id == src.node_id:
            dest = random.choice(self.nodes)

        packet = Packet(
            packet_id=self.packet_id_counter,
            src=src.node_id,
            dest=dest.node_id,
            creation_time=time
        )

        self.packet_id_counter += 1

        def inject():
            src.inject_packet(packet)

        description = f"Inject Packet({packet.packet_id}) from {packet.src} to {packet.dest}"
        self.event_queue.schedule(Event(time, inject, description))
