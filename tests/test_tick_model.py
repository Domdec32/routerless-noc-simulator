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

    def test_packet_delivery(self):
        packet = Packet(0, 0, 0, 1)
        self.node_a.inject_packet(packet, 0)
        self.node_a.tick(0)
        self.node_b.tick(0)
        self.assertEqual(len(self.node_b.delivered), 1)

    def test_buffer_overflow(self):
        for i in range(3):
            packet = Packet(i, 0, 0, 1)
            self.node_a.inject_packet(packet, 0)
        self.assertEqual(self.node_a.dropped, 1)

    def test_tick_traffic_generator(self):
        nodes = [self.node_a, self.node_b]
        config = {
            "size_distribution": [1.0, 0.0, 0.0],
            "traffic_distribution": "balanced"
        }
        gen = TickTrafficGenerator(nodes, packet_rate=1, stop_time=5, config=config)
        gen.schedule_traffic()
        self.assertEqual(len(gen.generated_packets), 5)

    def test_deflection_logic(self):
        node_a = TickNode(node_id=0, max_input_buffer=2, max_injection_buffer=2)
        node_b = TickNode(node_id=1, max_input_buffer=1, max_injection_buffer=2)
        node_a.add_neighbor(node_b)

        packet_dummy = Packet(packet_id=99, src=9, dest=1, creation_time=0)
        node_b.input_buffer.append(packet_dummy)

        packet = Packet(packet_id=1, src=0, dest=1, creation_time=0)
        node_a.inject_packet(packet, current_tick=0)

        for tick in range(3):
            node_a.tick(tick)
            node_b.tick(tick)

        self.assertGreaterEqual(node_a.deflections, 1)


if __name__ == '__main__':
    unittest.main()
