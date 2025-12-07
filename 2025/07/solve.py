import argparse
import collections


def _parse_file(filename: str) -> str:
    with open(filename) as f:
        raw_manifold = f.read()
    return raw_manifold


Coordinates = collections.namedtuple("Coorindate", ["x", "y"])


class Manifold:
    grid: list[list[str]]
    source: Coordinates
    beam_count: list[list[int]]

    def __init__(self, raw_manifold: str):
        self.grid = list(list(row) for row in raw_manifold.split())
        self.source = Coordinates(self.grid[0].index('S'), 0)

        self.beam_count = [[0 for _ in row] for row in self.grid]
        self.beam_count[self.source.y][self.source.x] = 1

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.grid)

    def emit_beam(self):
        y = 1
        beams = [self.source]
        while y < len(self.grid):
            new_beams = set()
            for beam in beams:
                if self.grid[y][beam.x] == '^':
                    if beam.x != 0:
                        new_beam = Coordinates(beam.x - 1, y)
                        self.grid[new_beam.y][new_beam.x] = '|'
                        self.beam_count[new_beam.y][new_beam.x] += self.beam_count[beam.y][beam.x]
                        new_beams.add(new_beam)
                    if beam.x != len(self.grid[y]) - 1:
                        new_beam = Coordinates(beam.x + 1, y)
                        self.grid[new_beam.y][new_beam.x] = '|'
                        self.beam_count[new_beam.y][new_beam.x] += self.beam_count[beam.y][beam.x]
                        new_beams.add(new_beam)
                else:
                    new_beam = Coordinates(beam.x, y)
                    self.grid[new_beam.y][new_beam.x] = '|'
                    self.beam_count[new_beam.y][new_beam.x] += self.beam_count[beam.y][beam.x]
                    new_beams.add(new_beam)
            beams = new_beams
            y += 1

    @property
    def splits(self) -> int:
        splits = 0
        coordinates = []
        for y, row in enumerate(self.grid):
            for x, point in enumerate(row):
                if self.grid[y][x] == '^' and self.grid[y - 1][x] == '|':
                    splits += 1
                    coordinates.append((x, y))
        return splits

    @property
    def timelines(self) -> int:
        return sum(manifold.beam_count[-1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw_manifold = _parse_file(args.filename)
    manifold = Manifold(raw_manifold)
    splits = manifold.emit_beam()
    print(f"Techyon beam splits: {manifold.splits}")
    print(f"Timelines: {manifold.timelines}")
