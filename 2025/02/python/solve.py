import argparse
import itertools


def _parse_file(filename: str) -> list[tuple[int, int]]:
    with open(filename) as f:
        line = f.read().strip("\n")

    ranges = []
    for product_range in line.split(","):
        start, end = product_range.split("-")
        ranges.append((int(start), int(end)))
    return ranges


def _find_invalid_ids_part_1(start: int, end: int):
    for product_id in range(start, end + 1):
        product_id = str(product_id)
        length = len(product_id)
        if length % 2 == 0:
            halfway = int(length / 2)
            if product_id[:halfway] == product_id[halfway:]:
                yield int(product_id)


def _find_invalid_ids_part_2(start: int, end: int):
    for product_id in range(start, end + 1):
        product_id = str(product_id)
        length = len(product_id)
        for subrange in range(1, int((length / 2) + 1)):
            if length % subrange != 0:
                continue
            pattern = product_id[:subrange]
            if product_id == pattern * int(length / len(pattern)) and pattern != product_id:
                yield int(product_id)
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    ranges = _parse_file(args.filename)
    bad_product_ids = itertools.chain.from_iterable(
        _find_invalid_ids_part_1(start, end) for start, end in ranges
    )
    result = sum(bad_product_ids)
    print(f"Sum of invalid IDs: {result}")

    bad_product_ids = itertools.chain.from_iterable(
        _find_invalid_ids_part_2(start, end) for start, end in ranges
    )
    result = sum(bad_product_ids)
    print(f"Sum of invalid IDs: {result}")
