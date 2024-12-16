import argparse
import collections
import dataclasses
import enum
import math
import queue
import typing


Position: typing.TypeAlias = tuple[int, int]


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

    @classmethod
    def turns_required(cls, direction_1, direction_2) -> int:
        if direction_1 == direction_2:
            return 0
        elif (
            set([direction_1, direction_2]) == set(cls.horizontals())
            or set([direction_1, direction_2]) == set(cls.verticals())
        ):
            return 2
        else:
            return 1

    @classmethod
    def get(cls, previous_position, current_position):
        diff = (
            current_position[0] - previous_position[0],
            current_position[1] - previous_position[1],
        )
        match diff:
            case (0, 1):
                direction = cls.RIGHT
            case (0, -1):
                direction = cls.LEFT
            case (1, 0):
                direction = cls.DOWN
            case (-1, 0):
                direction = cls.UP
            case _:
                raise ValueError("Impossible move between positions")
        return direction


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


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read()

    return raw.strip()


def _find_path(map_: Map):
    """Implement A* algorithm."""
    def _estimate_points(position: Position):
        return abs(map_.end[0] - position[0]) + abs(map_.end[1] - position[1])

    def _get_neighbors(position: Position) -> list[Position]:
        row, column = position
        possible_neighbors = (
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        )
        return filter(
            lambda pos: map_.is_valid(pos) and not map_.is_obstructed(pos),
            possible_neighbors,
        )

    def _point_step(
        previous_position: Position,
        current_position: Position,
        next_position: Position,
    ) -> int:
        if previous_position:
            current_direction = Direction.get(previous_position, current_position)
        else:
            current_direction = Direction.RIGHT
        next_direction = Direction.get(current_position, next_position)
        turns = Direction.turns_required(current_direction, next_direction)
        return 1 + 1000 * turns

    def _reconstruct_path(
        came_from: dict[Position],
        current: Position,
    ) -> list[Position]:
        path = collections.deque([current])
        while current := came_from.get(current):
            path.appendleft(current)
        return path

    path_ends = queue.PriorityQueue()
    path_ends.put((0, map_.start))
    came_from = {}

    points = collections.defaultdict(lambda: math.inf)
    points[map_.start] = 0

    estimated_points = collections.defaultdict(lambda: math.inf)
    estimated_points[map_.start] = _estimate_points(map_.start)

    while not path_ends.empty():
        current_points, current_position = path_ends.get()
        if current_position == map_.end:
            return _reconstruct_path(came_from, current_position), current_points

        for next_position in _get_neighbors(current_position):
            new_points = _point_step(
                came_from.get(current_position),
                current_position,
                next_position,
            )
            tentative_points = points[current_position] + new_points
            if tentative_points < points[next_position]:
                came_from[next_position] = current_position
                points[next_position] = tentative_points
                estimate = tentative_points + _estimate_points(next_position)
                estimated_points[next_position] = estimate

                if next_position not in (position for _, position in path_ends.queue):
                    path_ends.put((estimate, next_position))

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw_map = _parse_file(args.filename)
    map_ = Map(raw_map)
    path, points = _find_path(map_)
    print(f"Lowest possible score: {points}")
