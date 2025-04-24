class Packet:
    PACKET_DELAYS = {
        "small": 1,
        "medium": 2,
        "large": 3
    }

    def __init__(self, packet_id, creation_time, src, dest, size="small"):
        self.packet_id = packet_id
        self.creation_time = creation_time
        self.src = src
        self.dest = dest
        self.hops = 0
        self.size = size

    def get_delay(self):
        return Packet.PACKET_DELAYS.get(self.size, 1)                   

    def __repr__(self):
        return f"Packet({self.packet_id} from {self.src} to {self.dest})"
