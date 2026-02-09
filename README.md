# FluxQueue Benchmarks

Performance benchmarks comparing FluxQueue and Celery across different workloads on a FastAPI server.

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

Concurrency refers to the `concurrency` argument for both `fluxqueue` and `celery`, but they have different meanings internally. For `celery`, it also means the number of Python processes it's going to spawn. For `fluxqueue`, it means the number of `tokio` async threads within a single process.

## Email Processing Results

All benchmarks process 10,000 requests, each enqueues a task that sends an email on a local SMTP server. Email has html as body and its total size is about 4.4kb and both Celery and FluxQueue takes about 5 seconds to finish the task. The tasks are done Asynchronously.

#### Celery

- **Total Requests**: 10,000
- **Concurrency**: 75
- **Processes**: 75
- **Duration**: 672.939 seconds
- **Average RAM Usage**: 5,487.89 MB
- **Average CPU Usage**: 1.05% (of total 16-core CPU)

#### FluxQueue (Single Worker)

- **Total Requests**: 10,000
- **Concurrency**: 75 per process
- **Processes**: 1
- **Duration**: 673.882 seconds
- **Average RAM Usage**: 88.27 MB
- **Average CPU Usage**: 0.72% (of total 16-core CPU)

#### FluxQueue (75 Workers)

- **Total Requests**: 10,000
- **Concurrency**: 75 per process
- **Processes**: 75
- **Duration**: 52.856 seconds
- **Average RAM Usage**: 4,615.41 MB
- **Average CPU Usage**: 4.84% (of total 16-core CPU)

### Summary

FluxQueue with a single worker (process) matches Celery's performance while using significantly less resources (~88 MB vs 5,488 MB RAM, ~0.7% vs 1.05% CPU). When scaled to 75 workers, FluxQueue completes the same workload ~12.7x faster than Celery (~52.9 seconds vs 672.9 seconds) with similar RAM usage but moderately higher CPU utilization (~4.8% vs 1.05%).

Key points:

- FluxQueue matches Celery’s throughput with ~98% less memory in single-worker mode.
- Under equal RAM constraints, FluxQueue scales horizontally and completes the same workload ~12.7× faster than Celery.
- FluxQueue achieves ~15× higher throughput per GB of RAM compared to Celery.
- Celery is memory-heavy, while FluxQueue achieves similar or better throughput with far less memory and CPU usage.
