import argparse
import json
import os
import platform
import re
import subprocess
import sys


def get_sysctl_value(key):
    try:
        result = subprocess.check_output(
            ["sysctl", "-n", key],
            text=True,
            stderr=subprocess.DEVNULL
        )
        return result.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_cpu_frequency(cpu_name):
    match = re.search(r"@\s*([\d.]+)\s*GHz", cpu_name)
    if match:
        return float(match.group(1))
    return None


def get_hardware_profile():
    cpu_name = (
        get_sysctl_value("machdep.cpu.brand_string")
        or platform.processor()
        or "Unknown"
    )

    profile = {
        "cpu_model": cpu_name,
        "microarchitecture": "Coffee Lake",
        "base_frequency_ghz": get_cpu_frequency(cpu_name),
        "physical_cores": int(get_sysctl_value("hw.physicalcpu") or 0),
        "logical_threads": int(get_sysctl_value("hw.logicalcpu") or 0),
        "cache": {
            "L1_data_bytes": int(get_sysctl_value("hw.l1dcachesize") or 0),
            "L2_bytes": int(get_sysctl_value("hw.l2cachesize") or 0),
            "L3_bytes": int(get_sysctl_value("hw.l3cachesize") or 0),
            "cache_line_bytes": int(get_sysctl_value("hw.cachelinesize") or 0)
        },
        "operating_system": platform.system(),
        "os_version": subprocess.check_output(["sw_vers", "-productVersion"], text=True).strip(),
        "kernel_version": platform.release(),
        "architecture": platform.machine(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable
        }
    }

    return profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", required=True)
    args = parser.parse_args()

    from salt import get_student_params

    os.makedirs("results", exist_ok=True)

    profile = get_hardware_profile()
    params = get_student_params(args.student_id)

    with open("results/host_profile.json", "w") as file:
        json.dump(profile, file, indent=4)

    with open("results/salted_params.json", "w") as file:
        json.dump(params, file, indent=4)

    print("Hardware profile saved successfully.")
    print(json.dumps(profile, indent=4))
    print("\nSalted parameters:")
    print(json.dumps(params, indent=4))


if __name__ == "__main__":
    main()
