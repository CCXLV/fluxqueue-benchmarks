# FluxQueue Benchmarks

Performance benchmarks comparing FluxQueue and Celery across different workloads.

## Tested scenarios

- [x] Emails
- [ ] API Calling
- [ ] DB Queries
- ...

## Test machine

- **CPU**: 12th Gen Intel Core i5-12500H (16 logical CPUs)
- **Memory**: 16 GB RAM
- **OS**: Linux (Arch), kernel 6.18.7-arch1-1 (x86_64)

## Test Configuration

Concurrency refers to the `--concurrency` argument for both `fluxqueue` and `celery`, but they have different meanings internally. For `celery`, it also means the number of Python processes it's going to spawn. For `fluxqueue`, it means the number of `tokio` async threads within a single process.

## Email Processing Results

All benchmarks process 10,000 emails.

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

FluxQueue with a single worker (process) matches Celery's performance while using significantly less resources (89 MB vs 5,616 MB RAM, 0.93% vs 67.5% CPU). When scaled to 75 workers, FluxQueue completes the same workload 12.7x faster than Celery (52.8 seconds vs 672.9 seconds) with similar resource usage.

Key points:

- FluxQueue matches Celery’s throughput with ~98% less memory in single-worker mode.
- Under equal RAM constraints, FluxQueue scales horizontally and completes the same workload ~12.7× faster than Celery.
- FluxQueue achieves ~15× higher throughput per GB of RAM compared to Celery.
- Celery is memory-bound, while FluxQueue remains CPU-bound under load.
