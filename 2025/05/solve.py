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
) -> set[int]:
    fresh = set()
    for ingredient in available_ingredients:
        for range_ in fresh_ranges:
            if ingredient >= range_[0] and ingredient <= range_[1]:
                fresh.add(ingredient)
                break
    return fresh


def _count_ids(ranges: list[tuple[int]]) -> int:
    def _get_range_size(range_: tuple[int]):
        return (range_[1] - range_[0]) + 1

    new_ranges = _merge_ranges(ranges)
    count = 0
    for range_ in new_ranges:
        count += _get_range_size(range_)
    return count


def _merge_ranges(ranges: list[tuple[int]]) -> list[tuple[int]]:
    ranges.sort(key=lambda r: r[0])
    new_ranges = [ranges[0]]
    for range_ in ranges[1:]:
        prev = new_ranges[-1]
        if range_[0] <= prev[1]:
            new_prev = (prev[0], max(prev[1], range_[1]))
            new_ranges[-1] = new_prev
        else:
            new_ranges.append(range_)
    return new_ranges


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    fresh_ranges, available_ingredients = _parse_file(args.filename)
    fresh_ingredients = _get_fresh_ingredients(fresh_ranges, available_ingredients)
    print(f"{len(fresh_ingredients)} available ingredients are fresh")

    fresh_id_count = _count_ids(fresh_ranges)
    print(f"{fresh_id_count} ingredient IDs are considered fresh")
