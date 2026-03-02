# FluxQueue Benchmarks

Performance benchmarks comparing FluxQueue and Celery across different workloads on a FastAPI server.

## Charts

![Celery vs FluxQueue – Emails & DB Benchmarks](public/combined_overview.png)

### Email overview

![Email Benchmark – Duration & RAM](public/emails_overview.png)

### DB overview

![DB Benchmark – Duration & RAM](public/db_overview.png)

## Tested scenarios

- [x] Emails
- [x] DB Queries
- [ ] API Calling
- ...

## Test machine

- **CPU**: 12th Gen Intel Core i5-12500H (16 logical CPUs)
- **Memory**: 16 GB RAM
- **OS**: Linux (Arch), kernel 6.18.7-arch1-1 (x86_64)

## Test Configuration

Concurrency refers to the `concurrency` argument for both `fluxqueue` and `celery`, but they have different meanings internally. For `celery`, it also means the number of Python processes it's going to spawn. For `fluxqueue`, it means the number of `tokio task`s its going to spawn.

## Email Processing Results

All benchmarks process 10,000 requests on a FastAPI server with 8 `uvicorn` workers, each enqueues a task that sends an email on a local SMTP server. Email has HTML as body and its total size is about 4.4kb and both Celery and FluxQueue take about 5 seconds to finish the task. The tasks are done asynchronously.

#### Celery

- **Total Requests**: 10,000
- **Concurrency**: 75
- **Processes**: 75
- **Duration**: 691.743 seconds
- **Average RAM Usage**: 6525.47 MB
- **Average CPU Usage**: 2.57% (of total 16-core CPU)

#### FluxQueue (Single Worker)

- **Total Requests**: 10,000
- **Uvicorn Workers**: 8
- **Internal Executors (concurrency)**: 75
- **Processes**: 1
- **Duration**: 674.072 seconds
- **Average RAM Usage**: 107.32 MB
- **Average CPU Usage**: 1.01% (of total 16-core CPU)

#### FluxQueue (75 Workers)

- **Total Requests**: 10,000
- **Uvicorn Workers**: 8
- **Internal Executors (concurrency)**: 75 per process
- **Processes**: 75 (running workers)
- **Duration**: 58.735 seconds
- **Average RAM Usage**: 6614.60 MB
- **Average CPU Usage**: 8.93% (of total 16-core CPU)

### Summary (Emails)

FluxQueue with a single worker (process) matches Celery's performance while using significantly less resources (~107 MB vs 6,525 MB RAM, ~1.0% vs 2.6% CPU). When scaled to 75 workers, FluxQueue completes the same workload ~11.8x faster than Celery (~58.7 seconds vs 691.7 seconds) with similar RAM usage but higher CPU utilization (~8.9% vs 2.6%).

Key points:

- FluxQueue matches Celery’s throughput with ~98% less memory in single-worker mode.
- Under equal RAM constraints, FluxQueue scales horizontally and completes the same workload ~11.8x faster than Celery.
- FluxQueue achieves ~12x higher throughput per GB of RAM compared to Celery.
- Celery is memory-heavy, while FluxQueue achieves similar or better throughput with far less memory and CPU usage for email workloads.

## Database Query Results

All benchmarks process 10,000 HTTP requests on a FastAPI server with 8 `uvicorn` workers. Each request enqueues a task that performs two `SELECT` queries on a 1M-row table, does some simple calculations, and inserts the result into another table in a Postgres database. Database connections and queries are done asynchronously using the `asyncpg` library.

#### Celery (1 worker, 75 processes)

- **Total Requests**: 10,000
- **Uvicorn Workers**: 8
- **Celery Workers**: 1
- **Processes (concurrency)**: 75
- **Duration**: 75.980 seconds
- **Average RAM Usage**: 6295.37 MB
- **Average CPU Usage**: 9.00% (0.56% per core, 16 cores)

#### FluxQueue (1 worker, 75 internal executors)

- **Total Requests**: 10,000
- **Uvicorn Workers**: 8
- **FluxQueue Workers**: 1
- **Processes**: 1
- **Internal Executors (concurrency)**: 75
- **Duration**: 65.777 seconds
- **Average RAM Usage**: 112.42 MB
- **Average CPU Usage**: 3.96% (0.25% per core, 16 cores)

### Summary (DB queries)

For database-heavy workloads, FluxQueue completes the same workload while using far fewer resources. In this benchmark, FluxQueue finishes in 65.8 seconds and Celery in 76.0 seconds, with FluxQueue using ~56x less RAM (≈112 MB vs ≈6,295 MB) and about 2.3x less CPU (3.96% vs 9.00% total CPU).

Key points:

- Celery achieves good throughput but with very high RAM usage for DB-heavy workloads.
- FluxQueue trades a small amount of scheduling overhead for dramatically lower RAM and CPU usage.
- When memory and CPU are constrained, FluxQueue can handle the same DB workload more efficiently than Celery.

## Overall Takeaways

- For both email and DB workloads, FluxQueue completes the same tasks in comparable wall-clock time while using significantly less memory and CPU than Celery.
- Because a single FluxQueue worker uses much less memory than a single Celery worker, the same total memory budget that Celery uses for its processes could instead be used to run many more FluxQueue workers. In that regime, FluxQueue would be able to complete the workload much faster than Celery at similar or lower total resource usage.
