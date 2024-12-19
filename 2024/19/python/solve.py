import argparse
import functools

PATTERNS: list[str] = []


def _parse_file(filename: str) -> tuple[list[str], list[str]]:
    with open(filename, "r") as f:
        raw = f.read()

    raw_patterns, raw_designs = raw.split("\n\n")
    return raw_patterns.strip().split(', '), raw_designs.strip().split('\n')


@functools.cache
def _find_patterns(design: str) -> list[str]:
    if design in PATTERNS:
        return [design]

    for pattern in PATTERNS:
        if design.startswith(pattern):
            remaining = _find_patterns(design[len(pattern) :])  # noqa
            if remaining:
                return [pattern] + remaining
    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    PATTERNS, designs = _parse_file(args.filename)
    arrangements = {design: _find_patterns(design) for design in designs}
    achievable_designs = [design for design, arrangement in arrangements.items() if arrangement]
    print(f"Achievable designs #: {len(achievable_designs)}")
