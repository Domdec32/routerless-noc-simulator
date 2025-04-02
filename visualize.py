import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

def load_delivery_log(filename):
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def get_latency_histogram(deliveries):
    latencies = [float(row["latency"]) for row in deliveries]
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.hist(latencies, bins=10, color="skyblue", edgecolor="black")
    ax.set_title("Latency Distribution")
    ax.set_xlabel("Latency")
    ax.set_ylabel("Packets")
    ax.grid(True)
    return fig

def get_hop_histogram(deliveries):
    hops = [int(row["hops"]) for row in deliveries]
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.hist(hops, bins=range(min(hops), max(hops) + 2), align="left", color="salmon", edgecolor="black")
    ax.set_title("Hop Count Distribution")
    ax.set_xlabel("Hops")
    ax.set_ylabel("Packets")
    ax.grid(True)
    return fig

def get_latency_vs_hops(deliveries):
    latencies = [float(row["latency"]) for row in deliveries]
    hops = [int(row["hops"]) for row in deliveries]
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.scatter(hops, latencies, alpha=0.7, color="mediumseagreen")
    ax.set_title("Latency vs. Hop Count")
    ax.set_xlabel("Hop Count")
    ax.set_ylabel("Latency")
    ax.grid(True)
    return fig

def get_latency_cdf(deliveries):
    latencies = sorted([float(row["latency"]) for row in deliveries])
    cdf = np.arange(len(latencies)) / len(latencies)
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.plot(latencies, cdf, color="purple")
    ax.set_title("Cumulative Distribution of Latency")
    ax.set_xlabel("Latency")
    ax.set_ylabel("CDF")
    ax.grid(True)
    return fig

def get_per_packet_hops(deliveries):
    packet_ids = [int(row["packet_id"]) for row in deliveries]
    hops = [int(row["hops"]) for row in deliveries]
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.bar(packet_ids, hops, color="slateblue", edgecolor="black")
    ax.set_title("Per-Packet Hop Count")
    ax.set_xlabel("Packet ID")
    ax.set_ylabel("Hops")
    ax.grid(True, axis="y")
    return fig


if __name__ == "__main__":
    deliveries = load_delivery_log("results/delivery_log.csv")

    plot_latency_histogram(deliveries)
    plot_hops_histogram(deliveries)
    plot_latency_vs_hops(deliveries)
    plot_delivery_timeline(deliveries)
    plot_latency_cdf(deliveries)
    plot_per_packet_hops(deliveries)

