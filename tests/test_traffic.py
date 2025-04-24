import unittest
from core.event_queue import EventQueue
from models.node import Node
from models.packet import Packet
from metrics.metrics import MetricsCollector
from routing.clockwise import ClockwiseRouting
from traffic.generator import TrafficGenerator

class TestTrafficFlowAndMetrics(unittest.TestCase):

    def setUp(self):
        self.eq = EventQueue()
        self.metrics = MetricsCollector(log_deliveries=False)
        self.nodes = [Node(str(i), self.eq, routing_strategy_cls=ClockwiseRouting, metrics_collector=self.metrics) for i in range(3)]
        for i in range(len(self.nodes)):
            self.nodes[i].add_neighbor(self.nodes[(i + 1) % len(self.nodes)])

    def test_simple_packet_flow_metrics(self):
        packet = Packet(packet_id=0, creation_time=0, src="0", dest="2", size="small")
        self.nodes[0].inject_packet(packet, delay=0)

        self.eq.run()

        self.assertEqual(self.metrics.delivered_packets, 1)
        self.assertEqual(self.metrics.hop_counts, [2])
        self.assertEqual(self.metrics.latencies, [2])
        self.assertEqual(self.metrics.deflections, 0)
        self.assertEqual(self.metrics.dropped_packets, 0)

    def test_immediate_delivery_when_src_equals_dest(self):
        packet = Packet(packet_id=1, creation_time=0, src="1", dest="1", size="small")
        self.nodes[1].inject_packet(packet, delay=0)

        self.eq.run()

        self.assertEqual(self.metrics.delivered_packets, 1)
        self.assertEqual(self.metrics.hop_counts, [0])
        self.assertEqual(self.metrics.latencies, [0])
        self.assertEqual(self.metrics.deflections, 0)
        self.assertEqual(self.metrics.dropped_packets, 0)

if __name__ == '__main__':
    unittest.main()
