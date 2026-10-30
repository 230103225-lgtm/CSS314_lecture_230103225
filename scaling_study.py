
import csv
import json
import math
import multiprocessing as mp
import os
import statistics
import time

import numpy as np

from salt import get_student_params


def stencil_worker(args):
    start_row, end_row, matrix = args

    result = (
        4.0 * matrix[start_row:end_row, 1:-1]
        - matrix[start_row - 1:end_row - 1, 1:-1]
        - matrix[start_row + 1:end_row + 1, 1:-1]
        - matrix[start_row:end_row, :-2]
        - matrix[start_row:end_row, 2:]
    )

    return float(np.sum(result))


def run_stencil(N, processes, seed):
    rng = np.random.default_rng(seed)
    matrix = rng.random((N + 2, N + 2), dtype=np.float64)

    rows_per_process = math.ceil(N / processes)
    tasks = []

    for p in range(processes):
        start = p * rows_per_process + 1
        end = min((p + 1) * rows_per_process, N) + 1

        if start < end:
            tasks.append((start, end, matrix))

    start_time = time.perf_counter()

    if processes == 1:
        checksums = [stencil_worker(tasks[0])]
    else:
        with mp.get_context("spawn").Pool(processes) as pool:
            checksums = pool.map(stencil_worker, tasks)

    elapsed = time.perf_counter() - start_time

    return elapsed, sum(checksums)


def main():
    params = get_student_params("230103225")

    N = params["N"]
    seed = params["seed"]

    physical_cores = 4
    process_counts = [1, 2, 4]

    os.makedirs("results", exist_ok=True)

    print("SCALING STUDY")
    print(f"Salted N: {N}")
    print(f"Physical cores: {physical_cores}")

    strong_results = []

    print("\n--- STRONG SCALING ---")

    for p in process_counts:
        print(f"Running P={p}...")

        times = []
        checksums = []

        for _ in range(3):
            elapsed, checksum = run_stencil(N, p, seed)
            times.append(elapsed)
            checksums.append(checksum)

        median_time = statistics.median(times)

        strong_results.append({
            "processes": p,
            "time": median_time,
            "checksum": statistics.median(checksums)
        })

        print(f"P={p}, median={median_time:.4f} sec")

    t1 = strong_results[0]["time"]

    scaling_rows = []

    for result in strong_results:
        p = result["processes"]
        elapsed = result["time"]

        speedup = t1 / elapsed
        efficiency = speedup / p * 100

        if p > 1:
            serial_fraction = (
                (1 / speedup - 1 / p) / (1 - 1 / p)
            )
            amdahl_max = (
                1 / serial_fraction
                if serial_fraction > 0 else None
            )
        else:
            serial_fraction = 0
            amdahl_max = None

        scaling_rows.append({
            "processes": p,
            "time_seconds": elapsed,
            "speedup": speedup,
            "efficiency_percent": efficiency,
            "serial_fraction": serial_fraction,
            "amdahl_max_speedup": amdahl_max
        })

    print("\n--- WEAK SCALING ---")

    weak_results = []

    for p in process_counts:
        scaled_N = math.ceil(N * math.sqrt(p))

        print(f"Running P={p}, N={scaled_N}...")

        elapsed, checksum = run_stencil(scaled_N, p, seed)

        weak_results.append({
            "processes": p,
            "scaled_N": scaled_N,
            "time_seconds": elapsed,
            "checksum": checksum
        })

        print(f"Time={elapsed:.4f} sec")

    with open(
        "results/scaling_metrics.tsv",
        "w",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(scaling_rows[0].keys()),
            delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(scaling_rows)

    roofline = {
        "cpu": "Intel Core i5-8279U",
        "microarchitecture": "Coffee Lake",
        "physical_cores": physical_cores,
        "cache_line_bytes": 64,
        "arithmetic_intensity_estimate_flops_per_byte": 0.125,
        "classification": "Memory-bound (estimated)",
        "note": "Estimate based on stencil memory access pattern."
    }

    with open(
        "results/roofline_summary.json",
        "w"
    ) as file:
        json.dump({
            "roofline": roofline,
            "weak_scaling": weak_results
        }, file, indent=4)

    print("\nResults saved:")
    print("results/scaling_metrics.tsv")
    print("results/roofline_summary.json")


if __name__ == "__main__":
    main()
