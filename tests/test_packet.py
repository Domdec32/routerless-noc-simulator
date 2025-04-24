import unittest
from models.packet import Packet

class TestPacket(unittest.TestCase):

    def test_packet_defaults_to_small(self):
        p = Packet(packet_id=1, creation_time=0, src=0, dest=1)
        self.assertEqual(p.size, "small")
        self.assertEqual(p.get_delay(), 1)

    def test_packet_medium_size(self):
        p = Packet(packet_id=2, creation_time=0, src=0, dest=1, size="medium")
        self.assertEqual(p.size, "medium")
        self.assertEqual(p.get_delay(), 2)

    def test_packet_large_size(self):
        p = Packet(packet_id=3, creation_time=0, src=0, dest=1, size="large")
        self.assertEqual(p.size, "large")
        self.assertEqual(p.get_delay(), 3)

    def test_packet_attributes(self):
        p = Packet(packet_id=4, creation_time=5, src=1, dest=2)
        self.assertEqual(p.packet_id, 4)
        self.assertEqual(p.creation_time, 5)
        self.assertEqual(p.src, 1)
        self.assertEqual(p.dest, 2)
        self.assertEqual(p.hops, 0)

if __name__ == '__main__':
    unittest.main()
