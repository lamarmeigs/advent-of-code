import argparse
import collections
import dataclasses
import enum
import math
import queue
import typing


Position: typing.TypeAlias = tuple[int, int, 'Direction']


class Direction(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'

    @classmethod
    def horizontals(cls):
        return (cls.LEFT, cls.RIGHT)

    @classmethod
    def verticals(cls):
        return (cls.UP, cls.DOWN)


@dataclasses.dataclass
class Map:
    start: Position
    end: Position
    grid: list[list[str]] = dataclasses.field(default_factory=list)

    def __init__(self, raw_map: str):
        self.grid = []
        for row_index, raw_row in enumerate(raw_map.split('\n')):
            row = list(raw_row)
            if 'E' in row:
                self.end = (row_index, row.index('E'))
            elif 'S' in row:
                self.start = (row_index, row.index('S'))
            self.grid.append(row)

    def __str__(self):
        return '\n'.join(
            ''.join(row) for row in self.grid
        )

    @property
    def height(self):
        return len(self.grid)

    @property
    def width(self):
        try:
            return len(self.grid[0])
        except IndexError:
            return 0

    def positions(self) -> typing.Iterator[Position]:
        for row_index, row in enumerate(self.grid):
            for column_index, position in enumerate(row):
                if position != '#':
                    for direction in Direction:
                        yield row_index, column_index, direction

    def is_valid(self, position: Position) -> bool:
        return (
            0 <= position[0] < self.height
            and 0 <= position[1] < self.width
        )

    def is_obstructed(self, position: Position) -> bool:
        try:
            return self.grid[position[0]][position[1]] == '#'
        except IndexError:
            return False

    def get_next_positions(self, position: Position) -> list[tuple[Position, int]]:
        row, column, direction = position
        match direction:
            case Direction.LEFT:
                possible_neighbors = (
                    ((row, column, Direction.UP), 1000),
                    ((row, column, Direction.DOWN), 1000),
                    ((row, column - 1, direction), 1),
                )
            case Direction.RIGHT:
                possible_neighbors = (
                    ((row, column, Direction.UP), 1000),
                    ((row, column, Direction.DOWN), 1000),
                    ((row, column + 1, direction), 1),
                )
            case Direction.UP:
                possible_neighbors = (
                    ((row, column, Direction.LEFT), 1000),
                    ((row, column, Direction.RIGHT), 1000),
                    ((row - 1, column, direction), 1),
                )
            case Direction.DOWN:
                possible_neighbors = (
                    ((row, column, Direction.LEFT), 1000),
                    ((row, column, Direction.RIGHT), 1000),
                    ((row + 1, column, direction), 1),
                )
        return filter(
            lambda pos: self.is_valid(pos[0]) and not self.is_obstructed(pos[0]),
            possible_neighbors,
        )

    def render_path(self, path: list[Position]) -> str:
        grid = [list(row) for row in self.grid]
        for row, column, _ in path:
            grid[row][column] = 'O'
        return '\n'.join(
            ''.join(row) for row in grid
        )


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read()

    return raw.strip()


@dataclasses.dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: typing.Any = dataclasses.field(compare=False)

    def __iter__(self):
        return iter((self.priority, self.item))


def _find_all_paths(map_: Map):
    """Dijkstra's algorithm"""
    def _reconstruct_paths(
        paths_to: dict[Position, list[Position]],
        current: Position,
    ) -> list[list[Position]]:
        positions = set()
        if current is not None:
            positions.add(current)
        for previous in paths_to[current]:
            positions.update(_reconstruct_paths(paths_to, previous))
        return positions

    path_ends = queue.PriorityQueue()
    points_to = collections.defaultdict(lambda: math.inf)
    paths_to = collections.defaultdict(set)

    start_position = (*map_.start, Direction.RIGHT)
    points_to[start_position] = 0
    paths_to[start_position].add(None)
    path_ends.put(PrioritizedItem(0, start_position))
    for position in map_.positions():
        if position != start_position:
            path_ends.put(PrioritizedItem(math.inf, position))

    while not path_ends.empty():
        current_points, current_position = path_ends.get()
        for next_position, step_points in map_.get_next_positions(current_position):
            next_points = points_to[current_position] + step_points
            if next_points < points_to[next_position]:
                paths_to[next_position] = set([current_position])
                points_to[next_position] = next_points
                path_ends.put(PrioritizedItem(next_points, next_position))
            elif next_points == points_to[next_position]:
                paths_to[next_position].add(current_position)

    ends = [(*map_.end, direction) for direction in Direction]
    end_points = sorted([(end, points_to[end]) for end in ends], key=lambda t: t[1])
    min_points = end_points[0][1]
    positions = set()
    for end, points in end_points:
        if points == min_points:
            positions.update(_reconstruct_paths(paths_to, end))
    return positions, min_points


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw_map = _parse_file(args.filename)
    map_ = Map(raw_map)
    positions, points = _find_all_paths(map_)
    print(f"Lowest possible score: {points}")

    unique_coordinates = set(position[:2] for position in positions)
    print(f"Number of tiles in path: {len(unique_coordinates)}")
