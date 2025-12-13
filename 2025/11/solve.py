import argparse
import functools


def _parse_file(filename: str) -> dict[str, list[str]]:
    with open(filename) as f:
        lines = f.readlines()

    devices = {}
    for line in lines:
        device, outputs = line.split(":")
        devices[device] = outputs.split()
    devices["out"] = []
    return devices


class PathFinder:
    def __init__(self, devices):
        self.devices = devices

    @functools.cache
    def count_paths(
        self,
        start: str,
        end: str,
        required: tuple[str] = (),
    ) -> int:
        if start == end:
            return 1 if not required else 0
        if start in required:
            required = tuple(device for device in required if device != start)

        neighbors = self.devices[start]
        return sum(self.count_paths(neighbor, end, required) for neighbor in neighbors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    devices = _parse_file(args.filename)
    path_finder = PathFinder(devices)

    paths_to_out = path_finder.count_paths("you", "out")
    print(f"Number of paths to 'out': {paths_to_out}")

    paths_to_out = path_finder.count_paths("svr", "out", required=("fft", "dac"))
    print(f"Number of paths to 'out': {paths_to_out}")
