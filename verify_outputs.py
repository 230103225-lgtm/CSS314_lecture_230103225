
import json
import os
import csv
import hashlib
import sys

RESULTS = "results"

required_files = [
    "host_profile.json",
    "salted_params.json",
    "stride_results.tsv",
    "loop_interchange.json",
    "false_sharing_karp_flatt.tsv",
    "scaling_metrics.tsv",
    "roofline_summary.json",
]

errors = []
checks = []

def check(condition, message):
    if condition:
        print("[PASS]", message)
        checks.append(message)
    else:
        print("[FAIL]", message)
        errors.append(message)


def main():
    print("FINAL PROJECT VERIFICATION")
    print("=" * 45)

    for filename in required_files:
        path = os.path.join(RESULTS, filename)
        check(os.path.isfile(path), f"File exists: {path}")

    if errors:
        print("\nSome required files are missing.")
        sys.exit(1)

    with open(os.path.join(RESULTS, "host_profile.json")) as f:
        host = json.load(f)

    check(host.get("physical_cores", 0) == 4,
          "Physical CPU cores = 4")

    with open(os.path.join(RESULTS, "salted_params.json")) as f:
        params = json.load(f)

    check(params.get("student_id") == "230103225",
          "Student ID matches")

    check(params.get("N") == 1472,
          "Salted N = 1472")

    check(params.get("buffer_elements") == 16777216,
          "Buffer elements = 16777216")

    with open(os.path.join(RESULTS, "stride_results.tsv")) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    check(len(rows) == 8, "Eight stride measurements exist")

    with open(os.path.join(RESULTS, "loop_interchange.json")) as f:
        loop = json.load(f)

    check(loop.get("results_match") is True,
          "Matrix multiplication results match")

    check(loop.get("matrix_size") == 736,
          "Matrix size = 736")

    with open(os.path.join(
        RESULTS, "false_sharing_karp_flatt.tsv"
    )) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    check(len(rows) == 12,
          "Twelve false-sharing measurements exist")

    with open(os.path.join(RESULTS, "scaling_metrics.tsv")) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    check(len(rows) == 3,
          "Three strong-scaling measurements exist")

    with open(os.path.join(RESULTS, "roofline_summary.json")) as f:
        roofline = json.load(f)

    check("roofline" in roofline and "weak_scaling" in roofline,
          "Roofline and weak-scaling data exist")

    digest = hashlib.sha256(
        json.dumps(checks, sort_keys=True).encode()
    ).hexdigest()

    with open("verification_receipt.sig", "w") as f:
        f.write(digest + "\n")

    print("\n" + "=" * 45)
    print(f"Passed: {len(checks)}")
    print(f"Failed: {len(errors)}")
    print("Receipt: verification_receipt.sig")

    if errors:
        sys.exit(1)

    print("\nVERIFICATION COMPLETED")


if __name__ == "__main__":
    main()
