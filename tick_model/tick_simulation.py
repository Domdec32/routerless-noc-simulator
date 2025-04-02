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

    
    traffic = TickTrafficGenerator(nodes, packet_rate=config["packet_rate"], stop_time=max_ticks)
    traffic.schedule_traffic()

    
    for tick in range(max_ticks):
        for node in nodes:
            node.tick(tick)

    
    metrics = MetricsCollector()
    for node in nodes:
        for packet, delivered_at in node.delivered:
            latency = delivered_at - packet.creation_time
            metrics.record_packet_delivery(packet, delivered_at)
        metrics.deflections += node.deflections
        metrics.dropped_packets += node.dropped

    if config.get("log_deliveries"):
        metrics.export_log_to_csv(config["export_log_filename"])
        metrics.logged = True

    return metrics.report()
