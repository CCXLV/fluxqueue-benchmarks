# FluxQueue Benchmarks

## FluxQueue vs Celery

### Emails

#### Celery

concurrency = process

- **Total Requests** - 10,000
- **Concurrency** - 75
- **Processes** - 75
- **Start-to-finish** - 672.936 seconds

- **Average usages**:
  - RAM - 5,616 MB
  - CPU - 67.5%
 
#### FluxQueue

process = number of running worker

- **Total Requests** - 10,000
- **Concurrency (per process)**  - 75
- **Processes** - 1

- **Start-to-finish** - 671.204379 seconds

- **Average usages**:
  - RAM - 89.09 MB
  - CPU - 0.93 %

### FluxQueue (75 Processs)

process = number of running worker

- **Total Requests** - 10,000
- **Concurrency (per process)**  - 75
- **Processes** - 75

- **Start-to-finish** - 52.830544 seconds

- **Average usages**:
  - RAM - 4670.50 MB
  - CPU - 54.59 %
