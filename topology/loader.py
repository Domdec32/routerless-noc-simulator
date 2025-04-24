import json
from models.node import Node

def load_topology_from_json(filepath, event_queue, metrics, routing_cls):
    with open(filepath, 'r') as f:
        data = json.load(f)

    nodes = {}
    for node_data in data["nodes"]:
        node_id = str(node_data["id"])
        node = Node(
            node_id=node_id,
            event_queue=event_queue,
            metrics_collector=metrics,
            routing_strategy_cls=routing_cls,
            max_input_buffer=node_data.get("max_input_buffer", 2),
            max_injection_buffer=node_data.get("max_injection_buffer", 2)
        )
        nodes[node_id] = node

    for node_data in data["nodes"]:
        node_id = str(node_data["id"])
        neighbors = [str(n) for n in node_data["neighbors"]]
        for neighbor_id in neighbors:
            if neighbor_id in nodes:
                nodes[node_id].add_neighbor(nodes[neighbor_id])
            else:
                raise ValueError(f"Neighbor {neighbor_id} not found in node list.")

    return list(nodes.values())

