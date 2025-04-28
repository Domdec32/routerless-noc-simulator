import tkinter as tk
from tkinter import ttk
from main import run_simulation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualize import (
    load_delivery_log,
    get_latency_histogram,
    get_hop_histogram,
    get_latency_vs_hops,
    get_latency_cdf,
    get_per_packet_hops,
    get_deliveries_per_node
)

config = {}
results = {}

root = tk.Tk()
root.title("Routerless NoC Simulator Config")
root.geometry("1200x800")

left_panel = ttk.Frame(root)
left_panel.grid(row=0, column=0, sticky="n", padx=20, pady=20)

right_panel = ttk.Frame(root)
right_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
root.columnconfigure(1, weight=1)

canvas = tk.Canvas(right_panel, height=600)
scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

fields = {
    "num_nodes": tk.IntVar(value=6),
    "max_input_buffer": tk.IntVar(value=2),
    "max_injection_buffer": tk.IntVar(value=2),
    "packet_rate": tk.DoubleVar(value=1.0),
    "traffic_stop_time": tk.IntVar(value=10),
    "log_deliveries": tk.BooleanVar(value=True),
    "size_small": tk.DoubleVar(value=0.5),
    "size_medium": tk.DoubleVar(value=0.3),
    "size_large": tk.DoubleVar(value=0.2)
}

routing_var = tk.StringVar(value="deflection")
size_mode_var = tk.StringVar(value="custom")
traffic_distribution_var = tk.StringVar(value="balanced")
use_packet_template_var = tk.BooleanVar(value=False)

row = 0
for key in ["num_nodes", "max_input_buffer", "max_injection_buffer", "packet_rate", "traffic_stop_time"]:
    ttk.Label(left_panel, text=key.replace("_", " ").title()).grid(row=row, column=0, sticky="w")
    ttk.Entry(left_panel, textvariable=fields[key]).grid(row=row, column=1)
    row += 1

ttk.Label(left_panel, text="Routing Strategy").grid(row=row, column=0, sticky="w")
ttk.Combobox(left_panel, textvariable=routing_var, values=["deflection", "clockwise"]).grid(row=row, column=1)
row += 1

ttk.Checkbutton(left_panel, text="Log Deliveries", variable=fields["log_deliveries"]).grid(row=row, columnspan=2, sticky="w")
row += 1

ttk.Label(left_panel, text="Size Distribution Mode").grid(row=row, column=0, sticky="w")
ttk.Combobox(left_panel, textvariable=size_mode_var, values=["custom", "random"]).grid(row=row, column=1)
row += 1

for label, key in [("Small Packet %", "size_small"), ("Medium Packet %", "size_medium"), ("Large Packet %", "size_large")]:
    ttk.Label(left_panel, text=label).grid(row=row, column=0, sticky="w")
    ttk.Entry(left_panel, textvariable=fields[key]).grid(row=row, column=1)
    row += 1

ttk.Label(left_panel, text="Traffic Distribution").grid(row=row, column=0, sticky="w")
ttk.Combobox(left_panel, textvariable=traffic_distribution_var, values=["balanced", "unbalanced"]).grid(row=row, column=1)
row += 1

ttk.Checkbutton(left_panel, text="Use Packet Templates", variable=use_packet_template_var).grid(row=row, columnspan=2, sticky="w")
row += 1

def run():
    global config, results
    config = {
        "topology": "ring",
        "num_nodes": fields["num_nodes"].get(),
        "max_input_buffer": fields["max_input_buffer"].get(),
        "max_injection_buffer": fields["max_injection_buffer"].get(),
        "routing_strategy": routing_var.get(),
        "packet_rate": fields["packet_rate"].get(),
        "traffic_stop_time": fields["traffic_stop_time"].get(),
        "log_deliveries": fields["log_deliveries"].get(),
        "export_log_filename": "results/delivery_log.csv",
        "size_distribution_mode": size_mode_var.get(),
        "size_distribution": [fields["size_small"].get(), fields["size_medium"].get(), fields["size_large"].get()],
        "traffic_distribution": traffic_distribution_var.get()
    }

    if use_packet_template_var.get():
        config["packet_template_file"] = "packet_templates.json"

    results = run_simulation(config)

    results_box.configure(state="normal")
    results_box.delete("1.0", tk.END)
    results_box.insert(tk.END, f"Simulation Complete!\n\n")
    results_box.insert(tk.END, f"Delivered Packets: {results['delivered']}\n")
    results_box.insert(tk.END, f"Average Latency: {results['avg_latency']}\n")
    results_box.insert(tk.END, f"Average Hops: {results['avg_hops']}\n")
    results_box.insert(tk.END, f"Deflections: {results['deflections']}\n")
    results_box.insert(tk.END, f"Dropped Packets: {results['drops']}\n")
    results_box.insert(tk.END, f"Runtime (seconds): {results['runtime_seconds']}\n")
    results_box.insert(tk.END, f"Peak Memory Usage (KB): {results['peak_memory_kb']}\n")

    if results['logged']:
        results_box.insert(tk.END, f"Log saved to: {config['export_log_filename']}\n")
    results_box.configure(state="disabled")

def show_plots():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    try:
        deliveries = load_delivery_log(config["export_log_filename"])
        figures = [
            get_latency_histogram(deliveries),
            get_hop_histogram(deliveries),
            get_latency_vs_hops(deliveries),
            get_latency_cdf(deliveries),
            get_per_packet_hops(deliveries),
            get_deliveries_per_node(deliveries)
        ]
        for fig in figures:
            fig.set_size_inches(5.5, 2.5)
            canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="x", expand=True)
    except Exception as e:
        results_box.configure(state="normal")
        results_box.insert(tk.END, f"\n[Error showing plots: {e}]\n")
        results_box.configure(state="disabled")

ttk.Button(left_panel, text="Run Simulation", command=run).grid(row=row, columnspan=2, pady=10)
row += 1

results_box = tk.Text(left_panel, height=10, width=40, state="disabled")
results_box.grid(row=row, columnspan=2, pady=(5, 10))
row += 1

ttk.Button(left_panel, text="Show Plots", command=show_plots).grid(row=row, columnspan=2)
row += 1

root.mainloop()

