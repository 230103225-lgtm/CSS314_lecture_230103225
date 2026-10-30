
import multiprocessing as mp
import os
import statistics
import time
import csv


K = 5_000_000
PROCESS_COUNTS = [1, 2, 4, 8]
PADDING_FACTOR = 8


def worker(shared, index, count, lock=None):
    local_count = 0

    for _ in range(count):
        local_count += 1

    if lock is None:
        shared[index] = local_count
    else:
        with lock:
            shared[index] = local_count


def run_experiment(method, process_count):
    ctx = mp.get_context("spawn")

    if method == "unpadded":
        shared = ctx.Array("q", process_count, lock=False)
        indices = list(range(process_count))
        lock = None

    elif method == "padded":
        shared = ctx.Array(
            "q",
            process_count * PADDING_FACTOR,
            lock=False
        )
        indices = [p * PADDING_FACTOR for p in range(process_count)]
        lock = None

    elif method == "privatized":
        shared = ctx.Array("q", process_count, lock=False)
        indices = list(range(process_count))
        lock = ctx.Lock()

    else:
        raise ValueError("Unknown method")

    processes = []

    start = time.perf_counter()

    for p in range(process_count):
        process = ctx.Process(
            target=worker,
            args=(shared, indices[p], K, lock)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    elapsed = time.perf_counter() - start

    for process in processes:
        if process.exitcode != 0:
            raise RuntimeError(
                f"Worker failed with exit code {process.exitcode}"
            )

    values = [shared[index] for index in indices]
    expected = [K] * process_count

    if values != expected:
        raise ValueError(
            f"Incorrect counters: {values}, expected: {expected}"
        )

    return elapsed, sum(values)


def karp_flatt(t1, tp, p):
    if p <= 1:
        return None

    speedup = t1 / tp

    if speedup == 0:
        return None

    return (1 / speedup - 1 / p) / (1 - 1 / p)


def main():
    os.makedirs("results", exist_ok=True)

    methods = ["unpadded", "padded", "privatized"]
    all_results = []

    print("False Sharing Benchmark")
    print(f"Increments per process: {K:,}")
    print(f"Process counts: {PROCESS_COUNTS}")

    for method in methods:
        print(f"\n===== {method.upper()} =====")

        method_results = {}

        for p in PROCESS_COUNTS:
            print(f"Running with {p} process(es)...")

            elapsed, total = run_experiment(method, p)

            method_results[p] = elapsed

            print(
                f"P={p} | Time={elapsed:.4f} sec "
                f"| Total={total:,}"
            )

        t1 = method_results[1]

        for p in PROCESS_COUNTS:
            elapsed = method_results[p]
            efficiency = karp_flatt(t1, elapsed, p)

            all_results.append({
                "method": method,
                "processes": p,
                "K_per_process": K,
                "time_seconds": elapsed,
                "karp_flatt": (
                    efficiency if efficiency is not None else ""
                )
            })

    output_path = "results/false_sharing_karp_flatt.tsv"

    with open(output_path, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "method",
                "processes",
                "K_per_process",
                "time_seconds",
                "karp_flatt"
            ],
            delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(all_results)

    print("\nAll experiments completed.")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
