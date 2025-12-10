import argparse
import collections
import dataclasses
import itertools

Tile = collections.namedtuple("Tile", ["x", "y"])


@dataclasses.dataclass
class Segment:
    start: Tile
    end: Tile


@dataclasses.dataclass
class Rectangle:
    corner_1: Tile
    corner_2: Tile

    @property
    def area(self):
        return (abs(self.corner_1.x - self.corner_2.x) + 1) * (
            abs(self.corner_1.y - self.corner_2.y) + 1
        )

    def crosses(self, segment: Segment) -> bool:
        min_x, max_x = sorted([self.corner_1.x, self.corner_2.x])
        min_y, max_y = sorted([self.corner_1.y, self.corner_2.y])
        segment_min_x, segment_max_x = sorted([segment.start.x, segment.end.x])
        segment_min_y, segment_max_y = sorted([segment.start.y, segment.end.y])

        return (
            segment_min_x < max_x
            and segment_min_y < max_y
            and segment_max_x > min_x
            and segment_max_y > min_y
        )


def _parse_file(filename: str) -> list[Tile]:
    with open(filename) as f:
        lines = f.readlines()
    tiles = []
    for line in lines:
        x, y = line.split(',')
        tiles.append(Tile(int(x), int(y)))
    return tiles


def _get_perimeter(tiles: list[Tile]):
    # fmt: off
    segments = (
        [Segment(tile_1, tile_2) for tile_1, tile_2 in itertools.pairwise(tiles)]
        + [Segment(tiles[-1], tiles[0])]
    )
    return segments
    # fmt: on


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    tiles = _parse_file(args.filename)
    rectangles = [
        Rectangle(corner_1, corner_2) for corner_1, corner_2 in itertools.combinations(tiles, 2)
    ]
    largest_area = max(rectangle.area for rectangle in rectangles)
    print(f"Area of largest rectangle: {largest_area}")

    perimeter = _get_perimeter(tiles)
    valid_rectangles = filter(
        lambda r: not any(r.crosses(segment) for segment in perimeter),
        rectangles,
    )
    largest_valid_area = max(rectangle.area for rectangle in valid_rectangles)
    print(f"Area of largest red & green rectangle: {largest_valid_area}")
