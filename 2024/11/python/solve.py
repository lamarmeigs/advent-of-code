import argparse
import collections


known_blinks = collections.defaultdict(dict)


def _parse_file(filename: str) -> list[int]:
    with open(filename, "r") as f:
        raw = f.read()
    return [int(d) for d in raw.strip().split()]


def _get_next_value(stone: int):
    if stone == 0:
        return [1]
    elif len(str_stone := str(stone)) % 2 == 0:
        half_index = len(str_stone) // 2
        new_value_1 = int(str_stone[:half_index])
        new_value_2 = int(str_stone[half_index:])
        return [new_value_1, new_value_2]
    else:
        return [stone * 2024]


def _blink(stone: int, count: int) -> list[int]:
    if count == 0:
        return 0
    elif known_length := known_blinks.get(stone, {}).get(count):
        return known_length

    next_value = _get_next_value(stone)
    if count == 1:
        known_blinks[stone][count] = len(next_value)
        return len(next_value)
    else:
        length = sum(_blink(value, count - 1) for value in next_value)
        known_blinks[stone][count] = length
        return length


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    stones = _parse_file(args.filename)
    stone_count = 0
    for stone in stones:
        stone_count += _blink(stone, 25)
    print(f"Number of stones after 25 blinks: {stone_count}")

    stone_count = 0
    for stone in stones:
        stone_count += _blink(stone, 75)
    print(f"Number of stones after 75 blinks: {stone_count}")
