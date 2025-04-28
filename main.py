def run_simulation(config):
    from topology.loader import load_topology_from_json
    from core.event_queue import EventQueue
    from metrics.metrics import MetricsCollector
    from traffic.generator import TrafficGenerator
    from models.node import Node
    from routing.deflection import DeflectionRouting
    from routing.clockwise import ClockwiseRouting
    import time
    import tracemalloc

    eq = EventQueue()
    metrics = MetricsCollector(log_deliveries=config["log_deliveries"])

    if "topology_file" in config:
        routing_map = {
            "deflection": DeflectionRouting,
            "clockwise": ClockwiseRouting
        }
        routing_cls = routing_map[config["routing_strategy"]]
        nodes = load_topology_from_json(config["topology_file"], eq, metrics, routing_cls)
    else:
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

    if config.get("size_distribution_mode") == "random":
        import random
        rand = random.random()
        remaining = 1.0 - rand
        split = random.random()
        second = round(split * remaining, 2)
        third = round(remaining - second, 2)
        config["size_distribution"] = [round(rand, 2), second, third]

    traffic = TrafficGenerator(
        nodes=nodes,
        event_queue=eq,
        config=config
    )
    traffic.schedule_traffic()
    print(f"[DEBUG] Number of events scheduled in EventQueue: {len(eq.queue)}")


    tracemalloc.start()
    start_time = time.time()
    eq.run()
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime_seconds = end_time - start_time
    metrics.report()

    if config["log_deliveries"]:
        metrics.export_log_to_csv(config["export_log_filename"])

    return {
        "delivered": metrics.delivered_packets,
        "avg_latency": round(sum(metrics.latencies) / len(metrics.latencies), 2) if metrics.latencies else 0,
        "avg_hops": round(sum(metrics.hop_counts) / len(metrics.hop_counts), 2) if metrics.hop_counts else 0,
        "deflections": metrics.deflections,
        "drops": metrics.dropped_packets,
        "runtime_seconds": round(runtime_seconds, 4),
        "peak_memory_kb": round(peak / 1024, 2),
        "logged": config["log_deliveries"],
        "events_processed": eq.events_processed
    }
