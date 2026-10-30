
import os
import time
import statistics
import numpy as np


def benchmark_stride(data, stride):
    total_elements = len(data[::stride])

    for _ in range(5):
        data[::stride].sum(dtype=np.float64)

    timings = []

    for _ in range(5):
        start = time.perf_counter_ns()

        total = data[::stride].sum(dtype=np.float64)

        end = time.perf_counter_ns()
        timings.append(end - start)

    median_time = statistics.median(timings)
    latency = median_time / total_elements

    return {
        "stride": stride,
        "elements_touched": total_elements,
        "median_time_ns": median_time,
        "latency_per_element_ns": latency,
        "checksum": float(total)
    }


def main():
    os.makedirs("results", exist_ok=True)

    print("Allocating 128 MB array...")
    data = np.ones(16_777_216, dtype=np.float64)

    strides = [1, 2, 4, 8, 16, 32, 64, 128]

    results = []

    print("\nStarting stride benchmark...\n")

    for stride in strides:
        result = benchmark_stride(data, stride)
        results.append(result)

        print(
            f"Stride: {stride:3d} | "
            f"Elements: {result['elements_touched']:10d} | "
            f"Median: {result['median_time_ns'] / 1e6:.3f} ms | "
            f"Latency: {result['latency_per_element_ns']:.3f} ns"
        )

    output_file = "results/stride_results.tsv"

    with open(output_file, "w") as file:
        file.write(
            "stride\telements_touched\tmedian_time_ns\t"
            "latency_per_element_ns\tchecksum\n"
        )

        for result in results:
            file.write(
                f"{result['stride']}\t"
                f"{result['elements_touched']}\t"
                f"{result['median_time_ns']}\t"
                f"{result['latency_per_element_ns']:.6f}\t"
                f"{result['checksum']:.1f}\n"
            )

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
