import argparse
import itertools
import typing

Key: typing.TypeAlias = list[int]
Lock: typing.TypeAlias = list[int]


def _parse_file(filename: str) -> tuple[list[Key], list[Lock]]:
    with open(filename, "r") as f:
        raw = f.read().strip()
    return _build_schematics(raw.split('\n\n'))


def _build_schematics(raw_schematics: list[str]) -> tuple[list[Lock], list[Key]]:
    keys = []
    locks = []
    for schematic in raw_schematics:
        rows = schematic.split("\n")

        final = [-1] * len(rows[0])
        for row in rows:
            for i, column in enumerate(row):
                if column == "#":
                    final[i] += 1

        if all(c == "#" for c in rows[0]):
            locks.append(final)
        elif all(c == "#" for c in rows[-1]):
            keys.append(final)
        else:
            raise ValueError("Schematic is neither lock nor key")

    return locks, keys


def _find_non_overlap(locks: list[Lock], keys: list[Key]) -> list[tuple[Lock, Key]]:
    matches = []
    for lock, key in itertools.product(locks, keys):
        if all(tumbler_pin + key_pin <= 5 for tumbler_pin, key_pin in zip(lock, key)):
            matches.append((lock, key))
    return matches


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    locks, keys = _parse_file(args.filename)
    matches = _find_non_overlap(locks, keys)
    print(f"Unique key/lock pairs: {len(matches)}")
