import random
import json
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
        self.packet_templates = []

        if "packet_template_file" in self.config:
            self._load_packet_templates(self.config["packet_template_file"])

    def _load_packet_templates(self, filepath):
        with open(filepath, "r") as f:
            self.packet_templates = json.load(f)
        print(f"[DEBUG] Loaded {len(self.packet_templates)} packet templates from {filepath}")

    def schedule_traffic(self):
        time = self.start_time

        if self.packet_templates:
            for packet_info in self.packet_templates:
                self._schedule_packet_from_template(packet_info, time)
                time += 1 / self.packet_rate
        else:
            while time < self.stop_time:
                self._schedule_single_packet(time)
                time += 1 / self.packet_rate

    def _schedule_packet_from_template(self, packet_info, time):
        src_node = next(node for node in self.nodes if str(node.node_id) == str(packet_info["src"]))
        dest_node = next(node for node in self.nodes if str(node.node_id) == str(packet_info["dest"]))

        packet = Packet(
            packet_id=packet_info["packet_id"],
            src=src_node.node_id,
            dest=dest_node.node_id,
            creation_time=time,
            size=packet_info["size"]
        )

        def inject():
            #print(f"[DEBUG] Injecting packet {packet.packet_id} at node {src_node.node_id}")
            src_node.inject_packet(packet)

        description = f"Inject Packet({packet.packet_id}) from {packet.src} to {packet.dest}"
        delay = packet.get_delay()
        scheduled_time = time + delay
        self.event_queue.schedule(Event(scheduled_time, inject, description))

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