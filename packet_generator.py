import json
import random

def generate_packet_templates(num_packets, nodes, size_distribution=[0.5, 0.3, 0.2], output_filename="packet_templates.json"):
    packets = []
    for packet_id in range(num_packets):
        src = random.choice(nodes)
        dest_choices = [n for n in nodes if n != src]
        dest = random.choice(dest_choices)

        size = random.choices(["small", "medium", "large"], weights=size_distribution)[0]

        packets.append({
            "packet_id": packet_id,
            "src": src,
            "dest": dest,
            "size": size
        })

    with open(output_filename, "w") as f:
        json.dump(packets, f, indent=2)

    print(f"Generated {len(packets)} packet templates and saved to '{output_filename}'.")


if __name__ == "__main__":
    generate_packet_templates(
        num_packets=100,
        nodes=list(range(300)),
        size_distribution=[0.5, 0.3, 0.2],
        output_filename="packet_templates.json"
    )
