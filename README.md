# FluxQueue Benchmarks

Performance benchmarks comparing FluxQueue and Celery across different workloads.

## Email Processing

### Test Configuration

All benchmarks process 10,000 email requests. Concurrency refers to the `--concurrency` argument for both `fluxqueue` and `celery`, but they have different meanings internally. For `celery`, it also means the number of Python processes it's going to spawn. For `fluxqueue`, it means the number of `tokio` async threads within a single process.

### Results

#### Celery

- **Total Requests**: 10,000
- **Concurrency**: 75
- **Processes**: 75
- **Duration**: 672.936 seconds
- **Average RAM Usage**: 5,616 MB
- **Average CPU Usage**: 67.5%

#### FluxQueue (Single Process)

- **Total Requests**: 10,000
- **Concurrency**: 75 per process
- **Processes**: 1
- **Duration**: 671.204 seconds
- **Average RAM Usage**: 89.09 MB
- **Average CPU Usage**: 0.93%

#### FluxQueue (75 fluxqueue workers)

- **Total Requests**: 10,000
- **Concurrency**: 75 per process
- **Processes**: 75
- **Duration**: 52.831 seconds
- **Average RAM Usage**: 4,670.50 MB
- **Average CPU Usage**: 54.59%

### Summary

FluxQueue with a single process (worker) matches Celery's performance while using significantly less resources (89 MB vs 5,616 MB RAM, 0.93% vs 67.5% CPU). When scaled to 75 processes, FluxQueue completes the same workload 12.7x faster than Celery (52.8 seconds vs 672.9 seconds) with similar resource usage.
