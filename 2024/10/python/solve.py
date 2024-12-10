import argparse
import collections
import dataclasses
import typing


@dataclasses.dataclass
class Map:
    width: int = 0
    height: int = 0
    grid: list[list[int]] = dataclasses.field(default_factory=list)

    def __init__(self, raw_map: str):
        self.grid = []
        for raw_row in raw_map.split('\n'):
            self.width = max(self.width, len(raw_row))
            row = [int(c) for c in raw_row]
            self.grid.append(row)
        self.height = len(self.grid)

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return self.grid[key[0]][key[1]]
        return self.grid.__getitem__(key)

    def __str__(self):
        return '\n'.join(
            (''.join(str(p) for p in row))
            for row in self.grid
        )

    def trailheads(self) -> typing.Iterator[tuple[int,int]]:
        for row_index, row in enumerate(self.grid):
            for column_index, position in enumerate(row):
                if position == 0:
                    yield (row_index, column_index)

    def find_trails(self) -> list[list[tuple[int, int]]]:
        all_trails = []
        for trailhead in self.trailheads():
            trails, _ = self._find_trails(trailhead)
            all_trails.extend(trails)
        return all_trails

    def _find_trails(self, position: tuple[int, int]) -> tuple[list[tuple[int, int]], bool]:
        def _is_next(neighbor: tuple[int, int]) -> bool:
            if (
                0 <= neighbor[0] < self.height
                and 0 <= neighbor[1] < self.width
            ):
                current_elevation = self[position]
                neighbor_elevation = self[neighbor]
                return current_elevation == neighbor_elevation - 1
            return False

        if self[position] == 9:
            return [[position]], True

        row, column = position
        neighbors = [
            (row - 1, column),
            (row, column - 1),
            (row, column + 1),
            (row + 1, column),
        ]
        next_positions = filter(_is_next, neighbors)

        all_trails = []
        any_complete = False
        for next_position in next_positions:
            trails, is_complete = self._find_trails(next_position)
            if not is_complete:
                continue

            any_complete = True
            for i, trail in enumerate(trails):
                trails[i] = [position] + trail
            all_trails.extend(trails)

        return all_trails, any_complete


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read()
    return raw.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw = _parse_file(args.filename)
    map_ = Map(raw)

    reachable_peaks = collections.defaultdict(set)
    trails = map_.find_trails()
    for trail in trails:
        trailhead = trail[0]
        peak = trail[-1]
        reachable_peaks[trailhead].add(peak)
    scores = {trailhead: len(peaks) for trailhead, peaks in reachable_peaks.items()}
    print(f'Sum of all trailhead scores: {sum(scores.values())}')

    ratings = collections.defaultdict(int)
    for trail in trails:
        trailhead = trail[0]
        ratings[trailhead] += 1
    print(f'Sum of all trailhead ratings: {sum(ratings.values())}')
