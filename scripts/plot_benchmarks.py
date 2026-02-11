import matplotlib.pyplot as plt


def plot_email_benchmarks(output_prefix: str = "emails"):
    """
    Plot duration, RAM and CPU usage for the email benchmarks.
    """
    labels = ["Celery", "FluxQueue (1 worker)", "FluxQueue (75 workers)"]

    # Data from README
    duration = [672.939, 673.882, 52.856]  # seconds
    ram_mb = [5487.89, 88.27, 4615.41]  # MB
    cpu_pct = [1.05, 0.72, 4.84]  # % of total CPU

    x = range(len(labels))

    # Duration
    plt.figure(figsize=(8, 5))
    plt.bar(x, duration, color=["#f97316", "#22c55e", "#16a34a"])
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Duration (seconds)")
    plt.title("Email Benchmark – Duration")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_duration.png", dpi=150)
    plt.close()

    # RAM
    plt.figure(figsize=(8, 5))
    plt.bar(x, ram_mb, color=["#f97316", "#22c55e", "#16a34a"])
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Average RAM Usage (MB)")
    plt.title("Email Benchmark – RAM Usage")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_ram.png", dpi=150)
    plt.close()

    # CPU
    plt.figure(figsize=(8, 5))
    plt.bar(x, cpu_pct, color=["#f97316", "#22c55e", "#16a34a"])
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Average CPU Usage (% of total CPU)")
    plt.title("Email Benchmark – CPU Usage")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_cpu.png", dpi=150)
    plt.close()


def plot_db_benchmarks(output_prefix: str = "db"):
    """
    Plot duration, RAM and CPU usage for the DB query benchmarks.
    """
    labels = ["Celery", "FluxQueue"]

    # Data from README
    duration = [78.547, 63.110]  # seconds
    ram_mb = [7046.54, 87.41]  # MB
    cpu_pct = [8.88, 1.27]  # % of total CPU

    x = range(len(labels))

    # Duration
    plt.figure(figsize=(6, 4))
    plt.bar(x, duration, color=["#f97316", "#22c55e"])
    plt.xticks(x, labels)
    plt.ylabel("Duration (seconds)")
    plt.title("DB Benchmark – Duration")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_duration.png", dpi=150)
    plt.close()

    # RAM
    plt.figure(figsize=(6, 4))
    plt.bar(x, ram_mb, color=["#f97316", "#22c55e"])
    plt.xticks(x, labels)
    plt.ylabel("Average RAM Usage (MB)")
    plt.title("DB Benchmark – RAM Usage")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_ram.png", dpi=150)
    plt.close()

    # CPU
    plt.figure(figsize=(6, 4))
    plt.bar(x, cpu_pct, color=["#f97316", "#22c55e"])
    plt.xticks(x, labels)
    plt.ylabel("Average CPU Usage (% of total CPU)")
    plt.title("DB Benchmark – CPU Usage")
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_cpu.png", dpi=150)
    plt.close()


def plot_combined(output_path: str = "combined_overview.png"):
    """
    Single figure comparing Celery vs FluxQueue across both benchmarks
    (emails + DB) for duration, RAM and CPU.
    """
    # Email: Celery vs FluxQueue (1 worker)
    email_duration = [672.939, 673.882]
    email_ram = [5487.89, 88.27]
    email_cpu = [1.05, 0.72]

    # DB: Celery vs FluxQueue (1 worker)
    db_duration = [78.547, 63.110]
    db_ram = [7046.54, 87.41]
    db_cpu = [8.88, 1.27]

    labels = ["Emails – Celery", "Emails – FluxQueue", "DB – Celery", "DB – FluxQueue"]

    duration = email_duration + db_duration
    ram_mb = email_ram + db_ram
    cpu_pct = email_cpu + db_cpu

    x = range(len(labels))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Duration
    axes[0].bar(
        x,
        duration,
        color=["#f97316", "#22c55e", "#f97316", "#22c55e"],
    )
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("Seconds")
    axes[0].set_title("Duration")

    # RAM (log scale – huge differences)
    axes[1].bar(
        x,
        ram_mb,
        color=["#f97316", "#22c55e", "#f97316", "#22c55e"],
    )
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_ylabel("RAM (MB, log scale)")
    axes[1].set_yscale("log")
    axes[1].set_title("Average RAM Usage")

    # CPU
    axes[2].bar(
        x,
        cpu_pct,
        color=["#f97316", "#22c55e", "#f97316", "#22c55e"],
    )
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=20, ha="right")
    axes[2].set_ylabel("CPU (% of total)")
    axes[2].set_title("Average CPU Usage")

    fig.suptitle("Celery vs FluxQueue – Emails & DB Benchmarks", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    plot_email_benchmarks()
    plot_db_benchmarks()
    plot_combined()


if __name__ == "__main__":
    main()

