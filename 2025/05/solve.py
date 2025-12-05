import argparse
import re


def _parse_file(filename: str) -> tuple[list[tuple[int]], list[int]]:
    with open(filename) as f:
        raw = f.read().strip("\n")
    raw_ranges, ids = raw.split("\n\n")

    ranges = []
    for raw_range in raw_ranges.split("\n"):
        match = re.match(r"(\d+)-(\d+)", raw_range)
        ranges.append(tuple(int(m) for m in match.groups()))
    return ranges, [int(id_) for id_ in ids.split("\n")]


def _get_fresh_ingredients(
    fresh_ranges: list[tuple[int]],
    available_indients: list[int],
) -> list[int]:
    fresh = set()
    for ingredient in available_ingredients:
        for range_ in fresh_ranges:
            if ingredient >= range_[0] and ingredient <= range_[1]:
                fresh.add(ingredient)
                break
    return fresh


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    fresh_ranges, available_ingredients = _parse_file(args.filename)
    fresh_ingredients = _get_fresh_ingredients(fresh_ranges, available_ingredients)
    print(f"{len(fresh_ingredients)} available ingredients are fresh")
