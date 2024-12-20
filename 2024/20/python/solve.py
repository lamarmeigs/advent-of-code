import argparse
import collections
import dataclasses
import itertools
import typing

Position: typing.TypeAlias = tuple[int, int]


@dataclasses.dataclass
class Map:
    start: Position
    end: Position
    grid: list[list[str]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_raw(cls, raw_map: str) -> 'Map':
        start = None
        end = None
        grid = []
        for row_index, raw_row in enumerate(raw_map.split('\n')):
            row = []
            for column_index, position in enumerate(raw_row):
                row.append(position)
                if position == 'S':
                    start = (row_index, column_index)
                elif position == 'E':
                    end = (row_index, column_index)
            grid.append(row)
        return cls(start, end, grid)

    def __str__(self):
        return "\n".join("".join(row) for row in self.grid)

    @property
    def width(self) -> int:
        try:
            return len(self.grid[0])
        except IndexError:
            return 0

    @property
    def height(self):
        return len(self.grid)

    def _is_valid(self, position: Position) -> bool:
        return 0 <= position[0] < self.height and 0 <= position[1] < self.width

    def _is_wall(self, position: Position) -> bool:
        try:
            return self.grid[position[0]][position[1]] == "#"
        except IndexError:
            return False

    def get_neighbors(self, position: Position) -> list[Position]:
        row, column = position
        possible_neighbors = (
            (row, column - 1),
            (row, column + 1),
            (row - 1, column),
            (row + 1, column),
        )
        return filter(
            lambda pos: self._is_valid(pos) and not self._is_wall(pos),
            possible_neighbors,
        )


def _parse_file(filename: str) -> Map:
    with open(filename, "r") as f:
        raw = f.read()

    return Map.from_raw(raw.strip())


def _find_path(map_: Map) -> list[Position]:
    path = [map_.start]
    while path[-1] != map_.end:
        for neighbor in map_.get_neighbors(path[-1]):
            if neighbor not in path:
                path.append(neighbor)
    return path


def _get_cheats(
    map_: Map,
    path: list[Position],
    max_distance: int,
) -> dict[int, list[tuple[Position, Position]]]:
    cheats = collections.defaultdict(set)
    for i, start in enumerate(path):
        for j in range(i, len(path)):
            end = path[j]
            old_distance = j - i
            new_distance = _get_manhattan_distance(start, end)
            if new_distance <= max_distance and new_distance < old_distance:
                cheats[old_distance - new_distance].add((start, end))
    return cheats


def _get_manhattan_distance(position_1: Position, position_2: Position) -> int:
    return abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    map_ = _parse_file(args.filename)
    path = _find_path(map_)
    cheats = _get_cheats(map_, path, 2)
    big_cheats = itertools.chain(*[c for skipped, c in cheats.items() if skipped >= 100])
    print(f"Number of 2-step cheats skipping 100+ steps: {len(list(big_cheats))}")

    cheats = _get_cheats(map_, path, 20)
    big_cheats = itertools.chain(*[c for skipped, c in cheats.items() if skipped >= 100])
    print(f"Number of 20-step cheats skipping 100+ steps: {len(list(big_cheats))}")
