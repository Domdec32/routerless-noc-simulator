import random
from models.packet import Packet

class TickTrafficGenerator:
    def __init__(self, nodes, packet_rate=1.0, stop_time=10, config=None, debug=False):
        self.nodes = nodes
        self.packet_rate = int(packet_rate)
        self.stop_time = stop_time
        self.generated_packets = []
        self.packet_id = 0
        self.config = config or {}
        self.debug = debug

        self.packet_templates = []
        if "packet_template_file" in self.config:
            self._load_packet_templates(self.config["packet_template_file"])

    def _load_packet_templates(self, filepath):
        import json
        with open(filepath, "r") as f:
            self.packet_templates = json.load(f)

    def inject_packets_at_tick(self, current_tick):
        #print(f"[DEBUG] Injecting at tick {current_tick}...")
        for _ in range(self.packet_rate):
            #print(f"[DEBUG] Checking if packet template exists: {bool(self.packet_templates)}")
            if self.packet_templates:
                packet_info = self.packet_templates.pop(0)
                src = next(node for node in self.nodes if node.node_id == packet_info["src"])

                packet = Packet(
                    packet_id=packet_info["packet_id"],
                    src=packet_info["src"],
                    dest=packet_info["dest"],
                    creation_time=current_tick,
                    size=packet_info["size"]
                )


                src.inject_packet(packet, current_tick)
                self.generated_packets.append(packet)

            else:
                print(f"[DEBUG] Randomly scheduling packet at tick {current_tick}")
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
        #print(f"[DEBUG] Injected packet {packet.packet_id}")

