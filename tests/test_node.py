import unittest
from models.node import Node
from core.event_queue import EventQueue
from models.packet import Packet

class TestRouting:
    def __init__(self, node):
        self.node = node
    def select_next_hop(self, packet):
        return self.node.neighbors[0]

class TestMetrics:
    def __init__(self):
        self.delivered = []
        self.dropped = 0
    def record_packet_delivery(self, packet, time):
        self.delivered.append((packet, time))
    def record_packet_drop(self):
        self.dropped += 1

class TestNode(unittest.TestCase):

    def setUp(self):
        self.eq = EventQueue()
        self.metrics = TestMetrics()
        self.nodeA = Node("A", self.eq, TestRouting, self.metrics, max_input_buffer=1, max_injection_buffer=1)
        self.nodeB = Node("B", self.eq, TestRouting, self.metrics, max_input_buffer=1, max_injection_buffer=1)
        self.nodeA.add_neighbor(self.nodeB)
        self.nodeB.add_neighbor(self.nodeA)

    def test_packet_injection(self):
        p = Packet(0, 0, "A", "B")
        self.nodeA.inject_packet(p, delay=0)
        self.eq.run()
        self.assertEqual(len(self.nodeA.injection_buffer), 0)

    def test_packet_forwarding(self):
        p = Packet(1, 0, "A", "B")
        self.nodeA.injection_buffer.append(p)
        self.nodeA.resolve_contention()
        self.assertEqual(self.nodeB.input_buffer[0], p)

    def test_packet_delivery(self):
        p = Packet(2, 0, "A", "B")
        self.nodeB.input_buffer.append(p)
        self.nodeB.resolve_contention()
        self.assertEqual(len(self.metrics.delivered), 1)
        self.assertEqual(self.metrics.delivered[0][0], p)

    def test_packet_drop_on_input_buffer_full(self):
        p1 = Packet(3, 0, "A", "B")
        p2 = Packet(4, 0, "A", "B")
        self.nodeB.input_buffer.append(p1)
        self.nodeB.receive_packet(p2)
        self.assertEqual(self.metrics.dropped, 1)

    def test_packet_drop_on_injection_buffer_full(self):
        p1 = Packet(5, 0, "A", "B")
        p2 = Packet(6, 0, "A", "B")
        self.nodeA.injection_buffer.append(p1)
        self.nodeA.inject_packet(p2, delay=0)
        self.eq.run()
        self.assertEqual(self.metrics.dropped, 1)

if __name__ == '__main__':
    unittest.main()
