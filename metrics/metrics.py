import csv
import os

class MetricsCollector:
    def __init__(self, log_deliveries=True):
        self.latencies = []
        self.hop_counts = []
        self.delivered_packets = 0
        self.deflections = 0
        self.dropped_packets = 0
        self.log_deliveries = log_deliveries
        self.delivery_log = [] if log_deliveries else None

    def record_packet_delivery(self, packet, current_time):
        latency = current_time - packet.creation_time
        self.latencies.append(latency)
        self.hop_counts.append(packet.hops)
        self.delivered_packets += 1

        if self.log_deliveries:
            self.delivery_log.append({
                "packet_id": packet.packet_id,
                "src": packet.src,
                "dest": packet.dest,
                "created": packet.creation_time,
                "delivered": current_time,
                "latency": latency,
                "hops": packet.hops
            })

    def record_packet_drop(self):
        self.dropped_packets += 1

    
    def record_deflection(self):
        self.deflections += 1

    def report(self):
        if not self.latencies:
            print("No packets delivered.")
            return

        avg_latency = sum(self.latencies) / len(self.latencies)
        avg_hops = sum(self.hop_counts) / len(self.hop_counts)

        print("\n=== Simulation Metrics ===")
        print(f"Delivered packets:     {self.delivered_packets}")
        print(f"Average latency:       {avg_latency:.2f}")
        print(f"Average hop count:     {avg_hops:.2f}")
        print(f"Total deflections:     {self.deflections}")
        print(f"Total drops:           {self.dropped_packets}")
        print("=========================\n")

        return {
            "delivered": len(self.delivery_log),
            "avg_latency": avg_latency,
            "avg_hops": avg_hops,
            "deflections": self.deflections,
            "drops": self.dropped_packets,
            "logged": getattr(self, "logged", False)
        }


    def export_log_to_csv(self, filename="delivery_log.csv"):
        if not self.log_deliveries or not self.delivery_log:
            print("[Metrics] Packet logging is disabled or empty.")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        keys = self.delivery_log[0].keys()
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.delivery_log)

        print(f"[Metrics] Delivery log saved to {filename}")
