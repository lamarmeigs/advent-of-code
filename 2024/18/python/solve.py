import argparse
import collections
import dataclasses
import math
import queue
import typing

Position: typing.TypeAlias = tuple[int, int]


@dataclasses.dataclass
class Map:
    width: int = 71
    height: int = 71
    falls: list[Position] = dataclasses.field(default_factory=list)
    grid: list[list[str]] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.grid = [['.'] * self.width for _ in range(self.height)]

    def __str__(self):
        return "\n".join("".join(row) for row in self.grid)

    @property
    def start(self):
        return (0, 0)

    @property
    def end(self):
        return (self.width - 1, self.height - 1)

    def tick(self) -> Position:
        try:
            column, row = self.falls.pop(0)
        except IndexError:
            return None

        self.grid[row][column] = '#'
        return (column, row)

    def _is_valid(self, position: Position) -> bool:
        return 0 <= position[0] < self.height and 0 <= position[1] < self.width

    def _is_obstructed(self, position: Position) -> bool:
        try:
            return self.grid[position[0]][position[1]] == "#"
        except IndexError:
            return False

    def get_neighbors(self, position: Position) -> list[tuple[Position]]:
        row, column = position
        possible_neighbors = (
            (row, column - 1),
            (row, column + 1),
            (row - 1, column),
            (row + 1, column),
        )
        return filter(
            lambda pos: self._is_valid(pos) and not self._is_obstructed(pos),
            possible_neighbors,
        )

    def render_path(self, path: list[Position]) -> str:
        grid = [list(row) for row in self.grid]
        for row, column in path:
            grid[row][column] = "O"
        return "\n".join("".join(row) for row in grid)


def _parse_file(filename: str) -> Map:
    with open(filename, "r") as f:
        raw = f.read()

    return _build_map(raw.strip())


def _build_map(raw_falls: str, width: int = 71, height: int = 71) -> Map:
    falls = [
        tuple([int(coordinate) for coordinate in raw_position.split(',')])
        for raw_position in raw_falls.split('\n')
    ]
    return Map(width, height, falls)


def _find_path(map_: Map):
    """A* algorithm."""

    def _estimate_points(position: Position):
        return abs(map_.end[0] - position[0]) + abs(map_.end[1] - position[1])

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

    steps_to = collections.defaultdict(lambda: math.inf)
    steps_to[map_.start] = 0

    estimated_points = collections.defaultdict(lambda: math.inf)
    estimated_points[map_.start] = _estimate_points(map_.start)

    while not path_ends.empty():
        current_points, current_position = path_ends.get()
        if current_position == map_.end:
            return _reconstruct_path(came_from, current_position)

        for next_position in map_.get_neighbors(current_position):
            tentative_steps = steps_to[current_position] + 1
            if tentative_steps < steps_to[next_position]:
                came_from[next_position] = current_position
                steps_to[next_position] = tentative_steps
                estimate = tentative_steps + _estimate_points(next_position)
                estimated_points[next_position] = estimate

                if next_position not in (position for _, position in path_ends.queue):
                    path_ends.put((estimate, next_position))
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    map_ = _parse_file(args.filename)
    for _ in range(1024):
        map_.tick()
    path = _find_path(map_)
    print(f"Steps in path: {len(path) - 1}")

    while _find_path(map_) is not None:
        fall = map_.tick()
    print(f"Coordinates of fall preventing escape: {fall}")
