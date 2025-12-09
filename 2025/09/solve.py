import argparse
import itertools


def _parse_file(filename: str) -> list[tuple[int, int]]:
    with open(filename) as f:
        lines = f.readlines()
    tiles = []
    for line in lines:
        x, y = line.split(',')
        tiles.append((int(x), int(y)))
    return tiles


def _calculate_area(tile_1: tuple[int, int], tile_2: tuple[int, int]) -> int:
    return (abs(tile_1[0] - tile_2[0]) + 1) * (abs(tile_1[1] - tile_2[1]) + 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    tiles = _parse_file(args.filename)
    rectangles = itertools.permutations(tiles, 2)
    largest_area = max(_calculate_area(tile_1, tile_2) for tile_1, tile_2 in rectangles)
    print(f"Area of largest rectangle: {largest_area}")
