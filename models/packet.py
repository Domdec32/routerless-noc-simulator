class Packet:
    def __init__(self, packet_id, src, dest, creation_time):
        self.packet_id = packet_id      
        self.src = src                  
        self.dest = dest               
        self.creation_time = creation_time 
        self.hops = 0                   

    def __repr__(self):
        return f"Packet({self.packet_id} from {self.src} to {self.dest})"
