from models.node import Node

def build_ring_topology(num_nodes, event_queue):
    nodes = []

    for i in range(num_nodes):
        node = Node(node_id=str(i), event_queue=event_queue,
            metrics_collector=metrics, max_input_buffer=2, max_injection_buffer=2)
        nodes.append(node)

    for i in range(num_nodes):
        current = nodes[i]
        next_node = nodes[(i + 1) % num_nodes]
        prev_node = nodes[(i - 1) % num_nodes]
        current.add_neighbor(next_node)
        current.add_neighbor(prev_node)

    return nodes
