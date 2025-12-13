import argparse
import collections


def _parse_file(filename: str) -> dict[str, list[str]]:
    with open(filename) as f:
        lines = f.readlines()

    devices = {}
    for line in lines:
        device, outputs = line.split(":")
        devices[device] = outputs.split()
    devices["out"] = []
    return devices


def _count_paths(devices: dict[str, list[str]]) -> int:
    paths_to = collections.defaultdict(int)
    next_devices = ["you"]
    while len(next_devices) > 0:
        next_device = next_devices.pop(-1)
        paths_to[next_device] += 1
        next_devices.extend(devices[next_device])
    return paths_to["out"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    devices = _parse_file(args.filename)
    paths_to_out = _count_paths(devices)
    print(f"Number of paths to 'out': {paths_to_out}")
