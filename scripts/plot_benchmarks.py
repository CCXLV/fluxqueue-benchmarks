import matplotlib.pyplot as plt


def plot_combined(output_path: str = "public/combined_overview.png"):
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

    labels = ["Emails - Celery", "Emails - FluxQueue", "DB - Celery", "DB - FluxQueue"]

    duration = email_duration + db_duration
    ram_mb = email_ram + db_ram
    cpu_pct = email_cpu + db_cpu

    x = range(len(labels))

    celery_color = "#37814A"  # Celery green
    flux_color = "#fac500ff"  # FluxQueue yellow

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Duration
    axes[0].bar(
        x,
        duration,
        color=[celery_color, flux_color, celery_color, flux_color],
    )
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("Seconds")
    axes[0].set_title("Duration")

    # RAM (log scale - huge differences)
    axes[1].bar(
        x,
        ram_mb,
        color=[celery_color, flux_color, celery_color, flux_color],
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
        color=[celery_color, flux_color, celery_color, flux_color],
    )
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=20, ha="right")
    axes[2].set_ylabel("CPU (% of total)")
    axes[2].set_title("Average CPU Usage")

    fig.suptitle("Celery vs FluxQueue - Emails & DB Benchmarks", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_email_time_and_ram(output_path: str = "public/emails_overview.png"):
    """
    Single figure showing duration and RAM usage for:
    - Celery (75 processes)
    - FluxQueue (1 worker)
    - FluxQueue (75 workers)
    """
    labels = ["Celery (1 worker)", "FluxQueue (1 worker)", "FluxQueue (75 workers)"]
    celery_color = "#37814A"
    flux_color = "#fac500ff"

    # Data from README (emails benchmark)
    duration = [672.939, 673.882, 52.856]  # seconds
    ram_mb = [5487.89, 88.27, 4615.41]  # MB

    x = range(len(labels))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Duration
    axes[0].bar(x, duration, color=[celery_color, flux_color, flux_color])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("Seconds")
    axes[0].set_title("Email Benchmark - Duration")

    # RAM (log scale to show big differences)
    axes[1].bar(x, ram_mb, color=[celery_color, flux_color, flux_color])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_ylabel("RAM (MB, log scale)")
    axes[1].set_yscale("log")
    axes[1].set_title("Email Benchmark - RAM Usage")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_db_time_and_ram(output_path: str = "public/db_overview.png"):
    """
    Single figure showing duration and RAM usage for:
    - Celery (1 worker, 75 processes)
    - FluxQueue (1 worker, 75 internal executors)
    """
    labels = ["Celery (1 worker)", "FluxQueue (1 worker)"]
    celery_color = "#37814A"
    flux_color = "#fac500ff"

    # Data from README (DB benchmark)
    duration = [78.547, 63.110]  # seconds
    ram_mb = [7046.54, 87.41]  # MB

    x = range(len(labels))

    fig, axes = plt.subplots(1, 2, figsize=(8, 4))

    # Duration
    axes[0].bar(x, duration, color=[celery_color, flux_color])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("Seconds")
    axes[0].set_title("DB Benchmark - Duration")

    # RAM (log scale)
    axes[1].bar(x, ram_mb, color=[celery_color, flux_color])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_ylabel("RAM (MB, log scale)")
    axes[1].set_yscale("log")
    axes[1].set_title("DB Benchmark - RAM Usage")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    plot_combined()
    plot_email_time_and_ram()
    plot_db_time_and_ram()


if __name__ == "__main__":
    main()
