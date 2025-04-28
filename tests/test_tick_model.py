import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from tick_model.tick_node import TickNode
from tick_model.tick_traffic import TickTrafficGenerator
from models.packet import Packet
from routing.clockwise import ClockwiseRouting

class DummyRouting:
    def __init__(self, node):
        self.node = node
    def select_next_hop(self, packet):
        return self.node.neighbors[0] if self.node.neighbors else None

class TestTickModel(unittest.TestCase):

    def setUp(self):
        self.node_a = TickNode(0, max_input_buffer=2, max_injection_buffer=2, routing_strategy=DummyRouting(None))
        self.node_b = TickNode(1, max_input_buffer=2, max_injection_buffer=2, routing_strategy=DummyRouting(None))
        self.node_a.add_neighbor(self.node_b)
        self.node_b.add_neighbor(self.node_a)
        self.node_a.routing_strategy.node = self.node_a
        self.node_b.routing_strategy.node = self.node_b

    def flush_buffers(self):
        for node in [self.node_a, self.node_b]:
            node.input_buffer += node.next_input_buffer
            node.next_input_buffer = []

    def test_buffer_overflow(self):
        for i in range(3):
            packet = Packet(i, 0, 1, 0)
            self.node_a.inject_packet(packet, 0)
        self.assertEqual(self.node_a.dropped, 1)

    def test_tick_traffic_generator(self):
        nodes = [TickNode(0), TickNode(1)]
        nodes[0].add_neighbor(nodes[1])
        nodes[1].add_neighbor(nodes[0])

        config = {
            "size_distribution": [1.0, 0.0, 0.0],
            "traffic_distribution": "balanced"
        }
        gen = TickTrafficGenerator(nodes, packet_rate=1, stop_time=5, config=config)

        for tick in range(5):
            for node in nodes:
                node.input_buffer.clear()
                node.injection_buffer.clear()
            gen.inject_packets_at_tick(tick)

        print(f"[DEBUG] Generated packets: {len(gen.generated_packets)}")
        self.assertEqual(len(gen.generated_packets), 5)

    def test_deflection_logic(self):
        node_a = TickNode(node_id=0, max_input_buffer=2, max_injection_buffer=2)
        node_b = TickNode(node_id=1, max_input_buffer=1, max_injection_buffer=2)
        node_a.add_neighbor(node_b)

        dummy_packet = Packet(packet_id=99, src=9, dest=1, creation_time=0)
        node_b.input_buffer.append(dummy_packet)

        packet = Packet(packet_id=1, src=0, dest=1, creation_time=0)
        node_a.inject_packet(packet, current_tick=0)

        deflections_recorded = False
        for tick in range(10):
            print(f"[DEBUG] Tick {tick}: Node A input_buffer={len(node_a.input_buffer)}, Node B input_buffer={len(node_b.input_buffer)}")
            node_a.tick(tick)
            node_b.tick(tick)
            for node in [node_a, node_b]:
                node.input_buffer += node.next_input_buffer
                node.next_input_buffer = []

            if node_a.deflections > 0:
                deflections_recorded = True
                print(f"[DEBUG] Deflection recorded at tick {tick}")
                break

        self.assertTrue(deflections_recorded)

if __name__ == '__main__':
    unittest.main()