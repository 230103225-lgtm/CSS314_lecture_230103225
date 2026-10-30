# CS482 — Parallel Computing & Performance Optimization

## Student Information
- Student ID: 230103225
- CPU: Intel Core i5-8279U
- Microarchitecture: Coffee Lake
- Physical cores: 4
- Logical threads: 8
- Operating System: macOS
- Python: 3.13.5
- NumPy: 2.1.3

## Project Structure
- `src/profile_env.py` — hardware profiling
- `src/salt.py` — student-specific parameters
- `src/stride_bench.py` — memory stride benchmark
- `src/dense_kernel.py` — loop interchange benchmark
- `src/false_sharing.py` — false sharing experiments
- `src/scaling_study.py` — strong and weak scaling
- `verify_outputs.py` — output verification

## Benchmark Results

### Milestone 1 — Memory Locality
- Tested strides: 1, 2, 4, 8, 16, 32, 64, 128.
- Matrix size: 736 × 736.
- i-j-k median: 129.7604 seconds.
- i-k-j median: 155.5555 seconds.
- Speedup: 0.8342×.
- Matrix results matched.

### Milestone 2 — False Sharing
- Tested unpadded, padded and privatized counters.
- Process counts: 1, 2, 4, 8.
- Increments per process: 5,000,000.
- Counter totals were verified.

### Milestone 3 — Scaling Study
- Strong scaling: 1, 2, 4 processes.
- Weak scaling: 1, 2, 4 processes.
- Results saved in the `results` directory.

### Milestone 4 — Verification
- Verification checks passed: 17.
- Failed checks: 0.
- Verification receipt: `verification_receipt.sig`.

## Running the Project

Run commands from the project root:

```bash
python3 src/profile_env.py --student-id 230103225
python3 src/stride_bench.py
python3 src/dense_kernel.py
python3 src/false_sharing.py
python3 src/scaling_study.py
python3 verify_outputs.py
```

## Results Directory
All benchmark outputs are stored in `results/`.
