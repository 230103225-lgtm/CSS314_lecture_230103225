
import json
import os
import statistics
import time

import numpy as np

from salt import get_student_params


def multiply_ijk(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(n):
            total = 0.0
            for k in range(n):
                total += A[i, k] * B[k, j]
            C[i, j] = total

    return C


def multiply_ikj(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for k in range(n):
            a = A[i, k]
            for j in range(n):
                C[i, j] += a * B[k, j]

    return C


def benchmark(func, A, B, repeats=3):
    times = []
    result = None

    for _ in range(repeats):
        start = time.perf_counter()
        result = func(A, B)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return statistics.median(times), result


def main():
    params = get_student_params("230103225")

    N = params["N"]
    M = N // 2
    seed = params["seed"]

    print(f"Salted N: {N}")
    print(f"Matrix size: {M} x {M}")

    rng = np.random.default_rng(seed)

    A = rng.random((M, M), dtype=np.float64)
    B = rng.random((M, M), dtype=np.float64)

    print("\nRunning i-j-k benchmark...")
    time_ijk, C_ijk = benchmark(multiply_ijk, A, B)

    print("\nRunning i-k-j benchmark...")
    time_ikj, C_ikj = benchmark(multiply_ikj, A, B)

    if not np.allclose(C_ijk, C_ikj, rtol=1e-12, atol=1e-12):
        raise ValueError("Matrix results do not match!")

    speedup = time_ijk / time_ikj

    results = {
        "student_id": params["student_id"],
        "N": N,
        "matrix_size": M,
        "ijk_median_seconds": time_ijk,
        "ikj_median_seconds": time_ikj,
        "speedup": speedup,
        "results_match": True
    }

    os.makedirs("results", exist_ok=True)

    with open("results/loop_interchange.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\n--- Results ---")
    print(f"i-j-k: {time_ijk:.4f} seconds")
    print(f"i-k-j: {time_ikj:.4f} seconds")
    print(f"Speedup: {speedup:.4f}x")
    print("Matrix results match!")
    print("Saved to results/loop_interchange.json")


if __name__ == "__main__":
    main()
