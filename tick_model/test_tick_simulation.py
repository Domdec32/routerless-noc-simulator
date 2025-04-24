import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tick_model.tick_simulation import run_tick_simulation

config = {
    "num_nodes": 6,
    "max_input_buffer": 2,
    "max_injection_buffer": 2,
    "routing_strategy": "deflection", 
    "packet_rate": 1.0,
    "traffic_stop_time": 10,
    "log_deliveries": True,
    "export_log_filename": "results/tick_delivery_log.csv",
    "size_distribution": [0.5, 0.3, 0.2],
    "traffic_distribution": "balanced"
}

if __name__ == "__main__":
    print("Running tick-based simulation test...\n")
    summary = run_tick_simulation(config)

    print("\n=== Tick-Based Simulation Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")


