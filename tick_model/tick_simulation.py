import time
import tracemalloc
from tick_model.tick_node import TickNode
from tick_model.tick_traffic import TickTrafficGenerator
from metrics.metrics import MetricsCollector  
from models.topology import build_ring_topology
from routing.deflection import DeflectionRouting
from routing.clockwise import ClockwiseRouting

def run_tick_simulation(config):
    num_nodes = config["num_nodes"]
    max_ticks = config["traffic_stop_time"]

    routing_map = {
        "deflection": DeflectionRouting,
        "clockwise": ClockwiseRouting
    }
    routing_strategy_cls = routing_map[config["routing_strategy"]]

    nodes = [TickNode(i,
                      max_input_buffer=config["max_input_buffer"],
                      max_injection_buffer=config["max_injection_buffer"],
                      routing_strategy=None)
             for i in range(num_nodes)]

    for i in range(num_nodes):
        nodes[i].add_neighbor(nodes[(i + 1) % num_nodes])

    for node in nodes:
        node.routing_strategy = routing_strategy_cls(node)

    traffic = TickTrafficGenerator(
        nodes=nodes,
        packet_rate=config["packet_rate"],
        stop_time=max_ticks,
        config=config
    )
    traffic.schedule_traffic()

    tracemalloc.start()
    start_time = time.time()

    for tick in range(max_ticks):
        for node in nodes:
            node.tick(tick)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime_seconds = end_time - start_time

    metrics = MetricsCollector()
    for node in nodes:
        for packet, delivered_at in node.delivered:
            if delivered_at >= packet.creation_time:
                metrics.record_packet_delivery(packet, delivered_at)
            else:
                #print(f"[Warning] Packet {packet.packet_id} delivered before creation time! Skipping.")

        metrics.deflections += node.deflections
        metrics.dropped_packets += node.dropped

    if config.get("log_deliveries"):
        metrics.export_log_to_csv(config["export_log_filename"])
        metrics.logged = True

    return {
        "delivered": metrics.delivered_packets,
        "avg_latency": round(sum(metrics.latencies) / len(metrics.latencies), 2) if metrics.latencies else 0,
        "avg_hops": round(sum(metrics.hop_counts) / len(metrics.hop_counts), 2) if metrics.hop_counts else 0,
        "deflections": metrics.deflections,
        "drops": metrics.dropped_packets,
        "runtime_seconds": round(runtime_seconds, 4),
        "peak_memory_kb": round(peak / 1024, 2),
        "logged": config["log_deliveries"]
    }

