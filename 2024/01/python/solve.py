import argparse


def _parse_file(filename: str) -> tuple[list[int], list[int]]:
    with open(filename, 'r') as f:
        lines = f.readlines()

    locations_1 = []
    locations_2 = []
    for line in lines:
        l1, l2 = line.split()
        locations_1.append(int(l1))
        locations_2.append(int(l2))

    return locations_1, locations_2


def _calculate_distance(locations_1: list[int], locations_2: list[int]) -> int:
    pairs = zip(sorted(locations_1), sorted(locations_2))
    return sum(abs(l1 - l2) for l1, l2 in pairs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    locations_1, locations_2 = _parse_file(args.filename)
    distance = _calculate_distance(locations_1, locations_2)
    print(distance)
