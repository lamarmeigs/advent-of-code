import argparse
import functools

PATTERNS: list[str] = []


def _parse_file(filename: str) -> tuple[list[str], list[str]]:
    with open(filename, "r") as f:
        raw = f.read()

    raw_patterns, raw_designs = raw.split("\n\n")
    return raw_patterns.strip().split(', '), raw_designs.strip().split('\n')


@functools.cache
def _find_patterns(design: str) -> int:
    arrangements = 0
    for pattern in PATTERNS:
        if pattern == design:
            arrangements += 1
        elif design.startswith(pattern):
            remaining_design = design[len(pattern) :]  # noqa
            remaining_arrangements = _find_patterns(remaining_design)
            arrangements += remaining_arrangements

    return arrangements


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    PATTERNS, designs = _parse_file(args.filename)
    arrangements = {design: _find_patterns(design) for design in designs}
    achievable_designs = [design for design, arrangements in arrangements.items() if arrangements]
    print(f"Achievable designs #: {len(achievable_designs)}")
    print(f"Total arrangements #: {sum(arrangements.values())}")
