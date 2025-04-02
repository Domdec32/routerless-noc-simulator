def run_simulation(config):
    from core.event_queue import EventQueue
    from metrics.metrics import MetricsCollector
    from traffic.generator import TrafficGenerator
    from models.node import Node
    from routing.deflection import DeflectionRouting
    from routing.clockwise import ClockwiseRouting

    eq = EventQueue()
    metrics = MetricsCollector(log_deliveries=config["log_deliveries"])

    nodes = []
    for i in range(config["num_nodes"]):
        node = Node(
            node_id=str(i),
            event_queue=eq,
            metrics_collector=metrics,
            max_input_buffer=config["max_input_buffer"],
            max_injection_buffer=config["max_injection_buffer"]
        )
        nodes.append(node)

    for i in range(config["num_nodes"]):
        current = nodes[i]
        next_node = nodes[(i + 1) % config["num_nodes"]]
        prev_node = nodes[(i - 1) % config["num_nodes"]]
        current.add_neighbor(next_node)
        current.add_neighbor(prev_node)

    routing_map = {
        "deflection": DeflectionRouting,
        "clockwise": ClockwiseRouting
    }
    for node in nodes:
        node.routing_strategy = routing_map[config["routing_strategy"]](node)

    traffic = TrafficGenerator(
        nodes=nodes,
        event_queue=eq,
        packet_rate=config["packet_rate"],
        stop_time=config["traffic_stop_time"]
    )
    traffic.schedule_traffic()

    eq.run()
    metrics.report()

    if config["log_deliveries"]:
        metrics.export_log_to_csv(config["export_log_filename"])

    return {
        "delivered": metrics.delivered_packets,
        "avg_latency": round(sum(metrics.latencies) / len(metrics.latencies), 2) if metrics.latencies else 0,
        "avg_hops": round(sum(metrics.hop_counts) / len(metrics.hop_counts), 2) if metrics.hop_counts else 0,
        "deflections": metrics.deflections,
        "drops": metrics.dropped_packets,
        "logged": config["log_deliveries"]
    }
