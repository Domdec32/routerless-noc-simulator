import unittest
from core.event_queue import EventQueue
from models.node import Node
from models.packet import Packet
from routing.deflection import DeflectionRouting

class TestDeflectionRouting(unittest.TestCase):

    def setUp(self):
        self.eq = EventQueue()
        self.node = Node("0", self.eq, metrics_collector=None, max_input_buffer=1, max_injection_buffer=1)
        self.other = Node("1", self.eq, metrics_collector=None)
        self.node.add_neighbor(self.other)
        self.node.add_neighbor(Node("2", self.eq))
        self.node.routing_strategy = DeflectionRouting(self.node)

    def test_deflect_lower_priority_packet(self):
        early_packet = Packet(packet_id=1, creation_time=1.0, src="X", dest="Z")
        late_packet = Packet(packet_id=2, creation_time=2.0, src="Y", dest="Z")

        self.node.input_buffer.append(early_packet)
        self.node.injection_buffer.append(late_packet)

        self.node.resolve_contention()

        self.assertEqual(len(self.node.input_buffer), 0)
        self.assertEqual(len(self.node.injection_buffer), 0)
        self.assertEqual(len(self.other.input_buffer), 1)
        deflected_to = self.node.neighbors[1]
        self.assertEqual(len(deflected_to.input_buffer), 1)

        forwarded_ids = {p.packet_id for p in self.other.input_buffer + deflected_to.input_buffer}
        self.assertIn(1, forwarded_ids)
        self.assertIn(2, forwarded_ids)

if __name__ == '__main__':
    unittest.main()

