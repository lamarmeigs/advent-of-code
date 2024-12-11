import argparse


def _parse_file(filename: str) -> list[int]:
    with open(filename, 'r') as f:
        raw = f.read()
    return [int(d) for d in raw.strip().split()]


def _blink(stones: list[int]) -> list[int]:
    new_stones = []
    for stone in stones:
        if stone == 0:
            new_stones.append(1)
        elif len(str_stone := str(stone)) % 2 == 0:
            half_index = len(str_stone) // 2
            new_1, new_2 = str_stone[:half_index], str_stone[half_index:]
            new_stones.extend([int(new_1), int(new_2)])
        else:
            new_stones.append(stone * 2024)
    return new_stones


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    stones = _parse_file(args.filename)
    for _ in range(25):
        stones = _blink(stones)
    print(f'Number of stones after 25 blinks: {len(stones)}')
