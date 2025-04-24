from main import run_simulation

config = {
    "topology_file": "topology/test_topology.json",
    "routing_strategy": "clockwise",
    "packet_rate": 1.0,
    "traffic_stop_time": 5,
    "log_deliveries": False,
    "export_log_filename": "results/delivery_log.csv",
    "size_distribution": [1.0, 0.0, 0.0],
    "max_input_buffer": 2,
    "max_injection_buffer": 2
}

results = run_simulation(config)
print("Simulation Results:")
for k, v in results.items():
    print(f"{k}: {v}")
